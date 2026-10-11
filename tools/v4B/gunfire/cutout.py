#!/usr/bin/env python3
"""Agent cut-out for G1 (plan: docs/revisions/v4/plans/gunfire.md): agent C of media/shots/B_g2/kf_v3.png, seen from
behind with a level aim, cut out with BiRefNet (+ a dark-ink mask to keep the suit solid) into an RGBA PNG.

    tools/engrave/.venv/bin/python tools/v4B/gunfire/cutout.py
Writes media/shots/B_gcut/agent.png (RGBA) and agent.json: in that PNG's pixels, the muzzle, a point on the rear of
the slide (barrel line), the gun-arm shoulder (rotation pivot), head top and feet.
"""
import json
import os
import sys

import cv2
import numpy as np
import torch

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/engrave"))
from matte import BiRefNet  # noqa: E402

SRC = os.path.join(ROOT, "media/shots/B_g2/kf_v3.png")
OUT = os.path.join(ROOT, "media/shots/B_gcut")
BOX = (780, 420, 1400, 1380)                    # x0, y0, x1, y1 in the 2731x1536 keyframe
# landmarks read off the crop (crop px)
MUZZLE, SLIDE, SHOULDER = (566, 184), (452, 180), (215, 178)

os.makedirs(OUT, exist_ok=True)
im = cv2.imread(SRC)[BOX[1]:BOX[3], BOX[0]:BOX[2]]
h, w = im.shape[:2]
pad = 160                                       # BiRefNet sees him with some context
big = cv2.copyMakeBorder(im, pad, pad, pad, pad, cv2.BORDER_REPLICATE)
x = torch.from_numpy(cv2.cvtColor(big, cv2.COLOR_BGR2RGB)).permute(2, 0, 1)[None].float().cuda() / 255
m = BiRefNet()(x)[0, 0].cpu().numpy()[pad:pad + h, pad:pad + w]
# the suit is solid ink: keep BiRefNet's soft edge but fill its interior; drop specks away from the figure
hard = (m > 0.5).astype(np.uint8)
n, lab, st, _ = cv2.connectedComponentsWithStats(hard)
keep = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
body = (lab == keep).astype(np.uint8)
body = cv2.morphologyEx(body, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
alpha = np.clip(np.where(cv2.dilate(body, np.ones((5, 5), np.uint8)) > 0, m, 0) * 1.15, 0, 1)
alpha = np.maximum(alpha, cv2.erode(body, np.ones((3, 3), np.uint8)).astype(np.float32))
rgba = np.dstack([im, (alpha * 255).astype(np.uint8)])
cv2.imwrite(os.path.join(OUT, "agent.png"), rgba)
ys, xs = np.nonzero(alpha > 0.5)
info = dict(src=os.path.relpath(SRC, ROOT), box=BOX, size=[w, h], muzzle=MUZZLE, slide=SLIDE, shoulder=SHOULDER,
            head_top=[int(xs[ys.argmin()]), int(ys.min())], feet_y=int(ys.max()),
            barrel_deg=float(np.degrees(np.arctan2(MUZZLE[1] - SLIDE[1], MUZZLE[0] - SLIDE[0]))))
json.dump(info, open(os.path.join(OUT, "agent.json"), "w"), indent=1)
# check sheet: cut-out over grey, landmarks marked
chk = np.full_like(im, 128)
a3 = alpha[..., None]
chk = (im * a3 + chk * (1 - a3)).astype(np.uint8)
for p, c in ((MUZZLE, (0, 0, 255)), (SLIDE, (0, 200, 0)), (SHOULDER, (255, 0, 0))):
    cv2.circle(chk, p, 6, c, 2)
cv2.line(chk, SLIDE, (int(SLIDE[0] + 3 * (MUZZLE[0] - SLIDE[0])), int(SLIDE[1] + 3 * (MUZZLE[1] - SLIDE[1]))), (0, 0, 255), 1)
cv2.imwrite(os.path.join(OUT, "agent_check.jpg"), chk)
print(json.dumps(info))
