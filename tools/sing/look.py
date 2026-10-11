#!/usr/bin/env python3
"""Singing Jade, step 6: where the take's mouth is against her voice (lip lag), and what the face does.
After moongazing-public-version work/singer4/look.py; adds event-based lag (the handbook: read lag from mouth events,
not only from correlation, which was wrong on two of three shots there).

    MPY=~/Documents/orbital-sunrise-video/video/out/.venv/bin/python
    $MPY tools/sing/look.py SHOT take_N            (SHOT: S1 | E3 | V3S)

clip_time = song_time - ref_t0 + lag   (lag > 0: the take's mouth runs late, so the clip is played that much later).
1. Correlation lag: best shift (-0.6..+1.6 s) of the mouth opening (inner-lip gap + jawOpen, mouth.py) against the
   vocal stem's level.
2. Event lags: lip closures on the bilabials ('b' of before, 'm' of my) and the opening at the first word, each looked
   for within +-0.3 s of where the correlation lag puts it; the median of these is the event lag.
Writes take_N.look.json, take_N_look.jpg (whole clip, 2 frames/s, song time at the chosen lag) and take_N_win.jpg
(face crops every 2nd frame across the phrase), plus likeness numbers (face height, eye opening, iris, yaw) per take."""
import json
import os
import sys
import wave

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mouth as MT  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VOC = os.path.join(ROOT, "analysis/cinematic/vocals_bs_roformer_48k.wav")
SHOTS = {   # ref_t0, phrase window (for the face strip), events: (song time, kind)
    "S1": dict(t0=12.90, win=(13.10, 18.40), ev=[(13.20, "open"), (13.89, "close"), (16.286, "close"), (18.25, "end")]),
    "E3": dict(t0=119.14, win=(119.30, 122.95), ev=[(119.44, "open")]),
    "V3S": dict(t0=153.68, win=(153.90, 159.30), ev=[(153.98, "open"), (154.722, "close"), (157.12, "close"), (159.14, "end")]),
}


def env(t0, dur, hop=1 / 96):
    w = wave.open(VOC)
    sr = w.getframerate()
    w.setpos(int(t0 * sr))
    a = np.frombuffer(w.readframes(int(dur * sr)), np.int16).reshape(-1, w.getnchannels()).mean(1) / 32768
    h = int(sr * hop)
    k = len(a) // h
    db = 20 * np.log10(np.sqrt((a[:k * h].reshape(k, h) ** 2).mean(1) + 1e-9))
    lo, hi = np.percentile(db, 20), np.percentile(db, 98)
    return np.clip((db - lo) / (hi - lo), 0, 1), hop


def event_lag(t, mo, ev_t, kind, t0, lag0, rad=0.3):
    """Clip time of the mouth event nearest to where lag0 predicts it; returns the lag it implies (or None)."""
    c = ev_t - t0 + lag0
    sel = (t >= c - rad) & (t <= c + rad) & np.isfinite(mo)
    if sel.sum() < 4:
        return None
    tt, mm = t[sel], mo[sel]
    if kind == "close":                       # lips shut: the minimum of the opening
        tc = tt[int(np.argmin(mm))]
    elif kind == "open":                      # first frame past 40 % of the local rise
        lo, hi = np.nanmin(mm), np.nanmax(mm)
        idx = np.where(mm > lo + 0.4 * (hi - lo))[0]
        if not len(idx):
            return None
        tc = tt[idx[0]]
    else:                                     # end of phrase: last frame above 40 % before the fall
        lo, hi = np.nanmin(mm), np.nanmax(mm)
        idx = np.where(mm > lo + 0.4 * (hi - lo))[0]
        if not len(idx):
            return None
        tc = tt[idx[-1]]
    return round(float(tc - (ev_t - t0)), 3)


