#!/usr/bin/env python3
"""v6 (Jade's note 1:41, "she appears to somewhat clip through the sign"): G2's notice board moved further back.

In B_g2clean the board's posts stand on the turf at y ~708, and Jade's feet in G2 run y 677..762, so on the second
leg she is level with or behind the board on the ground yet drawn over it. This builds a per-frame RGBA overlay
for take_1_engraved.mp4 that removes the plate's board (sky / far turf, the hotel's side wall behind it, its two
posts and their shadow) and draws the same engraved board scaled by S with its feet on the turf at FEET_Y (further
back toward the horizon, y 523), so she is always clearly in front of it.

    tools/engrave/.venv/bin/python tools/v4B/gunfire/g2_board_v6.py [--frames N] [--check DIR]

Writes media/shots/B_g2clean/v6_board/f0000.png.. (1920x1080 RGBA, transparent outside the board area) and
v6_board.json (the new panel / text quad, for _B_gunfire.js). Each frame's fill is cut from that same frame where
the source is live (wall, posts, shadow band), so the overlay boils with the plate; B's hand, which reaches over
the board around source 0.83-1.05 s, is kept from the plate (foreground mask) and never copied.
"""
import argparse
import json
import os

import cv2
import numpy as np

ROOT = "/home/jade/Documents/rewind-take-two"
TAKE = os.path.join(ROOT, "media/shots/B_g2clean/take_1_engraved.mp4")
NOC = os.path.join(ROOT, "media/shots/B_g2noC/patch.png")
OUT = os.path.join(ROOT, "media/shots/B_g2clean/v6_board")

# the plate's board (design px, read off frame 0): panel outer box, posts, feet, cast shadow band
PANEL = (962, 330, 1350, 594)            # x0, y0, x1, y1 (frame lines included)
POSTS = [(996, 1026), (1284, 1314)]
POST_Y = (594, 716)
SHADOW = (986, 686, 1324, 718)
FEET_OLD = 709
WALL_X = 1147                            # the hotel's side wall starts here (left of it: sky over the far turf)
HORIZON_EDGE = 540                       # far edge of the turf

# the new board: same drawing scaled by S, feet on the turf at FEET_Y, panel right edge kept left of B's hand
S, FEET_Y, X0 = 0.70, 635, 990


def wall_xmap(x):
    """target x on the hidden part of the side wall -> source x on the visible bays 4/5 (piecewise linear: each
    hidden bay window onto bay 4's window, each pier onto the pier between bays 4 and 5)."""
    tk = [1140, 1165, 1198, 1212, 1250, 1265, 1305, 1338, 1352]
    sk = [1395, 1418, 1468, 1338, 1388, 1338, 1388, 1418, 1432]
    # sections: [1140,1165) pier, [1165,1198) bay1, [1198,1212) pier, [1212,1250) bay2, [1250,1265) pier,
    # [1265,1305) bay3, [1305,1338) pier, [1338,1352) bay4 left jamb
    sec = [(1140, 1165, 1388, 1418), (1165, 1198, 1338, 1388), (1198, 1212, 1388, 1418), (1212, 1250, 1338, 1388),
           (1250, 1265, 1388, 1418), (1265, 1305, 1338, 1388), (1305, 1338, 1388, 1418), (1338, 1352, 1418, 1432)]
    for a, b, c, d in sec:
        if a <= x < b:
            return c + (x - a) * (d - c) / (b - a)
    return x


# each hidden bay's arch top (bays 1-3) vs bay 4's (220): scale rows about the wall's foot (y 603) to match
ARCH = [(1140, 1205, 270), (1205, 1258, 262), (1258, 1352, 245)]


def build_maps():
    """remap maps (target -> source) for the hidden wall, and the masks of each fill region."""
    H, W = 1080, 1920
    mx = np.tile(np.arange(W, dtype=np.float32), (H, 1))
    my = np.tile(np.arange(H, dtype=np.float32)[:, None], (1, W))
    for x in range(WALL_X - 7, PANEL[2] + 2):
        sx = wall_xmap(x)
        top = next(t for a, b, t in ARCH if a <= x < b)
        k = (603 - 220) / (603 - top)
        for y in range(PANEL[1] - 2, PANEL[3] + 2):
            mx[y, x] = sx
            my[y, x] = 603 + (y - 603) * k
    return mx, my


