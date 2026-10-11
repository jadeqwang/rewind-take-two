#!/usr/bin/env python
"""Re-split swarm_boost into the flier (live) and the kneeling girl (ghost), rev 5b (Jade: the ghosts must never show
her real colours, the live girl must never be tinted).

Rules: LIVE must be exact (it is drawn on top, in colour); GHOST must cover the kneeling girl generously (it is drawn
under LIVE, so where it spills onto the flier, LIVE wins).
  base   = engrave matte ∩ dilate(jmatte, 41)          (Jade only, nothing of her dropped, far agents out)
  SEED   frame where the two are separate components: the flier = the component reaching highest
  LIVE   tracked from the seed backward / forward: each base pixel goes to the nearer of (previous LIVE shifted by the
         flier's velocity) and (previous GHOST); so her foot stays hers while it sits in the cupped hands
  GHOST  base minus LIVE, dilated; from TMPL on (she kneels still, arms up, while agents pile in) it is her pose at TMPL
         (dilated) ∪ her own pixels near it, so no agent creeps in and none of her escapes
    swarmsplit.py STEM [--seed=1.92] [--tmpl=2.08] [--t0=0.3] [--t1=3.35]
writes STEM_ghost/, STEM_live/ (PNG + matte.mp4) and STEM_split_sheet.jpg."""
import glob
import os
import subprocess
import sys

import cv2
import numpy as np

FF = os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg")
stem = sys.argv[1]
o = {x[2:].split("=")[0]: x.split("=", 1)[1] for x in sys.argv[2:] if x.startswith("--")}
E = sorted(glob.glob(stem + "_matte/*.png")); J = sorted(glob.glob(stem + "_jmatte/*.png"))
n = len(E); h, w = cv2.imread(E[0], 0).shape
fi = lambda t: min(n - 1, round(float(t) * 24))
s0, tm, i0, i1 = fi(o.get("seed", 1.92)), fi(o.get("tmpl", 1.92)), fi(o.get("t0", 0.3)), fi(o.get("t1", 3.35))
# her foot and shin while the foot sits in the cupped hands (source s -> polygon, design px 1920x1080, read off the
# frames): everything inside is the flier, so her sneaker never turns ghost; the cut is the sole, at the wrists' level
FOOT = [(0.33, [(965, 540), (1110, 540), (1095, 760), (1082, 800), (970, 800), (962, 760)]),
        (0.58, [(965, 550), (1110, 550), (1095, 775), (1080, 818), (965, 818), (960, 775)]),
        (0.83, [(965, 560), (1110, 560), (1095, 790), (1080, 825), (968, 825), (962, 790)]),
        (1.08, [(945, 600), (1035, 600), (1070, 780), (1078, 820), (965, 820), (962, 780)]),
        (1.25, [(955, 560), (1045, 560), (1075, 765), (1078, 805), (965, 805), (962, 765)]),
        (1.50, [(975, 560), (1080, 560), (1095, 690), (1092, 728), (985, 728), (985, 690)])]


def foot(i):
    t = i / 24
    if t > FOOT[-1][0] + 0.12:
        return None
    if t <= FOOT[0][0]:
        P = FOOT[0][1]
    else:
        k = max(j for j in range(len(FOOT)) if FOOT[j][0] <= t)
        if k == len(FOOT) - 1:
            P = FOOT[k][1]
        else:
            (ta, A), (tb, B) = FOOT[k], FOOT[k + 1]
            u = (t - ta) / (tb - ta)
            P = [(a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u) for a, b in zip(A, B)]
    m = np.zeros((h, w), np.uint8)
    cv2.fillPoly(m, [np.array([(x * w / 1920, y * h / 1080) for x, y in P], np.int32)], 1)
    return m > 0
ell = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def base(i):
    e = cv2.imread(E[i], 0) >= 100
    j = cv2.resize(cv2.imread(J[i], 0), (w, h)) >= 100
    return e & (cv2.dilate(j.astype(np.uint8), ell(45)) > 0)


def shift(m, d):
    M = np.float32([[1, 0, d[0]], [0, 1, d[1]]])
    return cv2.warpAffine(m.astype(np.uint8), M, (w, h), flags=cv2.INTER_NEAREST) > 0


def cen(m):
    ys, xs = np.nonzero(m)
    return np.array([xs.mean(), ys.mean()]) if len(xs) else np.zeros(2)


def assign(b, pl, pg):
    """b pixels to the nearer of predicted live pl / previous ghost pg."""
    dl = cv2.distanceTransform((~pl).astype(np.uint8), cv2.DIST_L2, 5)
    dg = cv2.distanceTransform((~pg).astype(np.uint8), cv2.DIST_L2, 5)
    live = b & (dl < dg)
    # keep only live components that touch the prediction (no stray agent/ghost bits)
    nn, lab = cv2.connectedComponents(live.astype(np.uint8))
    keep = np.zeros_like(live)
    for k in range(1, nn):
        c = lab == k
        if (c & cv2.dilate(pl.astype(np.uint8), ell(6)).astype(bool)).any():
            keep |= c
    return keep


def emat(i):
    return cv2.imread(E[i], 0) >= 100


def comps_touching(m, ref, r=6):
    """components of m that touch ref (dilated by r)."""
    nn, lab = cv2.connectedComponents(m.astype(np.uint8))
    rd = cv2.dilate(ref.astype(np.uint8), ell(r)) > 0
    keep = np.zeros_like(m)
    for k in range(1, nn):
        c = lab == k
        if (c & rd).any():
            keep |= c
    return keep


