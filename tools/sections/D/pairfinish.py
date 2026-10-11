#!/usr/bin/env python
"""Finish a splitpair.py split (rev 5b): the engrave blots are notches and holes in the live girl's matte, and the clean
cover laid under her would show through them as white patches. The live matte is closed (radius --close) and
hole-filled, never taking a ghost pixel; the ghost keeps every pixel splitpair gave her (a dropped ghost pixel would
show her real colours), hole-filled.
    pairfinish.py STEM [--close=14] [--t0=0.8] [--t1=4.5]"""
import glob
import os
import subprocess
import sys

import cv2
import numpy as np

FF = os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg")
stem = sys.argv[1]
o = {x[2:].split("=")[0]: x.split("=", 1)[1] for x in sys.argv[2:] if x.startswith("--")}
ell = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
E = sorted(glob.glob(stem + "_matte/*.png")); GA = sorted(glob.glob(stem + "_ghost/*.png")); LB = sorted(glob.glob(stem + "_live/*.png"))
n = len(E); h, w = cv2.imread(E[0], 0).shape
i0, i1 = round(float(o.get("t0", 0.8)) * 24), min(n - 1, round(float(o.get("t1", 4.5)) * 24))


def fill(m):
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, ell(4))
    ff = m.copy(); mk = np.zeros((h + 2, w + 2), np.uint8); cv2.floodFill(ff, mk, (0, 0), 2)
    return (ff != 2) | (m > 0)


cr = int(o.get("close", 14))
out = {"_ghost": {}, "_live": {}}
for i in range(i0, i1 + 1):
    g = fill(cv2.imread(GA[i], 0) >= 128)
    l = cv2.imread(LB[i], 0) >= 100
    l = cv2.morphologyEx(l.astype(np.uint8), cv2.MORPH_CLOSE, ell(cr)) > 0
    out["_ghost"][i], out["_live"][i] = g, fill(l) & ~g
for d, S in out.items():
    for f in glob.glob(stem + d + "/*.png"):
        os.remove(f)
    for i in range(n):
        cv2.imwrite(f"{stem}{d}/{i:05d}.png", (S.get(i, np.zeros((h, w), bool)) * 255).astype(np.uint8))
    subprocess.run([FF, "-y", "-loglevel", "error", "-framerate", "24", "-i", f"{stem}{d}/%05d.png", "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-crf", "12", f"{stem}{d}/matte.mp4"], check=True)
print("wrote", stem + "_ghost", stem + "_live")
