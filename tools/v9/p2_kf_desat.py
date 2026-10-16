#!/usr/bin/env python3
"""v9 fix 1a: media/shots/P2/kf_v9c.jpg -> kf_v9d.png. The nano-banana edit painted the park beyond the passenger
windows in colour (green lawn, blue sky); the world must be black-and-white. Desaturate green/blue pixels everywhere
except two small boxes (her pale-blue chest dot and the pale-blue eraser). Pixel pass, no model.

    tools/engrave/.venv/bin/python tools/v9/p2_kf_desat.py
"""
import cv2
import numpy as np
from PIL import Image

ROOT = "/home/jade/Documents/rewind-take-two/"
im = np.asarray(Image.open(ROOT + "media/shots/P2/kf_v9c.jpg").convert("RGB"))
H, W = im.shape[:2]
s = W / 1366
h = cv2.cvtColor(im, cv2.COLOR_RGB2HSV_FULL)[..., 0].astype(np.float32) * 360 / 256
chroma = (im.max(2).astype(np.float32) - im.min(2)) / 255
sel = ((h > 65) & (h < 265) & (chroma > 0.04)).astype(np.uint8)
for x0, y0, x1, y1 in [(745, 445, 810, 510), (770, 60, 830, 110), (600, 60, 650, 115)]:   # dot, erasers (1366-wide px)
    sel[int(y0 * s):int(y1 * s), int(x0 * s):int(x1 * s)] = 0
g = 0.299 * im[..., 0] + 0.587 * im[..., 1] + 0.114 * im[..., 2]
m = cv2.GaussianBlur(sel.astype(np.float32), (0, 0), 1.5)[..., None]
out = im * (1 - m) + np.repeat(g[..., None], 3, 2) * m
Image.fromarray(out.clip(0, 255).astype(np.uint8)).save(ROOT + "media/shots/P2/kf_v9d.png")
