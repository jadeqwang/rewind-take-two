"""F6b (v3): cut the generated agent sprite sheet (media/shots/F6b/kf_v3_F6b_agents.jpg: 4 front-walk frames, 3 back-walk
frames, all walking screen-right) into RGBA sprites with an engraver's paper halo, feet on the bottom edge.
    $PY tools/sectionF/agent_sprites.py   -> media/shots/F6b/agents/{front,back}_<k>.png + info.json
"""
import json
import os

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = "/home/jade/Documents/rewind-take-two"
D = os.path.join(ROOT, "media/shots/F6b")
OUT = os.path.join(D, "agents")
PAPER = (244, 236, 216)


def main():
    os.makedirs(OUT, exist_ok=True)
    a = np.asarray(Image.open(os.path.join(D, "kf_v3_F6b_agents.jpg")).convert("RGB")).astype(np.float32)
    white = a.min(2) > 225
    lab, _ = ndimage.label(white)
    border = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
    bg = np.isin(lab, list(border))
    fg = ndimage.binary_closing(~bg, iterations=2)
    fg = ndimage.binary_fill_holes(fg)
    lab2, n2 = ndimage.label(fg)
    sizes = ndimage.sum(fg, lab2, range(1, n2 + 1))
    keep = [i + 1 for i, v in enumerate(sizes) if v > 0.01 * fg.size]
    objs = ndimage.find_objects(lab2)
    runs = sorted((objs[i - 1][1].start, objs[i - 1][1].stop, i) for i in keep)
    names = [f"front_{k}" for k in range(4)] + [f"back_{k}" for k in range(len(runs) - 4)]
    info = {}
    for (x0, x1, li), n in zip(runs, names):
        m = lab2[:, x0:x1] == li
        ys = np.where(m.any(1))[0]
        y0, y1 = ys[0], ys[-1] + 1
        pad = 10
        X0, X1, Y0, Y1 = max(0, x0 - pad), min(fg.shape[1], x1 + pad), max(0, y0 - pad), y1
        mm = lab2[Y0:Y1, X0:X1] == li
        halo = ndimage.binary_dilation(mm, iterations=7)
        rgb = a[Y0:Y1, X0:X1].copy()
        rgb[~mm] = PAPER
        alpha = (halo * 255).astype(np.uint8)
        alpha = np.asarray(Image.fromarray(alpha).filter(__import__("PIL.ImageFilter", fromlist=["x"]).GaussianBlur(1.5)))
        im = Image.fromarray(np.dstack([rgb.clip(0, 255).astype(np.uint8), alpha]), "RGBA")
        # pre-shrink (the engine draws them ~100-200 px tall; a canvas downscale of a 1200 px halftone aliases)
        im = im.resize((round(im.width * 280 / im.height), 280), Image.LANCZOS)
        im.save(os.path.join(OUT, n + ".png"))
        info[n] = {"w": im.width, "h": im.height}
        print(n, im.size)
    json.dump(info, open(os.path.join(OUT, "info.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
