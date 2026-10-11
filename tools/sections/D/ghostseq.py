#!/usr/bin/env python
"""Bake a moving ghost: ghostsprite style per frame -> STEM_rgb.mp4 + STEM_alpha.mp4 (use as video + luma matte).
    ghostseq.py ENGRAVED.mp4 MATTE_DIR HEX OUTSTEM T0 T1 [--alpha=0.9]"""
import os
import subprocess
import sys
import tempfile

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ghostsprite  # noqa: E402

FF = os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg")
a = [x for x in sys.argv[1:] if not x.startswith("--")]
o = {x[2:].split("=")[0]: x.split("=", 1)[1] for x in sys.argv[1:] if x.startswith("--")}
eng, mdir, hexcol, stem, t0, t1 = a[0], a[1], a[2], a[3], float(a[4]), float(a[5])
tmp = tempfile.mkdtemp(dir=os.path.dirname(stem) or ".")
for i in range(round(t0 * 24), round(t1 * 24) + 1):
    p = os.path.join(tmp, "s.png")
    ghostsprite.sprite(eng, mdir, i / 24, hexcol, p, alpha=float(o.get("alpha", 0.9)))
    s = cv2.imread(p, cv2.IMREAD_UNCHANGED)
    cv2.imwrite(os.path.join(tmp, f"c{i:05d}.png"), s[..., :3])
    cv2.imwrite(os.path.join(tmp, f"a{i:05d}.png"), s[..., 3])
st = str(round(t0 * 24))
for k, suf in (("c", "_rgb.mp4"), ("a", "_alpha.mp4")):
    subprocess.run([FF, "-y", "-loglevel", "error", "-framerate", "24", "-start_number", st, "-i", os.path.join(tmp, k + "%05d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv444p" if k == "c" else "yuv420p", "-crf", "10", stem + suf], check=True)
subprocess.run(["rm", "-rf", tmp])
print(stem)
