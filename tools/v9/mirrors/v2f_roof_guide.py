#!/usr/bin/env python3
"""v9 fix #3 (C_V2f_car): a crude layout guide for the roof edit of the 1:30 wide still.

The v4 wide had no roof: the rear-view mirror floated among the overpass girders. This paints flat grey placeholder
shapes (headliner down to the windscreen header, the mirror's mount and stem, both sun visors folded up, the right
A-pillar) and a placeholder for the overhead sign, now seen THROUGH the windscreen below the header, onto the raw wide
still. nano-banana-pro then redraws them (tools/v9/mirrors/gen.py v2f_roof).

The header height comes from the close still (media/shots/V2f4/kf_close_b2.png): its header line at y~100 maps through
car_shot.js's R / MW / MC to y~334 in the wide, so the push lands on the close's own headliner.
    $PY tools/v9/mirrors/v2f_roof_guide.py   -> media/shots/V2f3/v9_roof_guide.png
"""
import os

from PIL import Image, ImageDraw

ROOT = "/home/jade/Documents/rewind-take-two"
SRC = os.path.join(ROOT, "media/shots/V2f3/kf_wide_b_fix.png")
OUT = os.path.join(ROOT, "media/shots/V2f3/v9_roof_guide.png")
MATTE = os.path.join(ROOT, "media/shots/V2f3/kf_wide_b_fix_matte/kf_wide_b_fix_matte.png")

GREY, LINE = (120, 120, 120), (0, 0, 0)
# design px (1920x1080)
HEADLINER = [(0, 0), (1920, 0), (1920, 318), (1860, 320), (1336, 330), (560, 322), (0, 130)]
VISOR_L = [(250, 200), (720, 250), (720, 312), (250, 262)]
VISOR_R = [(1470, 250), (1840, 246), (1840, 312), (1470, 318)]
MOUNT = [(1300, 300), (1372, 300), (1366, 340), (1306, 340)]
STEM = [(1326, 338), (1346, 338), (1346, 366), (1326, 366)]
PILLAR_R = [(1790, 318), (1920, 314), (1920, 360), (1742, 492), (1660, 492)]
SIGN = [(660, 352), (990, 352), (990, 446), (660, 446)]


def main():
    im = Image.open(SRC).convert("RGB")
    k = im.width / 1920
    d = ImageDraw.Draw(im)
    sc = lambda p: [(x * k, y * k) for x, y in p]
    for poly in (HEADLINER, VISOR_L, VISOR_R, PILLAR_R, MOUNT, STEM):
        d.polygon(sc(poly), fill=GREY, outline=LINE, width=max(2, round(3 * k)))
    d.polygon(sc(SIGN), fill=(30, 30, 30), outline=(230, 230, 230), width=max(2, round(4 * k)))
    # she stays in front of the roof: the still's own matte puts her back over the placeholders
    m = Image.open(MATTE).convert("L").resize(im.size)
    im.paste(Image.open(SRC).convert("RGB"), (0, 0), m)
    im.save(OUT)
    print("wrote", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
