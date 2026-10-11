#!/usr/bin/env python3
"""v4 gunfire blockout (notes 1:39 and 1:41): grey-box stills of the two new lawn shots, drawn from one 3D layout.

    ~/Documents/moongazing/.venv/bin/python tools/v4B/gunfire/blockout.py            # stills, plans, contact sheet
    ~/Documents/moongazing/.venv/bin/python tools/v4B/gunfire/blockout.py --t 99.82  # one extra still at a song time

Everything is placed in metres on a flat lawn (x right, y up, z away from the firing line toward the hotel) and
drawn through a pinhole camera, so positions, distances, barrel lines and tracer lines are what the layout says.
A tracer is the straight 3D line from a muzzle to the point where she was `lag` s before the shot (v3's rule); the
firing agent's arms and pistol are posed on that same line. Layout, camera keys and shot times are in the block below
and are written to media/reviews/v4/B/plans/gunfire/geometry.json with the screen positions of every muzzle and
impact, for the build. Plan: docs/revisions/v4/plans/gunfire.md. No generation, no engine, no GPU.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = "/home/jade/Documents/rewind-take-two"
OUT = os.path.join(ROOT, "media/reviews/v4/B/plans/gunfire")
ANTON = os.path.join(ROOT, "render/fonts/anton-latin-400-normal.woff2")
MONO = os.path.join(ROOT, "render/fonts/IBMPlexMono-Bold.ttf")
W, H, SS = 960, 540, 2                      # stills are 960x540, drawn at 2x and reduced
PAPER, INK, ORANGE, BLUE = "#ece7dc", "#0b0b0c", "#F08A24", "#8DB8E8"
LAWN, SUIT, SUIT2 = "#d3cfc2", "#2a2a2d", "#47474c"
LEAD = 0.33                                # traceMiss: the ruled line starts to draw LEAD s before the shot

# --------------------------------------------------------------------------------------------------------------
# The layout. Song seconds, metres. z = 0 is the firing line (agents A and B).
# --------------------------------------------------------------------------------------------------------------
# Jade: straight legs between turn points, every turn on a tracked beat. In G1 (wide lens) a leg lasts two beats, so
# the zigzag is 4.5 to 5 m wide; from 100.26 she cuts on every beat, as in v3, in a 2 m lane. She runs away at 4.1 m/s
# of depth and about 5 m/s across, i.e. a 6.5 m/s sprint. x drifts right, toward the hotel.
TURNS = [(97.62, -2.4), (98.50, 2.3), (99.38, -2.2), (100.26, 2.8), (100.70, 0.9), (101.14, 3.0), (101.58, 1.0),
         (102.00, 3.2), (102.46, 1.2), (102.90, 3.2), (103.34, 1.4), (103.76, 3.4), (104.22, 1.8), (104.66, 3.4)]
Z0, VZ = 19.0, 4.1                          # 19 m from the firing line at 98.28


def jade_at(t):
    for (t0, x0), (t1, x1) in zip(TURNS, TURNS[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / (t1 - t0)
            return np.array([x0 + (x1 - x0) * u, 0.0, Z0 + VZ * (t - 98.28)]), math.atan2((x1 - x0) / (t1 - t0), VZ)
    raise ValueError(t)


# Agents. A and B stand on the firing line; C is a few metres ahead and keeps walking forward as he fires.
def agent_pos(name, t):
    if name == "A":
        return np.array([-0.95, 0.0, 0.0])
    if name == "B":
        return np.array([1.25, 0.0, 0.3])
    # C: walks forward at 1.2 m/s as he fires, easing right; stops at 102.90 when he lowers the pistol
    return np.array([-1.3 + 0.19 * (min(t, 102.46) - 98.28), 0.0, 3.2 + 1.2 * (min(t, 102.90) - 98.28)])


GUN_HAND = {"A": +1, "B": -1, "C": +1}      # the pistol is in the hand on the camera's side, so it shows from behind
BLADE = {"A": -0.4, "B": 0.4, "C": -0.4}    # bladed stance: gun shoulder forward (radians of body turn)


# park notice board beyond her: she crosses in front of its plain lower band; the lyric is above her head (y >= ty0)
BOARD = dict(x0=-0.1, x1=4.1, z=46.0, y0=0.7, y1=3.5, ty0=1.72)
HOTEL = dict(corner=(29.0, 235.0), yaw=math.radians(-34), front=46.0, side=26.0, h=40.0)

SHOTS = {
    "G1": dict(t0=98.28, t1=100.70, title="G1  98.28-100.70  \"I zigzag\"  behind the firing line, push between A and B",
               # the shot always comes from the side she is running away from, so no line ever crosses her on screen:
               # she runs left until 99.38 (B, on the right, fires twice), then right (C, on the left, fires twice)
               fires=[(98.94, "B"), (99.38, "B"), (99.82, "C"), (100.26, "C")], callers={},
               lag=0.25,                    # each miss lands where she was a quarter second earlier (the v3 rule)
               ease="in",
               cam=[(98.28, (0.05, 1.78, -3.05), 0.0, 0.5, 47), (100.70, (-0.22, 1.68, 2.85), 0.6, 0.5, 27)],
               ground_text=dict(text="I ZIGZAG", quad=(-1.15, 2.75, 7.0, 16.5), words=[("I", 98.28), ("ZIG", 98.47), ("ZAG", 98.78)]),
               stills=[98.30, 98.94, 99.38, 99.82, 100.66]),
    "G2": dict(t0=100.70, t1=102.46, title="G2  100.70-102.46  \"across the field of\"  one fires, two call it in",
               fires=[(101.14, "C"), (102.00, "C")], callers={"A": (+1, 100.60), "B": (-1, 101.58)},
               lag=0.44,                    # she is further off: he is a whole beat behind, each miss lands on her last corner
               # long lens from well behind A and B, a slow creep in (Jade kept the 102.46 cut; G3, the earpiece
               # close-up 102.46-104.22, is a generated shot and is not blocked here)
               cam=[(100.70, (0.15, 1.50, -8.5), 0.4, -0.6, 18.5), (102.46, (0.15, 1.51, -8.2), 0.4, -0.6, 17.0)],
               board_text=[("ACROSS", 100.63), ("THE", 101.28), ("FIELD", 101.42), ("OF", 101.74)],
               stills=[100.74, 101.14, 101.58, 102.00, 102.42]),
}


# --------------------------------------------------------------------------------------------------------------
# camera
# --------------------------------------------------------------------------------------------------------------
def smooth(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


class Cam:
    def __init__(self, pos, yaw_deg, pitch_deg, hfov_deg, w=W * SS, h=H * SS):
        self.pos, self.yaw, self.pitch, self.hfov = np.array(pos, float), math.radians(yaw_deg), math.radians(pitch_deg), hfov_deg
        self.w, self.h = w, h
        self.f = (w / 2) / math.tan(math.radians(hfov_deg) / 2)

    def cam(self, P):                        # world -> camera space (x right, y up, z forward)
        d = np.asarray(P, float) - self.pos
        cy, sy, cp, sp = math.cos(self.yaw), math.sin(self.yaw), math.cos(self.pitch), math.sin(self.pitch)
        x, z = cy * d[0] - sy * d[2], sy * d[0] + cy * d[2]
        return np.array([x, cp * d[1] + sp * z, -sp * d[1] + cp * z])

    def px(self, c):
        return (self.w / 2 + self.f * c[0] / c[2], self.h / 2 - self.f * c[1] / c[2])

    def project(self, P):                    # -> (sx, sy, depth) or None behind the camera
        c = self.cam(P)
        return None if c[2] < 0.12 else (*self.px(c), c[2])

    def horizon(self):
        return self.h / 2 - self.f * math.tan(self.pitch)


def cam_at(shot, t):
    keys = shot["cam"]
    k = max(0, min(len(keys) - 2, sum(1 for c in keys[1:-1] if t >= c[0])))
    (ta, pa, ya, pia, fa), (tb, pb, yb, pib, fb) = keys[k], keys[k + 1]
    u = (t - ta) / (tb - ta)
    u = min(1.0, max(0.0, u))
    u = u * u if shot.get("ease") == "in" else u      # "in": starts slow behind them, accelerates through the gap
    lerp = lambda a, b: a + (b - a) * u
    # zoom is interpolated in log focal length so the push feels even
    fov = 2 * math.degrees(math.atan(math.exp(lerp(math.log(math.tan(math.radians(fa) / 2)), math.log(math.tan(math.radians(fb) / 2))))))
    return Cam([lerp(a, b) for a, b in zip(pa, pb)], lerp(ya, yb), lerp(pia, pib), fov)


# --------------------------------------------------------------------------------------------------------------
# a tiny painter's-algorithm renderer
# --------------------------------------------------------------------------------------------------------------
class Scene:
    def __init__(self, cam):
        self.cam, self.items = cam, []

    def clip(self, pts):                     # near-plane clip of a polygon given in camera space
        out, n = [], len(pts)
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            ina, inb = a[2] >= 0.12, b[2] >= 0.12
            if ina:
                out.append(a)
            if ina != inb:
                u = (0.12 - a[2]) / (b[2] - a[2])
                out.append(a + (b - a) * u)
        return out

    def poly(self, pts, fill, outline=None, width=1, bias=0.0):
        c = [self.cam.cam(p) for p in pts]
        depth = float(np.mean([p[2] for p in c])) + bias
        c = self.clip(c)
        if len(c) >= 3:
            self.items.append((depth, "poly", [self.cam.px(p) for p in c], fill, outline, width))

    def seg(self, a, b, wid, fill, bias=0.0):        # a 3D capsule drawn as a screen-facing strip with round ends
        ca, cb = self.cam.cam(a), self.cam.cam(b)
        if ca[2] < 0.12 and cb[2] < 0.12:
            return
        if ca[2] < 0.12:
            ca = ca + (cb - ca) * ((0.12 - ca[2]) / (cb[2] - ca[2]))
        if cb[2] < 0.12:
            cb = cb + (ca - cb) * ((0.12 - cb[2]) / (ca[2] - cb[2]))
        pa, pb = np.array(self.cam.px(ca)), np.array(self.cam.px(cb))
        ra, rb = self.cam.f * wid / 2 / ca[2], self.cam.f * wid / 2 / cb[2]
        self.items.append(((ca[2] + cb[2]) / 2 + bias, "seg", (pa, pb, ra, rb), fill, None, 0))

    def ball(self, c, r, fill, bias=0.0):
        cc = self.cam.cam(c)
        if cc[2] > 0.12:
            self.items.append((cc[2] + bias, "ball", (self.cam.px(cc), self.cam.f * r / cc[2]), fill, None, 0))

    def draw(self, d):
        for _, kind, g, fill, outline, width in sorted(self.items, key=lambda i: -i[0]):
            if kind == "poly":
                d.polygon(g, fill=fill, outline=outline, width=width) if outline else d.polygon(g, fill=fill)
            elif kind == "ball":
                (x, y), r = g
                d.ellipse([x - r, y - r, x + r, y + r], fill=fill)
            else:
                pa, pb, ra, rb = g
                v = pb - pa
                n = np.linalg.norm(v)
                nrm = np.array([-v[1], v[0]]) / n if n > 1e-6 else np.array([1.0, 0.0])
                d.polygon([tuple(pa + nrm * ra), tuple(pb + nrm * rb), tuple(pb - nrm * rb), tuple(pa - nrm * ra)], fill=fill)
                for p, r in ((pa, ra), (pb, rb)):
                    d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=fill)


def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def homography(src, dst):                    # 3x3 H with H*src = dst (4 point pairs)
    A, b = [], []
    for (x, y), (u, v) in zip(src, dst):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
        b += [u, v]
    return np.append(np.linalg.solve(np.array(A, float), np.array(b, float)), 1).reshape(3, 3)


def text_image(lines, color, height=220, track=0, bg=None, pad=0.12, fnt=ANTON):
    font = ImageFont.truetype(fnt, height)
    ws = [sum(font.getlength(ch) + track for ch in ln) for ln in lines]
    wid, lh = int(max(ws) * (1 + 2 * pad)) + 4, int(height * 1.22)
    im = Image.new("RGBA", (wid, int(lh * len(lines) + height * 2 * pad)), bg or (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k, ln in enumerate(lines):
        x = max(ws) * pad
        for ch in ln:
            d.text((x, height * pad + k * lh - height * 0.12), ch, font=font, fill=color)
            x += font.getlength(ch) + track
    return im


def paste_warp(img, tex, quad_px, below=None):        # tex corners TL, TR, BR, BL -> quad_px
    tw, th = tex.size
    Hm = homography(quad_px, [(0, 0), (tw, 0), (tw, th), (0, th)])       # screen -> texture
    warped = tex.transform(img.size, Image.PERSPECTIVE, (Hm / Hm[2, 2]).flatten()[:8], Image.BICUBIC)
    if below is not None:                    # keep only pixels below a screen row (the horizon)
        a = np.array(warped)
        a[: max(0, int(below))] = 0
        warped = Image.fromarray(a)
    img.alpha_composite(warped)


# --------------------------------------------------------------------------------------------------------------
# figures
# --------------------------------------------------------------------------------------------------------------
def frame(pos, facing):                      # facing: azimuth, 0 = +z
    f = np.array([math.sin(facing), 0, math.cos(facing)])
    r = np.array([math.cos(facing), 0, -math.sin(facing)])
    up = np.array([0, 1.0, 0])
    return lambda a, y, b=0.0: np.asarray(pos, float) + r * a + up * y + f * b, f, r


def agent(sc, pos, facing, pose, aim=None, ear=+1, raise_u=1.0, hand=+1, tuck=False):
    """pose 'fire': two-handed, pistol on the line to `aim`; 'call': two fingers of the `ear`-side hand on the earpiece
    (raise_u 0..1 = how far the hand has come up), pistol lowered in the other. Returns (grip, muzzle) for 'fire'."""
    P, f, r = frame(pos, facing)
    for s in (-1, 1):                                                             # legs
        sc.seg(P(s * 0.10, 0.92), P(s * 0.12, 0.04), 0.17, SUIT)
    sc.poly([P(-0.24, 1.47), P(0.24, 1.47), P(0.19, 0.86), P(-0.19, 0.86)], SUIT, "#77777c", 2)   # jacket back
    sc.seg(P(-0.21, 1.45), P(0.21, 1.45), 0.13, SUIT)                              # shoulders
    sc.seg(P(0, 1.50), P(0, 1.56), 0.11, "#f2efe6", bias=-0.01)                    # collar
    head = P(0, 1.67)
    sc.ball(head, 0.105, "#cfc9bd")                                                # head, hair on the back of it
    sc.ball(P(0, 1.685, -0.035), 0.103, "#141416", bias=-0.02 if f[2] > 0 else 0.02)
    out = None
    if pose == "fire":
        sh = P(hand * 0.21, 1.44)
        a = unit(np.asarray(aim) - sh)
        grip = sh + a * 0.64
        muzzle = grip + a * 0.24
        sc.seg(sh, grip, 0.105, SUIT2)                                             # gun arm, straight down the line
        sc.seg(P(-hand * 0.21, 1.44), P(-hand * 0.02, 1.36, 0.30), 0.10, SUIT2)     # support arm, bent in
        sc.seg(P(-hand * 0.02, 1.36, 0.30), grip, 0.09, SUIT2)
        sc.ball(grip, 0.055, "#cfc9bd")
        sc.seg(grip, muzzle, 0.05, "#000000", bias=-0.02)
        out = (grip, muzzle)
    else:
        s = ear
        sh = P(s * 0.21, 1.44)
        down, up_h = P(s * 0.27, 0.90), head + r * s * 0.125 + f * 0.03
        up_e = P(s * 0.30, 1.20, 0.12) if tuck else P(s * 0.39, 1.30, 0.10)
        elbow_d = P(s * 0.26, 1.16)
        elbow = elbow_d + (up_e - elbow_d) * raise_u
        hand = down + (up_h - down) * raise_u
        sc.seg(sh, elbow, 0.105, SUIT2)
        sc.seg(elbow, hand, 0.095, SUIT2, bias=-0.03)
        sc.ball(hand, 0.05, "#cfc9bd", bias=-0.04)
        sh2, hand2 = P(-s * 0.21, 1.44), P(-s * 0.28, 0.88)                         # pistol lowered at his side
        sc.seg(sh2, hand2, 0.105, SUIT2)
        sc.seg(hand2, hand2 + np.array([0, -0.2, 0]) + f * 0.06, 0.05, "#000000")
    sc.seg(head + r * 0.10 - f * 0.02, P(0.07, 1.51, -0.05), 0.016, "#f2efe6", bias=-0.05)     # coiled earpiece wire
    return out


def jade(sc, pos, heading, t):
    P, f, r = frame(pos, heading)
    lean = math.sin(heading) * 0.16                                                 # leans into the leg she is on
    L = lambda a, y, b=0.0: P(a, y, b) + np.array([lean * y, 0, 0])
    ph = math.sin(t * 2 * math.pi * 3.4)                                            # stride
    for s in (-1, 1):
        knee = L(s * 0.09, 0.45, s * ph * 0.22)
        sc.seg(L(s * 0.09, 0.82), knee, 0.16, "#1f2a4d")
        sc.seg(knee, L(s * 0.09, 0.06, s * ph * 0.42 - 0.08), 0.14, "#1f2a4d")
        sc.seg(L(s * 0.09, 0.05, s * ph * 0.42 - 0.08), L(s * 0.09, 0.04, s * ph * 0.42 + 0.10), 0.10, "#f4f1ea")
    sc.poly([L(-0.14, 1.0), L(0.14, 1.0), L(0.13, 0.82), L(-0.13, 0.82)], "#141416")                 # crop top / waist
    sc.poly([L(-0.19, 1.32), L(0.19, 1.32), L(0.17, 0.98), L(-0.17, 0.98)], "#f6f3ec", "#8a8a8a", 2, bias=-0.01)   # jacket back
    sc.poly([L(-0.185, 1.20), L(0.185, 1.20), L(0.18, 1.12), L(-0.18, 1.12)], ORANGE, bias=-0.02)     # orange band
    ring = [L(0.085 * math.cos(a), 1.16 + 0.085 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 18, endpoint=False)]
    sc.poly(ring, BLUE, bias=-0.03)                                                 # the pale-blue circle on her back
    for s in (-1, 1):
        el = L(s * 0.24, 1.08, -s * ph * 0.16)
        sc.seg(L(s * 0.19, 1.28), el, 0.10, "#f6f3ec")
        sc.seg(el, L(s * 0.22, 1.12, -s * ph * 0.30 + 0.12), 0.09, "#f6f3ec")
        sc.ball(L(s * 0.10, 1.35), 0.05, ORANGE, bias=-0.02)                        # headphones round her neck
    sc.ball(L(0, 1.46), 0.10, "#141416")
    sc.ball(L(0, 1.58, -0.04), 0.06, "#141416")                                     # bun, two crossed pencils
    for s in (-1, 1):
        sc.seg(L(s * 0.10, 1.66, -0.04), L(-s * 0.08, 1.50, -0.04), 0.018, "#f2c230", bias=-0.03)


def hotel_faces(sc):
    cx, cz = HOTEL["corner"]
    c, s, h = math.cos(HOTEL["yaw"]), math.sin(HOTEL["yaw"]), HOTEL["h"]
    front, side = np.array([c, 0, -s]), np.array([s, 0, c])       # front wall runs right from the near corner
    P0 = np.array([cx, 0, cz])
    faces = [(P0, front * HOTEL["front"]), (P0, -np.array([-side[0], 0, -side[2]]) * 0 + side * HOTEL["side"])]
    for k, (o, v) in enumerate(faces):
        sc.poly([o, o + v, o + v + [0, h, 0], o + [0, h, 0]], "#e3ded1" if k == 0 else "#bdb8ab", INK, 2)
        for fl in range(1, 13):
            y = 5.5 + (h - 7) * fl / 13
            sc.poly([o + [0, y, 0], o + v + [0, y, 0], o + v + [0, y + 0.9, 0], o + [0, y + 0.9, 0]], "#8f8a80", bias=-0.5)
        sc.poly([o + [0, 0.5, 0], o + v + [0, 0.5, 0], o + v + [0, 4.6, 0], o + [0, 4.6, 0]], "#9a958a", bias=-0.5)
    bb = P0 + front * 6
    quad = [bb + [0, h + 9.5, 0], bb + front * 26 + [0, h + 9.5, 0], bb + front * 26 + [0, h + 3, 0], bb + [0, h + 3, 0]]
    sc.poly(quad, "#efe7da", INK, 2, bias=-1)
    return quad, P0


# --------------------------------------------------------------------------------------------------------------
# one still
# --------------------------------------------------------------------------------------------------------------
def shot_of(t):
    return next(k for k, s in SHOTS.items() if s["t0"] <= t < s["t1"])


def fire_geometry(key):
    """For every miss of a shot: the muzzle and the impact in metres."""
    out = []
    for tb, who in SHOTS[key]["fires"]:
        lag = SHOTS[key]["lag"]
        target, _ = jade_at(tb - lag)
        sc = Scene(Cam((0, 1.6, -50), 0, 0, 30))
        apos = agent_pos(who, tb)
        through = None
        if key == "G2" and tb == 101.14:      # the miss passes where her waist was and goes on into the board behind
            through = target + [0, 1.1, 0]
            _, m0 = agent(sc, apos, BLADE[who], "fire", aim=through, hand=GUN_HAND[who])
            target = m0 + (through - m0) * ((BOARD["z"] - m0[2]) / (through[2] - m0[2]))
        _, muzzle = agent(sc, apos, BLADE[who], "fire", aim=target, hand=GUN_HAND[who])
        out.append(dict(t=tb, who=who, muzzle=muzzle, impact=target, through=through, range_m=float(np.linalg.norm((target - muzzle)[[0, 2]])),
                        jade_range_m=float(np.linalg.norm((jade_at(tb)[0] - apos)[[0, 2]]))))
    return out


def clearance(key):
    """For each miss, on its beat: how far (px at 960x540) the ruled line and the impact are from Jade's body, and
    whether the muzzle and the impact are inside the frame. (The line is aimed at a spot she has already left; during
    its lead-in it ends at her heels, which is the v3 design.)"""
    out = []
    for fz in fire_geometry(key):
        cam = cam_at(SHOTS[key], fz["t"])
        jp, _ = jade_at(fz["t"])
        body = [cam.project(jp + [0, y, 0]) for y in np.linspace(0.1, 1.6, 12)]
        half = cam.f * 0.28 / body[0][2]
        gap = lambda p: min(math.hypot(p[0] - b[0], p[1] - b[1]) for b in body) - half
        line = min(gap(p) for p in (cam.project(fz["muzzle"] + (fz["impact"] - fz["muzzle"]) * u) for u in np.linspace(0, 1, 400)) if p)
        inside = lambda p: bool(p and 0 <= p[0] <= cam.w and 0 <= p[1] <= cam.h)
        out.append(dict(t=fz["t"], who=fz["who"], line_clear_of_jade_px=round(line / SS), impact_clear_of_jade_px=round(gap(cam.project(fz["impact"])) / SS),
                        muzzle_in_frame=inside(cam.project(fz["muzzle"])), impact_in_frame=inside(cam.project(fz["impact"]))))
    return out


def draw_agents(sc, key, t, fires):
    """Pose and draw A, B, C for song time t. Returns the muzzles of the agents who are aiming."""
    shot, muzzles = SHOTS[key], {}
    for name in "ABC":
        pos = agent_pos(name, t)
        if name in shot["callers"]:
            ear, at = shot["callers"][name]                        # hand reaches the ear at `at`, starts 0.4 s before
            agent(sc, pos, 0.0, "call", ear=ear, raise_u=smooth((t - at + 0.4) / 0.4))
        elif t >= shot.get("lower", {}).get(name, 1e9) - 0.3:      # pistol comes down: she is out of range
            agent(sc, pos, 0.0, "call", ear=+1, raise_u=0.0)
        else:
            mine = [fz for fz in fires if fz["who"] == name]
            near = min(mine, key=lambda fz: abs(fz["t"] - t), default=None)
            if near and -0.45 <= t - near["t"] <= 0.2:
                aim = near["impact"]
            else:                             # between shots he tracks her, a little behind
                aim = jade_at(t - shot["lag"])[0] + [0, 0.5, 0]
            _, muzzles[name] = agent(sc, pos, BLADE[name], "fire", aim=aim, hand=GUN_HAND[name])
    return muzzles


def render(t, annotate=True, ref=None):
    """ref: None, or a set of things to leave out for a clean layout reference ('agents', 'jade', 'marks')."""
    ref = ref or set()
    key = shot_of(t)
    shot, cam = SHOTS[key], cam_at(SHOTS[shot_of(t)], t)
    img = Image.new("RGBA", (cam.w, cam.h), PAPER)
    d = ImageDraw.Draw(img)
    hz = cam.horizon()
    d.rectangle([0, hz, cam.w, cam.h], fill=LAWN)
    d.line([0, hz, cam.w, hz], fill="#8f8a80", width=2)
    small = ImageFont.truetype(MONO, 11 * SS)
    tiny = ImageFont.truetype(MONO, 9 * SS)

    # depth lines on the lawn every 5 m from the firing line
    for zz in range(5, 80, 5):
        a, b = cam.project((-60, 0, zz)), cam.project((60, 0, zz))
        if a and b:
            if "marks" not in ref:
                d.line([a[0], a[1], b[0], b[1]], fill="#bab5a8", width=1 if zz % 10 else 2)
            if annotate and zz % 10 == 0 and hz + 4 < a[1] < cam.h - 30:
                yl = a[1] + (b[1] - a[1]) * (cam.w - 80 - a[0]) / (b[0] - a[0])
                d.text((cam.w - 86, yl - 26), f"{zz} m", font=tiny, fill="#77736a")

    # lyric on the grass
    gt = shot.get("ground_text")
    if gt and "marks" not in ref:
        shown = [w for w, tw in gt["words"] if tw <= t + 1e-6]
        if shown:
            x0, x1, z0, z1 = gt["quad"]
            full = text_image([gt["text"]], INK, track=14)
            font = ImageFont.truetype(ANTON, 220)
            if len(gt["words"]) > 1:          # word-timed: cover what has not been sung yet
                n = len("I " + "".join(shown[1:])) if shown[0] == "I" else 0
                n = {1: 1, 2: 5, 3: 8}[len(shown)]
                wid = sum(font.getlength(ch) + 14 for ch in gt["text"][:n]) + full.size[0] * 0.107
                ImageDraw.Draw(full).rectangle([wid, 0, full.size[0], full.size[1]], fill=(0, 0, 0, 0))
            q = [cam.project(p) for p in ((x0, 0, z1), (x1, 0, z1), (x1, 0, z0), (x0, 0, z0))]
            if all(q):
                paste_warp(img, full, [(p[0], p[1]) for p in q], below=hz)
            else:                             # near edge behind the camera: go through the ground-plane homography
                g2s = lambda X, Z: cam.cam((X, 0, Z))
                pts = [((x0, z1)), ((x1, z1)), ((x1, z0)), ((x0, z0))]
                zc = max(z0, cam.pos[2] + 0.6)
                u0 = (z1 - zc) / (z1 - z0)
                tex = full.crop((0, 0, full.size[0], int(full.size[1] * u0)))
                q = [cam.project(p) for p in ((x0, 0, z1), (x1, 0, z1), (x1, 0, zc), (x0, 0, zc))]
                if all(q) and tex.size[1] > 2:
                    paste_warp(img, tex, [(p[0], p[1]) for p in q], below=hz)
            d = ImageDraw.Draw(img)

    # her residue ribbon on the lawn (orange), scars of the misses already fired
    ts = np.arange(max(97.7, t - 2.4), t, 0.02)
    pts = [cam.project(jade_at(x)[0] + [0, 0.02, 0]) for x in ts]
    for (a, b) in zip(pts, pts[1:]):
        if a and b and "marks" not in ref:
            d.line([a[0], a[1], b[0], b[1]], fill=ORANGE, width=max(2, int(cam.f * 0.22 / a[2])))
    fires = fire_geometry(key)
    for fz in fires:
        p = cam.project(fz["impact"])
        if p and fz["t"] <= t + 1e-6 and fz["impact"][1] < 0.1 and "marks" not in ref:
            r = cam.f * 0.28 / p[2]
            d.ellipse([p[0] - r * 1.6, p[1] - r * 0.45, p[0] + r * 1.6, p[1] + r * 0.45], fill="#3a3832")

    sc = Scene(cam)
    bbquad, hcorner = hotel_faces(sc)
    for tx, tz in ((-34, 130), (-20, 105), (-52, 170), (24, 190), (-70, 200), (90, 180)):          # a few trees for depth
        sc.seg((tx, 0, tz), (tx, 4, tz), 0.5, "#6f6b62")
        sc.ball((tx, 6.0, tz), 2.8, "#a39e93")

    # the notice board (G2; she crosses in front of it)
    board_q = None
    if "board_text" in shot:
        B = BOARD
        for x in (B["x0"] + 0.25, B["x1"] - 0.25):
            sc.seg((x, 0, B["z"]), (x, B["y1"], B["z"]), 0.12, "#6f6b62")
        board_q = [(B["x0"], B["y1"], B["z"]), (B["x1"], B["y1"], B["z"]), (B["x1"], B["y0"], B["z"]), (B["x0"], B["y0"], B["z"])]
        sc.poly(board_q, "#f6e8d8", INK, 3, bias=-0.05)

    jp, jh = jade_at(t)
    muzzles = draw_agents(sc, key, t, fires) if "agents" not in ref else {}
    if "jade" not in ref:
        jade(sc, jp, jh, t)
    sc.draw(d)

    # lettering on the hotel billboard and the notice board
    q = [cam.project(p) for p in bbquad]
    if all(q):
        paste_warp(img, text_image(["HILBERT"], INK, track=10), [(p[0], p[1]) for p in q])
    if board_q and "marks" not in ref:
        words = [w for w, tw in shot["board_text"] if tw <= t + 1e-6]
        lines = [" ".join(words[:2]), " ".join(words[2:])]
        full = text_image(["ACROSS THE", "FIELD OF"], (0, 0, 0, 0), pad=0.06)
        tex = text_image([ln for ln in lines if ln] or [""], INK, pad=0.06)
        canvas = Image.new("RGBA", full.size, (0, 0, 0, 0))
        canvas.alpha_composite(tex, (0, 0))
        B = BOARD
        q = [cam.project(p) for p in ((B["x0"], B["y1"], B["z"]), (B["x1"], B["y1"], B["z"]), (B["x1"], B["ty0"], B["z"]), (B["x0"], B["ty0"], B["z"]))]
        if all(q):
            paste_warp(img, canvas, [(p[0], p[1]) for p in q])
    d = ImageDraw.Draw(img)
    # Jade is in front of the board: redraw her over the lettering
    if board_q and jp[2] < BOARD["z"] and "jade" not in ref:
        s2 = Scene(cam)
        jade(s2, jp, jh, t)
        s2.draw(d)
    # ...and the agents are in front of everything on the lawn
    if (board_q or gt) and "agents" not in ref:
        s3 = Scene(cam)
        draw_agents(s3, key, t, fires)
        if jp[2] < 12:
            jade(s3, jp, jh, t)
        s3.draw(d)

    # tracers: every miss of the shot as a thin dashed line muzzle -> impact; the live one heavy, with its starburst
    def dashed(a, b, fill, width, dash=18):
        a, b = np.array(a[:2]), np.array(b[:2])
        n = np.linalg.norm(b - a)
        k = 0.0
        while k < n:
            p, q2 = a + (b - a) * k / n, a + (b - a) * min(n, k + dash * 0.6) / n
            d.line([p[0], p[1], q2[0], q2[1]], fill=fill, width=width)
            k += dash

    def seg3(a, b):                           # clip a 3D segment to the front of the camera, project
        ca, cb = cam.cam(a), cam.cam(b)
        if ca[2] < 0.15 and cb[2] < 0.15:
            return None
        if ca[2] < 0.15:
            ca = ca + (cb - ca) * ((0.15 - ca[2]) / (cb[2] - ca[2]))
        if cb[2] < 0.15:
            cb = cb + (ca - cb) * ((0.15 - cb[2]) / (ca[2] - cb[2]))
        return cam.px(ca), cam.px(cb)

    rec = []
    for fz in ([] if "marks" in ref else fires):
        s = seg3(fz["muzzle"], fz["impact"])
        live = -LEAD <= t - fz["t"] <= 0.10
        m, i = cam.project(fz["muzzle"]), cam.project(fz["impact"])
        rec.append(dict(t=fz["t"], who=fz["who"], muzzle_px=[round(m[0] / SS, 1), round(m[1] / SS, 1)] if m else None,
                        impact_px=[round(i[0] / SS, 1), round(i[1] / SS, 1)] if i else None))
        if not s:
            continue
        if live:
            dashed(s[0], s[1], INK, 5, 26)
        elif annotate:
            dashed(s[0], s[1], "#3b6fb5", 2, 16)
        if i and (fz["t"] <= t + 1e-6):
            if fz["impact"][1] > 0.1:         # the hole in the board
                d.ellipse([i[0] - 9, i[1] - 9, i[0] + 9, i[1] + 9], fill=INK)
            if abs(t - fz["t"]) <= 0.12:      # turf (or splinters) thrown up
                for a in np.linspace(-2.6, -0.5, 7):
                    r0, r1 = cam.f * 0.25 / i[2], cam.f * 0.75 / i[2]
                    d.line([i[0] + math.cos(a) * r0, i[1] + math.sin(a) * r0, i[0] + math.cos(a) * r1, i[1] + math.sin(a) * r1], fill=INK, width=4)
        if m and abs(t - fz["t"]) <= 0.045:    # muzzle starburst, two frames
            R = max(26, cam.f * 0.22 / m[2])
            star = []
            for k in range(16):
                a = k * math.pi / 8
                rr = R if k % 2 == 0 else R * 0.38
                star.append((m[0] + math.cos(a) * rr, m[1] + math.sin(a) * rr))
            d.polygon(star, fill="#ffffff", outline=INK, width=3)
        if annotate and i and fz["t"] - LEAD <= t:
            lab = f"{fz['t']:.2f} {fz['who']}"
            d.text((i[0] + 10, i[1] + 4), lab, font=tiny, fill="#3b6fb5")
    if annotate:
        for name, m in muzzles.items():
            p = cam.project(m)
            if p and 0 < p[0] < cam.w and 0 < p[1] < cam.h:
                d.ellipse([p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6], outline="#3b6fb5", width=3)
                d.text((p[0] + 10, p[1] - 26), f"muzzle {name}", font=tiny, fill="#3b6fb5")
        for name in "ABC":
            p = cam.project(agent_pos(name, t) + [0, 1.22, 0])
            if p and 30 < p[0] < cam.w - 30:
                role = "firing" if name in muzzles else "lowered"
                if name in shot["callers"]:
                    role = "on earpiece" if t >= shot["callers"][name][1] - 0.2 else "lowering pistol"
                big = ImageFont.truetype(MONO, int(min(30, max(13, cam.f * 0.16 / p[2] / SS)) * SS))
                d.text((p[0], min(cam.h - 90, p[1])), name, font=big, fill=PAPER, anchor="mm")
                d.text((p[0], min(cam.h - 90, p[1]) + big.size * 0.9), role, font=tiny, fill=PAPER, anchor="mm")
        p = cam.project(jp + [0, 1.9, 0])
        rng = float(np.linalg.norm((jp - np.array([0, 0, 0]))[[0, 2]]))
        if p:
            pm = cam.project(jp + [0, 0.8, 0])
            lab = f"Jade {rng:.0f} m"
            bx = d.textbbox((pm[0] + 46, pm[1]), lab, font=small, anchor="lm")
            d.rectangle([bx[0] - 6, bx[1] - 4, bx[2] + 6, bx[3] + 4], fill=PAPER, outline="#b05a00", width=2)
            d.text((pm[0] + 46, pm[1]), lab, font=small, fill="#b05a00", anchor="lm")
        p = cam.project(hcorner + [0, 14, 0])
        if key == "G2" and p and p[0] < cam.w - 40:
            d.text((p[0] + 8, 60), "hotel corner", font=tiny, fill=INK, stroke_width=3, stroke_fill=PAPER)
        d.rectangle([0, cam.h - 46, cam.w, cam.h], fill=INK)
        d.text((14, cam.h - 38), f"{key}  t={t:.2f}   camera {cam.pos[2]:+.1f} m from the line, lens {cam.hfov:.0f} deg"
               f"   blue dashes: every miss of this shot, muzzle to impact", font=small, fill=PAPER)
    return img.convert("RGB").resize((W, H), Image.LANCZOS), rec


# --------------------------------------------------------------------------------------------------------------
# top-down plan, to scale
# --------------------------------------------------------------------------------------------------------------
WIDE = 2.5                                  # the plans stretch the across-field axis 2.5x so the lanes can be read


def plan(keys, title, zmax=50.0, xr=(-4.0, 6.0)):
    PW, PH, m = 960, 540, 2
    w, h = PW * m, PH * m
    img = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(img)
    zmin = -8.0
    sc = (w - 80) / (zmax - zmin)             # z runs left to right, x runs down (her left at the top)
    X = lambda z: 40 + (z - zmin) * sc
    Y = lambda x: h / 2 + 30 + (x - (xr[0] + xr[1]) / 2) * sc * WIDE
    font, tiny = ImageFont.truetype(MONO, 12 * m), ImageFont.truetype(MONO, 9 * m)
    for zz in range(0, int(zmax) + 1, 5):
        d.line([X(zz), Y(xr[0]), X(zz), Y(xr[1])], fill="#cfcabd" if zz % 10 else "#a9a498", width=2)
        if zz % 10 == 0:
            d.text((X(zz) - 26, Y(xr[1]) + 6), f"{zz} m", font=tiny, fill="#77736a")
    d.text((24, 16), title, font=font, fill=INK)
    d.text((24, 16 + 17 * m), f"top view; depth to scale, across-field stretched {WIDE}x; hotel off the right edge; grid = metres from the firing line",
           font=tiny, fill="#77736a")
    cols = {"G1": "#1f7a4d", "G2": "#7a3fb0"}
    t_lo, t_hi = SHOTS[keys[0]]["t0"], SHOTS[keys[-1]]["t1"]
    # her path
    ts = np.arange(t_lo, t_hi + 0.001, 0.02)
    pts = [jade_at(x)[0] for x in ts]
    d.line([(X(p[2]), Y(p[0])) for p in pts], fill=ORANGE, width=8)
    for tt, _ in TURNS:
        if t_lo <= tt <= t_hi:
            p = jade_at(tt)[0]
            d.ellipse([X(p[2]) - 9, Y(p[0]) - 9, X(p[2]) + 9, Y(p[0]) + 9], fill=ORANGE, outline=INK)
            up = p[0] < jade_at(tt + 0.2 if tt + 0.2 < t_hi else tt - 0.2)[0][0]      # label on the outside of the corner
            d.text((X(p[2]), Y(p[0]) + (-24 if up else 24)), f"{tt:.2f}", font=tiny, fill="#b05a00", anchor="mm")
    for key in keys:
        shot, col = SHOTS[key], cols[key]
        gt = shot.get("ground_text")
        if gt:
            x0, x1, z0, z1 = gt["quad"]
            d.rectangle([X(z0), Y(x0), X(z1), Y(x1)], outline=INK, width=2)
            d.text((X(z0) + 8, Y(x0) + 6), f"\"{gt['text']}\" on the grass", font=tiny, fill=INK)
        if "board_text" in shot:
            B = BOARD
            d.line([X(B["z"]), Y(B["x0"]), X(B["z"]), Y(B["x1"])], fill=INK, width=8)
            d.text((X(B["z"]) + 14, Y(B["x1"]) - 20), "notice board", font=tiny, fill=INK)
        # camera start and end with the lens wedge
        for k, tt in enumerate((shot["t0"], shot["t1"] - 1e-3)):
            c = cam_at(shot, tt)
            for sgn in (-1, 1):
                a = c.yaw + sgn * math.radians(c.hfov / 2)
                L = 9.0
                d.line([X(c.pos[2]), Y(c.pos[0]), X(c.pos[2] + math.cos(a) * L), Y(c.pos[0] + math.sin(a) * L)], fill=col, width=2 + 2 * k)
            d.rectangle([X(c.pos[2]) - 8, Y(c.pos[0]) - 8, X(c.pos[2]) + 8, Y(c.pos[0]) + 8], fill=col)
        c0, c1 = cam_at(shot, shot["t0"]), cam_at(shot, shot["t1"] - 1e-3)
        d.line([X(c0.pos[2]), Y(c0.pos[0]), X(c1.pos[2]), Y(c1.pos[0])], fill=col, width=5)
        d.text((X(c0.pos[2]) - 30, Y(c0.pos[0]) + 14 + 22 * keys.index(key)), f"{key} camera", font=tiny, fill=col)
        for fz in fire_geometry(key):
            a, b = fz["muzzle"], fz["impact"]
            d.line([X(a[2]), Y(a[0]), X(b[2]), Y(b[0])], fill="#3b6fb5", width=3)
            s = 9
            d.line([X(b[2]) - s, Y(b[0]) - s, X(b[2]) + s, Y(b[0]) + s], fill=INK, width=4)
            d.line([X(b[2]) - s, Y(b[0]) + s, X(b[2]) + s, Y(b[0]) - s], fill=INK, width=4)
            d.text((X(b[2]) + 12, Y(b[0]) - 8), f"{fz['t']:.2f} {fz['who']}  {fz['range_m']:.0f} m", font=tiny, fill="#3b6fb5")
    # agents (C at the start and end of the plan's time span)
    for name in "ABC":
        for k, tt in enumerate((t_lo, t_hi) if name == "C" else (t_lo,)):
            p = agent_pos(name, tt)
            d.ellipse([X(p[2]) - 11, Y(p[0]) - 11, X(p[2]) + 11, Y(p[0]) + 11], fill=SUIT if k == 0 else "#8a8a8f")
            d.text((X(p[2]) - 9, Y(p[0]) - 44), name + ("'" if k else ""), font=font, fill=INK)
        if name == "C":
            a, b = agent_pos("C", t_lo), agent_pos("C", t_hi)
            d.line([X(a[2]), Y(a[0]), X(b[2]), Y(b[0])], fill="#8a8a8f", width=3)
    d.text((24, h - 50), "orange: her path, turn times are tracked beats   blue: barrel line of each miss, with range   X: where it lands"
           "   squares + wedges: camera start (thin) and end (thick)", font=tiny, fill=INK)
    return img.resize((PW, PH), Image.LANCZOS)


LEGEND = [
    "REWIND v4: gunfire on the lawn. Grey-box blockout (approved build).",
    "  Row 1: v3 at 1:39 and 1:41; top views of the two new shots.",
    "  G1 98.28-100.70 (five stills): behind A and B, push between",
    "    their shoulders, settle over C's. Misses 98.94 B, 99.38 B,",
    "    99.82 C, 100.26 C, from 18 to 21 m.",
    "  G2 100.70-102.46 (five stills), long lens: C alone fires",
    "    (101.14 board, 102.00 turf); A, then B, on the earpiece.",
    "  G3 102.46-104.22: earpiece close-up (generated, not blocked).",
    "  Black dashes + star: the shot fired in that frame.",
    "  Blue dashes: the shot's other misses. Every line is the 3D",
    "  line from that muzzle to a spot she has already left.",
    "  Grey boxes = engraved agents, lawn, hotel. Colour = Jade.",
]


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--ref" in sys.argv:                  # clean layout reference for a keyframe: --ref T OUT.jpg [agents,jade]
        k = sys.argv.index("--ref")
        skip = {"marks"} | set(sys.argv[k + 3].split(",") if len(sys.argv) > k + 3 else [])
        render(float(sys.argv[k + 1]), annotate=False, ref=skip)[0].save(sys.argv[k + 2], quality=92)
        return
    if "--t" in sys.argv:
        t = float(sys.argv[sys.argv.index("--t") + 1])
        render(t)[0].save(os.path.join(OUT, f"extra_{t:.2f}.jpg"), quality=92)
        return
    geo, tiles = {}, []
    for key, shot in SHOTS.items():
        names = ["start"] + [f"t{t:.2f}" for t in shot["stills"][1:-1]] + ["end"]
        geo[key] = dict(cut_in=shot["t0"], cut_out=shot["t1"], misses=[
            dict(t=f["t"], who=f["who"], muzzle_m=[round(float(v), 2) for v in f["muzzle"]], impact_m=[round(float(v), 2) for v in f["impact"]],
                 muzzle_to_impact_m=round(f["range_m"], 1), agent_to_jade_at_shot_m=round(f["jade_range_m"], 1)) for f in fire_geometry(key)],
            camera=[dict(t=c[0], pos_m=c[1], yaw_deg=c[2], pitch_deg=c[3], hfov_deg=c[4]) for c in shot["cam"]],
            lag_s=shot["lag"], checks=clearance(key),
            agents_m={n: {f"{tt:.2f}": [round(float(v), 2) for v in agent_pos(n, tt)] for tt in (shot["t0"], shot["t1"])} for n in "ABC"},
            jade_turns=[dict(t=tt, x_m=x, z_m=round(Z0 + VZ * (tt - 98.28), 1)) for tt, x in TURNS if shot["t0"] - 0.9 < tt < shot["t1"] + 0.9],
            stills={})
        for t, nm in zip(shot["stills"], names):
            img, rec = render(t)
            p = os.path.join(OUT, f"{key}_{nm}.jpg")
            img.save(p, quality=92)
            geo[key]["stills"][os.path.basename(p)] = dict(t=t, misses_px_960x540=rec)
            tiles.append(img)
    p1 = plan(["G1"], "G1 98.28-100.70: four misses, one per beat, each down its own barrel line (B, B, C, C)", zmax=34, xr=(-3.4, 3.6))
    p2 = plan(["G2"], "G2 100.70-102.46: C alone fires (hole in the board, then turf); A and B call it in", zmax=58)
    p1.save(os.path.join(OUT, "plan_G1_top.jpg"), quality=92)
    p2.save(os.path.join(OUT, "plan_G2_top.jpg"), quality=92)
    json.dump(geo, open(os.path.join(OUT, "geometry.json"), "w"), indent=1)
    for key in geo:
        for m, c in zip(geo[key]["misses"], geo[key]["checks"]):
            print(key, m["t"], m["who"], "range", m["muzzle_to_impact_m"], "m | Jade from shooter", m["agent_to_jade_at_shot_m"], "m |", c)

    # contact sheet: the v3 frames the notes are about, then the new shots, then the two plans
    cw, ch = 640, 360
    v3 = [Image.open(os.path.join(ROOT, "media/reviews/v4/B/v3_frames", f)).convert("RGB") for f in ("v3_099.00.jpg", "v3_101.50.jpg")]
    cells = [("v3 now, 1:39", v3[0]), ("v3 now, 1:41", v3[1]), (None, p1), (None, p2)] + [(None, im) for im in tiles]
    cols = 4
    rows = math.ceil(len(cells) / cols)
    sheet = Image.new("RGB", (cols * cw, rows * ch), INK)
    f = ImageFont.truetype(MONO, 15)
    for k, (lab, im) in enumerate(cells):
        x, y = (k % cols) * cw, (k // cols) * ch
        sheet.paste(im.resize((cw - 4, ch - 4), Image.LANCZOS), (x + 2, y + 2))
        if lab:
            dd = ImageDraw.Draw(sheet)
            dd.rectangle([x + 2, y + ch - 28, x + 150, y + ch - 2], fill=INK)
            dd.text((x + 8, y + ch - 25), lab, font=f, fill=PAPER)
    k = len(cells)
    x, y = (k % cols) * cw, (k // cols) * ch
    dd, fb = ImageDraw.Draw(sheet), ImageFont.truetype(MONO, 15)
    for n, ln in enumerate(LEGEND):
        dd.text((x + 18, y + 20 + n * 26), ln, font=fb, fill=PAPER if not ln.startswith("  ") else "#c9c4b8")
    sheet.save(os.path.join(OUT, "contact_sheet.jpg"), quality=90)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
