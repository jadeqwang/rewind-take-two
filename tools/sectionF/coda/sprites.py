"""v5-coda: cut the six figures of the committee line-up sheet (nano-banana-pro, white background) into RGBA sprites
for tools/sectionF/coda/hilbert_lobby.js. Background = near-white pixels connected to the image border (the drawn
baseline under their feet is removed first), so white jackets and sneakers inside the outlines stay opaque.

    $PY tools/sectionF/coda/sprites.py [sheet.png] [out_dir]
Writes <out_dir>/<name>.png (cropped to the figure, feet on the bottom edge) and info.json {name: [w, h]}.
"""
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = "/home/jade/Documents/rewind-take-two"
NAMES = ["jade", "watercolor", "engraved", "graphite", "ghost_orange", "ghost_blue"]   # left to right on the sheet


def main(sheet=os.path.join(ROOT, "media/reviews/v5/plans/coda/committee_sheet.png"),
         out=os.path.join(ROOT, "media/reviews/v5/plans/coda/sprites")):
    os.makedirs(out, exist_ok=True)
    im = np.asarray(Image.open(sheet).convert("RGB")).astype(np.float32)
    H, W, _ = im.shape
    lum = im.mean(2)
    dark = lum < 128
    # the baseline: a long thin dark horizontal line under the feet -> paint it white
    rows = np.where(dark.mean(1) > 0.6)[0]
    work = im.copy()
    for r in rows:
        work[max(0, r - 2):r + 3] = 255
    white = (work.min(2) > 232)
    lab, _ = ndimage.label(white)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(border))
    fg = ~bg
    fg = ndimage.binary_opening(fg, iterations=1)
    lab2, n = ndimage.label(fg)
    sizes = ndimage.sum(fg, lab2, range(1, n + 1))
    keep = np.isin(lab2, 1 + np.where(sizes > 0.002 * H * W)[0])           # drop specks
    cols = keep.any(0)
    runs, x = [], 0
    while x < W:                                                             # column runs separated by white gaps
        if cols[x]:
            x0 = x
            while x < W and cols[x]:
                x += 1
            runs.append((x0, x))
        x += 1
    runs = [r for r in runs if r[1] - r[0] > W * 0.03]
    assert len(runs) == len(NAMES), f"found {len(runs)} figures: {runs}"
    alpha = ndimage.gaussian_filter(keep.astype(np.float32), 0.8)
    info = {}
    for name, (x0, x1) in zip(NAMES, runs):
        m = keep[:, x0:x1]
        ys = np.where(m.any(1))[0]
        y0, y1 = ys[0], ys[-1] + 1
        rgba = np.dstack([im[y0:y1, x0:x1], 255 * alpha[y0:y1, x0:x1]]).clip(0, 255).astype(np.uint8)
        Image.fromarray(rgba, "RGBA").save(os.path.join(out, name + ".png"))
        info[name] = [int(x1 - x0), int(y1 - y0)]
        print(name, x0, x1, y0, y1)
    json.dump(info, open(os.path.join(out, "info.json"), "w"), indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:])
