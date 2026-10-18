#!/usr/bin/env python3
"""Singing Jade (v5), S1: put the two pencils back into the per-frame matte. BiRefNet keeps her bun but drops the two
pencils through it (thin, against the sky hatching), so in the wide Bean opening, where only her matted layer shows
her (render/timeline/A.js S1_her, 12.60-13.92), the pencils would vanish. The plate behind her head is pure black and
white engraving, so the pencils are the only saturated colour above her hairline: the pale-blue and pink erasers seed
the key, the yellow pencil body next to them joins it, and a stroke as wide as the eraser from each eraser to its pencil body
covers the silver ferrule between them.

    EPY=tools/engrave/.venv/bin/python      (needs OpenCV + PyAV)
    $EPY tools/sing/v5_pencils.py media/sing/S1/v5_sync_1080_open.mp4 media/sing/S1/v5_sync_1080_matte [--ferrule]
        -> the matte PNGs updated in place (max with the pencil key); the BiRefNet originals are kept once in
           <matte>_birefnet/; <matte>_pencils_check.jpg (frame crops: picture / old matte / new matte)
"""
import os
import shutil
import sys

import cv2
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


FERRULE = False      # v7 (--ferrule): an eraser with no pencil body beside it (the body hidden in her hair as she tilts)
#                      is joined to the nearest hair in the matte instead, so its silver ferrule is not dropped and the
#                      eraser does not float free of her head (S1 v7_sync_1080_open file frame 30)


def key(rgb, matte):
    """Pencil mask (float 0..1) for one frame."""
    ys, xs = np.nonzero(matte > 128)
    top = ys.min()
    h0, h1 = max(0, top - 80), top + 150                         # the bun's top: pencils stick out of it
    x0, x1 = max(0, xs[ys < top + 150].min() - 120), min(rgb.shape[1], xs[ys < top + 150].max() + 120)
    hsv = cv2.cvtColor(rgb[h0:h1, x0:x1], cv2.COLOR_RGB2HSV).astype(np.int32)
    H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    blue = (H >= 92) & (H <= 122) & (S > 60) & (V > 110)
    pink = ((H >= 150) | (H <= 6)) & (S > 60) & (V > 130)
    yellow = (H >= 11) & (H <= 24) & (S > 125) & (V > 105)          # measured on the take: H 12-17, S 140-210, V 110-230 (hair: V < 100)
    seeds = (blue | pink).astype(np.uint8)
    seeds = cv2.morphologyEx(seeds, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    near = cv2.dilate(seeds, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (71, 71))) > 0
    yel = yellow & near
    m = ((seeds > 0) | yel).astype(np.uint8)
    # each eraser joined to the pencil body next to it by a stroke as wide as the eraser: covers the silver ferrule
    # between them without taking in the sky hatching beside it
    n, lab, st, cen = cv2.connectedComponentsWithStats(seeds)
    for k in range(1, n):
        if st[k, cv2.CC_STAT_AREA] < 12:
            continue
        d = cv2.distanceTransform((lab != k).astype(np.uint8), cv2.DIST_L2, 3)
        body = yel & (d < 45)
        if body.sum() < 6:
            if FERRULE:
                hy, hx = np.nonzero(matte[h0:h1, x0:x1] > 128)
                if len(hy):
                    dd = np.hypot(hx - cen[k][0], hy - cen[k][1])
                    j = int(np.argmin(dd))
                    if dd[j] < 70:
                        w = max(3, int(round(0.8 * 2 * np.sqrt(st[k, cv2.CC_STAT_AREA] / np.pi))))
                        cv2.line(m, tuple(int(v) for v in cen[k]), (int(hx[j]), int(hy[j])), 1, w)
            continue
        by, bx = np.nonzero(body)
        w = max(3, int(round(0.8 * 2 * np.sqrt(st[k, cv2.CC_STAT_AREA] / np.pi))))
        cv2.line(m, tuple(int(v) for v in cen[k]), (int(bx.mean()), int(by.mean())), 1, w)
    m = m.astype(np.float32)
    m = cv2.GaussianBlur(m, (0, 0), 0.8)
    out = np.zeros(matte.shape, np.float32)
    out[h0:h1, x0:x1] = m
    return out


def main(src, mdir):
    import av
    bak = mdir.rstrip("/") + "_birefnet"
    if not os.path.exists(bak):
        shutil.copytree(mdir, bak)
    crops = []
    with av.open(src) as c:
        for i, f in enumerate(c.decode(c.streams.video[0])):
            p = os.path.join(bak, f"{i:05d}.png")
            if not os.path.exists(p):
                break
            old = np.asarray(Image.open(p), np.float32)
            rgb = f.to_ndarray(format="rgb24")
            if rgb.shape[:2] != old.shape:                   # v9w: 720p takes against 1080 mattes
                rgb = np.asarray(Image.fromarray(rgb).resize((old.shape[1], old.shape[0]), Image.LANCZOS))
            new = np.maximum(old, key(rgb, old) * 255)
            Image.fromarray(np.clip(new, 0, 255).astype(np.uint8)).save(os.path.join(mdir, f"{i:05d}.png"))
            if i % 30 == 0:
                ys, xs = np.nonzero(old > 128)
                y0 = max(0, ys.min() - 60)
                sl = (slice(y0, y0 + 220), slice(560, 1260))
                crops.append(np.vstack([rgb[sl], np.repeat(old[sl][..., None], 3, 2).astype(np.uint8),
                                        np.repeat(new[sl][..., None], 3, 2).astype(np.uint8)]))
    Image.fromarray(np.hstack(crops)).save(mdir.rstrip("/") + "_pencils_check.jpg", quality=88)
    print(os.path.relpath(mdir, ROOT), i + 1, "frames keyed; originals in", os.path.relpath(bak, ROOT))


if __name__ == "__main__":
    FERRULE = "--ferrule" in sys.argv
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    main(a[0], a[1])
