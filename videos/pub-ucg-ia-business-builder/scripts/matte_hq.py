"""Détourage haute qualité → masque alpha + aperçu fond vert.

Méthode (après comparaison RVM / BiRefNet / ViTMatte sur un gros plan visage) :
  - RobustVideoMatting pour tout le corps (stable dans le temps) ;
  - BiRefNet_lite @640 sur la zone tête + épaules, là où RVM « mange » les joues quand la peau
    éclairée a la couleur du mur ; utilisé seulement quand le visage est visible à l'écran ;
  - lissage temporel (médiane sur 3 images) pour éviter le scintillement du contour ;
  - le laptop tenu en main est ajouté via isnet (voir bg_replace.laptop_flags).

Sorties : assets/matte/cXX.mkv (alpha 8 bits sans perte) et assets/aroll-gs/cXX.mp4 (fond vert).
Usage : python3 scripts/matte_hq.py <dossier_rvm> c01 [c02 ...]
"""
import os
import subprocess
import sys
import time
from collections import deque

import cv2
import numpy as np
import torch
from PIL import Image
from torchvision import transforms

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bg_replace import laptop_flags, object_alpha  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1080, 1920
CROP = (60, 150, 1020, 1250)          # x0, y0, x1, y1 : tête + épaules
FEATHER = 40
# fenêtres (temps local du rush) où le visage est visible à l'écran (hors panneaux plein écran)
VISIBLE = {
    "c01": [(0, 99)], "c02": [(0, 0.8)], "c03": [(0, 99)], "c04": [(0, 99)], "c05": [(0, 1.0)],
    "c06": [(0, 5.2)], "c11": [(0, 7.7)], "c12": [(0, 1.0), (6.5, 99)],
    "c13": [(0, 6.4), (11.4, 17.9)], "c14": [(0, 0.6), (3.9, 99)],
}
GREEN = np.array([0, 0.78, 0.2], np.float32)


def crop_weight():
    x0, y0, x1, y1 = CROP
    w = np.zeros((H, W), np.float32)
    w[y0:y1, x0:x1] = 1
    # bords intérieurs adoucis (sauf le bas qui traverse le buste : alpha = 1 des deux côtés)
    w = cv2.GaussianBlur(w, (0, 0), FEATHER / 2)
    w[y0 + FEATHER:y1, x0 + FEATHER:x1 - FEATHER] = 1
    return w


def fg_estimate(img, a):
    """Couleur de premier plan sur les bords : moyenne pondérée par alpha (retire le reflet du mur)."""
    num = cv2.GaussianBlur(img * a[..., None], (0, 0), 3)
    den = cv2.GaussianBlur(a, (0, 0), 3)[..., None] + 1e-4
    est = num / den
    edge = ((a > 0.01) & (a < 0.97))[..., None]
    return np.where(edge, est, img)


def main():
    args = sys.argv[1:]
    rvm_dir = args[0]
    sys.path.insert(0, rvm_dir)
    from model import MattingNetwork
    torch.set_num_threads(os.cpu_count() or 4)
    rvm = MattingNetwork("resnet50").eval()
    rvm.load_state_dict(torch.load(os.path.join(rvm_dir, "rvm_resnet50.pth"), map_location="cpu"))
    from transformers import AutoModelForImageSegmentation
    bir = AutoModelForImageSegmentation.from_pretrained("ZhengPeng7/BiRefNet_lite", trust_remote_code=True).float().eval()
    tf = transforms.Compose([transforms.Resize((640, 640)), transforms.ToTensor(),
                             transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
    cw = crop_weight()
    x0, y0, x1, y1 = CROP
    os.makedirs(os.path.join(ROOT, "assets/matte"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "assets/aroll-gs"), exist_ok=True)

    for cid in args[1:]:
        src = os.path.join(ROOT, "assets/aroll", f"{cid}.mp4")
        flags = laptop_flags(src)
        wins = VISIBLE.get(cid, [])
        rd = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                              stdout=subprocess.PIPE)
        wa = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray",
                               "-s", f"{W}x{H}", "-r", "30", "-i", "-", "-c:v", "ffv1",
                               os.path.join(ROOT, "assets/matte", f"{cid}.mkv")], stdin=subprocess.PIPE)
        wg = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                               "-s", f"{W}x{H}", "-r", "30", "-i", "-", "-i", src, "-map", "0:v", "-map", "1:a",
                               "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest",
                               os.path.join(ROOT, "assets/aroll-gs", f"{cid}.mp4")], stdin=subprocess.PIPE)
        buf = deque()  # (frame, alpha) pour la médiane temporelle
        rec = [None] * 4
        n, nb, t0 = 0, 0, time.time()

        def emit(frame, a):
            img = frame.astype(np.float32) / 255
            fg = fg_estimate(img, a)
            comp = fg * a[..., None] + GREEN * (1 - a[..., None])
            wa.stdin.write((a * 255 + 0.5).astype(np.uint8).tobytes())
            wg.stdin.write((np.clip(comp, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())

        with torch.no_grad():
            while True:
                raw = rd.stdout.read(W * H * 3)
                if len(raw) < W * H * 3:
                    break
                frame = np.frombuffer(raw, np.uint8).reshape(H, W, 3)
                x = torch.from_numpy(frame.copy()).permute(2, 0, 1)[None].float() / 255
                _, pha, *rec = rvm(x, *rec, downsample_ratio=0.25)
                a = pha[0, 0].numpy()
                t = n / 30
                if any(s <= t < e for s, e in wins):
                    crop = frame[y0:y1, x0:x1]
                    p = bir(tf(Image.fromarray(crop))[None])[-1].sigmoid()[0, 0].numpy()
                    p = cv2.resize(p, (x1 - x0, y1 - y0), interpolation=cv2.INTER_CUBIC).clip(0, 1)
                    hq = a.copy()
                    hq[y0:y1, x0:x1] = p
                    a = hq * cw + a * (1 - cw)
                    nb += 1
                if n < len(flags) and flags[n]:
                    a = np.maximum(a, object_alpha(frame))
                buf.append((frame, a))
                if len(buf) == 3:
                    f_mid, a_mid = buf[1]
                    a_med = np.median(np.stack([b[1] for b in buf]), axis=0).astype(np.float32)
                    if n == 2:
                        emit(buf[0][0], buf[0][1])
                    emit(f_mid, a_med)
                    buf.popleft()
                n += 1
        if len(buf) >= 2:
            emit(buf[-1][0], buf[-1][1])
        elif len(buf) == 1 and n == 1:
            emit(buf[0][0], buf[0][1])
        for p in (wa, wg):
            p.stdin.close()
            p.wait()
        rd.kill()
        print(f"{cid}: {n} images ({nb} en haute précision) en {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
