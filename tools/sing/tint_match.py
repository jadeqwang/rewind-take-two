#!/usr/bin/env python3
"""Tint match (Jade, 2026-10-16): give the updo-with-pencils photo the more natural makeup and skin tints of the
hair-down photo. Only cheeks, lips, skin warmth/saturation and shine change; face, glasses, hair, pencils, jacket,
couch and framing stay as they are. Candidates for her to look at; nothing is wired in. Inputs are never overwritten.

    PY=~/Documents/1-music-shipped/moongazing/.venv/bin/python
    MPY=~/Documents/1-music-shipped/orbital-sunrise-video/video/out/.venv/bin/python   (MediaPipe, OpenCV)
    $PY  tools/sing/tint_match.py gen KEY [KEY ...] [--dry-run]   KEY in nbp_1 nbp_2 gpt_1 gpt_2 (tags tint_nbp / tint_gpt)
    $MPY tools/sing/tint_match.py local [--name=local_a] [--blush=..] [--warm=..] [--lips=..] [--shine=..] [--flush=..]
         (made: local_a = defaults; local_b = --flush=0.8 --shine=0.5, the pick)
    $MPY tools/sing/tint_match.py check            -> media/sing/tint/metrics.json, contact_sheet.jpg, <key>_aligned.png

Paid edits get both photos: image 1 = the photo to edit, image 2 = the tint reference. nano-banana-pro returns 4:3 like
the source; gpt-image-2.5 can only return 3:2, so it gets the source cropped to 3:2 (rows CROP3x2) and its output is
mapped back. `check` maps every candidate onto the source by eye/nose/brow landmarks (similarity fit) and reports how
far all 478 face landmarks moved (source px), plus how much the pixels outside the skin changed (pencils, glasses, hair,
jacket, background). `local` is a free pass with no model: soft landmark masks + LAB statistics from the hair-down photo.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "inputs/jade_ref_image2_music_video_pencils.png")          # 1448x1086, the one to edit
REF = os.path.join(ROOT, "inputs/jade_ref_image_music_video_long_hair.png")         # 1086x1448, tint reference
OUT = os.path.join(ROOT, "media/sing/tint")
W0, H0 = 1448, 1086
CROP3x2 = (0, 1448, 40, 1005)        # x0, x1, y0, y1: 1448x965 = 3:2, keeps both erasers (y ~95-160) and the patch
os.environ.setdefault("FACE_LANDMARKER", os.path.expanduser(
    "~/Documents/1-music-shipped/moongazing/tools/sync/models/face_landmarker.task"))

PROMPT = (
    "Two photos of the same woman. IMAGE 1 (the first image) is the photo to edit. IMAGE 2 (the second image) is only a "
    "colour reference for her makeup and skin tint.\n\n"
    "Edit IMAGE 1 so that her makeup and skin tint look like IMAGE 2, and change nothing else. In IMAGE 2 her skin is a "
    "neutral, even, natural tone with very little blush; her lips are a soft, muted, natural rosy-beige with no gloss; her "
    "skin has a soft, natural, mostly matte finish. In IMAGE 1 her cheeks are flushed rosy pink, her lips are pinker and "
    "glossy, and her skin is warmer, more saturated and glowing. So, in IMAGE 1 only:\n"
    "- tone the rosy flush on her cheeks and nose down to the faint, natural colour of IMAGE 2;\n"
    "- make her lips the same muted, natural, non-glossy colour as in IMAGE 2, keeping their exact shape and her closed "
    "half-smile;\n"
    "- make her skin a little less warm and less saturated, like IMAGE 2, and reduce the shiny glow on her forehead, nose "
    "and cheeks to a soft natural sheen. Keep her freckles, pores and real skin texture.\n\n"
    "Take ONLY the colour of the skin, cheeks and lips from IMAGE 2. Do not copy anything else from IMAGE 2: not her long "
    "hair, not her face shape or features, not her expression, head angle, glasses, clothes, lighting or background.\n\n"
    "Everything else in IMAGE 1 stays exactly the same, pixel for pixel: her face shape, eyes, eyebrows, nose, mouth, "
    "expression and head position; her thin black rectangular glasses; her dark hair up in a loose bun with the stray "
    "wisps; the two yellow pencils stuck in her bun, one with a pale-blue eraser and one with a pink eraser; the white "
    "jacket with its orange bands, the blue disc and the round black '1420 MHz' patch; the black top; the beige couch, "
    "the grey wall and the soft sunlight; the framing and crop. It stays the same real, unretouched photograph: do not "
    "beautify, smooth, slim, sharpen or restyle her, and do not add makeup.")
# take 2 (written after looking at take 1). nbp_1 matched the skin but posterized the wall into contour bands, smoothed
# her face a little and took the lips to a flat beige; gpt_1 kept her well but hardly moved the blush or the lip pink.
PROMPT_NBP2 = PROMPT.replace(
    "Edit IMAGE 1 so that", "This is a subtle colour-grading retouch, like a careful skin-tone correction in Lightroom: "
    "the person, every feature and every object stay identical, only colours on her skin and lips shift. Edit IMAGE 1 so that"
) + (" Keep the full photographic quality of IMAGE 1: the same sharpness, grain and smooth tonal gradients on the wall and "
     "skin, no banding or posterization, same resolution and crop. Her lips stay a soft natural rosy-peach like IMAGE 2, "
     "not beige or grey.")
PROMPT_GPT2 = PROMPT + (
    " The change must be clearly visible side by side with IMAGE 1: the bright pink flush on her cheek on the viewer's left "
    "and on her nose is gone, the skin there matches the rest of her face, and her lips are a paler, peachier, matte pink "
    "like IMAGE 2 instead of the deeper glossy pink. Keep every freckle and the skin texture; do not smooth her skin.")

# key -> (model, request builder(prompt, src_file, ref_file), source crop sent)
MODELS = {
    "nbp": ("google/nano-banana-pro", lambda p, s, r: {"prompt": p, "aspect_ratio": "4:3", "image_size": "2K",
                                                        "output_format": "png", "image_input": [s, r]}, None),
    "gpt": ("openai/gpt-image-2.5-flare", lambda p, s, r: {"prompt": p, "size": "1536x1024", "quality": "high",
                                                            "output_format": "png", "images": [s, r]}, CROP3x2),
}
TAKES = {"nbp_1": ("nbp", PROMPT), "gpt_1": ("gpt", PROMPT), "nbp_2": ("nbp", PROMPT_NBP2), "gpt_2": ("gpt", PROMPT_GPT2)}


def src_for(short):
    from PIL import Image
    crop = MODELS[short][2]
    if crop is None:
        return SRC
    p = os.path.join(OUT, "_in", "src_crop3x2.png")
    if not os.path.exists(p):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        x0, x1, y0, y1 = crop
        Image.open(SRC).convert("RGB").crop((x0, y0, x1, y1)).save(p)
    return p


def gen(argv):
    sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
    import cf
    from concurrent.futures import ThreadPoolExecutor
    dry = "--dry-run" in argv
    keys = [a for a in argv if not a.startswith("--")]
    os.makedirs(OUT, exist_ok=True)

    def one(key):
        short, prompt = TAKES[key]
        model, mk, crop = MODELS[short]
        if os.path.exists(os.path.join(OUT, f"{key}.json")) and not dry:
            print("exists, skipped:", key); return key, None
        s = src_for(short)
        inp = mk(prompt, "file:" + os.path.relpath(s, ROOT), "file:" + os.path.relpath(REF, ROOT))
        tag = f"tint_{short}"
        try:
            est, why = cf.estimate(model, inp)
            paths = cf.generate(model, inp, os.path.join(OUT, key + ".png"), tag=tag, dry_run=dry)
        except Exception as e:  # noqa: BLE001
            print(f"[fail] {key}: {str(e)[:300]}", file=sys.stderr); return key, None
        if not dry:
            json.dump({"key": key, "model": model, "prompt": prompt, "tag": tag, "src": os.path.relpath(s, ROOT),
                       "src_crop_x0x1y0y1": crop, "ref": os.path.relpath(REF, ROOT),
                       "request": {k: v for k, v in inp.items() if k not in ("prompt", "images", "image_input")},
                       "est_usd": est, "est_basis": why, "out": [os.path.relpath(x, ROOT) for x in paths]},
                      open(os.path.join(OUT, key + ".json"), "w"), indent=1)
        return key, est

    with ThreadPoolExecutor(4) as ex:
        res = list(ex.map(one, keys))
    print(json.dumps(res), f"est ${sum(e for _, e in res if e):.3f}{' (dry run)' if dry else ''}")


# ---------------------------------------------------------------------------------------------- landmarks and masks
OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150,
        136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
JAW = [288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58]      # lower jaw only: the neck below it
EYE_L = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
EYE_R = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
BROW_L = [70, 63, 105, 66, 107, 55, 65, 52, 53, 46]
BROW_R = [300, 293, 334, 296, 336, 285, 295, 282, 283, 276]
LIPS = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409, 270, 269, 267, 0, 37, 39, 40, 185]
STABLE = [33, 133, 362, 263, 168, 6, 197, 195, 5, 4, 1, 98, 327, 10, 151, 9, 127, 356, 234, 454]   # eyes, nose, brow, temples


def load(p):
    import numpy as np
    from PIL import Image
    return np.asarray(Image.open(p).convert("RGB"))


def landmarks(rgb):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import mouth as MT
    r = MT.detect(rgb, (0, 0, rgb.shape[1], rgb.shape[0]))
    return None if r is None else r[0]


def to_lab(rgb):
    import cv2
    import numpy as np
    return cv2.cvtColor(rgb.astype(np.float32) / 255, cv2.COLOR_RGB2LAB)


def from_lab(lab):
    import cv2
    import numpy as np
    return np.clip(cv2.cvtColor(lab.astype(np.float32), cv2.COLOR_LAB2RGB) * 255 + 0.5, 0, 255).astype(np.uint8)


def _poly(shape, pts):
    import cv2
    import numpy as np
    m = np.zeros(shape[:2], np.uint8)
    cv2.fillPoly(m, [np.round(pts).astype(np.int32)], 1)
    return m.astype(np.float32)


def _ss(x, a, b):
    import numpy as np
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def masks(rgb, L):
    """Soft masks (float 0..1): skin (face + neck, no eyes/brows/lips/glasses frame/hair), lips, cheeks."""
    import cv2
    import numpy as np
    H, W = rgb.shape[:2]
    io = float(np.linalg.norm(L[33] - L[263]))
    lab = to_lab(rgb)
    Lc, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    k = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(r) * 2 + 1,) * 2)
    face = _poly(rgb.shape, L[OVAL])
    down = L[152] - L[168]                                   # face axis, so the neck follows a tilted head
    down = down / np.linalg.norm(down) * 0.75 * io
    neck = _poly(rgb.shape, np.vstack([L[JAW], (L[JAW] + down)[::-1]]))
    ears = np.zeros((H, W), np.float32)
    for side, inner in ((234, 454), (454, 234)):              # ears sit just outside the oval's widest points
        c = L[side] + (L[side] - L[inner]) / np.linalg.norm(L[side] - L[inner]) * 0.2 * io
        cv2.circle(ears, (int(c[0]), int(c[1])), int(0.35 * io), 1, -1)
    region = cv2.dilate(np.maximum(np.maximum(face, neck), ears), k(0.05 * io))
    holes = np.zeros((H, W), np.float32)
    for ix, r in ((EYE_L, 0.10), (EYE_R, 0.10), (BROW_L, 0.06), (BROW_R, 0.06)):
        holes = np.maximum(holes, cv2.dilate(_poly(rgb.shape, L[ix]), k(r * io)))
    lips = _poly(rgb.shape, L[LIPS])
    chroma = np.hypot(a, b)
    colour = _ss(Lc, 28, 40) * _ss(chroma, 9, 16) * _ss(a, 4, 9) * _ss(b, 3, 8)     # skin-coloured; drops frame, hair, lens glints
    ear_only = ears * (1 - cv2.dilate(face, k(0.05 * io)))    # lit golden hair crosses the ears: stricter test there
    colour = colour * (1 - ear_only * (1 - _ss(Lc, 45, 55) * _ss(a, 11, 15)))
    skin = region * (1 - holes) * (1 - cv2.dilate(lips, k(0.03 * io))) * colour
    skin = cv2.GaussianBlur(skin, (0, 0), 0.012 * io) * _ss(Lc, 24, 34)            # feather, but never onto dark frame/hair
    lips = cv2.GaussianBlur(lips, (0, 0), 0.02 * io) * _ss(Lc, 18, 30)
    yy, xx = np.mgrid[:H, :W].astype(np.float32)
    cheeks = np.zeros((H, W), np.float32)
    for c in (205, 425):                                       # the apples of the cheeks, under the eyes
        cx, cy = (L[c] + L[[117, 346][c == 425]]) / 2
        cheeks = np.maximum(cheeks, np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * (0.28 * io) ** 2)))
    return {"skin": skin, "lips": lips, "cheeks": cheeks * skin, "io": io, "lab": lab}


def stats(lab, w, thr=0.8):
    import numpy as np
    m = w > thr
    v = lab[m]
    return {"n": int(m.sum()), "mean": v.mean(0).round(2).tolist(), "std": v.std(0).round(2).tolist(),
            "p95L": round(float(np.percentile(v[:, 0], 95)), 2)}


# ---------------------------------------------------------------------------------------------- local pass (no model)
def local(argv):
    """LAB statistics transfer from the hair-down photo's skin / lips onto the updo photo, under soft landmark masks.
    Geometry is untouched by construction: only a*, b* (and highlight L) of skin and lip pixels move."""
    import cv2
    import numpy as np
    from PIL import Image
    o = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    name = o.get("name", "local_a")
    warm = float(o.get("warm", 1.0))      # 0..1 of the way to the target's skin a*/b* means (warmth, saturation)
    blush = float(o.get("blush", 1.0))    # 0..1 of the way to the target's a* spread (flush on cheeks/nose)
    lipk = float(o.get("lips", 1.0))      # 0..1 of the way to the target's lip colour
    shine = float(o.get("shine", 0.5))    # fraction of skin highlight above the local base that is removed
    flush = float(o.get("flush", 0.0))    # fraction of the local a* excess (blotchy flush over the face's broad trend) removed
    src, ref = load(SRC), load(REF)
    Ls, Lr = landmarks(src), landmarks(ref)
    ms, mr = masks(src, Ls), masks(ref, Lr)
    lab = ms["lab"].copy()
    ss, sr = stats(lab, ms["skin"]), stats(mr["lab"], mr["skin"])
    ls, lr = stats(lab, ms["lips"], 0.6), stats(mr["lab"], mr["lips"], 0.6)
    w = ms["skin"]
    out = lab.copy()
    # skin: a*, b* -> target mean, and the a* spread (blush) compressed toward the target's
    for ch, kk in ((1, blush), (2, 0.5 * blush)):
        mu_s, mu_r = ss["mean"][ch], sr["mean"][ch]
        g = 1 + kk * (min(1.0, sr["std"][ch] / ss["std"][ch]) - 1)
        new = mu_s + warm * (mu_r - mu_s) + (lab[..., ch] - mu_s) * g
        out[..., ch] = lab[..., ch] + w * (new - lab[..., ch])
    # extra cheek flush: whatever a* the cheeks carry above the rest of the skin, scaled to the target's cheek excess
    cs, cr = stats(out, ms["cheeks"], 0.5), stats(mr["lab"], mr["cheeks"], 0.5)
    ex_s, ex_r = cs["mean"][1] - stats(out, w)["mean"][1], cr["mean"][1] - sr["mean"][1]
    if ex_s > ex_r:
        out[..., 1] -= blush * ms["cheeks"] * (ex_s - max(ex_r, 0))
    io = ms["io"]
    # local flush: a* smoothed at blush scale minus a* at face scale; its positive part is the patchy rosiness
    if flush > 0:
        def wblur(x, sg):
            return cv2.GaussianBlur(x * w, (0, 0), sg) / (cv2.GaussianBlur(w, (0, 0), sg) + 1e-4)
        exc = np.maximum(0, wblur(out[..., 1], 0.10 * io) - wblur(out[..., 1], 0.45 * io))
        out[..., 1] -= flush * w * exc
        out[..., 2] -= 0.3 * flush * w * exc                   # the flush is warm too; keep the hue from going green
    # shine: soft highlight roll-off above the local (blurred) skin lightness
    num = cv2.GaussianBlur(lab[..., 0] * w, (0, 0), 0.10 * io)
    den = cv2.GaussianBlur(w, (0, 0), 0.10 * io) + 1e-4
    base = num / den
    spec = np.maximum(0, lab[..., 0] - base - 1.5) * _ss(lab[..., 0], 60, 80)
    out[..., 0] = lab[..., 0] - shine * w * spec
    # lips: mean/std transfer of L*a*b* toward the target lips (L only half way: the lighting differs), gloss rolled off
    wl = ms["lips"]
    for ch, kk in ((0, 0.5), (1, 1.0), (2, 1.0)):
        mu_s, mu_r = ls["mean"][ch], lr["mean"][ch]
        g = 1 + (min(1.0, lr["std"][ch] / ls["std"][ch]) - 1)
        new = mu_s + kk * (mu_r - mu_s) + (lab[..., ch] - mu_s) * (g if ch else 1)
        out[..., ch] = out[..., ch] + lipk * wl * (new - lab[..., ch])
    lbase = cv2.GaussianBlur(lab[..., 0] * wl, (0, 0), 0.05 * io) / (cv2.GaussianBlur(wl, (0, 0), 0.05 * io) + 1e-4)
    out[..., 0] -= lipk * shine * wl * np.maximum(0, lab[..., 0] - lbase - 3)
    res = from_lab(out)
    keep = (ms["skin"] + ms["lips"]) < 1e-3                  # outside both masks: bit-exact source pixels
    res[keep] = src[keep]
    os.makedirs(OUT, exist_ok=True)
    Image.fromarray(res).save(os.path.join(OUT, name + ".png"))
    Image.fromarray((np.clip(np.maximum(ms["skin"], ms["lips"]), 0, 1) * 255).astype(np.uint8)).save(
        os.path.join(OUT, "_in", name + "_mask.png") if os.path.isdir(os.path.join(OUT, "_in")) else os.path.join(OUT, name + "_mask.png"))
    json.dump({"key": name, "model": "local LAB transfer (no model)", "params": {"warm": warm, "blush": blush, "lips": lipk,
               "shine": shine, "flush": flush}, "src_skin": ss, "ref_skin": sr, "src_lips": ls, "ref_lips": lr,
               "src_cheek_excess_a": round(ex_s, 2), "ref_cheek_excess_a": round(ex_r, 2), "est_usd": 0,
               "out": [os.path.relpath(os.path.join(OUT, name + ".png"), ROOT)]},
              open(os.path.join(OUT, name + ".json"), "w"), indent=1)
    print(name, "skin src", ss["mean"], "ref", sr["mean"], "| lips src", ls["mean"], "ref", lr["mean"],
          "| cheek excess a* src %.2f ref %.2f" % (ex_s, ex_r))


# ---------------------------------------------------------------------------------------------- check + contact sheet
VERDICT = {   # written after looking at every candidate at 1:1 (see media/sing/tint/README.md)
    "local_a": "OK: stats-only, a bit of blush left",
    "local_b": "PICK: flush + stats, exact likeness",
    "nbp_1": "REJECT: posterized wall/skin, beige lips",
    "nbp_2": "REJECT: same banding, blue glints",
    "gpt_1": "REJECT: barely changed, smoothed",
    "gpt_2": "RUNNER-UP: good tint, smoothed skin",
}
def candidates():
    out = []
    for f in sorted(os.listdir(OUT)):
        if f.endswith(".json") and f.split("_")[0] in ("nbp", "gpt", "local") and not f.startswith("metrics"):
            d = json.load(open(os.path.join(OUT, f)))
            if d.get("out") and os.path.exists(os.path.join(ROOT, d["out"][0])):
                out.append(d)
    order = {"local": 0, "nbp": 1, "gpt": 2}
    return sorted(out, key=lambda d: (order[d["key"].split("_")[0]], d["key"]))


def align(a, L, L0):
    """Similarity fit of candidate landmarks (STABLE) onto the source; returns warped image, warped landmarks, valid mask,
    scale (candidate px per source px)."""
    import cv2
    import numpy as np
    M, _ = cv2.estimateAffinePartial2D(L[STABLE].astype(np.float32), L0[STABLE].astype(np.float32), method=cv2.LMEDS)
    s = float(np.hypot(M[0, 0], M[0, 1]))
    w = cv2.warpAffine(a, M, (W0, H0), flags=cv2.INTER_AREA if s < 1 else cv2.INTER_LANCZOS4)
    valid = cv2.warpAffine(np.full(a.shape[:2], 255, np.uint8), M, (W0, H0), flags=cv2.INTER_NEAREST) > 0
    return w, L @ M[:, :2].T + M[:, 2], valid, 1 / s


def check(argv):
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    src, ref = load(SRC), load(REF)
    L0, Lr = landmarks(src), landmarks(ref)
    ms, mr = masks(src, L0), masks(ref, Lr)
    io0 = ms["io"]
    lab0 = ms["lab"]
    # regions that must not change: erasers (saturated blue / pink above the hairline), glasses frame, hair, the rest
    hsv = cv2.cvtColor(src, cv2.COLOR_RGB2HSV).astype(int)
    top = np.zeros(src.shape[:2], bool); top[:int(L0[10, 1] - 0.4 * io0)] = True   # above the forehead: only the pencils
    blue = top & (hsv[..., 0] >= 92) & (hsv[..., 0] <= 122) & (hsv[..., 1] > 60) & (hsv[..., 2] > 110)
    pink = top & ((hsv[..., 0] >= 150) | (hsv[..., 0] <= 6)) & (hsv[..., 1] > 60) & (hsv[..., 2] > 130)
    k = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(r) * 2 + 1,) * 2)
    eyes = cv2.dilate(_poly(src.shape, L0[EYE_L]) + _poly(src.shape, L0[EYE_R]), k(0.45 * io0)) > 0
    frame = eyes & (lab0[..., 0] < 30) & (_poly(src.shape, L0[OVAL]) > 0) | (eyes & (lab0[..., 0] < 25))
    face_zone = cv2.dilate(np.maximum(_poly(src.shape, L0[OVAL]), ms["skin"]), k(0.15 * io0)) > 0
    hair = ~face_zone & (lab0[..., 0] < 30) & (np.arange(H0)[:, None] < L0[152, 1])
    outside = ~face_zone & ~hair
    regions = {"erasers_blue": blue, "erasers_pink": pink, "glasses_frame": frame, "hair": hair, "outside_face": outside}
    metrics = {}
    tiles = {"original": src}
    for d in candidates():
        key = d["key"]
        a = load(os.path.join(ROOT, d["out"][0]))
        L = landmarks(a)
        if L is None:
            print("no face:", key); continue
        if a.shape == src.shape and d["model"].startswith("local"):   # same pixel grid by construction: no resampling
            w, Lw, valid, scale = a, L, np.ones(a.shape[:2], bool), 1.0
        else:
            w, Lw, valid, scale = align(a, L, L0)
        w = np.where(valid[..., None], w, src)                 # gpt's 3:2 crop: the missing strips shown from the source
        Image.fromarray(w).save(os.path.join(OUT, "_in", key + "_aligned.png"))
        sh = np.linalg.norm(Lw - L0, axis=1)
        labw = to_lab(w)
        reg = {}
        for n, m in regions.items():
            m = m & valid
            reg[n] = {"mean_abs_rgb": round(float(np.abs(w[m].astype(int) - src[m].astype(int)).mean()), 2),
                      "mean_rgb": np.round(w[m].mean(0)).astype(int).tolist(), "src_rgb": np.round(src[m].mean(0)).astype(int).tolist()} \
                if n.startswith("erasers") else round(float(np.abs(w[m].astype(int) - src[m].astype(int)).mean()), 2)
        tint = {}
        for n, (wm, wr, thr) in {"skin": (ms["skin"], mr["skin"], 0.8), "cheeks": (ms["cheeks"], mr["cheeks"], 0.5),
                                 "lips": (ms["lips"], mr["lips"], 0.6)}.items():
            c, r0, s0 = stats(labw, wm, thr)["mean"], stats(mr["lab"], wr, thr)["mean"], stats(lab0, wm, thr)["mean"]
            tint[n] = {"Lab": c, "src_Lab": s0, "target_Lab": r0,
                       "dE_ab_to_target": round(float(np.hypot(c[1] - r0[1], c[2] - r0[2])), 2),
                       "dE_ab_src_to_target": round(float(np.hypot(s0[1] - r0[1], s0[2] - r0[2])), 2)}
        metrics[key] = {"model": d["model"], "cand_px_per_src_px": round(scale, 3),
                        "landmark_shift_px_mean": round(float(sh.mean()), 2), "landmark_shift_px_max": round(float(sh.max()), 2),
                        "landmark_shift_pct_io_max": round(float(sh.max() / io0 * 100), 2),
                        "pixel_change_mean_abs_rgb": reg, "tint": tint}
        tiles[key] = w
        print(key, json.dumps({k2: v for k2, v in metrics[key].items() if k2 not in ("tint",)}))
        print("   tint ab dist to target (skin/cheeks/lips):",
              [tint[n]["dE_ab_to_target"] for n in tint], "source was", [tint[n]["dE_ab_src_to_target"] for n in tint])
    json.dump(metrics, open(os.path.join(OUT, "metrics.json"), "w"), indent=1)

    # target face mapped to the source face frame (same scale) for the crop row
    rw, _, _, _ = align(ref, Lr, L0)

    def font(sz):
        for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
            if os.path.exists(p):
                return ImageFont.truetype(p, sz)
        return ImageFont.load_default()

    keys = list(tiles)
    lab_of = {"original": ("ORIGINAL (updo, rosy)", "inputs/..._pencils.png"), "target": ("TARGET (hair down)", "inputs/..._long_hair.png")}
    for k2 in metrics:
        m = metrics[k2]
        lab_of[k2] = (k2, f"shift {m['landmark_shift_px_mean']:.1f}/{m['landmark_shift_px_max']:.1f}px  "
                          f"lips dab {m['tint']['lips']['dE_ab_to_target']:.1f}")
    cols = ["original", "target"] + keys[1:]
    fw, fh = 420, 315                       # full frames (4:3); the target is shown portrait at the same height
    cx0, cy0, cx1, cy1 = [int(v) for v in (L0[:, 0].min() - 0.25 * io0, L0[:, 1].min() - 0.35 * io0,
                                           L0[:, 0].max() + 0.25 * io0, L0[:, 1].max() + 0.12 * io0)]
    cw = fw
    ch = round(cw * (cy1 - cy0) / (cx1 - cx0))
    pad, lab = 12, 72
    widths = [round(fh * W0 / H0) if c != "target" else round(fh * ref.shape[1] / ref.shape[0]) for c in cols]
    colw = [max(wd, cw) for wd in widths]
    S = Image.new("RGB", (sum(colw) + pad * (len(cols) + 1), lab + fh + pad + ch + pad * 2 + 30), (28, 28, 30))
    dr = ImageDraw.Draw(S)
    x = pad
    for c, wd, cwid in zip(cols, widths, colw):
        full = ref if c == "target" else tiles[c]
        S.paste(Image.fromarray(full).resize((wd, fh), Image.LANCZOS), (x, lab))
        face = (rw if c == "target" else tiles[c])[cy0:cy1, cx0:cx1]
        S.paste(Image.fromarray(face).resize((cw, ch), Image.LANCZOS), (x, lab + fh + pad))
        dr.text((x + 2, 2), lab_of[c][0], fill=(255, 255, 255), font=font(20))
        dr.text((x + 2, 27), lab_of[c][1], fill=(170, 170, 175), font=font(14))
        if c in VERDICT:
            dr.text((x + 2, 47), VERDICT[c], fill=(120, 220, 140) if VERDICT[c][:2] in ("PI", "OK", "RU") else (240, 120, 110), font=font(15))
        x += cwid + pad
    dr.text((pad, S.size[1] - 28), "Row 2: face crops at the same scale (each image mapped onto the original by eye/nose/brow "
            "landmarks; target face too).  shift = mean/max landmark move in original px; lips dab = a*b* distance of lip "
            "colour to the target's", fill=(170, 170, 175), font=font(14))
    p = os.path.join(OUT, "contact_sheet.jpg")
    S.save(p, quality=92)
    print(p, S.size)
    # big face-crop strip for close looking (scratch, in _in/)
    strip = [Image.fromarray((rw if c == "target" else tiles[c])[cy0:cy1, cx0:cx1]) for c in cols]
    T = Image.new("RGB", (sum(t.size[0] for t in strip), strip[0].size[1]))
    xx = 0
    for t in strip:
        T.paste(t, (xx, 0)); xx += t.size[0]
    T.save(os.path.join(OUT, "_in", "faces_full_res.jpg"), quality=92)


if __name__ == "__main__":
    {"gen": gen, "local": local, "check": check}[sys.argv[1]](sys.argv[2:])
