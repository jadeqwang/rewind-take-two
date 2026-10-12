"""v5-build: prepare the post-credits assets in media/shots/PC/ from the stills in media/shots/PC/gen/ (gen_build.py).

    tools/engrave/.venv/bin/python tools/sectionF/coda/prep_pc.py [plates] [sprites] [door]

plates : lobby_tall -> de-red -> Real-ESRGAN x2 -> lobby.jpg (4800x3584); doorway / door_color -> de-red -> doorway.jpg, door.jpg
sprites: committee_a/b sheets (flat grey ground) -> 8 RGBA figures (feet on the bottom edge); the protagonist (v5-coda's
         jade.png); 8-bit Jade re-gridded to a 46-row pixel sprite with a 14-colour palette (drawn unsmoothed); five
         ghost Jades (the protagonist tinted in the film's ghost palette, translucent, with a glow). -> sprites/ + info.json
door   : the door leaf, its glass alpha, the bell, the glove (see door section)
"""
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/engrave"))
sys.path.insert(0, os.path.join(ROOT, "tools/sectionF"))
G = os.path.join(ROOT, "media/shots/PC/gen")
PC = os.path.join(ROOT, "media/shots/PC")
SP = os.path.join(PC, "sprites")


def load(p):
    return np.asarray(Image.open(p).convert("RGB"))


def dered(rgb):
    import dered as D
    a = D.frac(rgb)
    out = D.fix(rgb, "orange")
    print(f"  red {a:.4f} -> {D.frac(out):.4f}")
    return out


def plates():
    from upscale import Upscaler
    im = dered(load(os.path.join(G, "lobby_tall.jpg")))
    h, w = im.shape[:2]
    up = dered(Upscaler("animevideov3", w * 2, h * 2)(im))   # again: the upscale re-saturates the dark maroon ink lines
    Image.fromarray(up).save(os.path.join(PC, "lobby.jpg"), quality=93, subsampling=0)
    for src, dst in (("doorway.jpg", "doorway.jpg"), ("../../../reviews/v5/plans/coda/door_color.jpg", "door.jpg")):
        Image.fromarray(dered(dered(load(os.path.join(G, src))))).save(os.path.join(PC, dst), quality=95, subsampling=0)
    print("plates done", up.shape)


def key_figures(rgb, n, bg=None, thr=22):
    """Split a flat-ground sheet into n figures. fg = not (ground-coloured and connected to the border); enclosed
    ground-coloured pockets bigger than 300 px are ground too. Returns [(rgba crop)] left to right."""
    if bg is None:
        bg = np.median(np.concatenate([rgb[:20].reshape(-1, 3), rgb[-20:].reshape(-1, 3)]), axis=0)
    d = np.abs(rgb.astype(np.float32) - bg).max(2)
    low = d < thr
    lab, k = ndimage.label(low)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, k + 1))
    flat = ndimage.mean(d, lab, range(1, k + 1))
    ground = np.isin(lab, [i for i in range(1, k + 1) if i in border or (sizes[i - 1] > 300 and flat[i - 1] < 8)])
    fg = ~ground
    fg = ndimage.binary_opening(fg, iterations=1)
    # keep big components only
    lab2, k2 = ndimage.label(fg)
    sz = ndimage.sum(fg, lab2, range(1, k2 + 1))
    fg = np.isin(lab2, [i + 1 for i, s in enumerate(sz) if s > 2000])
    a = cv2.GaussianBlur(cv2.erode(fg.astype(np.uint8) * 255, np.ones((3, 3), np.uint8)), (3, 3), 0)
    cols = fg.any(0)
    # column runs = figures
    runs, x = [], 0
    while x < len(cols):
        if cols[x]:
            x0 = x
            while x < len(cols) and cols[x]:
                x += 1
            runs.append((x0, x))
        x += 1
    runs = sorted(runs, key=lambda r: r[1] - r[0], reverse=True)[:n]
    out = []
    for x0, x1 in sorted(runs):
        rows = np.where(fg[:, x0:x1].any(1))[0]
        y0, y1 = rows[0], rows[-1] + 1
        crop = np.dstack([rgb[y0:y1, x0:x1], a[y0:y1, x0:x1]])
        out.append(crop)
    return out


def save(name, rgba, info):
    Image.fromarray(rgba).save(os.path.join(SP, name + ".png"))
    info[name] = [int(rgba.shape[1]), int(rgba.shape[0])]
    print("  sprite", name, rgba.shape[1], rgba.shape[0])


