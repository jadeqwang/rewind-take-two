#!/usr/bin/env python3
"""Singing Jade (v5): first frames from Jade's two reference PHOTOS (2026-10-16), photo pixels only. Nothing of her is
repainted, restyled or redrawn: the photo is matted (BiRefNet, wc_comp.matte), its edge colours are decontaminated
from the photo's own background (couch, wall, shoji screen, painting), and it is laid over the exact Bean plate in the
v4 geometry (2576x1449 crop of the 2752x1536 sheet, media/sing/first/crop.json).

    S1  = inputs/jade_ref_image2_music_video_pencils.png  (hair up, two pencils: pale-blue + pink erasers) over plate_close_1
    V3S = inputs/jade_ref_image_music_video_long_hair.png (long hair down)                               over plate_truth_1

    EPY=tools/engrave/.venv/bin/python; MPY=~/Documents/1-music-shipped/orbital-sunrise-video/video/out/.venv/bin/python
    WC_VER=v5S1  $EPY tools/sing/wc_comp.py matte inputs/jade_ref_image2_music_video_pencils.png   -> first/v5S1_her_alpha.png
    WC_VER=v5V3S $EPY tools/sing/wc_comp.py matte inputs/jade_ref_image_music_video_long_hair.png  -> first/v5V3S_her_alpha.png
    $MPY tools/sing/v5_first.py comp [S1|V3S ...]   -> first/v5_<SHOT>_first.jpg, v5_her_mask_first_frame_<SHOT>.png,
                                                       v5_<SHOT>_fig.jpg + v5_<SHOT>_alpha.png (sheet geometry, unchoked)
    $MPY tools/sing/v5_first.py sheet               -> review/v5_first_vs_v4.jpg (v4 and v5 first frames side by side)
    V5_REV=b $MPY tools/sing/v5_first.py comp V3S   -> first/v5b_V3S_first.jpg etc.: the shoulder retake (REV below)
    V5_REV=c $MPY tools/sing/v5_first.py comp S1    -> first/v5c_S1_first.jpg etc.: S1 from the re-tinted photo local_a
    WC_VER=v5dV3S $EPY tools/sing/wc_comp.py matte media/sing/outpaint/nbp_1_merged.png
    V5_REV=d $MPY tools/sing/v5_first.py comp V3S   -> first/v5d_V3S_first.jpg etc.: V3S from the outpainted photo

Geometry: v4's face (landmarks 10-152) is 471.6 crop px tall (32.5 % of the frame height) with the eye midpoint at crop
(1263, 541) (measured on first/v4_S1_first.jpg). Each photo is scaled so its face is K x that height, its eye midpoint
put at v4's x and at v4's y + DY. K and DY per shot are in SHOTS below, with the reason.

Where the figure reaches the photo's own border (the jacket: left, right, bottom), and the frame needs more of it, ONLY
the jacket edge is extended: the border column / row of the photo is carried outward (fabric colour, a little sleeve
shading), with a shoulder line continued from the photo's own silhouette and a plain rounded arm edge. No anatomy, face
or hair is invented. V3S: the 1420 MHz patch is cut by the photo's right edge; its missing part is taken from the same
patch in the pencils photo (her own jacket), mapped ellipse-to-ellipse onto the visible ring (PATCH below)."""
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mouth as MT  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIRST = os.path.join(ROOT, "media/sing/first")
CROP = json.load(open(os.path.join(FIRST, "crop.json")))["box"]        # [88, 43, 2664, 1492] in the 2752x1536 sheet
W, H = 2752, 1536
V4_FH, V4_EYE = 471.6, (1263.0, 540.8)                                  # crop px, v4_S1_first.jpg
PAD = 900                                                               # photo px of room for the jacket extension
TAPER = 22                                                              # photo px an unextended arm edge tapers in by the bottom
# V5_REV=b (Jade, 2026-10-16: "yes, do the shoulder retake"): V3S's frame-right sleeve, which v5 carried 45 px past the
# photo's edge as a straight vertical strip (it read as a cut-out, squared shoulder), becomes a natural arm outline
# instead: the shoulder line runs on past the edge at a shallow slope, rounds over the deltoid (always wide enough for the
# completed patch) and turns down into the upper arm with a slight taper toward the elbow, cylinder shading toward the silhouette and the photo's own fabric texture (arm_right). Her face and hair
# pixels are untouched. Outputs are written as v5b_* beside the v5 files.
# V5_REV=c (Jade, 2026-10-16: "local_a is good"): S1 from media/sing/tint/local_a.png, the pencils photo with the cheek/nose
# flush, lip pink and skin warmth moved to match the hair-down photo (bit-identical outside its skin and lip masks, same
# size and geometry). Matte and landmarks stay the original photo's, so placement and scale are exactly v5's: only her
# skin and lip pixels change. Outputs v5c_*.
# V5_REV=d (Jade: "the hair down photo has parts of shoulders missing ... can the model fill those in?"): V3S from
# media/sing/outpaint/nbp_1_merged.png (tools/sing/v5_outpaint.py): nano-banana-pro outpainted both shoulders and arms
# and the whole 1420 MHz patch; the couch upholstery that v5/v5b took for her shoulder is gone; every pixel the photo
# really shows is the photo's own. No extension, no patch transplant. Outputs v5d_*.
REV = os.environ.get("V5_REV", "")
OUTPAINT = dict(photo="media/sing/outpaint/nbp_1_merged.png", x0=523)     # the canvas and where the photo sits on it
PFX = "v5" + REV
ARM_D, ARM_T = 85.0, 38.0          # V5_REV=b: the arm's outward reach past the photo edge (photo px), its taper by the frame bottom
#                                    (her frame-left shoulder runs >= 560 px from the neck, the photo's right edge is 526 px
#                                    from it, so the shoulder plausibly continues ~60-90 px past it)
SHOTS = {
    # K: face height / v4's.  DY: eye midpoint below v4's (crop px).  EXT: how far the sleeve may run past the photo's
    # left / right border (photo px; 0 = no extension) before it turns down as a plain arm edge.
    "S1": dict(photo="media/sing/tint/local_a.png" if REV == "c" else "inputs/jade_ref_image2_music_video_pencils.png",
               geom="inputs/jade_ref_image2_music_video_pencils.png", plate="media/sing/plates/plate_close_1.jpg",
               K=float(os.environ.get("V5_K_S1", 1.24)), DY=float(os.environ.get("V5_DY_S1", 80)), EXT=(0, 0)),
    "V3S": dict(photo=OUTPAINT["photo"] if REV == "d" else "inputs/jade_ref_image_music_video_long_hair.png",
                plate="media/sing/plates/plate_truth_1.jpg", gap_dx=OUTPAINT["x0"] if REV == "d" else 0,
                K=float(os.environ.get("V5_K_V3S", 1.10)), DY=float(os.environ.get("V5_DY_V3S", 35)),
                EXT={"b": (0, -1), "d": (0, 0)}.get(REV, (0, 45))),   # -1 = the shaped arm (arm_right); d: nothing to extend
}


