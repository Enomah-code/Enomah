"""Incruste les rushs détourés (assets/matte/cXX.mkv) dans le bureau EMK Blue Diamond.

Aucune IA ici : on réutilise le masque haute qualité validé sur fond vert.
Intégration : couleur de bord nettoyée (sans reflet du mur d'origine), étalonnage vers l'ambiance
du bureau, lumière de contour chaude/bleue très fine, fond flouté (profondeur de champ), grain.

Usage : python3 scripts/composite_bg.py c01 [c02 ...]
"""
import os
import subprocess
import sys
import time

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bg_replace import GAIN, RIM, W, H, SCALE, GRAIN, grade, prepare_bg  # noqa: E402
from matte_hq import fg_estimate  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def process(cid, bg, wrap_src, tint):
    src = os.path.join(ROOT, "assets/aroll", f"{cid}.mp4")
    matte = os.path.join(ROOT, "assets/matte", f"{cid}.mkv")
    dst = os.path.join(ROOT, "assets/aroll-bg", f"{cid}.mp4")
    rd = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                          stdout=subprocess.PIPE)
    ra = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", matte, "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                          stdout=subprocess.PIPE)
    wr = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", "30", "-i", "-", "-i", src, "-map", "0:v", "-map", "1:a",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-g", "15", "-pix_fmt", "yuv420p",
                           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                           "-c:a", "copy", "-shortest", "-movflags", "+faststart", dst], stdin=subprocess.PIPE)
    M = np.float32([[SCALE, 0, (1 - SCALE) * W / 2], [0, SCALE, (1 - SCALE) * H]])
    rng = np.random.default_rng(7)
    n, t0 = 0, time.time()
    while True:
        raw = rd.stdout.read(W * H * 3)
        al = ra.stdout.read(W * H)
        if len(raw) < W * H * 3 or len(al) < W * H:
            break
        img = np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
        a = np.frombuffer(al, np.uint8).reshape(H, W).astype(np.float32) / 255
        fg = fg_estimate(img, a)
        fg = cv2.warpAffine(fg, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
        a = cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
        fg = grade(np.clip(fg * GAIN.get(cid, 1.0), 0, 1), tint)
        # bande de contour très fine : légère lumière du décor + lumière de contour, sans assombrir
        edge = np.clip(a - cv2.erode(a, np.ones((5, 5), np.uint8)), 0, 1)
        edge = cv2.GaussianBlur(edge, (0, 0), 2)[..., None]
        fg = fg * (1 - 0.15 * edge) + wrap_src * 0.15 * edge + RIM * 0.18 * edge
        a3 = a[..., None]
        comp = fg * a3 + bg * (1 - a3)
        comp += rng.normal(0, GRAIN, (H // 2, W // 2, 1)).astype(np.float32).repeat(2, 0).repeat(2, 1)
        wr.stdin.write((np.clip(comp, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
        n += 1
    wr.stdin.close()
    wr.wait()
    rd.kill()
    ra.kill()
    print(f"{cid}: {n} images incrustées en {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    bg, wrap_src, tint = prepare_bg()
    for c in sys.argv[1:]:
        process(c, bg, wrap_src, tint)
