#!/usr/bin/env python3
"""Jade-only matte from an engrave matte that also caught agents / props: follow her blob through the clip.
    $PY tools/sections/B/jmatte.py TAKE [--seed=x,y] [--xmin=N] [--xmax=N] [--reach=90] [--kill=x0,y0,x1,y1@t0]
Reads media/shots/B_<TAKE>/take_1_matte/matte.mp4, writes take_1_jmatte/matte.mp4 (same size, fps).
Frame 0: the blob at --seed (design px) or the largest one. Each later frame keeps the blobs that touch the previous
frame's kept mask grown by --reach px; --xmin / --xmax (design px) hard-clip the matte (agents at a frame edge)."""
import os
import subprocess
import sys

import av
import numpy as np
from scipy import ndimage as ndi

ROOT = "/home/jade/Documents/rewind-take-two"
FF = os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg")

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opts = {a[2:].partition("=")[0]: a[2:].partition("=")[2] for a in sys.argv[1:] if a.startswith("--")}
    d = os.path.join(ROOT, "media/shots", "B_" + args[0])
    src, out = os.path.join(d, "take_1_matte/matte.mp4"), os.path.join(d, "take_1_jmatte")
    os.makedirs(out, exist_ok=True)
    reach = int(opts.get("reach", 90))
    with av.open(src) as c:
        st = c.streams.video[0]
        fps, W, H = st.average_rate, st.width, st.height
        fr = [f.to_ndarray(format="gray") for f in c.decode(st)]
    sx = W / 1920
    x0 = int(float(opts.get("xmin", 0)) * sx)
    x1 = int(float(opts.get("xmax", 1920)) * sx)
    p = subprocess.Popen([FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                          "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", os.path.join(out, "matte.mp4")], stdin=subprocess.PIPE)
    prev, k = None, max(1, round(reach * sx / 8))
    kill = None
    if "kill" in opts:   # x0,y0,x1,y1@t0: zero this design-px rect from source time t0 on (a prop the matte caught)
        r, _, k0 = opts["kill"].partition("@")
        kill = ([int(float(v) * sx) for v in r.split(",")], float(k0 or 0))
    for i, a in enumerate(fr):
        a = a.copy()
        a[:, :x0] = 0
        a[:, x1:] = 0
        if kill and i / float(fps) >= kill[1] - 1e-6:
            (kx0, ky0, kx1, ky1), _ = kill
            a[ky0:ky1, kx0:kx1] = 0
        lab, n = ndi.label(a > 127)
        keep = np.zeros(a.shape, bool)
        if n:
            if prev is None:
                if "seed" in opts:
                    x, y = (float(v) for v in opts["seed"].split(","))
                    ids = {lab[int(y * H / 1080), int(x * sx)]} - {0}
                else:
                    sizes = ndi.sum(a > 127, lab, range(1, n + 1))
                    ids = {int(np.argmax(sizes)) + 1}
            else:   # blobs touching where she just was (grown at 1/8 scale: cheap)
                g = ndi.binary_dilation(prev[::8, ::8], iterations=k)
                ids = set(np.unique(lab[::8, ::8][g])) - {0}
            for j in ids:
                keep |= lab == j
        if keep.any():
            prev = keep
        out_f = np.where(keep, a, 0).astype(np.uint8)
        p.stdin.write(out_f.tobytes())
    p.stdin.close()
    p.wait()
    print(os.path.join(out, "matte.mp4"), len(fr), "frames")
