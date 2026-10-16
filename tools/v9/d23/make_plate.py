#!/usr/bin/env python3
"""Jade's RGBA plate for the d23 scene card: plate_c_tip.png (nano-banana, pencil tip repainted) + BiRefNet matte
(tools/engrave/engrave_still.py --matte-out), the painted blot beside the new pencil tip taken out of the matte,
upscaled 2x with Real-ESRGAN animevideov3 in tiles (the card is seen up to ~2.5x magnified at the two-shot).
Run with tools/engrave/.venv/bin/python:  make_plate.py PLATE MATTE OUT"""
import math, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, 'tools/engrave')
from upscale import Upscaler
plate, matte, out = sys.argv[1:4]
rgb = np.asarray(Image.open(plate).convert('RGB'))
m = Image.open(matte).convert('L')
# the blot painted over the old eraser (pencil_tip.py) minus the new cone: not part of her
ax = (-0.65, 0.76); n = math.hypot(*ax); ax = (ax[0] / n, ax[1] / n); pp = (ax[1], -ax[0]); base = (553.0, 598.0); hw = 26.0
P = lambda o, a, b: (o[0] + ax[0] * a + pp[0] * b, o[1] + ax[1] * a + pp[1] * b)
cut = Image.new('L', m.size, 0); d = ImageDraw.Draw(cut)
d.polygon([P(base, -4, -hw - 8), P(base, -4, hw + 8), P(base, 110, hw + 12), P(base, 110, -hw - 12)], fill=255)
d.polygon([P(base, -6, -hw - 2), P(base, -6, hw + 2), P(base, 78, 0)], fill=0)
m = np.asarray(m).astype(np.float32) * (1 - np.asarray(cut, np.float32) / 255)
H, W = rgb.shape[:2]; S = 2
up = Upscaler('animevideov3', 0, 0)
T, O = 512, 32
big = np.zeros((H * S, W * S, 3), np.uint8)
for y0 in range(0, H, T):
    for x0 in range(0, W, T):
        xa, ya, xb, yb = max(0, x0 - O), max(0, y0 - O), min(W, x0 + T + O), min(H, y0 + T + O)
        up.ow, up.oh = (xb - xa) * S, (yb - ya) * S
        tile = up(np.ascontiguousarray(rgb[ya:yb, xa:xb]))
        cx0, cy0 = (x0 - xa) * S, (y0 - ya) * S
        cw, ch = (min(W, x0 + T) - x0) * S, (min(H, y0 + T) - y0) * S
        big[y0 * S:y0 * S + ch, x0 * S:x0 * S + cw] = tile[cy0:cy0 + ch, cx0:cx0 + cw]
a = np.asarray(Image.fromarray(m.astype(np.uint8)).resize((W * S, H * S), Image.BICUBIC))
Image.fromarray(np.dstack([big, a])).save(out)
print('wrote', out, big.shape)
