#!/usr/bin/env python3
"""Singing Jade (v7): Jade's two new selfies (2026-10-18) are close-ups, so at v6's placement (face 504.6 crop px, eyes at
crop (1262, 575)) each photo covers only the middle third of the frame and stops above its bottom edge:

    S1  inputs/selfie_hairup_jade_jacket_retouch_v2.png   scale 0.855: frame = photo x -887..2124, rows 49..1743 (photo 1086x1448)
    V3S inputs/selfie_hairdown_jade_jacket_retouch_v2.png scale 0.964: frame = photo x -692..1982, rows 72..1576

So her shoulders, upper arms and lower chest past the photo's left, right and bottom edges are filled in by an image model
(the v5_outpaint.py approach): the photo goes on a larger grey canvas, the model continues it "as if the camera had been
further back", and then EVERY pixel the photo shows is pasted back over the model's output (her face, hair, pencils,
glasses, collar are the photo's own), with a feathered seam and a low-frequency colour match of the fill to the photo
along the seam. The room behind her is kept (it is matted away later); only the empty canvas is new.

    PY=~/Documents/1-music-shipped/moongazing/.venv/bin/python; MPY=(MediaPipe venv)
    $PY  tools/sing/v7_outpaint.py prep                       -> media/sing/outpaint/v7/in_<SHOT>_<model>.png
    $PY  tools/sing/v7_outpaint.py gen S1 nbp_1 gpt_1 [--dry-run]   -> media/sing/outpaint/v7/<SHOT>_<key>.png + .json
    $MPY tools/sing/v7_outpaint.py merge S1 nbp_1            -> media/sing/outpaint/v7/<SHOT>_<key>_merged.png + _merge.json
    $MPY tools/sing/v7_outpaint.py sheet                     -> media/sing/outpaint/v7/contact_sheet.jpg
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OP_VER = os.environ.get("OP_VER", "v7")   # v8 (sultry test, 2026-10-18): a wider 3:2 canvas, the face placed smaller (0.30 of
#                                          the frame height) and the shoulders asked at natural full width (outpaint/v8/)
OUT = os.path.join(ROOT, f"media/sing/outpaint/{OP_VER}")
PHOTOS = {"S1": "inputs/selfie_hairup_jade_jacket_retouch_v2.png", "V3S": "inputs/selfie_hairdown_jade_jacket_retouch_v2.png"}
W0, H0 = 1086, 1448
# canvas per model: (width, height, x of the photo's left edge; the photo's top is the canvas top). 4:3 for
# nano-banana-pro, 3:2 for gpt-image. 1800 rows: the S1 frame needs photo rows to 1743, V3S to 1576.
JACKET_ROW = {"S1": 990, "V3S": 960}     # photo rows below which the seam moves ~100 px inside the photo (shoulder line)
CANVAS = {"nbp": (2400, 1800, 657), "gpt": (2700, 1800, 807)}
if OP_VER == "v8":   # at face 0.30 the S1 frame spans photo x -1124..2371, rows -39..1927; V3S x -902..2201, rows -5..1741
    CANVAS = {"nbp": (3000, 2000, 957)}
COMMON = (
    "This is a real photograph of a woman that has been placed on a larger canvas: the flat grey areas on the left, on the "
    "right and along the bottom are empty canvas, not part of the photo. Fill them in so the photograph simply continues "
    "past its old edges, as if the camera had been further back, showing her from the chest up with natural proportions. "
    "Complete both of her shoulders and upper arms in the same white jacket: each shoulder slopes down from the collar along "
    "its epaulet with the silver snap, then the arm hangs relaxed straight down at her side. The two orange bands continue "
    "across both sleeves and across the front of the jacket; the black turtleneck and the silver zip continue downward. On "
    "the right side of the image the round black-ringed '1420 MHz' patch on her sleeve is completed, a full circle with "
    "'1420' above 'MHz' in black. {HAIR}{WIDE} The room behind her simply continues, plain and softly lit. Do not change "
    "anything that is already in the photograph: her face, glasses, hair, {KEEP}expression, head angle, the visible jacket, "
    "collar, snaps, zip, blue disc and black top stay exactly as they are. Same lighting, colour, sharpness and photographic "
    "grain; no retouching, no beautifying, no extra people or objects, no text other than the patch.")
PER = {
    "S1": dict(HAIR="Her hair is up in a messy bun with two pencils in it, as it is; nothing is added to her hair.",
               KEEP="the two pencils, the loose flyaway hairs, "),
    "V3S": dict(HAIR="Her long dark hair falls in front of her shoulders and down over the jacket as it does.", KEEP=""),
}
MODELS = {
    "nbp": ("google/nano-banana-pro", lambda p, s: {"prompt": p, "aspect_ratio": "3:2" if OP_VER == "v8" else "4:3",
                                                     "image_size": "4K" if OP_VER == "v8" else "2K",
                                                     "output_format": "png", "image_input": [s]}),
    "gpt": ("openai/gpt-image-2.5-flare", lambda p, s: {"prompt": p, "size": "1536x1024", "quality": "high",
                                                         "output_format": "png", "images": [s]}),
}


WIDE = {"v7": "", "v8": (" Show her at her natural full shoulder width, as seen from a few metres away: broad adult shoulders "
                         "reaching well out to both sides, upper arms hanging down along her sides to the bottom of the image. "
                         "There is only one person and one jacket in the picture; the round patch appears once, on the "
                         "sleeve at the right of the image, and nothing white lies beside her.")}
# (the V3S nbp_1 / nbp_2 fills turned the bed and pillow at the photo's right into a second jacket with a second patch;
#  the sentence above was added for V3S nbp_4..7; S1 nbp_1..3 were made without it)


def prompt(shot):
    return COMMON.format(WIDE=WIDE[OP_VER], **PER[shot])


def prep():
    os.makedirs(OUT, exist_ok=True)
    for shot, p in PHOTOS.items():
        a = np.asarray(Image.open(os.path.join(ROOT, p)).convert("RGB"))
        assert a.shape[:2] == (H0, W0), a.shape
        grey = np.array([150, 150, 150], np.uint8)         # flat mid grey: plainly not the room's warm beige
        for k, (w, h, x0) in CANVAS.items():
            c = np.zeros((h, w, 3), np.uint8)
            c[:] = grey
            c[:H0, x0:x0 + W0] = a
            Image.fromarray(c).save(os.path.join(OUT, f"in_{shot}_{k}.png"))
            print(f"in_{shot}_{k}.png", (w, h), "photo at x", x0)


def gen(shot, keys, dry=False):
    sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
    import cf
    tot = 0.0
    for key in keys:
        short = key.split("_")[0]
        model, mk = MODELS[short]
        inp = mk(prompt(shot), "file:" + os.path.relpath(os.path.join(OUT, f"in_{shot}_{short}.png"), ROOT))
        est, why = cf.estimate(model, inp)
        tot += est or 0
        name = f"{shot}_{key}"
        if os.path.exists(os.path.join(OUT, name + ".json")) and not dry:
            print("exists, skipped:", name)
            continue
        paths = cf.generate(model, inp, os.path.join(OUT, name + ".png"), tag=f"{OP_VER}_sing_{shot}_outpaint", dry_run=dry)
        if not dry:
            json.dump({"key": name, "model": model, "prompt": prompt(shot), "input": f"media/sing/outpaint/{OP_VER}/in_{shot}_{short}.png",
                       "request": {k: v for k, v in inp.items() if k not in ("prompt", "images", "image_input")},
                       "est_usd": est, "est_basis": why, "out": [os.path.relpath(x, ROOT) for x in paths]},
                      open(os.path.join(OUT, name + ".json"), "w"), indent=1)
        print(name, model, f"${est}", why)
    print(f"est total ${tot:.3f}{' (dry run)' if dry else ''}")


def model_out(name):
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        if os.path.exists(os.path.join(OUT, name + ext)):
            return os.path.join(OUT, name + ext)
    raise SystemExit(f"no output for {name}")


def nconv(I, m, s):
    import cv2
    num = cv2.GaussianBlur(I * m[..., None], (0, 0), s)
    den = cv2.GaussianBlur(m, (0, 0), s)
    return num / (den[..., None] + 1e-6), den


def merge(shot, key):
    import cv2
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import mouth as MT
    short = key.split("_")[0]
    name = f"{shot}_{key}"
    w, h, x0 = CANVAS[short]
    photo = np.asarray(Image.open(os.path.join(ROOT, PHOTOS[shot])).convert("RGB"))
    ref = np.asarray(Image.open(os.path.join(OUT, f"in_{shot}_{short}.png")).convert("RGB"))
    out = Image.open(model_out(name)).convert("RGB")
    print(name, "model output", out.size)
    o = np.asarray(out.resize((w, h), Image.LANCZOS))
    # register the model's output onto the canvas by her face (similarity on stable landmarks)
    L0 = MT.detect(ref, (x0, 0, x0 + W0, H0))[0]
    L1 = MT.detect(o, (0, 0, w, h))[0]
    STABLE = [33, 133, 362, 263, 168, 6, 197, 195, 5, 4, 1, 98, 327, 10, 151, 9, 127, 356, 234, 454]
    M, _ = cv2.estimateAffinePartial2D(L1[STABLE].astype(np.float32), L0[STABLE].astype(np.float32), method=cv2.LMEDS)
    o = cv2.warpAffine(o, M, (w, h), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
    L1w = L1 @ M[:, :2].T + M[:, 2]
    drift = np.linalg.norm(L1w - L0, axis=1)
    sc = float(np.sqrt(abs(np.linalg.det(M[:, :2]))))
    src = np.zeros((h, w, 3), np.float32)
    src[:H0, x0:x0 + W0] = photo
    inside = np.zeros((h, w), np.float32)
    inside[:H0, x0:x0 + W0] = 1
    # the hand-over: above the shoulders (hair, flyaways, pencils, room) ~25 px inside the photo's edge; on the jacket
    # (rows >= JACKET_ROW) ~100 px inside it, so the band ends and the cut-off patch at the photo's edge come whole from the
    # model's own continuous jacket (nano-banana keeps the photo's area nearly unchanged, so the seam lands where the two
    # agree) instead of meeting the photo's half-patch and band ends a few px off (a doubled "1420", a kinked band)
    # (the bottom edge keeps the narrow hand-over: a wide one there runs through the blue disc and the collar tip, and the
    # model's copies of those sit 1-2 px off the photo's, which ghosts). The canvas top is the photo's top: no seam there.
    xx = np.arange(w)[None, :].astype(np.float32)
    yy = np.arange(h)[:, None].astype(np.float32)
    dx = np.minimum(xx - x0, x0 + W0 - 1 - xx) * np.ones((h, 1), np.float32)
    dy = (H0 - 1 - yy) * np.ones((1, w), np.float32)
    wr = np.clip((yy - JACKET_ROW[shot]) / 80.0, 0, 1)
    k_side = np.clip((dx - 8) / 34, 0, 1) * (1 - wr) + np.clip((dx - 70) / 60, 0, 1) * wr
    k_bot = np.clip((dy - 8) / 34, 0, 1)
    keep = cv2.GaussianBlur(np.minimum(k_side, k_bot) * inside, (0, 0), 3)
    # residual 1-3 px offsets of the model's jacket edges (band edges, patch ring) against the photo: dense flow from the
    # photo to the model inside the photo, smoothed, spread a little outward and faded, then the model is warped by it,
    # so the hand-over does not blend two edges a few px apart into a pale double edge. Only near the hand-over band (a
    # warp elsewhere wobbles the model's own patch ring)
    g1 = cv2.cvtColor(np.clip(src, 0, 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    g2 = cv2.cvtColor(np.clip(o, 0, 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    g2 = np.where(inside > 0, g2, g1)
    fl = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM).calc(g1, g2, None)
    fl = np.clip(fl, -8, 8) * inside[..., None]
    fl, fden = nconv(fl, inside, 12)
    hb = ((keep > 0.02) & (keep < 0.98)).astype(np.uint8)
    dband = cv2.distanceTransform(1 - hb, cv2.DIST_L2, 5)
    fl = fl * (np.exp(-dband / 25.0) * (fden > 0.05))[..., None]
    gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    o = cv2.remap(o, gx + fl[..., 0], gy + fl[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    flow_px = float(np.abs(fl[hb > 0]).max(1).mean())
    # low-frequency colour match: the photo-minus-model difference in a band just inside the photo's left / right /
    # bottom edges, spread outward (normalised blur) and faded with distance, added to the model's fill
    band = inside * (1 - cv2.erode(inside, np.ones((3, 3), np.uint8), iterations=40))
    band[:40] = 0
    # only where the fill shows the same thing as the photo (a band or patch the model put a few px off would otherwise
    # bleed its colour difference, e.g. orange-vs-white, outward as a cyan glow)
    agree = (np.abs(src - o).max(2) < 28).astype(np.float32)
    band = band * agree
    D, den = nconv(src - o, band, 45)
    D = np.clip(D, -18, 18)
    dist = cv2.distanceTransform((inside < 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    fade = np.exp(-dist / 220.0) * np.clip(den / (den.max() * 0.15 + 1e-6), 0, 1)
    of = np.clip(o + D * fade[..., None], 0, 255)
    mrg = src * keep[..., None] + of * (1 - keep[..., None])
    Image.fromarray(np.clip(mrg, 0, 255).astype(np.uint8)).save(os.path.join(OUT, f"{name}_merged.png"))
    sb = (band > 0.5)
    step0 = float(np.abs(o[sb] - src[sb]).mean())
    seam = (keep > 0.2) & (keep < 0.8)
    seam_diff = float(np.abs(of[seam] - src[seam]).max(1).mean())
    res = {"key": name, "scale_to_canvas": round(sc, 4), "landmark_drift_px_mean": round(float(drift.mean()), 2),
           "landmark_drift_px_max": round(float(drift.max()), 2), "seam_band_mean_abs_diff_raw": round(step0, 1),
           "handover_mean_max_channel_diff": round(seam_diff, 1), "flow_mean_px": round(flow_px, 2),
           "canvas": [w, h], "photo_x0": x0, "photo": PHOTOS[shot]}
    json.dump(res, open(os.path.join(OUT, f"{name}_merge.json"), "w"), indent=1)
    print(json.dumps(res))


def sheet():
    tiles = []
    for f in sorted(os.listdir(OUT)):
        if f.endswith("_merged.png"):
            k = f[:-11]
            tiles.append((f"{k} (model)", Image.open(model_out(k))))
            tiles.append((f"{k} merged", Image.open(os.path.join(OUT, f))))
    th = 600
    ims = []
    for lab, im in tiles:
        im = im.convert("RGB")
        im = im.resize((round(im.size[0] * th / im.size[1]), th), Image.LANCZOS)
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 8 * len(lab) + 12, 22], fill=(0, 0, 0))
        d.text((6, 5), lab, fill=(255, 220, 0))
        ims.append(im)
    rows, row, wsum = [], [], 0
    for im in ims:
        if wsum + im.size[0] > 1800 and row:
            rows.append(row); row, wsum = [], 0
        row.append(im); wsum += im.size[0]
    rows.append(row)
    S = Image.new("RGB", (max(sum(i.size[0] for i in r) for r in rows), th * len(rows)), (30, 30, 30))
    for j, r in enumerate(rows):
        x = 0
        for im in r:
            S.paste(im, (x, j * th)); x += im.size[0]
    p = os.path.join(OUT, "contact_sheet.jpg")
    S.save(p, quality=90)
    print(os.path.relpath(p, ROOT), S.size)


if __name__ == "__main__":
    cmd = sys.argv[1]
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    if cmd == "prep":
        prep()
    elif cmd == "gen":
        gen(args[0], args[1:], "--dry-run" in sys.argv)
    elif cmd == "merge":
        merge(args[0], args[1])
    elif cmd == "sheet":
        sheet()
