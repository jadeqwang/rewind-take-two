#!/usr/bin/env python3
"""Watercolor singing Jade (v3), step 1: her watercolor portrait, whole, on a 16:9 sheet of its own paper, in the
geometry of the v2 first frames (after moongazing-public-version work/singer5/base.py). Nothing of her is redrawn,
turned, recoloured or scaled out of proportion.

    MPY tools/sing/wc_base.py      -> media/sing/first/v3_base16.jpg (2752x1536) + v3_base.json

Framing: portrait rows ROW0..ROW1 fill the height of the v2 crop box (media/sing/first/crop.json, 2576x1449 inside the
2752x1536 sheet), so after the same crop the frame shows a little headroom above her hair and the whole round
"1420 MHz" sleeve patch at the bottom; her face (landmark box) is centred at x = 0.5.
"""
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mouth as MT  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VER = os.environ.get("WC_VER", "v3")      # v4: WC_VER=v4 (new portrait: glossier hair, less smile); see docs/revisions/v4/A.md
SRC = os.path.join(ROOT, os.environ.get("WC_SRC", "inputs/jade_watercolor_jacket_v6.png"))
SRC_K = float(os.environ.get("WC_SRC_SCALE", 1))   # the source is the portrait at SRC_K x its size (v4_pick.py writes 2 x)
OUT = os.path.join(ROOT, f"media/sing/first/{VER}_base16.jpg")
META = os.path.join(ROOT, f"media/sing/first/{VER}_base.json")
CROP = json.load(open(os.path.join(ROOT, "media/sing/first/crop.json")))["box"]
W, H = 2752, 1536
ROW0, ROW1 = -30, 1030


def main():
    a = np.asarray(Image.open(SRC).convert("RGB"))
    L = MT.detect(a, (0, 0, a.shape[1], a.shape[0]))[0]
    fx = (L[:, 0].min() + L[:, 0].max()) / 2
    x0c, y0c, x1c, y1c = CROP
    s = (y1c - y0c) / ((ROW1 - ROW0) * SRC_K)
    a = a.astype(np.float32)
    lum = a.mean(2)
    paper = np.median(a[lum > np.percentile(lum, 70)], axis=0)
    w, h = round(a.shape[1] * s), round(a.shape[0] * s)
    t = np.asarray(Image.fromarray(a.astype(np.uint8)).resize((w, h), Image.LANCZOS), np.float32)
    sheet = np.ones((H, W, 3), np.float32) * paper
    sheet += np.random.default_rng(7).normal(0, 1.2, (H, W, 1))
    x0 = round((x0c + x1c) / 2 - fx * s)
    if os.environ.get("WC_X0"):                     # v4: pin her to the v3 column (v3_base.json x0), whatever the new face measures
        x0 = int(os.environ["WC_X0"])
    y0 = round(y0c - ROW0 * SRC_K * s)                      # sheet y of portrait row 0
    ramp = np.clip(np.arange(w) / 70, 0, 1)
    ramp = np.minimum(ramp, ramp[::-1]) ** 1.5
    top = np.clip(np.arange(h) / 40, 0, 1) ** 1.5   # the portrait's top edge fades into the paper too
    m = ramp[None] * top[:, None]
    ys = slice(y0, min(H, y0 + h))
    n = ys.stop - ys.start
    sheet[ys, x0:x0 + w] = t[:n] * m[:n, :, None] + sheet[ys, x0:x0 + w] * (1 - m[:n, :, None])
    Image.fromarray(np.clip(sheet, 0, 255).astype(np.uint8)).save(OUT, quality=96)
    json.dump({"src": os.path.relpath(SRC, ROOT), "rows": [ROW0, ROW1], "src_scale": SRC_K, "scale": s, "x0": x0, "y0": y0, "w": w,
               "paper": [float(v) for v in paper], "face_cx_src": float(fx), "crop_box": CROP}, open(META, "w"), indent=1)
    print(os.path.relpath(OUT, ROOT), (W, H), "portrait at x", x0, "y", y0, "scale", round(s, 4))


if __name__ == "__main__":
    main()
