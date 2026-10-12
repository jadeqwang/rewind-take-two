#!/usr/bin/env python3
"""v5 note 0:13 & 2:35 (Jade): the rooftop stairwell left of the singer becomes a real impossible (Penrose) staircase.

    PY=~/Documents/moongazing/.venv/bin/python
    $PY tools/v5/stairs/penrose.py guide g16        # free: the drawn stair (defaults P = the picked one) -> media/sing/plates/stairs_v5/
    $PY tools/v5/stairs/comp.py g16_onplate.png g16 --wide   # then lay it into the plate, both takes and the S1 wide

The stair is a real 3-D object drawn by an orthographic camera and a z-buffer, so occlusion is honest. Every step is a
column standing on the roof; the four flights climb all the way round, and the loop closes in the picture only because
the path's end is pushed along the camera's view axis by exactly the total climb (the Penrose/Escher "magic angle").

Camera: fitted to the old square stairwell's top face in media/sing/plates/plate_close_1.jpg (corners L (137,1242),
T (215,1122), R (362,1187), B (290,1310) plate px; a scaled orthographic fit gives ~55 deg elevation), then lowered to
EL deg with the same azimuth and roll: at the roof's own steep view the risers are too foreshortened to read, and the
classic figure wants a lower, diagonal view (the stair is turned YAW off the camera so two flights face it).
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.chdir(ROOT)
OUT = "media/sing/plates/stairs_v5"
CLOSE = "media/sing/plates/plate_close_1.jpg"

# --- the roof's camera (plate px = O + M @ (u, v, w)); u, v on the roof in units of the old stairwell's side ----------
O_ROOF = np.array([137.0, 1242.0])
A = np.array([75.0, -121.5]); B = np.array([150.0, 66.5])     # L -> T, L -> B
_r1, _r2 = np.array([A[0], B[0]]), np.array([A[1], B[1]])
_p, _q = _r1 @ _r2, (_r2 @ _r2) - (_r1 @ _r1)
_Z0 = np.sqrt((_q + np.sqrt(_q * _q + 4 * _p * _p)) / 2); _Z1 = -_p / _Z0
if _Z1 > 0: _Z0, _Z1 = -_Z0, -_Z1                               # up points up the picture
M_ROOF = np.array([[A[0], B[0], _Z0], [A[1], B[1], _Z1]])
SCALE = np.linalg.norm(M_ROOF[0])                               # plate px per unit
_n = np.cross(M_ROOF[0], M_ROOF[1]); TOCAM_ROOF = _n / np.linalg.norm(_n) * np.sign(_n[2])
EL_ROOF = np.degrees(np.arcsin(TOCAM_ROOF[2]))
ROLL = np.degrees(np.arctan2(_Z0, -_Z1))                        # world up leans this many deg right of image-up
CENTRE_IMG = O_ROOF + M_ROOF[:, :2] @ [0.5, 0.5]                # the old stairwell's centre on the roof (plate px)


def camera(el, roll=ROLL, scale=SCALE):
    """2x3 scaled orthographic projection with the roof's azimuth, elevation el deg; returns (M, tocam)"""
    ch = TOCAM_ROOF[:2] / np.linalg.norm(TOCAM_ROOF[:2])
    e = np.radians(el)
    tc = np.array([np.cos(e) * ch[0], np.cos(e) * ch[1], np.sin(e)])
    ex = np.array([ch[1], -ch[0], 0.0])                          # horizontal, perpendicular to the view
    ey = np.cross(tc, ex)                                        # image down
    if ey[2] > 0: ex, ey = -ex, -ey                              # world up must map to image up (ey . up < 0)
    if np.cross(ex, ey) @ tc < 0: ex = -ex; ey = np.cross(tc, ex)
    if ey[2] > 0: ey = -ey
    # match the roof camera's handedness: its L->T axis (u) must go the same way across the picture
    if np.sign(ex[0]) != np.sign(M_ROOF[0, 0] / SCALE): ex = -ex
    r = np.radians(roll)
    ex2 = np.cos(r) * ex - np.sin(r) * ey; ey2 = np.sin(r) * ex + np.cos(r) * ey
    M = scale * np.array([ex2, ey2])
    if (M @ [0, 0, 1])[0] * (M_ROOF @ [0, 0, 1])[0] < 0:          # roll the other way if the lean came out mirrored
        ex2 = np.cos(r) * ex + np.sin(r) * ey; ey2 = -np.sin(r) * ex + np.cos(r) * ey
        M = scale * np.array([ex2, ey2])
    n = np.cross(M[0], M[1]); n = n / np.linalg.norm(n) * np.sign(n @ tc)
    return M, n