def ghost(rgba, col, alpha=0.78):
    """the film's colour ghost: her drawing tinted toward one Kandinsky colour, translucent, with a soft glow"""
    c = np.array([int(col[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255
    rgb = rgba[..., :3].astype(np.float32) / 255
    lum = rgb @ np.array([0.3, 0.59, 0.11], np.float32)
    tint = np.clip(c * (0.45 + 0.75 * lum[..., None]) + 0.12 * lum[..., None], 0, 1)
    a = rgba[..., 3].astype(np.float32) / 255
    pad = 40
    A = np.pad(a, pad)
    T = np.pad(tint, ((pad, pad), (pad, pad), (0, 0)))
    glow = cv2.GaussianBlur(A, (0, 0), 14)
    lit = np.clip(c * 1.15 + 0.15, 0, 1)
    out_a = np.clip(A * alpha + glow * 0.55 * (1 - A), 0, 1)
    out_rgb = (T * (A * alpha)[..., None] + lit * (glow * 0.55 * (1 - A))[..., None]) / np.maximum(out_a, 1e-4)[..., None]
    out = np.dstack([np.clip(out_rgb * 255, 0, 255), out_a * 255]).astype(np.uint8)
    return out[pad:pad + a.shape[0]]          # same height as her (feet on the bottom edge); the glow widens it only


def pixel_sprite(rows=46, colors=14):
    im = load(os.path.join(G, "pixel.jpg"))
    H, W = im.shape[:2]
    c = im[:, int(W * 0.31):int(W * 0.67)]                   # the sprite only (soft ghosts at the sides)
    fig = key_figures(c, 1, thr=26)[0]
    h, w = fig.shape[:2]
    cols = max(1, round(w * rows / h))
    small = cv2.resize(fig[..., :3], (cols, rows), interpolation=cv2.INTER_AREA)
    al = cv2.resize(fig[..., 3], (cols, rows), interpolation=cv2.INTER_AREA)
    pal = Image.fromarray(small).quantize(colors, method=Image.Quantize.MEDIANCUT).convert("RGB")
    rgba = np.dstack([np.asarray(pal), np.where(al > 110, 255, 0).astype(np.uint8)])
    return rgba


def sprites():
    os.makedirs(SP, exist_ok=True)
    info = {}
    names = {"committee_a": ["glasses", "teal", "purple", "braids"],
             "committee_b": ["plain", "sleepy", "rainbow", "mint"]}
    for sheet, ns in names.items():
        figs = key_figures(load(os.path.join(G, sheet + ".jpg")), 4)
        assert len(figs) == 4, (sheet, len(figs))
        for n, f in zip(ns, figs):
            save(n, f, info)
    jade = np.asarray(Image.open(os.path.join(ROOT, "media/reviews/v5/plans/coda/sprites/jade.png")).convert("RGBA"))
    save("jade", jade, info)
    for k, col in enumerate(["#F08A24", "#8DB8E8", "#C9A227", "#C23B8E", "#3FA55B", "#8E5CC8", "#2BA59A"]):
        save(f"ghost{k}", ghost(jade, col), info)
    save("pixel", pixel_sprite(), info)
    json.dump(info, open(os.path.join(SP, "info.json"), "w"), indent=1)


# ---------------------------------------------------------------- the door (PC1), for tools/sectionF/modules/hilbert_door.js
# Design px = door.jpg cover-fitted to 1920x1080 (2752x1536 -> scale 1080/1536, 7.5 px cropped each side).
LEAF = (560, 150, 1362, 1080)          # the door leaf (hinges on its left edge x 560, handle on the right stile)
GLASS = (668, 248, 1252, 1080)         # its glass pane
EMBLEM = (735, 405, 1185, 750)         # the gold HILBERT HOTEL crest on the glass (stays opaque)
BELL = (1140, 246, 1250, 410)          # the spring bell (hangs inside, behind the glass: it stays in the doorway)
HANDLE = (1348, 816)                   # where the glove grips the bar


def birefnet_alpha(rgb):
    import torch
    from matte import get_birefnet
    x = torch.from_numpy(rgb).cuda().permute(2, 0, 1)[None].float() / 255
    return (get_birefnet()(x)[0, 0].clamp(0, 1).cpu().numpy() * 255).astype(np.uint8)


def door():
    im = Image.open(os.path.join(PC, "door.jpg")).convert("RGB")
    s = 1080 / im.height
    W = round(im.width * s)
    ox = (W - 1920) / 2
    D = np.asarray(im.resize((W, 1080), Image.LANCZOS).crop((round(ox), 0, round(ox) + 1920, 1080)))
    # ---- leaf (design px, 1:1), alpha: wood 1, glass 0.55, crest 1; the bell inpainted out of the glass
    x0, y0, x1, y1 = LEAF
    rgb = D.copy()
    bm = np.zeros(D.shape[:2], np.uint8)
    bx0, by0, bx1, by1 = BELL
    bm[by0:by1, bx0:bx1] = 255
    rgb = cv2.inpaint(rgb, bm, 9, cv2.INPAINT_TELEA)
    rgb = np.where(bm[..., None] > 0, cv2.GaussianBlur(rgb, (0, 0), 6), rgb)
    a = np.ones(D.shape[:2], np.float32)
    gx0, gy0, gx1, gy1 = GLASS
    a[gy0:gy1, gx0:gx1] = 0.55
    lum = cv2.cvtColor(D, cv2.COLOR_RGB2GRAY).astype(np.float32)
    hp_ = np.abs(lum - cv2.GaussianBlur(lum, (0, 0), 6))
    ex0, ey0, ex1, ey1 = EMBLEM
    crest = np.zeros_like(a)
    crest[ey0:ey1, ex0:ex1] = (hp_[ey0:ey1, ex0:ex1] > 22).astype(np.float32)   # line work only (paper grain is < 15)
    crest = cv2.GaussianBlur(cv2.dilate(crest, np.ones((5, 5), np.uint8)), (0, 0), 1.5)
    a = np.maximum(a, np.clip(crest * 1.3, 0, 1))
    leaf = np.dstack([rgb, (a * 255).astype(np.uint8)])[y0:y1, x0:x1]
    Image.fromarray(leaf).save(os.path.join(PC, "door_leaf.png"))
    # ---- the frame with the leaf's opening cut out
    fr = np.dstack([D, np.full(D.shape[:2], 255, np.uint8)])
    fr[y0:y1, x0:x1, 3] = 0
    Image.fromarray(fr).save(os.path.join(PC, "door_frame.png"))
    # ---- the bell + spring (its own alpha by BiRefNet on a padded crop)
    pad = 30
    c = D[by0 - pad:by1 + pad, bx0 - pad:bx1 + pad]
    al = birefnet_alpha(np.ascontiguousarray(c))
    Image.fromarray(np.dstack([c, al])).save(os.path.join(PC, "door_bell.png"))
    # ---- the glove from Seedance take 1 (t = 1.25 s: the fist round the bar), scaled to design px
    import av
    fr_ = None
    with av.open(os.path.join(ROOT, "media/gen/v5_coda_door/take_1_dered.mp4")) as cnt:
        for f in cnt.decode(video=0):
            if f.time >= 1.25:
                fr_ = f.to_ndarray(format="rgb24")
                break
    crop = fr_[300:720, 820:1280]                    # hand + sleeve (the sleeve runs off the top-right)
    al = birefnet_alpha(np.ascontiguousarray(crop))
    # keep the largest component (the arm), drop bits of door
    m = al > 128
    lab, k = ndimage.label(m)
    if k > 1:
        big = 1 + int(np.argmax(ndimage.sum(m, lab, range(1, k + 1))))
        al = (al * ndimage.binary_dilation(lab == big, iterations=3)).astype(np.uint8)
    sc = 345 / 225                                    # take px -> design px (the bar is 225 px long in the take)
    g = np.dstack([crop, al])
    g = np.asarray(Image.fromarray(g).resize((round(crop.shape[1] * sc), round(crop.shape[0] * sc)), Image.LANCZOS)).copy()
    # the arm only (BiRefNet also kept a piece of the stained glass behind the cuff and the bar under the fist)
    poly = np.zeros(g.shape[:2], np.uint8)
    cv2.fillPoly(poly, [np.array([(66, 288), (180, 282), (255, 312), (300, 306), (590, 212), (720, 130), (720, 405),
                                  (520, 446), (322, 478), (290, 456), (250, 452), (150, 462), (88, 458), (64, 400)], np.int32)], 255)
    poly = cv2.GaussianBlur(poly, (0, 0), 1.5).astype(np.float32) / 255
    g[..., 3] = (g[..., 3] * poly).astype(np.uint8)
    Image.fromarray(g).save(os.path.join(PC, "glove.png"))
    grip = [round((892 - 820) * sc, 1), round((540 - 300) * sc, 1)]     # the bar at the fist, in sprite px
    json.dump({"leaf": LEAF, "glass": GLASS, "bell": BELL, "bellTop": [1195, 252], "handle": HANDLE, "hinge": LEAF[0],
               "glove": {"grip": grip, "split": round((960 - 820) * sc, 1), "size": [g.shape[1], g.shape[0]]}},
              open(os.path.join(PC, "door_geom.json"), "w"), indent=1)
    print("door done; glove", g.shape, "grip", grip)


if __name__ == "__main__":
    what = sys.argv[1:] or ["plates", "sprites"]
    os.makedirs(PC, exist_ok=True)
    for w in what:
        globals()[w]()
