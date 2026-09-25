"""Project 03 plates (Pexels License). Act 1 = cold / desaturated, act 2 = warm / appetising.
36895441, 36895463, 36895504 onion + knife ; 37261932, 37261913, 37261919 manual chopper ;
37292883 diced onion, 32960544 carrot slices, 19362627 grated cheese."""
import cv2, numpy as np, sys
SRC, OUT = sys.argv[1], sys.argv[2]
W, H = 1350, 2400
PLATES = {   # name: (photo, x0, x1, y0, y1, grade)
    "p-knife-a": ("36895441", 3200, 5540, 0, 4160, "cold"),
    "p-knife-b": ("36895463", 3470, 5790, 0, 4124, "cold"),
    "p-mess":    ("36895504", 3100, 5370, 0, 4040, "cold"),
    "k-hero":    ("37261932", 437, 3791, 0, 5963, "warm"),
    "k-press":   ("37261913", 684, 3784, 0, 5512, "warm"),
    "k-open":    ("37261919", 0, 3416, 0, 6073, "warm"),
    "r-onion":   ("37292883", 1200, 2200, 1750, 3528, "warm"),
    "r-carrot":  ("32960544", 378, 2646, 0, 4032, "warm"),
    "r-cheese":  ("19362627", 1924, 4426, 0, 4448, "warm"),
}
def grade(img, kind):
    f = img.astype(np.float32) / 255
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)[..., None]
    if kind == "cold":   # tense: desaturated, blue-grey, crushed
        f = g + (f - g) * 0.35
        f = f * np.array([1.08, 0.98, 0.9]) * 0.92
        f = np.clip((f - 0.5) * 1.12 + 0.5, 0, 1)
    else:                # warm, bright cream highlights, juicy colour
        f = g + (f - g) * 1.18
        f = f * np.array([0.95, 1.0, 1.05])
        f = np.clip((f - 0.5) * 1.05 + 0.53, 0, 1)
    return (f * 255).astype(np.uint8)
for name, (ph, x0, x1, y0, y1, kind) in PLATES.items():
    im = cv2.imread(f"{SRC}/{ph}.jpg")[y0:y1, x0:x1]
    im = cv2.resize(im, (W, H), interpolation=cv2.INTER_AREA)
    cv2.imwrite(f"{OUT}/{name}.jpg", grade(im, kind), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(name, "aspect", round((x1 - x0) / (y1 - y0), 4))
