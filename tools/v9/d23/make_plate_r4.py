#!/usr/bin/env python3
"""Round 4: the whole near interior + Jade as one plate (plate_r4_e2.png, nano-banana edit of plate_r4_a), the side
window and windshield left flat chroma green by the model. Writes, 2x upscaled (Real-ESRGAN animevideov3, tiles):
  OUT_rgba.png   : RGB + alpha (alpha = not green, soft edge, green spill removed)  -> the scene's card
  OUT_jade.png   : Jade-only matte (BiRefNet matte from engrave_still --matte-out, x not-green, + saturated colour near
                   her: the eraser tips)                                            -> the engrave pass's matte
Run with tools/engrave/.venv/bin/python:  make_plate_r4.py PLATE BIREFNET_MATTE OUT_PREFIX"""
import sys
import cv2, numpy as np
sys.path.insert(0, 'tools/engrave')
from upscale import Upscaler
plate, matte, out = sys.argv[1:4]
rgb = cv2.cvtColor(cv2.imread(plate), cv2.COLOR_BGR2RGB)
H, W = rgb.shape[:2]
f = rgb.astype(np.float32)
mx = np.maximum(f[..., 0], f[..., 2])
green = np.clip((f[..., 1] - mx - 40) / 70, 0, 1)                 # 1 = chroma green
alpha = 1 - green
alpha = cv2.GaussianBlur(cv2.erode(alpha, np.ones((3, 3), np.uint8)), (3, 3), 0.8)
# despill: wherever there is any green cast, clamp g to max(r, b)
spill = f[..., 1] > mx + 8
f[..., 1] = np.where(spill, np.minimum(f[..., 1], mx + 8), f[..., 1])
rgb2 = np.clip(f, 0, 255).astype(np.uint8)
# Jade matte
jm = cv2.imread(matte, cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255
hsv = cv2.cvtColor(rgb2, cv2.COLOR_RGB2HSV).astype(np.float32)
sat = (hsv[..., 1] / 255) * (hsv[..., 2] / 255)
near = cv2.dilate((jm > 0.5).astype(np.uint8), np.ones((61, 61), np.uint8)) > 0
jm = np.maximum(jm, ((sat > 0.22) & near).astype(np.float32))
jm = jm * (1 - green)
# upscale 2x in tiles
S, T, O = 2, 512, 32
up = Upscaler('animevideov3', 0, 0)
big = np.zeros((H * S, W * S, 3), np.uint8)
for y0 in range(0, H, T):
    for x0 in range(0, W, T):
        xa, ya, xb, yb = max(0, x0 - O), max(0, y0 - O), min(W, x0 + T + O), min(H, y0 + T + O)
        up.ow, up.oh = (xb - xa) * S, (yb - ya) * S
        tile = up(np.ascontiguousarray(rgb2[ya:yb, xa:xb]))
        cy0, cx0 = (y0 - ya) * S, (x0 - xa) * S
        ch, cw = (min(H, y0 + T) - y0) * S, (min(W, x0 + T) - x0) * S
        big[y0 * S:y0 * S + ch, x0 * S:x0 * S + cw] = tile[cy0:cy0 + ch, cx0:cx0 + cw]
A = cv2.resize(alpha, (W * S, H * S), interpolation=cv2.INTER_CUBIC)
J = cv2.resize(jm, (W * S, H * S), interpolation=cv2.INTER_CUBIC)
cv2.imwrite(out + '_rgba.png', cv2.cvtColor(np.dstack([big, (np.clip(A, 0, 1) * 255).astype(np.uint8)]), cv2.COLOR_RGBA2BGRA))
cv2.imwrite(out + '_jade.png', (np.clip(J, 0, 1) * 255).astype(np.uint8))
print('wrote', out + '_rgba.png', out + '_jade.png', big.shape)