L, G = {}, {}
e = emat(s0)
nn, lab, st, _ = cv2.connectedComponentsWithStats(e.astype(np.uint8))
big = [k for k in range(1, nn) if st[k, 4] > 1500]
L[s0] = lab == min(big, key=lambda k: st[k, 1])          # the flier: the component reaching highest (agents never touch her)
gb = base(s0) & ~L[s0]
gn, gl, gs, _ = cv2.connectedComponentsWithStats(gb.astype(np.uint8))
G[s0] = gl == 1 + int(np.argmax(gs[1:, 4]))             # the kneeling girl: the largest Jade-gated component left
print("seed", s0 / 24, "components", len(big))
T = None
for rng, step in ((range(s0 - 1, i0 - 1, -1), 1), (range(s0 + 1, i1 + 1), -1)):
    for i in rng:
        p = i + step
        e, b = emat(i), base(i)
        # LIVE: the E components that continue the flier; where she touches the kneeling girl, nearest previous label
        cl = comps_touching(e, L[p], 8)
        dl = cv2.distanceTransform((~L[p]).astype(np.uint8), cv2.DIST_L2, 5)
        dg = cv2.distanceTransform((~G[p]).astype(np.uint8), cv2.DIST_L2, 5)
        L[i] = comps_touching(cl & (dl <= dg), L[p], 8)
        # GHOST: Jade pixels (base) that continue the kneeling girl
        if i >= tm and step == -1:
            if T is None:     # her still kneeling pose (two clean frames before the agents reach her), arms from the seed
                k40 = fi(1.67)
                low = G[k40].copy(); low[: int(0.70 * h)] = False      # legs and back shoe only (her arms moved)
                T = (cv2.dilate((low | G[s0]).astype(np.uint8), ell(8)) > 0)
                TA = cv2.dilate(G[s0].astype(np.uint8), ell(10)) > 0
                ARM = cv2.dilate(G[s0].astype(np.uint8), ell(45)) > 0
                ytop = int(np.nonzero(G[s0])[0].min()) + 60
            G[i] = (e & T & ~L[i]) | (b & TA & ~L[i])
            up = comps_touching(e & ~L[i] & ~G[i], G[i], 3)
            up[ytop:] = False                                   # her raised hands, above her head line
            up &= ARM
            G[i] |= up
        else:
            e_ = e & ~L[i]
            G[i] = (e_ & (cv2.dilate(G[p].astype(np.uint8), ell(12)) > 0)) | comps_touching(b & ~L[i], G[p], 10)
up = comps_touching(emat(s0) & ~L[s0] & ~G[s0], G[s0], 3)
up[int(np.nonzero(G[s0])[0].min()) + 60:] = False
G[s0] |= up
for i in list(L):
    f = foot(i)
    if f is not None:
        L[i] = L[i] | (f & emat(i))
        G[i] = G[i] & ~f
# her hands (rev 5b, Jade: "the blue one seems to have a normal hand"): pale skin on pale paper is often missing from
# the engrave matte (the raised hands), and the cupped hands sit inside FOOT. Skin-coloured pixels of the source frame
# that touch the kneeling girl go to her (with their ink outline); from the launch on (HANDS_TOP = the seed frame) only skin above
# her head line (fixed, from 1.67) is taken, so the agents' faces stay out. Her own sneaker (white, unsaturated) is never skin.
import av  # noqa: E402
SRC = []
with av.open(stem + "_engraved.mp4") as c_:
    for f_ in c_.decode(video=0):
        SRC.append(cv2.resize(f_.to_ndarray(format="bgr24"), (w, h)))
HANDS_TOP = s0                                  # from the launch on her hands are raised above her head
HEAD_Y = int(np.nonzero(G[fi(1.67)])[0].min()) + 40   # her head line in her still kneeling pose (hands cupped low)
for i in sorted(G):
    hsv = cv2.cvtColor(SRC[min(i, len(SRC) - 1)], cv2.COLOR_BGR2HSV).astype(int)
    sk = (hsv[..., 0] >= 3) & (hsv[..., 0] <= 22) & (hsv[..., 1] >= 35) & (hsv[..., 1] <= 150) & (hsv[..., 2] >= 140)
    sk &= cv2.dilate(G[i].astype(np.uint8), ell(70)) > 0
    if i >= HANDS_TOP:
        sk[HEAD_Y:] = False
    sk = comps_touching(sk, G[i] | (cv2.dilate(G[i].astype(np.uint8), ell(8)) > 0), 4)
    nn, lab, st, _ = cv2.connectedComponentsWithStats(sk.astype(np.uint8))
    for k in range(1, nn):
        if st[k, 4] < 60:
            sk[lab == k] = False
    sk = cv2.morphologyEx(sk.astype(np.uint8), cv2.MORPH_CLOSE, ell(5)) > 0
    hand = cv2.dilate(sk.astype(np.uint8), ell(7)) > 0          # with her ink outline
    G[i] = G[i] | hand
    if i in L:
        L[i] = L[i] & ~hand
for d, S in (("_ghost", G), ("_live", L)):
    os.makedirs(stem + d, exist_ok=True)
    for f in glob.glob(stem + d + "/*.png"):
        os.remove(f)
    for i in range(n):
        m = S.get(i)
        if m is None:
            m = np.zeros((h, w), bool)
        elif d == "_ghost":
            m = cv2.dilate(m.astype(np.uint8), ell(3)) > 0
        cv2.imwrite(f"{stem}{d}/{i:05d}.png", (m * 255).astype(np.uint8))
    subprocess.run([FF, "-y", "-loglevel", "error", "-framerate", "24", "-i", f"{stem}{d}/%05d.png", "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-crf", "12", f"{stem}{d}/matte.mp4"], check=True)
print("wrote", stem + "_ghost", stem + "_live")
