#!/usr/bin/env python3
"""v6 (Jade 2:24, "blue dot missing from front of jacket for just a little bit"): paint the pale-blue chest dot onto
Jade's left chest (viewer's right jacket panel) in every frame of G2 take 5 (built on the sleeve-roundel `_patch` file).

    tools/engrave/.venv/bin/python tools/sectionE/g2_dot.py [IN] [OUT] [--debug geom.json]

Placement is measured, not guessed. In G1 take_3 and G3 take_5 (the shots either side) the dot is laid out the same
way relative to the orange chest band on that panel, in every sampled frame:
  * diameter D = 1.00 x the band's thickness (0.97-1.02 measured)
  * centre = band's inner end (where it meets the zip edge, on the band's top line) + 1.40 D along the band
    (1.27-1.47) + 0.77 D up, perpendicular to the band (0.75-0.81); so the dot sits just above the band.
Per G2 frame the band is found (orange, the component nearest the previous frame's), its top line, inner end and
thickness are fitted, smoothed over time (Savitzky-Golay, 9 frames), and the dot is drawn there.
Look: flat pale blue (G1's (125, 166, 220) easing to G3's (104, 147, 205) across the frames on screen, so both cuts match) with the
same thin, slightly darker blue rim as the G1/G3 dots (no black ink line on those), 4x antialiased edge, faint grain.
Occluders are kept: the dot is only laid on jacket pixels (light, unsaturated, or the grey fold shading); anything dark
(hair, headphone, top, ink) or saturated (skin, orange) in front stays in front.
"""
import argparse
import json
import os
import subprocess

