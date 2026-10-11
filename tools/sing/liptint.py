#!/usr/bin/env python3
"""Optional colour pass (no paid call): her traced lips are graphite grey; next to the warm skin of deshadow --tint=1.8
they read cold blue-grey in the takes. This moves the lip pixels part of the way to a muted rose at the same lightness
(teeth and the open mouth left alone), tracked per frame by the face mesh, like deshadow.py's tint. An alternate for
her to compare, never a replacement for the take.

    MPY tools/sing/liptint.py still IN OUT [--k=1]
    MPY tools/sing/liptint.py take SHOT take_N [--k=1]      -> media/sing/<SHOT>/take_N_lips.mp4 (same frames, fps)"""
import os
import shutil
import subprocess
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deshadow as DS  # noqa: E402

OUTER = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409, 270, 269, 267, 0, 37, 39, 40, 185]
INNER = [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308, 415, 310, 311, 312, 13, 82, 81, 80, 191]
ROSE = (0.80, 0.78, 1.0)          # BGR proportions: a quiet, dusty rose (hue about 355 degrees, low chroma)


def tint(img, L, k=1.0):
    H, W = img.shape[:2]
    fh = float(np.linalg.norm(L[10] - L[152]))
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [np.round(L[OUTER]).astype(np.int32)], 1)
    cv2.fillPoly(m, [np.round(L[INNER]).astype(np.int32)], 0)
    m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), max(0.8, 0.006 * fh))
    f = img.astype(np.float32)
    Y = DS.lum(f)
    rose = np.array(ROSE, np.float32)
    rose = rose / DS.lum(rose[None, None])[0, 0]
    a = np.clip(0.5 * k * m * np.clip((Y - 40) / 60, 0, 1), 0, 0.85)[..., None]   # not in the dark lip line
    g = f * (1 - a) + (Y[..., None] * rose) * a
    return np.clip(g, 0, 255).astype(np.uint8)


def still(src, dst, k):
    im = cv2.imread(src)
    L = DS.find(cv2.cvtColor(im, cv2.COLOR_BGR2RGB), None)
    cv2.imwrite(dst, tint(im, L, k), [cv2.IMWRITE_JPEG_QUALITY, 96])
    print(dst)


def take(shot, a, k):
    d = os.path.join(DS.ROOT, "media/sing", shot) + "/"
    cap = cv2.VideoCapture(d + a + ".mp4")
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames, Ls, prev = [], [], None
    while True:
        ok, f = cap.read()
        if not ok:
            break
        L = DS.find(cv2.cvtColor(f, cv2.COLOR_BGR2RGB), prev)
        if L is not None:
            prev = [L[:, 0].min(), L[:, 1].min(), L[:, 0].max(), L[:, 1].max()]
        frames.append(f)
        Ls.append(L)
    ok = [i for i, L in enumerate(Ls) if L is not None]
    A = np.array([Ls[i] for i in ok])
    full = np.empty((len(Ls), 478, 2))
    for j in range(478):
        for c in range(2):
            full[:, j, c] = np.interp(np.arange(len(Ls)), ok, A[:, j, c])
    kk = np.array([1, 2, 3, 2, 1], float)
    kk /= kk.sum()
    pad = np.concatenate([full[:1].repeat(2, 0), full, full[-1:].repeat(2, 0)])
    sm = sum(kk[i] * pad[i:i + len(Ls)] for i in range(5))
    tmp = d + a + "_lips_png"
    os.makedirs(tmp, exist_ok=True)
    for i, f in enumerate(frames):
        cv2.imwrite(f"{tmp}/{i:04d}.png", tint(f, sm[i], k))
    out = d + a + "_lips.mp4"
    subprocess.run([DS.FF, "-y", "-loglevel", "error", "-framerate", f"{fps:g}", "-i", tmp + "/%04d.png", "-c:v", "libx264",
                    "-crf", "10", "-preset", "slow", "-pix_fmt", "yuv420p", out], check=True)
    shutil.rmtree(tmp)
    print(out, "frames", len(frames), "no face in", len(Ls) - len(ok))


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    o = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--"))
    k = float(o.get("k", 1))
    if a[0] == "still":
        still(a[1], a[2], k)
    else:
        take(a[1], a[2], k)
