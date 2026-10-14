#!/usr/bin/env python
"""Canon pencils (v6, docs/revisions/v6/o2_erasers.md): the two crossed pencils in Jade's bun have ONE pale-blue eraser
and one pink eraser. Some generated takes drew both erasers pink. This recolours one pencil's eraser to the film's pale
blue in every frame, as a pixel pass (no generative model):

  * the eraser is tracked by anchors (per-frame centroid keys in the spec, linearly interpolated as the search prior);
  * per frame, the eraser is the small non-dark region enclosed by its ink outline nearest the prior (the walls behind
    her are often the same pink, so colour alone cannot separate it; the outline does). The pale-lavender ferrule is
    excluded by hue, so it keeps its colour;
  * inside that mask the hue is set to the canon blue (214 deg) and the saturation scaled to the canon's (pink ~95 ->
    blue ~56, OpenCV units), value kept, so shading, grain and fades carry over. The eraser's own outline pixels go dark
    slate (as on the canon pencils) instead of dark red;
  * "smear" frame ranges also take the motion-smeared pink right next to the eraser; a frame with no enclosed region
    reuses the previous frame's mask when the clip holds a pose (these takes move in 2-frame steps).

v7 (docs/revisions/v7/erasers.md) adds, per spec (defaults keep the v6 behaviour):
  * "target": "blue" (default) | "pink" | [hue, sat] (OpenCV units). Canon pink = the pink erasers of D3 / P2 / D6
    (good frames): RGB ~(224, 142, 165), hue ~344 deg (172), saturation ~0.35 (90).
  * "sat_mode": "scale" (default: the v6 scale, pink 95 -> blue 56) | "target": saturation SET to the target's, so a
    white, grey or lavender eraser (no colour to scale) takes the canon colour; value is kept, times "v_gain"
    (default 1), capped at "v_cap" (default 255): a paper-white eraser can be brought down to the canon's lightness.
  * "any_hue": true: the eraser is the enclosed non-dark region whatever its hue (white / grey erasers); with
    "s_max" (default 255) as an upper saturation bound for it.

Canon pale blue: median of the blue eraser in G1 take_3 / G2 take_5 (render/timeline/E.js G_CLIPS) and
media/shots/O2/_ref_bun_two_pencils.jpg: RGB ~(175, 200, 224), hue 214 deg, saturation ~0.22.

  tools/engrave/.venv/bin/python tools/blue_eraser.py apply tools/blue_eraser_specs/O2.json
  tools/engrave/.venv/bin/python tools/blue_eraser.py track IN.mp4 FRAME X Y [--maxd 25]   (first-pass anchors, for review)
"""
import argparse
import json
import os
import shutil
import subprocess

import av
import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TGT_H = 107            # OpenCV hue units (x2 = 214 deg)
SAT_K = 56 / 95.0      # canon blue saturation / O2 pink eraser saturation
SAT_CAP = 70           # never more saturated than a pale blue
VTS = (165, 185, 145, 200)   # outline darkness thresholds tried in turn


