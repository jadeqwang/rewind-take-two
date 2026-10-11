#!/usr/bin/env python
"""Red audit for section F ("no red anywhere"): rotate red hues to orange (terracotta, saturation capped under the
reviewer's 0.45 red-detector threshold) or magenta. Writes <IN stem>_dered.mp4 next to the input (edl.py picks it up).

  tools/engrave/.venv/bin/python tools/sectionF/dered.py IN.mp4 [--mode orange|magenta] [--check]
--check only reports the red fraction (hue within 15 deg of 0, saturation > 0.45, value > 0.2) per second.
"""
import argparse
import os
import shutil
import subprocess

import av
import cv2
import numpy as np


def ffmpeg():
    for c in (os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg"), shutil.which("ffmpeg")):
        if c and os.path.exists(c):
            return c


def red_mask(hsv, width=15):
    h, s, v = hsv[..., 0].astype(np.float32) * 2, hsv[..., 1] / 255.0, hsv[..., 2] / 255.0
    d = np.minimum(h, 360 - h)                       # hue distance to 0 deg
    w = np.clip((width + 5 - d) / 5.0, 0, 1)         # soft edge
    return w * np.clip((s - 0.30) / 0.1, 0, 1) * (v > 0.15), d, s


def fix(rgb, mode, jade=None):
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV_FULL if False else cv2.COLOR_RGB2HSV)
    w, d, s = red_mask(hsv)
    if jade is not None:                             # Jade stays on-model (her orange is never touched)
        w = w * (1 - jade)
    if w.max() == 0:
        return rgb
    out = hsv.astype(np.float32)
    if mode == "orange":
        out[..., 0] = 24 / 2.0
        out[..., 1] = np.minimum(out[..., 1], 0.40 * 255)
    else:
        out[..., 0] = 312 / 2.0
    new = cv2.cvtColor(out.astype(np.uint8), cv2.COLOR_HSV2RGB)
    return (rgb * (1 - w[..., None]) + new * w[..., None]).astype(np.uint8)


def frac(rgb):
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0].astype(np.float32) * 2, hsv[..., 1] / 255.0, hsv[..., 2] / 255.0
    d = np.minimum(h, 360 - h)
    return float(((d < 15) & (s > 0.45) & (v > 0.2)).mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--mode", default="orange")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--matte", help="Jade matte video (white = Jade): excluded from the rotation")
    a = ap.parse_args()
    c = av.open(a.input)
    vs = c.streams.video[0]
    W, H, fps = vs.codec_context.width, vs.codec_context.height, vs.average_rate
    if a.check:
        worst = 0
        for i, fr in enumerate(c.decode(vs)):
            if i % 6 == 0:
                worst = max(worst, frac(fr.to_ndarray(format="rgb24")))
        print(f"{a.input}: max red fraction {worst:.4f}")
        return
    out = os.path.splitext(a.input)[0] + "_dered.mp4"
    p = subprocess.Popen([ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps),
                          "-i", "-", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    worst = 0
    mit = av.open(a.matte).decode(video=0) if a.matte and os.path.exists(a.matte) else None
    jade = None
    for i, fr in enumerate(c.decode(vs)):
        if mit is not None:
            try:
                mm = next(mit).to_ndarray(format="gray").astype(np.float32) / 255
                mm = cv2.resize(mm, (W, H))
                jade = np.clip(cv2.dilate(mm, np.ones((9, 9), np.uint8)) * 1.5, 0, 1)
            except StopIteration:
                pass
        o = fix(fr.to_ndarray(format="rgb24"), a.mode, jade)
        if i % 6 == 0:
            worst = max(worst, frac(o))
        p.stdin.write(o.tobytes())
    p.stdin.close(); p.wait()
    print(f"wrote {out}  (max red fraction after: {worst:.4f})")


if __name__ == "__main__":
    main()
