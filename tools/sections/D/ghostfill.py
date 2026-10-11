#!/usr/bin/env python
"""Bake an opaque ghost (rev 5b): the ghostsprite line-art ghost laid over a pale fill inside her own matte, so the ghost
hides the real girl without a clean plate (for takes where agents move through her and a static plate would erase
them). Writes STEM_rgb.mp4 + STEM_alpha.mp4 (use as video + luma matte), and STEM_<frame>.png RGBA stills on request.
    ghostfill.py ENGRAVED.mp4 MATTE_DIR HEX OUTSTEM T0 T1 [--fill=#e6ebf3] [--grow=4] [--alpha=0.9] [--still=T,...]"""
import glob
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
fill = np.array([int(o.get("fill", "#e6ebf3")[i:i + 2], 16) for i in (5, 3, 1)], np.float32)   # BGR
grow = int(o.get("grow", 4))
stills = {round(float(s) * 24) for s in o["still"].split(",")} if "still" in o else set()
ms = sorted(glob.glob(mdir.rstrip("/") + "/*.png"))
tmp = tempfile.mkdtemp(dir=os.path.dirname(stem) or ".")
for i in range(round(t0 * 24), round(t1 * 24) + 1):
    p = os.path.join(tmp, "s.png")
    ghostsprite.sprite(eng, mdir, i / 24, hexcol, p, alpha=float(o.get("alpha", 0.9)))
    s = cv2.imread(p, cv2.IMREAD_UNCHANGED).astype(np.float32)
    H, W = s.shape[:2]
    m = cv2.resize(cv2.imread(ms[min(i, len(ms) - 1)], 0), (W, H)).astype(np.float32) / 255
    if grow:
        m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * grow + 1, 2 * grow + 1)))
    m = cv2.GaussianBlur(m, (0, 0), 1.2)
    sa = s[..., 3:] / 255
    rgb = s[..., :3] * sa + fill * (1 - sa)
    al = np.maximum(m, sa[..., 0])
    cv2.imwrite(os.path.join(tmp, f"c{i:05d}.png"), rgb.astype(np.uint8))
    cv2.imwrite(os.path.join(tmp, f"a{i:05d}.png"), (al * 255).astype(np.uint8))
    if i in stills:
        cv2.imwrite(f"{stem}_{i:05d}.png", np.dstack([rgb, al * 255]).astype(np.uint8))
st = str(round(t0 * 24))
for k, suf in (("c", "_rgb.mp4"), ("a", "_alpha.mp4")):
    subprocess.run([FF, "-y", "-loglevel", "error", "-framerate", "24", "-start_number", st, "-i", os.path.join(tmp, k + "%05d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv444p" if k == "c" else "yuv420p", "-crf", "10", stem + suf], check=True)
subprocess.run(["rm", "-rf", tmp])
print("wrote", stem + "_rgb.mp4", stem + "_alpha.mp4")
