#!/usr/bin/env python
"""Clean-plate patch for a ghost twin (rev 5): an RGBA PNG holding the nano clean plate only where the girl to be
removed ever is in [t0, t1] (union of her matte, dilated and feathered), to lay over the take's own video.

    patch.py NANO.jpg MATTE_DIR T0 T1 OUT.png [--grow=28] [--feather=10] [--check=SRC.jpg]
--check writes OUT_check.jpg: the patch composited over SRC (the frame the plate was made from).
The nano image is resized to 1920x1080 (nano keeps the 16:9 framing of the frame it edited).
"""
import glob
import sys

import cv2
import numpy as np

a = [x for x in sys.argv[1:] if not x.startswith("--")]
o = {x[2:].split("=")[0]: x.split("=", 1)[1] for x in sys.argv[1:] if x.startswith("--")}
nano, mdir, t0, t1, out = a[0], a[1], float(a[2]), float(a[3]), a[4]
grow, fe = int(o.get("grow", 28)), float(o.get("feather", 10))
W, H = 1920, 1080
fs = sorted(glob.glob(mdir.rstrip("/") + "/*.png"))
u = np.zeros((H, W), np.uint8)
for i in range(round(t0 * 24), min(len(fs) - 1, round(t1 * 24)) + 1):
    m = cv2.resize(cv2.imread(fs[i], 0), (W, H))
    u = np.maximum(u, (m >= 100).astype(np.uint8))
u = cv2.dilate(u, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * grow + 1, 2 * grow + 1)))
al = cv2.GaussianBlur(u.astype(np.float32), (0, 0), fe)
al = np.clip(al * 1.4, 0, 1) * u.astype(np.float32) + (1 - u) * np.clip(al * 1.4, 0, 1) * 0.0
al = cv2.GaussianBlur(al, (0, 0), fe / 2)
rgb = cv2.resize(cv2.imread(nano), (W, H), interpolation=cv2.INTER_AREA)
cv2.imwrite(out, np.dstack([rgb, (al * 255).astype(np.uint8)]))
if "check" in o:
    src = cv2.resize(cv2.imread(o["check"]), (W, H)).astype(np.float32)
    c = src * (1 - al[..., None]) + rgb.astype(np.float32) * al[..., None]
    cv2.imwrite(out[:-4] + "_check.jpg", cv2.resize(c.astype(np.uint8), (960, 540)))
print(out)
