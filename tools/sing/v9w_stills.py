#!/usr/bin/env python3
"""Singing Jade (v9w, warm watercolour): the two painted stills fixed and upscaled before Seedance.

Jade (2026-10-18): "i like warm watercolour warm light. can you animate those and let me see the lip sync on those with v8's
acting directions". Sources (media/sing/style/v8/README.md, tools/sing/style8.py): nano-banana-pro paintings with a
gpt-image face correction against her photo, 1536x1024:
    S1  media/sing/style/v8/glow_S1__nbp_1__fixx2.png        (hair up, pencils)
    V3S media/sing/style/v8/glow_V3S__nbp_1__fixx2__ext.png  (hair down)

fix      a LOCAL recolour in the hair only (no model call, face pixels untouched):
           S1: the orange light-wash bloom around the bun and down her left temple (reads as bleached hair) -> where it
               lies on paper it goes back to paper; where it tints a strand the strand goes to her dark hair tone.
           V3S: the brown-gold cast in the hair -> chroma cut to 25 % and mid-tones darkened a little, so the hair reads
               dark with a little warm highlight left.
         Protected: the face oval (MediaPipe, dilated a little), both ears, the pencils (yellow / pink / pale-blue keyed),
         and in V3S the jacket's bright orange bands.
upscale  Real-ESRGAN x4plus (via spandrel, tiled) to 2x, blended 50/50 with Lanczos 2x to keep the paint grain; the face is then checked
         against the 1536 still (landmarks, NME) and by eye.
metrics  likeness of each stage against her photo (the outpaint canvas), as in style8.py metrics.

    MPY=~/Documents/1-music-shipped/orbital-sunrise-video/video/out/.venv/bin/python   (MediaPipe + OpenCV)
    EPY=tools/engrave/.venv/bin/python                                                  (torch + spandrel)
    $MPY tools/sing/v9w_stills.py fix        -> media/sing/style/v9w/{S1,V3S}_fixed.png + _fixmask.png + before/after crops
    $EPY tools/sing/v9w_stills.py upscale    -> media/sing/style/v9w/{S1,V3S}_2k.png (3072x2048)
    $MPY tools/sing/v9w_stills.py metrics    -> media/sing/style/v9w/likeness.json
"""
import json
import os
import sys
import urllib.request

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "media/sing/style/v9w")
SRC = {"S1": "media/sing/style/v8/glow_S1__nbp_1__fixx2.png", "V3S": "media/sing/style/v8/glow_V3S__nbp_1__fixx2__ext.png"}
MATTE = {"S1": "media/sing/style/v8/_matte/glow_S1__nbp_1__fixx2.png",
         "V3S": "media/sing/style/v8/_matte/glow_V3S__nbp_1__fixx2__ext.png"}
PHOTO = {"S1": "media/sing/outpaint/v7/S1_nbp_2_merged.png", "V3S": "media/sing/outpaint/v7/V3S_nbp_5_merged.png"}
OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150,
        136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]


def rd(p):
    return np.asarray(Image.open(os.path.join(ROOT, p)).convert("RGB"), np.float32)


def landmarks(a):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import mouth as MT
    return MT.detect(a.astype(np.uint8), (0, 0, a.shape[1], a.shape[0]))[0]


def protect(I, L, shot):
    import cv2
    h, w = I.shape[:2]
    fh = float(np.linalg.norm(L[10] - L[152]))
    m = np.zeros((h, w), np.uint8)
    hull = cv2.convexHull(L[OVAL].astype(np.int32))
    cv2.fillConvexPoly(m, hull, 1)
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(0.05 * fh) | 1,) * 2))
    # the landmark oval stops mid-forehead: the forehead up to the hairline and the neck down to the collar are skin
    # too. Inside these extensions only skin-bright pixels are protected (dark strands across them stay recolourable).
    c = L[OVAL].mean(0)
    up = L[OVAL].copy()
    top = up[:, 1] < L[1][1]
    up[top] = c + (up[top] - c) * np.array([1.04, 1.45])
    ext = np.zeros((h, w), np.uint8)
    cv2.fillConvexPoly(ext, cv2.convexHull(up.astype(np.int32)), 1)
    jl, jr = L[172], L[397]
    neck = np.array([jl, jr, jr + [-0.05 * fh, 0.75 * fh], jl + [0.05 * fh, 0.75 * fh]], np.int32)
    cv2.fillConvexPoly(ext, neck, 1)
    lum = I @ np.array([0.299, 0.587, 0.114], np.float32)
    m |= (ext.astype(bool) & (lum > 120)).astype(np.uint8)
    for p in ((454,) if shot == "S1" else (234, 454)):                       # ears, just outside the oval (S1: the
        #                                                                       frame-left ear is under hair, and its
        #                                                                       ellipse would shield the orange wash there)
        c = L[p] + np.array([np.sign(L[p][0] - L[1][0]) * 0.05 * fh, 0.05 * fh])
        cv2.ellipse(m, (int(c[0]), int(c[1])), (int(0.07 * fh), int(0.13 * fh)), 0, 0, 360, 1, -1)
    hsv = cv2.cvtColor(I.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.int32)
    H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    pencil = (((H >= 18) & (H <= 34) & (S > 110) & (V > 150)) | (((H >= 150) | (H <= 4)) & (S > 50) & (V > 150))
              | ((H >= 90) & (H <= 120) & (S > 40) & (V > 150)))
    pencil[int(L[10][1]):] = False                                           # pencils sit above the hairline
    if pencil.any():
        n, lab, st, _ = cv2.connectedComponentsWithStats(pencil.astype(np.uint8))
        keep = np.zeros_like(pencil)
        for k in range(1, n):
            if st[k, 4] >= 25:
                keep |= lab == k
        m |= cv2.dilate(keep.astype(np.uint8), np.ones((15, 15), np.uint8))
    if shot == "V3S":                                                        # jacket bands: bright saturated orange
        band = (H >= 4) & (H <= 22) & (S > 110) & (V > 170)
        m |= cv2.dilate(band.astype(np.uint8), np.ones((9, 9), np.uint8))
        m[int(L[152][1] + 0.12 * fh):, :] |= ((V > 175) & (S < 60)).astype(np.uint8)[int(L[152][1] + 0.12 * fh):, :]   # pale jacket
    return m.astype(bool), fh