def rd(p):
    return np.asarray(Image.open(os.path.join(ROOT, p)).convert("RGB"), np.float32)


def face(a):
    L = MT.detect(a.astype(np.uint8), (0, 0, a.shape[1], a.shape[0]))[0]
    return L, float(np.linalg.norm(L[10] - L[152])), (L[33] + L[263]) / 2


def nconv(I, m, sigmas):
    num = np.zeros_like(I); den = np.zeros(I.shape[:2], np.float32)
    for s in sigmas:
        num += cv2.GaussianBlur(I * m[..., None], (0, 0), s) / s
        den += cv2.GaussianBlur(m, (0, 0), s) / s
    return num / (den[..., None] + 1e-6), den


def decontaminate(I, a):
    """Edge colours with the photo's own background taken out: F = (I - (1 - a) B) / a, B estimated from the
    background pixels nearby; where a is small, the colour from just inside her silhouette instead."""
    bgm = cv2.erode((a < 0.02).astype(np.uint8), np.ones((7, 7), np.uint8)).astype(np.float32)
    B, _ = nconv(I, bgm, (6, 16, 40))
    core = (a > 0.95).astype(np.float32)
    Fin, den = nconv(I, core, (1.5, 3, 6, 12))
    ac = a[..., None]
    Fd = np.clip((I - (1 - ac) * B) / np.maximum(ac, 0.2), 0, 255)
    w_in = np.clip((0.55 - a) / 0.45, 0, 1)[..., None] * (den[..., None] > 1e-3)
    F = np.where(ac >= 0.98, I, Fd * (1 - w_in) + Fin * w_in)
    return F.astype(np.float32)


