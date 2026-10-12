#!/usr/bin/env python3
"""v5 merge (Jade's 3:23 note): BLUE and ORANGE reassemble into the one original Jade, "un-Banach-Tarski".
Plan: docs/revisions/v5/merge.md. Free: works only from the F7e take 2 already on disk and its matte.

    tools/engrave/.venv/bin/python tools/v5/merge/bake.py [--sheet]

Writes media/shots/F7m/:
  approach_bo.mp4   F7e take 2 frames 0..FREEZE+5, the left twin ORANGE (orange dot), the right twin BLUE (blue band,
                    straps, headphones, dot); only pixels inside each twin's matte are touched (the F world is colour)
  plate.png         the L-platform plate with no girl (per-pixel from frames where the matte is clear; inpaint rest)
  fig/              RGBA PNG seq, 24 fps, 203.32 -> 204.64: the frozen twins get scored into triangles (graphite lines
                    sweep out from their touching hands), then on the 203.76 swell every triangle lifts off, turns and
                    flies (rigid motions: the paradox's pieces) into the matching place on the one merged girl. Pieces
                    from ORANGE glow orange, pieces from BLUE glow blue; mid-flight the figure is a checker of the two.
                    They seat by 204.48; the whole girl (take frame TARGET) fills in under them by 204.64.
  seams/            RGBA PNG seq, 204.64 -> 204.92: the triangle seams on the merged girl flash gold and fade
  layout.json       touch point, bboxes, tile counts (for the timeline / motes)
"""
import json
import math
import os
import subprocess
import sys

import cv2
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "v4B", "coop"))
from recolor import masks, BLUE_H, ORANGE_H  # noqa: E402

FFMPEG = os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg")
SRC = os.path.join(ROOT, "media/shots/F7e/take_2_engraved_dered.mp4")
MATTE = os.path.join(ROOT, "media/shots/F7e/take_2_matte/matte.mp4")
OUT = os.path.join(ROOT, "media/shots/F7m")

FPS = 24
FREEZE = 9          # take frame held from 203.32 (0.375 s: hands reaching, still two separate girls)
TARGET = 40         # take frame of the merged girl (1.667 s: burst gone); the video resumes here at 204.64
S = 46              # triangle side, px at 1080p
T_SCORE = 0.44      # 203.32 -> 203.76: scoring
T_FLY = 0.88        # 203.76 -> 204.64: flight + seat
N_FIG = int(round((T_SCORE + T_FLY) * FPS))     # 32
N_SEAM = 7
ORANGE = np.array([36, 138, 240], np.float32)   # BGR #F08A24
BLUE = np.array([216, 111, 62], np.float32)     # BGR #3E6FD8
GOLD = np.array([90, 193, 232], np.float32)     # BGR #E8C15A
GRAPHITE = np.array([38, 41, 43], np.float32)


def read_frames(path, idx, gray=False):
    cap = cv2.VideoCapture(path)
    out, i, want = {}, 0, set(idx)
    while want:
        ok, f = cap.read()
        if not ok:
            break
        if i in want:
            out[i] = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) if gray else f
            want.discard(i)
        i += 1
    return out


def twins(m):
    """split a matte into (left, right) girls: the two biggest components, else the widest empty column gap"""
    mb = (m > 127).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(mb)
    comps = sorted(range(1, n), key=lambda k: -st[k, cv2.CC_STAT_AREA])
    if len(comps) >= 2 and st[comps[1], cv2.CC_STAT_AREA] > 0.2 * st[comps[0], cv2.CC_STAT_AREA]:
        a, b = comps[:2]
        L, R = (a, b) if st[a, cv2.CC_STAT_LEFT] < st[b, cv2.CC_STAT_LEFT] else (b, a)
        # fold every small component (hair wisps, a pencil) into the nearer girl
        cl, cr = st[L, cv2.CC_STAT_LEFT] + st[L, cv2.CC_STAT_WIDTH] / 2, st[R, cv2.CC_STAT_LEFT] + st[R, cv2.CC_STAT_WIDTH] / 2
        left = lab == L
        right = lab == R
        for k in comps[2:]:
            c = st[k, cv2.CC_STAT_LEFT] + st[k, cv2.CC_STAT_WIDTH] / 2
            (left if abs(c - cl) < abs(c - cr) else right)[lab == k] = True
        return left, right, float((cl + cr) / 2)
    # touching (one component): split at the thinnest column in the middle 30-70 % of the pair (the joined hands)
    cs = mb.sum(0)
    xs = np.flatnonzero(cs)
    a, b = int(xs[0] + 0.3 * (xs[-1] - xs[0])), int(xs[0] + 0.7 * (xs[-1] - xs[0]))
    split = float(a + int(np.argmin(cs[a:b])))
    X = np.arange(m.shape[1])[None, :]
    return (mb > 0) & (X < split), (mb > 0) & (X >= split), float(split)


