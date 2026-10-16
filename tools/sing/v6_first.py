#!/usr/bin/env python3
"""Singing Jade (v6): first frames for BOTH singing slots from Jade's approved photo media/sing/selfie/selfie_r3b_pick.png
(her real face and light makeup, hair down and fuller, the film's jacket; 2026-10-16: "let's just use the hair down in
both"). One figure, pixel-identical in both shots; only the plate behind her differs.

    S1  over media/sing/plates/plate_close_1.jpg
    V3S over media/sing/plates/plate_truth_1.jpg

    EPY=tools/engrave/.venv/bin/python; MPY=~/Documents/1-music-shipped/orbital-sunrise-video/video/out/.venv/bin/python
    WC_VER=v6 $EPY tools/sing/wc_comp.py matte media/sing/selfie/selfie_r3b_pick.png   -> first/v6_her_alpha.png (BiRefNet)
    $MPY tools/sing/v6_first.py comp     -> first/v6_{S1,V3S}_first.jpg, v6_her_mask_first_frame_{S1,V3S}.png (identical),
                                            v6_fig.jpg + v6_alpha.png (sheet geometry, unchoked), v6_{S1,V3S}_first.json
    $MPY tools/sing/v6_first.py sheet    -> review/v6_first_vs_v5.jpg (v5c / v5d against v6, plus the v6 mask)

Geometry = v5d's (the v4 2576x1449 crop of the 2752x1536 sheet): face (landmarks 10-152) 504.6 crop px = 34.8 % of the
frame height, eye midpoint at crop (1262.1, 575.5), as measured on first/v5d_V3S_first.jpg. At that scale (1.130) the frame's
bottom edge is photo row ~1281; her arms only reach the photo's side borders at rows 1359 (left) and 1372 (right), so the
frame needs no pixel the photo does not have: no outpaint, no extension, no straight cut at the sides. Every pixel of her
is the photo's own; only the edge colours are decontaminated from the bedroom behind her (v5_first.decontaminate)."""
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mouth as MT  # noqa: E402
from v5_first import decontaminate  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIRST = os.path.join(ROOT, "media/sing/first")
CROP = json.load(open(os.path.join(FIRST, "crop.json")))["box"]        # [88, 43, 2664, 1492]
W, H = 2752, 1536
PHOTO = "media/sing/selfie/selfie_r3b_pick.png"
ALPHA = os.path.join(FIRST, "v6_her_alpha.png")
FACE_H, EYE = 504.6, (1262.1, 575.5)                                   # crop px, from v5d_V3S_first.json (first_face_h, first_eye)
PLATES = {"S1": "media/sing/plates/plate_close_1.jpg", "V3S": "media/sing/plates/plate_truth_1.jpg"}


def rd(p):
    return np.asarray(Image.open(os.path.join(ROOT, p)).convert("RGB"), np.float32)


def face(a):
    L = MT.detect(a.astype(np.uint8), (0, 0, a.shape[1], a.shape[0]))[0]
    return L, float(np.linalg.norm(L[10] - L[152])), (L[33] + L[263]) / 2


def place():
    I = rd(PHOTO)
    a = np.asarray(Image.open(ALPHA), np.float32) / 255
    _, fh, eye = face(I)
    F = decontaminate(I, a)
    s = FACE_H / fh
    ex, ey = EYE[0] + CROP[0], EYE[1] + CROP[1]                         # sheet px
    tx, ty = ex - s * eye[0], ey - s * eye[1]
    M = np.float32([[s, 0, tx], [0, s, ty]])
    fig = cv2.warpAffine(F, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
    al = np.clip(cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0), 0, 1)
    # guard: where the figure would meet a photo border inside the crop there would be a straight cut. Report it.
    h, w = a.shape
    bottom_row = (CROP[3] - ty) / s
    rows_l = np.flatnonzero(a[:, 1] > 0.5)
    rows_r = np.flatnonzero(a[:, w - 2] > 0.5)
    meta = dict(photo=PHOTO, scale=round(s, 5), face_h_photo=round(fh, 1), eye_photo=[round(float(v), 1) for v in eye],
                tx=round(float(tx), 1), ty=round(float(ty), 1),
                photo_box_sheet=[round(float(tx), 1), round(float(ty), 1), round(float(tx + s * w), 1), round(float(ty + s * h), 1)],
                crop_bottom_photo_row=round(float(bottom_row), 1),
                arm_meets_photo_border_row=dict(left=int(rows_l[0]) if len(rows_l) else None,
                                                right=int(rows_r[0]) if len(rows_r) else None),
                photo_top_in_crop=round(float(ty - CROP[1]), 1))
    for k, r in meta["arm_meets_photo_border_row"].items():
        assert r is None or r > bottom_row + 20, f"the {k} arm meets the photo border inside the frame (row {r})"
    return fig, al, meta


