"""Remplace le fond des rushs face caméra par le bureau EMK Blue Diamond.

Pipeline par rush (assets/aroll/cXX.mp4 → assets/aroll-bg/cXX.mp4, audio conservé) :
  1. détourage vidéo RobustVideoMatting (états récurrents → contours stables, cheveux, mains) ;
  2. personnage légèrement réduit (ancré en bas) pour que le logo mural reste au-dessus de la tête ;
  3. intégration : étalonnage vers la lumière chaude/bleutée du bureau, « light wrap » du décor
     sur les contours, fond flouté (profondeur de champ), grain commun sur toute l'image.

Usage : python3 scripts/bg_replace.py <dossier_rvm> c01 [c02 ...] [--frames N]
"""
import os
import subprocess
import sys
import time

import cv2
import numpy as np
import torch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1080, 1920
SCALE = 0.94            # taille du personnage (ancré en bas, centré)
DOF_SIGMA = 3.5         # flou du décor
GRAIN = 0.010
# rushs filmés avec moins de lumière : gain d'exposition avant étalonnage (mesuré sur le visage)
GAIN = {"c13": 1.85}


def load_model(rvm_dir):
    sys.path.insert(0, rvm_dir)
    from model import MattingNetwork  # noqa: E402
    m = MattingNetwork("resnet50").eval()
    m.load_state_dict(torch.load(os.path.join(rvm_dir, "rvm_resnet50.pth"), map_location="cpu"))
    torch.set_num_threads(os.cpu_count() or 4)
    return m


def prepare_bg():
    bg = cv2.imread(os.path.join(ROOT, "assets/bg/bureau-emk-1080x1920.png"))[:, :, ::-1].astype(np.float32) / 255
    bg = cv2.GaussianBlur(bg, (0, 0), DOF_SIGMA)
    # vignette douce
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    v = 1 - 0.28 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H * 0.45) / (H * 0.7)) ** 2)
    bg *= np.clip(v, 0.6, 1)[..., None]
    wrap_src = cv2.GaussianBlur(bg, (0, 0), 30)
    # teinte moyenne de la lumière du décor autour du personnage
    tint = bg[300:1400, 150:930].reshape(-1, 3).mean(0)
    tint = tint / tint.mean()
    return bg, wrap_src, tint


_yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
SHADE = 1.12 - 0.34 * np.clip((_yy - 0.25) / 0.75, 0, 1)
_xx = np.linspace(0, 1, W, dtype=np.float32)[None, :, None]
# lumière de contour : lampe chaude à gauche, néon bleu du logo à droite
RIM = (1 - _xx) * np.array([1.0, 0.62, 0.28], np.float32) + _xx * np.array([0.35, 0.45, 1.0], np.float32)


def grade(fg, tint):
    fg = fg * 0.74                                   # exposition : scène plus sombre
    fg = fg / (1 + 0.35 * fg)                        # adoucit les hautes lumières (peau, chemise)
    fg = fg * SHADE                                  # la lumière tombe du haut (plus sombre vers le bas)
    fg = (fg - 0.45) * 1.08 + 0.45                   # contraste
    lum = fg.mean(-1, keepdims=True)
    fg = lum + (fg - lum) * 0.92                     # saturation
    fg = fg * (0.82 + 0.18 * tint)                   # teinte du décor
    fg[..., 0] *= 1.03                               # chaleur des lampes
    fg[..., 2] *= 0.97
    return np.clip(fg, 0, 1)


def laptop_flags(src, margin=8, thr=0.07):
    """Repère les images où un objet gris (le laptop tenu en main) occupe le bas du cadre.
    RVM ne garde que la personne : sur ces images on complète le masque avec isnet."""
    w, h = 108, 192
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", src, "-vf", f"scale={w}:{h}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)[:, int(0.55 * h):].astype(np.float32) / 255
    mx, mn = fr.max(-1), fr.min(-1)
    grey = (((mx - mn) / (mx + 1e-6)) < 0.10) & (mx > 0.45) & (mx < 0.95)
    hit = grey.reshape(len(fr), -1).mean(1) > thr
    flags = np.zeros_like(hit)
    for i in np.nonzero(hit)[0]:
        flags[max(0, i - margin):i + margin + 1] = True
    return flags


