#!/usr/bin/env python
"""C4: put the crossed pencils THROUGH a hair bun (v7, Jade 0:11, second round).

Take 4 (kf_v3_b edit) draws the two pencils as a big X lying on the back of her head, crossing at ~(318, 161) at
1080p, with no bun round them; the long lower legs reach her neck (pink-eraser pencil A) and the headrest
(blue-eraser pencil B). Canon (C1, D3, D6, P2): a dark bun with the two pencils pushed through it, erasers out one
side, short points out the other, the middles hidden. This is a pixel pass on the engraved take, no generative model:

  1. BUN: the round bun of C4 take 2 (same keyframe family, same framing and drawing; frame 0, engraved), cut out
     along its own ink outline (dark pixels inside a hand polygon, closed; the bits of take 2's own pencil inside
     it inpainted dark), registered onto take 4 by an affine ECC fit on her head/face/ear (cc 0.96), plus BUN_SHIFT.
     It covers the crossing and the middle third of both pencils.
  2. TRACK: her head is followed by a rigid (Euclidean) ECC fit per frame on the pencil rods, always against frame 0
     (no drift); the bun, the new points and the fill holes ride that one warp, so nothing swims against the hair.
  3. SHORT POINTS: each pencil now ends POINT_OUT px past where it leaves the bun: the old lower leg beyond that is
     removed, and the sharpened end (cone + point) is resampled from the frame's own pixels and slid up the axis.
  4. FILL where the old lower legs were (same rule every frame, from that frame's own pixels or a fixed plate):
     - B (over the seat gap and the headrest's curved stripes): each half of the strip copies the frame straight
       above / below it (vertical shift, the stripes run near-vertical there, so they continue across the strip);
     - A (over hanging hair strands and the neck under the ear): take 2's frame 0 at the same place on her head
       (registered + tracked like the bun), which has hair and neck there and no pencil.
  5. Layers, back to front: the filled frame, the pencils (their kept parts and the new points), the bun.

  tools/engrave/.venv/bin/python tools/c4_bun.py [--frames N] [--out PATH]
"""
import argparse
import os
import subprocess
import sys

import av
import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from blue_eraser import encode, frames_of  # noqa: E402
from c4_pencils import ROD, HW, coords, silhouette, unit_n, warp_pt, warp_dir  # noqa: E402

SRC = "media/shots/C4/take_4_engraved.mp4"
RAW = "media/shots/C4/take_4.mp4"
MATTE = "media/shots/C4/take_4_matte"
BUN_SRC = "media/shots/C4/take_2_engraved.mp4"   # frame 0
OUT = "media/shots/C4/take_4_engraved_bun.mp4"
ROI = (150, 0, 520, 400)
# take 2 bun outline (take 2 frame 0 px): the round knot at the back of her head, take 2's pencil entry included
# (the pencil pixels themselves are dark-thresholded out and inpainted)
BUN_POLY = [(276, 100), (285, 88), (300, 80), (320, 76), (338, 84), (352, 98), (372, 110), (385, 140), (380, 180),
            (360, 205), (330, 212), (300, 205), (282, 190), (274, 150)]
BUN_SHIFT = (0.0, 0.0)   # extra shift of the bun on take 4 (px), after registration (35 px lower was tried: its edge
                         # showed inside her hair and take 4's own small bun showed above it)
POINT_OUT = 62.0         # visible length past the bun's edge: ~9 px of body + the 53 px cone
FAR_SEAM = 99.0          # raw px from the axis where the headrest-side copy hands over to the mirrored far side (99: never)


def first_frame(path):
    c = av.open(path)
    for f in c.decode(video=0):
        return f.to_ndarray(format="rgb24")


def register(a, b, box=(360, 140, 640, 420)):
    """affine warp mapping take-4 px -> take-2 px, fitted on her head/face/ear."""
    x0, y0, x1, y1 = box
    g = lambda im: cv2.GaussianBlur(cv2.cvtColor(im, cv2.COLOR_RGB2GRAY), (0, 0), 1.5).astype(np.float32)  # noqa: E731
    W = np.eye(2, 3, dtype=np.float32)
    cc, W = cv2.findTransformECC(g(a)[y0:y1, x0:x1], g(b)[y0:y1, x0:x1], W, cv2.MOTION_AFFINE,
                                 (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 300, 1e-6), None, 5)
    Wf = W.astype(np.float64)
    Wf[:, 2] += np.array([x0, y0]) - Wf[:, :2] @ np.array([x0, y0])
    return Wf, cc


