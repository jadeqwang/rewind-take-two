#!/usr/bin/env python3
"""Singing Jade (v9w, warm watercolour): first frames from the fixed, upscaled painted stills (tools/sing/v9w_stills.py), in
v8's medium-shot geometry (face 0.30 of the frame height, eyes at crop (1262, 560); tools/sing/v8_first.py).

    S1  media/sing/style/v9w/S1_2k.png  over media/sing/plates/plate_close_1.jpg
    V3S media/sing/style/v9w/V3S_2k.png over media/sing/plates/plate_truth_1.jpg

Matte: BiRefNet (WC_VER=v9w<SHOT> wc_comp.py matte), then wc_comp.refine (where the painting's background is bare paper
the hair wisps get a luminance key instead of BiRefNet's soft blur), then a hair-edge firming (painted wisps are ink on
paper: their alpha is set from how much darker than the paper they are, so they read dark over the plate instead of
semi-transparent grey), then (S1) the pencil key on the solid head. Edge colour: the paper is unmixed from the edge
pixels (F = (I - (1 - a) * paper) / a), so no cream fringe rides onto the engraving.

    EPY=tools/engrave/.venv/bin/python; MPY=~/Documents/1-music-shipped/orbital-sunrise-video/video/out/.venv/bin/python
    $MPY tools/sing/v9w_first.py comp      -> media/sing/first/v9w_{S1,V3S}_first.jpg, v9w_{S1,V3S}_fig.png / _alpha.png,
                                              v9w_her_mask_first_frame_*.png, v9w_*_first.json
    $MPY tools/sing/v9w_first.py check     -> media/sing/review/v9w_first_check_{S1,V3S}.jpg (magenta | plate, full size)
"""
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mouth as MT  # noqa: E402
import wc_comp  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIRST = os.path.join(ROOT, "media/sing/first")
CROP = json.load(open(os.path.join(FIRST, "crop.json")))["box"]
W, H = 2752, 1536
FACE_H, EYE = 0.30 * (CROP[3] - CROP[1]), (1262.1, 560.0)
SHOTS = {
    "S1": dict(still="media/sing/style/v9w/S1_2k.png", alpha="v9wS1_her_alpha.png", plate="media/sing/plates/plate_close_1.jpg",
               pencils=True, inktop=True),
    "V3S": dict(still="media/sing/style/v9w/V3S_2k.png", alpha="v9wV3S_her_alpha.png", plate="media/sing/plates/plate_truth_1.jpg"),
}


def rd(p):
    return np.asarray(Image.open(os.path.join(ROOT, p)).convert("RGB"), np.float32)