def ffmpeg():
    for c in (os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg"), shutil.which("ffmpeg")):
        if c and os.path.exists(c):
            return c


def pinkhue(h):
    return (h >= 150) | (h <= 22)


TARGETS = {"blue": (TGT_H, 56), "pink": (172, 90)}


def find(f, p, maxd, R=40, max_area=400, max_wh=30, min_area=6, color=None, any_hue=False, s_max=255):
    """Enclosed eraser region nearest p. Returns (mask, centroid, area) or None, plus the ROI, its HSV and origin.
    color = (hue_lo, hue_hi, sat_min): where the backdrop is not pink (the night car plates), the eraser is simply the
    strongly pink blob (hue >= hue_lo or <= hue_hi, OpenCV units) nearest p; no enclosure test."""
    x0, y0 = max(0, p[0] - R), max(0, p[1] - R)
    roi = np.ascontiguousarray(f[y0:p[1] + R, x0:p[0] + R])
    hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
    h, s, v = [hsv[..., k].astype(int) for k in range(3)]
    best = None
    for vt in (VTS if color is None else (110,)):
        if color is None:
            dd = cv2.dilate((v < vt).astype(np.uint8), np.ones((3, 3), np.uint8))   # close small gaps in the outline
            hue_ok = (s <= s_max) if any_hue else (pinkhue(h) & (s > 22))
            cand = ((dd == 0) & hue_ok).astype(np.uint8)
        else:
            cand = (((h >= color[0]) | (h <= color[1])) & (s > color[2]) & (v > vt)).astype(np.uint8)
        n, lab, st, c = cv2.connectedComponentsWithStats(cand, connectivity=4)
        Hh, Ww = cand.shape
        for k in range(1, n):
            X, Y, w, hh, a = st[k]
            if color is None and (X == 0 or Y == 0 or X + w >= Ww or Y + hh >= Hh):   # touches the ROI edge: not enclosed
                continue
            if not (min_area <= a <= max_area) or w > max_wh or hh > max_wh:
                continue
            cx, cy = c[k][0] + x0, c[k][1] + y0
            d = float(np.hypot(cx - p[0], cy - p[1]))
            if d <= maxd and (best is None or d < best[0]):
                best = (d, (lab == k).astype(np.uint8), (int(round(cx)), int(round(cy))), int(a))
        if best:
            break
    return (None if best is None else best[1:]), roi, hsv, (x0, y0)


def alpha_for(comp, hsv):
    v, h = hsv[..., 2].astype(int), hsv[..., 0].astype(int)
    full = (cv2.dilate(comp, np.ones((3, 3), np.uint8)) & (v >= 120).astype(np.uint8)) | comp
    ring = cv2.dilate(comp, np.ones((7, 7), np.uint8)) & ((v < 205) & pinkhue(h)).astype(np.uint8) & (1 - full)
    a = np.maximum(full, ring).astype(np.float32)
    soft = cv2.GaussianBlur(a, (0, 0), 0.6)
    al = np.where((a > 0) | (v < 205), np.maximum(a, soft), 0) * (cv2.dilate(comp, np.ones((9, 9), np.uint8)) > 0)
    return al, (1 - full).astype(np.float32)


def recolor(roi, hsv, a, ringw, tgt=(TGT_H, 56), sat_mode="scale", v_gain=1.0, v_cap=255):
    o = hsv.astype(np.float32)
    o[..., 0] = tgt[0]
    if sat_mode == "target":
        s2 = np.full_like(o[..., 1], float(tgt[1]))
        o[..., 2] = np.where(ringw < 0.5, np.minimum(o[..., 2] * v_gain, v_cap), o[..., 2])
    else:
        s2 = np.minimum(o[..., 1] * SAT_K * tgt[1] / 56.0, SAT_CAP * tgt[1] / 56.0)
    o[..., 1] = s2 * (1 - ringw) + np.minimum(o[..., 1] * 0.25, 40) * ringw
    new = cv2.cvtColor(o.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)
    return (roi * (1 - a[..., None]) + new * a[..., None] + 0.5).astype(np.uint8)


def frames_of(path):
    c = av.open(path)
    vs = c.streams.video[0]
    fr = [f.to_ndarray(format="rgb24") for f in c.decode(vs)]
    return fr, vs.average_rate


def ranges(spec_list):
    out = set()
    for r in spec_list:
        a, b = (r, r) if isinstance(r, int) else r
        out.update(range(a, b + 1))
    return out


def apply(spec, frames, log=None):
    n = len(frames)
    keys = sorted((int(k), v) for k, v in spec["anchors"].items())
    ki = [k for k, _ in keys]
    prior = [(int(round(np.interp(i, ki, [v[0] for _, v in keys]))), int(round(np.interp(i, ki, [v[1] for _, v in keys]))))
             for i in range(n)]
    maxd = {i: spec.get("maxd", 12) for i in range(n)}
    for r, d in spec.get("tight", {}).items():
        a, b = (int(x) for x in r.split("-")) if "-" in r else (int(r), int(r))
        for i in range(a, b + 1):
            maxd[i] = d
    smear, skip = ranges(spec.get("smear", [])), ranges(spec.get("skip", []))
    R, max_area, max_wh = spec.get("roi", 40), spec.get("max_area", 400), spec.get("max_wh", 30)
    min_area, smear_k = spec.get("min_area", 20), spec.get("smear_px", 11)
    color = spec.get("color")
    t = spec.get("target", "blue")
    tgt = TARGETS[t] if isinstance(t, str) else tuple(t)
    look = dict(tgt=tgt, sat_mode=spec.get("sat_mode", "scale"), v_gain=spec.get("v_gain", 1.0), v_cap=spec.get("v_cap", 255))
    any_hue, s_max = spec.get("any_hue", False), spec.get("s_max", 255)
    last, out = None, []
    for i in range(n):
        f = frames[i].copy()
        if i in skip:
            out.append(f); log is not None and log.append([i, "skip"]); last = None
            continue
        b, roi, hsv, (x0, y0) = find(f, prior[i], maxd[i], R, max_area, max_wh, color=color, any_hue=any_hue, s_max=s_max)
        how = "enclosed"
        if b is not None and b[2] < min_area:
            b = None
        if b is None and last is not None:
            # no region found: carry the previous frame's mask, moved with the anchors, and keep only its pink pixels
            comp, (x0, y0), lp = last
            x0, y0 = x0 + prior[i][0] - lp[0], y0 + prior[i][1] - lp[1]
            roi = np.ascontiguousarray(f[y0:y0 + comp.shape[0], x0:x0 + comp.shape[1]])
            hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
            hh, ss = hsv[..., 0].astype(int), hsv[..., 1].astype(int)
            keep = (ss <= s_max) & (hsv[..., 2] > 120) if any_hue else (((hh >= 150) | (hh <= 6)) & (ss > 20))
            comp = comp & keep.astype(np.uint8)
            how, cen, area = "reuse-prev", prior[i], int(comp.sum())
        elif b is None:
            out.append(f); log is not None and log.append([i, "MISS", list(prior[i])])
            continue
        else:
            comp, cen, area = b
        last = (comp.copy(), (x0, y0), prior[i])
        if i in smear:     # motion smear: take the pink right next to the eraser too (only where the backdrop is not pink)
            h, s, v = [hsv[..., k].astype(int) for k in range(3)]
            near = cv2.dilate(comp, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (smear_k, smear_k)))
            comp = comp | (near & (((h >= 158) | (h <= 1)) & (s > 28) & (v > 130)).astype(np.uint8))
        a, ringw = alpha_for(comp, hsv)
        f[y0:y0 + roi.shape[0], x0:x0 + roi.shape[1]] = recolor(roi, hsv, a, ringw, **look)
        out.append(f)
        log is not None and log.append([i, how, list(cen), area])
    return out


