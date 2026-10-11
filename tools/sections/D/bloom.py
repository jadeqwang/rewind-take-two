#!/usr/bin/env python
"""E1 residue bloom texture: a coloured-pencil radial bloom (orange core -> pale blue -> a little gold at the rim),
radial pencil strokes + paper tooth, transparent outside. RGBA PNG, 2048x2048 centred.
    bloom.py OUT.png"""
import sys
import cv2
import numpy as np

N = 2048
rng = np.random.default_rng(65)
yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
dx, dy = xx - N / 2, yy - N / 2
r = np.sqrt(dx * dx + dy * dy) / (N / 2)
ang = np.arctan2(dy, dx)
noise = cv2.resize(rng.random((64, 64)).astype(np.float32), (N, N), interpolation=cv2.INTER_CUBIC)
fine = cv2.resize(rng.random((N // 3, N // 3)).astype(np.float32), (N, N), interpolation=cv2.INTER_LINEAR)
strokes = 0.5 + 0.5 * np.sin(ang * 340 + noise * 9.0 + r * 6)            # radial pencil strokes
strokes2 = 0.5 + 0.5 * np.sin(ang * 211 - noise * 7.0)
tooth = cv2.GaussianBlur(rng.random((N, N)).astype(np.float32), (0, 0), 0.9)
O, B, G = np.array([0xF0, 0x8A, 0x24]) / 255, np.array([0x8D, 0xB8, 0xE8]) / 255, np.array([0xC9, 0xA2, 0x27]) / 255
w_o = np.clip(1 - (r - 0.45) / 0.45, 0, 1)
w_g = np.exp(-((r - 0.78) / 0.07) ** 2) * (0.5 + 0.5 * np.sin(ang * 7 + noise * 4)) * 0.45
col = O[None, None] * w_o[..., None] + B[None, None] * (1 - w_o[..., None])
col = col * (1 - w_g[..., None]) + G[None, None] * w_g[..., None]
edge = np.clip((1.0 - r) / 0.25, 0, 1) * (0.75 + 0.25 * noise)            # ragged soft rim
edge *= 0.08 + 0.92 * np.clip((r - 0.25) / 0.45, 0, 1) ** 1.5             # a wave: the centre clears
a = edge * (0.45 + 0.55 * (strokes * strokes2 > 0.3) + 0.2 * (fine - 0.5)) * (0.85 + 0.3 * (tooth - 0.5))
a = np.clip(a, 0, 1)
col = np.clip(col * (0.9 + 0.15 * strokes[..., None]), 0, 1)
out = np.dstack([col, a])
cv2.imwrite(sys.argv[1], cv2.cvtColor((out * 255 + 0.5).astype(np.uint8), cv2.COLOR_RGBA2BGRA))
