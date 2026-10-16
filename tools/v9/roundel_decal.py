#!/usr/bin/env python3
"""v9 fix 8 round 2: replace a wrong sleeve badge with the canon roundel (white disc, black ring, "1420 / MHz").

    tools/engrave/.venv/bin/python tools/v9/roundel_decal.py IN.mp4 OUT.mp4 --spec SPEC.json [--debug sheet.jpg]

For takes where the model drew something that is not a ring with a white interior (V2d2: a red rounded-square badge
with a grey plate), so `tools/sectionE/patchfix.py` has nothing to re-letter. Per frame:
  1. erase: the badge's red pixels (HSV) near the badge, their convex hull (= the grey plate and glyphs inside), grown
     a few px for the dark outline, are inpainted from the surrounding sleeve; pixels on the occluder side of the
     occluder line are never touched;
  2. paint: a canon roundel (ring + white + the patchfix artwork) is drawn antialiased (4x) as an ellipse at the
     spec's centre/radii/angle, again only on the visible side of the occluder line.
Spec (JSON): {"frames": [f0, f1], "keys": {"F": [cx, cy], ...} (centre, interpolated; one key = static),
  "r": outer radius px, "aspect": minor/major, "tilt": ellipse major-axis angle deg, "rot": lettering baseline deg,
  "ring": ring width as a fraction of r, "scale": lettering scale (patchfix art), "box": [x0, y0, x1, y1] erase search box,
  "occ": [[x0, y0], [x1, y1]] occluder line (pixels to its right, seen from the first point to the second, are kept),
  "ink": [r, g, b], "paper": [r, g, b] or null (null = median of the sleeve around the badge)}.
"""
import argparse
import json
import os
import subprocess
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sectionE"))
import patchfix  # noqa: E402

FFMPEG = os.environ.get("FFMPEG", patchfix.FFMPEG)