# --- the stair (local frame x, y on the roof, w up; units = the old stairwell's side) ------------------------------------
P = dict(el=46.0, yaw=45.0, hand=-1, size=0.97, ring=0.30, steps=(6, 5, 6, 5), rise=0.05, base=0.04, dx=0.0, dy=0.0,
         ox=64.0, oy=52.0)                                   # the picked stair (g16); ox, oy = plate px offset from the old stairwell


def build(p, tocam):
    """columns: (footprint quad in world u,v (4x2), top w, kind, k, travel dir). Corner landings + steps; the footprint
    is left open by g = H * (N_u, N_v) (N = view axis scaled to w = 1) so that the picture of the loop closes."""
    ch = tocam[:2] / np.linalg.norm(tocam[:2])
    a = np.radians(180 + p["yaw"])                               # side 1 runs away from the camera, turned yaw
    xh = np.array([np.cos(a) * ch[0] - np.sin(a) * ch[1], np.sin(a) * ch[0] + np.cos(a) * ch[1]])
    yh = np.array([-xh[1], xh[0]]) * p.get("hand", 1)            # hand -1: the loop turns the other way
    s, wR = p["size"], p["ring"]
    n1, n2, n3, n4 = p["steps"]
    cnt = n1 + n2 + n3 + n4 + 4
    h = p["rise"]; H = cnt * h
    Nv = tocam / tocam[2]
    g = H * Nv[:2]                                               # world (u, v): footprint end - start
    gx, gy = g @ xh, g @ yh
    L1 = L2 = s - wR
    L3 = L1 - gx; L4 = L2 - gy
    # centre the picture of the loop's footprint on the roof's old stairwell: centre-line start such that the mean of
    # the four corners is at the local origin
    cc = np.array([[0, 0], [L1, 0], [L1, L2], [L1 - L3, L2]])
    st = -cc.mean(0)
    cols = []
    k = 0
    hw = wR / 2
    x, y = st
    corners = []
    for side, (dx, dy) in enumerate([(1, 0), (0, 1), (-1, 0), (0, -1)]):
        L = (L1, L2, L3, L4)[side]; n = p["steps"][side]
        px, py = -dy, dx
        quads = [([(x - hw, y - hw), (x + hw, y - hw), (x + hw, y + hw), (x - hw, y + hw)], "landing")]
        a0, a1 = hw, L - hw
        for i in range(n):
            t0 = a0 + (a1 - a0) * i / n; t1 = a0 + (a1 - a0) * (i + 1) / n
            c0 = (x + dx * t0, y + dy * t0); c1 = (x + dx * t1, y + dy * t1)
            quads.append(([(c0[0] + px * hw, c0[1] + py * hw), (c1[0] + px * hw, c1[1] + py * hw),
                           (c1[0] - px * hw, c1[1] - py * hw), (c0[0] - px * hw, c0[1] - py * hw)], "step"))
        for q, kind in quads:
            k += 1
            wq = np.array([[p["dx"] + qx * xh[0] + qy * yh[0], p["dy"] + qx * xh[1] + qy * yh[1]] for qx, qy in q])
            cols.append((wq, p["base"] + k * h, kind, k, dx * xh + dy * yh))
        corners.append([p["dx"] + x * xh[0] + y * yh[0], p["dy"] + x * xh[1] + y * yh[1]])
        x += dx * L; y += dy * L
    corners.append([p["dx"] + x * xh[0] + y * yh[0], p["dy"] + x * xh[1] + y * yh[1]])
    return cols, dict(H=H, h=h, g=g.tolist(), lens=[L1, L2, L3, L4], xh=xh.tolist(), yh=yh.tolist(), corners=corners)


SS = 3                                                          # supersampling


def _inside(pt, quad):
    sgn = []
    for i in range(4):
        a, b = quad[i], quad[(i + 1) % 4]
        sgn.append((b[0] - a[0]) * (pt[1] - a[1]) - (b[1] - a[1]) * (pt[0] - a[0]))
    return all(x > 0 for x in sgn) or all(x < 0 for x in sgn)


