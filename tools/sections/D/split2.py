#!/usr/bin/env python
"""Split a two-Jade matte into the two girls, frame by frame, by tracking the two bodies (rev 5).

The engrave matte holds both copies of her as one blob wherever they touch (wrists, hands, a foot in cupped hands).
Frame `seed` is split by two seed boxes (each girl = matte ∩ her box, seeds only need to be partial); every other
frame is split by a marker watershed on the engraved colour frame, whose markers are the previous frame's two
labels eroded and intersected with this frame's matte. It walks forward and backward from the seed frame.

    split2.py STEM SEED_S AX0,AY0,AX1,AY1 BX0,BY0,BX1,BY1 [--erode=9] [--t0=0] [--t1=99] [--matte=_matte]
      STEM = media/shots/B_boost/take_1   girl A (the ghost) -> STEM_ghost/, girl B (live) -> STEM_live/
writes PNG sequences (frame numbers as in the matte dir; frames outside [t0, t1] are left black), matte.mp4 in each
dir, and STEM_split_sheet.jpg (A blue, B orange) for review.
"""
import glob
import os
import subprocess
import sys

import av
import cv2
import numpy as np

FF = os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg")


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    o = {x[2:].split("=")[0]: x.split("=", 1)[1] for x in sys.argv[1:] if x.startswith("--")}
    stem, seed = a[0], float(a[1])
    boxA, boxB = ([float(v) for v in s.split(",")] for s in a[2:4])
    er = int(o.get("erode", 9))
    t0, t1 = float(o.get("t0", 0)), float(o.get("t1", 99))
    mfs = sorted(glob.glob(stem + o.get("matte", "_matte") + "/*.png"))
    frames = []
    with av.open(stem + "_engraved.mp4") as c:
        for f in c.decode(video=0):
            frames.append(cv2.cvtColor(np.asarray(f.to_image().convert("RGB")), cv2.COLOR_RGB2BGR))
    n = min(len(mfs), len(frames))
    H, W = frames[0].shape[:2]
    M = [cv2.resize(cv2.imread(mfs[i], 0), (W, H)) for i in range(n)]
    lab = [None] * n
    i0 = min(n - 1, round(seed * 24))
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * er + 1, 2 * er + 1))

    def boxmask(b):
        z = np.zeros((H, W), bool)
        z[int(b[1] * H):int(b[3] * H), int(b[0] * W):int(b[2] * W)] = True
        return z

    def ws(i, mA, mB):
        m = M[i] >= 128
        mk = np.zeros((H, W), np.int32)
        mk[~cv2.dilate(m.astype(np.uint8), k).astype(bool)] = 3          # background
        mk[mA & m] = 1
        mk[mB & m & ~mA] = 2
        if not (mk == 1).any() or not (mk == 2).any():
            return mA & m, mB & m
        r = cv2.watershed(frames[i], mk.copy())
        return (r == 1) & m, (r == 2) & m

    if "kmeans" in o:
        # per frame, no tracking: 2-means on the matte's pixel positions, girl A = the cluster further along the
        # direction d (e.g. 1,1 = lower right); the halves, eroded, seed the watershed so the cut follows her ink lines
        d = np.array([float(v) for v in o["kmeans"].split(",")], np.float32)
        for i in range(n):
            ys, xs = np.nonzero(M[i] >= 128)
            if len(xs) < 400:
                lab[i] = (np.zeros((H, W), bool), np.zeros((H, W), bool))
                continue
            P = np.stack([xs, ys], 1).astype(np.float32)[::7]
            _, lb, cen = cv2.kmeans(P, 2, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5), 3,
                                    cv2.KMEANS_PP_CENTERS)
            ca = int(np.argmax(cen @ d))
            mid, nv = cen.mean(0), (cen[ca] - cen[1 - ca]) / (np.linalg.norm(cen[ca] - cen[1 - ca]) + 1e-6)
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
            s = (xx - mid[0]) * nv[0] + (yy - mid[1]) * nv[1]
            gap = float(o.get("gap", 40))
            lab[i] = ws(i, s > gap, s < -gap)
    else:
        lab[i0] = ws(i0, boxmask(boxA), boxmask(boxB))
    for rng in (() if "kmeans" in o else (range(i0 + 1, n), range(i0 - 1, -1, -1))):
        prev = i0
        for i in rng:
            pA, pB = lab[prev]
            eA = cv2.erode(pA.astype(np.uint8), k).astype(bool)
            eB = cv2.erode(pB.astype(np.uint8), k).astype(bool)
            if eA.sum() < 200:
                eA = pA
            if eB.sum() < 200:
                eB = pB
            lab[i] = ws(i, eA, eB)
            prev = i
    for side, j in (("_ghost", 0), ("_live", 1)):
        d = stem + side
        os.makedirs(d, exist_ok=True)
        for i in range(n):
            ok = t0 - 1e-6 <= i / 24 <= t1 + 1e-6
            g = (lab[i][j] & (M[i] >= 128)) if ok else np.zeros((H, W), bool)
            # soft edge from the original matte's own alpha, inside the label
            soft = np.where(cv2.dilate(g.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0, M[i], 0)
            cv2.imwrite(f"{d}/{i:05d}.png", soft.astype(np.uint8))
        open(f"{d}/fps.txt", "w").write("24\n")
        subprocess.run([FF, "-y", "-loglevel", "error", "-framerate", "24", "-i", f"{d}/%05d.png", "-c:v", "libx264",
                        "-pix_fmt", "yuv420p", "-crf", "12", f"{d}/matte.mp4"], check=True)
    tiles = []
    for i in np.linspace(0, n - 1, 10).astype(int):
        im = frames[i].astype(np.float32)
        A, B = lab[i]
        im[A] = 0.45 * im[A] + 0.55 * np.array([216, 111, 62])
        im[B] = 0.45 * im[B] + 0.55 * np.array([36, 138, 240])
        im = cv2.resize(im.astype(np.uint8), (384, 216))
        cv2.putText(im, f"{i / 24:.2f}", (4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
        tiles.append(im)
    cv2.imwrite(stem + "_split_sheet.jpg", np.vstack([np.hstack(tiles[:5]), np.hstack(tiles[5:])]))
    print("wrote", stem + "_ghost", stem + "_live")


if __name__ == "__main__":
    main()
