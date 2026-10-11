#!/usr/bin/env python3
"""Planar corner-pin tracker for the engine's `pin`/`etch` modules (Section A: D1 gantry sign, D2 rooftop sign,
D5 sunglasses, D7 ID card).

    tools/engrave/.venv/bin/python tools/sectionA/track_quad.py VIDEO.mp4 --corners x1,y1,...,x4,y4 [--frame F]
        [--region pad] [--from 0.0 --to 4.0] [--in 0.0 --rate 1.0] [--step 2] --out track.json

Corners are TL,TR,BR,BL in 1920x1080 DESIGN pixels of the frame `--frame` (default 0) as the engine draws a 16:9
video with fit 'cover'. Points inside the quad (dilated by --region, a fraction of its size) are tracked with
pyramidal Lucas-Kanade frame to frame (forwards and backwards from --frame), a RANSAC homography per step maps the
corners. Output JSON: {"keys": [[layer_t, [8 numbers]], ...]} where layer_t = (video_t - in) / rate, ready to paste
as `corners` keys. Also writes OUT.jpg: the quad drawn on 6 frames for review.
"""
import argparse
import json
import os

import cv2
import numpy as np


def read_frames(path):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    out = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        out.append(f)
    return out, fps


def track(frames, q0, f0, pad):
    h, w = frames[0].shape[:2]
    gray = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in frames]
    quads = {f0: q0.copy()}

    def mask_for(q):
        c = q.mean(0)
        qq = c + (q - c) * (1 + pad)
        m = np.zeros((h, w), np.uint8)
        cv2.fillConvexPoly(m, qq.astype(np.int32), 255)
        return m

    for direction in (1, -1):
        q = q0.copy()
        k = f0
        pts = cv2.goodFeaturesToTrack(gray[k], 400, 0.005, 5, mask=mask_for(q))
        while 0 <= k + direction < len(frames):
            n = k + direction
            if pts is None or len(pts) < 12:
                pts = cv2.goodFeaturesToTrack(gray[k], 400, 0.005, 5, mask=mask_for(q))
                if pts is None:
                    break
            nxt, st, _ = cv2.calcOpticalFlowPyrLK(gray[k], gray[n], pts, None, winSize=(31, 31), maxLevel=4)
            back, st2, _ = cv2.calcOpticalFlowPyrLK(gray[n], gray[k], nxt, None, winSize=(31, 31), maxLevel=4)
            good = (st[:, 0] == 1) & (st2[:, 0] == 1) & (np.linalg.norm(back - pts, axis=2)[:, 0] < 1.0)
            a, b = pts[good], nxt[good]
            if len(a) >= 8:
                H, inl = cv2.findHomography(a, b, cv2.RANSAC, 2.0)
            else:
                H = None
            if H is None:
                if len(a) >= 3:  # fall back to similarity
                    M, _ = cv2.estimateAffinePartial2D(a, b)
                    H = np.vstack([M, [0, 0, 1]]) if M is not None else np.eye(3)
                else:
                    H = np.eye(3)
            q = cv2.perspectiveTransform(q[None].astype(np.float64), H)[0]
            quads[n] = q.copy()
            pts = b.reshape(-1, 1, 2)
            k = n
            if k % 6 == 0:  # refresh features inside the moving quad
                pts = cv2.goodFeaturesToTrack(gray[k], 400, 0.005, 5, mask=mask_for(q))
    return quads


