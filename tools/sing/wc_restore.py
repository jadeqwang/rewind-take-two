#!/usr/bin/env python3
"""Watercolor singing Jade (v3), step 3: likeness check and face restore (moongazing-public-version
work/singer5/restore.py, paths changed).

    MPY tools/sing/wc_restore.py EDIT --check                 landmark shift against v3_base16.jpg
    MPY tools/sing/wc_restore.py EDIT OUT [--face=1] [--light=0] [--grow=1.10] [--feather=22] [--crop=FILE]

Inside her face oval (forehead to chin, feathered) the picture becomes HER OWN PIXELS from the base sheet, colour and
all:  R = base * (blur(edit) / blur(base)) ** light.  light 0 = her portrait untouched (the default here: she is meant
to mismatch the engraved world, so she takes no light from it); 1 = the painting's low-frequency light.
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mouth as MT  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = os.path.join(ROOT, "media/sing/first/v3_base16.jpg")
FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150,
             136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]


def lm(A):
    h, w = A.shape[:2]
    r = MT.detect(A.astype(np.uint8), (w // 4, 0, w * 3 // 4, h))
    if r is None:
        raise SystemExit("no face")
    return r[0]


def load(edit):
    A = np.asarray(Image.open(BASE).convert("RGB"), np.float32)
    B = np.asarray(Image.open(edit).convert("RGB").resize((A.shape[1], A.shape[0]), Image.LANCZOS), np.float32)
    return A, B


def check(A, B, name=""):
    La, Lb = lm(A), lm(B)
    d = np.linalg.norm(La - Lb, axis=1)
    io = lambda L: np.linalg.norm(L[33] - L[263])
    fh = lambda L: np.linalg.norm(L[10] - L[152])
    d0 = np.linalg.norm((La - La.mean(0)) - (Lb - Lb.mean(0)), axis=1)
    print(f"{name}: landmark shift mean {d.mean():.1f} max {d.max():.1f} px (shape only: mean {d0.mean():.1f} max {d0.max():.1f}); "
          f"eye distance x{io(Lb) / io(La):.3f}; face height x{fh(Lb) / fh(La):.3f}; offset {np.round((Lb - La).mean(0), 1)}")
    return La, Lb


def oval(La, shape, grow, feather):
    h, w = shape[:2]
    pts = La[FACE_OVAL]; c = pts.mean(0); pts = c + (pts - c) * grow
    pts[:, 1] = np.where(pts[:, 1] < c[1], c[1] + (pts[:, 1] - c[1]) * 1.10, pts[:, 1])   # up over the forehead to the hairline
    m = np.zeros((h, w), np.uint8); cv2.fillPoly(m, [pts.astype(np.int32)], 255)
    return cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), feather)[..., None]


def main(edit, out, face=1.0, light=0.0, grow=1.10, feather=22, crop=None):
    A, B = load(edit)
    La, _ = check(A, B, edit)
    w = A.shape[1]
    sigma = w / 110
    m = oval(La, A.shape, grow, feather)
    M = (oval(La, A.shape, grow * 1.04, 6) > 0.5).astype(np.float32)
    nb = lambda X: cv2.GaussianBlur(X * M, (0, 0), sigma) / (cv2.GaussianBlur(M, (0, 0), sigma)[..., None] + 1e-3)
    ratio = (nb(B) + 4) / (nb(A) + 4)
    R = A * ratio ** light
    k = m * face
    C = np.clip(R * k + B * (1 - k), 0, 255)
    Image.fromarray(C.astype(np.uint8)).save(out, quality=96)
    check(A, C, out)
    f = lambda X: X[int(La[:, 1].min()) - 220:int(La[:, 1].max()) + 120, int(La[:, 0].min()) - 150:int(La[:, 0].max()) + 150]
    sk = m[..., 0] > 0.9
    print(f"  face mean RGB: base {np.round(A[sk].mean(0))} edit {np.round(B[sk].mean(0))} out {np.round(C[sk].mean(0))}; "
          f"mean |edit-out| in oval {np.abs(B - C)[sk].mean():.1f}")
    if crop:
        Image.fromarray(np.hstack([f(A), f(B), f(C)]).astype(np.uint8)).save(crop, quality=92)
    print(out)


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    o = dict(x[2:].split("=") for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    if "--check" in sys.argv:
        for e in a:
            try:
                check(*load(e), e)
            except SystemExit as x:
                print(f"{e}: landmark check failed ({x}): her face is not where the base has it")
    else:
        main(a[0], a[1], face=float(o.get("face", 1)), light=float(o.get("light", 0)), grow=float(o.get("grow", 1.10)),
             feather=float(o.get("feather", 22)), crop=o.get("crop"))
