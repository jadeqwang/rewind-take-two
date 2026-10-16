#!/usr/bin/env python3
"""v9 fix #3: a small Python stand-in for the engine, for checking the v9 car shot (tools/v4B/car/car_shot_v9.js)
without render.mjs (the brief forbids engine renders by fix agents). It reproduces the layer transforms of
car_shot_v9.js for the picture layers only (take, held sky, gantry, roof, Jade through the take's matte, mirror body,
close still); lettering, plates, strobes, sweeps and the shot fx are left out (the sign quad is outlined in orange).

    PY=~/Documents/1-music-shipped/moongazing/.venv/bin/python
    $PY tools/v9/mirrors/mock_car.py OUTDIR 89.30 90.19 90.60 91.40 91.80 92.70 [--v8]
--v8 renders the v8 layering (old gantry above the header, no roof) for before/after sheets.
"""
import math
import os
import sys

import av
import numpy as np
from PIL import Image, ImageDraw

ROOT = "/home/jade/Documents/rewind-take-two"
S = os.path.join(ROOT, "media/shots/")
PW, PH = 960, 540
C0 = (960.0, 540.0)
MW, MC = (1335.8, 436.5), (961.0, 585.3)
R = 394.4 / 1866.8
E_END, VP = 1.08, (905.0, 488.0)
PUSH, Z0, Z1 = (90.50, 92.00), 1.0, 1.045
Z2, Z3 = 1.0 / R, E_END / R
PAD = 2.2


def sm(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def ease(u):
    u = max(0.0, min(1.0, u))
    return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2


def zoom(t):
    if t < PUSH[0]:
        return Z0 + (Z1 - Z0) * sm((t - 89.26) / (PUSH[0] - 89.26))
    if t < PUSH[1]:
        return math.exp(math.log(Z1) + (math.log(Z2) - math.log(Z1)) * ease((t - PUSH[0]) / (PUSH[1] - PUSH[0])))
    return Z2 + (Z3 - Z2) * sm((t - PUSH[1]) / (92.79 - PUSH[1]))


PEND = (MW[0] + R * (C0[0] - MC[0]), MW[1] + R * (C0[1] - MC[1]))
F = tuple((Z2 * PEND[i] - C0[i]) / (Z2 - 1) for i in (0, 1))


def wide_cam(t):
    z = zoom(t)
    return dict(scale=z, x=(F[0] - C0[0]) * (1 - z), y=(F[1] - C0[1]) * (1 - z))


def close_cam(t):
    z = zoom(t)
    return dict(scale=z * R, x=F[0] - C0[0] + z * (MW[0] - R * MC[0] - F[0] + R * C0[0]),
                y=F[1] - C0[1] + z * (MW[1] - R * MC[1] - F[1] + R * C0[1]))


def about(cam, k, a, d=(0, 0)):
    return dict(scale=cam["scale"] * k, x=cam["x"] + cam["scale"] * ((1 - k) * (a[0] - C0[0]) + d[0]),
                y=cam["y"] + cam["scale"] * ((1 - k) * (a[1] - C0[1]) + d[1]))


def apply(cam, q):
    return [C0[i % 2] + (cam["y"] if i % 2 else cam["x"]) + cam["scale"] * (v - C0[i % 2]) for i, v in enumerate(q)]


# ---- v9 (keep in step with tools/v4B/car/car_shot_v9.js) ----
def gantry_k9(t):
    u = max(0.0, t - 89.26)
    return 1 + 0.18 * u + 0.04 * u * u


def gantry_cam9(t):
    return about(wide_cam(t), gantry_k9(t), VP)


SIGN_Q9 = [660, 352, 990, 352, 990, 446, 660, 446]
# ---- v8 ----
GANTRY_A = (905, 276)


def gantry_cam8(t):
    u = max(0.0, t - 89.26)
    return about(wide_cam(t), 1 + 0.10 * u + 0.05 * u * u, GANTRY_A)


SIGN_Q8 = [846, 100, 1260, 100, 1260, 218, 846, 218]


def close_opacity(t):
    return sm((zoom(t) - 3.0) / (3.9 - 3.0))


def draw(canvas, img, cam, opacity=1.0, extra_scale=1.0):
    """img: RGBA PIL fit-cover to 1920x1080 design px; cam: the engine transform; canvas: PW x PH RGBA."""
    w, h = img.size
    k = 1920.0 / w
    s = cam["scale"] * extra_scale
    q = PW / 1920.0
    # preview = q * (C0 + d + s * (k * src - C0))
    ax = q * s * k
    bx = q * (C0[0] + cam["x"] - s * C0[0])
    by = q * (C0[1] + cam["y"] - s * C0[1])
    t = img.transform((PW, PH), Image.AFFINE, (1 / ax, 0, -bx / ax, 0, 1 / ax, -by / ax), resample=Image.BILINEAR)
    if opacity < 1:
        a = np.asarray(t).copy()
        a[..., 3] = (a[..., 3] * opacity).astype(np.uint8)
        t = Image.fromarray(a)
    canvas.alpha_composite(t)


def take_frames(path="V2f3/take_1_engraved.mp4"):
    c = av.open(os.path.join(S, path))
    return [f.to_image() for f in c.decode(video=0)]


def main():
    out = sys.argv[1]
    v8 = "--v8" in sys.argv
    times = [float(x) for x in sys.argv[2:] if not x.startswith("--")]
    os.makedirs(out, exist_ok=True)
    frames = take_frames()
    mattes = None if v8 else take_frames("V2f3/take_1_matte_v9/matte.mp4")
    load = lambda p: Image.open(os.path.join(S, p)).convert("RGBA")
    sky = load("V2f3/wide_sky_left.png")
    body = load("V2f4/kf_close_b2_engraved_body.png")
    pad = load("V2f4/close_pad.png")
    gantry = load("V2f3/wide_gantry.png" if v8 else "V2f3/v9_gantry.png")
    roof = None if v8 else load("V2f3/v9_roof_r2c.png")
    for t in times:
        n = min(len(frames) - 1, int(round((t - 89.26) * 24)))
        fr = frames[n].convert("RGBA")
        m = (Image.open(os.path.join(S, f"V2f3/take_1_matte/{n:05d}.png")) if v8 else mattes[n]).convert("L").resize(fr.size)
        jade = fr.copy()
        jade.putalpha(m)
        cv = Image.new("RGBA", (PW, PH), (11, 11, 12, 255))
        wc = wide_cam(t)
        draw(cv, fr, wc)
        if v8:
            draw(cv, gantry, gantry_cam8(t))
            draw(cv, sky, wc)
        else:
            draw(cv, sky, wc)
            draw(cv, gantry, gantry_cam9(t))
            draw(cv, roof, wc)
        draw(cv, jade, wc)
        draw(cv, body, close_cam(t))
        co = close_opacity(t)
        if co > 0:
            draw(cv, pad, close_cam(t), co, PAD)
        q = PW / 1920.0
        sq = apply(gantry_cam8(t) if v8 else gantry_cam9(t), SIGN_Q8 if v8 else SIGN_Q9)
        ImageDraw.Draw(cv).polygon([(sq[i] * q, sq[i + 1] * q) for i in range(0, 8, 2)], outline=(240, 138, 36, 255))
        p = os.path.join(out, f"{'v8' if v8 else 'v9'}_{t:.2f}.jpg")
        cv.convert("RGB").save(p, quality=88)
        print(p)


if __name__ == "__main__":
    main()
