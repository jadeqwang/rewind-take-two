#!/usr/bin/env python
"""Luminous ghost sprites: a frozen iteration of Jade baked as a full-frame RGBA PNG (1920x1080, same framing as the
clip, so it drops onto the plate with fit 'cover' and the usual x/y/scale), drawn as a coloured-pencil afterimage:

  * interior: light tint of the hue (paper-white lifted), the clip's own line work kept as darker hue strokes,
    diagonal pencil hatching grain, alpha ~.8
  * a thin bright outline in the hue (lifted toward white)
  * a soft outer glow in the hue

    ghostsprite.py ENGRAVED.mp4 MATTE_DIR FREEZE_S HEX OUT.png [--outline=3] [--glow=16] [--alpha=0.8] [--box=x0,y0,x1,y1]
Python API: sprite(eng, matte_dir, t, hexcol, out, ...)
"""
import glob
import os
import sys

import av
import cv2
import numpy as np

W, H = 1920, 1080


def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255.0


_cache = {}


def frame(path, t):
    key = (path, round(t * 24))
    if key in _cache:
        return _cache[key]
    i = round(t * 24)
    with av.open(path) as c:
        for k, f in enumerate(c.decode(video=0)):
            if k == i:
                im = np.asarray(f.to_image().convert("RGB").resize((W, H))).astype(np.float32) / 255.0
                _cache[key] = im
                return im
    raise ValueError(f"{path}: no frame {i}")


def hatch(seed=0):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    n = rng.random((H // 4 + 1, W // 4 + 1)).astype(np.float32)
    n = cv2.resize(n, (W, H), interpolation=cv2.INTER_LINEAR)
    lines = 0.5 + 0.5 * np.sin((xx + yy) * (2 * np.pi / 7.0) + n * 3.0)       # 45° pencil strokes, 7 px pitch
    tooth = cv2.GaussianBlur(rng.random((H, W)).astype(np.float32), (0, 0), 0.8)
    return np.clip(0.86 + 0.12 * lines + 0.2 * (tooth - 0.5), 0, 1.05)


_HATCH = None


def sprite(eng, matte_dir, t, hexcol, out, outline=4, glow=18, alpha=0.9, box=None, seed=0):
    global _HATCH
    if _HATCH is None:
        _HATCH = hatch(seed)
    rgb = frame(eng, t)
    fs = sorted(glob.glob(os.path.join(matte_dir, "*.png")))
    m = cv2.imread(fs[min(len(fs) - 1, round(t * 24))], cv2.IMREAD_GRAYSCALE)
    m = cv2.resize(m, (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255.0
    if box:
        b = np.zeros_like(m)
        b[int(box[1] * H):int(box[3] * H), int(box[0] * W):int(box[2] * W)] = 1
        m *= b
    m = np.clip((m - 0.35) / 0.3, 0, 1)                       # firm edge
    m = cv2.GaussianBlur(m, (0, 0), 0.8)
    hue = hexrgb(hexcol)
    light = np.clip((hue + (1 - hue) * 0.32) * 1.08, 0, 1)                             # lifted, pastel
    L = rgb.mean(2)
    ink = np.clip((cv2.GaussianBlur(L, (0, 0), 3) - L - 0.03) / 0.10, 0, 1)   # her line work only (local darks)
    Ln = (L - L[m > 0.5].min()) / max(1e-3, np.ptp(L[m > 0.5])) if (m > 0.5).any() else L
    body = light[None, None] * (0.86 + 0.14 * np.clip(Ln, 0, 1)[..., None])
    body = body * (1 - 0.8 * ink[..., None]) + (hue * 0.5)[None, None] * (0.8 * ink[..., None])
    body *= _HATCH[..., None]
    # outline: a thin band just outside the silhouette, bright hue
    mb = (m > 0.5).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * outline + 1, 2 * outline + 1))
    ring = np.clip(cv2.dilate(mb, k).astype(np.float32) - mb, 0, 1)
    ring = cv2.GaussianBlur(ring, (0, 0), 0.7)
    rim = np.clip(hue * 1.2 + 0.12, 0, 1)
    # glow: soft halo outside
    g = cv2.GaussianBlur(cv2.dilate(mb, k).astype(np.float32), (0, 0), glow)
    g = np.clip(g * 1.6, 0, 1) * (1 - m)
    # composite (premultiplied, over): glow < body < outline
    a_g = 0.7 * g
    a_b = alpha * m
    a_r = 0.95 * ring
    C = hue[None, None] * a_g[..., None]
    A = a_g.copy()
    C = body * a_b[..., None] + C * (1 - a_b[..., None]); A = a_b + A * (1 - a_b)
    C = rim[None, None] * a_r[..., None] + C * (1 - a_r[..., None]); A = a_r + A * (1 - a_r)
    rgbout = np.where(A[..., None] > 1e-4, C / np.maximum(A[..., None], 1e-4), 0)
    outimg = np.dstack([np.clip(rgbout, 0, 1), np.clip(A, 0, 1)])
    cv2.imwrite(out, cv2.cvtColor((outimg * 255 + 0.5).astype(np.uint8), cv2.COLOR_RGBA2BGRA))
    ys, xs = np.nonzero(m > 0.5)
    return dict(cx=float(xs.mean() - W / 2), cy=float(ys.mean() - H / 2), y0=float(ys.min() - H / 2), y1=float(ys.max() - H / 2),
                x0=float(xs.min() - W / 2), x1=float(xs.max() - W / 2))


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    o = {x[2:].split("=")[0]: x.split("=", 1)[1] for x in sys.argv[1:] if x.startswith("--")}
    box = [float(v) for v in o["box"].split(",")] if "box" in o else None
    print(sprite(a[0], a[1], float(a[2]), a[3], a[4], int(o.get("outline", 3)), float(o.get("glow", 16)),
                 float(o.get("alpha", 0.9)), box))
