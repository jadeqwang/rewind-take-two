#!/usr/bin/env python3
"""E5 fix (Jade, v4: "gold ethereal jade's arm pointing to Banach Tarski goes invisible for a moment"): from about take
frame 28 to 86 the engrave matte of media/shots/B_slide_point_b lost the gold ghost's pointing forearm and hand (pale
sleeve and skin over the pale label), so the clean patch showed through where the arm is. This re-segments a crop
round the arm with BiRefNet on the raw take, keeps only what is new, touches the ghost and is not the live girl, and
writes a repaired ghost matte dir; ghostseq.py then rebakes the gold ghost from it.

    tools/engrave/.venv/bin/python tools/v4B/coop/armfix.py [--check=sheet.jpg]
    -> media/shots/C_coop/e5_arm/ghost_matte/%05d.png (all 121 frames; unchanged frames copied)
"""
import os
import shutil
import sys

import cv2
import numpy as np
import torch

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/engrave"))
from matte import get_birefnet  # noqa: E402

TK = os.path.join(ROOT, "media/shots/B_slide_point_b")
OUT = os.path.join(ROOT, "media/shots/C_coop/e5_arm/ghost_matte")
BOX = (1150, 60, 1790, 700)                 # x0 y0 x1 y1: the ghost's upper body, arm and hand in every frame
ARM = (1380, 120, 1760, 470)                # only pixels in here may be added (forearm + hand region)


def main(check=None):
    os.makedirs(OUT, exist_ok=True)
    cap = cv2.VideoCapture(os.path.join(TK, "take_1.mp4"))
    net = get_birefnet()
    x0, y0, x1, y1 = BOX
    added, sheet, G, K, F_ = [], [], [], [], []
    i = 0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        f = cv2.resize(f, (1920, 1080), interpolation=cv2.INTER_LANCZOS4)
        g = cv2.imread(os.path.join(TK, "take_1_ghost", f"{i:05d}.png"), 0)
        lv = cv2.imread(os.path.join(TK, "take_1_live", f"{i:05d}.png"), 0) > 127
        crop = cv2.cvtColor(f[y0:y1, x0:x1], cv2.COLOR_BGR2RGB)
        t = torch.from_numpy(crop).cuda().permute(2, 0, 1)[None].float() / 255
        p = net(t)[0, 0].cpu().numpy()
        m = np.zeros(g.shape, bool)
        m[y0:y1, x0:x1] = p > 0.5
        lvd = cv2.dilate(lv.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
        cand = m & ~lvd & ~(g > 127)
        a = np.zeros_like(cand)
        a[ARM[1]:ARM[3], ARM[0]:ARM[2]] = cand[ARM[1]:ARM[3], ARM[0]:ARM[2]]
        # keep only components that touch the existing ghost matte
        gd = cv2.dilate((g > 127).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
        n, lab = cv2.connectedComponents(a.astype(np.uint8))
        keep = np.zeros_like(a)
        for k in range(1, n):
            comp = lab == k
            if (comp & gd).any() and comp.sum() > 150:
                keep |= comp
        keep = cv2.morphologyEx(keep.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) > 0
        G.append(g)
        K.append(keep)
        F_.append(f)
        i += 1
    # BiRefNet keeps the forearm on some frames only: the arm moves slowly, so each frame also takes its neighbours'
    # recovered arm (a 3-frame union), which removes the flicker
    for i in range(len(G)):
        g = G[i]
        keep = K[max(0, i - 1)] | K[i] | K[min(len(K) - 1, i + 1)] if K[i].any() or (0 < i < len(K) - 1 and K[i - 1].any() and K[i + 1].any()) else K[i]
        keep &= ~(g > 127)
        cv2.imwrite(os.path.join(OUT, f"{i:05d}.png"), np.maximum(g, (keep * 255).astype(np.uint8)))
        added.append(int(keep.sum()))
        f = F_[i]
        if check and i % 6 == 0 and 18 <= i <= 90:
            e = cv2.imread(os.path.join(TK, "take_1_sheet.jpg")) if False else f.copy()
            v = e.copy()
            v[g > 127] = (0.55 * v[g > 127] + [0, 90, 115]).astype(np.uint8)
            v[keep] = (0.4 * v[keep] + [0, 0, 150]).astype(np.uint8)
            c = v[100:600, 1200:1800].copy()
            cv2.putText(c, f"f{i} +{keep.sum()}", (6, 26), 0, 0.8, (0, 0, 255), 2)
            sheet.append(c)
    print("frames", len(G), "added px per frame:", added)
    if check:
        while len(sheet) % 4:
            sheet.append(np.zeros_like(sheet[0]))
        cv2.imwrite(check, np.vstack([np.hstack(sheet[k:k + 4]) for k in range(0, len(sheet), 4)]))


if __name__ == "__main__":
    o = {x[2:].partition("=")[0]: x[2:].partition("=")[2] for x in sys.argv[1:] if x.startswith("--")}
    main(o.get("check"))