def bun_patch(b):
    P = np.zeros(b.shape[:2], np.uint8)
    cv2.fillPoly(P, [np.array(BUN_POLY, np.int32)], 1)
    L = cv2.cvtColor(b, cv2.COLOR_RGB2GRAY)
    dark = ((L < 110) & (P > 0)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(dark, connectivity=8)
    dark = (lab == 1 + np.argmax(st[1:, 4])).astype(np.uint8)
    solid = cv2.morphologyEx(dark, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    cs, _ = cv2.findContours(solid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    solid = np.zeros_like(solid)
    cv2.drawContours(solid, cs, -1, 1, -1)
    holes = ((solid > 0) & (dark == 0)).astype(np.uint8) * 255
    return cv2.inpaint(b, holes, 5, cv2.INPAINT_TELEA), solid.astype(np.float32)


def vshift(img, bad, tv, d, steps=4, scale=1.0):
    """Vertical-shift fill: each half of a diagonal strip copies the frame straight above it (the half nearer the
    top, tv < 0) or straight below it, one strip height away, stepping further while the source is on a pencil."""
    dyv = int(np.ceil(scale * (2 * (HW + 4)) / abs(d[0]))) + 2
    res = []
    for sign in (1, -1):                       # +1: from above (pixel y <- y - dy); -1: from below
        val = np.zeros(bad.shape, bool)
        acc = np.zeros_like(img)
        for k in range(1, steps + 1):
            sh = sign * k * dyv
            ok = ~np.roll(bad, sh, axis=0) & ~val
            if sign > 0:
                ok[:sh] = False
            else:
                ok[sh:] = False
            acc[ok] = np.roll(img, sh, axis=0)[ok]
            val |= ok
        res.append((acc, val))
    (au, vu), (ad, vd) = res
    w = np.clip(0.5 - tv / 3.0, 0, 1)                   # 1 on the top half, 0 on the bottom half, 3 px seam
    if not (vu | vd).all():
        print(f"vshift: {(~(vu | vd)).sum()} px without a clean source")
    w = np.where(vu & ~vd, 1.0, np.where(vd & ~vu, 0.0, w))[..., None]
    return au * w + ad * (1 - w)


def harmonic(plate, frame, hole):
    """plate with the frame's low frequencies: the difference frame - plate, known outside `hole`, is filled
    smoothly into it (Navier-Stokes inpaint) and added, so the patch meets the frame's tone at its edge."""
    diff = np.clip(frame - plate + 128, 0, 255).astype(np.uint8)
    hm = cv2.dilate(hole.astype(np.uint8), np.ones((3, 3), np.uint8)) * 255
    dd = cv2.inpaint(diff, hm, 9, cv2.INPAINT_NS).astype(np.float32)
    dd = cv2.GaussianBlur(dd, (0, 0), 4.0)
    return plate + dd - 128


def compose(A, B):
    """3x3 compose of 2x3 affines: A after B."""
    return (np.vstack([A, [0, 0, 1]]) @ np.vstack([B, [0, 0, 1]]))[:2]


def hole_mask(r, xx, yy, cone0):
    """the old lower leg from the new cone's start to past the old point, wide enough for its ink outline (the cone's
    outline is kept at >= 6 px half-width to the point, 4 px past it)."""
    s, t = coords(xx, yy, r["p"], r["d"])
    lim = np.where(s < r["cone"], HW, np.maximum(HW * (r["tip"] - s) / (r["tip"] - r["cone"]), 6.0)) + 2.5
    return (np.abs(t) <= lim) & (s >= cone0 - 2) & (s <= r["tip"] + 4)


def track(fr, m0, roi_box):
    x0, y0, x1, y1 = roi_box
    g0 = cv2.GaussianBlur(cv2.cvtColor(fr[0][y0:y1, x0:x1], cv2.COLOR_RGB2GRAY), (0, 0), 1.0).astype(np.float32)
    crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-5)
    W = np.eye(2, 3, dtype=np.float32)
    out = []
    for i, f in enumerate(fr):
        if i:
            gi = cv2.GaussianBlur(cv2.cvtColor(f[y0:y1, x0:x1], cv2.COLOR_RGB2GRAY), (0, 0), 1.0).astype(np.float32)
            try:   # always against frame 0 (no drift), started from the previous frame's warp
                _, W = cv2.findTransformECC(g0, gi, W.copy(), cv2.MOTION_EUCLIDEAN, crit,
                                            cv2.dilate(m0, np.ones((9, 9), np.uint8)), 5)
            except cv2.error:
                pass
        Wf = W.astype(np.float64).copy()                 # frame-0 px -> frame-i px (full-frame coords)
        Wf[:, 2] += np.array([x0, y0]) - Wf[:, :2] @ np.array([x0, y0])
        out.append(Wf)
    return out


def reengrave_B(Ws, tip_new, n, tmp):
    """B's old lower leg lay along the headrest's edge, whose engraved hatching changes with every streetlight
    sweep, so no copy from the engraved frame holds up. The raw take's headrest is steady (camera locked to the
    car): the leg is removed in the RAW take instead (a clean plate of the static background, made once from raw
    frame 0 by shift-map, tone-matched per frame), the colour matte loses it, and tools/engrave re-engraves the
    take (deterministic: elsewhere identical to the shipped take up to encode noise). Returns the re-engraved
    frames and the per-frame 1080p hole masks."""
    raw, fps = frames_of(os.path.join(ROOT, RAW))
    raw = raw[:n]
    k = raw[0].shape[1] / 1920.0
    rx0, ry0, rx1, ry1 = [int(v * k) for v in ROI]
    vv, uu = np.mgrid[ry0:ry1, rx0:rx1].astype(np.float32)
    X1, Y1 = uu / k, vv / k                                   # raw ROI px in 1080p coords
    yy, xx = np.mgrid[0:1080, 0:1920].astype(np.float32)
    holes_raw, holes_hd, pencil_hd = [], [], []
    r0 = ROD["B"]
    cone0 = tip_new["B"] - (r0["tip"] - r0["cone"])
    for Wf in Ws:
        r = dict(r0, p=warp_pt(Wf, r0["p"]), d=warp_dir(Wf, r0["d"]))
        holes_raw.append(hole_mask(r, X1, Y1, cone0))
        hd = np.zeros((1080, 1920), bool)
        y0, y1, x0, x1 = ROI[1], ROI[3], ROI[0], ROI[2]
        hd[y0:y1, x0:x1] = hole_mask(r, xx[y0:y1, x0:x1], yy[y0:y1, x0:x1], cone0)
        holes_hd.append(hd)
        ph = np.zeros((1080, 1920), bool)
        sB, tB_ = coords(xx[y0:y1, x0:x1], yy[y0:y1, x0:x1], r["p"], r["d"])
        ph[y0:y1, x0:x1] = silhouette(sB, tB_, r["top"], r["cone"], r["tip"], HW + 3) > 0
        pencil_hd.append(ph)
    U = np.zeros_like(holes_raw[0])
    for h in holes_raw:
        U |= h
    U = cv2.dilate(U.astype(np.uint8), np.ones((5, 5), np.uint8))
    # the clean plate: raw frame 0 over the union of the holes, by a vertical-shift copy (the headrest's stripes run
    # near-vertical there, and the seat-gap bars on the far side run parallel to the pencil, so neither is broken):
    # the half of the strip nearer the headrest copies from straight above, the other half from straight below,
    # stepping further while the source is on a pencil
    crop = np.ascontiguousarray(raw[0][ry0:ry1, rx0:rx1]).astype(np.float32)
    bad = np.zeros(U.shape, bool)
    for rr in ROD.values():
        s_, t_ = coords(X1, Y1, rr["p"], rr["d"])
        bad |= silhouette(s_, t_, rr["top"], rr["cone"], rr["tip"], HW + 5) > 0
    bad |= U > 0
    _, tB = coords(X1, Y1, r0["p"], r0["d"])
    tv = tB * np.sign(unit_n(r0["d"])[1])              # < 0: the half nearer the top of the frame (the headrest)
    up = vshift(crop, bad, np.full_like(tv, -10.0), r0["d"], steps=6, scale=k)
    # the far half (the white strip and the seat-gap bars, parallel to the pencil): mirrored across the strip's
    # far edge, so the parallel bars stay parallel
    ys_, xs_ = np.nonzero(U)
    hw = (cv2.distanceTransform((U > 0).astype(np.uint8), cv2.DIST_L2, 5))
    nrm = unit_n(r0["d"]) * np.sign(unit_n(r0["d"])[1])  # unit normal pointing to the far (lower) side
    # distance of each hole px to the far edge, along the normal: march until outside U
    far = np.zeros_like(crop)
    for y_, x_ in zip(ys_, xs_):
        d_ = 0.0
        while d_ < 60:
            qx, qy = int(round(x_ + nrm[0] * d_)), int(round(y_ + nrm[1] * d_))
            if not (0 <= qy < U.shape[0] and 0 <= qx < U.shape[1]) or not U[qy, qx]:
                break
            d_ += 0.5
        qx, qy = x_ + nrm[0] * (2 * d_ + 1), y_ + nrm[1] * (2 * d_ + 1)
        far[y_, x_] = cv2.getRectSubPix(crop, (1, 1), (float(qx), float(qy)))[0, 0]
    del hw
    w = np.clip(0.5 - (tv - FAR_SEAM) / 2.0, 0, 1)[..., None]
    plate = np.where((U > 0)[..., None], up * w + far * (1 - w), crop)
    cv2.imwrite(os.path.join(tmp, "B_raw_plate.png"), cv2.cvtColor(plate.astype(np.uint8), cv2.COLOR_RGB2BGR))
    mdir = os.path.join(tmp, "B_matte")
    os.makedirs(mdir, exist_ok=True)
    src = os.path.join(ROOT, MATTE)
    rawfix = []
    for i in range(n):
        f = raw[i].copy()
        h = cv2.dilate(holes_raw[i].astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        c = f[ry0:ry1, rx0:rx1].astype(np.float32)
        fill = harmonic(plate, c, h)
        al = cv2.GaussianBlur(h.astype(np.float32), (0, 0), 0.8)[..., None]
        f[ry0:ry1, rx0:rx1] = np.clip(c * (1 - al) + fill * al + 0.5, 0, 255).astype(np.uint8)
        rawfix.append(f)
        # the matte there: what the background round the pencil has in this frame (the matte flickers on and off
        # the headrest from frame to frame; the re-engraved strip must do the same as its neighbours)
        m = cv2.imread(os.path.join(src, f"{i:05d}.png"), 0)
        hh = cv2.dilate(holes_hd[i].astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
        unk = (cv2.dilate(pencil_hd[i].astype(np.uint8), np.ones((9, 9), np.uint8)) > 0).astype(np.uint8) * 255
        mi = cv2.inpaint(m, unk, 7, cv2.INPAINT_TELEA)
        m[hh] = mi[hh]
        cv2.imwrite(os.path.join(mdir, f"{i:05d}.png"), m)
    rawp = os.path.join(tmp, "B_raw.mp4")
    encode(rawfix, fps, rawp, 8)
    rep = os.path.join(tmp, "B_re.mp4")
    subprocess.run([sys.executable, os.path.join(ROOT, "tools/engrave/engrave.py"), rawp, rep, "--out-height", "1080",
                    "--matte-in", os.path.join(mdir, "%05d.png"), "--crf", "12"], check=True, stdout=subprocess.DEVNULL)
    re, _ = frames_of(rep)
    return re, holes_hd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", type=int, default=0)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--tmp", default="/tmp", help="scratch dir for the B re-engrave (raw video, matte, re-run)")
    a = ap.parse_args()
    fr, fps = frames_of(os.path.join(ROOT, SRC))
    if a.frames:
        fr = fr[:a.frames]
    b0 = first_frame(os.path.join(ROOT, BUN_SRC))
    Reg, cc = register(fr[0], b0)                       # take-4 frame-0 px -> take-2 px
    Reg[:, 2] -= Reg[:, :2] @ np.asarray(BUN_SHIFT)     # the bun lands BUN_SHIFT further on take 4
    patch, pmask = bun_patch(b0)
    x0, y0, x1, y1 = ROI
    H, Wd = y1 - y0, x1 - x0
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    inv = cv2.invertAffineTransform(Reg.astype(np.float32))       # take-2 px -> take-4 px
    m4 = cv2.warpAffine(pmask, inv, (fr[0].shape[1], fr[0].shape[0]), flags=cv2.INTER_LINEAR) > 0.5
    tip_new = {}
    for k, r in ROD.items():
        p, d = np.asarray(r["p"]), np.asarray(r["d"])
        on = [s for s in range(-60, 190) if m4[int(round(p[1] + s * d[1])), int(round(p[0] + s * d[0]))]]
        tip_new[k] = max(on) + POINT_OUT
    print(f"registration cc {cc:.3f}; new tips (s) A {tip_new['A']:.0f} (was {ROD['A']['tip']:.0f}), "
          f"B {tip_new['B']:.0f} (was {ROD['B']['tip']:.0f})")
    m0 = np.zeros((H, Wd), np.uint8)
    for r in ROD.values():
        s, t = coords(xx, yy, r["p"], r["d"])
        m0 |= (silhouette(s, t, r["top"], r["cone"], r["tip"], HW + 3) > 0).astype(np.uint8)
    Ws = track(fr, m0, ROI)
    reB, holesB = reengrave_B(Ws, tip_new, len(fr), a.tmp)
    out = []
    for i, f in enumerate(fr):
        roi = np.ascontiguousarray(f[y0:y1, x0:x1])
        Wf = Ws[i]
        geo = {k: dict(r, p=warp_pt(Wf, r["p"]), d=warp_dir(Wf, r["d"])) for k, r in ROD.items()}
        T2 = compose(np.array([[1, 0, -x0], [0, 1, -y0]], np.float64), compose(Wf, inv.astype(np.float64)))
        T2 = T2.astype(np.float32)
        bunp = cv2.warpAffine(patch, T2, (Wd, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
        buna = cv2.GaussianBlur(cv2.warpAffine(pmask, T2, (Wd, H), flags=cv2.INTER_LINEAR), (0, 0), 0.8)[..., None]
        plate = cv2.warpAffine(b0, T2, (Wd, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
        comp = roi.astype(np.float32).copy()
        # B: the re-engraved frame over the old leg (+ 6 px, feathered)
        hb = cv2.dilate(holesB[i][y0:y1, x0:x1].astype(np.uint8), np.ones((13, 13), np.uint8)).astype(np.float32)
        al = cv2.GaussianBlur(hb, (0, 0), 2.0)[..., None]
        comp = comp * (1 - al) + reB[i][y0:y1, x0:x1].astype(np.float32) * al
        # A: take 2's frame 0 at the same place on her head, tone-matched to this frame
        r = geo["A"]
        cone0 = tip_new["A"] - (r["tip"] - r["cone"])
        hole = hole_mask(r, xx, yy, cone0)
        hole = cv2.dilate(hole.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        bad = np.zeros((H, Wd), bool)
        for rr in geo.values():
            s, t = coords(xx, yy, rr["p"], rr["d"])
            bad |= silhouette(s, t, rr["top"], rr["cone"], rr["tip"], HW + 4) > 0
        fill = harmonic(plate, comp, hole | bad)
        al = cv2.GaussianBlur(hole.astype(np.float32), (0, 0), 1.0)[..., None]
        comp = comp * (1 - al) + fill * al
        # the new points (cone resampled from the old one, slid up the axis); B first, A on top
        for k in ("B", "A"):
            r = geo[k]
            d, n = np.asarray(r["d"]), unit_n(r["d"])
            s, t = coords(xx, yy, r["p"], r["d"])
            L = r["tip"] - r["cone"]
            cone0 = tip_new[k] - L
            # the body stub from the pencil itself; the sharpened end from A's (over her neck, inside the colour
            # matte in every frame; B's own point lay on the headrest, where the matte flickers on and off, so it
            # was engraved white in some frames)
            ra = geo["A"]
            da, na = np.asarray(ra["d"]), unit_n(ra["d"])
            sa = s + (ra["tip"] - tip_new[k])
            px = np.where(s >= cone0, ra["p"][0] + sa * da[0] + t * na[0], r["p"][0] + s * d[0] + t * n[0]) - x0
            py = np.where(s >= cone0, ra["p"][1] + sa * da[1] + t * na[1], r["p"][1] + s * d[1] + t * n[1]) - y0
            smp = cv2.remap(roi, px.astype(np.float32), py.astype(np.float32), cv2.INTER_LINEAR,
                            borderMode=cv2.BORDER_REFLECT).astype(np.float32)
            al = silhouette(s, t, cone0 - 12, cone0, tip_new[k])[..., None]
            comp = comp * (1 - al) + smp * al
        # the bun on top
        comp = comp * (1 - buna) + bunp * buna
        g = f.copy()
        g[y0:y1, x0:x1] = np.clip(comp + 0.5, 0, 255).astype(np.uint8)
        out.append(g)
    path = a.out if os.path.isabs(a.out) else os.path.join(ROOT, a.out)
    encode(out, fps, path, 16, ["-tune", "grain", "-movflags", "+faststart"])
    dx = [w[0, 2] for w in Ws]
    dy = [w[1, 2] for w in Ws]
    print(f"wrote {a.out}: {len(out)} frames; head track dx {min(dx):.1f}..{max(dx):.1f}, dy {min(dy):.1f}..{max(dy):.1f}")


if __name__ == "__main__":
    main()
