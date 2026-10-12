"""v5 round 2 (Jade: "copy the one from later in the same video ... inside the clock at 3:13"): lift the F6b clock
Penrose stair off its plate. The mask is the engine's exact block geometry (tools/sectionF/penrose_guide.py, the
geometry the redraw was traced from), rasterised at plate scale; nothing is redrawn.

    $PY tools/v5/stairs2/lift.py check     -> scratch overlay of the exact outlines on the redraw
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/sectionF"))
import penrose_guide as pg  # noqa: E402

PLATE = os.path.join(ROOT, "media/shots/F6b/kf_v3_F6b_redraw_crop_dered.png")


def faces():
    """[(pts, kind)] for every visible block face, in the guide's draw order (plate px, 2400x1350)."""
    steps, N, h = pg.build(pg.PAR["n"], pg.PAR["w"])
    k = 2400 / 1920
    P, S = pg.projector(steps, pg.PAR, k)
    wall = pg.PAR["wall"]
    far = [s for s in steps if s["flight"][0] in "CTD"]
    near = [s for s in steps if s["flight"][0] not in "CTD"]
    out = []
    for grp in (far, near):
        for s in sorted(grp, key=lambda s: s["x0"] + s["x1"] + s["z0"] + s["z1"]):
            yb = s["y"] - wall
            if s["flight"] != "D":
                out.append(([P(s["x1"], s["y"], s["z0"]), P(s["x1"], s["y"], s["z1"]), P(s["x1"], yb, s["z1"]), P(s["x1"], yb, s["z0"])], "R"))
            if s["flight"] not in ("A", "R"):
                out.append(([P(s["x0"], s["y"], s["z1"]), P(s["x1"], s["y"], s["z1"]), P(s["x1"], yb, s["z1"]), P(s["x0"], yb, s["z1"])], "L"))
            out.append(([P(s["x0"], s["y"], s["z0"]), P(s["x1"], s["y"], s["z0"]), P(s["x1"], s["y"], s["z1"]), P(s["x0"], s["y"], s["z1"])], "T"))
    return out


def block_mask(size=(2400, 1350), grow=0):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    for pts, _ in faces():
        d.polygon(pts, fill=255)
        d.line(pts + [pts[0]], fill=255, width=3)
    if grow:
        m = m.filter(ImageFilter.MaxFilter(2 * grow + 1))
    return m


if __name__ == "__main__":
    out = sys.argv[2] if len(sys.argv) > 2 else "/tmp/lift_check.png"
    im = Image.open(PLATE).convert("RGB")
    d = ImageDraw.Draw(im)
    for pts, kd in faces():
        d.line(pts + [pts[0]], fill=(255, 0, 255), width=1)
    bb = block_mask().getbbox()
    print("bbox", bb)
    im.crop((bb[0] - 40, bb[1] - 40, bb[2] + 40, bb[3] + 80)).save(out)