def extend(F, a, ext_l, ext_r):
    """Pad the photo by PAD on the left, right and bottom; carry the jacket out where it touches the border.
    Sides: EXT > 0 = the sleeve continues EXT px past the border (the photo's last columns mirrored, softening with
    distance, a little sleeve shading), under a shoulder line continued from the photo's own silhouette, ending in a
    plain rounded arm edge. EXT = 0 = no new pixels: the arm edge is the photo border, its corner at the shoulder
    rounded off INSIDE the photo. Bottom: each column's own jacket colour from the last rows (orange left out, so no band
    ends are smeared), carried down, softened, a little darker with depth."""
    h, w = a.shape
    Fp = cv2.copyMakeBorder(F, 0, PAD, PAD, PAD, cv2.BORDER_REFLECT)
    ap = np.zeros((h + PAD, w + 2 * PAD), np.float32)
    ap[:h, PAD:PAD + w] = a
    yy = np.arange(h + PAD)[:, None].astype(np.float32)
    rng = np.random.default_rng(5)
    rounds = []
    for side, ext in (("l", ext_l), ("r", ext_r)):
        col = 1 if side == "l" else w - 2
        rows = np.flatnonzero(a[:, col] > 0.5)
        if not len(rows):
            continue
        rounds.append((side, rows[0]))
        if ext <= 0:                                  # 0: trim only (below); -1: the shaped arm (arm_right, after the patch)
            continue
        xs = np.arange(1, 70) if side == "l" else np.arange(w - 70, w - 1)
        tops = []
        for x in xs:
            r = np.flatnonzero(a[max(0, rows[0] - 250):, x] > 0.5)
            if len(r):
                tops.append((abs(x - col), max(0, rows[0] - 250) + r[0]))
        d_in, yt = np.array(tops, np.float32).T
        m = np.polyfit(d_in, yt, 1)[0] if len(tops) > 5 else 0.0      # dy per px going INWARD from the border
        m_out = max(-m, 0.25)                                           # going outward the shoulder only falls
        d = np.arange(1, PAD + 1, dtype=np.float32)[None]                # outward distance from the border column
        y_top = rows[0] + m_out * d + d ** 2 / 300.0
        msk = ((yy >= y_top) & (d <= ext)).astype(np.float32)
        shade = 1 - 0.24 * np.clip(d / max(ext, 1), 0, 1) ** 1.5         # the sleeve turns away from the light
        # each row's fabric colour at the border: the white fabric (lum > 170) of the last 40 columns (hair, the patch's
        # ring and text and their anti-aliased edges left out), smoothed down the sleeve
        edge = F[:, :40] if side == "l" else F[:, w - 40:]
        lum = edge.mean(2)
        cc = np.zeros((h, 3), np.float32)
        prev = np.array([235, 235, 232], np.float32)
        for y in range(h):
            ok = lum[y] > 170                                          # white fabric only
            cc[y] = prev = np.median(edge[y][ok], 0) if ok.sum() >= 4 else prev
        cc = cv2.GaussianBlur(cc[:, None], (0, 0), sigmaX=0.01, sigmaY=6)[:, 0]
        cc = np.vstack([cc, np.repeat(cc[-1:], PAD, 0)])
        noise = cv2.GaussianBlur(rng.normal(0, 1, (h + PAD, PAD)).astype(np.float32), (0, 0), 2) * 1.5
        sl = slice(PAD - 1, None, -1) if side == "l" else slice(PAD + w, PAD + w + PAD)
        Fp[:, sl] = cc[:, None] * shade[..., None] + noise[..., None]
        # hand over across the photo's last 6 columns (its border column is a shade darker)
        r6 = (np.arange(1, 7, dtype=np.float32) / 7)[None, :, None]
        last = slice(PAD + 5, PAD - 1, -1) if side == "l" else slice(PAD + w - 6, PAD + w)
        live = (a[:, :6][:, ::-1] if side == "l" else a[:, w - 6:]) > 0.9
        Fp[:h, last] = np.where(live[..., None], Fp[:h, last] * (1 - r6) + cc[:h, None] * r6, Fp[:h, last])
        ap[:, sl] = np.maximum(ap[:, sl], msk)
    # bottom
    base = Fp[h - 30:h - 1]
    hsv = cv2.cvtColor(np.clip(base, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
    orange = (hsv[..., 0] >= 5) & (hsv[..., 0] <= 22) & (hsv[..., 1] > 110)
    col_c = np.zeros((base.shape[1], 3), np.float32)
    for x in range(base.shape[1]):
        ok = ~orange[:, x]
        col_c[x] = np.median(base[ok, x], 0) if ok.sum() >= 3 else np.array([235, 235, 232], np.float32)
    col_c = cv2.GaussianBlur(col_c[None], (0, 0), sigmaX=2.5, sigmaY=0.01)[0]
    for k in range(PAD):
        sh = 1 - 0.08 * min(k / 120, 1)
        Fp[h + k] = col_c * sh
    Fp[h:] += cv2.GaussianBlur(rng.normal(0, 1, Fp[h:].shape[:2]).astype(np.float32), (0, 0), 1.5)[..., None] * 1.5
    r12 = (np.arange(1, 13, dtype=np.float32) / 13)[:, None, None]      # the photo's last 12 rows hand over to it
    Fp[h - 12:h] = Fp[h - 12:h] * (1 - r12) + Fp[h:h + 1] * r12
    ap[h:] = ap[h - 3][None]
    # sides without new pixels: round the shoulder corner where the figure meets the photo border (trim only: the
    # rounded silhouette is never larger than the photo's own)
    for side, r0 in rounds:
        if (side == "l" and ext_l) or (side == "r" and ext_r):
            continue
        xs = slice(PAD, PAD + 90) if side == "l" else slice(PAD + w - 90, PAD + w)
        ys = slice(max(0, r0 - 120), min(h + PAD, r0 + 220))
        win = (ap[ys, xs] > 0.5).astype(np.float32)
        big = cv2.copyMakeBorder(win, 40, 40, 40, 40, cv2.BORDER_REPLICATE)
        if side == "l":
            big[:, :40] = 0                      # outside the photo there is nothing
        else:
            big[:, -40:] = 0
        rnd = np.clip((cv2.GaussianBlur(big, (0, 0), 14)[40:-40, 40:-40] - 0.5) * 6 + 0.5, 0, 1)
        ap[ys, xs] = np.minimum(ap[ys, xs], np.where(win > 0, rnd, 1.0))
        # below the shoulder the arm edge tapers in a little toward the elbow instead of running down the photo
        # border as a ruler line (trim only; TAPER photo px by the photo's bottom row). Not where the figure meets the
        # border only near the bottom (S1's left forearm): there is no arm edge to shape.
        if r0 + 60 > h - 150:
            continue
        yv = np.arange(h + PAD, dtype=np.float32)
        t = np.clip((yv - (r0 + 60)) / (h - (r0 + 60)), 0, 1)
        cut = (TAPER * t * t * (3 - 2 * t))[:, None]                       # px trimmed at each row
        cols = np.arange(ap.shape[1], dtype=np.float32)[None]
        inward = cols - PAD if side == "l" else (PAD + w - 1) - cols       # distance inside the photo border
        ap *= np.where(inward > -1, np.clip(inward - cut + 0.5, 0, 1), 1.0)
    # rounded outer edge for the extended sleeves (only the new part is trimmed)
    for side, ext in (("l", ext_l), ("r", ext_r)):
        if ext <= 0 or ext >= PAD:
            continue
        xs = slice(PAD - ext - 30, PAD) if side == "l" else slice(PAD + w, PAD + w + ext + 30)
        win = (ap[:, xs] > 0.5).astype(np.float32)
        big = np.hstack([np.zeros_like(win[:, :1]).repeat(20, 1), win]) if side == "l" else np.hstack([win, np.zeros_like(win[:, :1]).repeat(20, 1)])
        rnd = np.clip((cv2.GaussianBlur(big, (0, 0), 8) - 0.5) * 4 + 0.5, 0, 1)
        rnd = rnd[:, 20:] if side == "l" else rnd[:, :-20]
        inner = 12                                   # next to the photo the silhouette stays as it is
        if side == "l":
            rnd[:, -inner:] = win[:, -inner:]
        else:
            rnd[:, :inner] = win[:, :inner]
        ap[:, xs] = np.minimum(ap[:, xs], np.where(win > 0, rnd, 0))
        ap[:, xs] = cv2.GaussianBlur(ap[:, xs], (0, 0), 1.0)
    ap = np.clip(ap, 0, 1)
    return np.clip(Fp, 0, 255), ap


# V3S: the 1420 MHz patch is cut by the photo's right border. The same patch is whole in the pencils photo (seen at an
# angle). The ellipses below were fitted to the two black rings (outer contour; the V3S one from its visible arc only);
# the map pencils -> V3S is ellipse-to-ellipse with the turn searched for the best match on the visible part, then a
# free affine refined on it (NCC 0.82). Only the part past the border (with 8 px of hand-over) is taken from it.
PATCH = dict(src="inputs/jade_ref_image2_music_video_pencils.png", ring_box=(1130, 850, 1280, 1050),
             ell_src=((1198.0, 957.3), (74.2, 151.5), 158.6), ell_dst=((1054.6, 1318.1), (122.8, 161.3), 177.3),
             fit_box=(960, 1200, 1084, 1440), border=1086, handover=8,
             # a refined fit from an earlier run of the same search (NCC 0.82; checked by eye: ring, '0' and 'z' line up);
             # Powell is start-sensitive here, so patch_fit refines from both and keeps the better
             seed=[[0.703687, 0.220967, 169.146933], [-0.117538, 0.882614, -88.089051]])


def _ell(c, ax, ang):
    t = np.radians(ang)
    M = np.eye(3)
    M[:2, :2] = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]]) @ np.diag([ax[0] / 2, ax[1] / 2])
    M[:2, 2] = c
    return M


