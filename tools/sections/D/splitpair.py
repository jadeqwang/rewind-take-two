#!/usr/bin/env python
"""Split two Jades who stay in contact (holding hands) into ghost + live, rev 5b. Every matte pixel goes to exactly one
girl (an unassigned pixel would show the plate, i.e. her real colours under a ghost).
  seed frame: 2-means on the matte's pixel positions; girl A (ghost) = the cluster further along DIR
  other frames, walking out from the seed: each pixel goes to the girl whose previous mask (shifted by her own
  velocity) is nearer; small islands are re-assigned to the girl they touch most. Matte components smaller than
  --minarea or not touching either girl's prediction are dropped (scenery).
    splitpair.py STEM SEED_S DX,DY [--matte=_fmatte] [--t0=0.6] [--t1=4.5] [--poly=x,y;x,y;... (girl A on the seed frame)]
writes STEM_ghost/, STEM_live/ (PNG + matte.mp4)."""
import glob
import os
import subprocess
import sys

import cv2
import numpy as np

FF = os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg")
a = [x for x in sys.argv[1:] if not x.startswith("--")]
o = {x[2:].split("=")[0]: x.split("=", 1)[1] for x in sys.argv[1:] if x.startswith("--")}
stem, seed = a[0], float(a[1])
D = np.array([float(v) for v in a[2].split(",")], np.float32)
M = sorted(glob.glob(stem + o.get("matte", "_fmatte") + "/*.png"))
n = len(M); h, w = cv2.imread(M[0], 0).shape
fi = lambda t: min(n - 1, round(float(t) * 24))
s0, i0, i1 = fi(seed), fi(o.get("t0", 0.6)), fi(o.get("t1", 4.5))
ell = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
mat = lambda i: cv2.imread(M[i], 0) >= 100


def cen(m):
    ys, xs = np.nonzero(m)
    return np.array([xs.mean(), ys.mean()]) if len(xs) else np.zeros(2)


def shift(m, d):
    return cv2.warpAffine(m.astype(np.uint8), np.float32([[1, 0, d[0]], [0, 1, d[1]]]), (w, h), flags=cv2.INTER_NEAREST) > 0


def clean(m, A, B):
    """drop matte components that touch neither prediction."""
    nn, lab = cv2.connectedComponents(m.astype(np.uint8))
    near = cv2.dilate((A | B).astype(np.uint8), ell(25)) > 0
    keep = np.zeros_like(m)
    for k in range(1, nn):
        c = lab == k
        if (c & near).any():
            keep |= c
    return keep


def split(m, pa, pb):
    da = cv2.distanceTransform((~pa).astype(np.uint8), cv2.DIST_L2, 5)
    db = cv2.distanceTransform((~pb).astype(np.uint8), cv2.DIST_L2, 5)
    A = m & (da < db)
    B = m & ~A
    for _ in range(2):      # islands -> the girl whose body is nearer
        for X, Y in ((A, B), (B, A)):
            nn, lab, st, _ = cv2.connectedComponentsWithStats(X.astype(np.uint8))
            if nn <= 2:
                continue
            big = 1 + int(np.argmax(st[1:, 4]))
            body = lab == big
            dx_ = cv2.distanceTransform((~body).astype(np.uint8), cv2.DIST_L2, 5)
            dy_ = cv2.distanceTransform((~Y).astype(np.uint8), cv2.DIST_L2, 5)
            for k in range(1, nn):
                if k != big:
                    c = lab == k
                    if dy_[c].min() < dx_[c].min():          # nearer the other girl's body: hers
                        X[c] = False; Y[c] = True
    return A, B


m = mat(s0)
ys, xs = np.nonzero(m)
P = np.stack([xs, ys], 1).astype(np.float32)[::5]
_, lb, cc = cv2.kmeans(P, 2, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5), 5, cv2.KMEANS_PP_CENTERS)
ca = int(np.argmax(cc @ D))
yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
nv = (cc[ca] - cc[1 - ca]) / np.linalg.norm(cc[ca] - cc[1 - ca]); mid = cc.mean(0)
sd = (xx - mid[0]) * nv[0] + (yy - mid[1]) * nv[1]
GA, GB = {}, {}
if "poly" in o:     # girl A drawn by hand on the seed frame: x,y;x,y;... in design px (1920x1080)
    P = np.array([[float(v) for v in q.split(",")] for q in o["poly"].split(";")]) * [w / 1920, h / 1080]
    pm = np.zeros((h, w), np.uint8); cv2.fillPoly(pm, [P.astype(np.int32)], 1); pm = pm > 0
    GA[s0], GB[s0] = split(m, m & pm, m & ~pm)
else:
    GA[s0], GB[s0] = split(m, m & (sd > 30), m & (sd < -30))
for rng, step in ((range(s0 + 1, i1 + 1), -1), (range(s0 - 1, i0 - 1, -1), 1)):
    for i in rng:
        p, pp = i + step, i + 2 * step
        va = cen(GA[p]) - cen(GA[pp]) if pp in GA else np.zeros(2)
        vb = cen(GB[p]) - cen(GB[pp]) if pp in GB else np.zeros(2)
        pa, pb = shift(GA[p], va), shift(GB[p], vb)
        m = clean(mat(i), pa, pb)
        GA[i], GB[i] = split(m, pa, pb)
for d, S in (("_ghost", GA), ("_live", GB)):
    os.makedirs(stem + d, exist_ok=True)
    for f in glob.glob(stem + d + "/*.png"):
        os.remove(f)
    src = sorted(glob.glob(stem + o.get("matte", "_fmatte") + "/*.png"))
    for i in range(n):
        x = S.get(i, np.zeros((h, w), bool))
        soft = np.where(x, cv2.imread(src[i], 0), 0).astype(np.uint8) if d == "_live" else (x * 255).astype(np.uint8)
        cv2.imwrite(f"{stem}{d}/{i:05d}.png", soft)
    subprocess.run([FF, "-y", "-loglevel", "error", "-framerate", "24", "-i", f"{stem}{d}/%05d.png", "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-crf", "12", f"{stem}{d}/matte.mp4"], check=True)
print("wrote", stem + "_ghost", stem + "_live")
