#!/usr/bin/env python
"""Matte track: per-frame centroid + bbox (normalised 0..1) of the white region of a matte PNG sequence.

    mtrack.py MATTE_DIR [--at=1.2,2.5] [--thr=128] [--json OUT]
--at prints only those source times (s, 24 fps). Without --at it prints every 6th frame.
Area is the matte fraction of the frame. Also reports secondary blobs (leaked agents etc.) as 'blobs'.
"""
import glob
import json
import os
import sys

import cv2
import numpy as np

FPS = 24


def stats(path, thr=128):
    m = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    h, w = m.shape
    b = (m >= thr).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(b, 8)
    blobs = sorted([(int(st[i, 4]), i) for i in range(1, n)], reverse=True)
    if not blobs:
        return None
    ys, xs = np.nonzero(b)
    big = [i for a, i in blobs if a > 0.002 * w * h]
    return dict(cx=round(float(xs.mean()) / w, 4), cy=round(float(ys.mean()) / h, 4),
                x0=round(xs.min() / w, 4), y0=round(ys.min() / h, 4), x1=round(xs.max() / w, 4), y1=round(ys.max() / h, 4),
                area=round(float(b.mean()), 4),
                blobs=[dict(area=round(st[i, 4] / (w * h), 4), x0=round(st[i, 0] / w, 3), y0=round(st[i, 1] / h, 3),
                            x1=round((st[i, 0] + st[i, 2]) / w, 3), y1=round((st[i, 1] + st[i, 3]) / h, 3)) for i in big])


def track(d, thr=128):
    fs = sorted(glob.glob(os.path.join(d, "*.png")))
    return [stats(f, thr) for f in fs]


if __name__ == "__main__":
    d = sys.argv[1]
    o = {a[2:].split("=")[0]: a.split("=", 1)[1] if "=" in a else True for a in sys.argv[2:] if a.startswith("--")}
    fs = sorted(glob.glob(os.path.join(d, "*.png")))
    idx = [round(float(t) * FPS) for t in o["at"].split(",")] if "at" in o else list(range(0, len(fs), 6))
    out = {}
    for i in idx:
        i = min(i, len(fs) - 1)
        s = stats(fs[i], int(o.get("thr", 128)))
        out[f"{i / FPS:.3f}"] = s
        print(f"t={i / FPS:.3f} f{i}: {json.dumps(s)}")
    if "json" in o:
        json.dump(out, open(o["json"], "w"), indent=1)
