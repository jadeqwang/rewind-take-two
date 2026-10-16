#!/usr/bin/env python3
"""Singing Jade (v6): every eye event in a synced singer file, frame by frame (Jade's rule: no half-blinks, i.e. lids that
sink partway and hang; a full natural blink, lids shut >= 2 frames, may stay).

    MPY=~/Documents/1-music-shipped/orbital-sunrise-video/video/out/.venv/bin/python
    $MPY tools/sing/v6_eyes.py FILE.mp4 IN_SONG_T [--upto=SECONDS] [--strip=OUT.jpg] [--from=F --to=F]

FILE time 0 = song IN_SONG_T (the wc_post contract). Openness = mean eyelid gap / inter-ocular (mouth.py "eye"), relative to
the clip's 90th percentile (= 1.0 open). Frames < 0.75 are grouped into events; each is classed
    full blink  : at least 2 frames < 0.30 (lids shut)
    half / droop: never below 0.30 (lids sink partway)
and printed with song m:ss.xx, song frame (song s x 24) and file frame. --strip writes eye crops of every frame in
[from, to] (default: the whole file) with those labels, so each event can be checked by eye."""
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mouth as MT  # noqa: E402


def mmss(t):
    return f"{int(t // 60)}:{t % 60:05.2f}"


def main(mp4, t_in, upto=None, strip=None, f0=None, f1=None):
    m = MT.cached(mp4)
    eye = np.array([np.nan if v is None else v for v in m["eye"]], float)
    n = len(eye) if upto is None else min(len(eye), int(round(upto * 24)))
    ref = np.nanpercentile(eye[:n], 90)
    o = eye[:n] / ref
    print(f"{os.path.basename(mp4)}: {n} frames, open ref {ref:.4f}; first 4 frames {np.round(o[:4], 2).tolist()}")
    ev, k = [], 0
    while k < n:
        if np.isfinite(o[k]) and o[k] < 0.75:
            j = k
            while j + 1 < n and np.isfinite(o[j + 1]) and o[j + 1] < 0.75:
                j += 1
            seg = o[k:j + 1]
            kind = "FULL blink" if (seg < 0.30).sum() >= 2 else ("shut 1 frame" if (seg < 0.30).any() else "HALF/droop")
            ev.append((k, j, kind, float(seg.min())))
            k = j + 1
        else:
            k += 1
    for a, b, kind, mn in ev:
        ta, tb = t_in + a / 24, t_in + (b + 1) / 24
        print(f"  {kind:12s} song {mmss(ta)}-{mmss(tb)} (f{round(ta * 24)}-f{round(t_in * 24) + b}), file frames {a}-{b}, "
              f"min {mn:.2f}; {np.round(o[a:b + 1], 2).tolist()}")
    miss = np.flatnonzero(~np.isfinite(o))
    if len(miss):
        print("  no face on file frames", miss.tolist()[:40])
    if strip:
        cap = cv2.VideoCapture(mp4)
        F = []
        while True:
            ok, fr = cap.read()
            if not ok:
                break
            F.append(fr)
        f0 = 0 if f0 is None else f0
        f1 = min(n - 1, len(F) - 1) if f1 is None else min(f1, len(F) - 1)
        mx, my, fh = (np.nanmedian(np.array([np.nan if v is None else v for v in m[k]], float)) for k in ("mx", "my", "fh"))
        cy = my - 0.42 * fh
        w, h = 0.62 * fh, 0.20 * fh
        tiles = []
        for i in range(f0, f1 + 1):
            c = F[i][int(cy - h):int(cy + h), int(mx - w):int(mx + w)]
            c = cv2.resize(c, (300, int(300 * h / w)))
            lab = f"{mmss(t_in + i / 24)} f{round((t_in + i / 24) * 24)} #{i} {o[i]:.2f}" if np.isfinite(o[i]) else f"#{i} --"
            cv2.rectangle(c, (0, 0), (300, 16), (0, 0, 0), -1)
            cv2.putText(c, lab, (3, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255) if o[i] >= 0.75 else (0, 0, 255), 1)
            tiles.append(c)
        while len(tiles) % 8:
            tiles.append(np.zeros_like(tiles[0]))
        cv2.imwrite(strip, np.vstack([np.hstack(tiles[i:i + 8]) for i in range(0, len(tiles), 8)]), [cv2.IMWRITE_JPEG_QUALITY, 85])
        print("  strip", strip)
    return o, ev


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    op = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    main(a[0], float(a[1]), float(op["upto"]) if "upto" in op else None, op.get("strip"),
         int(op["from"]) if "from" in op else None, int(op["to"]) if "to" in op else None)