_LOW = np.clip((np.linspace(0, 1, H, dtype=np.float32) - 0.40) / 0.10, 0, 1)[:, None]
_REMBG = None


def object_alpha(frame):
    global _REMBG
    from rembg import remove, new_session
    from PIL import Image
    if _REMBG is None:
        _REMBG = new_session("isnet-general-use")
    m = remove(Image.fromarray(frame), session=_REMBG, only_mask=True)
    return np.asarray(m, np.float32) / 255 * _LOW


def process(model, cid, bg, wrap_src, tint, max_frames=None):
    src = os.path.join(ROOT, "assets/aroll", f"{cid}.mp4")
    out_dir = os.path.join(ROOT, "assets/aroll-bg")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, f"{cid}.mp4")
    rd = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                          stdout=subprocess.PIPE)
    wr = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", "30", "-i", "-", "-i", src, "-map", "0:v", "-map", "1:a",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-g", "15", "-pix_fmt", "yuv420p",
                           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                           "-c:a", "copy", "-shortest", "-movflags", "+faststart", dst], stdin=subprocess.PIPE)
    flags = laptop_flags(src)
    print(f"{cid}: {int(flags.sum())} images avec objet tenu en main", flush=True)
    M = np.float32([[SCALE, 0, (1 - SCALE) * W / 2], [0, SCALE, (1 - SCALE) * H]])
    rec = [None] * 4
    rng = np.random.default_rng(7)
    n, t0 = 0, time.time()
    with torch.no_grad():
        while True:
            buf = rd.stdout.read(W * H * 3)
            if len(buf) < W * H * 3 or (max_frames and n >= max_frames):
                break
            frame = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
            x = torch.from_numpy(frame).permute(2, 0, 1)[None].float() / 255
            fgr, pha, *rec = model(x, *rec, downsample_ratio=0.25)
            fgr = fgr[0].permute(1, 2, 0).numpy()
            pha = pha[0, 0].numpy()
            if n < len(flags) and flags[n]:
                obj = object_alpha(frame)
                fgr = np.where((obj > pha)[..., None], frame.astype(np.float32) / 255, fgr)
                pha = np.maximum(pha, obj)
            fgr = cv2.warpAffine(fgr, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
            pha = cv2.warpAffine(pha, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
            fg = grade(np.clip(fgr * GAIN.get(cid, 1.0), 0, 1), tint)
            # light wrap : le décor déborde légèrement sur les bords du personnage
            edge = np.clip(pha - cv2.erode(pha, np.ones((15, 15), np.uint8)), 0, 1)
            edge = cv2.GaussianBlur(edge, (0, 0), 5)[..., None]
            fg = fg * (1 - 0.4 * edge) + wrap_src * 0.4 * edge + RIM * 0.22 * edge
            a = pha[..., None]
            comp = fg * a + bg * (1 - a)
            comp += rng.normal(0, GRAIN, (H // 2, W // 2, 1)).astype(np.float32).repeat(2, 0).repeat(2, 1)
            wr.stdin.write((np.clip(comp, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
            n += 1
    wr.stdin.close()
    wr.wait()
    rd.kill()
    print(f"{cid}: {n} images en {time.time() - t0:.0f}s ({n / max(1e-6, time.time() - t0):.2f} img/s)", flush=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    frames = None
    if "--frames" in args:
        i = args.index("--frames")
        frames = int(args[i + 1])
        del args[i:i + 2]
    model = load_model(args[0])
    bg, wrap_src, tint = prepare_bg()
    for cid in args[1:]:
        process(model, cid, bg, wrap_src, tint, frames)
