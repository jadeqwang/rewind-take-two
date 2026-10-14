#!/usr/bin/env python
"""C4: move the two crossed pencils up into the bun (v7, Jade 0:11: "pencils in slightly wrong positions in her hair").

In take 4 (from the kf_v3_b edit) the two pencils make a big X that crosses at the back of her skull, below the bun
(~(318, 161) at 1080p), and run down to her neck (pink pencil's point) and onto the headrest (blue pencil's point).
In every neighbouring verse-1 shot (C1, D2, D3, D6, D7, P2) they cross through the bun and only their points show
below it. This is a pixel pass on the engraved take, no generative model:

  1. the pencils are straight rods: their axes are fitted on the orange body pixels of frame 0, and they follow her
     head by a rigid (Euclidean) ECC fit per frame on the rods, chained from frame 0;
  2. both rods are removed (mask = the rods + 2 px) and the hole is filled by OpenCV's shift-map inpainting
     (cv2.xphoto INPAINT_SHIFTMAP: it copies whole patches of the same frame, so hair stays hair and the
     headrest keeps its engraved stripes). Shift-map is run once, on frame 0; the per-pixel source offset it
     chose is recovered and the SAME offsets fill every frame from that frame's own pixels: temporally stable
     (no per-frame re-solve flicker) and the streetlight sweeps carry over;
  3. the pencils are pasted back from the same frame's own pixels, at the same angles but crossing at NEW_X in the
     bun, with the body between crossing and point shortened (BELOW px from crossing to point instead of ~218/176):
     each new rod samples the old one along its axis (upper part as it was relative to the crossing, the sharpened
     end slid up), a 10 px cross-fade at the join, a silhouette alpha (body half-width 12.5, cones to the points).
     The pink-eraser pencil stays on top, as in the take.

  tools/engrave/.venv/bin/python tools/c4_pencils.py [--frames N] [--out PATH]
"""
import argparse
import os
import sys

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from blue_eraser import encode, frames_of  # noqa: E402

SRC = "media/shots/C4/take_4_engraved.mp4"
OUT = "media/shots/C4/take_4_engraved_pencils.mp4"
# frame 0 axes (fitted on the orange body pixels): point, unit direction (towards the point end), along-axis s of
# the eraser top, the cone start and the point. A = pink eraser (on top), B = blue eraser.
ROD = {
    "A": dict(p=(334.8, 183.8), d=(0.5745, 0.8185), top=-205.0, cone=138.0, tip=191.0),
    "B": dict(p=(312.5, 169.9), d=(-0.5433, 0.8395), top=-205.0, cone=138.0, tip=187.0),
}
NEW_X = (297.1, 130.0)   # new crossing: on A's own axis, at the bottom of the bun (bun ~x 272-352, y 60-132; old
                         # crossing (318.5, 160.6)), so A only loses its lower leg and B is moved. In the film the
                         # letterbox covers y < 138 at this shot's scale: the crossing sits just under the bar and
                         # the two points fan out below it, the bun (and the erasers) above the frame line
BELOW = 115.0            # crossing -> point, new (old: A ~219, B ~198)
HW = 12.5                # body half-width incl. ink outline
ROI = (150, 0, 520, 380)  # x0, y0, x1, y1: everything happens in here
# shift-map is solved per zone, each on a crop holding the texture that belongs there, so the headrest is filled
# from headrest and the neck from neck/hair (one solve over the whole ROI put hair on the headrest)
# The neck zone is skin meeting the hair edge: shift-map patches there showed cut-out hair curls and jagged skin
# once the head moved, a smooth inpaint read as an airbrushed shadow, and copying from each side of the old axis
# copied her ear. It gets a two-tone fill per frame instead (two_tone): hair and skin each inpainted from their own
# side, with a crisp edge where a smooth fill crosses mid-grey, like the cel-shaded hair edges round it.
# B's old lower leg lay right along the headrest's edge (headrest stripes on one side, the seat gap and the pillar's
# lines, parallel to the pencil, on the other): shift-map there mixed the two into a dark mess, so it is bridged:
# each side of B's old axis copies its own side one hole-width out, the shift tuned (once, on frame 0) to the
# texture's period on that side so the stripes run on; a 3 px seam on the axis.
ZONES = [  # (hole pixels with x0 <= x < x1 and y0 <= y < y1, crop the solve sees, fill), full-frame px
    ((0, 196, 300, 1080), (150, 110, 330, 380), "bridge"),     # B's old lower leg: headrest edge, the seat gap
    ((330, 252, 1920, 1080), (300, 150, 520, 380), "twotone"),  # A's old lower leg below the hair: neck, collar
    ((0, 0, 1920, 1080), (150, 0, 520, 380), "shiftmap"),       # the rest: hair, bun, headliner (mostly under the bar)
]
BRIDGE_H = HW + 2.5      # half-width of the removed strip


