#!/usr/bin/env python3
"""Round 7: the DRAWN door-mirror housing -> a card registered to the shot (scene_r7.js buildHousingCard).
  in : media/shots/D23/housing_r7_c.png (nano-banana-pro, gen.py r7_house_c), drawn over housing_guide_r7b.png (the CG
       cap from rig_r7.housingCam(), 1920x1080 design px)
  1. register the drawing onto the guide: ECC (affine) on the two silhouettes (not-green), so the drawn cap sits exactly
     where the rig's glass is
  2. key: alpha = not green (soft), green spill clamped; the glass hole is transparent (the live reflection shows there)
  3. the drawn glass hole, back-projected onto the glass plane -> glass-local (a, b) outline -> tools/v9/d23/tl_outline_r7.js
     (rig_r7's TL_OUTLINE: the reflection's glass mesh and the in-glass checks follow the drawing)
Writes media/shots/D23/r7_housing_rgba.png (2752 x 1536). Run with tools/engrave/.venv/bin/python from the repo root."""
import json, subprocess, sys
import cv2, numpy as np
D = 'media/shots/D23'
SRC = sys.argv[1] if len(sys.argv) > 1 else f'{D}/housing_r7_c.png'
guide = cv2.imread(f'{D}/housing_guide_r7b.png')
draw = cv2.imread(SRC)
GW, GH = guide.shape[1], guide.shape[0]
FW, FH = draw.shape[1], draw.shape[0]
def notgreen(im):
    f = im.astype(np.float32); return np.clip(((f[..., 1] - np.maximum(f[..., 0], f[..., 2])) - 40) / 70, 0, 1) < 0.5
mg = notgreen(guide).astype(np.float32)
md = notgreen(cv2.resize(draw, (GW, GH), interpolation=cv2.INTER_AREA)).astype(np.float32)
bl = lambda m: cv2.GaussianBlur(m, (0, 0), 4)
warp = np.eye(2, 3, dtype=np.float32)
cc, warp = cv2.findTransformECC(bl(mg), bl(md), warp, cv2.MOTION_AFFINE, (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 300, 1e-6), None, 5)
print('ECC', round(cc, 4), 'warp (guide px):', np.round(warp, 4).tolist())
# warp maps guide coords -> drawing coords (inverse map); at full res: scale by FW/GW
s = FW / GW
Wf = warp.copy(); Wf[:, 2] *= s
full = cv2.warpAffine(draw, Wf, (FW, FH), flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 255, 0))
f = full.astype(np.float32)
mx = np.maximum(f[..., 0], f[..., 2])
green = np.clip((f[..., 1] - mx - 40) / 70, 0, 1)
alpha = cv2.GaussianBlur(cv2.erode(1 - green, np.ones((3, 3), np.uint8)), (3, 3), 0.8)
spill = f[..., 1] > mx + 6
f[..., 1] = np.where(spill, np.minimum(f[..., 1], mx + 6), f[..., 1])
cv2.imwrite(f'{D}/r7_housing_rgba.png', np.dstack([np.clip(f, 0, 255).astype(np.uint8), (np.clip(alpha, 0, 1) * 255).astype(np.uint8)]))
# the glass hole: green regions not touching the border; the biggest
g8 = (green > 0.5).astype(np.uint8)
n, lab, st, _ = cv2.connectedComponentsWithStats(g8, 8)
best = max((i for i in range(1, n) if st[i, 0] > 0 and st[i, 1] > 0 and st[i, 0] + st[i, 2] < FW and st[i, 1] + st[i, 3] < FH), key=lambda i: st[i, 4])
hole = (lab == best).astype(np.uint8)
cnts, _ = cv2.findContours(hole, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
c = max(cnts, key=cv2.contourArea)[:, 0, :].astype(np.float64)
# back-project (full-res px -> design px -> ray from the housing camera -> glass plane -> (a, b))
R = json.loads(subprocess.run(['node', '-e', "import('./tools/v9/d23/rig_r7.js').then(R=>{const c=R.housingCam(); console.log(JSON.stringify({c, M: R.MIRROR}))})"], capture_output=True, text=True).stdout)
cam, M = R['c'], R['M']
pos, fwd, right, up = (np.array(cam[k]) for k in ('pos', 'fwd', 'right', 'up'))
fpx = (GH / 2) / np.tan(np.radians(cam['fov']) / 2)
P = []
for x, y in c[::4] / s:
    d = fwd + right * (x - GW / 2) / fpx - up * (y - GH / 2) / fpx
    t = np.dot(np.array(M['c']) - pos, M['n']) / np.dot(d, M['n'])
    q = pos + d * t - np.array(M['c'])
    P.append((round(float(np.dot(q, M['u']) / (M['w'] / 2)), 4), round(float(np.dot(q, M['v']) / (M['h'] / 2)), 4)))
P.append(P[0])
a = np.array(P); print('drawn glass hole (a, b) range', a[:, 0].min(), a[:, 0].max(), a[:, 1].min(), a[:, 1].max(), len(P), 'pts')
open('tools/v9/d23/tl_outline_r7.js', 'w').write(
    '// round 7: the glass outline of the DRAWN housing (tools/v9/d23/housing_r7.py, from media/shots/D23/housing_r7_c.png),\n'
    '// back-projected onto the glass plane: glass-local (a, b), a = +1 inboard, b = +1 up. Generated; do not edit by hand.\n'
    f'export const TL_OUTLINE_R7 = {json.dumps(P)};\n')
print('wrote', f'{D}/r7_housing_rgba.png', 'tools/v9/d23/tl_outline_r7.js')
