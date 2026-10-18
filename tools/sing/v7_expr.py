#!/usr/bin/env python3
"""Singing Jade (v7): how much a take ACTS (Jade, 2026-10-18: "the normal amount of expression that you would expect from a
singer in a music video. I think some of the shortcomings of previous versions came from a lack of expression"), and
whether her face stays her own. Per frame (MediaPipe FaceLandmarker + blendshapes, tracked in the mouth.json face box):

    expression  browInnerUp, browOuterUp (mean L/R), browDown (mean L/R), jawOpen, mouthSmile (mean L/R),
                cheekSquint (mean L/R), eyeBlink (mean L/R), inner-lip gap / face height (mouth.py "gap"),
                brow lift = mean brow-to-eye distance / inter-ocular (geometric, independent of the blendshape model)
    head        yaw (mouth.py), roll (eye line, deg), pitch proxy ((nose tip y - eye mid y) / face height),
                nose-tip x / y (px, as a fraction of inter-ocular, so camera-independent)
    identity    inter-ocular (33-263), eye width (33-133, 362-263 mean), face width (234-454), face height (10-152), px

    MPY=~/Documents/1-music-shipped/orbital-sunrise-video/video/out/.venv/bin/python
    $MPY tools/sing/v7_expr.py TAKE.mp4 [...] [--first=IMG] [--from=S --to=S]  -> TAKE.expr.json (cached) + a table
Ranges are p95 - p5 over the frames (or over clip seconds [from, to]). --first measures the identity numbers on the
start image resized to the take's size, for comparison."""
import json
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mouth as MT  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BROW_L, BROW_R = [70, 63, 105, 66, 107], [300, 293, 334, 296, 336]
EYE_L, EYE_R = [33, 133, 159, 145], [263, 362, 386, 374]


def row(L, bs):
    d = lambda a, b: float(np.linalg.norm(L[a] - L[b]))  # noqa: E731
    io, fh = d(33, 263), d(10, 152)
    el, er = L[EYE_L].mean(0), L[EYE_R].mean(0)
    lift = (np.linalg.norm(L[BROW_L].mean(0) - el) + np.linalg.norm(L[BROW_R].mean(0) - er)) / 2 / io
    m2 = lambda k: (bs.get(k + "Left", np.nan) + bs.get(k + "Right", np.nan)) / 2  # noqa: E731
    eye_mid = (L[33] + L[263]) / 2
    return dict(browInnerUp=bs.get("browInnerUp", np.nan), browOuterUp=m2("browOuterUp"), browDown=m2("browDown"),
                jawOpen=bs.get("jawOpen", np.nan), smile=m2("mouthSmile"), cheekSquint=m2("cheekSquint"),
                blink=m2("eyeBlink"), gap=np.mean([d(13, 14), d(82, 87), d(312, 317)]) / fh, brow_lift=float(lift),
                yaw=float((L[1][0] - eye_mid[0]) / io),
                roll=float(np.degrees(np.arctan2(L[263][1] - L[33][1], L[263][0] - L[33][0]))),
                pitch=float((L[1][1] - eye_mid[1]) / fh), nose_x=float(L[1][0]), nose_y=float(L[1][1]),
                io=io, eye_w=(d(33, 133) + d(362, 263)) / 2, face_w=d(234, 454), face_h=fh)


def track(mp4):
    js = mp4[:-4] + ".expr.json"
    if os.path.exists(js) and os.path.getmtime(js) >= max(os.path.getmtime(mp4), os.path.getmtime(__file__)):
        return json.load(open(js))
    m = MT.cached(mp4)
    cap = cv2.VideoCapture(mp4)
    rows, i = [], 0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
        H, W = rgb.shape[:2]
        hit = None
        mx, my, fh = (m[k][i] if i < len(m[k]) else None for k in ("mx", "my", "fh"))
        if mx is not None:
            s = 1.6 * fh
            hit = MT.detect(rgb, (max(0, mx - s), max(0, my - 1.3 * s), min(W, mx + s), min(H, my + 0.7 * s)))
        if hit is None:
            hit = MT.detect(rgb, (0, 0, W, H))
        rows.append(None if hit is None else {k: (None if not np.isfinite(v) else round(float(v), 5)) for k, v in row(*hit).items()})
        i += 1
    out = {"file": os.path.relpath(mp4, ROOT), "fps": m["fps"], "rows": rows}
    json.dump(out, open(js, "w"))
    return out


