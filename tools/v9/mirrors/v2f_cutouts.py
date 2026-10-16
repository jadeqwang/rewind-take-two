#!/usr/bin/env python3
"""v9 fix #3 (C_V2f_car): the two new layers of the 1:30 wide, cut from the engraved roof edit
media/shots/V2f3/v9_roof_a_engraved.png (nano-banana edit of the wide still, tools/v9/mirrors/gen.py v2f_roof_a):

  media/shots/V2f3/v9_roof.png    the cabin top: roof liner, both sun visors, the windshield header, the mirror's mount
                                  and stem, the right A-pillar and the passenger-side glass beside it (alpha). Where she
                                  is in the edit the roof liner is inpainted, so the take's moving Jade (drawn over it
                                  through the take's matte) never shows a second bun.
  media/shots/V2f3/v9_gantry.png  the overhead sign gantry, now seen THROUGH the windshield below the header (alpha:
                                  the sign panel solid, the truss and posts keyed by luminance).

    tools/engrave/.venv/bin/python tools/v9/mirrors/v2f_cutouts.py      (needs cv2)
All polygons in design px (1920x1080).
"""
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = "/home/jade/Documents/rewind-take-two"
SRC = os.path.join(ROOT, "media/shots/V2f3/v9_roof_a_engraved.png")
MATTE = os.path.join(ROOT, "media/shots/V2f3/v9_roof_a_matte/v9_roof_a_matte.png")
OUT_ROOF = os.path.join(ROOT, "media/shots/V2f3/v9_roof_r2c.png")   # round 2: + the painted stem (v9_roof.png = round 1)
OUT_GANTRY = os.path.join(ROOT, "media/shots/V2f3/v9_gantry.png")

# the roof: everything above the header line, the mount + stem down to the mirror's top edge (the engine's mirror body
# covers from y 360), the right A-pillar and the passenger-side glass right of it, down to the passenger seat's top
ROOF = [(0, 0), (1920, 0), (1920, 492), (1655, 492), (1792, 321), (1372, 321), (1368, 342), (1349, 344), (1349, 366),
        (1323, 366), (1323, 344), (1304, 342), (1300, 321), (0, 321)]
# the gantry
SIGN = [(656, 348), (994, 348), (994, 450), (656, 450)]
TRUSS_BOX = [(592, 322), (1090, 322), (1090, 474), (592, 474)]
NO_KEY = [[(978, 322), (1060, 322), (1060, 372), (978, 372)]]   # the starburst right of the truss is a streetlight, not steel


def poly_mask(size, k, polys, feather):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    for p in polys:
        d.polygon([(x * k, y * k) for x, y in p], fill=255)
    return m.filter(ImageFilter.GaussianBlur(feather * k)) if feather else m


def main():
    im = Image.open(SRC).convert("RGB")
    W, H = im.size
    k = W / 1920
    a = np.asarray(im).copy()

    # roof: inpaint her (dilated matte) out of the roof liner first
    jm = np.asarray(Image.open(MATTE).convert("L").resize((W, H)))
    hole = (jm > 8).astype(np.uint8) * 255
    hole = cv2.dilate(hole, np.ones((int(10 * k), int(10 * k)), np.uint8))
    roof_zone = np.asarray(poly_mask((W, H), k, [ROOF], 0)) > 0
    hole[~roof_zone] = 0
    # fill with the same roof liner 620 design px to the right (its hatching is even); a smooth inpaint smeared her
    # hair into a grey halo round the bun
    dx = int(620 * k)
    donor = np.roll(a, -dx, axis=1)
    hb = cv2.GaussianBlur(hole.astype(np.float32) / 255, (0, 0), 2 * k)[..., None]
    filled = (a * (1 - hb) + donor * hb).astype(np.uint8)
    roof = Image.fromarray(filled)
    roof.putalpha(poly_mask((W, H), k, [ROOF], 1.2))
    # round 2: the edit's stem was two pale edges with the night between them; a solid stem from the mount into the
    # mirror housing (the engine's mirror body, top edge y~360, is drawn over its lower end)
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from stem import paint_stem
    roof = paint_stem(roof, k, (1336, 334), (1336, 367), 31, 27)   # wide enough to cover the edit's two pale edges (x 1322-1350)
    roof.save(OUT_ROOF)
    print("wrote", os.path.relpath(OUT_ROOF, ROOT))

    # gantry: the panel solid, the steel keyed (pale lines on the dark sky), inside the truss box
    lum = np.asarray(im.convert("L")).astype(np.float32)
    key = np.clip((lum - 110) / 60, 0, 1)
    key = cv2.dilate(key, np.ones((3, 3), np.uint8))
    box = np.asarray(poly_mask((W, H), k, [TRUSS_BOX], 0)) / 255.0
    nokey = np.asarray(poly_mask((W, H), k, NO_KEY, 0)) / 255.0
    sign = np.asarray(poly_mask((W, H), k, [SIGN], 0.8)) / 255.0
    alpha = np.maximum(sign, key * box * (1 - nokey))
    alpha = cv2.GaussianBlur(alpha, (0, 0), 0.8 * k)
    g = Image.fromarray(a)
    g.putalpha(Image.fromarray((alpha * 255).astype(np.uint8)))
    g.save(OUT_GANTRY)
    print("wrote", os.path.relpath(OUT_GANTRY, ROOT))


if __name__ == "__main__":
    main()
