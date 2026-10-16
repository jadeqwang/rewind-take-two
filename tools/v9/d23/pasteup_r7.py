#!/usr/bin/env python3
"""Round 7: a rough paste-up of plate_r4_e2.png with the steering wheel and her hands moved LOWER (scaled 0.9 about the
wheel centre and dropped 150 px), so the rim's top sits below the window sill and the window's front lower corner, where
the TL's door mirror really is, is clear. The gap left above it is painted chroma green (window) or grey (the dash and
A-pillar foot behind, for the model to repair). nano-banana-pro (gen.py r7_c/r7_d) redraws it clean; make_plate_r7.py
then keeps e2's own pixels everywhere outside the changed area (her face stays pixel-identical, so round 6's blink and
lip-press variants still register). Run with tools/engrave/.venv/bin/python."""
import cv2, numpy as np
D = 'media/shots/D23'
e2 = cv2.imread(f'{D}/plate_r4_e2.png')
X0, Y0, X1, Y1 = 1560, 640, 1990, 1300           # the wheel + hands block (plate px)
CX, CY, K, DY = 1790, 960, 0.90, 150
M = np.float32([[K, 0, CX - K * CX], [0, K, CY - K * CY + DY]])
blk = np.zeros_like(e2); blk[Y0:Y1, X0:X1] = e2[Y0:Y1, X0:X1]
m = np.zeros(e2.shape[:2], np.uint8); m[Y0:Y1, X0:X1] = 255
blk = cv2.warpAffine(blk, M, (e2.shape[1], e2.shape[0]), flags=cv2.INTER_CUBIC)
mw = cv2.warpAffine(m, M, (e2.shape[1], e2.shape[0]), flags=cv2.INTER_NEAREST)
out = e2.copy()
# vacated area: green above the sill (x < 1850, y < 828), grey hole elsewhere (dash / pillar foot behind the old rim)
vac = (m > 0) & (mw == 0)
yy, xx = np.mgrid[0:e2.shape[0], 0:e2.shape[1]]
out[vac & (xx < 1850) & (yy < 828)] = (0, 255, 0)
out[vac & ~((xx < 1850) & (yy < 828))] = (128, 128, 128)
out[mw > 0] = blk[mw > 0]
cv2.imwrite(f'{D}/pasteup_r7.png', out)
print('wrote', f'{D}/pasteup_r7.png')
