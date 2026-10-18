#!/usr/bin/env python3
"""Singing Jade (v7): first frames from Jade's two new selfies (2026-10-18: "the first clip using hairup with pencils and the
second clip using hairdown"), one figure per shot, in v6's geometry (face height and eye position).

    S1  inputs/selfie_hairup_jade_jacket_retouch_v2.png   over media/sing/plates/plate_close_1.jpg
    V3S inputs/selfie_hairdown_jade_jacket_retouch_v2.png over media/sing/plates/plate_truth_1.jpg

The selfies are close-ups: at v6's scale each covers only the middle third of the frame and stops above its bottom edge,
so the shoulders, arms and lower chest are outpainted first (tools/sing/v7_outpaint.py; every pixel the photo shows is
the photo's own: face, hair, pencils, glasses, collar). The picks: S1 = outpaint/v7/S1_nbp_2_merged.png, V3S =
outpaint/v7/V3S_nbp_5_merged.png.

    EPY=tools/engrave/.venv/bin/python; MPY=~/Documents/1-music-shipped/orbital-sunrise-video/video/out/.venv/bin/python
    WC_VER=v7S1  $EPY tools/sing/wc_comp.py matte media/sing/outpaint/v7/S1_nbp_2_merged.png   -> first/v7S1_her_alpha.png
    WC_VER=v7V3S $EPY tools/sing/wc_comp.py matte media/sing/outpaint/v7/V3S_nbp_5_merged.png  -> first/v7V3S_her_alpha.png
    $MPY tools/sing/v7_first.py comp     -> first/v7_{S1,V3S}_first.jpg, v7_her_mask_first_frame_{S1,V3S}.png,
                                            v7_{S1,V3S}_fig.jpg + v7_{S1,V3S}_alpha.png (sheet geometry), v7_{S1,V3S}_first.json
    $MPY tools/sing/v7_first.py sheet    -> review/v7_first_vs_v6.jpg (v6 against v7 per shot, plus the v7 masks)
    $MPY tools/sing/v7_first.py magenta  -> review/v7_first_magenta_{S1,V3S}.jpg (the placed figure over magenta, full size)

Geometry = v6's (= v5d's): face (landmarks 10-152) 504.6 crop px, eye midpoint at crop (1262.1, 575.5) in the 2576x1449
crop of the 2752x1536 sheet. Edge colours are decontaminated from the room behind her (v5_first.decontaminate). A guard
asserts that the figure never meets the outpaint canvas's border inside the frame (no straight cut)."""
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
FACE_H, EYE = 504.6, (1262.1, 575.5)                                   # crop px (v6_first.py)
SHOTS = {
    "S1": dict(photo="media/sing/outpaint/v7/S1_nbp_2_merged.png", alpha="v7S1_her_alpha.png",
               plate="media/sing/plates/plate_close_1.jpg", source="inputs/selfie_hairup_jade_jacket_retouch_v2.png"),
    "V3S": dict(photo="media/sing/outpaint/v7/V3S_nbp_5_merged.png", alpha="v7V3S_her_alpha.png",
                plate="media/sing/plates/plate_truth_1.jpg", source="inputs/selfie_hairdown_jade_jacket_retouch_v2.png",
                # the white door trim behind the hair at the left of her head (photo x ~325-345, rows ~430-700): BiRefNet
                # keeps it between the strands (alpha 0.7-1.0) and it is not the wall's colour, so decontamination cannot
                # clean it. Luminance key inside this canvas box (x0, y0, x1, y1): see trim_key()
                trim=(940, 420, 1045, 790)),
}


