#!/usr/bin/env python3
"""Co-op level layers from the engraved takes (run after assets.py):
  <take>_bo.mp4        engraved take with the BLUE twin recoloured (ORANGE keeps the canon colours)
  <take>_L/, <take>_R/ per-girl mattes (PNG dirs, left / right twin on screen) for separate layers (the button sink
                       moves the girl standing on it)
  <take>_ag/           agents-only matte: the engrave matte (BiRefNet) holds the agents too; a matte component with no
                       saturated orange/blue in it is an agent, one with colour is a girl
Splits: a vertical seam between the girls per frame (the widest empty gap in the matte, else the thinnest column in
the middle of the blob). Which side is BLUE: "ob" (right is BLUE) or "bo" (left is BLUE) per frame range.
    tools/engrave/.venv/bin/python tools/v4B/coop/level.py
"""
import os
import subprocess
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recolor  # noqa: E402
from assets import PENCIL, BTN_L, BTN_R  # noqa: E402

D = "/home/jade/Documents/rewind-take-two/media/shots/C_coop"
FF = os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg")
JOBS = {
    # take: (engraved, matte dir, [(first, last, mode)])
    "c1t2": (f"{D}/c1/take_2_engraved.mp4", f"{D}/c1/take_2_matte", [(0, 200, "ob")]),
    "c2t1": (f"{D}/c2/take_1_engraved.mp4", f"{D}/c2/take_1_matte", [(0, 200, "ob")]),      # ORANGE stays the left girl
    "c1t1": (f"{D}/c1/take_1_engraved.mp4", f"{D}/c1/take_1_matte", [(0, 200, "ob")]),      # only its agents are used
}


def seam(m, prev):
    cols = m.sum(0)
    xs = np.flatnonzero(cols > 3)
    if len(xs) < 2:
        return prev
    g = np.diff(xs)
    k = int(np.argmax(g))
    if g[k] > 20:
        return 0.5 * (xs[k] + xs[k + 1])
    a, b = xs[0], xs[-1]
    lo, hi = int(a + 0.3 * (b - a)), int(a + 0.7 * (b - a))
    if hi <= lo:
        return prev
    return float(lo + np.argmin(cols[lo:hi]))


def enc(frames_dir, out):
    subprocess.run([FF, "-v", "error", "-y", "-framerate", "24", "-i", f"{frames_dir}/%05d.png", "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-crf", "14", out], check=True)


def main():
    plate = cv2.imread(f"{D}/plate.png")
    excl = np.zeros(plate.shape[:2], np.uint8)
    cv2.fillPoly(excl, [PENCIL], 1)
    for x0, y0, x1, y1 in (BTN_L, BTN_R):
        excl[y0 - 6:y1 + 6, x0 - 6:x1 + 6] = 1
    excl = cv2.dilate(excl, np.ones((9, 9), np.uint8)) > 0
    for name, (src, mdir, plan) in JOBS.items():
        cap = cv2.VideoCapture(src)
        out = {k: f"{D}/{name}_{k}" for k in ("L", "R", "ag")}
        for v in out.values():
            os.makedirs(v, exist_ok=True)
        w = None
        enc_p = None
        prev, i, log = 960.0, 0, []
        while True:
            ok, f = cap.read()
            if not ok:
                break
            if w is None:
                h, w = f.shape[:2]
                enc_p = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}", "-r", "24",
                                          "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-pix_fmt", "yuv420p",
                                          f"{D}/{name}_bo.mp4"], stdin=subprocess.PIPE)
            mp = os.path.join(mdir, f"{i:05d}.png")
            m0 = cv2.imread(mp, 0) > 127 if os.path.exists(mp) else np.zeros((h, w), bool)
            o, b_, _, _ = recolor.masks(cv2.cvtColor(f, cv2.COLOR_BGR2HSV).astype(np.float32))
            col = o | b_
            n, lab = cv2.connectedComponents(m0.astype(np.uint8))
            m = np.zeros_like(m0)
            agm = np.zeros_like(m0)
            for k in range(1, n):
                comp = lab == k
                if (comp & col).sum() > 400:
                    # an agent touching her joins her component: keep only what is near her colour
                    near = cv2.dilate(col.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (161, 161))) > 0
                    m |= comp & near
                    agm |= comp & ~near
                elif comp.sum() > 3000:
                    agm |= comp
            sx = seam(m, prev)
            prev = sx
            mode = next(md for a, b, md in plan if a <= i <= b)
            enc_p.stdin.write(recolor.recolor(f, sx, None, mode).tobytes())
            X = np.arange(w)[None, :]
            cv2.imwrite(f"{out['L']}/{i:05d}.png", ((m & (X < sx)) * 255).astype(np.uint8))
            cv2.imwrite(f"{out['R']}/{i:05d}.png", ((m & (X >= sx)) * 255).astype(np.uint8))
            # BiRefNet keeps the agents only on some frames: add the difference to the clean plate on the agents' side
            d = np.abs(cv2.GaussianBlur(f, (0, 0), 2).astype(np.int16) - cv2.GaussianBlur(plate, (0, 0), 2).astype(np.int16)).max(2) > 45
            jd = cv2.dilate(m.astype(np.uint8), np.ones((11, 11), np.uint8)) > 0
            ag = (d & ~jd & ~excl) | agm
            ag[770:] = False
            ag[:, 1150:] = False
            ag = cv2.morphologyEx(ag.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
            ag = cv2.morphologyEx(ag, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
            n2, lab2, st2, _ = cv2.connectedComponentsWithStats(ag)
            keep = np.zeros_like(ag)
            for k in range(1, n2):
                if st2[k, cv2.CC_STAT_AREA] > 4000:
                    keep[lab2 == k] = 1
            keep = cv2.morphologyEx(keep, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
            cv2.imwrite(f"{out['ag']}/{i:05d}.png", (keep * 255).astype(np.uint8))
            log.append((i, round(sx), mode))
            i += 1
        enc_p.stdin.close()
        enc_p.wait()
        for k, v in out.items():
            enc(v, f"{v}.mp4")
        print(name, i, "frames; seams", log[::12])


if __name__ == "__main__":
    main()
