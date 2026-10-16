#!/usr/bin/env python3
"""v9 fix 1a + 9: preview a shot from its plate without render.mjs. Emulates the engine for one video layer:
cover fit to 1920x1080, clip time = in + rate * shot-local time, kenBurns (screen = 960 + x + s * (p - 960), same in y
about 540; default ease inOutSine) and the 2.39 letterbox. Writes a contact sheet of reduced-size frames.

    PY=~/Documents/1-music-shipped/moongazing/.venv/bin/python
    $PY tools/v9/car_preview.py CLIP OUT.jpg --start 38.9 --end 39.68 --in 0.3 [--rate 1] \
        [--kb '{"from":{"scale":1,"y":60},"to":{"scale":1.1,"y":100},"ease":"inOutSine"}'] [--n 6] [--w 480]
"""
import argparse
import json
import math

import av
import numpy as np
from PIL import Image

EASE = {"inOutSine": lambda u: 0.5 - 0.5 * math.cos(math.pi * u), "linear": lambda u: u, "in": lambda u: u * u,
        "out": lambda u: 1 - (1 - u) ** 2}

ap = argparse.ArgumentParser()
ap.add_argument("clip"); ap.add_argument("out")
ap.add_argument("--start", type=float, required=True); ap.add_argument("--end", type=float, required=True)
ap.add_argument("--in", dest="inp", type=float, default=0.0); ap.add_argument("--rate", type=float, default=1.0)
ap.add_argument("--kb", default=None); ap.add_argument("--n", type=int, default=6); ap.add_argument("--w", type=int, default=480)
ap.add_argument("--cols", type=int, default=3)
a = ap.parse_args()

frames = [f.to_ndarray(format="rgb24") for f in av.open(a.clip).decode(video=0)]
fps = 24.0
kb = json.loads(a.kb) if a.kb else None
dur = a.end - a.start
tiles = []
for i in range(a.n):
    lt = dur * i / max(1, a.n - 1) if a.n > 1 else 0
    lt = min(lt, dur - 1 / fps)
    k = min(len(frames) - 1, int(round((a.inp + a.rate * lt) * fps)))
    im = Image.fromarray(frames[k])
    w, h = im.size
    c = max(1920 / w, 1080 / h)
    im = im.resize((round(w * c), round(h * c)), Image.LANCZOS)
    s, x, y = 1.0, 0.0, 0.0
    if kb:
        u = EASE[kb.get("ease", "inOutSine")](lt / dur)
        get = lambda key, d: (kb.get("from", {}).get(key, kb.get("to", {}).get(key, d)), kb.get("to", {}).get(key, kb.get("from", {}).get(key, d)))
        s0, s1 = get("scale", 1.0); x0, x1 = get("x", 0.0); y0, y1 = get("y", 0.0)
        s, x, y = s0 + (s1 - s0) * u, x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
    W2, H2 = im.size
    canvas = Image.new("RGB", (1920, 1080), (11, 11, 12))
    big = im.resize((round(W2 * s), round(H2 * s)), Image.LANCZOS)
    # image centre (W2/2, H2/2) sits at screen (960, 540) before the transform
    cx = 960 + x + s * (W2 / 2 - W2 / 2) - big.size[0] / 2
    cy = 540 + y - big.size[1] / 2
    canvas.paste(big, (round(cx), round(cy)))
    bar = round((1080 - 1920 / 2.39) / 2)
    arr = np.asarray(canvas).copy(); arr[:bar] = (11, 11, 12); arr[1080 - bar:] = (11, 11, 12)
    t = Image.fromarray(arr).resize((a.w, round(a.w * 9 / 16)), Image.LANCZOS)
    tiles.append(t)
cols = min(a.cols, len(tiles)); rows = math.ceil(len(tiles) / cols)
tw, th = tiles[0].size
sheet = Image.new("RGB", (cols * tw + (cols + 1) * 4, rows * th + (rows + 1) * 4), (40, 40, 40))
for i, t in enumerate(tiles):
    sheet.paste(t, (4 + (i % cols) * (tw + 4), 4 + (i // cols) * (th + 4)))
sheet.save(a.out, quality=85)
print(a.out, len(frames), "frames")
