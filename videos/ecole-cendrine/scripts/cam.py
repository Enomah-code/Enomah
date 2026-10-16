"""Plan « caméra 3D » à partir d'une photo (2,5D) : carte de profondeur Depth-Anything-V2, puis caméra virtuelle
qui se déplace dans la photo (cadre 9:16) avec parallaxe : les plans proches bougent plus que le fond.

Usage : python3 scripts/cam.py <image> <sortie.mp4> <durée> "<x0,y0,h0>" "<x1,y1,h1>" [k=0.06] [warm=1] [ease=io|lin|out]
  (x, y) = centre du cadre en fractions de l'image ; h = hauteur du cadre en fraction de la hauteur de l'image
  (plus h est petit, plus on est serré). La largeur suit le 9:16.
  k = force de la parallaxe (0 = simple recadrage animé).
  retro=1 : look « film ancien » cuit dans l'image (sépia, noirs délavés, grain, vignettage, poussières,
            rayures, léger scintillement et flottement de projection) — tout est déterministe (graine fixe).
Sortie 1080x1920, 30 i/s, H.264 CRF 16.
"""
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image
from transformers import pipeline

W, H, FPS = 1080, 1920, 30


def ease(p, kind):
    if kind == "lin":
        return p
    if kind == "out":
        return 1 - (1 - p) ** 3
    return p * p * (3 - 2 * p)


def retro_fx(fr, i, rng, W, H):
    """Film ancien : virage sépia, courbe délavée, scintillement, grain, vignettage, poussières et rayures."""
    lum = fr @ np.array([0.299, 0.587, 0.114], np.float32)
    lum = np.clip((lum - 0.04) * 1.12, 0, 1)
    lum = 0.07 + 0.86 * (lum ** 0.95)                                   # noirs délavés, blancs adoucis
    flick = 1 + 0.035 * np.sin(i * 1.7) + 0.02 * np.sin(i * 0.53 + 1.3)   # scintillement doux
    lum = lum * flick
    sep = lum[..., None] * np.array([1.06, 0.90, 0.68], np.float32)     # virage sépia
    out = 0.88 * sep + 0.12 * fr * lum[..., None] / (fr.mean(-1, keepdims=True) + 1e-3) * 0.9
    g = rng.normal(0, 0.05, (H // 2, W // 2)).astype(np.float32)
    out += cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    yy, xx = np.ogrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    out *= (1 - 0.55 * np.clip(r - 0.45, 0, 1) ** 1.4)[..., None]
    for _ in range(rng.integers(2, 7)):                                 # poussières
        x, y, rad = int(rng.integers(0, W)), int(rng.integers(0, H)), int(rng.integers(2, 6))
        cv2.circle(out, (x, y), rad, (0.08, 0.06, 0.05) if rng.random() < 0.7 else (0.95, 0.9, 0.8), -1, cv2.LINE_AA)
    if i % 37 < 9:                                                      # rayure verticale qui persiste quelques images
        x = int(W * (0.2 + 0.6 * ((i // 37) * 0.37 % 1))) + int(3 * np.sin(i))
        cv2.line(out, (x, 0), (x + int(rng.integers(-6, 6)), H), (0.85, 0.8, 0.7), 1, cv2.LINE_AA)
    return np.clip(out, 0, 1)


def main():
    src, dst, dur = sys.argv[1], sys.argv[2], float(sys.argv[3])
    a = [float(v) for v in sys.argv[4].split(",")]
    b = [float(v) for v in sys.argv[5].split(",")]
    opt = dict(o.split("=") for o in sys.argv[6:])
    k, warm, ek = float(opt.get("k", 0.06)), opt.get("warm", "1") == "1", opt.get("ease", "io")
    retro = opt.get("retro", "0") == "1"
    rng = np.random.default_rng(7)
    im = Image.open(src).convert("RGB")
    iw, ih = im.size
    img = np.asarray(im).astype(np.float32) / 255
    small = im.copy()
    small.thumbnail((1024, 1024))
    d = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf")(small)["predicted_depth"].squeeze().numpy()
    d = cv2.resize(d.astype(np.float32), (iw, ih), interpolation=cv2.INTER_CUBIC)
    d = (d - np.percentile(d, 2)) / (np.percentile(d, 99) - np.percentile(d, 2) + 1e-6)
    d = cv2.GaussianBlur(np.clip(d, 0, 1), (0, 0), max(3, iw / 300)).astype(np.float32)     # 1 = proche
    if warm:   # même étalonnage chaud que le film Origines
        lum = img.mean(-1, keepdims=True)
        img = np.clip((img - 0.5) * 1.05 + 0.5 + (1 - lum) * np.array([-0.008, 0.0, 0.012]) + lum * np.array([0.025, 0.01, -0.015]), 0, 1)
    img = img.astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    u, v = (xx - W / 2) / W, (yy - H / 2) / H          # coordonnées écran centrées
    n = int(round(dur * FPS))
    wr = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", dst], stdin=subprocess.PIPE)
    x0, y0, h0 = a
    for i in range(n):
        p = ease(i / max(1, n - 1), ek)
        cx, cy, hf = [a[j] + (b[j] - a[j]) * p for j in range(3)]
        fh = hf * ih                      # hauteur du cadre (px image)
        fw = fh * W / H
        # mouvement de caméra relatif au départ → décalage de parallaxe par profondeur
        mx, my = (cx - x0) * iw / fw, (cy - y0) * ih / fh       # en « écrans »
        zoom = h0 / hf - 1
        sx = cx * iw + u * fw
        sy = cy * ih + v * fh
        if retro:   # flottement de projection (sous le pixel près, 0,1 % de l'écran)
            sx = sx + 1.2 * np.sin(i * 0.9) * fw / W
            sy = sy + 1.6 * np.sin(i * 0.61 + 0.5) * fh / H
        dd = cv2.remap(d, sx, sy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE) - 0.45
        # proches : déplacés davantage dans le sens du mouvement et grossis davantage pendant l'avancée
        sx = sx + dd * k * (mx * fw + u * fw * zoom * 2.0)
        sy = sy + dd * k * (my * fh + v * fh * zoom * 2.0)
        fr = cv2.remap(img, sx, sy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        if retro:
            fr = retro_fx(fr, i, rng, W, H)
        wr.stdin.write((np.clip(fr, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
    wr.stdin.close()
    wr.wait()
    print(dst, n, "images")


if __name__ == "__main__":
    main()
