#!/usr/bin/env python3
"""Singing Jade (v5d), V3S: the hair-down photo's missing shoulders filled in by an image model (Jade, 2026-10-16: "the hair
down photo has parts of shoulders missing because that was simply where the edges of the photo are. can the model fill
those in?"), instead of hand-extending them (v5 / v5b squared the frame-right shoulder off).

Also: what v5/v5b treated as her frame-right shoulder is partly the couch behind her (white upholstery with a lacy raised
pattern above the epaulet, source x ~930-1086, y ~850-1050; BiRefNet kept it as her). Her real shoulder line is the top
edge of the epaulet with the silver snap (~(995, 1037)). That area is painted out to wall grey before the model sees it
(COUCH) and is never pasted back.

    PY=~/Documents/1-music-shipped/moongazing/.venv/bin/python
    $PY tools/sing/v5_outpaint.py prep              -> media/sing/outpaint/in_{nbp,gpt}.png (padded canvases) + couch mask
    $PY tools/sing/v5_outpaint.py gen nbp_1 gpt_1 [--dry-run]   -> media/sing/outpaint/<key>.png + .json (tag v5_sing_V3S_outpaint)
    MPY tools/sing/v5_outpaint.py merge KEY         -> media/sing/outpaint/<KEY>_merged.png: the model's fill, with the
                                                       photo's own pixels pasted back over everything the photo shows
                                                       (minus the couch), ~25 px feathered seam; landmark drift printed + saved
    MPY tools/sing/v5_outpaint.py sheet             -> media/sing/outpaint/contact_sheet.jpg
Then V5_REV=d (tools/sing/v5_first.py) lays the chosen merge over plate_truth_1 in the V3S geometry.
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "inputs/jade_ref_image_music_video_long_hair.png")
OUT = os.path.join(ROOT, "media/sing/outpaint")
W0, H0 = 1086, 1448
BOTTOM = 152                                         # rows of new canvas below the photo
# canvas per model: (width, height, x of the photo's left edge); aspect 4:3 for nano-banana-pro, 3:2 for gpt-image
CANVAS = {"nbp": (2133, 1600, 523), "gpt": (2400, 1600, 657)}
# the couch upholstery above her frame-right shoulder, in source px (hand-drawn on a gridded crop): its lower edge is
# the top edge of the epaulet; hair strands in front of it at x < 935 are kept
COUCH = [(935, 830), (1086, 830), (1086, 1052), (1052, 1041), (1012, 1024), (978, 1009), (950, 1000), (935, 994)]
PROMPT = (
    "This is a real photograph of a woman that has been placed on a larger canvas: the flat light-grey areas on the left, "
    "on the right and along the bottom are empty canvas, not part of the photo. Fill them in so the photograph simply "
    "continues past its old edges, as if the camera had been further back. Complete both of her shoulders and upper arms in "
    "the same white jacket: on the right side of the image her shoulder slopes down from her collar along the epaulet with "
    "its silver snap, then her arm hangs straight down at her side; the orange band continues around that sleeve, and the "
    "round black-ringed '1420 MHz' patch on that sleeve is complete, a full circle with '1420' above 'MHz' in black. On "
    "the left side of the image her other shoulder and arm continue the same way, the orange bands continuing across the "
    "sleeve. Her long dark hair falls in front of her shoulders as it does. The background is a plain, softly lit light-grey "
    "wall with nothing on it. Do not change anything that is already in the photograph: her face, glasses, hair, expression, "
    "head angle, the visible jacket, collar, zip and black top stay exactly as they are. Same lighting, colour, sharpness "
    "and photographic grain; no retouching, no beautifying, no extra people or objects, no text other than the patch.")
MODELS = {
    "nbp": ("google/nano-banana-pro", lambda p, s: {"prompt": p, "aspect_ratio": "4:3", "image_size": "2K",
                                                     "output_format": "png", "image_input": [s]}),
    "gpt": ("openai/gpt-image-2.5-flare", lambda p, s: {"prompt": p, "size": "1536x1024", "quality": "high",
                                                         "output_format": "png", "images": [s]}),
}


def wall_colour(a):
    return np.median(a[200:600, 960:1080].reshape(-1, 3), 0)          # the plain wall at the photo's top right


def couch_mask(shape=(H0, W0)):
    m = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(m).polygon(COUCH, fill=255)
    return np.asarray(m) > 0


def prep():
    os.makedirs(OUT, exist_ok=True)
    a = np.asarray(Image.open(SRC).convert("RGB"))
    wall = wall_colour(a)
    b = a.copy()
    b[couch_mask()] = wall
    for k, (w, h, x0) in CANVAS.items():
        c = np.zeros((h, w, 3), np.uint8)
        c[:] = (wall * 0.92 + 8).astype(np.uint8)                      # a light grey a touch apart from the wall
        c[:H0, x0:x0 + W0] = b
        Image.fromarray(c).save(os.path.join(OUT, f"in_{k}.png"))
        print(f"in_{k}.png", (w, h), "photo at x", x0)
    Image.fromarray((couch_mask() * 255).astype(np.uint8)).save(os.path.join(OUT, "couch_mask.png"))


def gen(keys, dry=False):
    sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
    import cf
    tot = 0.0
    for key in keys:
        short = key.split("_")[0]
        model, mk = MODELS[short]
        inp = mk(PROMPT, "file:" + os.path.relpath(os.path.join(OUT, f"in_{short}.png"), ROOT))
        est, why = cf.estimate(model, inp)
        tot += est
        if os.path.exists(os.path.join(OUT, f"{key}.json")) and not dry:
            print("exists, skipped:", key)
            continue
        paths = cf.generate(model, inp, os.path.join(OUT, key + ".png"), tag="v5_sing_V3S_outpaint", dry_run=dry)
        if not dry:
            json.dump({"key": key, "model": model, "prompt": PROMPT, "input": f"media/sing/outpaint/in_{short}.png",
                       "request": {k: v for k, v in inp.items() if k not in ("prompt", "images", "image_input")},
                       "est_usd": est, "est_basis": why, "out": [os.path.relpath(x, ROOT) for x in paths]},
                      open(os.path.join(OUT, key + ".json"), "w"), indent=1)
        print(key, model, f"${est:.3f}", why)
    print(f"est total ${tot:.3f}{' (dry run)' if dry else ''}")


def model_out(key):
    for ext in (".png", ".jpg", ".webp"):
        if os.path.exists(os.path.join(OUT, key + ext)):
            return os.path.join(OUT, key + ext)
    raise SystemExit(f"no output for {key}")


def merge(key):
    import cv2
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import mouth as MT
    short = key.split("_")[0]
    w, h, x0 = CANVAS[short]
    ref = np.asarray(Image.open(os.path.join(OUT, f"in_{short}.png")).convert("RGB"))
    out = Image.open(model_out(key)).convert("RGB")
    print(key, "model output", out.size)
    out = out.resize((w, h), Image.LANCZOS)
    o = np.asarray(out)
    # register the model's output onto the canvas by her face (similarity on stable landmarks), then measure drift
    L0 = MT.detect(ref, (x0, 0, x0 + W0, H0))[0]
    L1 = MT.detect(o, (0, 0, w, h))[0]
    STABLE = [33, 133, 362, 263, 168, 6, 197, 195, 5, 4, 1, 98, 327, 10, 151, 9, 127, 356, 234, 454]
    M, _ = cv2.estimateAffinePartial2D(L1[STABLE].astype(np.float32), L0[STABLE].astype(np.float32), method=cv2.LMEDS)
    o = cv2.warpAffine(o, M, (w, h), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
    L1w = L1 @ M[:, :2].T + M[:, 2]
    drift = np.linalg.norm(L1w - L0, axis=1)
    sc = float(np.sqrt(abs(np.linalg.det(M[:, :2]))))
    # paste the photo back over everything it really shows (not the couch), feathered 10 px inward from its edges
    keep = np.zeros((h, w), np.float32)
    keep[:H0, x0:x0 + W0] = 1
    keep[:H0, x0:x0 + W0][couch_mask()] = 0
    keep = cv2.erode(keep, np.ones((3, 3), np.uint8), iterations=14)   # a wide hand-over (~25 px) so no seam line shows
    keep = cv2.GaussianBlur(keep, (0, 0), 9)
    src = np.zeros_like(ref)
    src[:H0, x0:x0 + W0] = np.asarray(Image.open(SRC).convert("RGB"))
    mrg = (src * keep[..., None] + o * (1 - keep[..., None])).astype(np.uint8)
    Image.fromarray(mrg).save(os.path.join(OUT, f"{key}_merged.png"))
    # how well the model's own pixels matched the photo just inside the seam (colour step across it)
    inner = np.zeros((h, w), bool)
    inner[:H0, x0:x0 + W0] = True
    band = cv2.dilate((keep > 0.98).astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool) & (keep < 0.98) & inner
    step = float(np.abs(o[band].astype(float) - src[band].astype(float)).mean()) if band.any() else None
    res = {"key": key, "scale_to_canvas": round(sc, 4), "landmark_drift_px_mean": round(float(drift.mean()), 2),
           "landmark_drift_px_max": round(float(drift.max()), 2), "seam_band_mean_abs_diff": round(step, 1) if step else None,
           "canvas": [w, h], "photo_x0": x0}
    json.dump(res, open(os.path.join(OUT, f"{key}_merge.json"), "w"), indent=1)
    print(json.dumps(res))


def sheet():
    from PIL import ImageFont  # noqa: F401
    tiles = [("source (couch painted out)", Image.open(os.path.join(OUT, "in_nbp.png")))]
    for f in sorted(os.listdir(OUT)):
        if f.endswith("_merged.png"):
            k = f[:-11]
            tiles.append((f"{k} (model)", Image.open(model_out(k))))
            tiles.append((f"{k} merged", Image.open(os.path.join(OUT, f))))
    first = os.path.join(ROOT, "media/sing/first/v5d_V3S_first.jpg")
    if os.path.exists(first):
        tiles.append(("v5d_V3S_first.jpg", Image.open(first)))
    th = 540
    ims = []
    for lab, im in tiles:
        im = im.convert("RGB")
        im = im.resize((round(im.size[0] * th / im.size[1]), th), Image.LANCZOS)
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 9 * len(lab) + 12, 22], fill=(0, 0, 0))
        d.text((6, 5), lab, fill=(255, 220, 0))
        ims.append(im)
    rows, row, wsum = [], [], 0
    for im in ims:
        if wsum + im.size[0] > 2600 and row:
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
        gen(args, "--dry-run" in sys.argv)
    elif cmd == "merge":
        merge(args[0])
    elif cmd == "sheet":
        sheet()