def track_template(frames, q0, f0, pad):
    """Translation-only tracking by normalised cross-correlation of the (padded) quad patch; for fast-moving,
    flickering subjects LK loses (D2's bulb-lined sign)."""
    h, w = frames[0].shape[:2]
    gray = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in frames]
    c = q0.mean(0)
    qq = c + (q0 - c) * (1 + pad)
    x0, y0 = np.floor(qq.min(0)).astype(int)
    x1, y1 = np.ceil(qq.max(0)).astype(int)
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(w, x1), min(h, y1)
    tpl = gray[f0][y0:y1, x0:x1]
    quads = {f0: q0.copy()}
    for direction in (1, -1):
        off = np.zeros(2)
        k = f0
        while 0 <= k + direction < len(frames):
            n = k + direction
            # search the whole frame band (the sign moves up to ~1/6 frame per step)
            r = cv2.matchTemplate(gray[n], tpl, cv2.TM_CCOEFF_NORMED)
            _, mv, _, ml = cv2.minMaxLoc(r)
            if mv < 0.35:
                break
            new = np.array([ml[0] - x0, ml[1] - y0], float)
            steps = [np.abs(quads[j] - quads[j - direction]).max() for j in quads if j - direction in quads]
            med = np.median(steps[-6:]) if len(steps) >= 6 else None
            if med is not None and np.abs(new - off).max() > 3 * max(med, 10) + 20:
                break  # lost it (occluded or out of frame): stop, the caller extrapolates
            off = new
            quads[n] = q0 + off
            k = n
        # extrapolate the remaining frames with the mean velocity of the last 4 tracked frames
        last = sorted(j for j in quads if (j - f0) * direction >= 0)
        if direction < 0:
            last = last[::-1]
        if len(last) >= 5:
            v = (quads[last[-1]] - quads[last[-5]]) / 4
            q = quads[last[-1]].copy()
            j = last[-1] + direction
            while 0 <= j < len(frames):
                q = q + v
                quads[j] = q.copy()
                j += direction
    return quads


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--corners", required=True)
    ap.add_argument("--frame", type=int, default=0)
    ap.add_argument("--region", type=float, default=0.3)
    ap.add_argument("--in", dest="clip_in", type=float, default=0.0)
    ap.add_argument("--rate", type=float, default=1.0)
    ap.add_argument("--from", dest="t0", type=float, default=0.0)
    ap.add_argument("--to", dest="t1", type=float, default=1e9)
    ap.add_argument("--step", type=int, default=1)
    ap.add_argument("--mode", default="lk", choices=["lk", "template"])
    ap.add_argument("--jerk", type=float, default=12.0, help="px (video) tolerance before the track is distrusted")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    frames, fps = read_frames(a.video)
    h, w = frames[0].shape[:2]
    # design (1920x1080, cover) <-> video pixels
    s = max(1920 / w, 1080 / h)
    ox, oy = (1920 - w * s) / 2, (1080 - h * s) / 2
    c = np.array([float(v) for v in a.corners.split(",")]).reshape(4, 2)
    q0 = (c - [ox, oy]) / s
    quads = (track_template if a.mode == "template" else track)(frames, q0, a.frame, a.region)
    # once the quad has left the frame, the track is garbage: stop at the first fully-outside frame (going away
    # from --frame in both directions)
    def outside(q):
        d = q * s + [ox, oy]
        return (d[:, 1] < 0).all() or (d[:, 1] > 1080).all() or (d[:, 0] < 0).all() or (d[:, 0] > 1920).all()
    hi = max(quads)
    for i in range(a.frame, max(quads) + 1):
        if i in quads and outside(quads[i]):
            hi = i
            break
    lo = min(quads)
    for i in range(a.frame, min(quads) - 1, -1):
        if i in quads and outside(quads[i]):
            lo = i
            break
    quads = {i: q for i, q in quads.items() if lo <= i <= hi}
    # forward from --frame: stop trusting the track at the first jerk (corner jump far off the predicted motion) and
    # extrapolate with the last velocity, growing it by the last acceleration ratio, so the quad keeps flying out
    fr = sorted(i for i in quads if i >= a.frame)
    for n in range(3, len(fr)):
        i = fr[n]
        p0, p1, p2 = quads[fr[n - 3]], quads[fr[n - 2]], quads[fr[n - 1]]
        v1, v2 = p1 - p0, p2 - p1
        pred = p2 + v2 + (v2 - v1)
        err = np.abs(quads[i] - pred).max()
        step = np.abs(quads[i] - p2).max()
        if err > a.jerk and err > 1.5 * step:
            # velocity over the last 4 good frames (Seedance repeats frames, single steps can be zero)
            k0 = max(0, n - 5)
            v = (p2 - quads[fr[k0]]) / max(1, (n - 1 - k0))
            vprev = (quads[fr[max(0, k0 - 4)]] - quads[fr[max(0, k0 - 4) - 0]] if False else None)
            g = 1.12
            q = p2.copy()
            for j in fr[n:]:
                v = v * g
                q = q + v
                quads[j] = q.copy()
            print("extrapolated from frame", i)
            break
    keys = []
    for i in sorted(quads):
        vt = i / fps
        if vt < a.t0 - 1e-6 or vt > a.t1 + 1e-6 or (i - a.frame) % a.step:
            continue
        d = quads[i] * s + [ox, oy]
        keys.append([round((vt - a.clip_in) / a.rate, 4), [round(float(v), 1) for v in d.reshape(-1)]])
    json.dump({"video": a.video, "fps": fps, "keys": keys}, open(a.out, "w"))
    # review sheet
    idx = [round(i * (len(frames) - 1) / 5) for i in range(6)]
    tiles = []
    for i in idx:
        f = frames[i].copy()
        if i in quads:
            cv2.polylines(f, [quads[i].astype(np.int32)], True, (0, 0, 255), 2)
        tiles.append(cv2.resize(f, (640, round(640 * h / w))))
    sheet = np.vstack([np.hstack(tiles[:3]), np.hstack(tiles[3:])])
    cv2.imwrite(os.path.splitext(a.out)[0] + ".jpg", sheet)
    print(a.out, len(keys), "keys")


if __name__ == "__main__":
    main()
