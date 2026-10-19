#!/usr/bin/env python
"""v10 F4 blend (Jade 2026-10-18): close the leg gap in the front3 reflection painting.

front3_1.png stands with her feet apart (the inner gap opens from ~10 px at the crotch to ~250 px at the shoes), while
in the shot she falls with her legs nearly together, as the check's pose reference has them. This pinches each row
under the crotch towards the gap's centre line so the inner gap stays about GAP px: each leg slides inward by the
excess gap, i.e. turns about its hip to hang straight. Only the splayed leg moves (Jade: the straight one already
matches her body in the shot); the straighter leg is the one whose inner edge drifts less, or pick with --hold. Rows
above the crotch are untouched.

    tools/engrave/.venv/bin/python tools/sectionF/f4_legs_pinch.py IN.png OUT.png [--gap 28] [--hold auto|left|right]
        [--sheet SHEET.jpg]
"""
import argparse
import os
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../engrave"))


def matte(im):
    import torch
    from matte import get_birefnet
    net = get_birefnet("cuda")
    t = torch.from_numpy(im[..., ::-1].copy()).permute(2, 0, 1)[None].float().cuda() / 255
    return net(t)[0, 0].cpu().numpy() > 0.5


def inner_edges(m, y0, y1, xc0):
    """Per row, the gap between the legs: the empty run that holds the figure's centre column (or is nearest it)."""
    rows, xl, xr = [], [], []
    for y in range(y0, y1):
        xs = np.where(m[y])[0]
        if len(xs) < 2:
            continue
        br = np.where(np.diff(xs) > 1)[0]
        if not len(br):
            continue
        gaps = [(xs[b], xs[b + 1]) for b in br]
        l, r = min(gaps, key=lambda g: abs((g[0] + g[1]) / 2 - xc0))
        if r - l < 3 or not (l < xc0 + 120 and r > xc0 - 120):
            continue
        rows.append(y), xl.append(l), xr.append(r)
    return np.array(rows), np.array(xl, float), np.array(xr, float)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--gap", type=float, default=28, help="target inner gap between the legs, painting px")
    ap.add_argument("--hold", choices=["auto", "left", "right"], default="auto",
                    help="the leg (picture side, upright painting) that stays put; auto: the straighter one")
    ap.add_argument("--sheet", default=None)
    a = ap.parse_args()

    im = cv2.imread(a.src)
    H, W = im.shape[:2]
    m = matte(im)
    ys, xs = np.where(m)
    # the crotch: the first row (from the waist down) where the figure splits round its centre column
    xc0 = float(np.median(xs[ys > H * 0.5]))
    rows, xl, xr = inner_edges(m, int(H * 0.5), ys.max() - 30, xc0)
    crotch = int(rows.min())
    # straight-line fits of each inner edge (the shoes and straps make the raw edges ragged)
    pl, pr = np.polyfit(rows, xl, 1), np.polyfit(rows, xr, 1)
    y = np.arange(H, dtype=np.float32)
    L, Rr = np.polyval(pl, y), np.polyval(pr, y)
    hold = a.hold if a.hold != "auto" else ("left" if abs(pl[0]) < abs(pr[0]) else "right")
    e = np.clip((Rr - L) - a.gap, 0, None)
    e[y < crotch] = 0
    # ease in over the first 40 rows so the pelvis doesn't kink
    e *= np.clip((y - crotch) / 40.0, 0, 1)
    gx, gy = np.meshgrid(np.arange(W, dtype=np.float32), y)
    # the held leg's side of the new gap's middle samples itself; the other side samples e further out
    if hold == "left":
        b = (L + a.gap / 2)[:, None]
        mx = np.where(gx < b, gx, gx + e[:, None])
    else:
        b = (Rr - a.gap / 2)[:, None]
        mx = np.where(gx > b, gx, gx - e[:, None])
    out = cv2.remap(im, mx.astype(np.float32), gy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    cv2.imwrite(a.out, out)
    print(f"crotch y={crotch}, gap {Rr[crotch]-L[crotch]:.0f} -> {Rr[ys.max()]-L[ys.max()]:.0f} px at the shoes;"
          f" inner-edge slopes L {pl[0]:.3f} R {pr[0]:.3f}; held {hold}, the other moves in up to {e.max():.0f} px;"
          f" wrote {a.out}")
    if a.sheet:
        s = lambda z: cv2.resize(z, (W * 700 // H, 700))
        cv2.imwrite(a.sheet, np.hstack([s(im), s(out)]))


if __name__ == "__main__":
    main()
