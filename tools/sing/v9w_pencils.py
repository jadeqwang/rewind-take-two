#!/usr/bin/env python3
"""Singing Jade (v9w), S1: the two pencils keyed into the per-frame matte of a painted take, plus loose pieces removed.

v5_pencils.py's thresholds are for photographic takes; in the watercolour takes the erasers are pale (pink S ~40-80,
pale blue S ~15-40) and BiRefNet drops both erasers and most of the pink-eraser pencil. Per frame (720p take frames are
scaled to the 1080 matte):
  (round 2, the one used) each whole pencil (body + ferrule + eraser) is taken from the first frame
     (media/sing/first/v9w_S1_first.jpg, v5_pencils.key on her solid head) and moved rigidly with its yellow body in every
     frame (centre shift + axis rotation): the pale-blue eraser is too grey to key by colour in the painted takes.
  (round 1, replaced) 1. yellow pencil bodies: H 10-30, S > 100, V > 120, components >= 40 px, within 260 px above the matte's head top and
     near the head (BiRefNet's top-of-head region), at most two (largest);
  2. each body is grown by the pixels within 45 px of it that are tinted (S > 16, V > 140; the engraved plate is grey,
     S < 12) or yellow, and the convex hull of body + those pixels is the pencil (so the silver ferrule between body and
     eraser is in it);
  3. alpha = max(BiRefNet, hull), with a 1 px soft edge;
  4. detached pieces of matte (> 15 px) that are not a pencil and lie more than 8 px from her main silhouette are removed
     (the take's own plate fragments that BiRefNet picked up left of her head).
The BiRefNet originals are kept once in <matte>_birefnet/.

    EPY=tools/engrave/.venv/bin/python
    $EPY tools/sing/v9w_pencils.py media/sing/S1/v9w_take_4.mp4 media/sing/S1/v9w_take_4_matte
"""
import os
import shutil
import sys

import cv2
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIRST = os.path.join(ROOT, "media/sing/first/v9w_S1_first.jpg")
FIRST_MASK = os.path.join(ROOT, "media/sing/first/v9w_her_mask_first_frame_S1.png")


