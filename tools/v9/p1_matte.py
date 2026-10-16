#!/usr/bin/env python
"""v9 fix 9: Jade's matte in P1 take_v9_2. She is small in the driver's window, so the engrave matte (BiRefNet on the
whole frame) loses her in every frame and she is engraved grey. Here BiRefNet runs on a crop of the driver's window
only (where she is the salient subject), the result is limited to the window box, and it is merged (max) into the
engrave matte. Then: engrave.py again with --matte-in (same flags as tools/sectionA/engrave_take.sh).

    FFMPEG=... tools/engrave/.venv/bin/python tools/v9/p1_matte.py [--check K]   # --check: overlay jpgs only
"""
import os
import sys

import av
import cv2
import numpy as np
import torch
from PIL import Image

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/engrave"))
from matte import get_birefnet  # noqa: E402

RAW = os.path.join(ROOT, "media/shots/P1/take_v9_2.mp4")
OLD = os.path.join(ROOT, "media/shots/P1/take_v9_2_matte")
OUT = os.path.join(ROOT, "media/shots/P1/take_v9_2_matte_jade")
BOX = (380, 320, 990, 735)      # 1920x1080 px: the open driver's window with her in it (B-pillar / agent at x > 975)
LIMIT = (395, 330, 972, 726)     # what may enter the matte

frames = [f.to_ndarray(format="rgb24") for f in av.open(RAW).decode(video=0)]
net = get_birefnet()
check = "--check" in sys.argv
os.makedirs(OUT, exist_ok=True)
x0, y0, x1, y1 = BOX
prev = None
for i, fr in enumerate(frames):
    big = cv2.resize(fr, (1920, 1080), interpolation=cv2.INTER_CUBIC)
    crop = big[y0:y1, x0:x1]
    t = torch.from_numpy(crop).permute(2, 0, 1)[None].float().cuda() / 255
    p = net(t)[0, 0].cpu().numpy()
    m = np.zeros((1080, 1920), np.float32)
    m[y0:y1, x0:x1] = p
    lim = np.zeros_like(m); lim[LIMIT[1]:LIMIT[3], LIMIT[0]:LIMIT[2]] = 1
    m *= lim
    m[655:, :540] = 0   # the steering column and lower wheel rim below her hand
    b = (m > 0.5).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(b)
    if n > 1:   # keep the largest blob (her) plus any blob over 4 % of it (her hand on the wheel)
        big_i = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
        keep = [j for j in range(1, n) if st[j, cv2.CC_STAT_AREA] >= 0.04 * st[big_i, cv2.CC_STAT_AREA]]
        m *= np.isin(lab, keep)
    if prev is not None:   # light temporal smoothing against flicker
        m = 0.7 * m + 0.3 * prev
    prev = m
    old = np.asarray(Image.open(os.path.join(OLD, f"{i:05d}.png")).convert("L")).astype(np.float32) / 255
    if old.shape != m.shape:
        old = cv2.resize(old, (1920, 1080))
    out = np.maximum(old, cv2.GaussianBlur(m, (0, 0), 1.0))
    if check:
        if i in (0, 30, 60, 96):
            ov = big.copy(); ov[out > 0.5] = (0.5 * ov[out > 0.5] + [0, 127, 0]).astype(np.uint8)
            Image.fromarray(ov[y0:y1, x0:x1]).save(os.path.join(sys.argv[sys.argv.index("--check") + 1], f"p1m_{i}.jpg"))
        continue
    Image.fromarray((out * 255).clip(0, 255).astype(np.uint8)).save(os.path.join(OUT, f"{i:05d}.png"))
print("frames", len(frames), "->", OUT if not check else "check")
