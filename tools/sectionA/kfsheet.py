#!/usr/bin/env python3
"""Contact sheet of every keyframe of the given shots: kfsheet.py OUT.jpg SHOT [SHOT ...] [--cols=3]"""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import SHOTS, sheet  # noqa: E402

out = sys.argv[1]
cols = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--cols=")), 3))
tiles = []
for s in [a for a in sys.argv[2:] if not a.startswith("--")]:
    for p in sorted(glob.glob(os.path.join(SHOTS, s, "kf_*"))):
        if "_raw" in p or "_pretrim" in p:
            continue
        tiles.append((p, f"{s}/{os.path.basename(p)}"))
sheet(tiles, out, title=" ".join(sys.argv[2:]), cols=cols, width=2400)
print(out, len(tiles))