def unit_n(d):
    return np.array([-d[1], d[0]])


def crossing(pa, da, pb, db):
    M = np.array([[da[0], -db[0]], [da[1], -db[1]]])
    sa, sb = np.linalg.solve(M, np.asarray(pb) - np.asarray(pa))
    return np.asarray(pa) + sa * np.asarray(da), sa, sb


def coords(xx, yy, p, d):
    n = unit_n(d)
    return (xx - p[0]) * d[0] + (yy - p[1]) * d[1], (xx - p[0]) * n[0] + (yy - p[1]) * n[1]


def silhouette(s, t, top, cone, tip, hw=HW):
    lim = np.where(s < cone, hw, hw * (tip - s) / (tip - cone))
    a = np.clip(lim + 0.5 - np.abs(t), 0, 1)
    return a * np.clip(s - top + 0.5, 0, 1) * np.clip(tip - s + 0.5, 0, 1)


def shift_offsets(src, fill, hole, R=160, tol=6):
    """Per hole pixel, an offset (dy, dx) such that src[y+dy, x+dx] == fill[y, x] (shift-map copies pixels).
    In a flat area many offsets match by chance, and a chance match copies the wrong thing once the frame changes,
    so an offset only claims a pixel whose 3x3 hole neighbours it also explains (shift-map labels come in patches),
    offsets explaining the most such pixels first; what is left takes its smallest matching offset.
    Returns (ys, xs, oy, ox, ok)."""
    H, W = hole.shape
    ys, xs = np.nonzero(hole)
    tgt = fill[ys, xs].astype(np.int16)
    free = hole == 0
    k3 = np.ones((3, 3), np.uint8)
    cand = []
    for dy in range(-R, R + 1):
        yy = ys + dy
        vy = (yy >= 0) & (yy < H)
        for dx in range(-R, R + 1):
            xx = xs + dx
            v = vy & (xx >= 0) & (xx < W)
            iv = np.nonzero(v)[0]
            if len(iv) < 20:
                continue
            sy, sx = yy[iv], xx[iv]
            ok = free[sy, sx] & (np.abs(src[sy, sx].astype(np.int16) - tgt[iv]).max(1) <= tol)
            if ok.sum() < 20:
                continue
            M = free.astype(np.uint8)          # outside the hole counts as explained
            M[ys[iv[ok]], xs[iv[ok]]] = 1
            M[ys[iv[~ok]], xs[iv[~ok]]] = 0
            M[ys[~v], xs[~v]] = 0
            core = cv2.erode(M, k3)[ys, xs].astype(bool)
            m = np.zeros(len(ys), bool)
            m[iv[ok]] = True
            cand.append((int(core.sum()), dy * dy + dx * dx, dy, dx, core, m))
    oy = np.zeros(len(ys), np.int32)
    ox = np.zeros(len(ys), np.int32)
    done = np.zeros(len(ys), bool)
    for c, _, dy, dx, core, m in sorted(cand, key=lambda c: (-c[0], c[1])):
        sel = core & ~done
        oy[sel], ox[sel] = dy, dx
        done |= sel
    for c, _, dy, dx, core, m in sorted(cand, key=lambda c: c[1]):
        sel = m & ~done
        oy[sel], ox[sel] = dy, dx
        done |= sel
    return ys, xs, oy, ox, done


