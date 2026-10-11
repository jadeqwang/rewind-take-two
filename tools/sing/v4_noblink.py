#!/usr/bin/env python3
"""Watercolor singing Jade (v4): take a blink out of a synced singer file by laying the eyes of the last open frame
over the blink frames (no paid call; mouth, hair and timing untouched, so lip sync and the matte are unchanged).

S1 v4_take_1 blinks at file frames 8-13 (song 12.93-13.14), just as B's Bean push starts (13.04): with her small in the
wide it read as her looking down for the first beat (v4-B, 2026-10-11).

    MPY=~/Documents/orbital-sunrise-video/video/out/.venv/bin/python
    $MPY tools/sing/v4_noblink.py SRC OUT REF FIRST LAST [--fade=2]
    e.g. media/sing/S1/v4_sync_1080.mp4 media/sing/S1/v4_sync_1080_open.mp4 7 8 14

Frames FIRST..LAST get the eye region of frame REF, moved onto each frame by a similarity fit on the nose, brow and
face-side landmarks (the eyes themselves are left out of the fit); the last FADE frames blend back to the take's own
eyes. Writes OUT (same encode as wc_post.sync), OUT_check.jpg (before / after face crops) and links OUT's matte dir to
SRC's (the matte does not change: only pixels inside the face move)."""
import os
import subprocess
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mouth as MT  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FF = os.environ.get("FFMPEG", os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg"))
STABLE = [168, 6, 197, 195, 5, 4, 1, 127, 356, 234, 454, 10, 151, 9, 70, 63, 105, 66, 107, 336, 296, 334, 293, 300]
EYES = ([33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246],
        [263, 249, 390, 373, 374, 380, 381, 382, 362, 398, 384, 385, 386, 387, 388, 466])


def read(p):
    c = cv2.VideoCapture(p)
    out = []
    while True:
        ok, a = c.read()
        if not ok:
            return out
        out.append(cv2.cvtColor(a, cv2.COLOR_BGR2RGB))


def lm(a):
    r = MT.detect(a, (a.shape[1] // 4, 0, a.shape[1] * 3 // 4, a.shape[0]))
    if r is None:
        raise SystemExit("no face")
    return r[0]


def eye_mask(L, shape):
    io = np.linalg.norm(L[33] - L[263])
    m = np.zeros(shape[:2], np.float32)
    for idx in EYES:
        p = L[idx]
        c = p.mean(0)
        q = c + (p - c) * np.array([1.45, 2.1])          # wider than the lids, up to the brow and down to the lower lid's crease
        cv2.fillPoly(m, [cv2.convexHull(q.astype(np.float32)).astype(np.int32)], 1.0)
    return cv2.GaussianBlur(m, (0, 0), io * 0.05)


def main(src, out, ref, first, last, fade=2):
    F = read(src)
    Lr = lm(F[ref])
    G = [f.copy() for f in F]
    crops = []
    for k in range(first, last + 1):
        Lk = lm(F[k])
        M, _ = cv2.estimateAffinePartial2D(Lr[STABLE].astype(np.float32), Lk[STABLE].astype(np.float32), method=cv2.LMEDS)
        W = cv2.warpAffine(F[ref], M, (F[k].shape[1], F[k].shape[0]), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
        Lw = Lr @ M[:, :2].T + M[:, 2]
        w = 1.0 if k <= last - fade else (last + 1 - k) / (fade + 1)
        m = (eye_mask(Lw, F[k].shape) * w)[..., None]
        G[k] = np.clip(W.astype(np.float32) * m + F[k].astype(np.float32) * (1 - m) + 0.5, 0, 255).astype(np.uint8)
        x0, y0 = (Lk[[127, 10]].min(0) - 40).astype(int)
        x1, y1 = (np.array([Lk[356, 0], Lk[1, 1]]) + 40).astype(int)
        crops.append(np.vstack([cv2.resize(F[k][y0:y1, x0:x1], (300, 200)), cv2.resize(G[k][y0:y1, x0:x1], (300, 200))]))
    cv2.imwrite(os.path.splitext(out)[0] + "_check.jpg", cv2.cvtColor(np.hstack(crops), cv2.COLOR_RGB2BGR))
    h, w = G[0].shape[:2]
    p = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", "24", "-i", "-",
                          "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-pix_fmt", "yuv420p", "-colorspace", "bt709",
                          "-color_primaries", "bt709", "-color_trc", "bt709", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for f in G:
        p.stdin.write(f.tobytes())
    p.stdin.close()
    assert p.wait() == 0
    md_src, md_out = src[:-4] + "_matte", out[:-4] + "_matte"
    if os.path.isdir(md_src) and not os.path.exists(md_out):
        os.symlink(os.path.basename(md_src), md_out)
    print(os.path.relpath(out, ROOT), len(G), "frames; patched", first, "-", last, "from", ref, "; matte ->", os.path.basename(md_src))


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    o = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    main(a[0], a[1], int(a[2]), int(a[3]), int(a[4]), int(o.get("fade", 2)))