def comp():
    x0, y0, x1, y1 = CROP
    fig, al, meta = place()
    Image.fromarray(np.clip(fig, 0, 255).astype(np.uint8)).save(os.path.join(FIRST, "v6_fig.jpg"), quality=96)
    Image.fromarray((al * 255).astype(np.uint8)).save(os.path.join(FIRST, "v6_alpha.png"))
    ac = np.clip((cv2.GaussianBlur(al, (0, 0), 1.0) - 0.08) / 0.84, 0, 1)   # v4/v5's light choke
    for shot, plate in PLATES.items():
        P = rd(plate)
        C = fig * ac[..., None] + P * (1 - ac[..., None])
        out = os.path.join(FIRST, f"v6_{shot}_first.jpg")
        Image.fromarray(np.clip(C, 0, 255).astype(np.uint8)[y0:y1, x0:x1]).save(out, quality=96)
        m = ac[y0:y1, x0:x1]
        Image.fromarray((m * 255).astype(np.uint8)).save(os.path.join(FIRST, f"v6_her_mask_first_frame_{shot}.png"))
        _, fh, eye = face(np.asarray(Image.open(out).convert("RGB"), np.float32))
        row = np.flatnonzero(m[-3] > 0.5)
        md = dict(meta, shot=shot, plate=plate, first_face_h=round(fh, 1), first_face_frac=round(fh / (y1 - y0), 3),
                  first_eye=[round(float(v), 1) for v in eye], eye_1080=[round(float(v) * 1080 / (y1 - y0), 1) for v in eye],
                  bottom_row_span=[int(row[0]), int(row[-1])] if len(row) else None)
        json.dump(md, open(os.path.join(FIRST, f"v6_{shot}_first.json"), "w"), indent=1)
        print(os.path.relpath(out, ROOT), json.dumps(md))


def sheet():
    tiles = []
    for v in ("v5c_S1_first.jpg", "v6_S1_first.jpg", "v5d_V3S_first.jpg", "v6_V3S_first.jpg"):
        im = Image.open(os.path.join(FIRST, v)).convert("RGB").resize((960, 540), Image.LANCZOS)
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 230, 26], fill=(0, 0, 0))
        d.text((8, 7), v, fill=(255, 220, 0))
        tiles.append(np.asarray(im))
    m = Image.open(os.path.join(FIRST, "v6_her_mask_first_frame_S1.png")).convert("RGB").resize((960, 540), Image.LANCZOS)
    P = rd(PLATES["S1"])[CROP[1]:CROP[3], CROP[0]:CROP[2]]
    g = np.vstack([np.hstack(tiles[:2]), np.hstack(tiles[2:]),
                   np.hstack([np.asarray(m), np.asarray(Image.fromarray(P.astype(np.uint8)).resize((960, 540)))])])
    out = os.path.join(ROOT, "media/sing/review/v6_first_vs_v5.jpg")
    Image.fromarray(g).save(out, quality=92)
    print(os.path.relpath(out, ROOT))


if __name__ == "__main__":
    {"comp": comp, "sheet": sheet}[sys.argv[1]]()
