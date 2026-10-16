#!/usr/bin/env python3
"""plate_c: the lower end of the blue-eraser pencil came back with a second (pink) eraser. Paint it out (ink, like the
dark around it) and give that end a sharpened wooden point with a graphite tip, along the pencil's own axis."""
import math, sys
from PIL import Image, ImageDraw
src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB'); d = ImageDraw.Draw(im)
ax = (-0.65, 0.76); n = math.hypot(*ax); ax = (ax[0] / n, ax[1] / n); pp = (ax[1], -ax[0])
base = (553.0, 598.0); hw = 26.0
P = lambda o, a, b: (o[0] + ax[0] * a + pp[0] * b, o[1] + ax[1] * a + pp[1] * b)
# blot out ferrule + eraser
d.polygon([P(base, -4, -hw - 6), P(base, -4, hw + 6), P(base, 105, hw + 10), P(base, 105, -hw - 10)], fill=(8, 8, 9))
# sharpened cone (shaved wood) and graphite point
L, G = 74, 20
d.polygon([P(base, -2, -hw), P(base, -2, hw), P(base, L - G, hw * G / L), P(base, L - G, -hw * G / L)], fill=(238, 203, 150))
d.polygon([P(base, L - G, -hw * G / L), P(base, L - G, hw * G / L), P(base, L, 0)], fill=(52, 52, 56))
for b in (-hw * 0.35, hw * 0.3):   # the scalloped shaving edge lines
    d.line([P(base, 0, b), P(base, 18, b * 0.78)], fill=(120, 80, 40), width=2)
d.line([P(base, -2, -hw), P(base, L, 0), P(base, -2, hw)], fill=(10, 10, 10), width=4)
d.line([P(base, -2, -hw), P(base, -2, hw)], fill=(150, 100, 40), width=3)
im.save(dst)
