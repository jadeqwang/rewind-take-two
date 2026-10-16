#!/usr/bin/env python3
"""Singing Jade (v6): lip lag over a song window and in sliding 2 s windows (the check v5/v5c did by hand), so the
look.py whole-clip number can be confirmed or overruled.

    MPY=~/Documents/1-music-shipped/orbital-sunrise-video/video/out/.venv/bin/python
    $MPY tools/sing/v6_lagwin.py SHOT TAKE A B            (song window A..B, e.g. S1 v6_take_1 13.05 14.95)

clip_time = song_time - ref_t0 + lag. Signal: the inner-lip gap (mouth.py) and jawOpen, z-scored, against the vocal stem's
level (look.env). Prints the best lag (r) over A..B for gap, jaw and both; then 2 s windows every 0.5 s across the take;
then, at the best lag, the song times of the mouth's local minima (closures) inside A..B, to set against the voice."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import look as LK  # noqa: E402
import mouth as MT  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def best(t, sig, te, e, a, b, lags):
    sel = (te >= a) & (te <= b)
    out = []
    for lag in lags:
        x = np.interp(te[sel] - LK_T0 + lag, t, sig, left=np.nan, right=np.nan)
        v = np.isfinite(x)
        if v.sum() < 40:
            continue
        out.append((float(np.corrcoef(x[v], e[sel][v])[0, 1]), float(lag)))
    return max(out) if out else (np.nan, np.nan)


def main(shot, take, a, b):
    global LK_T0
    S = LK.SHOTS[shot]
    LK_T0 = t0 = S["t0"]
    m = MT.cached(os.path.join(ROOT, "media/sing", shot, take + ".mp4"))
    fps, n = m["fps"], m["n"]
    f = lambda k: np.array([np.nan if v is None else v for v in m[k]], float)  # noqa: E731
    z = lambda x: (x - np.nanmean(x)) / (np.nanstd(x) + 1e-9)  # noqa: E731
    gap, jaw = z(f("gap")), z(f("jaw"))
    both = np.nan_to_num(gap) + np.nan_to_num(jaw)
    t = np.arange(n) / fps
    # the vocal level from just before the take's song span
    e, hop = LK.env(t0 - 1.0, n / fps + 2.0)
    te = t0 - 1.0 + np.arange(len(e)) * hop
    lags = np.arange(-0.6, 1.8, 1 / 96)
    print(f"{shot} {take} window {a:.2f}-{b:.2f}")
    for name, sig in (("gap", np.nan_to_num(gap)), ("jaw", np.nan_to_num(jaw)), ("both", both)):
        r, lag = best(t, sig, te, e, a, b, lags)
        print(f"  {name:4s} best lag {lag:+.3f} (r {r:.2f})")
    r, lag = best(t, both, te, e, a, b, lags)
    wins = []
    for w0 in np.arange(t0, t0 + n / fps - 2.0 + 1e-6, 0.5):
        rr, ll = best(t, both, te, e, w0, w0 + 2.0, lags)
        wins.append(f"{w0:.1f}:{ll:+.2f}(r{rr:.2f})")
    print("  2 s windows:", " ".join(wins))
    # closures (local minima of the gap) inside the window at the best lag
    g = f("gap")
    st = t0 + t - lag
    mins = [round(float(st[i]), 2) for i in range(1, n - 1)
            if np.isfinite(g[i]) and a <= st[i] <= b and g[i] <= np.nanmin(g[max(0, i - 3):i + 4]) and g[i] < np.nanpercentile(g, 35)]
    print(f"  at {lag:+.3f}: mouth closures (song s) {mins}")
    sel = (te >= a) & (te <= b)
    ee = e[sel]
    dips = [round(float(te[sel][i]), 2) for i in range(4, len(ee) - 4) if ee[i] <= ee[i - 4:i + 5].min() and ee[i] < 0.5]
    print(f"  voice dips (song s) {dips}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]))
