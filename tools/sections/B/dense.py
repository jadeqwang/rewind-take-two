#!/usr/bin/env python3
"""Dense review sheet of takes: one row of N frames per take, time-stamped.
    $PY tools/sections/B/dense.py OUT.jpg TAKE[:N][@a-b] [...] [--n=10] [--w=320]
TAKE is a rev-B take name (media/gen/B_<take>/take_N.mp4) or a path to any mp4; @a-b limits the time range (s)."""
import os
import sys

import av
from PIL import Image, ImageDraw

ROOT = "/home/jade/Documents/rewind-take-two"


def frames(path, n, a=None, b=None):
    with av.open(path) as c:
        st = c.streams.video[0]
        fr = [f.to_image() for f in c.decode(st)]
        fps = float(st.average_rate)
    i0 = 0 if a is None else max(0, round(a * fps))
    i1 = len(fr) - 1 if b is None else min(len(fr) - 1, round(b * fps))
    idx = [round(i0 + k * (i1 - i0) / (n - 1)) for k in range(n)]
    return [(i / fps, fr[i]) for i in idx]


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opts = {a[2:].partition("=")[0]: a[2:].partition("=")[2] for a in sys.argv[1:] if a.startswith("--")}
    n, w = int(opts.get("n", 10)), int(opts.get("w", 320))
    rows = []
    for spec in args[1:]:
        name, _, rng = spec.partition("@")
        a, b = (float(x) for x in rng.split("-")) if rng else (None, None)
        take, _, k = name.partition(":")
        path = take if take.endswith(".mp4") else os.path.join(ROOT, "media/gen", "B_" + take, f"take_{k or 1}.mp4")
        tiles = []
        for t, im in frames(path, n, a, b):
            im = im.convert("RGB").resize((w, round(w * im.height / im.width)))
            d = ImageDraw.Draw(im)
            d.rectangle((0, 0, 52, 13), fill=(0, 0, 0))
            d.text((3, 1), f"{t:.2f}", fill=(255, 255, 0))
            tiles.append(im)
        rows.append((spec, tiles))
    h = rows[0][1][0].height
    S = Image.new("RGB", (w * n, (h + 16) * len(rows)), (20, 20, 20))
    d = ImageDraw.Draw(S)
    for r, (spec, tiles) in enumerate(rows):
        d.text((4, r * (h + 16) + 2), spec, fill=(255, 200, 80))
        for k, t in enumerate(tiles):
            S.paste(t, (k * w, r * (h + 16) + 16))
    out = args[0] if args[0].startswith("/") else os.path.join(ROOT, args[0])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    S.save(out, quality=84)
    print(out, S.size)
