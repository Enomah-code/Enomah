"""Anime une photo fixe en « plan caméra » 2,5D : carte de profondeur (Depth-Anything-V2) puis travelling
où les plans proches bougent plus que le fond (parallaxe), + léger étalonnage chaud et grain.
Sortie 1080x1920, 30 i/s.

Usage : python3 scripts/parallax.py <photo> <sortie.mp4> <durée> <mode>
  mode : push (avancée), pan (latéral), rise (montée vers le ciel), sky (dérive lente dans les nuages)
         + option « crop=x0,y0,x1,y1 » (fractions) pour cadrer une partie de la photo
"""
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image
from transformers import pipeline

W, H, FPS = 1080, 1920, 30


def main():
    src, dst, dur, mode = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
    crop = None
    for a in sys.argv[5:]:
        if a.startswith("crop="):
            crop = [float(v) for v in a[5:].split(",")]
    im = Image.open(src).convert("RGB")
    if crop:
        w0, h0 = im.size
        im = im.crop((int(crop[0] * w0), int(crop[1] * h0), int(crop[2] * w0), int(crop[3] * h0)))
    # cadre vertical 9:16 un peu plus grand que l'écran (marge pour le mouvement)
    M = 1.18
    tw, th = int(W * M), int(H * M)
    r = max(tw / im.width, th / im.height)
    im = im.resize((int(im.width * r + 0.5), int(im.height * r + 0.5)), Image.LANCZOS)
    x0, y0 = (im.width - tw) // 2, (im.height - th) // 2
    if mode == "sky":
        y0 = 0
    im = im.crop((x0, y0, x0 + tw, y0 + th))
    img = np.asarray(im).astype(np.float32) / 255
    d = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf")(im)["predicted_depth"].squeeze().numpy()
    d = cv2.resize(d, (tw, th))
    d = (d - np.percentile(d, 2)) / (np.percentile(d, 99) - np.percentile(d, 2) + 1e-6)
    d = cv2.GaussianBlur(np.clip(d, 0, 1), (0, 0), 25).astype(np.float32)   # 1 = proche
    # étalonnage commun avec les rushs
    lum = img.mean(-1, keepdims=True)
    img = np.clip((img - 0.5) * 1.06 + 0.5 + (1 - lum) * np.array([-0.01, 0.0, 0.015]) + lum * np.array([0.03, 0.012, -0.018]), 0, 1)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    n = int(round(dur * FPS))
    wr = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", dst], stdin=subprocess.PIPE)
    rng = np.random.default_rng(3)
    cx, cy = tw / 2, th / 2
    for i in range(n):
        p = i / max(1, n - 1)
        e = p * p * (3 - 2 * p) if mode != "sky" else p           # ease in-out
        if mode == "push":
            zoom, dx, dy, k = 1.0 + 0.10 * e, 0, 0, 0.10 * e
        elif mode == "pan":
            zoom, dx, dy, k = 1.04, (e - 0.5) * 0.10 * W, 0, 0.0
        elif mode == "rise":
            zoom, dx, dy, k = 1.03 + 0.04 * e, 0, (0.5 - e) * 0.10 * H, 0.05
        else:  # sky
            zoom, dx, dy, k = 1.02 + 0.05 * e, 0.02 * W * e, -0.03 * H * e, 0.02
        # position dans l'image source : les zones proches (d≈1) bougent plus (parallaxe)
        sx = cx + dx + (xx - W / 2) / zoom
        sy = cy + dy + (yy - H / 2) / zoom
        dd = cv2.remap(d, sx, sy, cv2.INTER_LINEAR)
        par = 1 + k * (dd - 0.4)
        sx = cx + dx * (0.6 + 0.8 * dd) + (xx - W / 2) / (zoom * par)
        sy = cy + dy * (0.6 + 0.8 * dd) + (yy - H / 2) / (zoom * par)
        fr = cv2.remap(img, sx, sy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        fr += rng.normal(0, 0.010, (H // 2, W // 2, 1)).astype(np.float32).repeat(2, 0).repeat(2, 1)
        wr.stdin.write((np.clip(fr, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
    wr.stdin.close()
    wr.wait()
    print(dst, n, "images")


if __name__ == "__main__":
    main()