def faces(cols):
    """planar quads (3-D) with a type. A side face shared with a neighbouring column only shows above that neighbour's
    top (below it the face is inside the masonry); the two ends of the loop are not neighbours (the seam's gap)."""
    out = []
    for quad, top, kind, k, tdir in cols:
        q = [np.array([u, v, 0.0]) for u, v in quad]
        out.append(([qq + [0, 0, top] for qq in q], "top", k, np.array([0, 0, 1.0]), tdir))
        c = np.mean(q, 0)
        for i in range(4):
            a, b = q[i], q[(i + 1) % 4]
            e = b - a
            nrm = np.array([e[1], -e[0], 0.0]); nrm /= np.linalg.norm(nrm) + 1e-12
            if nrm @ (a - c) < 0: nrm = -nrm
            mid = (a + b) / 2 + nrm * 1e-4
            bot = 0.0
            for q2, top2, _, k2, _ in cols:
                if k2 != k and _inside(mid[:2], q2): bot = max(bot, top2)
            if bot >= top - 1e-9: continue
            z0 = np.array([0, 0, bot])
            out.append(([a + z0, b + z0, b + [0, 0, top], a + [0, 0, top]], "riser" if abs(nrm[:2] @ tdir) > 0.7 else "wall", k, nrm, tdir))
    return out


def render(cols, M, tocam, origin, box, floor=None):
    x0, y0, x1, y1 = box
    W, Hh = (x1 - x0) * SS, (y1 - y0) * SS
    depth = np.full((Hh, W), -1e9, np.float32)
    fid = np.full((Hh, W), -1, np.int32)
    hgt = np.zeros((Hh, W), np.float32); along = np.zeros((Hh, W), np.float32)
    yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
    px = x0 + (xx + 0.5) / SS; py = y0 + (yy + 0.5) / SS
    meta = []
    pr = lambda P3: origin + (M @ np.asarray(P3, float).T).T
    F = faces(cols)
    if floor is not None: F = [(floor, "floor", 0, np.array([0, 0, 1.0]), np.zeros(2))] + F
    for pts, ftype, k, nrm, tdir in F:
        if nrm @ tocam <= 1e-6: continue
        pts = np.array(pts); img = pr(pts)
        m = Image.new("L", (W, Hh), 0)
        ImageDraw.Draw(m).polygon([((x - x0) * SS, (y - y0) * SS) for x, y in img], fill=255)
        m = np.asarray(m) > 0
        if not m.any(): continue
        p0, e1, e2 = pts[0], pts[1] - pts[0], pts[3] - pts[0]
        Ji = np.linalg.inv(np.stack([M @ e1, M @ e2], 1))
        d0 = img[0]
        rx, ry = px[m] - d0[0], py[m] - d0[1]
        s = Ji[0, 0] * rx + Ji[0, 1] * ry; t = Ji[1, 0] * rx + Ji[1, 1] * ry
        P3 = p0[None] + s[:, None] * e1[None] + t[:, None] * e2[None]
        dep = P3 @ tocam
        if ftype == "floor": dep = dep - 1e3                      # the courtyard floor is behind everything
        win = dep > depth[m]
        iy, ix = np.where(m); sel = (iy[win], ix[win])
        depth[sel] = dep[win]; fid[sel] = len(meta)
        hgt[sel] = P3[win, 2]
        along[sel] = (P3[win, :2] @ np.array([-nrm[1], nrm[0]])) if ftype != "top" else 0
        plane = (tuple(np.round(nrm, 3)), round(float(nrm @ p0), 3))
        meta.append(dict(type=ftype, k=k, nrm=nrm, plane=plane))
    return fid, depth, hgt, along, meta


LIGHT = np.array([-0.45, -0.75, 0.5])                          # set per stair below (light from the picture's upper left)


