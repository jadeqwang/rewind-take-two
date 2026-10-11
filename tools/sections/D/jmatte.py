#!/usr/bin/env python
"""Jade-only matte: the engrave matte (BiRefNet) also keeps the agents when they touch or stand near her. Keep only
the part of it that lies near her coloured pixels (orange straps/band, navy pants, skin, pale-blue patch), optionally
restricted to a box, and write a new PNG sequence + matte.mp4.

    jmatte.py STEM [--box=x0,y0,x1,y1] [--grow=34] [--out=SUFFIX]      (STEM = media/shots/E2/take_fld_slide_1)
reads STEM.mp4 (raw colour take) and STEM_matte/*.png; writes STEM_jmatte/ (or STEM<SUFFIX>/).
--box keeps only the matte inside a normalised box (for tinting the twin in E5).
--nocolor skips the colour gate (box only).
"""
import glob
import os
import subprocess
import sys

import av
import cv2
import numpy as np

FFMPEG = os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg")


def main():
    stem = sys.argv[1]
    o = {a[2:].split("=")[0]: (a.split("=", 1)[1] if "=" in a else True) for a in sys.argv[2:] if a.startswith("--")}
    grow = int(o.get("grow", 34))
    out = stem + o.get("out", "_jmatte")
    os.makedirs(out, exist_ok=True)
    mfiles = sorted(glob.glob(stem + "_matte/*.png"))
    box = [float(v) for v in o["box"].split(",")] if "box" in o else None
    with av.open(stem + ".mp4") as c:
        for k, f in enumerate(c.decode(video=0)):
            if k >= len(mfiles):
                break
            rgb = np.asarray(f.to_image().convert("RGB"))
            m = cv2.imread(mfiles[k], cv2.IMREAD_GRAYSCALE)
            H, W = m.shape
            keep = np.ones((H, W), np.uint8)
            if "nocolor" not in o:
                hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
                s, v = hsv[..., 1] / 255.0, hsv[..., 2] / 255.0
                col = ((s > 0.30) & (v > 0.12)).astype(np.uint8)
                col = cv2.morphologyEx(col, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
                n, lab, st, _ = cv2.connectedComponentsWithStats(col, 8)
                big = np.zeros_like(col)
                for i in range(1, n):
                    if st[i, 4] >= 40:
                        big[lab == i] = 1
                big = cv2.morphologyEx(big, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41)))
                big = cv2.dilate(big, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * grow + 1, 2 * grow + 1)))
                keep = cv2.resize(big, (W, H), interpolation=cv2.INTER_NEAREST)
            if box:
                b = np.zeros((H, W), np.uint8)
                b[int(box[1] * H):int(box[3] * H), int(box[0] * W):int(box[2] * W)] = 1
                keep = keep & b
            keep = cv2.GaussianBlur(keep.astype(np.float32), (0, 0), 3)
            mm = (m.astype(np.float32) * np.clip(keep * 1.5, 0, 1)).astype(np.uint8)
            cv2.imwrite(os.path.join(out, os.path.basename(mfiles[k])), mm)
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-framerate", "24", "-i", os.path.join(out, "%05d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "12", os.path.join(out, "matte.mp4")], check=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