def patch_fit():
    """-> first/v5_patch_V3S.json: the affine map V3S photo px -> pencils photo px."""
    from scipy.optimize import minimize
    gP = cv2.cvtColor(rd(PATCH["src"]), cv2.COLOR_RGB2GRAY)
    gV = cv2.cvtColor(rd(SHOTS["V3S"]["photo"]), cv2.COLOR_RGB2GRAY)
    Ep, Ev = _ell(*PATCH["ell_src"]), _ell(*PATCH["ell_dst"])
    x0, y0, x1, y1 = PATCH["fit_box"]
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    iv = np.linalg.inv(Ev)
    u, v = iv[0, 0] * xx + iv[0, 1] * yy + iv[0, 2], iv[1, 0] * xx + iv[1, 1] * yy + iv[1, 2]
    vis = (u * u + v * v) < 1.15 ** 2
    tm, tmb = gV[y0:y1, x0:x1][vis], cv2.GaussianBlur(gV[y0:y1, x0:x1], (0, 0), 1)[vis]

    def score(A, blur=False):        # the turn search on the raw grey, the refinement on a 1 px blur of both
        mx, my = A[0, 0] * xx + A[0, 1] * yy + A[0, 2], A[1, 0] * xx + A[1, 1] * yy + A[1, 2]
        smp = cv2.remap(gP, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR)
        return np.corrcoef(cv2.GaussianBlur(smp, (0, 0), 1)[vis], tmb)[0, 1] if blur else np.corrcoef(smp[vis], tm)[0, 1]
    best = (-2, None)
    for th in np.arange(-180, 180, 1.0):
        t = np.radians(th)
        R = np.eye(3)
        R[:2, :2] = [[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]]
        A = Ep @ np.linalg.inv(R) @ iv
        r = score(A)
        if r > best[0]:
            best = (r, A)
    sc = np.array([[1e-2, 1e-2, 1], [1e-2, 1e-2, 1]])
    seed = np.vstack([np.array(PATCH["seed"]), [0, 0, 1]])
    res = []
    for A0 in (best[1], seed):
        def f(p, A0=A0):
            A = A0.copy()
            A[:2] += p.reshape(2, 3) * sc
            return -score(A, True)
        r = minimize(f, np.zeros(6), method="Powell", options=dict(maxiter=4000, xtol=1e-3, ftol=1e-6))
        A = A0.copy()
        A[:2] += r.x.reshape(2, 3) * sc
        res.append((-r.fun, A))
    r_best, A = max(res, key=lambda t: t[0])
    r = type("R", (), {"fun": -r_best})
    json.dump({"A_v3s_to_pencils": A.tolist(), "ncc_turn_search": round(float(best[0]), 3), "ncc": round(float(-r.fun), 3)},
              open(os.path.join(FIRST, "v5_patch_V3S.json"), "w"), indent=1)
    print("patch fit ncc", round(float(best[0]), 3), "->", round(float(-r.fun), 3), A.round(4).tolist())


