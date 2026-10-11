#!/usr/bin/env python3
"""Review sheet of 540p stills: for each still, the full frame and a crop at Nx (nearest: what the pixels really are).
    sheet.py OUT.jpg --crop x0,y0,x1,y1 [--zoom 3] [--full] STILL.png [STILL.png ...]"""
import argparse
import numpy as np
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("out"); ap.add_argument("stills", nargs="+")
ap.add_argument("--crop", default="560,150,860,320"); ap.add_argument("--zoom", type=int, default=3)
ap.add_argument("--full", action="store_true"); ap.add_argument("--cols", type=int, default=2)
a = ap.parse_args()
box = [int(v) for v in a.crop.split(",")]
tiles = []
for s in a.stills:
    im = Image.open(s).convert("RGB")
    c = im.crop(box)
    c = c.resize((c.width * a.zoom, c.height * a.zoom), Image.NEAREST)
    if a.full:
        f = im.resize((round(im.width * c.height / im.height), c.height), Image.LANCZOS) if im.height != c.height else im
        c = Image.fromarray(np.hstack([np.asarray(f), np.asarray(c)]))
    tiles.append(np.asarray(c))
while len(tiles) % a.cols:
    tiles.append(np.zeros_like(tiles[0]))
Image.fromarray(np.vstack([np.hstack(tiles[i:i + a.cols]) for i in range(0, len(tiles), a.cols)])).save(a.out, quality=92)
print(a.out)
