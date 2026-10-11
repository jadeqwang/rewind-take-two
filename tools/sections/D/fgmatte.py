#!/usr/bin/env python
"""Foreground-only matte for a locked-off take (rev 5b): the engrave matte sometimes holds static scenery (the white
trail strip on the slide book in slide_point). Pixels that match the take's own temporal median (the empty scene: the
girls keep moving, the scenery stays) are dropped; the rest is closed and hole-filled so a white jacket over a white
page survives, then intersected with the engrave matte.
    fgmatte.py STEM [--thresh=28] [--close=15] [--out=_fmatte] [--t0=0 --t1=99 (median window)] [--bg=CLEAN.jpg]
--bg: diff against a clean plate (e.g. the nano plate) instead of the median, for takes where the girls linger.
writes STEM<out>/%05d.png + matte.mp4 (same frame numbering and size as STEM_matte)."""
import glob
import os
import subprocess
import sys

import av
import cv2
import numpy as np

FF = os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg")
stem = sys.argv[1]
o = {x[2:].split("=")[0]: x.split("=", 1)[1] for x in sys.argv[2:] if x.startswith("--")}
th, cl = float(o.get("thresh", 28)), int(o.get("close", 15))
out = stem + o.get("out", "_fmatte")
os.makedirs(out, exist_ok=True)
ms = sorted(glob.glob(stem + "_matte/*.png"))
mh, mw = cv2.imread(ms[0], 0).shape
fr = []
with av.open(stem + "_engraved.mp4") as c:
    for f in c.decode(video=0):
        fr.append(cv2.resize(f.to_ndarray(format="bgr24"), (mw, mh), interpolation=cv2.INTER_AREA))
t0, t1 = round(float(o.get("t0", 0)) * 24), min(len(fr), round(float(o.get("t1", 99)) * 24) + 1)
bg = (cv2.resize(cv2.imread(o["bg"]), (mw, mh), interpolation=cv2.INTER_AREA) if "bg" in o
      else np.median(np.stack(fr[t0:t1]), axis=0)).astype(np.float32)
bgb = cv2.GaussianBlur(bg, (0, 0), 2)
cv2.imwrite(out + "/_median.jpg", bg.astype(np.uint8))
K = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * cl + 1, 2 * cl + 1))
for i, p in enumerate(ms):
    m = cv2.imread(p, 0)
    d = np.abs(cv2.GaussianBlur(fr[min(i, len(fr) - 1)].astype(np.float32), (0, 0), 2) - bgb).max(2)
    fg = (d > th).astype(np.uint8)
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, K)
    # fill holes (a white jacket panel over a white page): flood the background from the border
    ff = fg.copy(); h, w = ff.shape; mask = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(ff, mask, (0, 0), 2)
    fg = ((ff != 2) | (fg > 0)).astype(np.uint8)
    keep = (m >= 128) & (fg > 0)
    n, lab, st, _ = cv2.connectedComponentsWithStats(keep.astype(np.uint8))
    for k in range(1, n):
        if st[k, 4] < 400:
            keep[lab == k] = False
    cv2.imwrite(f"{out}/{i:05d}.png", np.where(keep, m, 0).astype(np.uint8))
subprocess.run([FF, "-y", "-loglevel", "error", "-framerate", "24", "-i", f"{out}/%05d.png", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-crf", "12", f"{out}/matte.mp4"], check=True)
print("wrote", out)
