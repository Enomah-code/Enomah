"""Traitement « caméra cinéma » d'un plan : vrai flou de profondeur + étalonnage.

Pour chaque image :
  1. détourage du sujet : RobustVideoMatting (stable dans le temps), médiane temporelle sur 3 images.
     (Le fond reste le vrai décor, seulement flouté : une petite erreur de masque ne se voit pas,
     inutile de payer BiRefNet à 14 s/image) ;
  2. carte de profondeur Depth-Anything-V2 (lissée dans le temps) → le flou augmente avec la distance
     au plan de netteté (le sujet), comme un objectif ouvert ;
  3. arrière-plan reconstruit sous le sujet (pas de halo), bokeh disque en lumière linéaire ;
  4. étalonnage chaud doux, vignette, grain.
Sorties : assets/shots/<id>.mp4 (1440x2560, 30 i/s) et assets/shots/<id>-alpha.mkv (masque 720x1280).

Usage : python3 scripts/cine.py <dossier_rushs> <dossier_rvm> p02a [p03a ...]   (ids de scripts/edl.json)
"""
import json
import os
import subprocess
import sys
import time
from collections import deque

import cv2
import numpy as np
import torch
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1440, 2560
SW, SH = 720, 1280            # résolution de travail du flou
FPS = 30
LEVELS = [0, 5, 11, 19, 30]   # rayons de bokeh (à SW x SH)
STRENGTH = 0.85


def shots():
    edl = json.load(open(os.path.join(ROOT, "scripts/edl.json")))
    return {s["id"]: s for seg in edl["segments"] for s in seg.get("shots", [])}


def reader(path, t_in, t_out, speed):
    if speed == 1:
        vf = f"fps={FPS},scale={W}:{H}"
    else:   # ralenti : interpolation de mouvement (images intermédiaires calculées)
        vf = f"scale={W}:{H},setpts=PTS/{speed},minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"
    return subprocess.Popen(["ffmpeg", "-loglevel", "error", "-ss", f"{t_in}", "-t", f"{t_out - t_in}", "-i", path,
                             "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)


def disk(r):
    k = np.zeros((2 * r + 1, 2 * r + 1), np.float32)
    cv2.circle(k, (r, r), r, 1, -1)
    return k / k.sum()


KERNELS = [None] + [disk(r) for r in LEVELS[1:]]
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIGN = np.clip(1 - 0.30 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H * 0.42) / (H * 0.78)) ** 2), 0.6, 1)[..., None]
del yy, xx


def grade(x):
    x = np.clip((x - 0.5) * 1.07 + 0.5, 0, 1)
    lum = x.mean(-1, keepdims=True)
    x = x + (1 - lum) * np.array([-0.010, 0.002, 0.016], np.float32) + lum * np.array([0.030, 0.012, -0.018], np.float32)
    x = lum + (x - lum) * 1.04
    return np.clip(x * VIGN, 0, 1)


def bokeh(bg_small, coc_small):
    lin = bg_small ** 2.2
    stack = [lin] + [cv2.filter2D(lin, -1, k) for k in KERNELS[1:]]
    idx = coc_small * (len(LEVELS) - 1)
    lo = np.floor(idx).astype(np.int32).clip(0, len(LEVELS) - 2)
    fr = (idx - lo)[..., None]
    out = np.zeros_like(lin)
    for i in range(len(LEVELS) - 1):
        m = (lo == i)[..., None]
        out += m * (stack[i] * (1 - fr) + stack[i + 1] * fr)
    return np.clip(out, 0, 1) ** (1 / 2.2)


