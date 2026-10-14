#!/usr/bin/env python
"""D6: give her a breath (v7, Jade: "she's perfectly still at the wheel ... except for a single blink, no breathing").

D6 take 2 has no body motion in the used range (in 0.4, 1.3 s = source frames ~10-41): shoulders move < 0.5 px,
head < 1 px until ~frame 36. No other stretch of the take, and no other D6 take with this staging, is livelier.
This is a pixel pass, no generative model: her layer (the colour matte, with the pencil tops that
tools/matte_fix.py restored) is warped by a smooth, low-amplitude field and laid back over the untouched frame.

  * breath: shoulders, upper back, chest and head rise by up to AMP px (and the chest swells forward by CHEST of
    that), on a calm cycle (BREATH_T s, trough at TROUGH s take time, so the shot plays one inhale);
  * the field is 1 over head/shoulders/chest and falls smoothly to 0 down the torso to the waist and along the
    forearms to the hands, so her hands stay on the wheel and her lap stays on the seat; the arms flex between;
  * head settle: the head sinks back HEAD_SETTLE px relative to the shoulders over the shot (neck easing);
  * composite: out = warped(her) * warped(matte) + frame * (1 - warped(matte)). The world (agents, stopwatch,
    window frame, wheel, seat) is never warped: it is only covered where she rises (by <= AMP px), and where she
    moves off a pixel (downward-facing edges: under the jaw, hair tips) the world pixel straight below is copied in.

  tools/engrave/.venv/bin/python tools/matte_fix.py tools/matte_fix_specs/D6.json --tmp DIR --check-only
  tools/engrave/.venv/bin/python tools/d6_breath.py --matte DIR/take_2_engraved_matte_matte
"""
import argparse
import os
import sys

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from blue_eraser import encode, frames_of  # noqa: E402

SRC = "media/shots/D6/take_2_engraved_eraser.mp4"
OUT = "media/shots/D6/take_2_engraved_breath.mp4"
AMP = 5.0          # px (1080p) shoulder rise at the top of the breath
CHEST = 0.25       # forward (+x) swell of the chest, as a fraction of AMP
BREATH_T = 2.8     # s, one breath
TROUGH = 0.1       # s take time of the breath's low point: just before the in-point (0.4), so she is already rising
                   # on the first frame, peaks ~1.5 s and turns to the exhale as the shot ends (1.7)
HEAD_SETTLE = 1.5  # px the head sinks back relative to the shoulders over the shot
# body layout in this take (1080p px): head ~(380-720, 230-520), shoulders/back ~(480-820, 480-700),
# hands on the wheel ~(1120-1360, 480-700), lap y > 850
Y_FULL, Y_ZERO = 660, 900     # torso: full rise above Y_FULL, none below Y_ZERO
X_FULL, X_ZERO = 860, 1120    # arms: full rise left of X_FULL, none right of X_ZERO (the hands)
HEAD_BOX = (360, 200, 740, 520)


def smooth01(v):
    v = np.clip(v, 0, 1)
    return v * v * (3 - 2 * v)


def fields(H, W):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    body = smooth01((Y_ZERO - yy) / (Y_ZERO - Y_FULL)) * smooth01((X_ZERO - xx) / (X_ZERO - X_FULL))
    body = cv2.GaussianBlur(body, (0, 0), 25)
    chest = body * smooth01((xx - 560) / 160) * smooth01((Y_ZERO - yy) / (Y_ZERO - 600))   # her front, not her back
    head = np.zeros((H, W), np.float32)
    x0, y0, x1, y1 = HEAD_BOX
    head[y0:y1, x0:x1] = 1
    head = cv2.GaussianBlur(head, (0, 0), 30)
    return body, chest, head


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matte", required=True, help="her matte, %05d.png per frame (tools/matte_fix.py D6 --check-only)")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--frames", type=int, default=0)
    a = ap.parse_args()
    fr, fps = frames_of(os.path.join(ROOT, SRC))
    if a.frames:
        fr = fr[:a.frames]
    H, W = fr[0].shape[:2]
    body, chest, head = fields(H, W)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    out = []
    for i, f in enumerate(fr):
        t = i / float(fps)
        br = 0.5 * (1 - np.cos(2 * np.pi * (t - TROUGH) / BREATH_T))
        settle = smooth01((t - TROUGH) / 1.3)
        dy = -AMP * br * body + HEAD_SETTLE * settle * head          # up is negative
        dx = AMP * CHEST * br * chest
        m = cv2.imread(os.path.join(a.matte, f"{i:05d}.png"), 0).astype(np.float32) / 255.0
        mx, my = (xx - dx).astype(np.float32), (yy - dy).astype(np.float32)   # backward map: out(p) = src(p - d)
        her = cv2.remap(f, mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
        mw = cv2.remap(m, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)[..., None]
        # where she moved off (her before, not her now: under the jaw, hanging hair tips) the world shows through:
        # each such pixel copies the nearest world pixel straight below it (she moves up, so the world there is
        # the strip just below her old edge; the hatching there runs near-horizontal, so a few rows repeat cleanly)
        bg = f.astype(np.float32).copy()
        unc = (m - mw[..., 0]) > 0.02
        if unc.any():
            ys, xs = np.nonzero(unc)
            got = np.zeros(len(ys), bool)
            for k in range(1, 16):
                yk = np.minimum(ys + k, H - 1)
                ok = ~got & (m[yk, xs] < 0.1)
                bg[ys[ok], xs[ok]] = f[yk[ok], xs[ok]]
                got |= ok
        g = her * mw + bg * (1 - mw)
        out.append(np.clip(g + 0.5, 0, 255).astype(np.uint8))
    path = a.out if os.path.isabs(a.out) else os.path.join(ROOT, a.out)
    encode(out, fps, path, 16, ["-tune", "grain", "-movflags", "+faststart"])
    print(f"wrote {a.out}: {len(out)} frames; breath {BREATH_T}s from {TROUGH}s, amp {AMP}px")


if __name__ == "__main__":
    main()
