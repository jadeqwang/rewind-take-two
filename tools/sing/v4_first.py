#!/usr/bin/env python3
"""Watercolor singing Jade (v4): first frames from Jade's picked portrait WITHOUT a repaint. Every pixel of her is
the pick's own (media/sing/v4/stills/pick_*.png); nothing is redrawn by a model.

Why not wc_paint.py as in v3: with the new portrait nano-banana-pro shrank her to 0.77x on both tries
(media/sing/first/v4_paint_wc_{1,2}.*, rejected), and B needs her at exactly the v3 scale, position and bottom cut
line. BiRefNet mattes her cleanly straight off the portrait's own paper (no blossom, no mountains), so the plate
goes behind her by plain compositing. The only thing the portrait lacks is the bit of sleeve past its left and right
edges; that comes from the v3 figure (media/sing/first/v3_wc_2_r.jpg + v3_her_alpha.png), which sits at the same
place and scale.

    MPY=~/Documents/orbital-sunrise-video/video/out/.venv/bin/python; EPY=tools/engrave/.venv/bin/python
    $MPY tools/sing/v4_first.py sheet PICK.png          -> media/sing/first/v4pick_sheet.jpg (pick on paper, sheet geometry)
    WC_VER=v4pick $EPY tools/sing/wc_comp.py matte media/sing/first/v4pick_sheet.jpg     -> v4pick_her_alpha.png
    $MPY tools/sing/v4_first.py comp                    -> media/sing/first/v4_fig.jpg, v4_her_alpha.png,
                                                           v4_S1_first.jpg, v4_V3S_first.jpg, v4_her_mask_first_frame.png
Geometry is v3's (media/sing/first/v3_base.json: x0, y0, portrait px -> sheet px scale), so she lands where v3 had her.
"""
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIRST = os.path.join(ROOT, "media/sing/first")
G = json.load(open(os.path.join(FIRST, "v3_base.json")))
W, H = 2752, 1536
EDGE = 28          # px of the portrait's left/right edge over which it hands over to the v3 sleeves
PLATES = {"S1": "media/sing/plates/plate_close_1.jpg", "V3S": "media/sing/plates/plate_truth_1.jpg"}


def place(pick):
    """The pick (portrait at K x) on a paper sheet in v3 geometry: (sheet float32, inside-the-portrait weight 0..1)."""
    a = Image.open(pick).convert("RGB")
    k = a.size[0] / 971
    s = G["scale"] / k
    w, h = round(a.size[0] * s), round(a.size[1] * s)
    t = np.asarray(a.resize((w, h), Image.LANCZOS), np.float32)
    sheet = np.ones((H, W, 3), np.float32) * np.array(G["paper"], np.float32)
    x0, y0 = G["x0"], G["y0"]
    n = min(H, y0 + h) - y0
    sheet[y0:y0 + n, x0:x0 + w] = t[:n]
    e = np.zeros((H, W), np.float32)
    ramp = np.clip(np.arange(w) / EDGE, 0, 1)
    e[y0:y0 + n, x0:x0 + w] = np.minimum(ramp, ramp[::-1])[None]
    e[:y0 + 1] = e[y0 + 1]                      # above the portrait's top row there is only sky: no hand-over needed there
    return sheet, e, {"pick": os.path.relpath(pick, ROOT), "pick_scale": k, "x0": x0, "y0": y0, "w": w, "scale": s}


def sheet(pick):
    s, _, meta = place(pick)
    out = os.path.join(FIRST, "v4pick_sheet.jpg")
    Image.fromarray(np.clip(s, 0, 255).astype(np.uint8)).save(out, quality=97)
    json.dump(meta, open(os.path.join(FIRST, "v4pick_sheet.json"), "w"), indent=1)
    print(os.path.relpath(out, ROOT), meta)


def comp():
    os.environ["WC_VER"] = "v4"
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import wc_comp as C
    meta = json.load(open(os.path.join(FIRST, "v4pick_sheet.json")))
    S4, e, _ = place(os.path.join(ROOT, meta["pick"]))
    a4 = np.asarray(Image.open(os.path.join(FIRST, "v4pick_her_alpha.png")), np.float32) / 255
    a4 = C.refine(S4, a4)                                    # hair over bare paper: a luminance key, as in v3
    S3 = C.rd(os.path.join(FIRST, "v3_wc_2_r.jpg"))
    a3 = np.asarray(Image.open(os.path.join(FIRST, "v3_her_alpha.png")), np.float32) / 255
    a3 = C.refine(S3, a3)
    F4, F3 = C.foreground(S4, a4), C.foreground(S3, a3)      # edge colours pulled from inside each silhouette
    fig = F4 * e[..., None] + F3 * (1 - e[..., None])
    a = a4 * e + a3 * (1 - e)
    Image.fromarray(np.clip(fig, 0, 255).astype(np.uint8)).save(os.path.join(FIRST, "v4_fig.jpg"), quality=97)
    Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).save(os.path.join(FIRST, "v4_her_alpha.png"))
    ac = np.clip((cv2.GaussianBlur(a, (0, 0), 1.0) - 0.08) / 0.84, 0, 1)     # the same light choke as wc_comp.comp
    x0, y0, x1, y1 = C.CROP
    for shot, plate in PLATES.items():
        P = C.rd(os.path.join(ROOT, plate))
        if P.shape != fig.shape:
            P = np.asarray(Image.fromarray(P.astype(np.uint8)).resize((W, H), Image.LANCZOS), np.float32)
        out = os.path.join(FIRST, f"v4_{shot}_first.jpg")
        Image.fromarray(np.clip(fig * ac[..., None] + P * (1 - ac[..., None]), 0, 255).astype(np.uint8)[y0:y1, x0:x1]).save(out, quality=96)
        print(os.path.relpath(out, ROOT))
    Image.fromarray((ac[y0:y1, x0:x1] * 255).astype(np.uint8)).save(os.path.join(FIRST, "v4_her_mask_first_frame.png"))
    # how far her outline at the bottom edge and her matte differ from v3's (B needs the same cut line and scale)
    m3 = np.asarray(Image.open(os.path.join(FIRST, "v3_her_mask_first_frame.png")), np.float32) / 255
    m4 = ac[y0:y1, x0:x1]
    row = lambda m: np.flatnonzero(m[-3] > 0.5)[[0, -1]].tolist()
    print("bottom row figure span (crop px): v3", row(m3), "v4", row(m4), "| matte area v4/v3", round(float(m4.sum() / m3.sum()), 3))


if __name__ == "__main__":
    {"sheet": lambda: sheet(os.path.abspath(sys.argv[2])), "comp": comp}[sys.argv[1]]()