def ink(fid, hgt, along, meta, light):
    Hh, W = fid.shape
    out = np.ones((Hh, W), np.float32)
    yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
    for j, m in enumerate(meta):
        sel = fid == j
        if not sel.any() or m["type"] == "top": continue
        if m["type"] == "floor":
            out[sel] = 0.0; continue                           # the courtyard: in deep shadow
        lit = m["nrm"] @ light
        hs, al = hgt[sel], along[sel]
        if m["type"] == "riser":                               # risers: close horizontal lines, near solid in shade
            out[sel] = np.where(((hs / 0.018) % 1) < (0.6 if lit > 0.15 else 0.85), 0.0, 1.0)
            continue
        # walls: engraved masonry. Horizontal courses every 0.05 (about 4.5 plate px), staggered joints; walls turned
        # from the light get heavier courses and vertical hatching; the darkest (the seam's end face) dense cross-hatch
        course = 0.05
        c = (hs / course) % 1
        duty = 0.16 if lit > 0.2 else (0.38 if lit > -0.2 else 0.55)
        lines = c < duty
        joint = ((al / 0.11 + 0.5 * (np.floor(hs / course) % 2)) % 1) < (0.035 if lit > 0.2 else 0.08)
        val = np.where(lines | joint, 0.0, 1.0)
        if lit < -0.2:
            val = np.minimum(val, np.where((xx[sel] / SS) % 3.0 < (1.3 if lit > -0.35 else 2.0), 0.0, 1.0))
        out[sel] = val
    # outlines where the plane changes
    pk = np.full(fid.shape, -1, np.int64)
    planes = {}
    for j, m in enumerate(meta):
        pk[fid == j] = planes.setdefault(m["plane"], len(planes))
    e = np.zeros(fid.shape, bool)
    d1 = pk[:, 1:] != pk[:, :-1]; d2 = pk[1:, :] != pk[:-1, :]
    e[:, 1:] |= d1; e[:, :-1] |= d1; e[1:, :] |= d2; e[:-1, :] |= d2
    e = np.asarray(Image.fromarray(e.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(5))) > 0
    out[e] = 0.0
    return out


def draw(p=None, name="penrose"):
    p = {**P, **(p or {})}
    M, tocam = camera(p["el"])
    cols, info = build(p, tocam)
    origin = CENTRE_IMG + np.array([p.get("ox", 0.0), p.get("oy", 0.0)])
    pts = []
    for quad, top, *_ in cols:
        for u, v in quad: pts += [origin + M @ [u, v, 0], origin + M @ [u, v, top]]
    pts = np.array(pts); pad = 8
    box = (int(pts[:, 0].min()) - pad, int(pts[:, 1].min()) - pad, int(pts[:, 0].max()) + pad, int(pts[:, 1].max()) + pad)
    # courtyard floor: the ring's footprint at roof level (its outer hull), drawn behind everything
    floor = [np.array([u, v, 0.0]) for u, v in info["corners"]]
    fid, depth, hgt, along, meta = render(cols, M, tocam, origin, box, floor=floor)
    light = np.array([-tocam[1], tocam[0], 0.0]) * 0.0 + np.array([*(tocam[:2] / np.linalg.norm(tocam[:2]) @ np.array([[np.cos(0.9), np.sin(0.9)], [-np.sin(0.9), np.cos(0.9)]])), 0.4])
    im = ink(fid, hgt, along, meta, light)
    size = (box[2] - box[0], box[3] - box[1])
    gray = Image.fromarray((im * 255).astype(np.uint8)).resize(size, Image.LANCZOS)
    alpha = Image.fromarray(((fid >= 0) * 255).astype(np.uint8)).resize(size, Image.LANCZOS)
    rgba = Image.merge("RGBA", (gray, gray, gray, alpha))
    return rgba, box, dict(params=p, info=info, M=M.tolist(), tocam=tocam.tolist(), origin=origin.tolist(), box=box,
                           el_roof=float(EL_ROOF), roll=float(ROLL))


def guide(name="penrose", **kw):
    os.makedirs(OUT, exist_ok=True)
    rgba, box, meta = draw(kw, name)
    rgba.save(f"{OUT}/{name}_draw.png")
    json.dump(meta, open(f"{OUT}/{name}_draw.json", "w"), indent=1, default=float)
    pl = Image.open(CLOSE).convert("RGBA")
    pl.alpha_composite(rgba, (box[0], box[1]))
    pl.convert("RGB").crop((0, 768, 1024, 1536)).save(f"{OUT}/{name}_onplate.png")
    print("wrote", f"{OUT}/{name}_draw.png", "box", box, "H %.2f" % meta["info"]["H"], "roof el %.1f roll %.1f" % (EL_ROOF, ROLL))
    return rgba, box


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    o = {k: (tuple(int(n) for n in v.split(",")) if k == "steps" else float(v))
         for k, v in (x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--"))}
    if not a or a[0] == "guide":
        guide(a[1] if len(a) > 1 else "penrose", **o)
    else:
        sys.exit(__doc__)
