#!/usr/bin/env python3
"""v10 (Jade 2026-10-18, 3:07): "RARE EARTH" on the back of Jade's cropped jacket in F5b (the colour-pencil rooftop,
song 3:07.08-3:08.84), "flowing with the way the jacket sways".

Same canon as tools/v9/rare_earth.py (inputs/jade_in_outfit.png BACK: small dark-grey sans capitals centred under the
pale-blue dot, text width ~1.0 D, gap dot -> caps 0.14 D, D = dot diameter), but the jacket here is cropped and swings,
so the lettering is not a rigid decal on the dot. Per frame:

  1. DOT: pale-blue blob nearest the previous centre, ellipse-fitted on its visible outline only (contour points next to
     dark hair are dropped, the hair blows across the top of the dot). Gives the panel's position and scale
     (semi-diameters along/across the baseline).
  2. HEM: the cropped jacket's bottom outline under the dot (per column: the first black run below the dot with jacket
     white above it), robust quadratic fit y = h(x). Gives the panel's tilt (tangent at the dot's x) and its bend.
  3. MESH: the text is laid out in dot units (u along the baseline, v down from the dot centre) and mapped to the
     frame by a two-anchor deformation: rigid rotation/scale about the dot (tilt = hem tangent), plus the hem's
     deviation from its tangent line, blended in linearly from 0 at the dot's bottom edge to 1 at the hem. So the
     lettering bends and rocks with the hem as the cropped jacket flaps, while staying printed under the dot. All
     track parameters are lightly smoothed in time (Gaussian, cut at nothing: the take is one continuous push-in).
  4. INK: glyphs (Liberation Sans Bold) get a fixed, text-space ink texture (slightly rough edges, 80-100 % density
     grain), so the texture rides with the fabric and never swims. Rendered by inverse-mapping each output pixel
     at 4x supersampling, then painted as a MULTIPLY: pixel * ink / local jacket white, so the cloth's own shading,
     pencil grain and fold strokes darken the letters.
  5. OCCLUSION: ink only lands on jacket-white pixels (low chroma, bright: the dot, orange band and skin are excluded)
     and never on hair: dark pixels (lum < hair_lum, raw, not closed, so single blown strands count) dilated by 1 px
     with a soft edge. Arms are white sleeves separated by black outlines, which the same dark mask excludes.

    $PY tools/v10/rare_earth_F5b.py tools/v10/rare_earth_F5b.json                  # write spec["out"]
    $PY tools/v10/rare_earth_F5b.py SPEC --track-only                              # per-frame track + flow residual
    $PY tools/v10/rare_earth_F5b.py SPEC --sheet 0:50 --outdir DIR                 # every-frame crop sheets
    $PY tools/v10/rare_earth_F5b.py SPEC --compare 6,21,35 --outdir DIR            # before/after tiles
$PY = tools/engrave/.venv/bin/python (cv2, av, numpy, PIL).
"""
import argparse
import json
import math
import os
import subprocess

import av
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = "/home/jade/Documents/rewind-take-two"
FFMPEG = os.path.expanduser("~/Documents/1-music-shipped/moongazing/.venv/lib/python3.12/site-packages/"
                            "imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2")


def frames(path):
    c = av.open(path)
    for f in c.decode(video=0):
        yield f.to_ndarray(format="rgb24")
    c.close()


def lum_of(img):
    return img.astype(np.float32).mean(-1)


# ---------------------------------------------------------------- 1. dot
def hair_mask(img, spec):
    """black hair (uint8 0/1): very dark, or dark and not blue (the dot's own outline is a dark BLUE line, ~(40,72,110))"""
    a = img.astype(np.int16)
    lum = a.mean(-1)
    return ((lum < spec.get("hair_dark", 55)) | ((lum < 80) & (a[..., 2] - a[..., 0] < 25))).astype(np.uint8)


