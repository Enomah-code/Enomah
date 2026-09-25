"""Project 04 plates: clean hob (after), greasy hob (before), spray bottle and sponge cut-outs.
Sources (Pexels License): 6653928 hob, 11969601 bottle, 4440528 sponge,
grease built from real textures 9175906 (smudges), 19769300 (rings), 36316675 (speckles)."""
import cv2, numpy as np, sys
from PIL import Image
SRC = sys.argv[1]; OUT = sys.argv[2]
def rd(n): return cv2.imread(f"{SRC}/{n}.jpg").astype(np.float32) / 255

# ---------- hob, 9:16 crop ----------
hob = rd("6653928")
X0, Y0, W, H = 2200, 25, 1300, 2311
crop = hob[Y0:Y0 + H, X0:X0 + W].copy()
after = np.clip((crop - 0.5) * 1.06 + 0.5 + 0.03, 0, 1)
after = after * np.array([1.02, 1.0, 0.97])          # BGR: cooler, crisper whites
after = np.clip(after, 0, 1).astype(np.float32)

# hob surface plane (perspective) and visible hob polygon, in crop px
plane = np.float32([[-395, 1470], [1900, 953], [1900, 2840], [512, 1975]])
poly = np.int32([[-395, 1470], [1025, 1200], [1300, 1235], [1300, 2311], [1050, 2311], [512, 1975]])
mask = np.zeros((H, W), np.float32); cv2.fillPoly(mask, [poly], 1.0)
mask = cv2.GaussianBlur(mask, (0, 0), 14)

def darkness(img, lo, hi):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return np.clip((hi - g) / (hi - lo), 0, 1)

