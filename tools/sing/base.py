#!/usr/bin/env python3
"""Singing Jade, step 1 (the Orbital Sunrise method): her approved pencil trace, whole, centred on a 16:9 sheet of its
own paper. Nothing of her is redrawn, rescaled out of proportion, turned or recoloured: frame height = trace height.
Same as moongazing-public-version work/singer4/base.py, so the face geometry matches the frames deshadow.py was drawn on.

    PY tools/sing/base.py        -> media/sing/first/base16.jpg (2752x1536)

The trace is read from orbital-sunrise-video (read-only); set JADE_TRACE to use another copy.
"""
import os

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TRACE = os.environ.get("JADE_TRACE", os.path.expanduser(
    "~/Documents/orbital-sunrise-video/media/chars/jade_src/jade_trace_jacket_hp_2.jpg"))
OUT = os.path.join(ROOT, "media/sing/first/base16.jpg")
W, H = 2752, 1536


def main():
    a = np.asarray(Image.open(TRACE).convert("RGB"), np.float32)
    paper = np.median(a[:200].reshape(-1, 3), axis=0)
    s = H / a.shape[0]
    w = round(a.shape[1] * s)
    t = np.asarray(Image.fromarray(a.astype(np.uint8)).resize((w, H), Image.LANCZOS), np.float32)
    sheet = np.ones((H, W, 3), np.float32) * paper
    sheet += np.random.default_rng(7).normal(0, 1.2, (H, W, 1))
    x0 = (W - w) // 2
    ramp = np.clip(np.arange(w) / 70, 0, 1)
    ramp = np.minimum(ramp, ramp[::-1]) ** 1.5
    m = np.ones((H, w), np.float32) * ramp[None]
    sheet[:, x0:x0 + w] = t * m[..., None] + sheet[:, x0:x0 + w] * (1 - m[..., None])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    Image.fromarray(np.clip(sheet, 0, 255).astype(np.uint8)).save(OUT, quality=96)
    print(os.path.relpath(OUT, ROOT), (W, H), "trace at x", x0, "scale", round(s, 4))


if __name__ == "__main__":
    main()