def find_dot(img, prev, spec):
    a = img.astype(np.int16)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    win = spec.get("win", 90)
    x0, y0 = max(int(prev[0] - win), 0), max(int(prev[1] - win), 0)
    x1, y1 = int(prev[0] + win), int(prev[1] + win)
    m = ((B - R > 60) & (B > 150) & (G > 100))[y0:y1, x0:x1].astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    idx = [k for k in range(1, n) if st[k, 4] >= spec.get("min_area", 500)]
    if not idx:
        return None
    k = min(idx, key=lambda k: np.hypot(*(cen[k] + [x0, y0] - prev)) - st[k, 4] / 40)
    blob = (lab == k).astype(np.uint8)
    blob = cv2.morphologyEx(blob, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    cnts, _ = cv2.findContours(blob, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cnt = max(cnts, key=cv2.contourArea)[:, 0, :]
    # drop outline points that touch dark hair (the hair cuts the dot; its edge there is not the dot's edge)
    dark = hair_mask(img[y0:y1, x0:x1], spec)
    dark = cv2.dilate(dark, np.ones((5, 5), np.uint8))
    keep = dark[cnt[:, 1], cnt[:, 0]] == 0
    used = cnt[keep] if keep.sum() >= 25 else cnt
    (cx, cy), (w, h), ang = cv2.fitEllipse(used.reshape(-1, 1, 2).astype(np.float32))
    return dict(c=[cx + x0, cy + y0], ax=[w / 2, h / 2], ang=ang, vis=float(keep.mean()), area=int(st[k, 4]))


# ---------------------------------------------------------------- 2. hem
def find_hem(img, d, spec):
    """quadratic y = p(x) of the jacket's bottom outline under the dot (columns cx +- hem_span radii)"""
    cx, cy = d["c"]
    r = 0.5 * (d["ax"][0] + d["ax"][1])
    lum = cv2.blur(lum_of(img), (3, 1))
    a = img.astype(np.int16)
    chroma = a.max(-1) - a.min(-1)
    pts = []
    span = spec.get("hem_span", 1.5)
    for x in range(max(int(cx - span * r), 0), min(int(cx + span * r) + 1, img.shape[1])):
        ya, yb = int(cy + 1.15 * r), min(img.shape[0] - 3, int(cy + 3.4 * r))
        for y in range(ya, yb):
            # the seam between the back panel and the waist rib: a thin grey-black line, so a single-pixel test
            # (a 2-px test skips it in places and lands on the rib's bottom outline instead)
            if lum[y, x] < spec.get("hem_lum", 115):
                above = lum[y - 5:y - 1, x]
                if above.mean() > spec.get("hem_bright", 140) and chroma[y - 5:y - 1, x].mean() < 45:
                    pts.append((x, y))
                break
    if len(pts) < 15:
        return None
    pts = np.array(pts, float)
    keep = np.ones(len(pts), bool)
    for _ in range(5):
        p = np.polyfit(pts[keep, 0] - cx, pts[keep, 1], 2)
        res = pts[:, 1] - np.polyval(p, pts[:, 0] - cx)
        keep = np.abs(res) < max(1.5, np.median(np.abs(res[keep])) * 2.5)
    if keep.sum() < 15:
        return None
    return dict(p=p.tolist(), n=int(keep.sum()), x=[float(pts[keep, 0].min()), float(pts[keep, 0].max())])


def track(clip, spec):
    prev = np.array(spec["start"], float)
    out = []
    for img in frames(clip):
        d = find_dot(img, prev, spec)
        if d:
            d["hem"] = find_hem(img, d, spec)
            prev = np.array(d["c"])
        out.append(d)
    return out


def gsmooth(v, sig):
    if sig <= 0 or len(v) < 3:
        return v
    R = int(3 * sig + 1)
    k = np.exp(-0.5 * (np.arange(-R, R + 1) / sig) ** 2)
    k /= k.sum()
    # reflect-pad so the ends keep their trend
    vp = np.concatenate([2 * v[0] - v[R:0:-1], v, 2 * v[-1] - v[-2:-R - 2:-1]])
    return np.convolve(vp, k, "valid")


def semi(d, phi):
    """the dot ellipse's semi-diameter in direction phi (radians)"""
    e = math.radians(d["ang"])
    return 1.0 / math.sqrt((math.cos(phi - e) / d["ax"][0]) ** 2 + (math.sin(phi - e) / d["ax"][1]) ** 2)


def normalise(tr, spec):
    """per frame: centre, scale along/across the baseline, tilt, and the hem's bend, all smoothed in time"""
    n = len(tr)
    ok = [i for i in range(n) if tr[i]]
    cs = np.array([tr[i]["c"] for i in ok], float)
    # hem: tangent slope at the dot's x and its curvature; dist dot centre -> hem (along y)
    hp = []
    for i in ok:
        h = tr[i]["hem"]
        hp.append(h["p"] if h else [np.nan] * 3)
    hp = np.array(hp, float)
    for j in range(3):
        g = ~np.isnan(hp[:, j])
        hp[:, j] = np.interp(np.arange(len(ok)), np.nonzero(g)[0], hp[g, j])
    slope = hp[:, 1]
    curv = hp[:, 0]
    hdist = hp[:, 2] - cs[:, 1]
    rot = np.degrees(np.arctan(slope))
    rot = gsmooth(rot, spec.get("rot_smooth", 1.5))
    curv = gsmooth(curv, spec.get("curv_smooth", 1.5))
    hdist = gsmooth(hdist, spec.get("hdist_smooth", 1.5))
    sx = np.array([semi(tr[i], math.radians(rot[j])) for j, i in enumerate(ok)])
    sy = np.array([semi(tr[i], math.radians(rot[j]) + math.pi / 2) for j, i in enumerate(ok)])
    # dot size: robust (log) trend + small residual, since the visible arc changes as the hair blows
    sx = gsmooth(sx, spec.get("scale_smooth", 2.0))
    sy = gsmooth(sy, spec.get("scale_smooth", 2.0))
    cx = gsmooth(cs[:, 0], spec.get("c_smooth", 0.8))
    cy = gsmooth(cs[:, 1], spec.get("c_smooth", 0.8))
    res = [None] * n
    for j, i in enumerate(ok):
        res[i] = dict(c=[float(cx[j]), float(cy[j])], sx=float(sx[j]), sy=float(sy[j]), rot=float(rot[j]),
                      curv=float(curv[j]), hdist=float(hdist[j]), raw=tr[i])
    if spec.get("frames"):
        for i in range(n):
            if not any(a <= i <= b for a, b in spec["frames"]):
                res[i] = None
    return res


# ---------------------------------------------------------------- 3. lettering art (with a fixed ink texture)
def glyphs(spec):
    S = 400
    font = ImageFont.truetype(spec.get("font", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"), S)
    text = spec.get("text", "RARE EARTH")
    trk = spec.get("tracking", 0.05) * S
    word = spec.get("word_space", 1.5)
    xs, x = [], 0.0
    for ch in text:
        xs.append(x)
        x += font.getlength(ch) * (word if ch == " " else 1.0) + trk
    im = Image.new("L", (int(x + 200), 800), 0)
    dr = ImageDraw.Draw(im)
    for ch, cx in zip(text, xs):
        dr.text((100 + cx, 200), ch, font=font, fill=255)
    a = np.asarray(im, np.float32) / 255
    ys, xs_ = np.nonzero(a > 0.5)
    a = a[ys.min() - 20:ys.max() + 21, xs_.min() - 20:xs_.max() + 21].copy()
    rng = np.random.default_rng(spec.get("seed", 7))
    tex = spec.get("texture", {})
    if tex:
        H, W = a.shape
        # rough edges: displace the glyph mask by smooth noise (amplitude in fraction of cap height)
        cap = H - 40
        amp = tex.get("edge", 0.025) * cap
        nx = cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), cap * 0.04)
        ny = cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), cap * 0.04)
        nx *= amp / (nx.std() + 1e-6)
        ny *= amp / (ny.std() + 1e-6)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        a = cv2.remap(a, xx + nx, yy + ny, cv2.INTER_LINEAR)
        # density grain: pencil/ink tooth, streaky along a slight diagonal like the plate's pencil strokes
        g = rng.standard_normal((H, W)).astype(np.float32)
        g = cv2.GaussianBlur(g, (0, 0), sigmaX=cap * 0.06, sigmaY=cap * 0.015)
        g = (g - g.mean()) / (g.std() + 1e-6)
        dens = np.clip(1 - tex.get("grain", 0.12) * (1 + g) / 2 * 1.6, tex.get("min_density", 0.75), 1)
        a = a * dens
    # tight cap box (by the un-textured coverage threshold)
    ys, xs_ = np.nonzero(a > 0.35)
    return a[ys.min():ys.max() + 1, xs_.min():xs_.max() + 1].copy()


