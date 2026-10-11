#!/usr/bin/env python3
"""Costume pass for the Banach-Tarski twins (Jade, v4): ORANGE keeps the orange accents and gets orange dots; BLUE gets
blue stripes, straps, headphones and dots. ORANGE is always the girl further LEFT, so the pass works on screen position:
right of the split every saturated orange pixel turns blue (#3E6FD8), left of it every bright pale-blue pixel turns
orange (#F08A24). The world is a black-and-white engraving, so colour alone finds the girls; nothing else is touched.

    tools/engrave/.venv/bin/python tools/v4B/coop/recolor.py SRC.mp4 DST.mp4 [--split=960 | --split=auto] [--check=out.jpg]
    --split=N     a fixed column (the E6c take, where they run apart from the middle)
    --split=auto  per frame: the widest empty column gap between the two girls' coloured pixels, smoothed over time
    --plan=A-B:S:M,...  per frame range A..B (frame numbers): split S (number or auto) and mode M, "ob" (left stays
                  ORANGE, right becomes BLUE; the default) or "bo" (left becomes BLUE, right stays ORANGE: after the
                  girls swap sides, as in the C2 take from about 3.7 s)
    --splits=out.json  write the per-frame split columns and modes (the matte splitter reads them)
"""
import json
import os
import subprocess
import sys

import cv2
import numpy as np

FFMPEG = os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg")
BLUE_H, ORANGE_H = 221 / 2.0, 28 / 2.0          # OpenCV hue = degrees / 2


def masks(hsv):
    h, s, v = hsv[..., 0] * 2.0, hsv[..., 1] / 255.0, hsv[..., 2] / 255.0
    orange = ((h >= 4) & (h <= 36) & (s >= 0.45) & (v >= 0.35)).astype(np.uint8)   # <=36: the yellow bun pencils stay yellow
    blue = ((h >= 185) & (h <= 240) & (s >= 0.25) & (v >= 0.58)).astype(np.uint8)
    # soft fringe: anti-aliased edge pixels of the same hue within 2 px of a core pixel
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    o_f = (cv2.dilate(orange, k) > 0) & (h >= 0) & (h <= 38) & (s >= 0.2) & (v >= 0.3)
    b_f = (cv2.dilate(blue, k) > 0) & (h >= 180) & (h <= 245) & (s >= 0.14) & (v >= 0.5)
    return o_f, b_f, s, v


def auto_split(o, b, w, prev):
    """the widest gap between coloured columns; None if there is only one cluster"""
    cols = (o | b).sum(0) > 3
    xs = np.flatnonzero(cols)
    if len(xs) < 2:
        return prev
    gaps = np.diff(xs)
    i = int(np.argmax(gaps))
    if gaps[i] < 24:
        return prev
    return 0.5 * (xs[i] + xs[i + 1])


def recolor(frame, split, stats=None, mode="ob"):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
    o, b, s, v = masks(hsv)
    X = np.arange(frame.shape[1])[None, :]
    blue_side = (X >= split) if mode == "ob" else (X < split)
    to_blue = o & blue_side
    to_orange = b & ~blue_side
    hsv[..., 0][to_blue] = BLUE_H
    hsv[..., 1][to_blue] = np.clip(s[to_blue] * 0.86, 0, 1) * 255
    hsv[..., 2][to_blue] = np.clip(v[to_blue] * 0.93, 0, 1) * 255
    hsv[..., 0][to_orange] = ORANGE_H
    hsv[..., 1][to_orange] = np.clip(np.maximum(s[to_orange] * 1.6, 0.7), 0, 0.88) * 255
    hsv[..., 2][to_orange] = np.clip(np.maximum(v[to_orange], 0.92), 0, 1) * 255
    if stats is not None:
        stats.append((int(to_blue.sum()), int(to_orange.sum())))
    return cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)


def main(src, dst, split="960", check=None, plan="", splits_out=None):
    cap = cv2.VideoCapture(src)
    w, h = int(cap.get(3)), int(cap.get(4))
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    frames = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(f)
    if split == "auto":
        sp, prev = [], w / 2
        for f in frames:
            o, b, _, _ = masks(cv2.cvtColor(f, cv2.COLOR_BGR2HSV).astype(np.float32))
            prev = auto_split(o, b, w, prev)
            sp.append(prev)
        sp = np.convolve(np.pad(sp, 2, mode="edge"), np.ones(5) / 5, mode="valid")
    else:
        sp = [float(split)] * len(frames)
    modes = ["ob"] * len(frames)
    if plan:
        sp = list(sp)
        for item in plan.split(","):
            rng, s_, m_ = item.split(":")
            a, b = (int(x) for x in rng.split("-"))
            prev = w / 2
            for i in range(a, min(b, len(frames) - 1) + 1):
                if s_ == "auto":
                    o, bb, _, _ = masks(cv2.cvtColor(frames[i], cv2.COLOR_BGR2HSV).astype(np.float32))
                    prev = auto_split(o, bb, w, prev)
                    sp[i] = prev
                else:
                    sp[i] = float(s_)
                modes[i] = m_
    if splits_out:
        json.dump(dict(split=[float(x) for x in sp], mode=modes), open(splits_out, "w"))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    enc = subprocess.Popen([FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}", "-r", f"{fps}",
                            "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-pix_fmt", "yuv420p", dst],
                           stdin=subprocess.PIPE)
    stats, outs = [], []
    for f, x, m_ in zip(frames, sp, modes):
        g = recolor(f, x, stats, m_)
        enc.stdin.write(g.tobytes())
        if check:
            outs.append(g)
    enc.stdin.close()
    enc.wait()
    print(f"{dst}: {len(frames)} frames {w}x{h} @ {fps:g}; split {sp[0]:.0f}..{sp[-1]:.0f}; "
          f"px to blue max {max(s[0] for s in stats)}, to orange max {max(s[1] for s in stats)}")
    if check:
        idx = np.linspace(0, len(frames) - 1, 6).astype(int)
        rows = [np.hstack([cv2.resize(frames[i], (640, 360)), cv2.resize(outs[i], (640, 360))]) for i in idx]
        for r, i in zip(rows, idx):
            cv2.line(r, (int(sp[i] / w * 640) + 640, 0), (int(sp[i] / w * 640) + 640, 12), (0, 0, 255), 2)
        cv2.imwrite(check, np.vstack(rows))


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    o = {x[2:].partition("=")[0]: x[2:].partition("=")[2] for x in sys.argv[1:] if x.startswith("--")}
    main(a[0], a[1], o.get("split", "960"), o.get("check"), o.get("plan", ""), o.get("splits"))