def two_tone(img, hole, T=100, rim=7):
    """Fill `hole` (uint8 0/1) with flat dark hair and flat skin: a Navier-Stokes fill decides the edge (where its
    luminance crosses T); the hair side is inpainted with the light rim pixels hidden, the skin side with the dark
    ones hidden, so neither smears into the other; a 1 px soft edge."""
    ys, xs = np.nonzero(hole)
    pad = rim + 8
    cy0, cy1 = max(ys.min() - pad, 0), min(ys.max() + pad + 1, img.shape[0])
    cx0, cx1 = max(xs.min() - pad, 0), min(xs.max() + pad + 1, img.shape[1])
    im = np.ascontiguousarray(img[cy0:cy1, cx0:cx1])
    hm = hole[cy0:cy1, cx0:cx1]
    lum = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY).astype(np.float32)
    near = cv2.dilate(hm, np.ones((2 * rim + 1, 2 * rim + 1), np.uint8)) & (1 - hm)
    F = cv2.inpaint(im, hm * 255, 6, cv2.INPAINT_NS)
    dark = cv2.cvtColor(F, cv2.COLOR_RGB2GRAY).astype(np.float32) < T
    Hf = cv2.inpaint(im, ((hm | (near & (lum >= T))) * 255).astype(np.uint8), 6, cv2.INPAINT_NS)
    Sf = cv2.inpaint(im, ((hm | (near & (lum < T))) * 255).astype(np.uint8), 6, cv2.INPAINT_NS)
    w = cv2.GaussianBlur(dark.astype(np.float32), (0, 0), 0.7)[..., None]
    fill = Hf * w + Sf * (1 - w)
    out = img.copy()
    sub = out[cy0:cy1, cx0:cx1]
    sub[hm > 0] = np.clip(fill[hm > 0] + 0.5, 0, 255).astype(np.uint8)
    return out


def _st(r, Y, X, x0, y0):
    d, n = np.asarray(r["d"]), unit_n(r["d"])
    return (X + x0 - r["p"][0]) * d[0] + (Y + y0 - r["p"][1]) * d[1], (X + x0 - r["p"][0]) * n[0] + (Y + y0 - r["p"][1]) * n[1]


def _sample(roi, r, s, t, x0, y0):
    d, n = np.asarray(r["d"]), unit_n(r["d"])
    mx = (r["p"][0] + s * d[0] + t * n[0] - x0).astype(np.float32)[None]
    my = (r["p"][1] + s * d[1] + t * n[1] - y0).astype(np.float32)[None]
    return cv2.remap(roi, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)[0].astype(np.float32)


def bridge_period(roi, r, Y, X, x0, y0, H=BRIDGE_H):
    """Per side of the rod, the copy distance (one hole width + 0..12 px) under which the band just outside the
    hole best repeats itself (the stripes' period on that side)."""
    s, _ = _st(r, Y, X, x0, y0)
    ss = np.linspace(s.min(), s.max(), 200)
    out = {}
    for sign in (-1, 1):
        band = np.concatenate([ss + 0 * k for k in range(6)]), np.concatenate([np.full(200, sign * (H + 1 + k)) for k in range(6)])
        ref = _sample(roi, r, band[0], band[1], x0, y0)
        best = None
        for dlt in range(0, 13):
            D = 2 * H + 1 + dlt
            e = np.abs(_sample(roi, r, band[0], band[1] + sign * D, x0, y0) - ref).mean()
            if best is None or e < best[0]:
                best = (e, D)
        out[sign] = best[1]
    return out


def bridge(roi, r, Y, X, x0, y0, shifts, seam=1.5):
    s, t = _st(r, Y, X, x0, y0)
    L = _sample(roi, r, s, t - shifts[-1], x0, y0)
    R = _sample(roi, r, s, t + shifts[1], x0, y0)
    w = np.clip(t / (2 * seam) + 0.5, 0, 1)[:, None]
    return L * (1 - w) + R * w


def warp_pt(W, p):
    return W[:, :2] @ np.asarray(p, float) + W[:, 2]