# ---------------------------------------------------------------- 4. geometry
class Mesh:
    """text space (u, v) in dot radii -> frame px. u along the baseline (0 = under the dot centre), v down from the
    dot centre. Rigid part: rotate by tilt, scale by the dot's semi-diameters. Flexible part: the hem's deviation from
    its tangent, blended in from the dot's bottom edge (v = 1) to the hem (v = hdist / sy)."""

    def __init__(self, d, spec):
        self.d = d
        th = math.radians(d["rot"])
        self.R = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
        self.c = np.array(d["c"])
        self.sx, self.sy = d["sx"], d["sy"]
        self.vh = max(d["hdist"] / self.sy, 1.3)
        self.flex = spec.get("flex", 1.0)

    def fwd(self, u, v):
        x = self.c[0] + self.R[0, 0] * u * self.sx + self.R[0, 1] * v * self.sy
        y = self.c[1] + self.R[1, 0] * u * self.sx + self.R[1, 1] * v * self.sy
        w = np.clip((v - 1.0) / (self.vh - 1.0), 0, 1.2) * self.flex
        dx = x - self.c[0]
        y = y + w * self.d["curv"] * dx ** 2         # quadratic term of the hem, measured about the dot's x
        return x, y


def text_box(spec, art):
    ah, aw = art.shape
    tw = spec.get("width", 2.1)
    return tw, tw * ah / aw, 1.0 + spec.get("gap", 0.28)       # width, cap height (dot radii), cap top (v)