import av
import cv2
import numpy as np
from scipy.signal import savgol_filter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FFMPEG = os.environ.get("FFMPEG", os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg"))
IN = "media/shots/G2/take_5_engraved_patch.mp4"
OUT = "media/shots/G2/take_5_engraved_patch_dot.mp4"
SEED = (1169, 479)          # band centroid at frame 0 (design px)
D_T, ALONG, UP = 1.00, 1.40, 0.77
C0, C1 = np.array([125, 166, 220.]), np.array([104, 147, 205.])   # G1 dot, G3 dot (median RGB)
RIM = 0.80                  # rim colour = fill x RIM
SS = 4                      # supersampling for the edge
ON = (16, 65)               # frames on screen: E.js G2 in 0.68 s, rate 1.15, 144.54-146.32 -> clip 0.68-2.73 s


def band(a, near, maxd=80):
    h = cv2.cvtColor(a, cv2.COLOR_RGB2HSV)
    m = ((h[..., 0] >= 5) & (h[..., 0] <= 20) & (h[..., 1] > 120) & (h[..., 2] > 170)).astype(np.uint8)
    n, lab, st, c = cv2.connectedComponentsWithStats(m)
    best = None
    for k in range(1, n):
        if st[k, 4] < 1200:
            continue
        d = np.hypot(c[k][0] - near[0], c[k][1] - near[1])
        if d < maxd and (best is None or d < best[0]):
            best = (d, k)
    if best is None:
        return None
    k = best[1]
    comp = lab == k
    X, w = st[k, 0], st[k, 2]
    tops, bots = [], []
    for x in range(X + int(0.08 * w), X + int(0.55 * w)):
        ys = np.nonzero(comp[:, x])[0]
        if len(ys):
            tops.append((x, ys.min())); bots.append((x, ys.max()))
    tops, bots = np.array(tops, float), np.array(bots, float)
    p = np.polyfit(tops[:, 0], tops[:, 1], 1)
    ang = np.arctan(p[0])
    thick = float(np.median(bots[:, 1] - tops[:, 1]) * np.cos(ang))
    ymid = int(np.polyval(p, X + 0.1 * w) + thick / 2)
    left = float(np.nonzero(comp[ymid - 3:ymid + 4].any(0))[0].min())
    return dict(c=(float(c[k][0]), float(c[k][1])), left=left, ay=float(np.polyval(p, left)), slope=float(p[0]), thick=thick)


def geometry(frames):
    near, g = SEED, []
    for a in frames:
        b = band(a, near)
        if b is None:
            g.append(None)
            continue
        near = b["c"]
        g.append(b)
    idx = [i for i, b in enumerate(g) if b]
    keys = ("left", "ay", "slope", "thick")
    tr = {k: np.interp(range(len(g)), idx, [g[i][k] for i in idx]) for k in keys}
    sm = {k: savgol_filter(v, 9, 2, mode="interp") for k, v in tr.items()}
    out = []
    for i in range(len(g)):
        ang = np.arctan(sm["slope"][i])
        u, nrm = np.array([np.cos(ang), np.sin(ang)]), np.array([np.sin(ang), -np.cos(ang)])
        D = D_T * sm["thick"][i]
        cx, cy = np.array([sm["left"][i], sm["ay"][i]]) + ALONG * D * u + UP * D * nrm
        out.append(dict(i=i, cx=float(cx), cy=float(cy), D=float(D), measured=g[i] is not None))
    return out


def paint(a, cx, cy, D, col, rng):
    R = D / 2
    pad = int(R + 4)
    x0, y0 = int(cx) - pad, int(cy) - pad
    roi = a[y0:y0 + 2 * pad, x0:x0 + 2 * pad].astype(np.float32)
    hh, ww = roi.shape[:2]
    ys, xs = np.mgrid[0:hh * SS, 0:ww * SS]
    d = np.hypot((xs + 0.5) / SS - 0.5 + x0 - cx, (ys + 0.5) / SS - 0.5 + y0 - cy)
    cover = (d <= R).reshape(hh, SS, ww, SS).mean((1, 3))
    rimw = max(1.2, D / 40)                                   # ~1.7 px at D=67, as measured on G1
    rim = ((d <= R) & (d > R - rimw)).reshape(hh, SS, ww, SS).mean((1, 3))
    hsv = cv2.cvtColor(roi.astype(np.uint8), cv2.COLOR_RGB2HSV)
    S, V = hsv[..., 1].astype(np.float32), hsv[..., 2].astype(np.float32)
    jacket = ((V > 95) & (S < 75)).astype(np.float32)        # white jacket and its grey folds
    jacket = cv2.morphologyEx(jacket, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    jacket = cv2.GaussianBlur(jacket, (0, 0), 0.6)
    fill = np.broadcast_to(col, roi.shape).astype(np.float32).copy()
    fill += rng.normal(0, 1.5, roi.shape[:2])[..., None]    # paper grain like the G1/G3 dots (std ~2)
    rimc = col * RIM
    frac = np.where(cover > 0, rim / np.maximum(cover, 1e-6), 0)[..., None]
    paintc = fill * (1 - frac) + rimc * frac
    al = (cover * jacket)[..., None]
    a[y0:y0 + hh, x0:x0 + ww] = np.clip(roi * (1 - al) + paintc * al + 0.5, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp", nargs="?", default=IN)
    ap.add_argument("out", nargs="?", default=OUT)
    ap.add_argument("--debug")
    a = ap.parse_args()
    c = av.open(os.path.join(ROOT, a.inp))
    vs = c.streams.video[0]
    fps, W, H = vs.average_rate, vs.width, vs.height
    frames = [f.to_ndarray(format="rgb24") for f in c.decode(vs)]
    geo = geometry(frames)
    if a.debug:
        json.dump(geo, open(a.debug, "w"))
    rng = np.random.default_rng(7)
    n = len(frames)
    p = subprocess.Popen([FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", f"{fps}",
                          "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-pix_fmt", "yuv420p",
                          "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                          os.path.join(ROOT, a.out)], stdin=subprocess.PIPE)
    for i, f in enumerate(frames):
        g = geo[i]
        col = C0 + (C1 - C0) * float(np.clip((i - ON[0]) / (ON[1] - ON[0]), 0, 1))
        paint(f, g["cx"], g["cy"], g["D"], col, rng)
        p.stdin.write(np.ascontiguousarray(f).tobytes())
    p.stdin.close()
    assert p.wait() == 0
    print("wrote", a.out, n, "frames;", sum(not g["measured"] for g in geo), "frames with the band interpolated")


if __name__ == "__main__":
    main()