def warp_dir(W, d):
    v = W[:, :2] @ np.asarray(d, float)
    return v / np.linalg.norm(v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", type=int, default=0, help="only the first N frames (review)")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--cache", help="npz: keep the recovered shift-map offsets between runs (review)")
    a = ap.parse_args()
    fr, fps = frames_of(os.path.join(ROOT, SRC))
    if a.frames:
        fr = fr[:a.frames]
    x0, y0, x1, y1 = ROI
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    # frame-0 masks for tracking (the rods + their outline)
    m0 = np.zeros((y1 - y0, x1 - x0), np.uint8)
    for r in ROD.values():
        s, t = coords(xx, yy, r["p"], r["d"])
        m0 |= (silhouette(s, t, r["top"], r["cone"], r["tip"], HW + 3) > 0).astype(np.uint8)
    g0 = cv2.GaussianBlur(cv2.cvtColor(fr[0][y0:y1, x0:x1], cv2.COLOR_RGB2GRAY), (0, 0), 1.0).astype(np.float32)
    crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-5)
    W = np.eye(2, 3, dtype=np.float32)
    # old crossing and the along-axis positions of the crossing on each rod (frame 0)
    X0, sa0, sb0 = crossing(ROD["A"]["p"], ROD["A"]["d"], ROD["B"]["p"], ROD["B"]["d"])
    cross_s = {"A": sa0, "B": sb0}
    # what goes: all of B; A from its new cone down (its axis stays, its upper part stays as it is)
    sA_new = float((np.asarray(NEW_X) - ROD["A"]["p"]) @ np.asarray(ROD["A"]["d"]))
    cut = {"A": sA_new + BELOW - (ROD["A"]["tip"] - ROD["A"]["cone"]) - 2.0, "B": ROD["B"]["top"]}

    def hole_of(geo_):
        h = np.zeros_like(m0)
        for k, r in geo_.items():
            s_, t_ = coords(xx, yy, r["p"], r["d"])
            h |= ((silhouette(s_, t_, r["top"], r["cone"], r["tip"], HW + 0.5) > 0) & (s_ >= cut[k])).astype(np.uint8)
        return cv2.dilate(h, np.ones((5, 5), np.uint8))

    hole0 = hole_of(ROD)
    if True:
        # shift-map once, on frame 0, per zone; then recover the offsets it chose
        if a.cache and os.path.exists(a.cache):
            z = np.load(a.cache)
            hy, hx, oy, ox, okk, mode = z["hy"], z["hx"], z["oy"], z["ox"], z["ok"], z["mode"]
        else:
            roi0 = np.ascontiguousarray(fr[0][y0:y1, x0:x1])
            left = hole0.astype(bool).copy()
            parts = []
            for (zx0, zy0, zx1, zy1), (cx0, cy0, cx1, cy1), how in ZONES:
                zone = np.zeros_like(left)
                zone[max(zy0 - y0, 0):max(zy1 - y0, 0), max(zx0 - x0, 0):max(zx1 - x0, 0)] = True
                zone &= left
                left &= ~zone
                if not zone.any():
                    continue
                if how != "shiftmap":
                    zy_, zx_ = np.nonzero(zone)
                    parts.append((zy_, zx_, 0 * zy_, 0 * zx_, np.zeros(len(zy_), bool),
                                  np.full(len(zy_), 1 if how == "twotone" else 2)))
                    continue
                cx0, cy0, cx1, cy1 = cx0 - x0, cy0 - y0, cx1 - x0, cy1 - y0
                crop = np.ascontiguousarray(roi0[cy0:cy1, cx0:cx1])
                hc = hole0[cy0:cy1, cx0:cx1]          # every hole pixel in the crop is unknown (no pencil sources)
                fc = np.zeros_like(crop)
                cv2.xphoto.inpaint(cv2.cvtColor(crop, cv2.COLOR_RGB2BGR), (1 - hc) * 255, fc, cv2.xphoto.INPAINT_SHIFTMAP)
                fc = cv2.cvtColor(fc, cv2.COLOR_BGR2RGB)
                zy_, zx_, oy_, ox_, ok_ = shift_offsets(crop, fc, hc)
                keep = zone[cy0:cy1, cx0:cx1][zy_, zx_]
                parts.append((zy_[keep] + cy0, zx_[keep] + cx0, oy_[keep], ox_[keep], ok_[keep],
                              np.zeros(int(keep.sum()), int)))
            hy, hx, oy, ox, okk, mode = (np.concatenate([p_[j] for p_ in parts]) for j in range(6))
            if a.cache:
                np.savez(a.cache, hy=hy, hx=hx, oy=oy, ox=ox, ok=okk, mode=mode)
        print(f"shift-map offsets: {okk.mean() * 100:.1f}% of {len(hy)} hole px explained, "
              f"{len(set(zip(oy[okk].tolist(), ox[okk].tolist())))} distinct offsets")
    out, log = [], []
    for i, f in enumerate(fr):
        roi = np.ascontiguousarray(f[y0:y1, x0:x1])
        if i:
            gi = cv2.GaussianBlur(cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY), (0, 0), 1.0).astype(np.float32)
            try:   # warp maps frame-0 ROI coords -> frame-i ROI coords (start from the previous frame's)
                _, W = cv2.findTransformECC(g0, gi, W.copy(), cv2.MOTION_EUCLIDEAN, crit,
                                            cv2.dilate(m0, np.ones((9, 9), np.uint8)), 5)
            except cv2.error:
                pass
        # frame-i geometry (full-frame coords): W is in ROI coords
        Wf = W.astype(np.float64).copy()
        Wf[:, 2] += np.array([x0, y0]) - Wf[:, :2] @ np.array([x0, y0])
        geo = {k: dict(r, p=warp_pt(Wf, r["p"]), d=warp_dir(Wf, r["d"])) for k, r in ROD.items()}
        newX = warp_pt(Wf, NEW_X)
        # 1-2: remove both rods: the frame-0 hole and shift-map offsets, moved with the head (the camera is
        # locked to the car and her head moves < ~1 px here, so the hole and offsets are moved by whole pixels)
        sh = (int(round(float(warp_pt(Wf, (330, 160))[1] - 160))), int(round(float(warp_pt(Wf, (330, 160))[0] - 330))))
        comp = roi.astype(np.float32).copy()
        Y, X = np.clip(hy + sh[0], 0, y1 - y0 - 1), np.clip(hx + sh[1], 0, x1 - x0 - 1)
        SY, SX = np.clip(Y + oy, 0, y1 - y0 - 1), np.clip(X + ox, 0, x1 - x0 - 1)
        comp[Y[okk], X[okk]] = roi[SY[okk], SX[okk]]
        # despeckle the fill: a copied pixel far from its 3x3 median (a chance offset whose source changed
        # since frame 0) takes the median
        med = cv2.medianBlur(np.clip(comp, 0, 255).astype(np.uint8), 3).astype(np.float32)
        hm = np.zeros(hole0.shape, bool)
        hm[Y, X] = True
        bad = hm & (np.abs(comp - med).max(2) > 40)
        comp[bad] = med[bad]
        br = mode == 2
        if br.any():       # B's old lower leg on the headrest edge: bridged across B's old axis
            if i == 0:
                shifts = bridge_period(roi, geo["B"], Y[br], X[br], x0, y0)
            comp[Y[br], X[br]] = bridge(roi, geo["B"], Y[br], X[br], x0, y0, shifts)
        tt_ = mode == 1
        if tt_.any():      # the neck zone (A's old lower leg): two-tone fill
            miss = np.zeros(hole0.shape, np.uint8)
            miss[Y[tt_], X[tt_]] = 1
            comp = two_tone(np.clip(comp, 0, 255).astype(np.uint8), miss).astype(np.float32)
        # 3: new rods, B first, A on top
        for k in ("B", "A"):
            r = geo[k]
            d, n = r["d"], unit_n(r["d"])
            # new rod in new-crossing coords: s' in [-above, BELOW]; join where the old crossing is out of the way.
            # A: same axis, upper part where it was (src = its own s); B: upper part as it was relative to the
            # old crossing, where A hid it (join above that)
            sx = sA_new if k == "A" else cross_s[k]
            above = sx - r["top"]
            sn, tn = coords(xx, yy, newX, d)
            join = 20.0 if k == "A" else -30.0
            src_up = sx + sn
            src_lo = r["tip"] - (BELOW - sn)      # lower part: the sharpened end slid up
            w = np.clip((sn - join) / 10.0 + 0.5, 0, 1)
            al = silhouette(sn, tn, -above, BELOW - (r["tip"] - r["cone"]), BELOW)
            for part, ws in ((src_up, 1 - w), (src_lo, w)):
                px = (r["p"][0] + part * d[0] + tn * n[0] - x0).astype(np.float32)
                py = (r["p"][1] + part * d[1] + tn * n[1] - y0).astype(np.float32)
                smp = cv2.remap(roi, px, py, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
                if part is src_up:
                    acc = smp * ws[..., None]
                else:
                    acc += smp * ws[..., None]
            comp = comp * (1 - al[..., None]) + acc * al[..., None]
        g = f.copy()
        g[y0:y1, x0:x1] = np.clip(comp + 0.5, 0, 255).astype(np.uint8)
        out.append(g)
        log.append((i, float(Wf[0, 2]), float(Wf[1, 2])))
    encode(out, fps, os.path.join(ROOT, a.out) if not os.path.isabs(a.out) else a.out, 16,
           ["-tune", "grain", "-movflags", "+faststart"])
    dx = [l[1] for l in log]
    dy = [l[2] for l in log]
    print(f"wrote {a.out}: {len(out)} frames; head track dx {min(dx):.1f}..{max(dx):.1f}, dy {min(dy):.1f}..{max(dy):.1f}")


if __name__ == "__main__":
    main()