def lattice_uv(spec, art):
    """control lattice in text space (nv x nu), a margin around the cap box"""
    tw, th_, top = text_box(spec, art)
    nu, nv = spec.get("lattice", [9, 3])
    m = spec.get("lattice_margin", 0.25)
    return np.meshgrid(np.linspace(-tw / 2 - m, tw / 2 + m, nu), np.linspace(top - m, top + th_ + m, nv))


class Lattice:
    """text space -> frame px through the flow-tracked control lattice P (nv x nu x 2): bilinear inside the lattice,
    linear extrapolation outside. `geo` (the dot/hem Mesh) is only used as the starting guess for the inverse."""

    def __init__(self, P, U, V, geo):
        self.P, self.geo = P, geo
        self.u0, self.du = U[0, 0], U[0, 1] - U[0, 0]
        self.v0, self.dv = V[0, 0], V[1, 0] - V[0, 0]
        self.R, self.c, self.sx, self.sy = geo.R, geo.c, geo.sx, geo.sy

    def fwd(self, u, v):
        nv, nu = self.P.shape[:2]
        fu = (u - self.u0) / self.du
        fv = (v - self.v0) / self.dv
        iu = np.clip(np.floor(fu), 0, nu - 2).astype(int)
        iv = np.clip(np.floor(fv), 0, nv - 2).astype(int)
        a = fu - iu
        b = fv - iv
        P = self.P
        out = []
        for k in range(2):
            p00, p01 = P[iv, iu, k], P[iv, iu + 1, k]
            p10, p11 = P[iv + 1, iu, k], P[iv + 1, iu + 1, k]
            out.append((1 - b) * ((1 - a) * p00 + a * p01) + b * ((1 - a) * p10 + a * p11))
        return out[0], out[1]


