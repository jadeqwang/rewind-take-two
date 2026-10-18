#!/usr/bin/env python3
"""Singing Jade (v7): trace plot of a take's mouth against the voice at given lags (the check v6/v6b read the S1 lag from:
the 'b' closure and its release into "fore", the end of "fore", the 'm' of "my", the phrase end).

    MPY=~/Documents/1-music-shipped/orbital-sunrise-video/video/out/.venv/bin/python
    $MPY tools/sing/v7_trace.py SHOT TAKE LAG [LAG ...] [--out=PNG] [--from=S --to=S]

One panel per lag over song time: vocal-stem level (grey fill), inner-lip gap (orange) and jawOpen (blue) moved to song
time by clip_time = song_time - ref_t0 + LAG. Vertical ticks every 0.1 s, labels every 0.5 s; the look.py events
(open, 'b', 'm', end) are marked in red. Also prints, per lag, the song times of the gap's local minima (closures) and of
the voice's dips, so the markers can be read off as numbers."""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import look as LK  # noqa: E402
import mouth as MT  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main(shot, take, lags, out=None, a=None, b=None):
    S = LK.SHOTS[shot]
    t0 = S["t0"]
    m = MT.cached(os.path.join(ROOT, "media/sing", shot, take + ".mp4"))
    fps, n = m["fps"], m["n"]
    f = lambda k: np.array([np.nan if v is None else v for v in m[k]], float)  # noqa: E731
    gap, jaw = f("gap"), f("jaw")
    t = np.arange(n) / fps
    a = a if a is not None else S["win"][0] - 0.3
    b = b if b is not None else S["win"][1] + 0.4
    e, hop = LK.env(a, b - a)
    te = a + np.arange(len(e)) * hop
    Wd, Hp, pad = 1800, 170, 40
    img = Image.new("RGB", (Wd, Hp * len(lags) + 30), (255, 255, 255))
    d = ImageDraw.Draw(img)
    X = lambda s: pad + (s - a) / (b - a) * (Wd - 2 * pad)  # noqa: E731
    g_lo, g_hi = np.nanpercentile(gap, 2), np.nanpercentile(gap, 99.5)
    j_lo, j_hi = np.nanpercentile(jaw, 2), np.nanpercentile(jaw, 99.5)
    for p, lag in enumerate(lags):
        y0 = 20 + p * Hp
        Y = lambda v: y0 + Hp - 15 - v * (Hp - 30)  # noqa: E731
        for k in range(len(te) - 1):
            d.line([(X(te[k]), Y(0)), (X(te[k]), Y(e[k]))], fill=(215, 215, 215))
        st = t0 + t - lag                                  # song time of each take frame
        for arr, lo, hi, col in ((gap, g_lo, g_hi, (230, 110, 0)), (jaw, j_lo, j_hi, (40, 100, 200))):
            pts = [(X(s), Y(np.clip((v - lo) / (hi - lo), 0, 1))) for s, v in zip(st, arr) if a <= s <= b and np.isfinite(v)]
            if len(pts) > 1:
                d.line(pts, fill=col, width=2)
        for s in np.arange(np.ceil(a * 10) / 10, b, 0.1):
            big = abs(s * 2 - round(s * 2)) < 1e-6
            d.line([(X(s), y0 + Hp - 15), (X(s), y0 + Hp - (9 if big else 12))], fill=(0, 0, 0))
            if big:
                d.text((X(s) - 14, y0 + Hp - 9), f"{s:.1f}", fill=(0, 0, 0))
        for et, kind in S["ev"]:
            if a <= et <= b:
                d.line([(X(et), y0), (X(et), y0 + Hp - 15)], fill=(220, 0, 0))
                d.text((X(et) + 3, y0 + 2), kind, fill=(220, 0, 0))
        d.text((pad, y0), f"{shot} {take} lag {lag:+.2f}   orange gap, blue jaw, grey voice", fill=(0, 0, 0))
        sel = (st >= a) & (st <= b) & np.isfinite(gap)
        idx = np.flatnonzero(sel)
        mins = [round(float(st[i]), 2) for i in idx[1:-1]
                if gap[i] <= np.nanmin(gap[max(0, i - 3):i + 4]) and gap[i] < np.nanpercentile(gap, 35)]
        print(f"lag {lag:+.2f}: mouth closures (song s) {mins}")
    dips = [round(float(te[i]), 2) for i in range(4, len(e) - 4) if e[i] <= e[i - 4:i + 5].min() and e[i] < 0.5
            and e[max(0, i - 15):i].max() > 0.55 and e[i + 1:i + 16].max() > 0.55]   # voiced on both sides within 0.15 s
    print("voice dips (song s)", dips)
    out = out or os.path.join(ROOT, "media/sing", shot, f"{take}_trace.png")
    img.save(out)
    print(os.path.relpath(out, ROOT))


if __name__ == "__main__":
    x = [v for v in sys.argv[1:] if not v.startswith("--")]
    o = dict(v[2:].split("=", 1) for v in sys.argv[1:] if v.startswith("--") and "=" in v)
    main(x[0], x[1], [float(v) for v in x[2:]], o.get("out"), float(o["from"]) if "from" in o else None,
         float(o["to"]) if "to" in o else None)