def fix_one(shot):
    import cv2
    I = rd(SRC[shot])
    a = np.asarray(Image.open(os.path.join(ROOT, MATTE[shot])).convert("L"), np.float32) / 255
    L = landmarks(I)
    prot, fh = protect(I, L, shot)
    hsv = cv2.cvtColor(I.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
    H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    lum = I @ np.array([0.299, 0.587, 0.114], np.float32)
    zone = cv2.dilate((a > 0.05).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41))) > 0
    zone &= ~prot
    zone[int(L[152][1] + (0.05 if shot == "S1" else 0.6) * fh):] = False     # S1: only the head; V3S: hair down to the chest
    warm = np.clip((S - 40) / 40, 0, 1) * ((H >= 4) & (H <= 30))
    w = (warm * zone).astype(np.float32)
    w = cv2.GaussianBlur(w, (0, 0), 1.2)
    paper = np.median(I[(lum > np.percentile(lum, 85)) & (a < 0.02)], axis=0)
    darkhair = np.median(I[(lum < 70) & zone & (a > 0.5)], axis=0) if ((lum < 70) & zone & (a > 0.5)).sum() > 200 else np.array([45, 38, 36], np.float32)
    grey = lum[..., None] / max(float(darkhair.mean()), 1) * darkhair       # her hair tone at the pixel's own luminance
    if shot == "S1":
        light = np.clip((lum - 150) / 40, 0, 1)[..., None]                   # wash on paper -> paper; tinted strand -> dark hair
        # ... except inside the hair mass (the bun): there a light wash pixel is a gap between dark strands, so it goes dark
        mass = cv2.morphologyEx((lum < 95).astype(np.uint8), cv2.MORPH_CLOSE,
                                cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31)))
        mass = cv2.GaussianBlur(mass.astype(np.float32), (0, 0), 3)[..., None]
        light = light * (1 - mass)
        onpaper = np.minimum(paper, paper * (lum[..., None] / float(paper @ np.array([0.299, 0.587, 0.114]))) ** 0.4)
        strand = grey * 0.8
        target = onpaper * light + strand * (1 - light)
    else:
        g = lum[..., None]
        chroma = I - g
        target = g + chroma * 0.25
        mid = np.clip(1 - np.abs(lum - 110) / 80, 0, 1)[..., None]           # darken the mid-tones a little
        target = target * (1 - 0.22 * mid)
    F = I * (1 - w[..., None]) + target * w[..., None]
    os.makedirs(OUT, exist_ok=True)
    Image.fromarray(np.clip(F, 0, 255).astype(np.uint8)).save(os.path.join(OUT, f"{shot}_fixed.png"))
    Image.fromarray((w * 255).astype(np.uint8)).save(os.path.join(OUT, f"{shot}_fixmask.png"))
    # face pixels must be untouched
    fm = np.zeros(I.shape[:2], np.uint8)
    cv2.fillConvexPoly(fm, cv2.convexHull(L[OVAL].astype(np.int32)), 1)
    dface = float(np.abs(F - I)[fm > 0].max())
    x0, y0 = (L[:, 0].min() - 0.9 * fh), (L[:, 1].min() - 0.7 * fh)
    box = tuple(int(v) for v in (max(0, x0), max(0, y0), min(I.shape[1], x0 + 2.4 * fh), min(I.shape[0], y0 + 2.0 * fh)))
    ba = np.hstack([I[box[1]:box[3], box[0]:box[2]], F[box[1]:box[3], box[0]:box[2]]]).astype(np.uint8)
    Image.fromarray(ba).save(os.path.join(OUT, f"{shot}_fix_before_after.jpg"), quality=92)
    print(shot, "recoloured px (w>0.5):", int((w > 0.5).sum()), " max change inside the face oval:", round(dface, 2),
          " paper", np.round(paper).tolist(), " hair", np.round(darkhair).tolist())


def fix(argv):
    for s in argv or ["S1", "V3S"]:
        fix_one(s)