def _poly_fit(U, V, D):
    """low-order smooth model of the lattice displacement (constant, linear, u^2, uv): no per-point wobble"""
    u, v = U.ravel(), V.ravel()
    A = np.stack([np.ones_like(u), u, v, u * u, u * v], 1)
    out = np.zeros_like(D.reshape(-1, 2))
    for k in range(2):
        coef, *_ = np.linalg.lstsq(A, D.reshape(-1, 2)[:, k], rcond=None)
        out[:, k] = A @ coef
    return out.reshape(D.shape)


def _flow_at(f0, f1, P, spec):
    """Farneback flow f0 -> f1 sampled at the points P (… x 2), averaged over jacket pixels near each point"""
    pad = 40
    X0, Y0 = int(max(P[..., 0].min() - pad, 0)), int(max(P[..., 1].min() - pad, 0))
    X1, Y1 = int(P[..., 0].max() + pad), int(P[..., 1].max() + pad)
    g0 = cv2.cvtColor(f0[Y0:Y1, X0:X1], cv2.COLOR_RGB2GRAY)
    g1 = cv2.cvtColor(f1[Y0:Y1, X0:X1], cv2.COLOR_RGB2GRAY)
    fl = cv2.calcOpticalFlowFarneback(g0, g1, None, 0.5, 3, spec.get("flow_win", 21), 5, 7, 1.5, 0)
    # weight: jacket-white only (hair blowing past must not drag the lettering)
    w = masks(f0[Y0:Y1, X0:X1].astype(np.float32), spec) + 1e-3
    r = spec.get("flow_radius", 6)
    num = np.stack([cv2.boxFilter(fl[..., k] * w, -1, (2 * r + 1, 2 * r + 1)) for k in range(2)], -1)
    den = cv2.boxFilter(w, -1, (2 * r + 1, 2 * r + 1))[..., None]
    fl = num / den
    mx = (P[..., 0] - X0).astype(np.float32)
    my = (P[..., 1] - Y0).astype(np.float32)
    return np.stack([cv2.remap(fl[..., k], mx, my, cv2.INTER_LINEAR) for k in range(2)], -1)


def flow_lattice(clip, tr, spec, art):
    """per frame: control points that ride the cloth. Each pass chains the plate's optical flow at the lattice points
    (smoothed to a low-order field), with a leaky pull (k) toward the dot/hem geometry so it cannot drift; a forward and a
    backward pass are averaged (zero lag). Returns {frame: P}."""
    U, V = lattice_uv(spec, art)
    imgs = list(frames(clip))
    n = len(imgs)
    geo = {i: np.stack(Mesh(tr[i], spec).fwd(U, V), -1) for i in range(n) if tr[i]}
    k = spec.get("flow_k", 0.2)
    passes = []
    for order in (range(n), range(n - 1, -1, -1)):
        P, prev, res = None, None, {}
        for i in order:
            if i not in geo:
                P, prev = None, None
                continue
            if P is None:
                P = geo[i].copy()
            else:
                D = _flow_at(imgs[prev], imgs[i], P, spec)
                P = P + _poly_fit(U, V, D)
                P = P + k * (geo[i] - P)
            res[i] = P.copy()
            prev = i
        passes.append(res)
    out = {i: 0.5 * (passes[0][i] + passes[1][i]) for i in geo}
    return out, geo, U, V