def trim_key(I, a, box):
    """Dark strands over a bright trim: where the brightest thing nearby is much brighter than hair (the trim), alpha is
    how much darker than that the pixel is (hair ~45 -> 1, trim -> 0). Only lowers alpha, only inside box."""
    x0, y0, x1, y1 = box
    L = I[y0:y1, x0:x1].mean(2)
    bg = cv2.dilate(L, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    k = np.clip((bg - L) / np.maximum(bg - 45, 1), 0, 1)
    k = np.where(bg > 140, k, 1.0)
    out = a.copy()
    out[y0:y1, x0:x1] = np.minimum(a[y0:y1, x0:x1], k)
    return out


def rd(p):
    return np.asarray(Image.open(os.path.join(ROOT, p)).convert("RGB"), np.float32)


def face(a):
    L = MT.detect(a.astype(np.uint8), (0, 0, a.shape[1], a.shape[0]))[0]
    return L, float(np.linalg.norm(L[10] - L[152])), (L[33] + L[263]) / 2


def place(shot):
    S = SHOTS[shot]
    I = rd(S["photo"])
    a = np.asarray(Image.open(os.path.join(FIRST, S["alpha"])), np.float32) / 255
    if "trim" in S:
        a = trim_key(I, a, S["trim"])
    _, fh, eye = face(I)
    F = decontaminate(I, a)
    s = FACE_H / fh
    ex, ey = EYE[0] + CROP[0], EYE[1] + CROP[1]
    tx, ty = ex - s * eye[0], ey - s * eye[1]
    M = np.float32([[s, 0, tx], [0, s, ty]])
    fig = cv2.warpAffine(F, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
    al = np.clip(cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0), 0, 1)
    h, w = a.shape
    # guard: the canvas border inside the crop must carry no figure (else a straight cut shows)
    cx0, cy0 = (CROP[0] - tx) / s, (CROP[1] - ty) / s                   # crop box in canvas px
    cx1, cy1 = (CROP[2] - tx) / s, (CROP[3] - ty) / s
    r0, r1 = int(max(0, cy0)), int(min(h, cy1))
    edge = dict(left=float(a[r0:r1, :3].max()) if cx0 < 0 else None, right=float(a[r0:r1, -3:].max()) if cx1 > w else None,
                bottom=float(a[-3:, int(max(0, cx0)):int(min(w, cx1))].max()) if cy1 > h else None,
                top=float(a[:3, int(max(0, cx0)):int(min(w, cx1))].max()) if cy0 < 0 else None)
    meta = dict(photo=S["photo"], source=S["source"], scale=round(s, 5), face_h_canvas=round(fh, 1),
                eye_canvas=[round(float(v), 1) for v in eye], tx=round(float(tx), 1), ty=round(float(ty), 1),
                crop_in_canvas=[round(float(v), 1) for v in (cx0, cy0, cx1, cy1)], canvas=[w, h],
                figure_alpha_at_canvas_border_in_frame=edge)
    for k, v in edge.items():
        assert v is None or v < 0.1, f"{shot}: the figure meets the canvas {k} border inside the frame ({v})"
    return fig, al, meta


def comp(shots=("S1", "V3S")):
    x0, y0, x1, y1 = CROP
    for shot in shots:
        fig, al, meta = place(shot)
        Image.fromarray(np.clip(fig, 0, 255).astype(np.uint8)).save(os.path.join(FIRST, f"v7_{shot}_fig.jpg"), quality=96)
        Image.fromarray((al * 255).astype(np.uint8)).save(os.path.join(FIRST, f"v7_{shot}_alpha.png"))
        ac = np.clip((cv2.GaussianBlur(al, (0, 0), 1.0) - 0.08) / 0.84, 0, 1)   # v4-v6's light choke
        P = rd(SHOTS[shot]["plate"])
        C = fig * ac[..., None] + P * (1 - ac[..., None])
        out = os.path.join(FIRST, f"v7_{shot}_first.jpg")
        Image.fromarray(np.clip(C, 0, 255).astype(np.uint8)[y0:y1, x0:x1]).save(out, quality=96)
        m = ac[y0:y1, x0:x1]
        Image.fromarray((m * 255).astype(np.uint8)).save(os.path.join(FIRST, f"v7_her_mask_first_frame_{shot}.png"))
        L, fh, eye = face(np.asarray(Image.open(out).convert("RGB"), np.float32))
        row = np.flatnonzero(m[-3] > 0.5)
        md = dict(meta, shot=shot, plate=SHOTS[shot]["plate"], first_face_h=round(fh, 1), first_face_frac=round(fh / (y1 - y0), 3),
                  first_eye=[round(float(v), 1) for v in eye], eye_1080=[round(float(v) * 1080 / (y1 - y0), 1) for v in eye],
                  first_interocular=round(float(np.linalg.norm(L[33] - L[263])), 1),
                  first_face_w=round(float(np.linalg.norm(L[234] - L[454])), 1),
                  bottom_row_span=[int(row[0]), int(row[-1])] if len(row) else None)
        json.dump(md, open(os.path.join(FIRST, f"v7_{shot}_first.json"), "w"), indent=1)
        print(os.path.relpath(out, ROOT), json.dumps(md))


def label(im, t):
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 8 * len(t) + 14, 24], fill=(0, 0, 0))
    d.text((7, 6), t, fill=(255, 220, 0))
    return im


def sheet():
    rows = []
    for shot in ("S1", "V3S"):
        t = [label(Image.open(os.path.join(FIRST, f)).convert("RGB").resize((960, 540), Image.LANCZOS), f)
             for f in (f"v6_{shot}_first.jpg", f"v7_{shot}_first.jpg")]
        m = label(Image.open(os.path.join(FIRST, f"v7_her_mask_first_frame_{shot}.png")).convert("RGB").resize((960, 540)),
                  f"v7 {shot} mask")
        rows.append(np.hstack([np.asarray(x) for x in t + [m]]))
    out = os.path.join(ROOT, "media/sing/review/v7_first_vs_v6.jpg")
    Image.fromarray(np.vstack(rows)).save(out, quality=92)
    print(os.path.relpath(out, ROOT), "(v6b S1 used v6_S1_first.jpg)")


def magenta():
    x0, y0, x1, y1 = CROP
    for shot in SHOTS:
        F = rd(f"media/sing/first/v7_{shot}_fig.jpg")
        a = np.asarray(Image.open(os.path.join(FIRST, f"v7_{shot}_alpha.png")), np.float32) / 255
        ac = np.clip((cv2.GaussianBlur(a, (0, 0), 1.0) - 0.08) / 0.84, 0, 1)[..., None]
        C = F * ac + np.array([255, 0, 255], np.float32) * (1 - ac)
        out = os.path.join(ROOT, f"media/sing/review/v7_first_magenta_{shot}.jpg")
        Image.fromarray(np.clip(C, 0, 255).astype(np.uint8)[y0:y1, x0:x1]).save(out, quality=94)
        print(os.path.relpath(out, ROOT))


if __name__ == "__main__":
    {"comp": comp, "sheet": sheet, "magenta": magenta}[sys.argv[1]]()