def side(shape, occ):
    """True where a pixel is on the visible (left) side of the occluder line."""
    H, W = shape
    (x0, y0), (x1, y1) = occ
    yy, xx = np.mgrid[0:H, 0:W]
    return ((x1 - x0) * (yy - y0) - (y1 - y0) * (xx - x0)) > 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--spec", required=True)
    ap.add_argument("--debug", default=None)
    ap.add_argument("--crf", type=int, default=12)
    a = ap.parse_args()
    sp = json.load(open(a.spec))
    fr, fps = patchfix.read(a.src)
    H, W = fr[0].shape[:2]
    f0, f1 = sp["frames"]
    kk = sorted(int(k) for k in sp["keys"])
    kx = [sp["keys"][str(k)][0] for k in kk]
    ky = [sp["keys"][str(k)][1] for k in kk]
    vis = side((H, W), sp["occ"]) if sp.get("occ") else np.ones((H, W), bool)
    art = patchfix.art(sp.get("scale", 0.8), sp.get("weight", 900))
    ART = art.shape[0]
    SS = 4
    x0, y0, x1, y1 = sp["box"]
    ink = np.array(sp.get("ink", [22, 20, 20])[::-1], np.float32)
    dbg = []
    out = [f.copy() for f in fr]
    for i in range(f0, min(f1, len(fr) - 1) + 1):
        img = fr[i].copy()
        cx, cy = float(np.interp(i, kk, kx)), float(np.interp(i, kk, ky))
        # ---- 1. erase the badge
        hsv = cv2.cvtColor(img[y0:y1, x0:x1], cv2.COLOR_BGR2HSV)
        h, s, v = hsv[..., 0].astype(int), hsv[..., 1].astype(int), hsv[..., 2].astype(int)
        red = ((h < 12) | (h > 165)) & (s > 70) & (v > 60)
        red &= vis[y0:y1, x0:x1]
        m = np.zeros((H, W), np.uint8)
        if red.sum() > 20:
            n, lab, st, _ = cv2.connectedComponentsWithStats(red.astype(np.uint8))
            big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
            pts = np.argwhere(lab == big)[:, ::-1] + [x0, y0]
            cv2.fillConvexPoly(m, cv2.convexHull(pts.astype(np.int32)), 255)
            m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * sp.get("grow", 3) + 1,) * 2))
        # up to the occluder's own dark edge: erase on the visible side of a line shifted `reach` px into the occluder,
        # but never the occluder's dark pixels there
        vis2 = side((H, W), [[x + sp.get("reach", 3), y] for x, y in sp["occ"]]) if sp.get("occ") else vis
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        m[~vis2 | (~vis & (g < 90))] = 0
        if m.any():
            # flat sleeve colour (the badge sat on plain sleeve): median of the bright, non-red pixels around it
            ring = cv2.dilate(m, np.ones((9, 9), np.uint8)) & ~m
            around = img[(ring > 0) & vis & (g > 170)]
            sleeve = np.median(around, 0) if len(around) > 10 else np.array([225, 228, 236])
            mf = cv2.GaussianBlur((m > 0).astype(np.float32), (0, 0), 0.7)[..., None]
            img = np.clip(img * (1 - mf) + sleeve * mf, 0, 255).astype(np.uint8)
        # ---- 2. paint the roundel (ellipse: major r along tilt, minor r*aspect)
        r = sp["r"]
        th = np.deg2rad(sp.get("tilt", 0.0))
        R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
        L = R @ np.diag([r, r * sp.get("aspect", 1.0)])          # unit disc -> ellipse
        pad = int(r + 4)
        bx0, by0 = int(cx) - pad, int(cy) - pad
        bw = 2 * pad + 1
        yy, xx = np.mgrid[0:bw * SS, 0:bw * SS]
        P = np.stack([(xx + 0.5) / SS + bx0 - cx, (yy + 0.5) / SS + by0 - cy], -1)
        U = P @ np.linalg.inv(L).T                               # frame -> unit disc
        rho = np.hypot(U[..., 0], U[..., 1])
        rw = sp.get("ring", 0.16)
        disc = (rho < 1.0).astype(np.float32)
        white = (rho < 1.0 - rw).astype(np.float32)
        # lettering: unit disc of the inner edge, rotated so the baseline runs at `rot`
        t = np.deg2rad(sp.get("rot", 0.0) - sp.get("tilt", 0.0))
        Ui = U / (1.0 - rw)
        ur = np.stack([Ui[..., 0] * np.cos(t) + Ui[..., 1] * np.sin(t), -Ui[..., 0] * np.sin(t) + Ui[..., 1] * np.cos(t)], -1)
        mx = ((ur[..., 0] + 1) * ART / 2).astype(np.float32)
        my = ((ur[..., 1] + 1) * ART / 2).astype(np.float32)
        let = cv2.remap(art, mx, my, cv2.INTER_LINEAR, borderValue=0) * white
        cov = cv2.resize(disc, (bw, bw), interpolation=cv2.INTER_AREA)[..., None]
        wht = cv2.resize(white, (bw, bw), interpolation=cv2.INTER_AREA)[..., None]
        ltr = cv2.resize(let, (bw, bw), interpolation=cv2.INTER_AREA)[..., None]
        crop = img[by0:by0 + bw, bx0:bx0 + bw].astype(np.float32)
        if sp.get("paper"):
            paper = np.array(sp["paper"][::-1], np.float32)
        else:
            ring_px = fr[i][by0:by0 + bw, bx0:bx0 + bw][(cov[..., 0] == 0) & vis[by0:by0 + bw, bx0:bx0 + bw]]
            bright = ring_px[ring_px.mean(1) > 180]
            paper = np.median(bright, 0).astype(np.float32) if len(bright) > 10 else np.array([232, 232, 236], np.float32)
        face = paper * (1 - ltr) + ink * ltr                     # white face with lettering
        col = ink * (1 - wht) + face * wht                       # ring outside the face
        al = cov * vis[by0:by0 + bw, bx0:bx0 + bw, None]
        img[by0:by0 + bw, bx0:bx0 + bw] = np.clip(crop * (1 - al) + col * al, 0, 255).astype(np.uint8)
        out[i] = img
        if a.debug and len(dbg) < 16:
            z = 200
            c0 = cv2.resize(fr[i][by0 - 10:by0 + bw + 10, bx0 - 10:bx0 + bw + 10], (z, z), interpolation=cv2.INTER_CUBIC)
            c1 = cv2.resize(img[by0 - 10:by0 + bw + 10, bx0 - 10:bx0 + bw + 10], (z, z), interpolation=cv2.INTER_CUBIC)
            cv2.putText(c0, str(i), (4, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            dbg.append(np.vstack([c0, c1]))
    if a.debug and dbg:
        while len(dbg) % 8:
            dbg.append(np.zeros_like(dbg[0]))
        cv2.imwrite(a.debug, np.vstack([np.hstack(dbg[r:r + 8]) for r in range(0, len(dbg), 8)]))
    if a.out.lower().endswith((".png", ".jpg")):
        cv2.imwrite(a.out, out[f0])
        return
    p = subprocess.Popen([FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", f"{fps}",
                          "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", str(a.crf), "-pix_fmt", "yuv420p",
                          "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", a.out], stdin=subprocess.PIPE)
    for f in out:
        p.stdin.write(f.tobytes())
    p.stdin.close()
    p.wait()
    print("wrote", a.out)


if __name__ == "__main__":
    main()
