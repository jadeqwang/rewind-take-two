#!/usr/bin/env python3
"""Singing Jade, step 3: put her own lines back (Orbital Sunrise restore_lines; copied from moongazing-public-version
work/singer4/restore.py, paths changed).

    MPY tools/sing/restore.py EDIT OUT [--check] [--face=0..1] [--lips=0..1]   (how much of the restored face / lips replaces the edit)

Inside her face oval the picture becomes the edit's low-frequency light and colour times the trace's own line detail
(trace / blurred trace), so every line of her face is hers while colour and light are the painting's. Needs the same
geometry: prints how far the edit's face landmarks sit from the base's (px at 2752 wide) and the eye-distance ratio.
"""
import os
import sys
import cv2
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mouth as MT

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "media/sing/first/base16.jpg")
FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150,
             136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]


def lm(A):
    h, w = A.shape[:2]
    r = MT.detect(A.astype(np.uint8), (w // 4, 0, w * 3 // 4, h))
    if r is None:
        raise SystemExit("no face")
    return r[0]


LIPS = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409, 270, 269, 267, 0, 37, 39, 40, 185]


def main(edit, out, check=False, grow=1.08, feather=18, face=1.0, lips=1.0):
    A = np.asarray(Image.open(BASE).convert("RGB"), np.float32)
    B = np.asarray(Image.open(edit).convert("RGB").resize((A.shape[1], A.shape[0]), Image.LANCZOS), np.float32)
    h, w = A.shape[:2]
    La, Lb = lm(A), lm(B)
    d = np.linalg.norm(La - Lb, axis=1)
    io = lambda L: np.linalg.norm(L[33] - L[263])
    fh = lambda L: np.linalg.norm(L[10] - L[152])
    print(f"{edit}: landmark shift mean {d.mean():.1f} max {d.max():.1f} px; eye distance x{io(Lb) / io(La):.3f}; "
          f"face height x{fh(Lb) / fh(La):.3f}; offset {np.round((Lb - La).mean(0), 1)}")
    if check:
        return
    sigma = w / 220
    pts = La[FACE_OVAL]; c = pts.mean(0); pts = c + (pts - c) * grow
    pts[:, 1] = np.where(pts[:, 1] < c[1], c[1] + (pts[:, 1] - c[1]) * 1.12, pts[:, 1])   # up over the forehead to the hairline
    m = np.zeros((h, w), np.uint8); cv2.fillPoly(m, [pts.astype(np.int32)], 255)
    m = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), feather)[..., None]
    ga = A.mean(2)
    detail = np.clip((ga + 1) / (cv2.GaussianBlur(ga, (0, 0), sigma) + 1), 0, 1.15)[..., None]
    light = cv2.GaussianBlur(B, (0, 0), sigma)
    R = light * detail
    lp = La[LIPS]; lc = lp.mean(0); lp = lc + (lp - lc) * 1.3
    ml = np.zeros((h, w), np.uint8); cv2.fillPoly(ml, [lp.astype(np.int32)], 255)
    ml = cv2.GaussianBlur(ml.astype(np.float32) / 255, (0, 0), 9)[..., None]
    k = np.maximum(m * face, ml * lips)          # how much of the restored face replaces the edit
    C = R * k + B * (1 - k)
    Image.fromarray(np.clip(C, 0, 255).astype(np.uint8)).save(out, quality=95)
    print(out)


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    o = dict(x[2:].split("=") for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    main(a[0], a[1] if len(a) > 1 else None, "--check" in sys.argv, face=float(o.get("face", 1)), lips=float(o.get("lips", 1)))
