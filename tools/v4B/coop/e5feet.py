#!/usr/bin/env python3
"""E5 fix, v6 (Jade: "2:03 - Banach-Tarski pointing scene: ethereal gold Jade's butt is opaque for a split second and
protagonist Jade's sneaker is partly erased"). Two faults in the splitpair.py split of media/shots/B_slide_point_b:

  * take frames 19-39: the live (protagonist) matte holds the gold ghost's left leg (hip, thigh, knee, shin and on the
    early frames her sneaker), so the `jade` layer painted it opaque in navy over the ghost. Hand-keyed polygons
    (source px, interpolated between keys) move it: it is cut out of the live matte and added to the ghost matte
    (only where BiRefNet sees a figure, so the slide's shadow strokes stay out).
  * frames 19-104: the colour-gated jmatte that the live matte is cut from drops her pale sneaker soles (and a patch of
    her trouser leg on frames 45-49 and 92-95), so the clean/cover patches showed through. BiRefNet on a crop round her legs puts
    them back: only pixels that touch the live matte, are not ghost, lie in the bottom 100 px of her (the feet), or in
    the trouser boxes on 44-50 and 90-97.

    tools/engrave/.venv/bin/python tools/v4B/coop/e5feet.py [--check=sheet.jpg]
    -> media/shots/C_coop/e5_arm/live_v6/%05d.png + matte.mp4    (the jade layer's matte)
       media/shots/C_coop/e5_arm/ghost_matte_v6/%05d.png       (then ghostseq.py rebakes ghost_slideptb_v6_{rgb,alpha})
Inputs are left untouched (take_1_live/, e5_arm/ghost_matte/).
"""
import os
import shutil
import subprocess
import sys

import cv2
import numpy as np
import torch

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/engrave"))
from matte import get_birefnet  # noqa: E402

FF = os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg")
TK = os.path.join(ROOT, "media/shots/B_slide_point_b")
E5 = os.path.join(ROOT, "media/shots/C_coop/e5_arm")
LIVE_OUT, GH_OUT = os.path.join(E5, "live_v6"), os.path.join(E5, "ghost_matte_v6")
BOX = (900, 380, 1400, 880)                 # BiRefNet crop: both girls' legs on every frame the shot uses (21-104)
F0, F1 = 19, 104                            # frames touched (the shot plays take frames 21.6-104)
HEM, HEM_Y, HEM_W, HEM_GAP, HEM_DARK = (36, 92), (480, 760), 45, 40, 115  # v6b trouser-edge strip: frames, rows, max width, row gap, dark
TROUSER = [(44, 50, (1000, 360, 1170, 600)), (90, 97, (1150, 400, 1350, 640))]   # trouser holes: frames, box
# the ghost's left leg inside the live matte, keyed on the take (1920x1080 px); 7 vertices each, same order
# (top-left, top-right, right, bottom-right, bottom, bottom-left, left). The left edge runs between her thigh and the
# protagonist's sneaker toe; the right side reaches well into the ghost matte, so no live sliver is left inside her.
LEG = {
    19: [(1116, 400), (1215, 380), (1340, 700), (1320, 790), (1150, 780), (1120, 700), (1116, 560)],
    20: [(1116, 400), (1215, 380), (1340, 700), (1320, 790), (1150, 780), (1120, 700), (1116, 560)],
    23: [(1140, 420), (1230, 400), (1350, 710), (1330, 800), (1180, 790), (1150, 710), (1140, 560)],
    26: [(1162, 440), (1260, 420), (1370, 700), (1380, 790), (1240, 790), (1190, 700), (1163, 570)],
    29: [(1183, 470), (1280, 460), (1340, 700), (1320, 780), (1220, 770), (1210, 700), (1184, 600)],
    32: [(1204, 480), (1300, 470), (1350, 710), (1320, 760), (1250, 750), (1240, 700), (1206, 610)],
    35: [(1227, 500), (1330, 490), (1360, 720), (1320, 760), (1260, 750), (1240, 705), (1227, 640)],
    38: [(1252, 545), (1340, 540), (1360, 720), (1320, 740), (1285, 730), (1270, 700), (1252, 620)],
    39: [(1252, 545), (1340, 540), (1360, 720), (1320, 740), (1285, 730), (1270, 700), (1252, 620)],
}
ell = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def leg_poly(i):
    ks = sorted(LEG)
    if i < ks[0] or i > ks[-1]:
        return None
    a = max(k for k in ks if k <= i)
    b = min(k for k in ks if k >= i)
    u = 0 if a == b else (i - a) / (b - a)
    return np.round((1 - u) * np.array(LEG[a], float) + u * np.array(LEG[b], float)).astype(np.int32)