def costume(frame, m):
    """ORANGE (left): pale-blue dot -> orange. BLUE (right): every orange accent -> blue. Inside the mattes only."""
    left, right, split = twins(m)
    k = np.ones((5, 5), np.uint8)
    left = cv2.dilate(left.astype(np.uint8), k) > 0
    right = cv2.dilate(right.astype(np.uint8), k) > 0
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
    o, b, s, v = masks(hsv)
    to_blue = o & right
    to_orange = b & left
    hsv[..., 0][to_blue] = BLUE_H
    hsv[..., 1][to_blue] = np.clip(s[to_blue] * 0.86, 0, 1) * 255
    hsv[..., 2][to_blue] = np.clip(v[to_blue] * 0.93, 0, 1) * 255
    hsv[..., 0][to_orange] = ORANGE_H
    hsv[..., 1][to_orange] = np.clip(np.maximum(s[to_orange] * 1.6, 0.7), 0, 0.88) * 255
    hsv[..., 2][to_orange] = np.clip(np.maximum(v[to_orange], 0.92), 0, 1) * 255
    return cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR), split


def encode(frames, path):
    h, w = frames[0].shape[:2]
    p = subprocess.Popen([FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-pix_fmt", "yuv420p", path],
                         stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(f.tobytes())
    p.stdin.close()
    p.wait()


# ------------------------------------------------------------------------------------------------ triangle grid
def tri_grid(w, h, s):
    """equilateral triangles over the frame: list of (verts float32 (3,2), up: bool)"""
    rh = s * math.sqrt(3) / 2
    tris = []
    for r in range(int(h / rh) + 2):
        y0, y1 = r * rh, (r + 1) * rh
        off = (s / 2) if r % 2 else 0.0
        for c in range(-1, int(w / s) + 2):
            x = c * s + off
            tris.append((np.float32([[x, y1], [x + s, y1], [x + s / 2, y0]]), True))      # up
            tris.append((np.float32([[x + s / 2, y0], [x + 1.5 * s, y0], [x + s, y1]]), False))  # down
    return tris


def tiles_of(sprite_a, tris, thr=0.06):
    """the triangles a sprite covers: dict(verts, c, up, box, mask, cov)"""
    h, w = sprite_a.shape
    out = []
    for vt, up in tris:
        x0, y0 = np.floor(vt.min(0)).astype(int)
        x1, y1 = np.ceil(vt.max(0)).astype(int)
        if x1 <= 0 or y1 <= 0 or x0 >= w or y0 >= h:
            continue
        bx0, by0, bx1, by1 = max(x0, 0), max(y0, 0), min(x1, w), min(y1, h)
        tm = np.zeros((y1 - y0, x1 - x0), np.uint8)
        cv2.fillConvexPoly(tm, np.round((vt - [x0, y0]) * 16).astype(np.int32), 255, lineType=cv2.LINE_AA, shift=4)
        tm = tm[by0 - y0:by1 - y0, bx0 - x0:bx1 - x0].astype(np.float32) / 255
        a = sprite_a[by0:by1, bx0:bx1]
        cov = float((a * tm).sum() / max(tm.sum(), 1))
        if cov > thr:
            out.append(dict(verts=vt, c=vt.mean(0), up=up, box=(bx0, by0, bx1, by1), mask=tm, cov=cov))
    return out


def patch(rgb, a, t, pad=4):
    """RGBA float patch of tile t, centred on its centroid, padded so it can rotate: (img (k,k,4), half)"""
    x0, y0, x1, y1 = t["box"]
    half = int(math.ceil(S * 0.6)) + pad
    k = 2 * half
    P = np.zeros((k, k, 4), np.float32)
    cx, cy = t["c"]
    ox, oy = int(round(x0 - cx + half)), int(round(y0 - cy + half))
    al = a[y0:y1, x0:x1] * t["mask"]
    P[oy:oy + y1 - y0, ox:ox + x1 - x0, :3] = rgb[y0:y1, x0:x1].astype(np.float32) * al[..., None]
    P[oy:oy + y1 - y0, ox:ox + x1 - x0, 3] = al
    return P, half


def over(canvas, P, cx, cy):
    """premultiplied over at centre (cx, cy)"""
    k = P.shape[0]
    x0, y0 = int(round(cx - k / 2)), int(round(cy - k / 2))
    H, W = canvas.shape[:2]
    a0, b0 = max(0, -x0), max(0, -y0)
    a1, b1 = min(k, W - x0), min(k, H - y0)
    if a1 <= a0 or b1 <= b0:
        return
    dst = canvas[y0 + b0:y0 + b1, x0 + a0:x0 + a1]
    src = P[b0:b1, a0:a1]
    dst[:] = src + dst * (1 - src[..., 3:4])


def rot(P, deg, scale=1.0):
    k = P.shape[0]
    M = cv2.getRotationMatrix2D((k / 2, k / 2), deg, scale)
    return cv2.warpAffine(P, M, (k, k), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def smooth(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def ease_io(x):
    x = min(max(x, 0.0), 1.0)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def edges_img(tiles, shape, color, width, alpha_fn):
    """BGRA float overlay: each tile's outline, alpha by alpha_fn(tile)"""
    H, W = shape
    img = np.zeros((H, W, 4), np.float32)
    for t in tiles:
        a = alpha_fn(t)
        if a <= 0.01:
            continue
        lay = np.zeros((H, W), np.uint8)
        pts = np.round(t["verts"] * 16).astype(np.int32)
        cv2.polylines(lay, [pts], True, 255, width, cv2.LINE_AA, shift=4)
        x0, y0, x1, y1 = t["box"]
        sl = (slice(max(y0 - 3, 0), min(y1 + 3, H)), slice(max(x0 - 3, 0), min(x1 + 3, W)))
        aa = lay[sl].astype(np.float32) / 255 * a
        img[sl][..., 3] = np.maximum(img[sl][..., 3], aa)
    img[..., :3] = color[None, None, :] * img[..., 3:4]
    return img


def main(sheet=False):
    os.makedirs(os.path.join(OUT, "fig"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "seams"), exist_ok=True)
    idx = list(range(0, FREEZE + 6)) + [TARGET, 60, 100]
    F = read_frames(SRC, idx)
    M = read_frames(MATTE, idx, gray=True)
    H, W = F[0].shape[:2]

    # 1. the approach in costume
    bo, splits = [], []
    for i in range(0, FREEZE + 6):
        g, sp = costume(F[i], M[i])
        bo.append(g)
        splits.append(sp)
    encode(bo, os.path.join(OUT, "approach_bo.mp4"))

    # 2. the plate: per pixel the first frame whose (dilated) matte is clear there; inpaint what is left
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
    plate = np.zeros_like(F[0])
    todo = np.ones((H, W), bool)
    for i in (TARGET, 100, 60, 0, 2):
        clear = (cv2.dilate((M[i] > 40).astype(np.uint8), k) == 0) & todo
        plate[clear] = F[i][clear]
        todo &= ~clear
    if todo.any():
        plate = cv2.inpaint(plate, todo.astype(np.uint8) * 255, 9, cv2.INPAINT_TELEA)
    # the touch point is never clear (hands, then her body): patch it from the nano clean-plate edit of frame 40
    # (kf/plate_edit_v1.jpg, $0.134), registered onto the take by ORB + homography, only inside a feathered box
    # round the hands and the confetti burst, so a small drift in the edit cannot show
    ed = os.path.join(OUT, "kf", "plate_edit_v1.jpg")
    if os.path.exists(ed):
        E = cv2.imread(ed)
        orb = cv2.ORB_create(6000)
        g1, g2 = cv2.cvtColor(E, cv2.COLOR_BGR2GRAY), cv2.cvtColor(F[TARGET], cv2.COLOR_BGR2GRAY)
        k1, d1 = orb.detectAndCompute(g1, None)
        k2, d2 = orb.detectAndCompute(g2, None)
        mt = sorted(cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(d1, d2), key=lambda m: m.distance)[:1500]
        Hm, inl = cv2.findHomography(np.float32([k1[m.queryIdx].pt for m in mt]), np.float32([k2[m.trainIdx].pt for m in mt]),
                                     cv2.RANSAC, 3.0)
        Ew = cv2.warpPerspective(E, Hm, (W, H))
        box = np.zeros((H, W), np.float32)
        box[100:570, 740:1200] = 1
        box = cv2.GaussianBlur(box, (0, 0), 18)
        plate = (plate * (1 - box[..., None]) + Ew * box[..., None]).astype(np.uint8)
        print(f"plate patch: {int(inl.sum())} inliers of {len(mt)}")
    cv2.imwrite(os.path.join(OUT, "plate.png"), plate)

    # 3. sprites
    fz = bo[FREEZE]
    left, right, split = twins(M[FREEZE])
    a_all = M[FREEZE].astype(np.float32) / 255
    a_or = a_all * cv2.dilate(left.astype(np.uint8), np.ones((5, 5), np.uint8))
    a_bl = a_all * cv2.dilate(right.astype(np.uint8), np.ones((5, 5), np.uint8))
    tg = F[TARGET]
    a_tg = M[TARGET].astype(np.float32) / 255

    def bbox(a):
        ys, xs = np.nonzero(a > 0.5)
        return np.float32([xs.min(), ys.min(), xs.max(), ys.max()])

    b_or, b_bl, b_tg = bbox(a_or), bbox(a_bl), bbox(a_tg)
    # touch point: the facing hands (right edge of ORANGE, left edge of BLUE), at the height of the arms
    ys_or = np.nonzero((a_or[:, int(b_or[2]) - 14:int(b_or[2]) + 1] > 0.5).any(1))[0]
    ys_bl = np.nonzero((a_bl[:, int(b_bl[0]):int(b_bl[0]) + 15] > 0.5).any(1))[0]
    touch = np.float32([(b_or[2] + b_bl[0]) / 2, (np.mean(ys_or) + np.mean(ys_bl)) / 2])

    tris = tri_grid(W, H, S)
    T_or, T_bl, T_tg = tiles_of(a_or, tris), tiles_of(a_bl, tris), tiles_of(a_tg, tris)
    for t in T_or:
        t["P"], _ = patch(fz, a_or, t)
        t["col"] = ORANGE
    for t in T_bl:
        t["P"], _ = patch(fz, a_bl, t)
        t["col"] = BLUE
    for t in T_tg:
        t["P"], _ = patch(tg, a_tg, t)

    # 4. assignment: each piece goes to the target triangle at the same place on her body (bbox-normalised), so the
    #    two copies' pieces land interleaved on one girl; ORANGE is mirrored onto her left half first, BLUE her right
    def norm(c, b):
        return np.float32([(c[0] - b[0]) / (b[2] - b[0]), (c[1] - b[1]) / (b[3] - b[1])])

    tg_n = np.array([norm(t["c"], b_tg) for t in T_tg])
    got = np.zeros(len(T_tg), int)
    rng = np.random.default_rng(323)
    pieces = []
    for src_tiles, b, side in ((T_or, b_or, -1), (T_bl, b_bl, 1)):
        for t in src_tiles:
            n = norm(t["c"], b)
            d = ((tg_n - n) ** 2 * [1.0, 1.6]).sum(1) + got * 0.004    # spread the load a little
            j = int(np.argmin(d))
            got[j] += 1
            dst = T_tg[j]
            base = 0.0 if t["up"] == dst["up"] else 180.0
            spin = base + 120.0 * rng.integers(-2, 3)
            # one shared turning sense: every piece bows to the right of its own path, so ORANGE's pieces (moving
            # right) dip under and BLUE's (moving left) arc over: the two streams braid into each other
            d = dst["c"] - t["c"]
            L = float(np.linalg.norm(d)) + 1e-6
            perp = np.float32([-d[1], d[0]]) / L
            ctrl = (t["c"] + dst["c"]) / 2 + perp * (0.35 * L + rng.uniform(20, 90))
            dist = float(np.linalg.norm(t["c"] - touch))
            delay = 0.03 + 0.20 * min(dist / 420.0, 1.0) + rng.uniform(0, 0.05)
            pieces.append(dict(src=t, dst=dst, spin=spin, ctrl=ctrl, delay=delay, dur=rng.uniform(0.42, 0.5),
                               col=t["col"], j=j))
    pieces.sort(key=lambda p: p["delay"])      # first to leave drawn first, so late pieces fly over seated ones

    # 5. frames
    reach = max(np.linalg.norm(np.float32([x, y]) - touch) for x, y in
                [(b_or[0], b_or[1]), (b_or[0], b_or[3]), (b_bl[2], b_bl[1]), (b_bl[2], b_bl[3])])
    full_tg = np.zeros((H, W, 4), np.float32)
    full_tg[..., :3] = tg.astype(np.float32) * a_tg[..., None]
    full_tg[..., 3] = a_tg
    for f in range(N_FIG):
        t = f / FPS
        C = np.zeros((H, W, 4), np.float32)
        if t < T_SCORE:
            # the frozen twins, scored: graphite triangle lines sweep out from the touching hands
            for a in (a_or, a_bl):
                C[..., :3] += fz.astype(np.float32) * a[..., None]
                C[..., 3] += a
            C[..., 3] = np.clip(C[..., 3], 0, 1)
            R = reach * 1.05 * smooth(t / (T_SCORE - 0.06))
            ov = edges_img(T_or + T_bl, (H, W), GRAPHITE, 2, lambda q: smooth((R - np.linalg.norm(q["c"] - touch)) / 60.0))
            ov[..., 3] *= np.clip(C[..., 3], 0, 1)
            ov[..., :3] *= np.clip(C[..., 3:4], 0, 1)
            C = ov + C * (1 - ov[..., 3:4])
        else:
            lt = t - T_SCORE
            # the whole girl fills in under the seated pieces over the last 0.22 s
            fill = smooth((lt - (T_FLY - 0.30)) / 0.22)
            if fill > 0:
                C += full_tg * fill
            for p in pieces:
                u = (lt - p["delay"]) / p["dur"]
                if u < 0:
                    # not yet lifted: sits where it was (the twin dissolves outward-in, pieces nearest the hands first)
                    P = p["src"]["P"].copy()
                    e = edges_one(P.shape[0], p["src"], 0.0, GRAPHITE, 0.8)
                    P = e + P * (1 - e[..., 3:4])
                    over(C, P, *p["src"]["c"])
                    continue
                e = ease_io(u)
                q = (1 - e) ** 2 * p["src"]["c"] + 2 * (1 - e) * e * p["ctrl"] + e ** 2 * p["dst"]["c"]
                ang = p["spin"] * e
                lift = 1.0 + 0.18 * math.sin(math.pi * min(u, 1.0))
                mix = smooth((u - 0.35) / 0.5)
                Ps = rot(p["src"]["P"], ang, lift)
                Pd = rot(p["dst"]["P"], ang - p["spin"], lift)
                P = Ps * (1 - mix) + Pd * mix
                # its copy's colour: a glow on the piece and its outline, strongest mid-flight
                glow = 0.4 * math.sin(math.pi * min(u, 1.0))
                if glow > 0:
                    P[..., :3] = P[..., :3] * (1 - glow) + p["col"][None, None, :] * P[..., 3:4] * glow
                seam_a = 0.95 * (1 - smooth((u - 1.0) / 0.5)) if u < 1.5 else 0.0
                if seam_a > 0:
                    col = p["col"] * (1 - smooth(u - 0.6)) + GOLD * smooth(u - 0.6) if u < 1.6 else GOLD
                    eo = edges_one(P.shape[0], p["dst"] if mix > 0.5 else p["src"], ang - (p["spin"] if mix > 0.5 else 0),
                                   col, seam_a, scale=lift)
                    P = eo + P * (1 - eo[..., 3:4])
                over(C, P, *q)
            if fill > 0.999:
                C = full_tg.copy()
        out = np.zeros((H, W, 4), np.uint8)
        a = np.clip(C[..., 3:4], 1e-6, 1)
        out[..., :3] = np.clip(C[..., :3] / a, 0, 255).astype(np.uint8)
        out[..., 3] = np.clip(C[..., 3] * 255, 0, 255).astype(np.uint8)
        cv2.imwrite(os.path.join(OUT, "fig", f"{f:05d}.png"), out)
    open(os.path.join(OUT, "fig", "fps.txt"), "w").write(str(FPS))

    # 6. seams: gold triangle lines on the merged girl, fading
    for f in range(N_SEAM):
        a = 1.0 - f / N_SEAM
        ov = edges_img(T_tg, (H, W), GOLD, 2, lambda q: a)
        ov[..., 3] *= np.clip(a_tg * 1.2, 0, 1)
        out = np.zeros((H, W, 4), np.uint8)
        out[..., :3] = GOLD.astype(np.uint8)
        out[..., 3] = np.clip(ov[..., 3] * 255, 0, 255).astype(np.uint8)
        cv2.imwrite(os.path.join(OUT, "seams", f"{f:05d}.png"), out)
    open(os.path.join(OUT, "seams", "fps.txt"), "w").write(str(FPS))

    lay = dict(touch=[float(touch[0]), float(touch[1])], split=split, bbox_orange=b_or.tolist(), bbox_blue=b_bl.tolist(),
               bbox_target=b_tg.tolist(), tiles=dict(orange=len(T_or), blue=len(T_bl), target=len(T_tg)),
               target_tiles_without_piece=int((got == 0).sum()), freeze=FREEZE, target=TARGET, S=S, frames=N_FIG)
    json.dump(lay, open(os.path.join(OUT, "layout.json"), "w"), indent=1)
    print(json.dumps(lay))
    if sheet:
        make_sheet(plate)


def edges_one(k, t, deg, color, alpha, scale=1.0):
    """BGRA premultiplied outline of tile t, in a k x k patch centred on its centroid, rotated by deg"""
    lay = np.zeros((k, k), np.uint8)
    pts = np.round((t["verts"] - t["c"] + k / 2) * 16).astype(np.int32)
    cv2.polylines(lay, [pts], True, 255, 2, cv2.LINE_AA, shift=4)
    if deg or scale != 1.0:
        lay = cv2.warpAffine(lay, cv2.getRotationMatrix2D((k / 2, k / 2), deg, scale), (k, k))
    a = lay.astype(np.float32) / 255 * alpha
    E = np.zeros((k, k, 4), np.float32)
    E[..., :3] = np.asarray(color, np.float32)[None, None, :] * a[..., None]
    E[..., 3] = a
    return E


def make_sheet(plate):
    fr = [0, 8, 12, 15, 18, 21, 24, 27, 31]
    tiles = []
    for f in fr:
        im = cv2.imread(os.path.join(OUT, "fig", f"{f:05d}.png"), cv2.IMREAD_UNCHANGED).astype(np.float32)
        a = im[..., 3:4] / 255
        c = im[..., :3] * a + plate.astype(np.float32) * (1 - a)
        c = cv2.resize(c.astype(np.uint8), (640, 360))
        cv2.putText(c, f"{203.32 + f / FPS:.2f}", (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        tiles.append(c)
    rows = [np.hstack(tiles[i:i + 3]) for i in range(0, 9, 3)]
    cv2.imwrite(os.path.join(OUT, "fig_sheet.jpg"), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 88])


if __name__ == "__main__":
    main("--sheet" in sys.argv)