def main():
    rush_dir, rvm_dir, ids = sys.argv[1], sys.argv[2], sys.argv[3:]
    torch.set_num_threads(os.cpu_count() or 4)
    sys.path.insert(0, rvm_dir)
    from model import MattingNetwork
    rvm = MattingNetwork("resnet50").eval()
    rvm.load_state_dict(torch.load(os.path.join(rvm_dir, "rvm_resnet50.pth"), map_location="cpu"))
    from transformers import pipeline
    depth = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf")
    S = shots()
    out_dir = os.path.join(ROOT, "assets/shots")
    os.makedirs(out_dir, exist_ok=True)
    rng = np.random.default_rng(5)
    for sid in ids:
        sh = S[sid]
        rd = reader(os.path.join(rush_dir, sh["src"]), sh["in"], sh["out"], sh["speed"])
        wv = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                               "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p",
                               "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                               os.path.join(out_dir, f"{sid}.mp4")], stdin=subprocess.PIPE)
        wa = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{SW}x{SH}", "-r", str(FPS),
                               "-i", "-", "-c:v", "ffv1", os.path.join(out_dir, f"{sid}-alpha.mkv")], stdin=subprocess.PIPE)
        rec = [None] * 4
        buf = deque()
        dep_ema, focus_ema = None, None
        k_emit = 0
        n, t0 = 0, time.time()

        def emit(frame, a):
            nonlocal dep_ema, focus_ema, k_emit
            img = frame.astype(np.float32) / 255
            small = cv2.resize(img, (SW, SH), interpolation=cv2.INTER_AREA)
            a_s = cv2.resize(a, (SW, SH), interpolation=cv2.INTER_AREA)
            if dep_ema is None or k_emit % 2 == 0:                       # profondeur 1 image sur 2, lissée
                d = depth(Image.fromarray((small * 255).astype(np.uint8)))["predicted_depth"].squeeze().numpy()
                d = cv2.resize(d, (SW, SH))
                lo, hi = np.percentile(d, 2), np.percentile(d, 99.5)
                d = np.clip((d - lo) / (hi - lo + 1e-6), 0, 1)          # 1 = proche
                dep_ema = d if dep_ema is None else dep_ema * 0.5 + d * 0.5
            k_emit += 1
            subj = a_s > 0.85
            f = float(np.median(dep_ema[subj])) if subj.sum() > 500 else (focus_ema or 0.8)
            focus_ema = f if focus_ema is None else focus_ema * 0.85 + f * 0.15
            coc = np.clip((focus_ema - dep_ema) / max(focus_ema, 1e-3), 0, 1) ** 0.75 * STRENGTH
            coc = cv2.GaussianBlur(coc, (0, 0), 6)
            # arrière-plan sans le sujet (remplissage) pour éviter le halo autour d'elle
            m = cv2.dilate((a_s > 0.08).astype(np.uint8), np.ones((15, 15), np.uint8))
            q = cv2.resize(small, (SW // 4, SH // 4))
            mq = cv2.resize(m, (SW // 4, SH // 4), interpolation=cv2.INTER_NEAREST)
            fill = cv2.inpaint((q * 255).astype(np.uint8), mq, 5, cv2.INPAINT_TELEA).astype(np.float32) / 255
            fill = cv2.resize(fill, (SW, SH))
            plate = small * (1 - m[..., None]) + fill * m[..., None]
            bg = cv2.resize(bokeh(plate, coc), (W, H), interpolation=cv2.INTER_CUBIC)
            a3 = cv2.GaussianBlur(a, (0, 0), 1.0)[..., None]
            comp = grade(img * a3 + bg * (1 - a3))
            comp += rng.normal(0, 0.010, (H // 2, W // 2, 1)).astype(np.float32).repeat(2, 0).repeat(2, 1)
            wv.stdin.write((np.clip(comp, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
            wa.stdin.write((np.clip(a_s, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())

        with torch.no_grad():
            while True:
                raw = rd.stdout.read(W * H * 3)
                if len(raw) < W * H * 3:
                    break
                frame = np.frombuffer(raw, np.uint8).reshape(H, W, 3)
                x = torch.from_numpy(frame.copy()).permute(2, 0, 1)[None].float() / 255
                _, pha, *rec = rvm(x, *rec, downsample_ratio=0.2)
                a = pha[0, 0].numpy().astype(np.float32)
                buf.append((frame, a))
                if len(buf) == 3:
                    if n == 2:
                        emit(*buf[0])
                    emit(buf[1][0], np.median(np.stack([b[1] for b in buf]), axis=0).astype(np.float32))
                    buf.popleft()
                n += 1
                if n % 30 == 0:
                    print(f"{sid}: {n} images, {(time.time() - t0) / n:.2f} s/img", flush=True)
        if n == 1:
            emit(*buf[0])
        elif len(buf) >= 2:
            emit(*buf[-1])
        for p in (wv, wa):
            p.stdin.close()
            p.wait()
        rd.kill()
        print(f"{sid}: terminé — {n} images en {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
