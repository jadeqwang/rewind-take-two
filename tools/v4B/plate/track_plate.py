#!/usr/bin/env python3
"""Track the agents' sedan front plate in D3's wing mirror (v4 note 0:26, plate reads TVA 1729).

    tools/engrave/.venv/bin/python tools/v4B/plate/track_plate.py

The raw take (media/shots/D3/take_2.mp4, 1280x720) is tracked, not the engraved one: the engraving's screen-space
line texture does not move with the car. Passing streetlights swing the car between unlit and fully lit, so matching
is done on gradient magnitude (normalised cross-correlation), per frame against a lit reference frame AND a dark one
(the better score wins), for two patches: the whole front (grille, bumper, plate) and the plate alone. The car keeps its distance, so the
track is a translation of the reference plate rectangle (it moves about +-1 px at 720p: a slow bob).
Output: media/shots/D3/track_plate_v4.json {"keys": [[layer_t, [TLx,TLy,TRx,TRy,BRx,BRy,BLx,BLy]], ...]} in the
engine's 1920x1080 design space (video drawn fit 'cover', same mapping as tools/sectionA/track_quad.py), plus
"light": per-frame 0..1 brightness of the take's own plate (to dim the drawn plate with the passing lights), and
track_plate_v4.jpg, the quad drawn on a contact sheet of the ENGRAVED take.
"""
import json
import os
import sys

import cv2
import numpy as np

ROOT = "/home/jade/Documents/rewind-take-two"
RAW = os.path.join(ROOT, "media/shots/D3/take_2.mp4")
ENG = os.path.join(ROOT, "media/shots/D3/take_2_engraved.mp4")
OUT = os.path.join(ROOT, "media/shots/D3/track_plate_v4.json")
REF_LIT, REF_DARK = 28, 49
SEARCH = 14      # px (720p) search radius round the reference position
UP = 4           # sub-pixel: correlation surface upsampled UP x


def read(path):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    out = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        out.append(f)
    return out, fps


def grad(g):
    g = cv2.GaussianBlur(g.astype(np.float32), (0, 0), 1.0)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(g, cv2.CV_32F, 0, 1)
    m = np.sqrt(gx * gx + gy * gy)
    return np.log1p(m)   # compress: lit edges are 10x stronger than unlit ones


def plate_rect(gray):
    """The lit plate's rectangle in the reference frame: the bright blob nearest the expected position."""
    x0, y0, x1, y1 = 895, 335, 985, 370
    sub = gray[y0:y1, x0:x1]
    th = (sub > 0.5 * sub.max()).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(th)
    k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    x, y, w, h = st[k, :4]
    return np.array([x0 + x, y0 + y, x0 + x + w, y0 + y + h], float)


def match(img, tpl, box):
    x0, y0, x1, y1 = box
    sx0, sy0 = x0 - SEARCH, y0 - SEARCH
    win = img[sy0:y1 + SEARCH, sx0:x1 + SEARCH]
    r = cv2.matchTemplate(win, tpl, cv2.TM_CCOEFF_NORMED)
    r = cv2.resize(r, None, fx=UP, fy=UP, interpolation=cv2.INTER_CUBIC)
    _, mv, _, ml = cv2.minMaxLoc(r)
    # resize maps source pixel centre i to (i + .5) * UP - .5
    dx = (ml[0] + 0.5) / UP - 0.5 - SEARCH
    dy = (ml[1] + 0.5) / UP - 0.5 - SEARCH
    return mv, dx, dy