def main(shot, take):
    S = SHOTS[shot]
    d = os.path.join(ROOT, "media/sing", shot)
    mp4 = os.path.join(d, take + ".mp4")
    t0 = S["t0"]
    m = MT.cached(mp4)
    fps, n = m["fps"], m["n"]
    f = lambda k: np.array([np.nan if v is None else v for v in m[k]], float)  # noqa: E731
    gap, jaw = f("gap"), f("jaw")
    z = lambda x: (x - np.nanmean(x)) / (np.nanstd(x) + 1e-9)  # noqa: E731
    mo = np.where(np.isfinite(gap), z(gap) + z(np.where(np.isfinite(jaw), jaw, np.nanmean(jaw))), np.nan)
    dur = n / fps
    e, hop = env(t0, dur + 0.01)
    tt = np.arange(len(e)) * hop
    t = np.arange(n) / fps
    res, best = [], (-9, 0.0)
    for lag in np.arange(-0.6, 1.6, 1 / 96):
        x = np.interp(tt + lag, t, np.nan_to_num(mo, nan=np.nanmean(mo)), left=np.nan, right=np.nan)
        v = np.isfinite(x)
        if v.sum() < 96 * 2:
            continue
        r = np.corrcoef(x[v], e[v])[0, 1]
        res.append((round(float(lag), 3), round(float(r), 3)))
        if r > best[0]:
            best = (r, float(lag))
    r, lag_c = best
    evs = [(et, k, event_lag(t, mo, et, k, t0, lag_c)) for et, k in S["ev"]]
    el = [x for _, _, x in evs if x is not None]
    lag_e = float(np.median(el)) if el else None
    lag = lag_e if lag_e is not None and abs(lag_e - lag_c) <= 0.3 else lag_c
    hits = np.isfinite(gap)
    fh = f("fh")
    out = {"shot": shot, "take": take, "frames": n, "fps": fps, "face_hit": round(float(hits.mean()), 3),
           "lag_corr": round(lag_c, 3), "r": round(float(r), 3), "events": [dict(t=a, kind=b, lag=c) for a, b, c in evs],
           "lag_events": lag_e, "lag": round(float(lag), 3),
           "fh_px": [round(float(np.nanmin(fh)), 1), round(float(np.nanmedian(fh)), 1), round(float(np.nanmax(fh)), 1)],
           "eye": [round(float(np.nanmin(f("eye"))), 3), round(float(np.nanmedian(f("eye"))), 3)],
           "iris_first_last": [round(float(np.nanmean(f("iris")[:12])), 4), round(float(np.nanmean(f("iris")[-12:])), 4)],
           "yaw": [round(float(np.nanmin(f("yaw"))), 3), round(float(np.nanmax(f("yaw"))), 3)]}
    json.dump(out, open(os.path.join(d, take + ".look.json"), "w"), indent=1)
    print(json.dumps(out))
    cap = cv2.VideoCapture(mp4)
    F = []
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        F.append(fr)
    w0, w1 = S["win"]
    tiles = []
    for i in range(0, len(F), 12):
        tl = cv2.resize(F[i], (480, 270))
        st = t0 + i / fps - lag
        cv2.putText(tl, f"{i / fps:.1f}s song {st:.2f}", (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        tiles.append(tl)
    while len(tiles) % 4:
        tiles.append(np.zeros_like(tiles[0]))
    cv2.imwrite(os.path.join(d, take + "_look.jpg"), np.vstack([np.hstack(tiles[i:i + 4]) for i in range(0, len(tiles), 4)]),
                [cv2.IMWRITE_JPEG_QUALITY, 85])
    mx, my = f("mx"), f("my")
    cx, cy, s = np.nanmedian(mx), np.nanmedian(my) - 0.28 * np.nanmedian(fh), int(np.nanmedian(fh) * 0.8)
    tiles = []
    for i in range(int(round((w0 - t0 + lag) * fps)), int(round((w1 - t0 + lag) * fps)) + 1, 3):
        if 0 <= i < len(F):
            c = F[i][max(0, int(cy - s)):int(cy + s), max(0, int(cx - s)):int(cx + s)]
            c = cv2.resize(c, (200, 200))
            cv2.putText(c, f"{t0 + i / fps - lag:.2f}", (4, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            tiles.append(c)
    while len(tiles) % 10:
        tiles.append(np.zeros_like(tiles[0]))
    cv2.imwrite(os.path.join(d, take + "_win.jpg"), np.vstack([np.hstack(tiles[i:i + 10]) for i in range(0, len(tiles), 10)]),
                [cv2.IMWRITE_JPEG_QUALITY, 85])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
