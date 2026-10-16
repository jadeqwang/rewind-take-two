#!/usr/bin/env python3
"""Sleeve-roundel fix (v3 note 2:21, "arm patch text consistency"): re-letter Jade's `1420 / MHz` patch in a clip.

    tools/engrave/.venv/bin/python tools/sectionE/patchfix.py IN.mp4 OUT.mp4 --init X,Y[,FRAME] [--from F0] [--to F1]
        [--debug sheet.jpg] [--rot DEG] [--scale 0.74]

The video model redraws the tiny lettering every frame ("M2Z NHC", "1420 MHc" ...). This keeps the clip's own ring,
sleeve shading and occluders and replaces only the lettering inside the ring with one piece of artwork:
  1. track: the patch interior is the white hole enclosed by the dark ring; per frame the hole contour nearest the
     previous position is taken and an ellipse is RANSAC-fitted to it (the ring arc wins over a sleeve edge or hair that
     clips the patch). Ellipses are smoothed over time as centre + shape matrix; gaps are interpolated.
  2. orientation: the baseline angle at the --init frame is given by eye (`--guess`, deg, clockwise positive) and
     carried frame to frame by the sleeve's own motion around the patch (LK features, RANSAC similarity).
     `--guess-end` pins the last frame too; `--rot` forces one fixed angle.
  3. paint: inside the ring, everything that is not an occluder (thick dark shapes such as hair survive a morphological
     opening; lettering strokes do not) is refilled with the patch's own white (a normalised blur of its bright pixels,
     so sleeve shading stays) and the clean lettering, warped by the ellipse's affine map and antialiased 4x.
X,Y are pixels of IN at frame FRAME (default F0). Frames outside [F0, F1] are copied untouched. Audio is not kept.
"""
import argparse
import os
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FFMPEG = os.environ.get("FFMPEG", os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg"))
FONT = os.path.join(ROOT, "render/fonts/Overpass-wght.ttf")
ART = 640           # artwork size (px); the unit disc of the ring's inner edge maps to the inscribed circle


def art(scale=0.80, weight=900):
    """Alpha map (0..1, float32, ART x ART) of the lettering, centred on the disc."""
    im = Image.new("L", (ART, ART), 0)
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 10)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass

    def fit(text, width):
        size = 40
        while True:
            ff = ImageFont.truetype(FONT, size)
            try:
                ff.set_variation_by_axes([weight])
            except Exception:
                pass
            l, t, r, b = d.textbbox((0, 0), text, font=ff)
            if r - l >= width or size > 600:
                return ff, (l, t, r, b)
            size += 2
    R = ART / 2
    # two centred lines; widths are chords of the disc at the line heights
    f1, b1 = fit("1420", 2 * R * scale * 0.98)
    f2, b2 = fit("MHz", 2 * R * scale * 0.80)
    h1, h2 = b1[3] - b1[1], b2[3] - b2[1]
    gap = 0.10 * R
    top = R - (h1 + gap + h2) / 2
    d.text((R - (b1[0] + b1[2]) / 2, top - b1[1]), "1420", font=f1, fill=255)
    d.text((R - (b2[0] + b2[2]) / 2, top + h1 + gap - b2[1]), "MHz", font=f2, fill=255)
    im = im.filter(ImageFilter.MaxFilter(5))          # a touch heavier: thin strokes vanish at 30 px
    return np.asarray(im, np.float32) / 255.0


STILL = (".png", ".jpg", ".jpeg")


def read(path):
    if path.lower().endswith(STILL):                  # v9: a still is a one-frame clip
        return [cv2.imread(path)], 24
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    fr = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        fr.append(f)
    return fr, fps


