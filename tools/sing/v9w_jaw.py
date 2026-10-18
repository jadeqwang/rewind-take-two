#!/usr/bin/env python3
"""Singing Jade (v9w): jaw / chin stability of a take (Jade on the old watercolour animation: "a little bit strange
distortion in the chin that was a little bit unnatural and was hard to correct for").

The jaw outline moves when the mouth opens, so the measures are ones that opening should NOT change:
    gonial   jaw width at the gonial points (172-397) / inter-ocular
    midjaw   jaw width half way to the chin (136-365) / inter-ocular
    chin_x   chin (152) offset from the face midline (168-6 line extended) / inter-ocular (a sideways chin = warp)
    upper    Procrustes residual of the upper jaw contour (127,234,93,132,58,172 / 356,454,323,361,288,397) against the
             first frame, after a similarity fit on eyes + nose bridge, / inter-ocular (rigid head turns cancel out)
Per take: first-frame value, p5..p95 spread, the worst frame (clip s). Head yaw is printed too, since a turn narrows the
projected jaw honestly.

    MPY=~/Documents/1-music-shipped/orbital-sunrise-video/video/out/.venv/bin/python
    $MPY tools/sing/v9w_jaw.py TAKE.mp4 [...]       -> TAKE.jaw.json + a table
"""
import json
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mouth as MT  # noqa: E402

STABLE = [33, 133, 362, 263, 168, 6, 197, 195]
UPPER = [127, 234, 93, 132, 58, 172, 356, 454, 323, 361, 288, 397]


def track(mp4):
    m = MT.cached(mp4)
    cap = cv2.VideoCapture(mp4)
    out, i = [], 0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
        H, W = rgb.shape[:2]
        mx, my, fh = (m[k][i] if i < len(m[k]) else None for k in ("mx", "my", "fh"))
        hit = None
        if mx is not None:
            s = 1.6 * fh
            hit = MT.detect(rgb, (max(0, mx - s), max(0, my - 1.3 * s), min(W, mx + s), min(H, my + 0.7 * s)))
        out.append(None if hit is None else hit[0])
        i += 1
    return out, m["fps"]


def main(paths):
    print(f"{'take':26s} {'gonial f0 / p5-p95':>22s} {'midjaw f0 / p5-p95':>22s} {'chin_x p5..p95':>16s} "
          f"{'upper p50/p95/max (s)':>26s} {'yaw p5..p95':>14s}")
    for p in paths:
        Ls, fps = track(p)
        L0 = next(L for L in Ls if L is not None)
        rows = []
        for i, L in enumerate(Ls):
            if L is None:
                continue
            io = np.linalg.norm(L[33] - L[263])
            d = lambda a, b: float(np.linalg.norm(L[a] - L[b])) / io  # noqa: E731
            ax = L[6] - L[168]
            ax = ax / (np.linalg.norm(ax) + 1e-9)
            v = L[152] - L[168]
            chin_x = float((v[0] * ax[1] - v[1] * ax[0]) / io)
            M, _ = cv2.estimateAffinePartial2D(L0[STABLE].astype(np.float32), L[STABLE].astype(np.float32))
            P0 = L0[UPPER] @ M[:, :2].T + M[:, 2]
            up = float(np.linalg.norm(P0 - L[UPPER], axis=1).mean() / io)
            yaw = float((L[1][0] - (L[33][0] + L[263][0]) / 2) / io)
            rows.append((i, d(172, 397), d(136, 365), chin_x, up, yaw))
        R = np.array(rows)
        pc = lambda c: (np.percentile(R[:, c], 5), np.percentile(R[:, c], 95))  # noqa: E731
        worst = int(R[np.argmax(R[:, 4]), 0])
        res = dict(file=p, n=len(R), gonial_f0=R[0, 1], gonial=pc(1), midjaw_f0=R[0, 2], midjaw=pc(2), chin_x=pc(3),
                   upper_p50=float(np.median(R[:, 4])), upper_p95=float(np.percentile(R[:, 4], 95)),
                   upper_max=float(R[:, 4].max()), upper_worst_s=round(worst / fps, 2), yaw=pc(5))
        json.dump(res, open(p[:-4] + ".jaw.json", "w"), indent=1, default=float)
        print(f"{os.path.basename(p)[:26]:26s} {R[0,1]:6.3f} / {res['gonial'][0]:.3f}-{res['gonial'][1]:.3f}  "
              f"{R[0,2]:6.3f} / {res['midjaw'][0]:.3f}-{res['midjaw'][1]:.3f}  {res['chin_x'][0]:+.3f}..{res['chin_x'][1]:+.3f}  "
              f"{res['upper_p50']:.3f}/{res['upper_p95']:.3f}/{res['upper_max']:.3f} ({res['upper_worst_s']:.2f}s)  "
              f"{res['yaw'][0]:+.3f}..{res['yaw'][1]:+.3f}")


if __name__ == "__main__":
    main(sys.argv[1:])