def render_cov(shape, d, spec, art):
    """coverage of the lettering in frame px (float32 HxW crop) and its box"""
    H, W = shape
    ah, aw = art.shape
    tw, th_, top = text_box(spec, art)
    mesh = Mesh(d, spec)
    if d.get("P") is not None:
        U, V = lattice_uv(spec, art)
        mesh = Lattice(d["P"], U, V, mesh)
    # forward-map a fine grid of text space, then invert by scattering into a supersampled canvas via remap of the
    # inverse: build the inverse with a dense forward grid and cv2.remap on its (u,v) lookup
    nu, nv = 160, 40
    uu, vv = np.meshgrid(np.linspace(-tw / 2 - 0.15, tw / 2 + 0.15, nu), np.linspace(top - 0.15, top + th_ + 0.15, nv))
    X, Y = mesh.fwd(uu, vv)
    bx0, by0 = int(np.floor(X.min())) - 3, int(np.floor(Y.min())) - 3
    bx1, by1 = int(np.ceil(X.max())) + 4, int(np.ceil(Y.max())) + 4
    bx0, by0, bx1, by1 = max(bx0, 0), max(by0, 0), min(bx1, W), min(by1, H)
    SS = 4
    # inverse map by Newton iterations from the rigid inverse (the flex term is small and smooth)
    yy, xx = np.mgrid[0:(by1 - by0) * SS, 0:(bx1 - bx0) * SS].astype(np.float64)
    px = (xx + 0.5) / SS + bx0
    py = (yy + 0.5) / SS + by0
    Ri = mesh.R.T
    u = (Ri[0, 0] * (px - mesh.c[0]) + Ri[0, 1] * (py - mesh.c[1])) / mesh.sx
    v = (Ri[1, 0] * (px - mesh.c[0]) + Ri[1, 1] * (py - mesh.c[1])) / mesh.sy
    for _ in range(10):
        fx, fy = mesh.fwd(u, v)
        ex, ey = px - fx, py - fy
        u += (Ri[0, 0] * ex + Ri[0, 1] * ey) / mesh.sx
        v += (Ri[1, 0] * ex + Ri[1, 1] * ey) / mesh.sy
    mx = ((u + tw / 2) / tw * aw).astype(np.float32)
    my = ((v - top) / th_ * ah).astype(np.float32)
    cov = cv2.remap(art, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    cov = cv2.resize(cov, (bx1 - bx0, by1 - by0), interpolation=cv2.INTER_AREA)
    if spec.get("soft", 0) > 0:
        cov = cv2.GaussianBlur(cov, (0, 0), spec["soft"])
    return cov, (bx0, by0, bx1, by1)


def masks(a, spec):
    """jacket-white weight and hair/outline exclusion for a crop (float RGB)"""
    lum = a.mean(-1)
    chroma = a.max(-1) - a.min(-1)
    wj = np.clip((lum - spec.get("lum_lo", 95)) / 35, 0, 1) * np.clip((spec.get("chroma_hi", 48) - chroma) / 14, 0, 1)
    dark = np.clip((spec.get("hair_lum", 75) + 15 - lum) / 30, 0, 1)
    dark = cv2.dilate(dark, np.ones((3, 3), np.uint8))
    dark = cv2.GaussianBlur(dark, (0, 0), 0.6)
    return wj * (1 - np.clip(dark, 0, 1))


def letter(img, spec, d, art):
    cov, (bx0, by0, bx1, by1) = render_cov(img.shape[:2], d, spec, art)
    a = img[by0:by1, bx0:bx1].astype(np.float32)
    m = masks(a, spec)
    lum = a.mean(-1)
    chroma = a.max(-1) - a.min(-1)
    # local jacket white around the box (upper quartile of the bright, unsaturated fabric)
    wpx = a[(lum > 150) & (chroma < 30)]
    wref = np.percentile(wpx, 80, axis=0) if len(wpx) > 30 else np.array([225, 215, 220], np.float32)
    ink = np.array(spec.get("ink", [52, 51, 56]), np.float32)
    kf = np.clip(ink / np.maximum(wref, 1), 0, 1)
    al = (cov * m)[..., None]
    a = a * (1 - al) + a * kf * al
    out = img.copy()
    out[by0:by1, bx0:bx1] = np.clip(a + 0.5, 0, 255).astype(np.uint8)
    full = np.zeros(img.shape[:2], np.float32)
    full[by0:by1, bx0:bx1] = cov
    return out, full, cov * m, (bx0, by0, bx1, by1)


# ---------------------------------------------------------------- 5. diagnostics / sheets
def _label_font():
    return ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 20)


