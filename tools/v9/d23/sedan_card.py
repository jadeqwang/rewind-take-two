#!/usr/bin/env python3
"""The TVA sedan impostor for the mirror: sedan_a.png (nano-banana, flat grey background) -> RGBA with a key matte
(background = border median, flood-filled from the edges so the car's own greys stay), plus the blank plate's pixel
rectangle (printed; rig.js SEDAN_IMG). Run with tools/engrave/.venv/bin/python."""
import sys, json
import cv2, numpy as np
src, out = sys.argv[1], sys.argv[2]
im = cv2.cvtColor(cv2.imread(src), cv2.COLOR_BGR2RGB)
H, W = im.shape[:2]
border = np.concatenate([im[:8].reshape(-1, 3), im[-8:].reshape(-1, 3), im[:, :8].reshape(-1, 3), im[:, -8:].reshape(-1, 3)])
bg = np.median(border, 0)
diff = np.abs(im.astype(np.float32) - bg).max(2)
fg = (diff > 22).astype(np.uint8)
fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
# background = connected to the border among non-fg pixels
inv = (1 - fg).astype(np.uint8)
n, lab = cv2.connectedComponents(inv)
edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
bgmask = np.isin(lab, [l for l in edge if l != 0] if 0 not in edge or True else []) & (inv > 0)
alpha = (~bgmask).astype(np.float32)
# keep only the biggest blob (the car)
n2, lab2, st, _ = cv2.connectedComponentsWithStats((alpha > 0).astype(np.uint8))
big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]); alpha = (lab2 == big).astype(np.float32)
alpha = cv2.GaussianBlur(cv2.erode(alpha, np.ones((3, 3), np.uint8)), (5, 5), 1.2)
cv2.imwrite(out, cv2.cvtColor(np.dstack([im, (alpha * 255).astype(np.uint8)]), cv2.COLOR_RGBA2BGRA))
# the plate: the brightest compact rectangle in the bumper zone
zone = im[int(H * 0.55):int(H * 0.8), int(W * 0.45):int(W * 0.75)].mean(2)
pm = (zone > 215).astype(np.uint8)
n3, lab3, st3, _ = cv2.connectedComponentsWithStats(pm)
k = 1 + np.argmax(st3[1:, cv2.CC_STAT_AREA])
x, y, w, h = st3[k, :4]; x += int(W * 0.45); y += int(H * 0.55)
ys, xs = np.where(alpha > 0.5)
print(json.dumps({'size': [W, H], 'plate': [int(x), int(y), int(w), int(h)], 'car': [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]}))
