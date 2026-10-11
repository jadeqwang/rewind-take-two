#!/usr/bin/env python3
"""Track agent C's pistol in the G2 take (media/shots/B_g2clean/take_1_engraved.mp4): per frame the muzzle (design px)
and the barrel direction (unit vector, rear of slide -> muzzle), from the dark blob of the pistol next to his hand.
    ~/Documents/moongazing/.venv/bin/python tools/v4B/gunfire/gun_track.py [--sheet]
Writes media/shots/B_g2clean/take_1_gun.json; --sheet also writes take_1_gun_check.jpg (crops with the line drawn)."""
import json
import sys

import av
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

ROOT = "/home/jade/Documents/rewind-take-two"
SRC = f"{ROOT}/media/shots/B_g2clean/take_1_engraved.mp4"
WIN = (780, 520, 1000, 700)                 # x0, y0, x1, y1 design px: hand + pistol only
AX = np.array([0.636, 0.772])                # rough barrel direction (from the 1.0 s frame)
rows, crops = [], []
with av.open(SRC) as c:
    for i, f in enumerate(c.decode(video=0)):
        im = f.to_ndarray(format="rgb24")
        g = im[WIN[1]:WIN[3], WIN[0]:WIN[2]].mean(axis=2)
        dark = ndi.binary_opening(g < 80, structure=np.ones((7, 7)))   # the pistol is solid; lawn strokes are thin
        lab, n = ndi.label(dark)
        best = None
        for k in range(1, n + 1):
            ys, xs = np.nonzero(lab == k)
            if not 250 <= len(xs) <= 6000:
                continue
            P = np.stack([xs, ys], 1).astype(float)
            ext = (P @ AX).max()
            w, h = np.ptp(xs) + 1, np.ptp(ys) + 1
            if w > 160 or h > 160:                       # the sleeve or the lawn, not the pistol
                continue
            score = ext
            if best is None or score > best[0]:
                best = (score, P)
        if best is None:
            rows.append(None)
            continue
        P = best[1]
        m = P.mean(0)
        u, s, vt = np.linalg.svd(P - m, full_matrices=False)
        d = vt[0] if vt[0] @ AX > 0 else -vt[0]
        tip = P[np.argmax((P - m) @ d)]
        mz = [float(tip[0] + WIN[0]), float(tip[1] + WIN[1])]
        rows.append([round(mz[0], 1), round(mz[1], 1), round(float(d[0]), 4), round(float(d[1]), 4)])
        if "--sheet" in sys.argv and i % 8 == 0:
            cr = Image.fromarray(im).crop((700, 500, 1150, 800))
            dd = ImageDraw.Draw(cr)
            a = (mz[0] - 700, mz[1] - 500)
            dd.line([a, (a[0] + d[0] * 400, a[1] + d[1] * 400)], fill=(255, 0, 0), width=2)
            dd.text((6, 6), f"{i / 24:.2f}", fill=(255, 0, 0))
            crops.append(cr)
json.dump(dict(src=SRC, fps=24, cols=["muzzle_x", "muzzle_y", "dir_x", "dir_y"], rows=rows),
          open(f"{ROOT}/media/shots/B_g2clean/take_1_gun.json", "w"))
for i in range(0, len(rows), 4):
    print(i, round(i / 24, 2), rows[i])
if crops:
    S = Image.new("RGB", (450 * 4, 300 * ((len(crops) + 3) // 4)))
    for k, cr in enumerate(crops):
        S.paste(cr, ((k % 4) * 450, (k // 4) * 300))
    S.save(f"{ROOT}/media/shots/B_g2clean/take_1_gun_check.jpg", quality=88)