def song(i, spec):
    t = spec["song_in"] + (i / 24.0 - spec["clip_in"]) / spec.get("rate", 1.0)
    return t, t * 24


def mss(t):
    return "%d:%05.2f" % (int(t // 60), t - 60 * int(t // 60))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--track-only", action="store_true")
    ap.add_argument("--sheet", help="a:b every-frame crop sheets from the ENCODED output (or the plate with --live)")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--compare", help="comma list of src frames for before/after tiles")
    ap.add_argument("--crop", default="200x150")
    ap.add_argument("--zoom", type=float, default=3)
    ap.add_argument("--cols", type=int, default=6)
    ap.add_argument("--per", type=int, default=24)
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--name", default="every_frame")
    a = ap.parse_args()
    spec = json.load(open(a.spec))
    clip = os.path.join(ROOT, spec["clip"])
    tr = normalise(track(clip, spec), spec)
    art = glyphs(spec)
    if spec.get("flow", True):
        lat, geo, U, V = flow_lattice(clip, tr, spec, art)
        for i, P in lat.items():
            tr[i]["P"] = P
    if a.track_only:
        imgs = list(frames(clip))
        for i, d in enumerate(tr):
            if d is None:
                print(i, None)
                continue
            raw = d["raw"]
            t, sf = song(i, spec)
            line = "%3d %s f%.0f c=(%.1f,%.1f) s=(%.1f,%.1f) rot=%.1f curv=%.5f hdist=%.1f vis=%.2f hem=%s" % (
                i, mss(t), sf, *d["c"], d["sx"], d["sy"], d["rot"], d["curv"], d["hdist"], raw["vis"],
                raw["hem"]["n"] if raw["hem"] else None)
            if d.get("P") is not None:
                dev = np.hypot(*(d["P"] - geo[i]).transpose(2, 0, 1))
                line += " |lattice-geo| mean %.2f max %.2f" % (dev.mean(), dev.max())
                if i > 0 and tr[i - 1] is not None:
                    # slide vs the cloth: plate flow at last frame's points minus how the points moved (px, median)
                    Dl = _flow_at(imgs[i - 1], imgs[i], tr[i - 1]["P"], spec)
                    Dg = _flow_at(imgs[i - 1], imgs[i], geo[i - 1], spec)
                    sl = np.median(np.hypot(*(Dl - (d["P"] - tr[i - 1]["P"])).transpose(2, 0, 1)))
                    sg = np.median(np.hypot(*(Dg - (geo[i] - geo[i - 1])).transpose(2, 0, 1)))
                    line += " slide lattice %.2f geo-only %.2f" % (sl, sg)
            print(line)
        return
    cw, ch = (int(v) for v in a.crop.split("x"))
    if a.sheet or a.compare:
        os.makedirs(a.outdir, exist_ok=True)
        src_frames = list(frames(clip))
        if a.sheet:
            s0, s1 = (int(v) for v in a.sheet.split(":"))
            enc = list(frames(os.path.join(ROOT, spec["out"]))) if not a.live else None
            want = list(range(s0, s1 + 1))
            for k in range(0, len(want), a.per):
                chunk = want[k:k + a.per]
                tiles = []
                for i in chunk:
                    d = tr[i]
                    img = enc[i] if enc is not None else (letter(src_frames[i], spec, d, art)[0] if d else src_frames[i])
                    cx, cy = d["c"] if d else (1465, 560)
                    cy += (d["sy"] * 1.0 if d else 0)
                    bx = (int(cx - cw / 2), int(cy - ch / 2), int(cx - cw / 2) + cw, int(cy - ch / 2) + ch)
                    im = Image.fromarray(img).crop(bx).resize((int(cw * a.zoom), int(ch * a.zoom)), Image.LANCZOS)
                    t, sf = song(i, spec)
                    used = spec["used"][0] <= i <= spec["used"][1]
                    ImageDraw.Draw(im).text((5, 4), "src %d  song %s f%.0f%s" % (i, mss(t), sf, "" if used else "  (spare)"),
                                            fill=(255, 255, 0) if used else (170, 170, 170), font=_label_font(),
                                            stroke_width=2, stroke_fill=(0, 0, 0))
                    tiles.append(im)
                w, h = tiles[0].size
                rows = (len(tiles) + a.cols - 1) // a.cols
                sheet = Image.new("RGB", (w * a.cols, h * rows))
                for j, t_ in enumerate(tiles):
                    sheet.paste(t_, ((j % a.cols) * w, (j // a.cols) * h))
                p = os.path.join(a.outdir, "%s_src%03d-%03d.jpg" % (a.name, chunk[0], chunk[-1]))
                sheet.save(p, quality=90)
                print(p)
        if a.compare:
            enc = list(frames(os.path.join(ROOT, spec["out"])))
            for i in (int(v) for v in a.compare.split(",")):
                d = tr[i]
                t, sf = song(i, spec)
                tag = mss(t).replace(":", "m").replace(".", "_")
                cx, cy = d["c"]
                cy += d["sy"]
                # wide context (1:1 at 1080p around her) + zoomed crop, before | after
                parts = []
                for (W_, H_, z) in ((560, 420, 1), (cw, ch, a.zoom)):
                    bx = (int(cx - W_ / 2), int(cy - H_ / 2), int(cx - W_ / 2) + W_, int(cy - H_ / 2) + H_)
                    pair = []
                    for lab, im in (("before", src_frames[i]), ("after", enc[i])):
                        t_ = Image.fromarray(im).crop(bx).resize((int(W_ * z), int(H_ * z)), Image.LANCZOS)
                        ImageDraw.Draw(t_).text((5, 4), "%s  src %d  song %s f%.0f  %s" % (
                            lab, i, mss(t), sf, "1:1" if z == 1 else "%gx" % z), fill=(255, 255, 0), font=_label_font(),
                            stroke_width=2, stroke_fill=(0, 0, 0))
                        pair.append(t_)
                    parts.append(pair)
                Wt = max(sum(p.size[0] for p in pr) for pr in parts)
                Ht = sum(pr[0].size[1] for pr in parts)
                sheet = Image.new("RGB", (Wt, Ht))
                y = 0
                for pr in parts:
                    x = 0
                    for p in pr:
                        sheet.paste(p, (x, y))
                        x += p.size[0]
                    y += pr[0].size[1]
                p = os.path.join(a.outdir, "before_after_%s.jpg" % tag)
                sheet.save(p, quality=92)
                print(p)
        return
    c = av.open(clip)
    s = c.streams.video[0]
    W, H, fps = s.width, s.height, s.average_rate
    c.close()
    out = os.path.join(ROOT, spec["out"])
    tmp = out + ".tmp.mp4"
    enc = subprocess.Popen([FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(fps), "-i", "-", "-c:v", "libx264", "-crf", str(spec.get("crf", 13)),
                            "-preset", "slow", "-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart",
                            tmp], stdin=subprocess.PIPE)
    n = done = 0
    for i, img in enumerate(frames(clip)):
        if tr[i] is not None:
            img = letter(img, spec, tr[i], art)[0]
            done += 1
        enc.stdin.write(img.tobytes())
        n += 1
    enc.stdin.close()
    enc.wait()
    if enc.returncode:
        raise SystemExit("ffmpeg failed")
    os.replace(tmp, out)
    print(out, n, "frames,", done, "lettered")


if __name__ == "__main__":
    main()
