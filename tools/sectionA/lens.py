#!/usr/bin/env python3
"""S2: the Bean-reflection lens. Bends a plate clip through a spherical-mirror (barrel) distortion that relaxes to a
flat image, with a soft dark circular rim that opens out, so the push from S1's reflection lands on the road.

    tools/engrave/.venv/bin/python tools/sectionA/lens.py IN.mp4 OUT.mp4 [--dur 1.74] [--k0 0.9] [--relax 0.75]

k(t) = k0 * (1 - smoothstep(0, relax*dur, t)); zoom compensates so the centre stays put. Output 1920x1080, 24 fps.
"""
import argparse
import subprocess

import cv2
import numpy as np

FF = "/home/jade/Documents/moongazing/.venv/bin/ffmpeg"


def smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp")
    ap.add_argument("out")
    ap.add_argument("--dur", type=float, default=2.2)
    ap.add_argument("--k0", type=float, default=0.9)
    ap.add_argument("--relax", type=float, default=0.75)
    ap.add_argument("--in", dest="clip_in", type=float, default=0.0)
    a = ap.parse_args()
    cap = cv2.VideoCapture(a.inp)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    W, H = 1920, 1080
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx, ny = (xx - W / 2) / (W / 2), (yy - H / 2) / (W / 2)
    r2 = nx * nx + ny * ny
    p = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", "24",
                          "-i", "-", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", a.out], stdin=subprocess.PIPE)
    i = 0
    written = 0
    n_out = int(round(a.dur * 24))
    while written < n_out:
        ok, f = cap.read()
        if not ok:
            break
        t = i / fps
        if t < a.clip_in:
            i += 1
            continue
        lt = t - a.clip_in
        f = cv2.resize(f, (W, H), interpolation=cv2.INTER_LANCZOS4)
        k = a.k0 * (1 - smooth(lt / (a.relax * a.dur)))
        # inverse barrel: sample source at r * (1 + k r^2) / (1 + k * rmax^2-ish) so edges compress like a convex mirror
        s = (1 + k * r2) / (1 + k * 1.33)  # corners sample at most the frame edge (no mirrored seams)
        mx = (nx * s) * (W / 2) + W / 2
        my = (ny * s) * (W / 2) + H / 2
        g = cv2.remap(f, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        # circular mirror rim that opens out as the lens relaxes
        rim = 1 - smooth((np.sqrt(r2) - (0.55 + 1.2 * (1 - k / max(a.k0, 1e-6)))) / 0.25)
        g = (g.astype(np.float32) * (0.15 + 0.85 * rim[..., None])).astype(np.uint8)
        p.stdin.write(g.tobytes())
        i += 1
        written += 1
    p.stdin.close()
    p.wait()
    print(a.out, written)


if __name__ == "__main__":
    main()
