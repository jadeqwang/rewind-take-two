#!/usr/bin/env python3
"""Local (free) fixes to the chosen wide keyframe of the 1:30 car shot:
  1. the left pencil's eraser recoloured pale blue (canon: one pink eraser = graphite, one pale-blue = rainbow; the
     model drew two pink ones);
  2. the close keyframe's mirror laid back in where the model drew the mirror, so the engine's push into the mirror
     ends in register on media/shots/V2f4/kf_close_b2.png.
    ~/Documents/moongazing/.venv/bin/python tools/v4B/car/fix_wide.py   -> media/shots/V2f3/kf_wide_b_fix.png (+ .json)
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kf  # noqa: E402

ROOT = kf.ROOT
SRC, CLOSE, OUT = "media/shots/V2f3/kf_wide_b.jpg", "media/shots/V2f4/kf_close_b2.png", "media/shots/V2f3/kf_wide_b_fix.png"
ERASER = (100, 155, 172, 215)               # box round the left pencil's eraser, source px (2580x1451)
BLUE = np.array([141, 184, 232], float)     # #8DB8E8, the canon pale blue
MIRROR_IN_WIDE = dict(x=1138.6, y=360.0, w=394.4)   # measured mirror body in kf_wide_b, design px (1920 wide)

im = Image.open(os.path.join(ROOT, SRC)).convert("RGB")
a = np.asarray(im).astype(float)
x0, y0, x1, y1 = ERASER
reg = a[y0:y1, x0:x1]
r, g, b = reg[..., 0], reg[..., 1], reg[..., 2]
pink = (r > 150) & (r - g > 25) & (r - b > 10)            # pink eraser pixels (not the silver ferrule, not the yellow wood)
m = Image.fromarray((pink * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
m = np.asarray(m).astype(float)[..., None] / 255
lum = (0.3 * r + 0.59 * g + 0.11 * b)[..., None]
blue = np.clip(BLUE * lum / 200.0, 0, 255)                 # keep the eraser's shading
a[y0:y1, x0:x1] = reg * (1 - m) + blue * m
im = Image.fromarray(a.round().astype(np.uint8))
print("eraser pixels recoloured:", int(pink.sum()))

kf.MIRROR_DST = MIRROR_IN_WIDE
box = kf.lay_mirror(im, CLOSE)
im.save(os.path.join(ROOT, OUT))
im.save(os.path.join(ROOT, OUT.replace(".png", ".jpg")), quality=94)
json.dump({"source": SRC, "close": CLOSE, "close_src_box_px": kf.MIRROR_SRC, "mirror_box_design_px": box,
           "eraser_box_px": ERASER}, open(os.path.join(ROOT, OUT.replace(".png", ".json")), "w"), indent=1)
print("wrote", OUT, "mirror box (design px)", [round(v, 1) for v in box])
