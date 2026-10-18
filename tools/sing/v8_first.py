#!/usr/bin/env python3
"""Singing Jade (v8, "sultry" test round, 2026-10-18): first frames with a medium-shot framing and a warm side light.

Kenton on v7: "much better than the previous version, but there's something about the original one (in watercolor art)
that this one is lacking". The coordinator's comparison against watercolor v4 found: the watercolor is lit warm from one
side with cheekbone shadow and a flush, and it is framed wider (a medium shot), while the selfies are flat frontal
daylight and the selfie lens makes her head look big. So, against v7:

  framing  face 0.30 of the frame height (v6/v7: 0.35), eyes at crop (1262, 560); natural-width shoulders:
           S1 from a new, wider fill (outpaint/v8/S1_nbp_1, ~2.7 face heights across against v7's ~2.3);
           V3S from v7's fill (outpaint/v7/V3S_nbp_5, already ~2.7; every wider v8 V3S fill cut her arm or added a
           second jacket)
  pencils  S1: v5_pencils.key on the canvas puts both pencils back into the BiRefNet alpha (the first v8 S1 frame lacked
           the pink eraser and ferrule, and all three takes made from it, v8_take_1..3, lost the pink eraser)
  relight  a LOCAL relight: one smooth, low-frequency gain field (per channel) multiplied over her own pixels. There is
           no generative edit, so no feature, face shape, eye size or makeup can move. The field has a warm key from one
           side (S1 from frame-right, as in the watercolor; V3S from frame-left, the warm side of plate_truth_1), a
           shadow fall-off to the other side, shadow down the far side of the face and under the cheekbones, and a light
           warm flush on the cheeks.

    EPY=tools/engrave/.venv/bin/python; MPY=~/Documents/1-music-shipped/orbital-sunrise-video/video/out/.venv/bin/python
    WC_VER=v8S1 $EPY tools/sing/wc_comp.py matte media/sing/outpaint/v8/S1_nbp_1_merged.png   -> first/v8S1_her_alpha.png
    $MPY tools/sing/v8_first.py comp     -> first/v8_{S1,V3S}_first.jpg (relit) + v8_{S1,V3S}_flat.jpg (same, unlit),
                                            v8_her_mask_first_frame_*.png, v8_*_fig.jpg / _alpha.png / _gain.png, .json
    $MPY tools/sing/v8_first.py sheet    -> review/v8_first_relight.jpg (v7 | v8 flat | v8 relit, plus face crops)
"""
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mouth as MT  # noqa: E402
from v5_first import decontaminate  # noqa: E402
from v7_first import trim_key  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIRST = os.path.join(ROOT, "media/sing/first")
CROP = json.load(open(os.path.join(FIRST, "crop.json")))["box"]
W, H = 2752, 1536
FACE_FRAC = 0.30
FACE_H, EYE = FACE_FRAC * (CROP[3] - CROP[1]), (1262.1, 560.0)
SHOTS = {
    "S1": dict(photo="media/sing/outpaint/v8/S1_nbp_1_merged.png", alpha="v8S1_her_alpha.png",
               plate="media/sing/plates/plate_close_1.jpg", key=+1, pencils=True),
    "V3S": dict(photo="media/sing/outpaint/v7/V3S_nbp_5_merged.png", alpha="v7V3S_her_alpha.png",
                plate="media/sing/plates/plate_truth_1.jpg", key=-1, trim=(940, 420, 1045, 790)),
}
# relight strengths (gain - 1); key = +1 lights from frame-right, -1 from frame-left
K = dict(key=0.09, fall=0.27, face_side=0.21, cheek=0.17, flush=0.05, warm=0.05)


def rd(p):
    return np.asarray(Image.open(os.path.join(ROOT, p)).convert("RGB"), np.float32)


def landmarks(a):
    return MT.detect(a.astype(np.uint8), (0, 0, a.shape[1], a.shape[0]))[0]


def ellipse(shape, c, axes, ang):
    m = np.zeros(shape, np.float32)
    cv2.ellipse(m, (int(c[0]), int(c[1])), (max(1, int(axes[0])), max(1, int(axes[1]))), float(ang), 0, 360, 1.0, -1)
    return m


