#!/usr/bin/env python
"""Color-flood wipe for section F (F1 and the "rewind that paints" F7.08).

Composites an engraved twin and a color version of the SAME clip through an animated radial matte with a hatched,
pencil-stroke front and a gold leading edge. Also writes the matte as a video for the engine.

  wipe.py --color C.mp4 --engraved E.mp4 --out OUT.mp4 --matte-out M.mp4 --origin 0.42,0.62 \
          --t0 0.0 --t1 1.78 [--reverse] [--ease out|in|inout]

--reverse   the wipe is computed on the reversed clock (for footage that will be played backward in the edit, so the
            color appears to paint IN as the rewind runs). Frames are still written in source order.
--origin    normalized x,y of the pencil point (can be a keyframed list "t:x,y;t:x,y").
Run with tools/engrave/.venv/bin/python (cv2, av, numpy).
"""
import argparse
import os
import shutil
import subprocess

import av
import cv2
import numpy as np

GOLD = np.array([0.79, 0.64, 0.15], np.float32)
ORANGE = np.array([0.94, 0.54, 0.14], np.float32)


def ffmpeg():
    for c in (os.environ.get("FFMPEG"), os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg"), shutil.which("ffmpeg")):
        if c and os.path.exists(c):
            return c
    raise SystemExit("no ffmpeg")


def writer(path, w, h, fps, crf=14):
    return subprocess.Popen([ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                             "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
                             "-pix_fmt", "yuv420p", "-movflags", "+faststart", path], stdin=subprocess.PIPE)


def frames(path, size=None):
    c = av.open(path)
    s = c.streams.video[0]
    for f in c.decode(s):
        a = f.to_ndarray(format="rgb24")
        if size and (a.shape[1], a.shape[0]) != size:
            a = cv2.resize(a, size, interpolation=cv2.INTER_LANCZOS4)
        yield a


def fbm(h, w, seed=3, octaves=4, base=6):
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        n = base * 2 ** o
        g = rng.standard_normal((n, int(n * w / h) + 1)).astype(np.float32)
        out += amp * cv2.resize(g, (w, h), interpolation=cv2.INTER_CUBIC)
        tot += amp
        amp *= 0.5
    return out / tot


def parse_origin(s):
    if ":" not in s:
        x, y = map(float, s.split(","))
        return [(0.0, x, y)]
    keys = []
    for part in s.split(";"):
        t, xy = part.split(":")
        x, y = map(float, xy.split(","))
        keys.append((float(t), x, y))
    return sorted(keys)


def origin_at(keys, t):
    if t <= keys[0][0]:
        return keys[0][1:]
    for (t0, x0, y0), (t1, x1, y1) in zip(keys, keys[1:]):
        if t <= t1:
            u = (t - t0) / max(1e-6, t1 - t0)
            return x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
    return keys[-1][1:]


def ease(u, kind):
    u = min(1.0, max(0.0, u))
    if kind == "out":
        return 1 - (1 - u) ** 3
    if kind == "linear":
        return u
    if kind == "outq":
        return 1 - (1 - u) ** 2
    if kind == "in":
        return u ** 3
    return u * u * (3 - 2 * u)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--color", required=True)
    ap.add_argument("--engraved", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--matte-out")
    ap.add_argument("--origin", default="0.5,0.6")
    ap.add_argument("--t0", type=float, default=0.0)
    ap.add_argument("--t1", type=float, default=1.78)
    ap.add_argument("--ease", default="out")
    ap.add_argument("--reverse", action="store_true")
    ap.add_argument("--glow", type=float, default=0.75)
    ap.add_argument("--hatch", type=float, default=0.018, help="amplitude of the hatched front")
    ap.add_argument("--wobble", type=float, default=0.07)
    ap.add_argument("--reach", type=float, default=1.15, help="front radius at t1 (diagonal units; ~0.6 = corners from the centre)")
    a = ap.parse_args()

    ce = av.open(a.engraved)
    vs = ce.streams.video[0]
    fps = vs.average_rate
    W, H = vs.codec_context.width, vs.codec_context.height
    nfr = vs.frames or 0
    ce.close()
    if a.reverse and not nfr:
        nfr = sum(1 for _ in frames(a.engraved))
    keys = parse_origin(a.origin)

    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    xn, yn = xx / H, yy / H                       # aspect-correct units (height = 1)
    wob = fbm(H, W, seed=5) * a.wobble
    ang = np.deg2rad(38.0)
    hatch = np.sin(2 * np.pi * (xx * np.cos(ang) + yy * np.sin(ang)) / (H / 95.0)).astype(np.float32) * a.hatch
    diag = np.hypot(W / H, 1.0)

    wr = writer(a.out, W, H, fps)
    mw = writer(a.matte_out, W, H, fps, crf=12) if a.matte_out else None
    for i, (e, c) in enumerate(zip(frames(a.engraved), frames(a.color, (W, H)))):
        t = i / float(fps)
        tc = ((nfr - 1 - i) / float(fps)) if a.reverse else t
        ox, oy = origin_at(keys, tc)
        d = np.hypot(xn - ox * W / H, yn - oy) / diag
        R = ease((tc - a.t0) / max(1e-6, a.t1 - a.t0), a.ease) * a.reach - 0.04
        f = d + wob + hatch - R
        m = np.clip(0.5 - f / 0.02, 0, 1)                   # 1 = color
        band = np.exp(-(f / 0.018) ** 2) * (0.0 < R < a.reach - 0.07)
        ef, cf = e.astype(np.float32) / 255, c.astype(np.float32) / 255
        out = ef * (1 - m[..., None]) + cf * m[..., None]
        g = (band * a.glow)[..., None]
        tint = GOLD * 0.65 + ORANGE * 0.35
        out = out * (1 - g * 0.55) + tint * g * 0.55 + g * 0.25 * tint   # gold leading edge, slight additive bloom
        wr.stdin.write((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
        if mw:
            mu8 = (m * 255).astype(np.uint8)
            mw.stdin.write(np.repeat(mu8[..., None], 3, 2).tobytes())
    for p in (wr, mw):
        if p:
            p.stdin.close()
            p.wait()
    print("wrote", a.out, a.matte_out or "")


if __name__ == "__main__":
    main()