def encode(frames, fps, path, crf, extra=()):
    H, W = frames[0].shape[:2]
    p = subprocess.Popen([ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(fps), "-i", "-", "-c:v", "libx264", "-crf", str(crf), "-pix_fmt", "yuv420p", *extra, path],
                         stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(np.ascontiguousarray(f).tobytes())
    p.stdin.close()
    assert p.wait() == 0


def track(frames, i0, xy, maxd=25, any_hue=False, R=40):
    """First pass: follow the enclosed eraser region by position continuity, both ways from a seed. Review the result."""
    res = {}
    for rng in (range(i0, len(frames)), range(i0, -1, -1)):
        p = tuple(xy)
        for i in rng:
            b, *_ = find(frames[i], p, maxd, R, any_hue=any_hue)
            if b is not None:
                p = b[1]
                res[i] = list(p)
    return dict(sorted(res.items()))


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    a1 = sp.add_parser("apply"); a1.add_argument("spec"); a1.add_argument("--log")
    a2 = sp.add_parser("track"); a2.add_argument("input"); a2.add_argument("frame", type=int); a2.add_argument("x", type=int)
    a2.add_argument("y", type=int); a2.add_argument("--maxd", type=int, default=25)
    a2.add_argument("--any-hue", action="store_true"); a2.add_argument("--roi", type=int, default=40)
    a = ap.parse_args()
    if a.cmd == "track":
        fr, _ = frames_of(a.input)
        print(json.dumps(track(fr, a.frame, (a.x, a.y), a.maxd, a.any_hue, a.roi)))
        return
    spec = json.load(open(a.spec))
    fr, fps = frames_of(os.path.join(ROOT, spec["clip"]))
    log = []
    out = apply(spec, fr, log)
    # match the source plate's encode: crf (and the engrave tool's -tune grain / +faststart for engraved takes)
    encode(out, fps, os.path.join(ROOT, spec["out"]), spec.get("crf", 16), spec.get("x264_extra", []))
    if a.log:
        json.dump(log, open(a.log, "w"))
    bad = [l for l in log if l[1] == "MISS"]
    print(f"wrote {spec['out']}: {len(fr)} frames, {sum(l[1] == 'reuse-prev' for l in log)} reused, "
          f"{len(bad)} missed {[l[0] for l in bad]}")


if __name__ == "__main__":
    main()
