#!/usr/bin/env python3
"""Singing Jade, step 4: lay her (the restored painting of her kept trace, same place, same scale) over a clean
engraved plate, so the background of the first frame is the plate itself, pixel for pixel (the engine can push into
the very same reflection for S2), and every shot that uses the same figure has exactly the same framing.

    MPY tools/sing/comp.py mask                          -> media/sing/first/her_mask.png (from base16, the trace)
    MPY tools/sing/comp.py comp FIGURE PLATE OUT [--grow=6] [--feather=5]
    MPY tools/sing/comp.py align PAINT PLATE             # how well the painting's background matches the plate
    MPY tools/sing/comp.py extend PAINT PLATE            # add what the painter drew of her beyond the trace (the shoulder
                                                         # the trace cuts off at lower left) to the mask -> her_mask_ext.png
    MPY tools/sing/comp.py unborder IN OUT               # the model leaves a ~22 px cream margin and a black rule: crop to
                                                         # the largest centred 16:9 box inside them (no resize); the box is
                                                         # fixed in media/sing/first/crop.json so all shots crop alike

The silhouette comes from the trace on its plain paper (ink or colour = her; outline closed and holes filled), not from
the painting, so it is the same for every shot. Nothing of her is moved, scaled or redrawn here."""
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = os.path.join(ROOT, "media/sing/first/base16.jpg")
MASK = os.path.join(ROOT, "media/sing/first/her_mask.png")
CROP = os.path.join(ROOT, "media/sing/first/crop.json")
MASK_EXT = os.path.join(ROOT, "media/sing/first/her_mask_ext.png")


def rd(p):
    return np.asarray(Image.open(p).convert("RGB"), np.float32)


def mask():
    a = rd(BASE)
    H, W = a.shape[:2]
    paper = np.median(a[:150].reshape(-1, 3), axis=0)
    lum = a @ [0.299, 0.587, 0.114]
    plum = paper @ [0.299, 0.587, 0.114]
    chroma = np.abs((a - a.mean(2, keepdims=True)) - (paper - paper.mean())).sum(2)
    ink = ((plum - lum) > 16) | (chroma > 28)
    ink = cv2.morphologyEx(ink.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41))
    closed = cv2.morphologyEx(ink, cv2.MORPH_CLOSE, k)
    # background = paper reachable from the top and side edges (her body runs off the bottom edge)
    inv = (1 - closed).astype(np.uint8)
    ff = inv.copy()
    seeds = [(x, 0) for x in range(0, W, 16)] + [(0, y) for y in range(0, H - 40, 16)] + [(W - 1, y) for y in range(0, H - 40, 16)]
    m2 = np.zeros((H + 2, W + 2), np.uint8)
    for sx, sy in seeds:
        if ff[sy, sx] == 1:
            cv2.floodFill(ff, m2, (sx, sy), 2)
    her = (ff != 2).astype(np.uint8)
    # keep the largest component (her), drop stray specks of paper grain
    n, lab, st, _ = cv2.connectedComponentsWithStats(her)
    big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    her = (lab == big).astype(np.uint8)
    her = cv2.erode(her, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))   # closing grew it a little
    Image.fromarray(her * 255).save(MASK)
    print(os.path.relpath(MASK, ROOT), "coverage", round(float(her.mean()), 3))


def comp(fig, plate, out, grow=6, feather=5, mask_path=None):
    F, P = rd(fig), rd(plate)
    if F.shape != P.shape:
        P = np.asarray(Image.fromarray(P.astype(np.uint8)).resize((F.shape[1], F.shape[0]), Image.LANCZOS), np.float32)
    m = (np.asarray(Image.open(mask_path or (MASK_EXT if os.path.exists(MASK_EXT) else MASK))) > 127).astype(np.uint8)
    if grow:
        m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * grow + 1, 2 * grow + 1)))
    m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), feather)[..., None]
    C = F * m + P * (1 - m)
    Image.fromarray(np.clip(C, 0, 255).astype(np.uint8)).save(out, quality=96)
    print(out)