def gain_field(shape, L, key):
    """Per-channel gain (h, w, 3), smooth on the scale of the face. key = +1 / -1 (light from frame-right / left)."""
    h, w = shape
    fh = float(np.linalg.norm(L[10] - L[152]))
    fw = float(np.linalg.norm(L[234] - L[454]))
    cx = float(L[:, 0].mean())
    xx = np.arange(w, dtype=np.float32)[None, :] * np.ones((h, 1), np.float32)
    ramp = np.tanh((xx - cx) / (0.9 * fw) * key)                     # +1 on the key side, -1 on the far side
    lum = 1 + np.where(ramp > 0, K["key"] * ramp, K["fall"] * ramp)
    # the far side of the face: a shadow band just inside the face outline on that side
    hull = np.zeros((h, w), np.uint8)
    cv2.fillConvexPoly(hull, cv2.convexHull(L.astype(np.int32)), 1)
    edge_d = cv2.distanceTransform(hull, cv2.DIST_L2, 5)
    far = np.clip(-ramp, 0, 1)
    side = np.exp(-edge_d / (0.10 * fw)) * hull * far
    # under the cheekbones: an elongated soft ellipse from below the outer cheekbone toward the mouth corner, each side
    cheek = np.zeros((h, w), np.float32)
    for side_pt, corner, wgt in ((234, 61, None), (454, 291, None)):
        a, b = L[side_pt], L[corner]
        c = a + (b - a) * 0.45 + np.array([0, 0.05 * fh])
        ang = np.degrees(np.arctan2(b[1] - a[1], b[0] - a[0]))
        e = ellipse((h, w), c, (0.20 * fw, 0.045 * fh), ang)
        s = 1.0 if np.sign(c[0] - cx) != np.sign(key) else 0.45       # deeper on the far side
        cheek = np.maximum(cheek, e * s)
    side = cv2.GaussianBlur(side, (0, 0), 0.04 * fh)
    cheek = cv2.GaussianBlur(cheek, (0, 0), 0.05 * fh)
    lum = lum * (1 - K["face_side"] * side) * (1 - K["cheek"] * cheek)
    lum = cv2.GaussianBlur(lum, (0, 0), 0.03 * fh)
    G = np.repeat(lum[..., None], 3, 2)
    # warm key, slightly cooler shadow
    warm = np.clip(ramp, 0, 1)
    G[..., 0] *= 1 + K["warm"] * (0.6 + 0.4 * warm)
    G[..., 2] *= 1 - K["warm"] * (0.6 + 0.4 * warm)
    G[..., 2] *= 1 + 0.02 * np.clip(-ramp, 0, 1)
    # flush on the cheek apples, stronger on the key side
    fl = np.zeros((h, w), np.float32)
    for pt in (50, 280):
        s = 1.0 if np.sign(L[pt][0] - cx) == np.sign(key) else 0.6
        fl = np.maximum(fl, ellipse((h, w), L[pt], (0.17 * fw, 0.12 * fh), 0) * s)
    fl = cv2.GaussianBlur(fl, (0, 0), 0.09 * fh)   # broad and weak: a warmth, never a blush spot (her makeup stays hers)
    G[..., 0] *= 1 + K["flush"] * fl
    G[..., 1] *= 1 - 0.45 * K["flush"] * fl
    G[..., 2] *= 1 - 0.5 * K["flush"] * fl
    return G


def place(shot):
    S = SHOTS[shot]
    I = rd(S["photo"])
    a = np.asarray(Image.open(os.path.join(FIRST, S["alpha"])), np.float32) / 255
    if "trim" in S:
        a = trim_key(I, a, S["trim"])
    if S.get("pencils"):          # BiRefNet dropped the pink eraser + ferrule on the v8 canvas: key both pencils back in
        from v5_pencils import key as pencil_key
        solid = cv2.morphologyEx((a > 0.97).astype(np.uint8), cv2.MORPH_OPEN, np.ones((15, 15), np.uint8)) * 255.0   # the head, not the flyaways (they set key()'s window too high)
        a = np.maximum(a, pencil_key(np.clip(I, 0, 255).astype(np.uint8), solid.astype(np.float32)))
    L = landmarks(I)
    fh, eye = float(np.linalg.norm(L[10] - L[152])), (L[33] + L[263]) / 2
    F = decontaminate(I, a)
    G = gain_field(a.shape, L, S["key"])
    s = FACE_H / fh
    ex, ey = EYE[0] + CROP[0], EYE[1] + CROP[1]
    tx, ty = ex - s * eye[0], ey - s * eye[1]
    M = np.float32([[s, 0, tx], [0, s, ty]])
    warp = lambda X, f=cv2.INTER_LANCZOS4: cv2.warpAffine(X, M, (W, H), flags=f, borderMode=cv2.BORDER_REPLICATE)  # noqa: E731
    fig, gain = warp(F), warp(G, cv2.INTER_LINEAR)
    al = np.clip(cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0), 0, 1)
    h, w = a.shape
    cx0, cy0, cx1, cy1 = (CROP[0] - tx) / s, (CROP[1] - ty) / s, (CROP[2] - tx) / s, (CROP[3] - ty) / s
    r0, r1 = int(max(0, cy0)), int(min(h, cy1))
    edge = dict(left=float(a[r0:r1, :3].max()) if cx0 < 0 else None, right=float(a[r0:r1, -3:].max()) if cx1 > w else None,
                bottom=float(a[-3:, int(max(0, cx0)):int(min(w, cx1))].max()) if cy1 > h else None,
                top=float(a[:3, int(max(0, cx0)):int(min(w, cx1))].max()) if cy0 < 0 else None)
    for k, v in edge.items():
        assert v is None or v < 0.1, f"{shot}: the figure meets the canvas {k} border inside the frame ({v})"
    meta = dict(photo=S["photo"], scale=round(s, 5), face_frac_target=FACE_FRAC, key="frame-right" if S["key"] > 0 else "frame-left",
                relight=K, crop_in_canvas=[round(float(v), 1) for v in (cx0, cy0, cx1, cy1)],
                figure_alpha_at_canvas_border_in_frame=edge)
    return fig, gain, al, meta


