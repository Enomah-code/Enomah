"""Project 01 plates (Pexels License): 3585797 earbuds + case (hero), 4271693 black box, 29754884 grille."""
import cv2, numpy as np, sys
from PIL import Image
SRC, OUT = sys.argv[1], sys.argv[2]
def cool(f, sat=0.9, lift=0.0):
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)[..., None]
    f = g + (f - g) * sat
    return np.clip(f * np.array([1.06, 1.0, 0.93]) + lift, 0, 1)   # BGR: cool, slightly teal night studio

# ---------- hero: earbuds in open case ----------
im = cv2.imread(f"{SRC}/3585797.jpg").astype(np.float32) / 255
k = 6936 / 900
# LEDs: red -> electric cyan
for (vx, vy) in ((445, 707), (650, 578)):
    cx, cy = int(vx * k), int(vy * k); r = 60
    roi = im[cy - r:cy + r, cx - r:cx + r]
    red = np.clip((roi[..., 2] - np.maximum(roi[..., 0], roi[..., 1]) - 0.08) * 3, 0, 1)[..., None]
    lum = roi.max(2, keepdims=True)
    cyan = np.concatenate([lum * 1.0, lum * 0.9, lum * 0.0], 2)          # BGR #00E5FF-ish
    im[cy - r:cy + r, cx - r:cx + r] = roi * (1 - red) + cyan * red
# bud masks (ellipses in view coords) -> cut-outs + inpainted case
H0, W0 = im.shape[:2]
buds = [((412, 686), (104, 78), 28), ((608, 568), (96, 70), 28)]
plate = (im * 255).astype(np.uint8)
holes = np.zeros((H0, W0), np.uint8)
for i, ((vx, vy), (ax, ay), ang) in enumerate(buds):
    m = np.zeros((H0, W0), np.uint8)
    cv2.ellipse(m, (int(vx * k), int(vy * k)), (int(ax * k), int(ay * k)), ang, 0, 360, 255, -1)
    ms = cv2.GaussianBlur(m, (0, 0), 6)
    x, y, w, h = cv2.boundingRect(m); pad = 40
    x0, y0, x1, y1 = x - pad, y - pad, x + w + pad, y + h + pad
    cut = np.dstack([(cool(im[y0:y1, x0:x1]) * 255).astype(np.uint8), ms[y0:y1, x0:x1]])
    cv2.imwrite(f"{OUT}/bud{i + 1}.webp", cut, [cv2.IMWRITE_WEBP_QUALITY, 92])
    print(f"bud{i + 1}", "box", x0, y0, x1 - x0, y1 - y0)
    holes |= m
# fill the cavities: dark soft cavity (inpaint at 1/6)
q = 6
small = cv2.resize(plate, (W0 // q, H0 // q), interpolation=cv2.INTER_AREA)
hs = cv2.dilate(cv2.resize(holes, (W0 // q, H0 // q), interpolation=cv2.INTER_NEAREST), np.ones((5, 5), np.uint8))
filled = cv2.inpaint(small, hs, 9, cv2.INPAINT_TELEA)
filled = (filled.astype(np.float32) * 0.55).astype(np.uint8)          # cavities read darker
filled = cv2.resize(filled, (W0, H0), interpolation=cv2.INTER_CUBIC)
hb = cv2.GaussianBlur(holes, (0, 0), 10).astype(np.float32)[..., None] / 255
empty = (plate * (1 - hb) + filled * hb).astype(np.uint8)
X0, X1 = 867, 6069                                                     # 9:16 crop
for name, src in (("hero", plate), ("hero-empty", empty)):
    f = cool(src[:, X0:X1].astype(np.float32) / 255)
    cv2.imwrite(f"{OUT}/{name}.jpg", (cv2.resize(f, (1620, 2880), interpolation=cv2.INTER_AREA) * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
print("hero crop x0", X0, "scale", 1620 / (X1 - X0))
# macro crops (native resolution, 9:16) for the texture scene
def macro(name, cx, cy, w, extra=None):
    h = int(w * 16 / 9); x0, y0 = int(cx - w / 2), int(cy - h / 2)
    f = cool(im[y0:y0 + h, x0:x0 + w], sat=0.6, lift=0.02)
    if extra: f = extra(f)
    cv2.imwrite(f"{OUT}/{name}.jpg", (cv2.resize(f, (1080, 1920), interpolation=cv2.INTER_AREA) * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
macro("m-case", int(560 * k), int(860 * k), 1400, lambda f: np.clip((f - 0.02) * 2.4, 0, 1))
macro("m-bud", int(420 * k), int(672 * k), 900, lambda f: np.clip((f - 0.02) * 2.0, 0, 1))
g = cv2.imread(f"{SRC}/29754884.jpg").astype(np.float32) / 255
gh = g.shape[0]; gw = int(gh * 9 / 16); gx = (g.shape[1] - gw) // 2
cv2.imwrite(f"{OUT}/m-grille.jpg", (cv2.resize(cool(g[:, gx:gx + gw], sat=0.3), (1080, 1920), interpolation=cv2.INTER_AREA) * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
# dark surface plate from the hero photo's floor
surf = cool(im[7400:9248, 0:3400], sat=0.5)
cv2.imwrite(f"{OUT}/surface.jpg", (cv2.resize(surf, (1400, 760)) * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 90])
# ---------- box (closed, top view) ----------
bx = cv2.imread(f"{SRC}/4271693.jpg")[2180:3720, 1930:3410]
from rembg import remove, new_session
cut = remove(Image.fromarray(cv2.cvtColor(bx, cv2.COLOR_BGR2RGB)), session=new_session("birefnet-general"))
a = np.array(cut.split()[3])
a = cv2.GaussianBlur(cv2.erode(a, np.ones((5, 5), np.uint8)), (3, 3), 0)
f = cool(bx.astype(np.float32) / 255, sat=0.4)
f = np.clip((f - 0.05) * 1.1, 0, 1)
cv2.imwrite(f"{OUT}/box.webp", np.dstack([(f * 255).astype(np.uint8), a]), [cv2.IMWRITE_WEBP_QUALITY, 92])
print("box", bx.shape[1], bx.shape[0])
