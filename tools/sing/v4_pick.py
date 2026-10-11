#!/usr/bin/env python3
"""Watercolor singing Jade (v4), step 0b: one portrait from a hair pick and an expression pick (no paid call).

    MPY=~/Documents/orbital-sunrise-video/video/out/.venv/bin/python
    $MPY tools/sing/v4_pick.py HAIR_KEY FACE_KEY [--out=media/sing/v4/stills/pick_<name>.png] [--name=...]
    $MPY tools/sing/v4_pick.py HAIR_KEY -            hair pick only (keeps the portrait's own expression)
    $MPY tools/sing/v4_pick.py - FACE_KEY            expression pick only (keeps the portrait's own hair)

Keys are the candidate names in media/sing/v4/stills/ (v4_stills.py), e.g. hair_gloss__nbp_1 face_e2_trace__nbp_1.
Both candidates are mapped onto the reference portrait at K x its size (similarity fit on eye, nose and brow
landmarks; the face layer is then registered to the hair layer on the glasses). The result is the hair candidate
with the expression candidate's face laid into it through a feathered face oval. Where the two disagree about hair
(a strand across the cheek in one and not in the other) the hair candidate wins, except in the middle of the face
(brows, eyes, nose, mouth). Rows the candidates do not reach come from the portrait itself.

Writes OUT (K x 971x1620), OUT.json (inputs, masks, registration) and OUT_check.jpg (hair | face | result, head crop).
"""
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mouth as MT  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "inputs/jade_watercolor_jacket_v6.png")
DIR = os.path.join(ROOT, "media/sing/v4/stills")
K = 2
STABLE = [33, 133, 362, 263, 168, 6, 197, 195, 5, 4, 1, 98, 327, 10, 151, 9, 127, 356, 234, 454]
FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150,
             136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
MIDDLE = [70, 63, 105, 66, 107, 336, 296, 334, 293, 300, 33, 263, 61, 291, 17, 18, 200, 129, 358, 50, 280]


def lum(a):
    return a @ np.array([0.299, 0.587, 0.114], np.float32)


def load(key, L0, size):
    """Candidate mapped onto the portrait at K x: (image float32, coverage 0..1, landmarks in K x portrait px)."""
    d = json.load(open(os.path.join(DIR, key + ".json")))
    a = np.asarray(Image.open(os.path.join(ROOT, d["out"][0])).convert("RGB"))
    L = MT.detect(a, (0, 0, a.shape[1], a.shape[0]))[0]
    M, _ = cv2.estimateAffinePartial2D(L[STABLE].astype(np.float32), (L0[STABLE] * K).astype(np.float32), method=cv2.LMEDS)
    s = float(np.hypot(M[0, 0], M[0, 1]))
    w = cv2.warpAffine(a, M, size, flags=cv2.INTER_AREA if s < 0.8 else cv2.INTER_LANCZOS4, borderValue=(0, 0, 0))
    cov = cv2.warpAffine(np.full(a.shape[:2], 255, np.uint8), M, size, flags=cv2.INTER_LINEAR)
    cov = cv2.erode(cov, np.ones((9, 9), np.uint8)).astype(np.float32) / 255
    return w.astype(np.float32), cov, L @ M[:, :2].T + M[:, 2], d, s


def poly(pts, shape, grow=1.0):
    c = pts.mean(0)
    m = np.zeros(shape[:2], np.uint8)
    cv2.fillPoly(m, [(c + (pts - c) * grow).astype(np.int32)], 255)
    return m