def touching(cand, m, r=3):
    """components of cand that touch m"""
    md = cv2.dilate(m.astype(np.uint8), ell(r)) > 0
    n, lab = cv2.connectedComponents(cand.astype(np.uint8))
    keep = np.zeros_like(cand)
    for k in range(1, n):
        c = lab == k
        if (c & md).any():
            keep |= c
    return keep


def main(check=None):
    os.makedirs(LIVE_OUT, exist_ok=True)
    os.makedirs(GH_OUT, exist_ok=True)
    net = get_birefnet()
    cap = cv2.VideoCapture(os.path.join(TK, "take_1.mp4"))
    x0, y0, x1, y1 = BOX
    sheet, log = [], []
    i = 0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        lp, gp = os.path.join(TK, "take_1_live", f"{i:05d}.png"), os.path.join(E5, "ghost_matte", f"{i:05d}.png")
        if not os.path.exists(lp):
            break
        if not F0 <= i <= F1:
            shutil.copy(lp, os.path.join(LIVE_OUT, f"{i:05d}.png"))
            shutil.copy(gp, os.path.join(GH_OUT, f"{i:05d}.png"))
            i += 1
            continue
        f = cv2.resize(f, (1920, 1080), interpolation=cv2.INTER_LANCZOS4)
        lv = cv2.imread(lp, 0)
        g = cv2.imread(gp, 0)
        crop = cv2.cvtColor(f[y0:y1, x0:x1], cv2.COLOR_BGR2RGB)
        t = torch.from_numpy(crop).cuda().permute(2, 0, 1)[None].float() / 255
        p = np.zeros(lv.shape, np.float32)
        p[y0:y1, x0:x1] = net(t)[0, 0].cpu().numpy()
        fig = p > 0.5
        # 1. the ghost's leg: out of the live matte, into the ghost matte
        P = np.zeros(lv.shape, np.uint8)
        poly = leg_poly(i)
        if poly is not None:
            cv2.fillPoly(P, [poly], 1)
        P = P > 0
        moved = P & (lv >= 100)
        lv2 = np.where(P, 0, lv)
        if poly is not None:        # thin slivers of her outline left just outside the polygon: an opening, near it only
            L = lv2 >= 100
            band = (cv2.dilate(P.astype(np.uint8), ell(12)) > 0) & ~P
            thin = band & L & ~(cv2.morphologyEx(L.astype(np.uint8), cv2.MORPH_OPEN, ell(3)) > 0)
            # and the bare plate (cover, shadow strokes) the split gave her between her toe and the ghost's leg
            thin |= (cv2.dilate(P.astype(np.uint8), ell(40)) > 0) & ~P & L & (p < 0.2)
            lv2[thin] = 0
            moved |= thin
        gadd = P & fig & (g <= 127)
        g2 = np.maximum(g, (gadd * 255).astype(np.uint8))
        # 1b. (v6b, Jade: "gold ghost's edge of pants (near protagonist Jade's sneaker) is opaque for a couple frames")
        # after the leg, a strip of her left trouser edge (up to ~40 px, from her belt to the knee) stays in the live
        # matte. Row by row: from the ghost matte's left edge, walk left over dark (navy) live pixels, at most HEM_W px;
        # the walk stops at the white cover or her pale sneaker. Those, and dark live pixels just inside the ghost
        # matte, go to the ghost.
        if HEM[0] <= i <= HEM[1]:
            dark = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) < HEM_DARK
            G, L = g2 > 127, lv2 >= 100
            n, lab, st, _ = cv2.connectedComponentsWithStats(G.astype(np.uint8))
            body = lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])) if n > 1 else G
            hem = np.zeros_like(L)
            XG, D = {}, {}               # per row: ghost edge, strip width (None where the walk ran into her own navy)
            for y in range(*HEM_Y):
                xs = np.nonzero(body[y, x0:x1])[0]
                if not len(xs):
                    continue
                xg = XG[y] = x0 + xs[0]
                x = xg - 1
                while x > xg - 1 - HEM_W and L[y, x] and dark[y, x]:
                    x -= 1
                D[y] = None if x == xg - 1 - HEM_W else xg - 1 - x
            # rows where the walk ran on (her toe's dark sole and outline touch the strip, or her own trousers): take
            # the strip width from the nearest clean strip rows above and below, if both are within HEM_GAP rows
            good = sorted(y for y, d in D.items() if d)
            for y, d in D.items():
                if d is None and good:
                    a = [v for v in good if y - HEM_GAP <= v < y]
                    b = [v for v in good if y < v <= y + HEM_GAP]
                    if a and b:
                        a, b = a[-1], b[0]
                        D[y] = round(D[a] + (D[b] - D[a]) * (y - a) / (b - a))
            for y, d in D.items():
                if d:
                    xg = XG[y]
                    hem[y, xg - d:xg] = L[y, xg - d:xg] & dark[y, xg - d:xg]
                    hem[y, xg:xg + HEM_W] = L[y, xg:xg + HEM_W] & G[y, xg:xg + HEM_W] & dark[y, xg:xg + HEM_W]
            lv2[hem] = 0
            g2[hem] = 255
            moved |= hem
        # 2. her sneaker soles (and the trouser hole): figure pixels next to the live matte that are not ghost
        L = lv2 >= 100
        gd = cv2.dilate((g2 > 127).astype(np.uint8), ell(4)) > 0
        cand = fig & ~L & ~gd & ~P
        ys = np.nonzero((L & fig)[:, x0:x1].any(1))[0]          # her lowest figure pixel (not a stray lobe of plate)
        feet = np.zeros_like(cand)
        if len(ys):
            feet[max(0, ys.max() - 100):, :] = True
        roi = feet.copy()
        for a, b, bx in TROUSER:
            if a <= i <= b:
                roi[bx[1]:bx[3], bx[0]:bx[2]] = True
        add = touching(cand & roi, L)
        lv2 = np.maximum(lv2, np.where(add, np.clip(p * 255, 0, 255), 0).astype(np.uint8))
        cv2.imwrite(os.path.join(LIVE_OUT, f"{i:05d}.png"), lv2)
        cv2.imwrite(os.path.join(GH_OUT, f"{i:05d}.png"), g2)
        log.append((i, int(moved.sum()), int(gadd.sum()), int(add.sum())))
        if check and i % 3 == 0 and i <= 99:
            v = f.copy()
            v[moved] = (0.4 * v[moved] + [150, 0, 150]).astype(np.uint8)
            v[add] = (0.4 * v[add] + [0, 150, 0]).astype(np.uint8)
            for m, col in ((lv2 >= 100, (0, 0, 255)), (g2 > 127, (255, 120, 0))):
                cs, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
                cv2.drawContours(v, cs, -1, col, 1)
            c = cv2.resize(v[y0:y1, x0:x1], (250, 250))
            cv2.putText(c, f"f{i}", (4, 18), 0, 0.6, (0, 0, 255), 2)
            sheet.append(c)
        i += 1
    for d in (LIVE_OUT,):
        subprocess.run([FF, "-y", "-loglevel", "error", "-framerate", "24", "-i", os.path.join(d, "%05d.png"), "-c:v", "libx264",
                        "-pix_fmt", "yuv420p", "-crf", "12", os.path.join(d, "matte.mp4")], check=True)
    for r in log:
        print("f%d leg->ghost %d (ghost +%d)  soles/trouser +%d" % r)
    if check:
        while len(sheet) % 8:
            sheet.append(np.zeros_like(sheet[0]))
        cv2.imwrite(check, np.vstack([np.hstack(sheet[k:k + 8]) for k in range(0, len(sheet), 8)]), [cv2.IMWRITE_JPEG_QUALITY, 85])


if __name__ == "__main__":
    o = {x[2:].partition("=")[0]: x[2:].partition("=")[2] for x in sys.argv[1:] if x.startswith("--")}
    main(o.get("check"))
