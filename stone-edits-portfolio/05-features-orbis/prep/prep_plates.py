"""Project 05 plates (Pexels License): 35147280 robot hero (brand removed), 7641526 close-up,
36714313 living room, 7412033 phone."""
import cv2, numpy as np, sys
from PIL import Image
SRC, OUT = sys.argv[1], sys.argv[2]
def grade(f, warm=0.0, sat=1.0, lift=0.0, con=1.0):
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)[..., None]
    f = g + (f - g) * sat
    f = f * np.array([1.0 + 0.04 * (1 - warm), 1.0, 1.0 - 0.04 * (1 - warm)])   # cool blue-ish by default
    return np.clip((f - 0.5) * con + 0.5 + lift, 0, 1)
rd = lambda n: cv2.imread(f"{SRC}/{n}.jpg").astype(np.float32) / 255
# ---- hero robot: remove the real brand mark, 16:9 crop
im = rd("35147280")
m = np.zeros(im.shape[:2], np.uint8)
x0, y0, x1, y1 = 3740, 2380, 4210, 2700
g8 = cv2.cvtColor((im * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
sub = g8[y0:y1, x0:x1]
local = cv2.GaussianBlur(sub, (0, 0), 25)
m[y0:y1, x0:x1] = ((local.astype(int) - sub.astype(int)) > 12).astype(np.uint8) * 255
m = cv2.dilate(m, np.ones((15, 15), np.uint8))
im8 = cv2.inpaint((im * 255).astype(np.uint8), m, 15, cv2.INPAINT_TELEA)
im = im8.astype(np.float32) / 255
cv2.imwrite("/tmp/claude-0/-home-user-Enomah/472f2c9a-427e-531d-829b-c674d5865f37/scratchpad/logo_check.jpg", im8[y0 - 150:y1 + 150, x0 - 200:x1 + 200])
H0 = 3240; Y0 = 780
hero = grade(im[Y0:Y0 + H0], sat=0.85, con=1.04)
cv2.imwrite(f"{OUT}/hero.jpg", (cv2.resize(hero, (2880, 1620), interpolation=cv2.INTER_AREA) * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
from rembg import remove, new_session
cut = remove(Image.fromarray(cv2.cvtColor(im8, cv2.COLOR_BGR2RGB)).resize((1920, 1440), Image.LANCZOS), session=new_session("birefnet-general"))
a = np.array(cut.split()[3].resize((5760, 4320), Image.LANCZOS))
bb = cv2.boundingRect((a > 20).astype(np.uint8)); print("robot bbox", bb)
bx, by, bw, bh = bb
rob = grade(im[by:by + bh, bx:bx + bw], sat=0.85, con=1.04)
s = 1400 / bw
cv2.imwrite(f"{OUT}/robot.webp", np.dstack([(cv2.resize(rob, (1400, int(bh * s)), interpolation=cv2.INTER_AREA) * 255).astype(np.uint8),
            cv2.resize(a[by:by + bh, bx:bx + bw], (1400, int(bh * s)), interpolation=cv2.INTER_AREA)]), [cv2.IMWRITE_WEBP_QUALITY, 92])
print("robot.webp", 1400, int(bh * s), "scale", s, "logo area in cut px", ((3740 - bx) * s, (2380 - by) * s, (4210 - bx) * s, (2700 - by) * s))
print("hero logo area in hero px", ((3740) * 0.5, (2380 - Y0) * 0.5, 4210 * 0.5, (2700 - Y0) * 0.5))
# ---- close-up on hex tiles: orange accent -> mint
c = rd("7641526")
hsv = cv2.cvtColor((c * 255).astype(np.uint8), cv2.COLOR_BGR2HSV)
org = ((hsv[..., 0] < 22) | (hsv[..., 0] > 170)) & (hsv[..., 1] > 90)
hsv[..., 0] = np.where(org, 80, hsv[..., 0]); hsv[..., 1] = np.where(org, np.minimum(hsv[..., 1], 170), hsv[..., 1])
c = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR).astype(np.float32) / 255
c = grade(c[500:500 + 3375], sat=0.8)
cv2.imwrite(f"{OUT}/closeup.jpg", (cv2.resize(c, (2880, 1620), interpolation=cv2.INTER_AREA) * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
# ---- living room (already 16:9)
lr = grade(rd("36714313"), warm=0.6, sat=0.95)
cv2.imwrite(f"{OUT}/living.jpg", (cv2.resize(lr, (2880, 1620), interpolation=cv2.INTER_AREA) * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
# ---- phone (portrait), keep native crop around the phone
ph = grade(rd("7412033"), sat=0.7)
X0, PY0, X1, PY1 = 400, 700, 3577, 4700
ph = ph[PY0:PY1, X0:X1]
sc = 1600 / (PY1 - PY0)
cv2.imwrite(f"{OUT}/phone.jpg", (cv2.resize(ph, (int((X1 - X0) * sc), 1600), interpolation=cv2.INTER_AREA) * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
Q = (np.array([[1071, 1410], [2446, 1410], [2476, 3888], [1090, 3888]]) - [X0, PY0]) * sc
print("phone.jpg", int((X1 - X0) * sc), 1600, "screen quad", Q.round(1).tolist())
# ---- living room: lift the robot out (rug patched from a neighbouring area) so it can drive
lrraw = cv2.imread(f"{SRC}/36714313.jpg")
rx0, ry0, rx1, ry1 = 1590, 1680, 2150, 1920
crop = lrraw[ry0 - 40:ry1 + 20, rx0 - 40:rx1 + 40]
from rembg import remove as _rm
rc = _rm(Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)), session=new_session("birefnet-general"))
ra = np.array(rc.split()[3]); ra = cv2.GaussianBlur(cv2.erode(ra, np.ones((3, 3), np.uint8)), (3, 3), 0)
rob2 = grade(crop.astype(np.float32) / 255, warm=0.6, sat=0.95)
hsv = cv2.cvtColor((rob2 * 255).astype(np.uint8), cv2.COLOR_BGR2HSV)
org = ((hsv[..., 0] < 22) | (hsv[..., 0] > 170)) & (hsv[..., 1] > 90)
hsv[..., 0] = np.where(org, 80, hsv[..., 0])
rob2 = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
cv2.imwrite(f"{OUT}/living-robot.webp", np.dstack([rob2, ra]), [cv2.IMWRITE_WEBP_QUALITY, 92])
print("living-robot", crop.shape[1], crop.shape[0], "at", rx0 - 40, ry0 - 40)
hole = np.zeros(lrraw.shape[:2], np.float32)
hole[ry0 - 40:ry1 + 20, rx0 - 40:rx1 + 40] = cv2.dilate(ra, np.ones((25, 25), np.uint8)).astype(np.float32) / 255
hole = cv2.GaussianBlur(hole, (0, 0), 8)[..., None]
donor = np.roll(lrraw, 620, axis=1).astype(np.float32)      # rug texture from the left
filled = lrraw * (1 - hole) + donor * hole
lr2 = grade(filled.astype(np.float32) / 255, warm=0.6, sat=0.95)
cv2.imwrite(f"{OUT}/living-empty.jpg", (cv2.resize(lr2, (2880, 1620), interpolation=cv2.INTER_AREA) * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
