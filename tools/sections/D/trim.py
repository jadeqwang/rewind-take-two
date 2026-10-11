#!/usr/bin/env python
"""Trim paper margins / printed frame lines that image models add, then crop back to 16:9.

    trim.py IMG [IMG ...] [--pad=6] [--dry]
The original is kept as <name>_pretrim.<ext>. Prints the crop box per image.
"""
import os
import sys

import numpy as np
from PIL import Image


def edge_cut(dens, maxfrac=0.12):
    """dens: ink density per row/col from the edge inward. Returns how many lines to cut from this edge."""
    n = len(dens)
    lim = int(n * maxfrac)
    if dens[:6].mean() > 0.10:          # content (not paper) right at the edge: nothing to trim
        return 0
    # walk in over blank paper, then over a printed frame line if one follows
    i = 0
    while i < lim and dens[i] < 0.10:
        i += 1
    if i >= lim:
        return 0
    j = i
    while j < lim and dens[j] > 0.55:   # solid rule
        j += 1
    if j > i and j - i < 40:            # it was a rule: skip it plus a gap
        return j
    return i


def trim(path, pad=6, dry=False):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im.convert("L")).astype(np.float32)
    ink = (a < 140).astype(np.float32)
    rows, cols = ink.mean(1), ink.mean(0)
    t = edge_cut(rows)
    b = edge_cut(rows[::-1])
    l = edge_cut(cols)
    r = edge_cut(cols[::-1])
    if sum(1 for v in (t, b, l, r) if v) < 3:   # one blank edge is usually sky, not a margin
        print(f"{os.path.basename(path)}: clean")
        return path
    h, w = a.shape
    box = [l + pad if l else 0, t + pad if t else 0, w - (r + pad if r else 0), h - (b + pad if b else 0)]
    bw, bh = box[2] - box[0], box[3] - box[1]
    if bw / bh > 16 / 9:
        nw = round(bh * 16 / 9)
        box[0] += (bw - nw) // 2
        box[2] = box[0] + nw
    else:
        nh = round(bw * 9 / 16)
        box[1] += (bh - nh) // 2
        box[3] = box[1] + nh
    print(f"{os.path.basename(path)}: cut t{t} b{b} l{l} r{r} -> box {box} ({box[2]-box[0]}x{box[3]-box[1]})")
    if dry:
        return path
    base, ext = os.path.splitext(path)
    keep = base + "_pretrim" + ext
    if not os.path.exists(keep):
        im.save(keep, quality=95)
    im.crop(tuple(box)).resize((w, h), Image.LANCZOS).save(path, quality=95)
    return path


if __name__ == "__main__":
    pad = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--pad=")), 6))
    for p in [a for a in sys.argv[1:] if not a.startswith("--")]:
        trim(p, pad, "--dry" in sys.argv)