def patch_fix(Fp, ap, shot, gain_ref):
    """V3S only: complete the 1420 MHz patch past the photo's right border (PATCH, patch_fit)."""
    js = os.path.join(FIRST, "v5_patch_V3S.json")
    if shot != "V3S" or REV == "d":                                   # d: the model completed the patch itself
        return Fp, ap
    if not os.path.exists(js):
        patch_fit()
    A = np.array(json.load(open(js))["A_v3s_to_pencils"])
    from scipy import ndimage as ndi
    P = rd(PATCH["src"])
    bx0, by0, bx1, by1 = PATCH["ring_box"]
    dark = cv2.cvtColor(P[by0:by1, bx0:bx1], cv2.COLOR_RGB2GRAY) < 70
    lab, n = ndi.label(dark)
    ring = lab == (np.argmax(ndi.sum(dark, lab, range(1, n + 1))) + 1)
    disc = np.zeros(P.shape[:2], np.float32)
    disc[by0:by1, bx0:bx1] = ndi.binary_dilation(ndi.binary_fill_holes(ring), iterations=2)
    disc = cv2.GaussianBlur(disc, (0, 0), 1.0)
    y0, y1, x0, x1 = 1150, 1448, 900, 1300                           # V3S photo px around the patch
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    mx, my = (A[0, 0] * xx + A[0, 1] * yy + A[0, 2]).astype(np.float32), (A[1, 0] * xx + A[1, 1] * yy + A[1, 2]).astype(np.float32)
    Pw = cv2.remap(P, mx, my, cv2.INTER_LANCZOS4)
    Dw = cv2.remap(disc, mx, my, cv2.INTER_LINEAR)
    # colour: match the white of the visible half of the patch
    G = gain_ref[y0:y1, x0:min(x1, PATCH["border"] - 4)]
    sel = (Dw[:, :G.shape[1]] > 0.9) & (G.mean(2) > 150) & (Pw[:, :G.shape[1]].mean(2) > 120)
    gain = np.median(G[sel], 0) / np.maximum(np.median(Pw[:, :G.shape[1]][sel], 0), 1)
    Pw = np.clip(Pw * gain, 0, 255)
    ramp = np.clip((xx - (PATCH["border"] - PATCH["handover"])) / PATCH["handover"], 0, 1)
    k = (Dw * ramp)[..., None]
    sl = (slice(y0, y1), slice(x0 + PAD, x1 + PAD))
    Fp[sl] = Fp[sl] * (1 - k) + Pw * k
    ap[sl] = np.maximum(ap[sl], Dw * (xx >= PATCH["border"] - 2))
    print("patch gain", np.round(gain, 3))
    return Fp, ap