def upscale(argv):
    import torch
    from spandrel import ModelLoader
    path = os.path.expanduser("~/.cache/engrave/RealESRGAN_x4plus.pth")
    if not os.path.exists(path):
        urllib.request.urlretrieve("https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth", path)
    net = ModelLoader().load_from_file(path).to("cuda").eval().half()
    for s in argv or ["S1", "V3S"]:
        I = np.asarray(Image.open(os.path.join(OUT, f"{s}_fixed.png")).convert("RGB"))
        T, P = 384, 32                                    # tiles with a 32 px overlap (the GPU is shared)
        h, w = I.shape[:2]
        Y = np.zeros((h * 4, w * 4, 3), np.float32)
        Wt = np.zeros((h * 4, w * 4, 1), np.float32)
        with torch.no_grad():
            for y0 in range(0, h, T):
                for x0 in range(0, w, T):
                    a0, b0 = max(0, y0 - P), max(0, x0 - P)
                    a1, b1 = min(h, y0 + T + P), min(w, x0 + T + P)
                    x = torch.from_numpy(np.ascontiguousarray(I[a0:a1, b0:b1])).cuda().permute(2, 0, 1)[None].half() / 255
                    t = net(x).float().clamp(0, 1)[0].permute(1, 2, 0).cpu().numpy()
                    ry, rx = np.minimum(np.arange(t.shape[0]), np.arange(t.shape[0])[::-1]), np.minimum(np.arange(t.shape[1]), np.arange(t.shape[1])[::-1])
                    wy = np.clip((ry + 1) / (4 * P), 0, 1) if a0 > 0 or a1 < h else np.ones(t.shape[0])
                    wx = np.clip((rx + 1) / (4 * P), 0, 1) if b0 > 0 or b1 < w else np.ones(t.shape[1])
                    if a0 == 0: wy[:t.shape[0] // 2] = 1
                    if a1 == h: wy[t.shape[0] // 2:] = 1
                    if b0 == 0: wx[:t.shape[1] // 2] = 1
                    if b1 == w: wx[t.shape[1] // 2:] = 1
                    ww = (wy[:, None] * wx[None, :])[..., None].astype(np.float32)
                    Y[a0 * 4:a1 * 4, b0 * 4:b1 * 4] += t * ww
                    Wt[a0 * 4:a1 * 4, b0 * 4:b1 * 4] += ww
                    torch.cuda.empty_cache()
        Y = Y / np.maximum(Wt, 1e-6)
        U = np.asarray(Image.fromarray((Y * 255 + 0.5).clip(0, 255).astype(np.uint8)).resize((w * 2, h * 2), Image.LANCZOS))
        # ESRGAN alone smooths the paint grain on the skin (a beautifying drift); half of a plain Lanczos 2x keeps it
        Lz = np.asarray(Image.fromarray(I).resize((w * 2, h * 2), Image.LANCZOS), np.float32)
        U = np.clip(0.5 * U.astype(np.float32) + 0.5 * Lz + 0.5, 0, 255).astype(np.uint8)
        Image.fromarray(U).save(os.path.join(OUT, f"{s}_2k.png"))
        print(s, "->", U.shape)


def measures(L):
    d = lambda a, b: float(np.linalg.norm(L[a] - L[b]))  # noqa: E731
    io, fw, fh = d(33, 263), d(234, 454), d(10, 152)
    return dict(io_fw=io / fw, fw_fh=fw / fh, eye_w=(d(33, 133) + d(362, 263)) / 2 / io,
                eye_h=(d(159, 145) + d(386, 374)) / 2 / ((d(33, 133) + d(362, 263)) / 2), jaw=d(172, 397) / fw,
                nose=d(98, 327) / io, mouth=d(61, 291) / io, lower=d(1, 152) / fh)


def nme(A, B):
    import cv2
    M, _ = cv2.estimateAffinePartial2D(A.astype(np.float32), B.astype(np.float32))
    Aw = A @ M[:, :2].T + M[:, 2]
    return float(np.linalg.norm(Aw - B, axis=1).mean() / np.linalg.norm(B[33] - B[263]) * 100)


def metrics(argv):
    out = {}
    for s in argv or ["S1", "V3S"]:
        Lp = landmarks(rd(PHOTO[s]))
        mp = measures(Lp)
        for tag, p in (("v8_still", SRC[s]), ("fixed", f"media/sing/style/v9w/{s}_fixed.png"), ("2k", f"media/sing/style/v9w/{s}_2k.png")):
            if not os.path.exists(os.path.join(ROOT, p)):
                continue
            L = landmarks(rd(p))
            m = measures(L)
            row = {"nme_pct": round(nme(L, Lp), 2), **{k: round((m[k] / mp[k] - 1) * 100, 1) for k in m}}
            out[f"{s}:{tag}"] = row
            print(f"{s:4s} {tag:9s}", json.dumps(row))
    json.dump(out, open(os.path.join(OUT, "likeness.json"), "w"), indent=1)


if __name__ == "__main__":
    {"fix": fix, "upscale": upscale, "metrics": metrics}[sys.argv[1]](sys.argv[2:])