def main(hair, face, out=None, name=None):
    src = np.asarray(Image.open(SRC).convert("RGB"))
    L0 = MT.detect(src, (0, 0, src.shape[1], src.shape[0]))[0]
    size = (src.shape[1] * K, src.shape[0] * K)
    P = cv2.resize(src, size, interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    info = {"hair": hair, "face": face, "src": os.path.relpath(SRC, ROOT), "scale": K}

    if hair != "-":
        H, covH, LH, dH, sH = load(hair, L0, size)
        info["hair_model"], info["hair_px_per_out_px"] = dH["model"], round(1 / sH, 3)
        fade = cv2.GaussianBlur(covH, (0, 0), 12 * K)                     # the candidate's bottom edge fades into the portrait
        fade = np.clip((fade - 0.5) * 2, 0, 1)[..., None]
        R = H * fade + P * (1 - fade)
    else:
        R, LH = P.copy(), L0 * K

    if face != "-":
        F, covF, LF, dF, sF = load(face, L0, size)
        info["face_model"], info["face_px_per_out_px"] = dF["model"], round(1 / sF, 3)
        # register the face layer to the hair layer on the glasses and brows (both kept them): translation only
        x0, y0 = (LF[[127, 70]].min(0) - 30 * K).astype(int)
        x1, y1 = (np.array([LF[356, 0], LF[[230, 450], 1].max()]) + 30 * K).astype(int)
        g1 = cv2.GaussianBlur(lum(R[y0:y1, x0:x1]), (0, 0), 1.5)
        g2 = cv2.GaussianBlur(lum(F[y0:y1, x0:x1]), (0, 0), 1.5)
        try:
            warp = np.eye(2, 3, dtype=np.float32)
            cc, warp = cv2.findTransformECC(g1, g2, warp, cv2.MOTION_TRANSLATION,
                                            (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6), None, 5)
            dx, dy = float(warp[0, 2]), float(warp[1, 2])
            if max(abs(dx), abs(dy)) < 8 * K:
                Mt = np.float32([[1, 0, -dx], [0, 1, -dy]])
                F = cv2.warpAffine(F, Mt, size, flags=cv2.INTER_LANCZOS4)
                LF = LF - [dx, dy]
            info["register"] = {"dx": round(dx, 2), "dy": round(dy, 2), "cc": round(float(cc), 3)}
        except cv2.error as e:
            info["register"] = {"error": str(e)[:120]}
        oval = cv2.GaussianBlur(poly(LF[FACE_OVAL], F.shape, 0.93).astype(np.float32) / 255, (0, 0), 9 * K)
        mid = cv2.dilate(poly(cv2.convexHull(LF[MIDDLE].astype(np.float32))[:, 0], F.shape, 1.0), np.ones((25 * K, 25 * K), np.uint8))
        lr, lf = lum(R), lum(F)
        hairy = ((np.abs(lr - lf) > 45) & (np.minimum(lr, lf) < 105)).astype(np.uint8)
        hairy = cv2.dilate(cv2.morphologyEx(hairy, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)), np.ones((5 * K, 5 * K), np.uint8))
        hairy = cv2.GaussianBlur((hairy * (mid == 0)).astype(np.float32), (0, 0), 2.5 * K)
        m = (oval * (1 - np.clip(hairy * 1.6, 0, 1)))[..., None]
        # the face layer takes the hair layer's low-frequency colour, so two models' skin tones meet without a step
        core = (oval > 0.6).astype(np.float32)
        nb = lambda X: cv2.GaussianBlur(X * core[..., None], (0, 0), 60 * K) / (cv2.GaussianBlur(core, (0, 0), 60 * K)[..., None] + 1e-3)
        ratio = np.clip((nb(R) + 4) / (nb(F) + 4), 0.85, 1.18)
        info["skin_ratio_mean"] = [round(float(v), 3) for v in ratio[core > 0].mean(0)]
        R = F * ratio * m + R * (1 - m)
        info["face_mask_area_px"] = int((m > 0.5).sum())

    name = name or f"{hair.replace('hair_', '') if hair != '-' else 'hair0'}+{face.replace('face_', '') if face != '-' else 'face0'}"
    out = out or os.path.join(DIR, f"pick_{name}.png")
    R8 = np.clip(R, 0, 255).astype(np.uint8)
    Image.fromarray(R8).save(out)
    Lr = MT.detect(R8, (0, 0, size[0], size[1]))
    if Lr is not None:
        up = [i for i in range(468) if L0[i, 1] < L0[2, 1]]
        io = np.linalg.norm(L0[33] - L0[263]) * K
        d = np.linalg.norm(Lr[0][up] - L0[up] * K, axis=1) / io * 100
        info["upper_face_shift_pct_io"] = {"mean": round(float(d.mean()), 2), "max": round(float(d.max()), 2)}
        info["smile"] = round((Lr[1].get("mouthSmileLeft", 0) + Lr[1].get("mouthSmileRight", 0)) / 2, 3)
    info["out"] = os.path.relpath(out, ROOT)
    json.dump(info, open(os.path.splitext(out)[0] + ".json", "w"), indent=1)
    box = (60 * K, 20 * K, 910 * K, 1060 * K)
    tiles = [Image.fromarray(np.clip(X, 0, 255).astype(np.uint8)).crop(box).resize((850, 1040), Image.LANCZOS)
             for X in ([H] if hair != "-" else [P]) + ([F] if face != "-" else []) + [R]]
    S = Image.new("RGB", (860 * len(tiles), 1040), (28, 28, 30))
    for i, t in enumerate(tiles):
        S.paste(t, (860 * i, 0))
    S.save(os.path.splitext(out)[0] + "_check.jpg", quality=92)
    print(json.dumps(info))


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    o = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    main(a[0], a[1], o.get("out"), o.get("name"))
