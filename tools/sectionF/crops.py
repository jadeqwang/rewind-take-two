"""Detect paper margins (nano-banana sometimes draws a page border) in each chosen plate and write 16:9 crops to
tools/sectionF/crops.json (normalised [x0, y0, x1, y1]). Run with tools/engrave/.venv/bin/python."""
import json
import os
import sys

import av

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edl import CHOSEN, plate, ROOT  # noqa: E402

res = {}
for shot in CHOSEN:
    f = os.path.join(ROOT, plate(shot)["file"])
    c = av.open(f)
    frames = []
    for i, fr in enumerate(c.decode(video=0)):
        if i in (12, 60):
            frames.append(fr.to_ndarray(format="rgb24").astype(float).mean(2))
        if i > 60:
            break
    H, W = frames[0].shape

    def border(get, n):
        k = 0
        while k < n // 4 and max(get(a, k).std() for a in frames) <= 6:
            k += 1
        return k
    t = border(lambda a, k: a[k, :], H); b = border(lambda a, k: a[H - 1 - k, :], H)
    l = border(lambda a, k: a[:, k], W); r = border(lambda a, k: a[:, W - 1 - k], W)
    if not (t or b or l or r):
        res[shot] = None
        continue
    pad = 6
    x0, y0, x1, y1 = (l + pad if l else 0), (t + pad if t else 0), W - (r + pad if r else 0), H - (b + pad if b else 0)
    w, h = x1 - x0, y1 - y0
    if w / h > 16 / 9:
        nw = h * 16 / 9; x0 += (w - nw) / 2; x1 = x0 + nw
    else:
        nh = w * 9 / 16; y0 += (h - nh) / 2; y1 = y0 + nh
    res[shot] = [round(x0 / W, 4), round(y0 / H, 4), round(x1 / W, 4), round(y1 / H, 4)]
    print(shot, (t, b, l, r), res[shot])
json.dump(res, open(os.path.join(ROOT, "tools/sectionF/crops.json"), "w"), indent=0)