def extend(paint, plate):
    F, P = rd(paint), rd(plate)
    m = (np.asarray(Image.open(MASK)) > 127).astype(np.uint8)
    H, W = m.shape
    d = cv2.GaussianBlur(np.abs(F - P).mean(2), (0, 0), 6)
    cand = (d > 28).astype(np.uint8)
    box = np.zeros_like(cand); box[int(H * 0.55):, :int(W * 0.36)] = 1      # only the lower-left, where the trace ends
    cand = cv2.morphologyEx(cand * box, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(cand)
    touch = cv2.dilate(m, np.ones((15, 15), np.uint8))
    add = np.zeros_like(m)
    for i in range(1, n):
        comp_i = lab == i
        if st[i, cv2.CC_STAT_AREA] > 4000 and (touch[comp_i] > 0).any():
            add |= comp_i.astype(np.uint8)
    ff = add.copy(); h2 = np.zeros((H + 2, W + 2), np.uint8)              # fill holes in the added sleeve
    inv = (1 - ff).astype(np.uint8); cv2.floodFill(inv, h2, (0, 0), 0)
    add = add | inv
    ext = np.maximum(m, add)
    Image.fromarray(ext * 255).save(MASK_EXT)
    print(os.path.relpath(MASK_EXT, ROOT), "added", int(add.sum()), "px; coverage", round(float(ext.mean()), 3))


def margins(src, thr=225):
    g = np.asarray(Image.open(src).convert("L"), np.float32)
    H, W = g.shape

    def width(lines):
        k = 0
        while k < 80 and lines(k).mean() > thr and np.percentile(lines(k), 10) > 195:
            k += 1
        return k + 12 if k else 0                     # + the engraving's black rule line (~10 px)
    return width(lambda k: g[k]), width(lambda k: g[H - 1 - k]), width(lambda k: g[:, k]), width(lambda k: g[:, W - 1 - k])


def cropbox(src):
    """The largest 16:9 box (multiples of 16) centred on the frame centre inside the model's margins: a plain crop, so
    she keeps the trace's scale and stays centred. Saved to media/sing/first/crop.json for every later frame."""
    t, b, l, r = margins(src)
    W, H = Image.open(src).size
    m = max(t, b, round(max(l, r) * 9 / 16))
    h = (H - 2 * m) // 16 * 16
    w = round(h * 16 / 9) // 16 * 16
    h = round(w * 9 / 16)
    x0, y0 = (W - w) // 2, (H - h) // 2
    box = [x0, y0, x0 + w, y0 + h]
    json.dump({"src": os.path.relpath(src, ROOT), "margins_tblr": [t, b, l, r], "box": box}, open(CROP, "w"), indent=1)
    print("margins t/b/l/r", t, b, l, r, "-> crop", box, f"{w}x{h}")
    return box


def unborder(src, out):
    box = json.load(open(CROP))["box"] if os.path.exists(CROP) else cropbox(src)
    Image.open(src).convert("RGB").crop(box).save(out, quality=96)
    print(out, "crop", box)


def align(paint, plate):
    F, P = rd(paint), rd(plate)
    m = (np.asarray(Image.open(MASK)) > 127)
    far = cv2.dilate(m.astype(np.uint8), np.ones((61, 61), np.uint8)) == 0
    g1, g2 = F.mean(2), P.mean(2)
    d = np.abs(g1 - g2)[far]
    sh, resp = cv2.phaseCorrelate(np.where(far, g2, 0).astype(np.float64), np.where(far, g1, 0).astype(np.float64))
    print(f"background mean |diff| {d.mean():.1f}/255, p90 {np.percentile(d, 90):.1f}; shift {np.round(sh, 2)} (resp {resp:.2f})")


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    o = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    if a[0] == "mask":
        mask()
    elif a[0] == "comp":
        comp(a[1], a[2], a[3], int(o.get("grow", 6)), float(o.get("feather", 5)))
    elif a[0] == "extend":
        extend(a[1], a[2])
    elif a[0] == "unborder":
        unborder(a[1], a[2])
    elif a[0] == "align":
        align(a[1], a[2])