def ident(img):
    a = np.asarray(Image.fromarray(img).resize((1280, 720), Image.LANCZOS))
    L = landmarks(a.astype(np.float32))
    d = lambda i, j: float(np.linalg.norm(L[i] - L[j]))  # noqa: E731
    return dict(io=round(d(33, 263), 1), eye_w=round((d(33, 133) + d(362, 263)) / 2, 1), face_w=round(d(234, 454), 1),
                face_h=round(d(10, 152), 1)), L


def comp(shots=("S1", "V3S")):
    x0, y0, x1, y1 = CROP
    for shot in shots:
        fig, gain, al, meta = place(shot)
        lit = np.clip(fig * gain, 0, 255)
        Image.fromarray(lit.astype(np.uint8)).save(os.path.join(FIRST, f"v8_{shot}_fig.jpg"), quality=96)
        Image.fromarray((al * 255).astype(np.uint8)).save(os.path.join(FIRST, f"v8_{shot}_alpha.png"))
        Image.fromarray(np.clip((gain[..., 0] / 1.3) * 255, 0, 255).astype(np.uint8)).save(os.path.join(FIRST, f"v8_{shot}_gain.png"))
        ac = np.clip((cv2.GaussianBlur(al, (0, 0), 1.0) - 0.08) / 0.84, 0, 1)
        P = rd(SHOTS[shot]["plate"])
        out = {}
        for tag, F in (("flat", fig), ("first", lit)):
            C = F * ac[..., None] + P * (1 - ac[..., None])
            img = np.clip(C, 0, 255).astype(np.uint8)[y0:y1, x0:x1]
            Image.fromarray(img).save(os.path.join(FIRST, f"v8_{shot}_{tag}.jpg"), quality=96)
            out[tag] = img
        Image.fromarray((ac[y0:y1, x0:x1] * 255).astype(np.uint8)).save(os.path.join(FIRST, f"v8_her_mask_first_frame_{shot}.png"))
        idf, Lf = ident(out["flat"])
        idl, Ll = ident(out["first"])
        fh = float(np.linalg.norm(Ll[10] - Ll[152]))
        row = np.flatnonzero(ac[y1 - 3, x0:x1] > 0.5)
        md = dict(meta, shot=shot, plate=SHOTS[shot]["plate"], ident_720_flat=idf, ident_720_relit=idl,
                  landmark_shift_relit_vs_flat_px_720=round(float(np.linalg.norm(Ll - Lf, axis=1).mean()), 2),
                  first_face_frac=round(fh / 720, 3), eye_1080=[round(float(v) * 1.5, 1) for v in (Ll[33] + Ll[263]) / 2],
                  bottom_row_span=[int(row[0]), int(row[-1])] if len(row) else None)
        json.dump(md, open(os.path.join(FIRST, f"v8_{shot}_first.json"), "w"), indent=1)
        print(shot, json.dumps({k: md[k] for k in ("scale", "first_face_frac", "eye_1080", "ident_720_flat", "ident_720_relit",
                                                     "landmark_shift_relit_vs_flat_px_720", "bottom_row_span", "key")}))


def label(im, t):
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 8 * len(t) + 14, 24], fill=(0, 0, 0))
    d.text((7, 6), t, fill=(255, 220, 0))
    return im


def sheet():
    rows = []
    for shot in ("S1", "V3S"):
        files = (f"v7_{shot}_first.jpg", f"v8_{shot}_flat.jpg", f"v8_{shot}_first.jpg")
        rows.append(np.hstack([np.asarray(label(Image.open(os.path.join(FIRST, f)).convert("RGB").resize((960, 540), Image.LANCZOS),
                                                f.replace("_first", " relit" if f.startswith("v8") else " first")))
                               for f in files]))
        crops = []
        for f in files[1:]:
            im = Image.open(os.path.join(FIRST, f)).convert("RGB")
            js = json.load(open(os.path.join(FIRST, f"v8_{shot}_first.json")))
            ex, ey = js["eye_1080"][0] * 2576 / 1920, js["eye_1080"][1] * 2576 / 1920
            box = (int(ex - 330), int(ey - 300), int(ex + 330), int(ey + 420))
            crops.append(np.asarray(label(im.crop(box).resize((660, 720), Image.LANCZOS), f"{f[:-4]} face")))
        pad = np.zeros((720, 2880 - 1320, 3), np.uint8)
        rows.append(np.hstack(crops + [pad]))
    out = os.path.join(ROOT, "media/sing/review/v8_first_relight.jpg")
    Image.fromarray(np.vstack(rows)).save(out, quality=90)
    print(os.path.relpath(out, ROOT))


if __name__ == "__main__":
    {"comp": comp, "sheet": sheet}[sys.argv[1]]()