TS = 2048
def to_square(img):
    h, w = img.shape[:2]; s = min(h, w)
    return cv2.resize(img[(h - s) // 2:(h + s) // 2, (w - s) // 2:(w + s) // 2], (TS, TS), interpolation=cv2.INTER_AREA)

smudge = darkness(to_square(rd("9175906")), 0.25, 0.62)
rings = darkness(to_square(rd("19769300")), 0.35, 0.78)
speck = darkness(to_square(rd("36316675")), 0.2, 0.55)
speck = cv2.resize(speck, (TS // 2, TS // 2)); speck = np.tile(speck, (2, 2))   # finer splatter
def warp(t, sx, sy, ox, oy):   # flattened placement over the hob (reads as perspective on a receding surface)
    M = np.float32([[sx, 0, ox], [0, sy, oy]])
    return cv2.warpAffine(t, M, (W, H), borderMode=cv2.BORDER_WRAP)
a_sm = warp(smudge, 0.9, 0.42, -300, 1080) * 0.85
a_rg = warp(rings, 0.75, 0.36, -150, 1150) * 0.8
a_sp = warp(speck, 0.8, 0.4, 0, 1100) * 0.38
# grime concentrates around the burners, with lighter patches elsewhere
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
dens = np.zeros((H, W), np.float32)
for (bx, by, r, k) in ((320, 1650, 330, 1.0), (820, 1420, 300, 0.9), (1220, 2040, 330, 1.0), (80, 1900, 260, 0.7), (1150, 1300, 220, 0.6)):
    dens += k * np.exp(-(((xx - bx) / r) ** 2 + ((yy - by) / (r * 0.55)) ** 2))
rng = np.random.default_rng(4)
noise = cv2.GaussianBlur(rng.random((H // 16, W // 16)).astype(np.float32), (0, 0), 2)
noise = cv2.resize((noise - noise.min()) / (noise.max() - noise.min()), (W, H), interpolation=cv2.INTER_CUBIC)
dens = np.clip(dens * 0.85 + noise * 0.35 - 0.05, 0, 1)
a_sm, a_rg, a_sp = a_sm * dens, a_rg * np.clip(dens * 1.2, 0, 1), a_sp * np.clip(dens + 0.25, 0, 1)
bgr = lambda h: np.array([int(h[5:7], 16), int(h[3:5], 16), int(h[1:3], 16)], np.float32) / 255
before = after.copy()
for a, col in ((a_sm, "#6B5A45"), (a_rg, "#3E3226"), (a_sp, "#3E3226")):
    a = (a * mask)[..., None]
    before = before * (1 - a) + (before * bgr(col) * 1.25).clip(0, 1) * a    # tinted multiply, keeps shading
veil = (mask * (0.18 + 0.3 * dens))[..., None]
before = before * (1 - veil) + before * bgr("#A08A5C") * 1.5 * veil
before = np.clip(before, 0, 1).astype(np.float32)
# brief grading, baked only on the hob: 'before' saturate(0.6) brightness(0.8) sepia(0.25)
g = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)[..., None]
graded = (g + (before - g) * 0.6) * 0.8
sepia = np.dstack([graded[..., 0] * 0.272 + graded[..., 1] * 0.534 + graded[..., 2] * 0.131,
                   graded[..., 0] * 0.349 + graded[..., 1] * 0.686 + graded[..., 2] * 0.168,
                   graded[..., 0] * 0.393 + graded[..., 1] * 0.769 + graded[..., 2] * 0.189])
graded = np.clip(graded * 0.75 + sepia * 0.25, 0, 1)
m3 = mask[..., None]
before = before * (1 - m3) + graded * m3
for name, img in (("hob-after", after), ("hob-before", before)):
    cv2.imwrite(f"{OUT}/{name}.jpg", (img * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 93])

# ---------- cut-outs (alpha from BiRefNet at 1600 px, see run notes) ----------
def cutout(name, alpha_png, box, scale_to, hue=None):
    img = rd(name); h, w = img.shape[:2]
    a = cv2.resize(cv2.imread(alpha_png, 0), (w, h), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255
    x0, y0, x1, y1 = box
    img, a = img[y0:y1, x0:x1], a[y0:y1, x0:x1]
    if hue is not None:   # recolour (sponge -> brand aqua / mint)
        hsv = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.int32)
        hsv[..., 0] = (hsv[..., 0] + hue) % 180
        img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32) / 255
    s = scale_to / img.shape[0]
    img = cv2.resize(img, (int(img.shape[1] * s), scale_to), interpolation=cv2.INTER_AREA)
    a = cv2.resize(a, (img.shape[1], scale_to), interpolation=cv2.INTER_AREA)
    return img, a, s

bot, ba, bs = cutout("11969601", f"{SRC}/11969601_alpha.png", (2691, 390, 4290, 3800), 1800)
g = cv2.cvtColor(bot, cv2.COLOR_BGR2GRAY)[..., None]          # remove the pink cast: neutral white plastic
bot = np.clip(g * np.array([1.0, 0.995, 0.985]) * 1.04, 0, 1)
cv2.imwrite(f"{OUT}/bottle.webp", np.dstack([(bot * 255).astype(np.uint8), (ba * 255).astype(np.uint8)]), [cv2.IMWRITE_WEBP_QUALITY, 92])
print("bottle", bot.shape[1], bot.shape[0], "label quad", ((np.array([[3230, 2250], [4070, 2250], [4070, 3350], [3230, 3350]]) - [2691, 390]) * bs).round(1).tolist())
# sponge: keep the front (lower-right) sponge only
sp, sa, ss = cutout("4440528", f"{SRC}/4440528_alpha.png", (881, 619, 1466, 1277), 600, hue=88)
ys_, xs_ = np.mgrid[0:sa.shape[0], 0:sa.shape[1]]
sa = sa * (ys_ > 190 - 100 * xs_ / sa.shape[1])     # drop the second sponge peeking behind
cv2.imwrite(f"{OUT}/sponge.webp", np.dstack([(sp * 255).astype(np.uint8), (sa * 255).astype(np.uint8)]), [cv2.IMWRITE_WEBP_QUALITY, 92])
print("sponge", sp.shape[1], sp.shape[0])
