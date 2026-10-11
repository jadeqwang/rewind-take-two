#!/usr/bin/env python3
"""Track Jade in a matte video: per frame, the largest blob's bottom-centre (feet) and height, in 1920x1080 design px.
    ~/Documents/moongazing/.venv/bin/python tools/v4B/gunfire/track.py media/shots/B_g1world/take_1_matte/matte.mp4 OUT.json
Smoothed (5-frame running median); used by render/timeline/_B_gunfire.js to place her card on the layout path."""
import json
import sys

import av
import numpy as np
from scipy import ndimage as ndi

src, out = sys.argv[1], sys.argv[2]
rows = []
with av.open(src) as c:
    for f in c.decode(video=0):
        a = f.to_ndarray(format="gray") > 128
        sx, sy = 1920 / a.shape[1], 1080 / a.shape[0]
        lab, n = ndi.label(a)
        if not n:
            rows.append(None)
            continue
        k = 1 + int(np.argmax(ndi.sum(a, lab, range(1, n + 1))))
        ys, xs = np.nonzero(lab == k)
        foot = ys >= ys.max() - max(3, (ys.max() - ys.min()) * 0.08)
        rows.append([float(xs.mean() * sx), float(ys.max() * sy), float((ys.max() - ys.min()) * sy), float(xs[foot].mean() * sx)])
arr = np.array([r if r else [np.nan] * 4 for r in rows])
sm = np.array([np.nanmedian(arr[max(0, i - 2):i + 3], axis=0) for i in range(len(arr))])
json.dump(dict(src=src, fps=24, cols=["cx", "bottom", "height", "foot_x"], rows=[[round(v, 1) for v in r] for r in sm]), open(out, "w"))
for i in range(0, len(sm), 6):
    print(i, round(i / 24, 2), sm[i].round(1))