def holes(gray, thr, centre, rad):
    """White regions enclosed by dark, near `centre`: [(contour, area, centroid)]."""
    h, w = gray.shape
    R = int(rad * 3.2)
    x0, y0 = max(0, int(centre[0]) - R), max(0, int(centre[1]) - R)
    x1, y1 = min(w, int(centre[0]) + R), min(h, int(centre[1]) + R)
    dark = (gray[y0:y1, x0:x1] < thr).astype(np.uint8)
    cnts, hier = cv2.findContours(dark, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    out = []
    if hier is None:
        return out
    for c, hh in zip(cnts, hier[0]):
        if hh[3] < 0 or len(c) < 12:
            continue
        a = cv2.contourArea(c)
        if a < 30:
            continue
        m = cv2.moments(c)
        if m["m00"] <= 0:
            continue
        out.append((c + np.array([[x0, y0]]), a, (m["m10"] / m["m00"] + x0, m["m01"] / m["m00"] + y0)))
    return out


def ell_params(e):
    (cx, cy), (d1, d2), ang = e
    return cx, cy, d1 / 2, d2 / 2, np.deg2rad(ang)


def ell_resid(pts, e):
    cx, cy, a, b, th = ell_params(e)
    c, s = np.cos(th), np.sin(th)
    x, y = pts[:, 0] - cx, pts[:, 1] - cy
    u, v = (x * c + y * s) / max(a, 1e-3), (-x * s + y * c) / max(b, 1e-3)
    return np.abs(np.hypot(u, v) - 1) * min(a, b)


def ransac_ellipse(pts, rng, tol=1.0, iters=160, prev_r=None):
    pts = pts.astype(np.float32)
    best, best_n = None, -1
    n = len(pts)
    if n < 12:
        return None, 0
    for _ in range(iters):
        # sample a contiguous-ish arc plus random points: arcs make better hypotheses than scattered points
        i0 = rng.integers(0, n)
        span = rng.integers(max(8, n // 6), max(9, n // 2))
        idx = (i0 + np.sort(rng.choice(span, 7, replace=False))) % n
        try:
            e = cv2.fitEllipseDirect(pts[idx])
        except cv2.error:
            continue
        cx, cy, a, b, _ = ell_params(e)
        if not np.isfinite([cx, cy, a, b]).all() or min(a, b) < 3 or max(a, b) / max(1e-3, min(a, b)) > 3.2:
            continue
        if prev_r is not None and not (0.7 * prev_r < np.sqrt(a * b) < 1.4 * prev_r):
            continue
        k = int((ell_resid(pts, e) < tol).sum())
        if k > best_n:
            best, best_n = e, k
    if best is None:
        return None, 0
    inl = ell_resid(pts, best) < tol * 1.3
    if inl.sum() >= 8:
        try:
            best = cv2.fitEllipseDirect(pts[inl])
        except cv2.error:
            pass
    return best, best_n / n


def shape_matrix(e):
    cx, cy, a, b, th = ell_params(e)
    Rm = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    return Rm @ np.diag([a * a, b * b]) @ Rm.T


def baseline_angle(gray, mask, thr, guess, span=50, step=2):
    """Baseline direction (deg, image coords, y down) of two lines of dark lettering inside `mask`."""
    ys, xs = np.nonzero(mask & (gray < thr))
    if len(xs) < 20:
        return None
    xs = xs - xs.mean()
    ys = ys - ys.mean()
    best, bs = None, -1
    for ang in np.arange(guess - span, guess + span + 1e-3, step):
        t = np.deg2rad(ang)
        proj = -xs * np.sin(t) + ys * np.cos(t)          # distance from the baseline direction
        hist, _ = np.histogram(proj, bins=np.arange(proj.min() - 1, proj.max() + 2, 1.0))
        hist = cv2.GaussianBlur(hist.astype(np.float32)[None], (0, 0), 0.8)[0]
        sc = float(hist.var())
        if sc > bs:
            best, bs = ang, sc
    return best


def smooth(v, sigma):
    v = np.asarray(v, np.float64)
    if sigma <= 0 or len(v) < 3:
        return v
    r = int(np.ceil(sigma * 3))
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    k /= k.sum()
    p = np.pad(v, [(r, r)] + [(0, 0)] * (v.ndim - 1), mode="edge")
    return np.stack([np.tensordot(k, p[i:i + 2 * r + 1], axes=(0, 0)) for i in range(len(v))])


def fill_gaps(vals, ok):
    vals = np.asarray(vals, np.float64).copy()
    idx = np.nonzero(ok)[0]
    if len(idx) == 0:
        raise SystemExit("patch not found in any frame")
    flat = vals.reshape(len(vals), -1)
    for j in range(flat.shape[1]):
        flat[:, j] = np.interp(np.arange(len(vals)), idx, flat[idx, j])
    return flat.reshape(vals.shape)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--init", required=True)
    ap.add_argument("--from", dest="f0", type=int, default=0)
    ap.add_argument("--to", dest="f1", type=int, default=None)
    ap.add_argument("--thr", type=int, default=120)
    ap.add_argument("--rad", type=float, default=None, help="initial inner radius guess (px); default: auto")
    ap.add_argument("--guess", type=float, default=0.0, help="initial baseline angle guess (deg, clockwise positive)")
    ap.add_argument("--guess-end", dest="guess_end", type=float, default=None, help="baseline angle at frame F1 (drift pin)")
    ap.add_argument("--rot", type=float, default=None, help="force this baseline angle for every frame")
    ap.add_argument("--scale", type=float, default=0.80)
    ap.add_argument("--weight", type=int, default=900)
    ap.add_argument("--ink", default=None, help="lettering colour r,g,b (default: the ring's own dark)")
    ap.add_argument("--crf", type=int, default=12)
    ap.add_argument("--debug", default=None)
    # v9 (fix 8): fast, jumpy takes (F7_02: the roundel jumps 20-60 px between held pairs of frames)
    ap.add_argument("--keys", default=None, help="per-frame seeds 'F:X,Y[,ANG];F:X,Y[,ANG]...': the ring is searched at X,Y "
                    "on frame F instead of at the previous frame's centre; if ANG is given on every key, the baseline angle "
                    "is interpolated between the keys instead of carried by optical flow")
    ap.add_argument("--occ", type=float, default=0.26, help="occluder opening radius (x inner radius): dark shapes thicker "
                    "than this inside the ring are kept as hair/occluders; raise it when the take's own glyphs are bold")
    ap.add_argument("--ring-fill", dest="ring_fill", type=float, default=0.0, help="also repaint everything inside this "
                    "fraction of the fitted inner ellipse, even outside the white hull (glyphs fused to the ring)")
    ap.add_argument("--drop", default="", help="frames whose ring fit is wrong (e.g. '29,30'): treated as untracked, so "
                    "the ellipse is interpolated from their neighbours")
    ap.add_argument("--skip", default="", help="frames to leave untouched (fix them in a second pass with other settings)")
    ap.add_argument("--sigma", default="0.8,1.6,1.5", help="temporal smoothing of centre, shape, angle (frames); 0 = off")
    a = ap.parse_args()
    keys = {}
    if a.keys:
        for kv in a.keys.replace(" ", "").strip(";").split(";"):
            kf, kxy = kv.split(":")
            keys[int(kf)] = [float(v) for v in kxy.split(",")]
    sig_c, sig_s, sig_a = [float(v) for v in a.sigma.split(",")]

    fr, fps = read(a.src)
    H, W = fr[0].shape[:2]
    ini = [float(v) for v in a.init.split(",")]
    f0 = a.f0
    f1 = len(fr) - 1 if a.f1 is None else min(a.f1, len(fr) - 1)
    fi = int(ini[2]) if len(ini) > 2 else f0
    gray = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in fr]
    rng = np.random.default_rng(7)

    # ---- 1. track -------------------------------------------------------------------------------------------------------
    rad0 = a.rad or H * 0.035
    ell, hole = {}, {}

    def step(i, centre, rad):
        cs = holes(gray[i], a.thr, centre, rad)
        cs = [c for c in cs if np.hypot(c[2][0] - centre[0], c[2][1] - centre[1]) < 0.95 * rad and c[1] < 1.7 * np.pi * rad * rad]
        if not cs or sum(c[1] for c in cs) < 0.25 * np.pi * rad * rad:
            return None
        # lettering that touches the ring or a clipping edge splits the white interior into several holes and makes
        # its outline ragged: take them all, and fit only to the points on their common convex hull (ring arc + clip edge)
        allp = np.concatenate([c[0][:, 0, :] for c in cs]).astype(np.float32)
        hull = cv2.convexHull(allp.reshape(-1, 1, 2).astype(np.int32))
        d = np.array([abs(cv2.pointPolygonTest(hull, (float(x), float(y)), True)) for x, y in allp])
        outer = allp[d < 1.2]
        e, frac = ransac_ellipse(outer, rng, tol=max(0.8, rad * 0.035), prev_r=rad if (i != fi or a.rad) else None)
        if e is None or frac < 0.3:
            return None
        return e, hull

    # the first frame: try a few radius guesses
    got = None
    for r in ([a.rad] if a.rad else [H * s for s in (0.02, 0.03, 0.045, 0.065, 0.09)]):
        got = step(fi, ini[:2], r)
        if got:
            break
    if not got:
        raise SystemExit(f"no ring found near {ini[:2]} in frame {fi}")
    ell[fi], hole[fi] = got
    for order in (range(fi + 1, f1 + 1), range(fi - 1, f0 - 1, -1)):
        prev = ell[fi]
        for i in order:
            cx, cy, ea, eb, _ = ell_params(prev)
            if i in keys:
                cx, cy = keys[i][:2]
            got = step(i, (cx, cy), np.sqrt(ea * eb))
            if got:
                ell[i], hole[i] = got
                prev = got[0]
    for d_ in [int(v) for v in a.drop.split(",") if v.strip()]:
        ell.pop(d_, None)
        hole.pop(d_, None)
    frames = list(range(f0, f1 + 1))
    ok = np.array([i in ell for i in frames])
    print(f"tracked {ok.sum()}/{len(frames)} frames; missing: {[i for i, o in zip(frames, ok) if not o][:40]}")
    cen = fill_gaps([ell_params(ell[i])[:2] if i in ell else (0, 0) for i in frames], ok)
    shp = fill_gaps([shape_matrix(ell[i]) if i in ell else np.eye(2) for i in frames], ok)
    for k, i in enumerate(frames):                   # an untracked frame with a key: trust the key over interpolation
        if not ok[k] and i in keys:
            cen[k] = keys[i][:2]
    cen = smooth(cen, sig_c)
    shp = smooth(shp, sig_s)

    # ---- 2. orientation -------------------------------------------------------------------------------------------------
    # The lettering itself is too garbled to measure a baseline from, so the in-plane rotation is carried from frame to
    # frame by the sleeve around the patch (LK features within ~2.4 radii, RANSAC similarity) starting from --guess,
    # the baseline angle at the --init frame (deg, clockwise positive in image space, read off a frame by eye).
    def flow_rot(i, j, c, r):
        m = np.zeros((H, W), np.uint8)
        cv2.circle(m, (int(c[0]), int(c[1])), int(2.4 * r), 255, -1)
        pts = cv2.goodFeaturesToTrack(gray[i], 120, 0.01, 3, mask=m)
        if pts is None or len(pts) < 8:
            return 0.0
        nxt, st, _ = cv2.calcOpticalFlowPyrLK(gray[i], gray[j], pts, None, winSize=(21, 21), maxLevel=3)
        back, st2, _ = cv2.calcOpticalFlowPyrLK(gray[j], gray[i], nxt, None, winSize=(21, 21), maxLevel=3)
        good = (st[:, 0] == 1) & (st2[:, 0] == 1) & (np.linalg.norm(back - pts, axis=2)[:, 0] < 0.8)
        if good.sum() < 6:
            return 0.0
        Ms, _ = cv2.estimateAffinePartial2D(pts[good], nxt[good], method=cv2.RANSAC, ransacReprojThreshold=1.5)
        if Ms is None:
            return 0.0
        return float(np.degrees(np.arctan2(Ms[1, 0], Ms[0, 0])))

    rads = np.sqrt(np.sqrt(np.maximum(np.linalg.det(shp), 1e-6)))
    angs = np.zeros(len(frames))
    if a.rot is not None:
        angs[:] = a.rot
    elif keys and all(len(v) > 2 for v in keys.values()):
        kk = sorted(keys)
        angs = np.interp(frames, kk, [keys[k][2] for k in kk])
        angs = smooth(angs, sig_a)
    else:
        k0 = fi - f0
        angs[k0] = a.guess
        for k in range(k0 + 1, len(frames)):
            angs[k] = angs[k - 1] + flow_rot(frames[k - 1], frames[k], cen[k - 1], rads[k - 1])
        for k in range(k0 - 1, -1, -1):
            angs[k] = angs[k + 1] + flow_rot(frames[k + 1], frames[k], cen[k + 1], rads[k + 1])
        if a.guess_end is not None:                      # optional drift correction: pin the last frame's angle too
            angs += np.linspace(0, a.guess_end - angs[-1], len(angs)) * (np.arange(len(angs)) >= k0)
        angs = smooth(angs, sig_a)
    print("baseline angle: start %.1f end %.1f min %.1f max %.1f" % (angs[0], angs[-1], angs.min(), angs.max()))

    # ---- 3. paint -------------------------------------------------------------------------------------------------------
    alpha_art = art(a.scale, a.weight)
    out_frames = [f.copy() for f in fr]
    dbg = []
    SS = 4
    skip = {int(v) for v in a.skip.split(",") if v.strip()}
    for k, i in enumerate(frames):
        if i in skip:
            continue
        M = shp[k]
        w_, v_ = np.linalg.eigh(M)
        L = v_ @ np.diag(np.sqrt(np.maximum(w_, 1e-6)))         # unit circle -> ellipse (any L R also does)
        # choose the in-disc rotation so that the artwork's x axis lands on the measured baseline direction
        t = np.deg2rad(angs[k])
        bdir = np.array([np.cos(t), np.sin(t)])
        u = np.linalg.solve(L, bdir)
        psi = np.arctan2(u[1], u[0])
        Rp = np.array([[np.cos(psi), -np.sin(psi)], [np.sin(psi), np.cos(psi)]])
        A = L @ Rp
        if np.linalg.det(A) < 0:                               # keep the lettering right-reading
            A = A @ np.diag([1, -1])
        c = cen[k]
        r = float(np.sqrt(np.sqrt(max(np.linalg.det(M), 1e-6))))
        pad = int(np.ceil(np.sqrt(w_.max()) + 4))
        x0, y0 = int(np.floor(c[0])) - pad, int(np.floor(c[1])) - pad
        x1, y1 = x0 + 2 * pad + 1, y0 + 2 * pad + 1
        if x0 < 0 or y0 < 0 or x1 > W or y1 > H:
            continue
        # artwork -> frame crop at SSx, then area-downsample
        S_art = np.array([[2 / ART, 0, -1], [0, 2 / ART, -1]])                   # art px -> unit disc
        Aff = np.hstack([A, (c - [x0, y0])[:, None]]) @ np.vstack([S_art, [0, 0, 1]])   # art px -> crop px
        Aff[:, :] *= SS
        big = cv2.warpAffine(alpha_art, Aff.astype(np.float32), ((x1 - x0) * SS, (y1 - y0) * SS), flags=cv2.INTER_LINEAR)
        al = cv2.resize(big, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
        crop = fr[i][y0:y1, x0:x1].astype(np.float32)
        gcrop = gray[i][y0:y1, x0:x1]
        # inside the inner ellipse (slightly shrunk so the clip's own ring edge is never touched)
        yy, xx = np.mgrid[y0:y1, x0:x1]
        P = np.stack([xx - c[0], yy - c[1]], -1)
        Minv = np.linalg.inv(M)
        rho = np.sqrt(np.einsum("...i,ij,...j->...", P, Minv, P))
        inner = rho < 1 - 1.6 / max(r, 4)
        # visible interior = the convex hull of the white interior (so the clip's ring, a sleeve edge clipping the patch
        # and its antialiasing are never touched, while lettering that touches them is covered). Thick dark shapes inside
        # it (hair crossing the patch) are left alone below.
        hi = i if i in hole else min(hole, key=lambda j: abs(j - i))
        hm = np.zeros((H, W), np.uint8)
        cv2.fillConvexPoly(hm, hole[hi], 255)
        hm = cv2.erode(hm, np.ones((3, 3), np.uint8))[y0:y1, x0:x1]
        if hi != i:                                   # borrowed from the nearest tracked frame, moved with the patch
            sh = np.round(cen[k] - cen[hi - f0]).astype(int)
            hm = np.roll(np.roll(hm, sh[1], 0), sh[0], 1)
        vis = ((rho < 1.04) & (hm > 0)) | (rho < a.ring_fill)
        dark = (gcrop < a.thr) & vis
        ro = max(2, int(round(a.occ * r)))
        ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * ro + 1, 2 * ro + 1))
        thick = cv2.dilate(cv2.morphologyEx(dark.astype(np.uint8), cv2.MORPH_OPEN, ker), np.ones((3, 3), np.uint8)) > 0
        paint = vis & ~thick
        # the patch's own white: normalised blur of its bright pixels
        bright = (inner & (gcrop > a.thr + 40)).astype(np.float32)
        sg = max(1.5, 0.35 * r)
        num = cv2.GaussianBlur(crop * bright[..., None], (0, 0), sg)
        den = cv2.GaussianBlur(bright, (0, 0), sg)[..., None]
        med = np.median(crop[bright > 0], 0) if bright.sum() > 5 else np.array([235, 235, 235], np.float32)
        white = np.where(den > 0.05, num / np.maximum(den, 1e-3), med)
        if a.ink:
            ink = np.array([float(v) for v in a.ink.split(",")][::-1], np.float32)
        else:
            ringpx = fr[i][y0:y1, x0:x1][(rho > 1.02) & (rho < 1.12) & (gcrop < a.thr - 30)]
            ink = np.median(ringpx, 0).astype(np.float32) if len(ringpx) > 8 else np.array([30, 28, 28], np.float32)
        new = white * (1 - al[..., None]) + ink * al[..., None]
        pm = cv2.GaussianBlur(paint.astype(np.float32), (0, 0), 0.6)[..., None]
        pm = np.clip(pm * 1.15, 0, 1) * (rho < 1.04)[..., None]
        res = crop * (1 - pm) + new * pm
        out_frames[i][y0:y1, x0:x1] = np.clip(res, 0, 255).astype(np.uint8)
        if a.debug and k % max(1, len(frames) // 16) == 0 and len(dbg) < 16:
            z = 240
            b4 = cv2.resize(fr[i][y0:y1, x0:x1], (z, z), interpolation=cv2.INTER_CUBIC)
            af = cv2.resize(out_frames[i][y0:y1, x0:x1], (z, z), interpolation=cv2.INTER_CUBIC)
            cv2.putText(b4, str(i), (4, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            dbg.append(np.vstack([b4, af]))
    if a.debug and dbg:
        while len(dbg) % 8:
            dbg.append(np.zeros_like(dbg[0]))
        cv2.imwrite(a.debug, np.vstack([np.hstack(dbg[r:r + 8]) for r in range(0, len(dbg), 8)]))

    # ---- encode ---------------------------------------------------------------------------------------------------------
    if a.out.lower().endswith(STILL):
        cv2.imwrite(a.out, out_frames[0])
        print("wrote", a.out)
        return
    p = subprocess.Popen([FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", f"{fps}",
                          "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", str(a.crf), "-pix_fmt", "yuv420p",
                          "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", a.out], stdin=subprocess.PIPE)
    for f in out_frames:
        p.stdin.write(f.tobytes())
    p.stdin.close()
    p.wait()
    print("wrote", a.out)


if __name__ == "__main__":
    main()