def main():
    raw, fps = read(RAW)
    gray = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in raw]
    G = [grad(g) for g in gray]
    h, w = gray[0].shape
    pr = plate_rect(gray[REF_LIT])
    print("plate rect in raw frame %d (720p px):" % REF_LIT, pr, "size", pr[2] - pr[0], pr[3] - pr[1])
    # patches (720p px, reference frames). The headlights are no use (they bloom when lit and the match jumps);
    # the grille + bumper + plate block and the plate alone both hold through the light changes.
    boxes = {"front": (878, 303, 976, 368), "plate": (int(pr[0]) - 10, int(pr[1]) - 8, int(pr[2]) + 10, int(pr[3]) + 8)}
    names = list(boxes)
    n = len(raw)
    m = np.zeros((n, len(names), 2, 3))   # frame, patch, template (lit, dark), (score, dx, dy)
    for i in range(n):
        for j, k in enumerate(names):
            b = boxes[k]
            for r, ref in enumerate((REF_LIT, REF_DARK)):
                m[i, j, r] = match(G[i], G[ref][b[1]:b[3], b[0]:b[2]], b)
    # the dark template's bias against the lit one: median difference over the frames both match well (twilight)
    off = np.zeros((n, len(names), 2))
    score = np.zeros((n, len(names)))
    for j, k in enumerate(names):
        both = (m[:, j, 0, 0] > 0.45) & (m[:, j, 1, 0] > 0.45) & (np.abs(m[:, j, :, 1:]).max((1, 2)) < 4)
        bias = np.median(m[both, j, 1, 1:] - m[both, j, 0, 1:], axis=0) if both.sum() >= 4 else np.zeros(2)
        print("%s: dark-template bias (%.2f, %.2f) px from %d frames" % (k, bias[0], bias[1], both.sum()))
        wl, wd = m[:, j, 0, 0].clip(0, 1) ** 6, m[:, j, 1, 0].clip(0, 1) ** 6
        ok_l, ok_d = np.abs(m[:, j, 0, 1:]).max(1) < 4, np.abs(m[:, j, 1, 1:]).max(1) < 4   # a jump = a false match
        wl, wd = wl * ok_l, wd * ok_d
        off[:, j] = (wl[:, None] * m[:, j, 0, 1:] + wd[:, None] * (m[:, j, 1, 1:] - bias)) / (wl + wd + 1e-9)[:, None]
        score[:, j] = np.maximum(m[:, j, 0, 0] * ok_l, m[:, j, 1, 0] * ok_d)
    print("front vs plate patch disagreement (px 720p): mean %.2f max %.2f" % (
        np.abs(off[:, 0] - off[:, 1]).mean(), np.abs(off[:, 0] - off[:, 1]).max()))
    wgt = score ** 2
    d = (off * wgt[:, :, None]).sum(1) / wgt.sum(1)[:, None]     # translation only: the car keeps its distance
    quad0 = np.array([[pr[0], pr[1]], [pr[2], pr[1]], [pr[2], pr[3]], [pr[0], pr[3]]])
    quads = quad0[None] + d[:, None, :]
    par = np.concatenate([d, np.ones((n, 1)), np.zeros((n, 1))], 1)
    print("dx range %.2f..%.2f  dy %.2f..%.2f px (720p)  min score %.2f" % (
        d[:, 0].min(), d[:, 0].max(), d[:, 1].min(), d[:, 1].max(), score.max(1).min()))
    # 5-frame triangular smooth (Seedance repeats frames; sub-pixel jitter on a 44 px plate reads as shimmer)
    k = np.array([1, 2, 3, 2, 1], float)
    k /= k.sum()
    pad = np.concatenate([quads[:1]] * 2 + [quads] + [quads[-1:]] * 2)
    sm = sum(k[j] * pad[j:j + n] for j in range(5))
    # light on the plate: mean luma of the take's plate rectangle, normalised over the take
    lum = np.array([gray[i][int(round(sm[i, 0, 1])):int(round(sm[i, 2, 1])) + 1,
                            int(round(sm[i, 0, 0])):int(round(sm[i, 1, 0])) + 1].mean() for i in range(n)])
    light = (lum - lum.min()) / max(1e-6, lum.max() - lum.min())
    # 720p px -> design px (fit 'cover' of a 16:9 video in 1920x1080)
    s = max(1920 / w, 1080 / h)
    ox, oy = (1920 - w * s) / 2, (1080 - h * s) / 2
    keys = [[round(i / fps, 4), [round(float(v), 2) for v in (sm[i] * s + [ox, oy]).reshape(-1)]] for i in range(n)]
    json.dump({"video": "media/shots/D3/take_2.mp4", "fps": fps, "space": "design 1920x1080, fit cover",
               "what": "front licence plate of the sedan in the wing mirror, TL TR BR BL, the take's own (small) plate",
               "ref_frame": REF_LIT, "keys": keys, "light": [round(float(v), 3) for v in light],
               "raw": {"dx_dy_scale_rot": [[round(float(v), 4) for v in p] for p in par],
                       "score": [[round(float(v), 3) for v in r] for r in score], "patches": names}},
              open(OUT, "w"))
    print("wrote", OUT, len(keys), "keys; light", np.round(light[::6], 2))
    # contact sheet on the engraved take: 3x crop round the car, quad in orange
    eng, _ = read(ENG)
    idx = list(range(0, 78, 6))
    tiles = []
    c = (sm[REF_LIT].mean(0) * s + [ox, oy])
    X0, Y0, X1, Y1 = int(c[0] - 150), int(c[1] - 110), int(c[0] + 150), int(c[1] + 60)
    for i in idx:
        t = cv2.resize(eng[i][Y0:Y1, X0:X1], None, fx=3, fy=3, interpolation=cv2.INTER_LANCZOS4)
        q = ((sm[i] * s + [ox, oy]) - [X0, Y0]) * 3
        cv2.polylines(t, [np.round(q).astype(np.int32)], True, (36, 138, 240), 1, cv2.LINE_AA)
        cv2.putText(t, "f%d %.2fs L%.2f" % (i, i / fps, light[i]), (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (36, 138, 240), 2)
        tiles.append(t)
    while len(tiles) % 4:
        tiles.append(np.zeros_like(tiles[0]))
    sheet = np.vstack([np.hstack(tiles[j:j + 4]) for j in range(0, len(tiles), 4)])
    cv2.imwrite(os.path.splitext(OUT)[0] + ".jpg", sheet, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print("wrote", os.path.splitext(OUT)[0] + ".jpg")


if __name__ == "__main__":
    sys.exit(main())
