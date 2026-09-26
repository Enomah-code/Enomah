"""Project 06 stills (Pexels License): 2081199 olive backpack -> cut-out for the iconic shot + detail macros."""
import cv2, numpy as np, sys
from PIL import Image
from rembg import remove, new_session
SRC, OUT = sys.argv[1], sys.argv[2]
im = cv2.imread(f"{SRC}/2081199.jpg")
def macro(name, x0, y0, w):
    h = int(w * 5 / 4)
    c = cv2.resize(im[y0:y0 + h, x0:x0 + w], (1080, 1350), interpolation=cv2.INTER_CUBIC)
    cv2.imwrite(f"{OUT}/{name}.jpg", c, [cv2.IMWRITE_JPEG_QUALITY, 92])
macro("m-zip", 160, 2600, 800)
macro("m-strap", 1250, 1760, 1100)
cut = remove(Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).resize((1600, 1929), Image.LANCZOS), session=new_session("birefnet-general"))
a = np.array(cut.split()[3].resize((4000, 4822), Image.LANCZOS))
x, y, w, h = cv2.boundingRect((a > 20).astype(np.uint8)); print("bag bbox", x, y, w, h)
a = cv2.GaussianBlur(cv2.erode(a, np.ones((5, 5), np.uint8)), (3, 3), 0)
pad = 20
x0, y0, x1, y1 = max(0, x - pad), max(0, y - pad), min(4000, x + w + pad), min(4822, y + h + pad)
bag = np.dstack([im[y0:y1, x0:x1], a[y0:y1, x0:x1]])
s = 1300 / (y1 - y0)
bag = cv2.resize(bag, (int((x1 - x0) * s), 1300), interpolation=cv2.INTER_AREA)
cv2.imwrite(f"{OUT}/bag.webp", bag, [cv2.IMWRITE_WEBP_QUALITY, 92]); print("bag.webp", bag.shape[1], bag.shape[0])
# floor: the photo's own stone ledge, darkened into a night studio surface
floor = im[4250:4822, 0:4000]
floor = cv2.resize(floor, (1600, 229))
floor = (floor.astype(np.float32) * 0.35).astype(np.uint8)
cv2.imwrite(f"{OUT}/floor.jpg", floor, [cv2.IMWRITE_JPEG_QUALITY, 90])