def summary(mp4, t0=None, t1=None):
    r = track(mp4)
    fps = r["fps"]
    R = r["rows"]
    a = int(round((t0 or 0) * fps))
    b = len(R) if t1 is None else min(len(R), int(round(t1 * fps)))
    R = [x for x in R[a:b] if x]
    col = lambda k: np.array([np.nan if x[k] is None else x[k] for x in R], float)  # noqa: E731
    rng = lambda k: float(np.nanpercentile(col(k), 95) - np.nanpercentile(col(k), 5))  # noqa: E731
    io = np.nanmedian(col("io"))
    s = dict(n=len(R),
             browInnerUp_rng=rng("browInnerUp"), browInnerUp_p95=float(np.nanpercentile(col("browInnerUp"), 95)),
             browOuterUp_rng=rng("browOuterUp"), browDown_rng=rng("browDown"), brow_lift_rng=rng("brow_lift"),
             jaw_p95=float(np.nanpercentile(col("jawOpen"), 95)), jaw_rng=rng("jawOpen"), gap_p95=float(np.nanpercentile(col("gap"), 95)),
             cheek_rng=rng("cheekSquint"), smile_max=float(np.nanmax(col("smile"))), smile_p95=float(np.nanpercentile(col("smile"), 95)),
             yaw_rng=rng("yaw"), roll_rng=rng("roll"), pitch_rng=rng("pitch"),
             x_rng_io=rng("nose_x") / io, y_rng_io=rng("nose_y") / io,
             io=float(io), eye_w=float(np.nanmedian(col("eye_w"))), face_w=float(np.nanmedian(col("face_w"))),
             face_h=float(np.nanmedian(col("face_h"))),
             io_rng=[float(np.nanpercentile(col("io"), 5)), float(np.nanpercentile(col("io"), 95))],
             eye_w_rng=[float(np.nanpercentile(col("eye_w"), 5)), float(np.nanpercentile(col("eye_w"), 95))],
             face_w_rng=[float(np.nanpercentile(col("face_w"), 5)), float(np.nanpercentile(col("face_w"), 95))])
    return s


def first(img, size):
    a = np.asarray(cv2.resize(cv2.cvtColor(cv2.imread(img), cv2.COLOR_BGR2RGB), size, interpolation=cv2.INTER_AREA))
    hit = MT.detect(a, (0, 0, a.shape[1], a.shape[0]))
    return row(*hit)


KEYS = [("browInnerUp_rng", "brInUp"), ("browOuterUp_rng", "brOutUp"), ("browDown_rng", "brDown"), ("brow_lift_rng", "lift"),
        ("jaw_p95", "jaw95"), ("gap_p95", "gap95"), ("cheek_rng", "cheek"), ("smile_max", "smileMx"),
        ("yaw_rng", "yaw"), ("roll_rng", "roll°"), ("pitch_rng", "pitch"), ("x_rng_io", "x/io"), ("y_rng_io", "y/io"),
        ("io", "io"), ("eye_w", "eyeW"), ("face_w", "faceW")]


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    o = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    t0, t1 = (float(o["from"]) if "from" in o else None), (float(o["to"]) if "to" in o else None)
    print(f"{'take':34s}" + "".join(f"{h:>8s}" for _, h in KEYS))
    for p in a:
        s = summary(p, t0, t1)
        print(f"{os.path.basename(p)[:34]:34s}" + "".join(f"{s[k]:8.3f}" if k not in ("io", "eye_w", "face_w") else f"{s[k]:8.1f}"
                                                          for k, _ in KEYS))
        json.dump(s, open(p[:-4] + ".expr_summary.json", "w"), indent=1)
    if "first" in o:
        cap = cv2.VideoCapture(a[0])
        size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        f = first(o["first"], size)
        print(f"first frame {os.path.basename(o['first'])} at {size}: io {f['io']:.1f} eyeW {f['eye_w']:.1f} faceW {f['face_w']:.1f} "
              f"faceH {f['face_h']:.1f}")
