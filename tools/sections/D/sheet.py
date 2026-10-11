#!/usr/bin/env python
"""Dense contact sheet of a clip: sheet.py IN.mp4 OUT.jpg [--n=12] [--cols=4] [--t0=0] [--t1=end] [--w=480]"""
import sys

import av
from PIL import Image, ImageDraw


def sheet(src, out, n=12, cols=4, t0=0.0, t1=None, w=480):
    with av.open(src) as c:
        st = c.streams.video[0]
        fps = float(st.average_rate)
        frames = [f.to_image() for f in c.decode(st)]
    D = len(frames) / fps
    t1 = D if t1 is None else min(t1, D)
    ts = [t0 + (t1 - t0) * k / max(1, n - 1) for k in range(n)]
    tiles = []
    for t in ts:
        i = min(len(frames) - 1, int(round(t * fps)))
        im = frames[i].convert("RGB")
        im = im.resize((w, round(w * im.height / im.width)))
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, 110, 16), fill=(0, 0, 0))
        d.text((3, 2), f"{i / fps:.2f}s f{i}", fill=(255, 220, 0))
        tiles.append(im)
    h = tiles[0].height
    rows = (len(tiles) + cols - 1) // cols
    S = Image.new("RGB", (w * cols, h * rows + 18), (16, 16, 16))
    ImageDraw.Draw(S).text((4, 3), f"{src.split('media/')[-1]}  {len(frames)}f @ {fps:g}fps  {frames[0].width}x{frames[0].height}",
                           fill=(255, 255, 255))
    for k, t in enumerate(tiles):
        S.paste(t, ((k % cols) * w, 18 + (k // cols) * h))
    S.save(out, quality=85)
    return out


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    o = {x[2:].split("=")[0]: float(x.split("=")[1]) for x in sys.argv[1:] if x.startswith("--")}
    sheet(a[0], a[1], int(o.get("n", 12)), int(o.get("cols", 4)), o.get("t0", 0.0), o.get("t1"), int(o.get("w", 480)))