def board_art(f0):
    """the plate's board (panel + posts) as RGBA, cut from frame 0, and its cast-shadow darkness."""
    x0, y0, x1, y1 = PANEL
    art = np.zeros((POST_Y[1] - y0, x1 - x0, 4), np.uint8)
    art[:y1 - y0, :, :3] = f0[y0:y1, x0:x1]
    art[:y1 - y0, :, 3] = 255
    for a, b in POSTS:
        art[y1 - y0:, a - x0:b - x0, :3] = f0[y1:POST_Y[1], a:b]
        # the post: dark outline + light shaft; keep columns between the outer ink lines
        col = f0[y1 + 10:FEET_OLD - 6, a:b].mean(axis=(0, 2))
        ink = np.where(col < 140)[0]
        l, r = (ink.min(), ink.max() + 1) if len(ink) else (0, b - a)
        art[y1 - y0:FEET_OLD - y0 + 2, a - x0 + l:a - x0 + r, 3] = 255
    return art


def scaled_board(art):
    h, w = art.shape[:2]
    nw, nh = round(w * S), round(h * S)
    a = art.astype(np.float32)
    a[..., :3] *= a[..., 3:] / 255                 # premultiply so the cut edges don't fringe
    r = cv2.resize(a, (nw, nh), interpolation=cv2.INTER_AREA)
    al = r[..., 3:] / 255
    rgb = np.where(al > 1e-3, r[..., :3] / np.maximum(al, 1e-3), 0)
    return np.dstack([np.clip(rgb, 0, 255), np.clip(r[..., 3], 0, 255)]).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", type=int, default=75)
    ap.add_argument("--check", default=None, help="also write opaque composites here (for review)")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    cap = cv2.VideoCapture(TAKE)
    frames = []
    while len(frames) < args.frames:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(f)
    f0 = frames[0]
    noc = cv2.imread(NOC, cv2.IMREAD_UNCHANGED)
    na = noc[..., 3:].astype(np.float32) / 255

    def with_noc(f):
        return (f * (1 - na) + noc[..., :3] * na).astype(np.uint8)

    comp0 = with_noc(f0)
    mx, my = build_maps()
    art = scaled_board(board_art(f0))
    bh, bw = art.shape[:2]
    by0 = FEET_Y - round((FEET_OLD - PANEL[1]) * S)   # art top so the post feet land on FEET_Y
    bx0 = X0
    ref_blur = cv2.GaussianBlur(f0.astype(np.float32), (0, 0), 3).mean(axis=2)

    # region masks (design px)
    H, W = 1080, 1920
    region = np.zeros((H, W), np.uint8)
    x0, y0, x1, y1 = PANEL
    region[y0 - 2:y1 + 2, x0 - 2:x1 + 2] = 1
    for a, b in POSTS:
        region[POST_Y[0]:POST_Y[1], a - 2:b + 2] = 1
    sx0, sy0, sx1, sy1 = SHADOW
    region[sy0:sy1, sx0:sx1] = 1
    alpha_reg = cv2.GaussianBlur(region.astype(np.float32), (0, 0), 1.5)
    alpha_reg = np.maximum(alpha_reg, region * 0)

    # B's hand: frames where something big moves over the board (from the scan: source frames 18..27)
    def fg_mask(f):
        d = np.abs(cv2.GaussianBlur(f.astype(np.float32), (0, 0), 3).mean(axis=2) - ref_blur)
        m = np.zeros((H, W), np.uint8)
        # v6b: down to the posts' feet and the shadow band too (B's hand dips to y ~700 near the right post)
        m[y0 - 4:SHADOW[3] + 6, 1180:x1 + 12] = (d[y0 - 4:SHADOW[3] + 6, 1180:x1 + 12] > 22).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(m)
        keep = np.zeros_like(m)
        for i in range(1, n):
            if st[i, cv2.CC_STAT_AREA] > 300:
                keep[lab == i] = 1
        keep = cv2.morphologyEx(keep, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
        return cv2.GaussianBlur(cv2.dilate(keep, np.ones((3, 3), np.uint8)).astype(np.float32), (0, 0), 1.2)

    fgs = [fg_mask(f) for f in frames]
    busy = [float(m.sum()) > 200 for m in fgs]
    print("fg (B's hand) area per frame:", {i: int(m.sum()) for i, m in enumerate(fgs) if m.sum() > 0})
    print("frames with B's hand over the board:", [i for i, b in enumerate(busy) if b])

    # v6b (Jade: "a disembodied elbow"): the wall fill is remapped from bays 4/5 (source x 1338-1432, y ~285-612),
    # and from source frame ~20 on B's raised arm is in that source and was being copied onto the hidden bays. A frame
    # may be a wall source only if nothing moves there; busy frames take a clean frame from a cycling pool, so the fill
    # still boils.
    def src_busy(f):
        d = np.abs(cv2.GaussianBlur(f.astype(np.float32), (0, 0), 3).mean(axis=2) - ref_blur)[280:615, 1330:1442]
        n, lab, st, _ = cv2.connectedComponentsWithStats((d > 22).astype(np.uint8))
        return any(st[k, cv2.CC_STAT_AREA] > 150 for k in range(1, n))

    wbusy = [src_busy(f) for f in frames]
    clean_idx = [i for i, b in enumerate(wbusy) if not b]
    print("frames whose wall source has B's arm in it:", [i for i, b in enumerate(wbusy) if b], "clean pool:", clean_idx)

    meta = None
    for i, f in enumerate(frames):
        # wall source: this frame unless B's arm is over the source bays (see src_busy)
        wsrc = f if not wbusy[i] else frames[clean_idx[i % len(clean_idx)]]
        # turf source for the posts / shadow band: this frame, unless B's hand is near (it would be copied too)
        tsrc = f if not busy[i] else frames[min((j for j in range(len(frames)) if not busy[j]), key=lambda j: abs(j - i))]
        out = f.copy()
        comp = with_noc(f)
        # 1. sky and far turf left of the wall: the same rows 200 px left (C's take is painted out there by noC)
        out[y0 - 2:y1 + 2, x0 - 2:WALL_X] = comp[y0 - 2:y1 + 2, x0 - 202:WALL_X - 200]
        # 2. the side wall: bays 4/5 remapped onto the hidden bays 1-3 (live)
        wall = cv2.remap(wsrc, mx, my, cv2.INTER_LINEAR)
        wy1 = 606                                     # wall foot; below it the turf rows
        out[y0 - 2:wy1, WALL_X - 6:x1 + 2] = wall[y0 - 2:wy1, WALL_X - 6:x1 + 2]
        # soften the sky/wall seam (the wall's left edge line is kept from the source edge at 1147)
        out[y0 - 2:HORIZON_EDGE, WALL_X - 6:WALL_X - 1] = comp[y0 - 2:HORIZON_EDGE, WALL_X - 206:WALL_X - 201]
        # 3. posts: the turf beside them (live)
        for a, b in POSTS:
            sh = -(b - a + 6) if a < 1100 else (b - a + 6)
            out[POST_Y[0]:POST_Y[1], a - 3:b + 3] = tsrc[POST_Y[0]:POST_Y[1], a - 3 + sh:b + 3 + sh]
        # 4. the cast-shadow band: turf rows just below it (live)
        out[sy0:sy1, sx0:sx1] = tsrc[sy0 + 34:sy1 + 34, sx0:sx1]
        # 5. the new board's shadow (the old band, scaled, as darkness) and the board
        sh_src = f0[sy0:sy1, sx0:sx1].astype(np.float32).mean(axis=2)
        dark = np.clip(sh_src / max(np.percentile(f0[sy1 + 30:sy1 + 70, sx0:sx1], 90), 1), 0.25, 1)
        dark = cv2.resize(dark, (round((sx1 - sx0) * S), round((sy1 - sy0) * S)), interpolation=cv2.INTER_AREA)
        dy0 = FEET_Y - round((FEET_OLD - sy0) * S)
        dx0 = bx0 + round((sx0 - PANEL[0]) * S)
        reg = out[dy0:dy0 + dark.shape[0], dx0:dx0 + dark.shape[1]].astype(np.float32)
        out[dy0:dy0 + dark.shape[0], dx0:dx0 + dark.shape[1]] = (reg * dark[..., None]).astype(np.uint8)
        a = art[..., 3:].astype(np.float32) / 255
        roi = out[by0:by0 + bh, bx0:bx0 + bw].astype(np.float32)
        out[by0:by0 + bh, bx0:bx0 + bw] = (roi * (1 - a) + art[..., :3] * a).astype(np.uint8)
        # overlay alpha: the old board area (and the new shadow) minus B's hand
        al = np.maximum(alpha_reg, 0)
        al[dy0:dy0 + dark.shape[0], dx0:dx0 + dark.shape[1]] = 1
        al = al * (1 - np.clip(fgs[i], 0, 1))
        a8 = (al * 255).astype(np.uint8)
        rgba = np.dstack([out * (a8[..., None] > 0), a8])   # zero RGB outside: small PNGs
        cv2.imwrite(os.path.join(OUT, f"f{i:04d}.png"), rgba, [cv2.IMWRITE_PNG_COMPRESSION, 6])
        if args.check:
            os.makedirs(args.check, exist_ok=True)
            base = with_noc(f).astype(np.float32)
            c = base * (1 - al[..., None]) + out * al[..., None]
            cv2.imwrite(os.path.join(args.check, f"c{i:04d}.jpg"), c.astype(np.uint8)[250:800, 850:1500])
        if meta is None:
            px = lambda u, v: [round(bx0 + (u - PANEL[0]) * S), round(by0 + (v - PANEL[1]) * S)]
            q = [*px(985, 346), *px(1325, 346), *px(1325, 500), *px(985, 500)]   # the v4 text quad, carried over
            meta = {"scale": S, "feet_y": FEET_Y, "panel": [*px(PANEL[0], PANEL[1]), *px(PANEL[2], PANEL[3])],
                    "text_quad": [q[0], q[1], q[2], q[1], q[2], q[5], q[0], q[5]], "art_box": [bx0, by0, bw, bh]}
    with open(os.path.join(OUT, "fps.txt"), "w") as fh:
        fh.write("24\n")
    with open(os.path.join(ROOT, "media/shots/B_g2clean/v6_board.json"), "w") as fh:
        json.dump(meta, fh, indent=1)
    print(json.dumps(meta))
    noc_v6()


def noc_v6():
    """v6b (Jade: "a floating partial ghost arm on another agent"): B_g2noC/patch.png feathers in over x ~525-570,
    right where the take's own C hangs his left arm (x >= ~540), so a see-through copy of that arm floated beside the
    cut-out C all through G2. Above the horizon the gap between A's elbow (x <= ~529, he moves a little) and that arm
    is x 530-539, so patch_v6.png is fully opaque from x 538 with an 8 px feather from 530; the rest is unchanged."""
    noc = cv2.imread(NOC, cv2.IMREAD_UNCHANGED)
    a = noc[..., 3].astype(np.float32)
    rows = a.max(axis=1) > 0
    ramp = np.clip((np.arange(a.shape[1], dtype=np.float32) - 530) / 8, 0, 1) * 255
    a[rows, 520:600] = np.maximum(a[rows, 520:600], ramp[None, 520:600])
    noc[..., 3] = np.clip(a, 0, 255).astype(np.uint8)
    cv2.imwrite(os.path.join(ROOT, "media/shots/B_g2noC/patch_v6.png"), noc)


if __name__ == "__main__":
    main()
