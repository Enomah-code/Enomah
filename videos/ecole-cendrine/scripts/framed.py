"""Plan « image encadrée » pour une photo presque carrée (ex. le pagne) : l'image entière au centre, avec ombre,
lente avancée, sur un fond = la même image agrandie, floutée et assombrie. Sortie 1080x1920, 30 i/s.
Usage : python3 scripts/framed.py <image> <sortie.mp4> <durée>"""
import subprocess
import sys

import cv2
import numpy as np

W, H, FPS = 1080, 1920, 30
src, dst, dur = sys.argv[1], sys.argv[2], float(sys.argv[3])
img = cv2.cvtColor(cv2.imread(src), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
ih, iw = img.shape[:2]
r = max(W / iw, H / ih) * 1.1
bg = cv2.resize(img, (int(iw * r), int(ih * r)), interpolation=cv2.INTER_AREA)
y0, x0 = (bg.shape[0] - H) // 2, (bg.shape[1] - W) // 2
bg = cv2.GaussianBlur(bg[y0:y0 + H, x0:x0 + W], (0, 0), 40) * 0.45
fw = 960
fh = int(ih * fw / iw)
fg = cv2.resize(img, (fw, fh), interpolation=cv2.INTER_AREA)
n = int(round(dur * FPS))
wr = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", dst], stdin=subprocess.PIPE)
for i in range(n):
    p = i / max(1, n - 1)
    e = 1 - (1 - p) ** 2
    s = 1.0 + 0.10 * e
    fr = bg.copy()
    sw, sh = int(fw * s), int(fh * s)
    f2 = cv2.resize(fg, (sw, sh), interpolation=cv2.INTER_CUBIC)
    x, y = (W - sw) // 2, int(H * 0.40 - sh / 2)
    # ombre portée douce
    sh_mask = np.zeros((H, W), np.float32)
    cv2.rectangle(sh_mask, (x + 10, y + 24), (x + sw + 10, y + sh + 24), 1, -1)
    sh_mask = cv2.GaussianBlur(sh_mask, (0, 0), 30)
    fr *= (1 - 0.6 * sh_mask)[..., None]
    ya, yb, xa, xb = max(0, y), min(H, y + sh), max(0, x), min(W, x + sw)
    fr[ya:yb, xa:xb] = f2[ya - y:yb - y, xa - x:xb - x]
    wr.stdin.write((np.clip(fr, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
wr.stdin.close()
wr.wait()
print(dst, n, "images")