def arm_right(Fp, ap, F, a, bottom):
    """V5_REV=b, V3S: the frame-right arm past the photo's right edge as a natural outline (see REV). Runs after
    patch_fix, so the completed patch's reach on each row is known and the arm is always wide enough for it."""
    h, w = a.shape
    y0 = int(np.flatnonzero(a[:, w - 2] > 0.5)[0])                    # where the shoulder meets the photo edge
    H2, W2 = ap.shape
    yv = np.arange(H2, dtype=np.float32)
    b0 = PAD + w                                                       # first column past the photo
    beyond = ap[:, b0:b0 + 200] > 0.5                                  # so far only the patch disc is there
    reach = np.where(beyond.any(1), 200 - np.argmax(beyond[:, ::-1], 1), 0).astype(np.float32)
    # the shoulder line leaves the photo edge at a shallow slope (as the photo's own shoulder runs into it), rounds over
    # the deltoid and turns down into the upper arm, which narrows a little toward the elbow
    off = ARM_D * (1 - np.exp(-np.clip(yv - y0, 0, None) / (0.35 * ARM_D)))
    u = np.clip((yv - (y0 + 120)) / max(bottom - (y0 + 120), 1), 0, 1)
    off -= ARM_T * u ** 1.3                                            # the upper arm narrows toward the elbow
    off = np.maximum(off, np.where(reach > 0, reach + 6, -1e3))
    off = cv2.GaussianBlur(off[:, None], (0, 0), sigmaX=0.01, sigmaY=12)[:, 0]
    d = np.arange(W2, dtype=np.float32)[None] - (b0 - 1)               # > 0 past the photo edge, <= 0 inside it
    rows = yv >= y0
    al = np.clip(off[:, None] - d + 0.5, 0, 1)                         # the outline, 1 px anti-aliased
    ap[rows] = np.where((d > 0)[0][None], al[rows], ap[rows])          # past the edge: the arm; inside: the photo's own matte
    ap[:] = cv2.GaussianBlur(ap, (0, 0), 0.8) * (d > 0) + ap * (d <= 0)
    # colour past the edge: each row's white fabric (as in extend), smooth, with soft low-frequency folds (the photo's
    # own texture mirrored outward made a visible butterfly pattern), handed over from the photo's last 10 columns
    edge = F[:, w - 40:]
    lum = edge.mean(2)
    cc = np.zeros((h, 3), np.float32)
    prev = np.array([235, 235, 232], np.float32)
    for y in range(h):
        ok = lum[y] > 170
        cc[y] = prev = np.median(edge[y][ok], 0) if ok.sum() >= 4 else prev
    cc = cv2.GaussianBlur(cc[:, None], (0, 0), sigmaX=0.01, sigmaY=6)[:, 0]
    cc = np.vstack([cc, np.repeat(cc[-1:], PAD, 0)])
    disc = beyond.astype(np.float32)
    n = int(ARM_D) + 40
    rng = np.random.default_rng(11)
    folds = cv2.GaussianBlur(rng.normal(0, 1, (H2, n)).astype(np.float32), (0, 0), sigmaX=5, sigmaY=14) * 40
    fab = cc[:, None] * np.ones((1, n, 1), np.float32) + folds[..., None] + \
        cv2.GaussianBlur(rng.normal(0, 1, (H2, n)).astype(np.float32), (0, 0), 0.8)[..., None] * 1.2
    sl = slice(b0, b0 + n)
    k = cv2.GaussianBlur(disc[:, :n], (0, 0), 1.0)[..., None]          # the patch stays the patch
    Fp[:, sl] = Fp[:, sl] * k + fab * (1 - k)
    r10 = (np.arange(1, 11, dtype=np.float32) / 11)[None, :, None]
    last = slice(b0 - 10, b0)
    hand = (rows[:, None] & (disc[:, :1] < 0.5) & (np.arange(H2)[:, None] < h))[..., None]
    Fp[:, last] = np.where(hand, Fp[:, last] * (1 - r10) + fab[:, :1] * r10, Fp[:, last])
    sh = np.clip((d + 40) / (off[:, None] + 40), 0, 1)                 # cylinder: darker toward the silhouette
    shade = np.where(rows[:, None] & (d > -40), 1 - 0.26 * sh ** 2.2, 1.0)
    Fp *= shade[..., None]
    return Fp, ap