def bodies(rgb, a8, prev=None):
    """Yellow pencil bodies near the top of her head (not skin: skin lies inside her solid matte, a8 = 255)."""
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(np.int32)
    H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    ys = np.nonzero(a8 > 128)[0]
    top = int(ys.min()) if len(ys) else 0
    zone = np.zeros(a8.shape, bool)
    zone[max(0, top - 200):top + 170] = True
    yellow = (H >= 10) & (H <= 30) & (S > 100) & (V > 120) & zone & (a8 < 230)
    yellow = cv2.morphologyEx(yellow.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(yellow)
    out = []
    for k in range(1, n):
        if st[k, 4] < 30:
            continue
        yx = np.column_stack(np.nonzero(lab == k)).astype(np.float32)
        c = yx.mean(0)
        _, _, vt = np.linalg.svd(yx - c, full_matrices=False)
        out.append(dict(c=c[::-1], ax=vt[0][::-1], area=int(st[k, 4])))
    return sorted(out, key=lambda b: -b["area"])[:2]


def templates(first_rgb, first_a8):
    """Whole pencils (body + ferrule + eraser) on the first frame, from v5_pencils.key on her solid head."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from v5_pencils import key
    solid = cv2.morphologyEx((first_a8 > 240).astype(np.uint8), cv2.MORPH_OPEN, np.ones((15, 15), np.uint8)) * 255.0
    k = (key(first_rgb, solid.astype(np.float32)) > 0.3).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(k)
    T = []
    head = cv2.morphologyEx((first_a8 > 240).astype(np.uint8), cv2.MORPH_OPEN, np.ones((25, 25), np.uint8))
    hsv = cv2.cvtColor(first_rgb, cv2.COLOR_RGB2HSV).astype(np.int32)
    Y = (hsv[..., 0] >= 10) & (hsv[..., 0] <= 30) & (hsv[..., 1] > 100) & (hsv[..., 2] > 120)
    top = int(np.nonzero(first_a8 > 128)[0].min())
    Y[top + 170:] = False
    ny, laby, sty, _ = cv2.connectedComponentsWithStats(Y.astype(np.uint8))
    cand = []
    for kk in range(1, ny):
        sel = laby == kk
        if sty[kk, 4] >= 50 and head[sel].mean() < 0.9:              # a body, not warm skin inside her head
            yx = np.column_stack(np.nonzero(sel)).astype(np.float32)
            cc = yx.mean(0)
            _, _, vt = np.linalg.svd(yx - cc, full_matrices=False)
            cand.append(dict(c=cc[::-1], ax=vt[0][::-1], area=int(sty[kk, 4])))
    for b in sorted(cand, key=lambda b: -b["area"])[:2]:
        x, y = int(b["c"][0]), int(b["c"][1])
        win = lab[max(0, y - 30):y + 30, max(0, x - 30):x + 30]
        ids = [v for v in np.unique(win) if v]
        if ids:
            m = np.isin(lab, ids).astype(np.uint8) * 255
        else:                                       # no key component: body + nearby eraser-hued pixels, convex hull
            bx = (laby == laby[y, x]) if laby[y, x] else np.zeros_like(Y)
            reach = cv2.dilate(bx.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (121, 121))) > 0
            Hh, Ss, Vv = hsv[..., 0], hsv[..., 1], hsv[..., 2]
            er = ((((Hh >= 88) & (Hh <= 125)) | (Hh >= 150) | (Hh <= 6)) & (Ss > 15) & (Vv > 140)) & reach & (head == 0)
            # only along the pencil: within 11 px of the body's axis line, up to 75 px from its centre
            yy, xx = np.mgrid[0:first_a8.shape[0], 0:first_a8.shape[1]].astype(np.float32)
            dx, dy = xx - b["c"][0], yy - b["c"][1]
            along = dx * b["ax"][0] + dy * b["ax"][1]
            perp = np.abs(-dx * b["ax"][1] + dy * b["ax"][0])
            er &= (perp < 11) & (np.abs(along) < 75)
            pts = np.column_stack(np.nonzero(er | bx))[:, ::-1].astype(np.int32)
            m = np.zeros(first_a8.shape, np.uint8)
            if len(pts) >= 3:
                cv2.fillConvexPoly(m, cv2.convexHull(pts), 255)
        T.append(dict(b, mask=m))
    return T


def place(T, cur):
    """Move each template pencil onto the nearest current body (rigid: shift + rotation about the body centre)."""
    out = np.zeros(T[0]["mask"].shape, np.uint8) if T else None
    used = set()
    for t in T:
        if not cur:
            break
        j = min((j for j in range(len(cur)) if j not in used), key=lambda j: np.linalg.norm(cur[j]["c"] - t["c"]), default=None)
        if j is None or np.linalg.norm(cur[j]["c"] - t["c"]) > 120:
            continue
        used.add(j)
        b = cur[j]
        a0, a1 = np.arctan2(t["ax"][1], t["ax"][0]), np.arctan2(b["ax"][1], b["ax"][0])
        d = (a1 - a0 + np.pi / 2) % np.pi - np.pi / 2                      # axis has no sign
        if abs(d) > 0.5:
            d = 0.0
        M = cv2.getRotationMatrix2D((float(t["c"][0]), float(t["c"][1])), -np.degrees(d), 1.0)
        M[:, 2] += b["c"] - t["c"]
        out = np.maximum(out, cv2.warpAffine(t["mask"], M, (out.shape[1], out.shape[0]), flags=cv2.INTER_LINEAR))
    return out, len(used)


def track(T, first_rgb, rgb, state):
    """Round 3 (used for the wired file): each first-frame pencil (its RGB patch + mask) is found in the take frame by
    masked template matching, position within 60 px of its last place and rotation -20..+20 deg in 4 deg steps; the
    yellow-body centroid alone shifts when hair hides part of the body. A weak match (< 0.90) keeps the last placement."""
    out = np.zeros(rgb.shape[:2], np.uint8)
    found = 0
    for j, t in enumerate(T):
        ys, xs = np.nonzero(t["mask"])
        if not len(ys):
            continue
        pad = 12
        y0, y1, x0, x1 = ys.min() - pad, ys.max() + pad, xs.min() - pad, xs.max() + pad
        patch = first_rgb[y0:y1, x0:x1].astype(np.float32)
        pm = (t["mask"][y0:y1, x0:x1] > 0).astype(np.float32)
        cy, cx = (y0 + y1) / 2, (x0 + x1) / 2
        last = state.get(j, (0.0, 0.0, 0.0))
        best = (-1, None)
        for ang in range(-20, 21, 4):
            R = cv2.getRotationMatrix2D(((x1 - x0) / 2, (y1 - y0) / 2), ang, 1.0)
            pr = cv2.warpAffine(patch, R, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR)
            mr = cv2.warpAffine(pm, R, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR)
            sy0, sx0 = int(y0 + last[1] - 60), int(x0 + last[0] - 60)
            win = rgb[max(0, sy0):sy0 + (y1 - y0) + 120, max(0, sx0):sx0 + (x1 - x0) + 120].astype(np.float32)
            if win.shape[0] < pr.shape[0] or win.shape[1] < pr.shape[1]:
                continue
            r = cv2.matchTemplate(win, pr, cv2.TM_CCORR_NORMED, mask=np.repeat(mr[..., None], 3, 2))
            r = np.nan_to_num(r, nan=-1, posinf=-1, neginf=-1)
            _, v, _, loc = cv2.minMaxLoc(r)
            if v > best[0]:
                dx = max(0, sx0) + loc[0] - x0
                dy = max(0, sy0) + loc[1] - y0
                best = (v, (float(dx), float(dy), float(ang)))
        if best[1] is not None and best[0] >= 0.90:
            state[j] = best[1]
            found += 1
        dx, dy, ang = state.get(j, (0.0, 0.0, 0.0))
        M = cv2.getRotationMatrix2D((float(cx), float(cy)), ang, 1.0)
        M[:, 2] += (dx, dy)
        out = np.maximum(out, cv2.warpAffine(t["mask"], M, (out.shape[1], out.shape[0]), flags=cv2.INTER_LINEAR))
    return out, found


def clean(a8, keep):
    b = (a8 > 60).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(b)
    if n < 3:
        return a8, 0
    big = 1 + int(np.argmax(st[1:, 4]))
    near = cv2.dilate((lab == big).astype(np.uint8), np.ones((17, 17), np.uint8)) > 0
    out = a8.copy()
    removed = 0
    for k in range(1, n):
        if k == big or st[k, 4] < 15:
            continue
        comp = lab == k
        if (comp & (keep > 0)).any() or (comp & near).any():
            continue
        out[cv2.dilate(comp.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0] = 0
        removed += 1
    return out, removed


def main(src, mdir):
    import av
    bak = mdir.rstrip("/") + "_birefnet"
    if not os.path.exists(bak):
        shutil.copytree(mdir, bak)
    counts, rem = [], 0
    fr = np.asarray(Image.open(FIRST).convert("RGB").resize((1920, 1080), Image.LANCZOS))
    fa = np.asarray(Image.open(FIRST_MASK).convert("L").resize((1920, 1080), Image.BILINEAR))
    T = templates(fr, fa)
    print("templates:", [(np.round(t["c"]).tolist(), int((t["mask"] > 0).sum())) for t in T])
    state = {}
    with av.open(src) as c:
        for i, f in enumerate(c.decode(c.streams.video[0])):
            p = os.path.join(bak, f"{i:05d}.png")
            if not os.path.exists(p):
                break
            a8 = np.asarray(Image.open(p))
            rgb = np.asarray(Image.fromarray(f.to_ndarray(format="rgb24")).resize((a8.shape[1], a8.shape[0]), Image.LANCZOS))
            pk, nb = track(T, fr, rgb, state) if T else (np.zeros_like(a8), 0)
            a = np.maximum(a8, cv2.GaussianBlur(pk, (0, 0), 0.8))
            a, r = clean(a, pk)
            rem += r
            counts.append(nb)
            Image.fromarray(a).save(os.path.join(mdir, f"{i:05d}.png"))
    c = np.array(counts)
    print(os.path.relpath(mdir), len(c), "frames; pencils matched (>= 0.90) per frame: 2 in", int((c == 2).sum()), ", 1 in",
          int((c == 1).sum()), ", 0 in", int((c == 0).sum()), "; loose pieces removed:", rem)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
