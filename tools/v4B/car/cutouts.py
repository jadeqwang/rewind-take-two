#!/usr/bin/env python3
"""Cut-outs for the animated 1:30 car shot (Jade, after 0130_car.mp4: "would be better if it were animated").
Free: everything comes from the two engraved stills. Polygons are in design px (1920x1080 of each still under 'cover').
    ~/Documents/moongazing/.venv/bin/python tools/v4B/car/cutouts.py
writes, beside the stills:
  media/shots/V2f3/wide_cabin.png    the wide with the windows cut out (road ahead + sky/gantry), alpha
  media/shots/V2f3/wide_gantry.png   only the sky band with the gantry and sign (+ margin below the header), alpha
  media/shots/V2f4/close_pad.png     the close still on a black margin (so the hand-over never shows the wide's edge)
  media/shots/V2f4/car_{hero,left,right}.png   each pursuing sedan in the mirror on its own, alpha (full frame)
"""
import os

from PIL import Image, ImageDraw, ImageFilter

ROOT = "/home/jade/Documents/rewind-take-two"
WIDE = os.path.join(ROOT, "media/shots/V2f3/kf_wide_b_fix_engraved.png")
CLOSE = os.path.join(ROOT, "media/shots/V2f4/kf_close_b2_engraved.png")

# wide: the road ahead through the windshield (between her face / the A pillar and the passenger seat, above the wheel
# and dash) and the sky band above the windshield header with the gantry
ROAD = [(632, 318), (1030, 316), (1640, 318), (1920, 300), (1920, 488), (1622, 492), (1622, 700), (1150, 694), (1120, 650),
        (1050, 622), (950, 610), (850, 612), (760, 628), (700, 645), (645, 642), (628, 560), (612, 470), (605, 380)]
MIRROR = [(1132, 352), (1540, 352), (1540, 518), (1132, 518)]           # stays in the cabin layer (with its stalk)
STALK = [(1300, 300), (1360, 300), (1360, 356), (1300, 356)]
SKY = [(545, 0), (1920, 0), (1920, 203), (1642, 214), (1640, 283), (1030, 283), (1000, 254), (545, 254)]
SKY_MARGIN = [(545, 0), (1920, 0), (1920, 420), (545, 420)]             # the gantry layer reaches below the header
# close: the three nearest sedans (light bar to bumper), each its own layer
CARS = {
    "hero": [(835, 368), (1080, 368), (1150, 448), (1185, 520), (1212, 560), (1218, 700), (1204, 748), (722, 748), (712, 700),
             (716, 560), (758, 450), (800, 398)],
    "left": [(438, 402), (622, 402), (645, 448), (684, 480), (684, 602), (604, 668), (282, 654), (276, 560), (318, 478), (398, 438)],
    "right": [(1338, 404), (1522, 404), (1562, 448), (1642, 518), (1654, 600), (1642, 652), (1352, 668), (1266, 642), (1252, 560),
              (1268, 470), (1318, 440)],
}


def mask(size, k, polys, minus=(), feather=2.0):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    for p in polys:
        d.polygon([(x * k, y * k) for x, y in p], fill=255)
    for p in minus:
        d.polygon([(x * k, y * k) for x, y in p], fill=0)
    return m.filter(ImageFilter.GaussianBlur(feather * k))


def rgba(im, a, out):
    o = im.copy()
    o.putalpha(a)
    o.save(out)
    print("wrote", os.path.relpath(out, ROOT))


w = Image.open(WIDE).convert("RGB")
kw = w.width / 1920
holes = mask(w.size, kw, [ROAD, SKY], minus=[MIRROR, STALK], feather=1.5)
rgba(w, Image.eval(holes, lambda v: 255 - v), os.path.join(ROOT, "media/shots/V2f3/wide_cabin.png"))
# the gantry layer: only the sky band above the windshield header (it grows about a point ON the header line, so its
# lower edge never leaves the header and no gap or second header can show)
import numpy as np  # noqa: E402
rgba(w, mask(w.size, kw, [SKY], feather=1.0), os.path.join(ROOT, "media/shots/V2f3/wide_gantry.png"))

c = Image.open(CLOSE).convert("RGB")
kc = c.width / 1920
for name, poly in CARS.items():
    rgba(c, mask(c.size, kc, [poly], feather=2.5), os.path.join(ROOT, f"media/shots/V2f4/car_{name}.png"))
PAD = 0.6    # margin on each side, as a share of the still's size; its alpha falls off smoothly (no edge)
pw, ph = round(c.width * (1 + 2 * PAD)), round(c.height * (1 + 2 * PAD))
ox, oy = round(c.width * PAD), round(c.height * PAD)
pw, ph = c.width + 2 * ox, c.height + 2 * oy
# the margin continues the still by reflection (headliner above, the dark below), blurred more the further out it is
from PIL import ImageFilter as IF  # noqa: E402
ref = np.pad(np.asarray(c), ((oy, oy), (ox, ox), (0, 0)), mode="reflect")
ref = Image.fromarray(ref)
blur = ref.filter(IF.GaussianBlur(c.width * 0.02))
yy0, xx0 = np.mgrid[0:ph, 0:pw].astype(np.float32)
d0 = np.maximum(np.maximum(0, np.maximum(ox - xx0, xx0 - (ox + c.width))) / ox, np.maximum(0, np.maximum(oy - yy0, yy0 - (oy + c.height))) / oy)
kb = np.clip(d0 * 4, 0, 1)[..., None]
pad = Image.fromarray((np.asarray(ref) * (1 - kb) + np.asarray(blur) * kb).astype(np.uint8))
pad.paste(c, (ox, oy))
yy, xx = np.mgrid[0:ph, 0:pw].astype(np.float32)
dx = np.maximum(0, np.maximum(ox - xx, xx - (ox + c.width))) / ox
dy = np.maximum(0, np.maximum(oy - yy, yy - (oy + c.height))) / oy
fall = np.clip(1 - np.maximum(dx, dy) * 1.05, 0, 1)
rgba(pad, Image.fromarray((fall * fall * (3 - 2 * fall) * 255).astype(np.uint8)), os.path.join(ROOT, "media/shots/V2f4/close_pad.png"))
print("pad factor", (1 + 2 * PAD))
