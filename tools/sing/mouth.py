#!/usr/bin/env python3
"""Per-frame face measurements of a generated take (MediaPipe FaceLandmarker, CPU), cached as take_N.mouth.json.

Copied from moongazing-public-version work/engine/tools/sync/mouth.py. Runs in the MediaPipe venv:  MPY=~/Documents/orbital-sunrise-video/video/out/.venv/bin/python
    $MPY tools/sing/mouth.py media/sing/S1/take_1.mp4

Tracking: the detector only finds large faces, so each frame is searched in a crop around the previous face
(2.4x the face box, upscaled to >= 640 px); on a miss, a grid of crops (60/45/33 % of the frame) is searched.
Per frame (NaN when no face):
    gap    inner-lip opening: mean of 3 inner-lip pairs (13-14, 82-87, 312-317) / face height (10-152)
    jaw    blendshape jawOpen          width  mouth corners 78-308 / face height
    eye    mean eyelid opening (159-145, 386-374) / inter-ocular (33-263)
    iris   mean iris diameter (469-471, 474-476) / inter-ocular   (likeness: Seedance shrinks eyes over a clip)
    yaw    (nose tip - eye-corner midpoint).x / inter-ocular: 0 = frontal, |0.3+| = three-quarter; a jump = head turn
    mouth  mouth centre (px) and face height (px), for crops
"""
import json
import os
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.environ.get("FACE_LANDMARKER", os.path.expanduser("~/Documents/moongazing/tools/sync/models/face_landmarker.task"))
_LM = None


def landmarker():
    global _LM
    if _LM is None:
        os.environ.setdefault("GLOG_minloglevel", "2")
        from mediapipe.tasks.python import BaseOptions, vision
        opt = vision.FaceLandmarkerOptions(base_options=BaseOptions(model_asset_path=MODEL), output_face_blendshapes=True,
                                           num_faces=1, min_face_detection_confidence=0.3,
                                           min_face_presence_confidence=0.3)
        _LM = vision.FaceLandmarker.create_from_options(opt)
    return _LM


def detect(rgb, box):
    """Run the landmarker on rgb[box]; returns (landmarks in full-frame px (478x2), blendshapes) or None."""
    import mediapipe as mp
    x0, y0, x1, y1 = [int(v) for v in box]
    crop = rgb[y0:y1, x0:x1]
    if crop.size == 0:
        return None
    s = max(1.0, 640 / max(crop.shape[:2]))
    if s > 1:
        crop = cv2.resize(crop, None, fx=s, fy=s, interpolation=cv2.INTER_CUBIC)
    r = landmarker().detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(crop)))
    if not r.face_landmarks:
        return None
    L = np.array([[p.x * crop.shape[1] / s + x0, p.y * crop.shape[0] / s + y0] for p in r.face_landmarks[0]])
    bs = {b.category_name: b.score for b in r.face_blendshapes[0]} if r.face_blendshapes else {}
    return L, bs


def grid_boxes(W, H):
    for cs in (1.0, 0.6, 0.45, 0.33):
        cw, ch = int(W * cs), int(min(H, W * cs))
        for yy in np.linspace(0, H - ch, 1 if ch >= H else 4).astype(int):
            for xx in np.linspace(0, W - cw, 1 if cw >= W else 6).astype(int):
                yield (xx, yy, xx + cw, yy + ch)


def measure(L, bs):
    d = lambda a, b: float(np.linalg.norm(L[a] - L[b]))
    fh = d(10, 152)
    io = d(33, 263)
    gap = np.mean([d(13, 14), d(82, 87), d(312, 317)]) / fh
    return {"gap": gap, "jaw": bs.get("jawOpen", np.nan), "width": d(78, 308) / fh,
            "eye": (d(159, 145) + d(386, 374)) / 2 / io, "iris": (d(469, 471) + d(474, 476)) / 2 / io,
            "yaw": float((L[1][0] - (L[33][0] + L[263][0]) / 2) / io),   # nose tip vs eye-corner midpoint: 0 = frontal
            "mx": float((L[13][0] + L[14][0]) / 2), "my": float((L[13][1] + L[14][1]) / 2), "fh": fh,
            "box": [float(L[:, 0].min()), float(L[:, 1].min()), float(L[:, 0].max()), float(L[:, 1].max())]}


def track(mp4):
    cap = cv2.VideoCapture(mp4)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    rows, prev, since_grid, grays = [], None, 99, []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
        grays.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY))
        H, W = rgb.shape[:2]
        hit = None
        if prev is not None:
            x0, y0, x1, y1 = prev
            for k in (0.8, 1.0, 0.65, 1.3, 1.8):
                cx, cy, s = (x0 + x1) / 2, (y0 + y1) / 2, k * max(x1 - x0, y1 - y0)
                hit = detect(rgb, (max(0, cx - s), max(0, cy - s), min(W, cx + s), min(H, cy + s)))
                if hit is not None:
                    break
        if hit is None and (prev is None or since_grid >= 8):
            since_grid = 0
            for b in grid_boxes(W, H):
                hit = detect(rgb, b)
                if hit is not None:
                    break
        since_grid += 1
        if hit is None:
            rows.append(None)
            continue
        m = measure(*hit)
        prev = m["box"]
        rows.append(m)
    keys = ["gap", "jaw", "width", "eye", "iris", "yaw", "mx", "my", "fh"]
    out = {"file": mp4, "fps": fps, "n": len(rows), "hit": float(np.mean([r is not None for r in rows])) if rows else 0}
    for k in keys:
        out[k] = [None if r is None or not np.isfinite(r[k]) else round(float(r[k]), 5) for r in rows]
    out["roi_dark"] = roi_dark(grays, out)
    return out


def roi_dark(grays, out):
    """Fallback openness for frames the landmarker misses (profiles, line art): in a mouth box centred on the
    interpolated mouth position (0.5 x 0.3 face heights), the fraction of pixels darker than the box's
    clip-wide median minus 0.6 std. Open mouths show a dark interior in most of our styles."""
    ok = [i for i, v in enumerate(out["mx"]) if v is not None]
    if len(ok) < 2:
        return None
    idx = np.arange(len(grays))
    mx = np.interp(idx, ok, [out["mx"][i] for i in ok])
    my = np.interp(idx, ok, [out["my"][i] for i in ok])
    fh = float(np.median([out["fh"][i] for i in ok]))
    w, h = 0.25 * fh, 0.15 * fh
    crops = []
    for g, x, y in zip(grays, mx, my):
        c = g[int(max(0, y - h)):int(y + h), int(max(0, x - w)):int(x + w)].astype(np.float32)
        crops.append(c)
    allpx = np.concatenate([c.ravel() for c in crops if c.size])
    thr = np.median(allpx) - 0.6 * allpx.std()
    return [round(float((c < thr).mean()), 4) if c.size else None for c in crops]


def cached(mp4):
    js = mp4[:-4] + ".mouth.json"
    if os.path.exists(js) and os.path.getmtime(js) >= max(os.path.getmtime(mp4), os.path.getmtime(__file__)):
        return json.load(open(js))
    r = track(mp4)
    json.dump(r, open(js, "w"))
    return r


if __name__ == "__main__":
    for p in sys.argv[1:]:
        r = cached(p)
        print(p, f"frames {r['n']} face-hit {r['hit']:.2f}")