def key_gaps(shot, I, a):
    """V3S: the blue painting behind her crown shows between the hair strands at high matte (BiRefNet calls it hair).
    Blue is never her hair's colour, so inside the crown box the matte drops with blueness (the plate shows through
    those gaps instead)."""
    if shot != "V3S":
        return a
    dx = SHOTS[shot].get("gap_dx", 0)                                  # the outpaint canvas puts the photo at x = dx
    x0, y0, x1, y1 = 330 + dx, 110, 560 + dx, 270
    R, G, B = (I[y0:y1, x0:x1, c] for c in range(3))
    k = np.clip(1 - (B - R - 6) / 24, 0, 1)
    a = a.copy()
    a[y0:y1, x0:x1] *= cv2.GaussianBlur(k.astype(np.float32), (0, 0), 0.7)
    return a


def place(shot):
    S = SHOTS[shot]
    I = rd(S["photo"])
    a = np.asarray(Image.open(os.path.join(FIRST, f"v5{'d' if REV == 'd' and shot == 'V3S' else ''}{shot}_her_alpha.png")),
                   np.float32) / 255
    _, fh, eye = face(rd(S.get("geom", S["photo"])))                   # placement from the original photo's landmarks
    if S.get("gap_dx"):                                                # d: measured on the photo itself (the detector reads the
        _, fh, eye = face(rd("inputs/jade_ref_image_music_video_long_hair.png"))   # face 2 % bigger on the wide canvas),
        eye = eye + np.array([S["gap_dx"], 0])                         # then moved to where the photo sits on the canvas
    a = key_gaps(shot, I, a)
    F = decontaminate(I, a)
    Fp, ap = extend(F, a, *S["EXT"])
    Fp, ap = patch_fix(Fp, ap, shot, I)
    if S["EXT"][1] < 0:
        bottom = (CROP[3] - (V4_EYE[1] + S["DY"] + CROP[1] - S["K"] * V4_FH / fh * eye[1])) / (S["K"] * V4_FH / fh)
        Fp, ap = arm_right(Fp, ap, F, a, bottom)
    s = S["K"] * V4_FH / fh
    ex, ey = V4_EYE[0] + CROP[0], V4_EYE[1] + S["DY"] + CROP[1]          # sheet px
    tx, ty = ex - s * (eye[0] + PAD), ey - s * eye[1]
    M = np.float32([[s, 0, tx], [0, s, ty]])
    fig = cv2.warpAffine(Fp, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
    al = np.clip(cv2.warpAffine(ap, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0), 0, 1)
    # where the photo itself ends inside the sheet (below the bottom extension there is nothing): keep alpha as warped
    meta = dict(shot=shot, photo=S["photo"], scale=round(s, 5), K=S["K"], DY=S["DY"], face_h_photo=round(fh, 1),
                eye_photo=[round(float(v), 1) for v in eye], tx=round(float(tx), 1), ty=round(float(ty), 1),
                photo_box_sheet=[round(float(tx + s * PAD), 1), round(float(ty), 1),
                                 round(float(tx + s * (PAD + I.shape[1])), 1), round(float(ty + s * I.shape[0]), 1)])
    return fig, al, meta


def comp(shots):
    x0, y0, x1, y1 = CROP
    for shot in shots:
        fig, al, meta = place(shot)
        Image.fromarray(np.clip(fig, 0, 255).astype(np.uint8)).save(os.path.join(FIRST, f"{PFX}_{shot}_fig.jpg"), quality=96)
        Image.fromarray((al * 255).astype(np.uint8)).save(os.path.join(FIRST, f"{PFX}_{shot}_alpha.png"))
        ac = np.clip((cv2.GaussianBlur(al, (0, 0), 1.0) - 0.08) / 0.84, 0, 1)   # v4's light choke (wc_comp.comp)
        P = rd(SHOTS[shot]["plate"])
        C = fig * ac[..., None] + P * (1 - ac[..., None])
        out = os.path.join(FIRST, f"{PFX}_{shot}_first.jpg")
        Image.fromarray(np.clip(C, 0, 255).astype(np.uint8)[y0:y1, x0:x1]).save(out, quality=96)
        m = ac[y0:y1, x0:x1]
        Image.fromarray((m * 255).astype(np.uint8)).save(os.path.join(FIRST, f"{PFX}_her_mask_first_frame_{shot}.png"))
        _, fh, eye = face(np.asarray(Image.open(out).convert("RGB"), np.float32))
        row = np.flatnonzero(m[-3] > 0.5)
        meta.update(first_face_h=round(fh, 1), first_face_frac=round(fh / (y1 - y0), 3),
                    first_eye=[round(float(v), 1) for v in eye], eye_1080=[round(float(v) * 1080 / (y1 - y0), 1) for v in eye],
                    bottom_row_span=[int(row[0]), int(row[-1])] if len(row) else None)
        json.dump(meta, open(os.path.join(FIRST, f"{PFX}_{shot}_first.json"), "w"), indent=1)
        print(os.path.relpath(out, ROOT), json.dumps(meta))


def sheet():
    tiles = []
    for v in ("v4_S1", "v5_S1", "v4_V3S", "v5_V3S"):
        im = Image.open(os.path.join(FIRST, f"{v}_first.jpg")).resize((960, 540), Image.LANCZOS)
        cv = cv2.putText(np.array(im), v.replace("_", " "), (16, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                         (255, 220, 0), 3)
        tiles.append(cv)
    g = np.vstack([np.hstack(tiles[:2]), np.hstack(tiles[2:])])
    out = os.path.join(ROOT, "media/sing/review/v5_first_vs_v4.jpg")
    Image.fromarray(g).save(out, quality=92)
    print(os.path.relpath(out, ROOT))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "comp":
        comp(sys.argv[2:] or list(SHOTS))
    elif cmd == "sheet":
        sheet()