def alpha_of(shot, I):
    S = SHOTS[shot]
    a = np.asarray(Image.open(os.path.join(FIRST, S["alpha"])), np.float32) / 255
    a = wc_comp.refine(I, a)
    lum = I @ np.array([0.299, 0.587, 0.114], np.float32)
    paper_l = float(np.percentile(lum[a < 0.02], 60))
    # firm the hair edge: ink wisps on paper -> alpha by darkness against the paper, inside a band around the figure
    band = cv2.dilate((a > 0.5).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (61, 61))) > 0
    band &= a < 0.95
    ink = np.clip((paper_l - lum - 12) / max(paper_l - 90, 1), 0, 1)
    a = np.where(band, np.maximum(a * (ink > 0.05), ink), a)
    if S.get("inktop"):
        # S1: the bun carried a pale orange wash bloom that BiRefNet keeps as solid figure. Where v9w_stills.fix recoloured
        # (its fixmask), the alpha comes from the ORIGINAL still's darkness: dark strands stay, the pale bloom and the gaps
        # it filled go transparent. Skin (the face hull stretched up to the hairline) is never touched.
        h, w = I.shape[:2]
        wm = np.asarray(Image.open(os.path.join(ROOT, "media/sing/style/v9w/S1_fixmask.png")).convert("L").resize((w, h), Image.BILINEAR), np.float32) / 255
        orig = np.asarray(Image.open(os.path.join(ROOT, "media/sing/style/v8/glow_S1__nbp_1__fixx2.png")).convert("RGB").resize((w, h), Image.LANCZOS), np.float32)
        lo = orig @ np.array([0.299, 0.587, 0.114], np.float32)
        ink = np.clip((paper_l - 70 - lo) / 70, 0, 1)
        ink = cv2.morphologyEx(ink, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
        L = MT.detect(I.astype(np.uint8), (0, 0, w, h))[0]
        from v9w_stills import OVAL
        c = L[OVAL].mean(0)
        up = L[OVAL].copy()
        top = up[:, 1] < L[1][1]
        up[top] = c + (up[top] - c) * np.array([1.04, 1.45])
        skin = np.zeros((h, w), np.uint8)
        cv2.fillConvexPoly(skin, cv2.convexHull(up.astype(np.int32)), 1)
        edge = cv2.distanceTransform((a > 0.3).astype(np.uint8), cv2.DIST_L2, 5)     # depth inside her silhouette
        k = np.clip(wm * 2, 0, 1) * (1 - skin) * np.clip((90 - edge) / 30, 0, 1)   # outer bloom only, not the parting
        a = a * (1 - k) + np.minimum(a, ink) * k
    if S.get("pencils"):
        from v5_pencils import key as pencil_key
        solid = cv2.morphologyEx((a > 0.97).astype(np.uint8), cv2.MORPH_OPEN, np.ones((25, 25), np.uint8)) * 255.0
        a = np.maximum(a, pencil_key(np.clip(I, 0, 255).astype(np.uint8), solid.astype(np.float32)))
    return np.clip(a, 0, 1).astype(np.float32), paper_l


def unmix(I, a):
    """Edge colour with the paper taken out."""
    lum = I @ np.array([0.299, 0.587, 0.114], np.float32)
    paper = np.median(I[(a < 0.02) & (lum > np.percentile(lum, 50))], axis=0)
    ac = np.maximum(a, 0.15)[..., None]
    F = np.clip((I - (1 - ac) * paper) / ac, 0, 255)
    return np.where(a[..., None] > 0.97, I, F).astype(np.float32), paper


def place(shot):
    S = SHOTS[shot]
    I = rd(S["still"])
    a, paper_l = alpha_of(shot, I)
    F, paper = unmix(I, a)
    L = MT.detect(I.astype(np.uint8), (0, 0, I.shape[1], I.shape[0]))[0]
    fh, eye = float(np.linalg.norm(L[10] - L[152])), (L[33] + L[263]) / 2
    s = FACE_H / fh
    tx, ty = EYE[0] + CROP[0] - s * eye[0], EYE[1] + CROP[1] - s * eye[1]
    M = np.float32([[s, 0, tx], [0, s, ty]])
    fig = cv2.warpAffine(F, M, (W, H), flags=cv2.INTER_AREA if s < 1 else cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
    al = np.clip(cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_CONSTANT, borderValue=0), 0, 1)
    h, w = a.shape
    bottom_in_crop = ty + s * h - CROP[1]
    meta = dict(still=S["still"], scale=round(s, 5), still_bottom_in_crop=round(float(bottom_in_crop), 1),
                still_left_right_in_crop=[round(float(tx - CROP[0]), 1), round(float(tx + s * w - CROP[0]), 1)],
                paper=np.round(paper).tolist())
    # where does the figure meet the still's own border inside the frame?
    cy1 = (CROP[3] - ty) / s
    if cy1 > h:
        meta["figure_alpha_on_still_bottom_row"] = round(float(a[-2].max()), 2)
    return fig, al, meta


def comp(shots=("S1", "V3S")):
    x0, y0, x1, y1 = CROP
    for shot in shots:
        fig, al, meta = place(shot)
        Image.fromarray(np.clip(fig, 0, 255).astype(np.uint8)).save(os.path.join(FIRST, f"v9w_{shot}_fig.png"))
        Image.fromarray((al * 255).astype(np.uint8)).save(os.path.join(FIRST, f"v9w_{shot}_alpha.png"))
        P = rd(SHOTS[shot]["plate"])
        C = fig * al[..., None] + P * (1 - al[..., None])
        out = os.path.join(FIRST, f"v9w_{shot}_first.jpg")
        img = np.clip(C, 0, 255).astype(np.uint8)[y0:y1, x0:x1]
        Image.fromarray(img).save(out, quality=96)
        Image.fromarray((al[y0:y1, x0:x1] * 255).astype(np.uint8)).save(os.path.join(FIRST, f"v9w_her_mask_first_frame_{shot}.png"))
        L = MT.detect(img, (0, 0, img.shape[1], img.shape[0]))[0]
        d = lambda i, j: float(np.linalg.norm(L[i] - L[j]))  # noqa: E731
        row = np.flatnonzero(al[y1 - 3, x0:x1] > 0.5)
        md = dict(meta, shot=shot, plate=SHOTS[shot]["plate"], first_face_frac=round(d(10, 152) / (y1 - y0), 3),
                  eye_1080=[round(float(v) * 1080 / (y1 - y0), 1) for v in (L[33] + L[263]) / 2],
                  io_1080=round(d(33, 263) * 1080 / (y1 - y0), 1),
                  bottom_row_span=[int(row[0]), int(row[-1])] if len(row) else None)
        json.dump(md, open(os.path.join(FIRST, f"v9w_{shot}_first.json"), "w"), indent=1)
        print(os.path.relpath(out, ROOT), json.dumps(md))


def check():
    x0, y0, x1, y1 = CROP
    for shot in SHOTS:
        F = rd(f"media/sing/first/v9w_{shot}_fig.png")[y0:y1, x0:x1]
        a = (np.asarray(Image.open(os.path.join(FIRST, f"v9w_{shot}_alpha.png")), np.float32) / 255)[y0:y1, x0:x1, None]
        M = F * a + np.array([255, 0, 255], np.float32) * (1 - a)
        P = rd(f"media/sing/first/v9w_{shot}_first.jpg")
        Image.fromarray(np.hstack([M, P]).clip(0, 255).astype(np.uint8)).save(
            os.path.join(ROOT, f"media/sing/review/v9w_first_check_{shot}.jpg"), quality=92)
        print(f"media/sing/review/v9w_first_check_{shot}.jpg")


if __name__ == "__main__":
    {"comp": comp, "check": check}[sys.argv[1]]()
