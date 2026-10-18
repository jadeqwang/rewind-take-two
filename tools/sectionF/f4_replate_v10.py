#!/usr/bin/env python
"""v10b F4: re-plate the clean-up under the new (smaller) Bean reflection.

v9's Bria plates (media/shots/F4/v9_plates*/) were hidden under v9's big reflection. Under the v10b reflection, two of
their faults show: a gap in the reflected horizon tree line with lone Bria trees in it (src ~12-36), and a pale streak
down the pink and blue bands (src ~18-60, where the video model drew a glow round its own reflection's head, outside v9's
mask). This re-runs Bria fibo-edit-1.5 ($0.03 a call) on the v9 clean composite of each keyframe, with v9's mask grown
to take in the glow and kept below her head, asking for the tree band and the hatched bands to run straight across.

    tools/engrave/.venv/bin/python tools/sectionF/f4_replate_v10.py [--keys 12,16,...,60] [--seed 7] [--dry-run]
Writes media/shots/F4/v10b_plates/kNNN_{in,mask,out}.png, boxes.json, and chosen.json (v9's list with these keys
replaced); f4_reflection_v10.py reads that chosen.json (--plates).
"""
import argparse
import json
import os
import shutil
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f4_reflection as R  # noqa: E402

ROOT = R.ROOT
import subprocess
GENPY = os.path.expanduser("~/Documents/1-music-shipped/moongazing/.venv/bin/python")   # tools/gen needs its venv

V9 = os.path.join(ROOT, "media/shots/F4/v9_plates2")
OUT = os.path.join(ROOT, "media/shots/F4/v10b_plates")
SRC = os.path.join(ROOT, "media/shots/F4/take_2_engraved_dered_patch.mp4")
INSTR = ("Continue the picture across the masked area from its left and right edges, so that the masked area looks "
         "exactly like the strips just left and right of it: the same thin dark-green tree line at the same height, the "
         "same tiles and grid lines, the same pink and blue hatched bands. Nothing new: no tree, no bush, no glow, no "
         "person, no object.")

INSTR_TILES = ("Continue the picture across the masked area from its left and right edges: the same thin black grid lines "
               "of the plaza tiles, the same warm white paper, the same soft pink and blue colored-pencil bands. Nothing "
               "new: no dark shapes, no plants, no rings, no glow, no person, no object.")


def boxes_of(d):
    b = {}
    for fn in sorted(os.listdir(d)):
        if fn.startswith("boxes") and fn.endswith(".json"):
            b.update({int(k): v for k, v in json.load(open(os.path.join(d, fn))).items()})
    return b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keys", default="12,16,20,24,28,32,36,40,44,48,52,56,60")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--grow", type=int, default=28, help="px the v9 mask grows by (takes in the glow)")
    ap.add_argument("--below", type=int, default=None, help="crop from this many px under her crown to the frame bottom")
    ap.add_argument("--tiles", action="store_true", help="the close frames (64+): ask only for tiles and the bands")
    ap.add_argument("--top", type=int, default=12, help="the mask starts this many px under her crown")
    ap.add_argument("--column", type=int, default=0, help="half-width of a column added under the mask to the crop bottom")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    keys = [int(k) for k in a.keys.split(",")]
    os.makedirs(OUT, exist_ok=True)

    fr = R.read(SRC)
    n = 105
    hp = R.track_band(fr)
    work = os.path.join(ROOT, "media/shots/F4/v9_work")
    Jr, Rr = R.masks(fr, hp, work, n)
    Mj = R.track_matte(fr, Jr, hp, n, work)
    plates = R.Plates(fr, Rr, Mj, hp, V9)
    chosen = json.load(open(os.path.join(V9, "chosen.json")))
    boxes = {}
    for k in keys:
        d, name = chosen[str(k)]
        x0, y0 = boxes_of(os.path.join(ROOT, d))[k]
        o = cv2.imread(os.path.join(ROOT, d, f"k{k:03d}_mask.png"), 0) > 127
        ch, cw = o.shape
        H, W = fr[0].shape[:2]
        old = np.zeros((H, W), bool)
        old[y0:y0 + ch, x0:x0 + cw] = o
        chin_abs = int(hp[k] + R.CHIN)
        if a.below is not None:     # a crop that starts under her head: with her head in view Bria paints a reflection
            y0 = chin_abs + a.below
            ch = H - y0
        comp = np.clip(plates.P[k][y0:y0 + ch, x0:x0 + cw], 0, 255).astype(np.uint8)     # v9's clean composite
        her = cv2.dilate((Mj[k] > 60).astype(np.uint8), np.ones((15, 15), np.uint8)) > 0
        m = cv2.dilate(old.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * a.grow + 1, 2 * a.grow + 1))) > 0
        if a.column:    # the model's glow under its reflection's head runs on down the pink band: a column to the bottom
            ys, xs = np.where(old)
            xc = int(np.median(xs))
            m[int(ys.max()) - 10:, max(0, xc - a.column):xc + a.column] = True
        m[: chin_abs + a.top] = False   # never her head or the strip right under it
        m &= ~her
        m = m[y0:y0 + ch, x0:x0 + cw]
        cv2.imwrite(os.path.join(OUT, f"k{k:03d}_in.png"), comp)
        cv2.imwrite(os.path.join(OUT, f"k{k:03d}_mask.png"), m.astype(np.uint8) * 255)
        boxes[k] = [x0, y0]
        inp = {"images": [f"file:media/shots/F4/v10b_plates/k{k:03d}_in.png"],
               "mask": f"file:media/shots/F4/v10b_plates/k{k:03d}_mask.png", "seed": a.seed,
               "instruction": INSTR_TILES if a.tiles else INSTR}
        subprocess.run([GENPY, os.path.join(ROOT, "tools/gen/cf.py"), "bria/fibo-edit-1.5",
                        os.path.join(OUT, f"k{k:03d}_out.png"), json.dumps(inp), "--tag=v10b_f4plate"]
                       + (["--dry-run"] if a.dry_run else []), check=True, cwd=ROOT)
        chosen[str(k)] = ["media/shots/F4/v10b_plates", f"k{k:03d}_out.png"]
        print("keyframe", k, "box", x0, y0, "mask px", int(m.sum()))
    old_boxes = json.load(open(os.path.join(OUT, "boxes.json"))) if os.path.exists(os.path.join(OUT, "boxes.json")) else {}
    old_boxes.update({str(k): v for k, v in boxes.items()})
    json.dump(old_boxes, open(os.path.join(OUT, "boxes.json"), "w"))
    prev = os.path.join(OUT, "chosen.json")
    if os.path.exists(prev):        # keep keys re-plated in earlier runs
        for k, v in json.load(open(prev)).items():
            if v[0].endswith("v10b_plates") and int(k) not in keys:
                chosen[k] = v
    if not a.dry_run:
        json.dump(chosen, open(prev, "w"), indent=1)


if __name__ == "__main__":
    main()
