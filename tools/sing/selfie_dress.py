#!/usr/bin/env python3
"""Selfie dress (Jade, 2026-10-16): a friend said neither singing reference photo looks like her (both were beautified),
so start from her real bare-faced selfie (inputs/nomakeup_selfie.png, 512x683, never overwritten) and add only light
natural makeup (lashes + lips + a little skin evening; brows untouched), light hair tidying, and the film's jacket.
Face shape, proportions and brows must not change. Candidates for her to look at; nothing is wired in.

    PY=~/Documents/1-music-shipped/moongazing/.venv/bin/python
    MPY=~/Documents/1-music-shipped/orbital-sunrise-video/video/out/.venv/bin/python   (MediaPipe, OpenCV)
    $PY  tools/sing/selfie_dress.py gen KEY [KEY ...] [--dry-run]     KEY = <model>_<take>, e.g. nbp_1 gpt_2 (tags selfie_<model>)
    $MPY tools/sing/selfie_dress.py hybrid KEY [KEY ...]              -> hyb_<KEY>.png (her own face back + local makeup)
    $MPY tools/sing/selfie_dress.py check                             -> metrics.json, contact_sheet.jpg, _in/<key>_aligned.png

Jacket reference: media/sing/selfie/_in/jacket_ref.png, the jacket cut from the pencils photo (rows 620-1086) with her
chin/neck painted black, so no face goes in as a reference. flux-1-kontext takes one image only, so it gets the jacket
in words. `check` similarity-fits each candidate onto the selfie and measures shape: landmark residuals, per-feature
proportion ratios and brow geometry, against a noise floor (the selfie itself upscaled 3x and re-detected).
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "inputs/nomakeup_selfie.png")          # 512x683
OUT = os.path.join(ROOT, "media/sing/selfie")
JACKET = os.path.join(OUT, "_in", "jacket_ref.png")
W0, H0 = 512, 683
CROP2x3 = (28, 483, 0, 683)          # gpt-image returns 2:3 at most: 455x683 around her
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

JACKET_WORDS = (
    "a white cropped jacket with a stand-up collar with two black snaps, epaulets with silver snaps on the shoulders, a "
    "silver zip worn open, wide orange bands around the chest and the sleeves, a flat pale-blue disc on the chest on the "
    "viewer's right, and a round white patch with a thick black ring reading '1420 MHz' on her left upper sleeve (viewer's "
    "right), worn over a black turtleneck")
KEEP = (
    "Her face must stay exactly her own face, unchanged in shape and proportion: the same face width and roundness, the "
    "same jaw and chin, the same eyes at the same size and shape, the same nose width, the same mouth width and lip shape, "
    "the same neutral expression and head tilt. Her eyebrows stay exactly as they are: the same shape, thickness, arch, "
    "length and colour. Do not slim her face, enlarge her eyes, narrow her nose or jaw, reshape or groom her brows, smooth "
    "her skin, or beautify her in any way. Her glasses stay exactly as they are: thin gunmetal rectangular frames with teal "
    "temples. Keep the soft window light from the left, the room behind her, and the framing and crop. It stays a real, "
    "natural phone photo of the same person, just sharp and clean at a higher resolution.")
MAKEUP = (
    "LIGHT NATURAL MAKEUP on her own face, like a careful everyday look: her skin evened out with a light foundation and "
    "a little concealer (it may cover freckles and small moles), still showing real skin texture, not airbrushed; a soft natural rose colour on her lips; a "
    "little mascara on her lashes. Nothing else: no eyeliner, no contouring, no blush, no highlighter, and nothing at all "
    "on her eyebrows.\n"
    "You may also tidy her hair lightly: smooth the flyaways and give it a little more shine and body and tidier ends. "
    "Same length, colour, centre part and loose down style.\n\n")
PROMPT = (
    "IMAGE 1 is a real, unretouched phone selfie of a woman. IMAGE 2 is only a clothing reference: a white jacket over a "
    "black turtleneck (the black area at its neck is not a person). Make exactly these changes to IMAGE 1:\n\n"
    "1. CLOTHES. Replace her black top with the floral velvet panel by the jacket in IMAGE 2: " + JACKET_WORDS + ". It "
    "sits on her shoulders at the same pose, size and position as her current top, and her long hair falls over the "
    "jacket's shoulders and front exactly as it falls over her top now. Take only the jacket and turtleneck from IMAGE 2: "
    "no face, no hair, no skin, no background.\n\n2. " + MAKEUP + KEEP)
PROMPT_1IMG = (
    "This is a real, unretouched phone selfie of a woman. Make exactly these changes:\n\n"
    "1. CLOTHES. Replace her black top with the floral velvet panel by " + JACKET_WORDS + ". It sits on her shoulders at "
    "the same pose, size and position as her current top, and her long hair falls over the jacket's shoulders and front "
    "exactly as it falls over her top now.\n\n2. " + MAKEUP + KEEP)
TRYON = ("Dress her in the white jacket from the garment image (orange bands, pale-blue disc on the chest, round "
         "black-ringed '1420 MHz' patch on the left sleeve), worn open over the black turtleneck. Keep her face, glasses "
         "and long hair exactly as they are.")

# take 2 prompts, written after looking at take 1: gpt and flux-2 opened her eyes wider (+7..15 % eye height/width),
# seedream gave her a red gradient lip, nano-banana-pro made the frames silver and the makeup almost invisible,
# kontext made a different, beautified person.
EYES = (" Her eyes in particular: the same relaxed, slightly hooded upper lids, the same eye opening and the same amount of "
        "iris showing; do not open her eyes wider or make them rounder or bigger. Her glasses keep their colour: dark "
        "gunmetal-green metal with teal on the temples and nose pads.")
VISIBLE = ("The makeup should be noticeable side by side with the original, but still light and natural: an even, fresh "
           "complexion, softly tinted lips (a sheer natural rose, not lipstick, not a gradient lip, not red) and defined "
           "lashes. ")
PROMPT2 = PROMPT.replace("2. LIGHT NATURAL", "2. LIGHT NATURAL").replace(MAKEUP, MAKEUP + VISIBLE) + EYES
PROMPT2_1IMG = PROMPT_1IMG.replace(MAKEUP, MAKEUP + VISIBLE) + EYES + (
    " This is the same real woman: do not replace her with a model or change her ethnicity, age or face.")
TRYON2 = ("Replace her floral top completely: she wears a plain black turtleneck (no floral pattern visible anywhere) and "
          "over it the white jacket from the garment image, worn open, with its orange bands, the pale-blue disc on the "
          "chest and the round black-ringed '1420 MHz' patch on her left sleeve. Her long hair stays down in front of the "
          "jacket on both sides. Keep her face, glasses and hair exactly as they are.")
# take 3 for seedream: take 2 kept her shape but brightened and smoothed her skin like a beauty filter
PROMPT3 = PROMPT2 + (" Keep the photo's exposure, white balance and her natural skin tone; no brightening, no beauty "
                     "filter, no soft-focus skin: pores and fine texture stay visible.")
PROMPTS = {"p3": PROMPT3, "p1": PROMPT, "p1k": PROMPT_1IMG, "tryon": TRYON, "p2": PROMPT2, "p2k": PROMPT2_1IMG, "tryon2": TRYON2}

# short -> (model, builder(prompt, selfie_file, jacket_file), selfie crop)
MODELS = {
    "nbp": ("google/nano-banana-pro", lambda p, s, j: {"prompt": p, "aspect_ratio": "3:4", "image_size": "2K",
                                                        "output_format": "png", "image_input": [s, j]}, None),
    "nb2": ("google/nano-banana-2", lambda p, s, j: {"prompt": p, "aspect_ratio": "3:4", "resolution": "2K",
                                                      "output_format": "png", "image_input": [s, j]}, None),
    "gpt": ("openai/gpt-image-2.5-flare", lambda p, s, j: {"prompt": p, "size": "1024x1536", "quality": "high",
                                                            "output_format": "png", "images": [s, j]}, CROP2x3),
    "sdr": ("bytedance/seedream-5-pro", lambda p, s, j: {"prompt": p, "size": "1536x2048", "watermark": False,
                                                          "image": [s, j]}, None),
    "kontext": ("black-forest-labs/flux-1-kontext-max", lambda p, s, j: {"prompt": p, "input_image": s, "aspect_ratio": "3:4",
                                                                          "output_format": "png"}, None),
    "flux2": ("black-forest-labs/flux-2-max", lambda p, s, j: {"prompt": p, "input_images": [s, j], "width": 1536,
                                                               "height": 2048, "output_format": "png"}, None),
    "tryon": ("pruna/p-image-try-on", lambda p, s, j: {"person_image": "file:media/sing/selfie/_in/selfie.jpg",
                                                        "garment_images": ["file:media/sing/selfie/_in/jacket_ref.jpg"],
                                                        "prompt": p, "turbo": False,
                                                        "output_format": "png", "output_quality": 95,
                                                        "preserve_input_size": False}, None),
}
DEFAULT_PROMPT = {"kontext": "p1k", "tryon": "tryon"}


def src_for(short):
    from PIL import Image
    crop = MODELS[short][2]
    if crop is None:
        return SRC
    p = os.path.join(OUT, "_in", "selfie_crop2x3.png")
    if not os.path.exists(p):
        x0, x1, y0, y1 = crop
        Image.open(SRC).convert("RGB").crop((x0, y0, x1, y1)).save(p)
    return p


def gen(argv):
    sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
    import cf
    from concurrent.futures import ThreadPoolExecutor
    o = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    dry = "--dry-run" in argv
    keys = [a for a in argv if not a.startswith("--")]

    def one(key):
        short = key.rsplit("_", 1)[0]
        pk = o.get("prompt", DEFAULT_PROMPT.get(short, "p1"))
        prompt = PROMPTS[pk]
        model, mk, crop = MODELS[short]
        if os.path.exists(os.path.join(OUT, f"{key}.json")) and not dry:
            print("exists, skipped:", key); return key, None
        s = src_for(short)
        inp = mk(prompt, "file:" + os.path.relpath(s, ROOT), "file:" + os.path.relpath(JACKET, ROOT))
        tag = f"selfie_{short}"
        try:
            est, why = cf.estimate(model, inp)
            paths = cf.generate(model, inp, os.path.join(OUT, key + ".png"), tag=tag, dry_run=dry)
        except Exception as e:  # noqa: BLE001
            print(f"[fail] {key}: {str(e)[:400]}", file=sys.stderr); return key, None
        if not dry:
            from PIL import Image
            json.dump({"key": key, "model": model, "prompt_key": pk, "prompt": prompt, "tag": tag,
                       "src": os.path.relpath(s, ROOT), "src_crop_x0x1y0y1": crop, "jacket_ref": os.path.relpath(JACKET, ROOT),
                       "request": {k: v for k, v in inp.items() if not (isinstance(v, str) and v.startswith("file:"))
                                   and k not in ("prompt", "images", "image_input", "image", "input_images", "garment_images")},
                       "est_usd": est, "est_basis": why, "out": [os.path.relpath(x, ROOT) for x in paths],
                       "out_size": list(Image.open(paths[0]).size)},
                      open(os.path.join(OUT, key + ".json"), "w"), indent=1)
        return key, est

    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(one, keys))
    print(json.dumps(res), f"est ${sum(e for _, e in res if e):.3f}{' (dry run)' if dry else ''}")

# ---------------------------------------------------------------------------------------------- shape metrics
BROW_R_UP, BROW_L_UP = [107, 66, 105, 63, 70], [336, 296, 334, 293, 300]      # inner -> outer, upper edge
BROW_R_LO, BROW_L_LO = [55, 65, 52, 53, 46], [285, 295, 282, 283, 276]
FLAG = 3.0                                                                     # % (ratios) or % of inter-ocular (positions)


def _d(L, a, b):
    import numpy as np
    return float(np.linalg.norm(L[a] - L[b]))


def face_frame(L):
    """Landmarks in a face frame: origin at the eye-corner midpoint, x along the eye line, unit = outer inter-ocular."""
    import numpy as np
    c = (L[33] + L[263]) / 2
    ex = (L[263] - L[33]); io = np.linalg.norm(ex); ex = ex / io
    ey = np.array([-ex[1], ex[0]])
    return np.stack([(L - c) @ ex, (L - c) @ ey], 1) / io


def jaw_at(F, y):
    """Width of the face oval at height y (face frame)."""
    import numpy as np
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import tint_match as T
    P = F[T.OVAL + [T.OVAL[0]]]
    xs = []
    for (x0, y0), (x1, y1) in zip(P[:-1], P[1:]):
        if (y0 - y) * (y1 - y) <= 0 and y0 != y1:
            xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
    return (max(xs) - min(xs)) if len(xs) >= 2 else float("nan")


def shape(L):
    """Similarity-invariant shape numbers. Ratios (compared as % change) and brow positions (compared in % of io)."""
    import numpy as np
    F = face_frame(L)
    fh, fw, io = _d(L, 10, 152), _d(L, 234, 454), _d(L, 33, 263)
    r = {"face_w/h": fw / fh,
         "jaw@mouth/face_h": jaw_at(F, (F[61, 1] + F[291, 1]) / 2) * io / fh,
         "io/face_w": io / fw,
         "eyeR_h/w": _d(L, 159, 145) / _d(L, 33, 133),
         "eyeL_h/w": _d(L, 386, 374) / _d(L, 362, 263),
         "nose_w/io": _d(L, 129, 358) / io,
         "mouth_w/io": _d(L, 61, 291) / io,
         "chin/face_h": _d(L, 17, 152) / fh}
    pos = {}
    for side, up, lo, e_in, e_out in (("R", BROW_R_UP, BROW_R_LO, 133, 33), ("L", BROW_L_UP, BROW_L_LO, 362, 263)):
        a, b = F[up[0]], F[up[-1]]
        ln = np.linalg.norm(b - a)
        n = np.array([-(b - a)[1], (b - a)[0]]) / ln
        arch = max(abs(float((F[i] - a) @ n)) for i in up[1:-1])
        r[f"brow{side}_arch/len"] = arch / ln
        r[f"brow{side}_len/io"] = ln
        r[f"brow{side}_thick/io"] = float(np.mean([np.linalg.norm(F[u] - F[l]) for u, l in zip(up, lo)]))
        pos[f"brow{side}_inner_dx"], pos[f"brow{side}_inner_dy"] = (F[up[0]] - F[e_in]).tolist()
        pos[f"brow{side}_outer_dx"], pos[f"brow{side}_outer_dy"] = (F[up[-1]] - F[e_out]).tolist()
    return r, pos


def compare(L, L0):
    """Candidate vs original: similarity-fit residuals (orig px, % io), ratio changes (%), brow position moves (% io)."""
    import cv2
    import numpy as np
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import tint_match as T
    M, _ = cv2.estimateAffinePartial2D(L[T.STABLE].astype(np.float32), L0[T.STABLE].astype(np.float32), method=cv2.LMEDS)
    Lw = L @ M[:, :2].T + M[:, 2]
    io0 = _d(L0, 33, 263)
    res = np.linalg.norm(Lw - L0, axis=1)
    r0, p0 = shape(L0)
    r1, p1 = shape(L)
    ratios = {k: round((r1[k] / r0[k] - 1) * 100, 2) for k in r0}
    pos = {k: round((p1[k] - p0[k]) * 100, 2) for k in p0}
    return {"scale_cand_px_per_orig_px": round(1 / float(np.hypot(M[0, 0], M[0, 1])), 3),
            "resid_px_mean": round(float(res.mean()), 2), "resid_px_max": round(float(res.max()), 2),
            "resid_pct_io_mean": round(float(res.mean() / io0 * 100), 2), "resid_pct_io_max": round(float(res.max() / io0 * 100), 2),
            "ratio_change_pct": ratios, "brow_pos_change_pct_io": pos}, M


def flags(c, floor=None):
    """Features over FLAG (beyond the noise floor's own deviation for that feature, if given)."""
    out = []
    for grp in ("ratio_change_pct", "brow_pos_change_pct_io"):
        for k, v in c[grp].items():
            f = abs(floor[grp][k]) if floor else 0
            if abs(v) - f > FLAG:
                out.append(f"{k} {v:+.1f}")
    return out


# ---------------------------------------------------------------------------------------------- noise floor
def noise_floor(src, L0):
    """Max |deviation| per feature when nothing changed: the selfie upscaled 3x, re-JPEG'd, blurred, sharpened, brightened."""
    import io as _io
    import cv2
    import numpy as np
    from PIL import Image
    import tint_match as T
    up = np.asarray(Image.fromarray(src).resize((W0 * 3, H0 * 3), Image.LANCZOS))
    b = _io.BytesIO(); Image.fromarray(src).save(b, "JPEG", quality=75)
    vs = [up, np.asarray(Image.open(b)), cv2.GaussianBlur(src, (0, 0), 1.0),
          cv2.addWeighted(up, 1.6, cv2.GaussianBlur(up, (0, 0), 3), -0.6, 0),
          np.clip(src.astype(int) * 1.1 + 8, 0, 255).astype(np.uint8)]
    cs = [compare(T.landmarks(v), L0)[0] for v in vs]
    fl = {g: {k: round(max(abs(c[g][k]) for c in cs), 2) for k in cs[0][g]} for g in ("ratio_change_pct", "brow_pos_change_pct_io")}
    fl["resid_px_mean"] = max(c["resid_px_mean"] for c in cs)
    fl["resid_px_max"] = max(c["resid_px_max"] for c in cs)
    return fl


# ---------------------------------------------------------------------------------------------- hybrid
EYE_UP_R = [246, 161, 160, 159, 158, 157, 173]
EYE_UP_L = [398, 384, 385, 386, 387, 388, 466]


def hybrid_face_mask(shape_, L, io):
    """Face oval with its upper half pushed out to the hairline, plus the whole glasses band; feathered."""
    import cv2
    import numpy as np
    import tint_match as T
    P = L[T.OVAL].copy()
    c = (L[33] + L[263]) / 2
    up = P[:, 1] < c[1]
    P[up] = P[up] + (P[up] - c) / np.linalg.norm(P[up] - c, axis=1)[:, None] * 0.10 * io
    lo = P[:, 1] > L[1, 1]                                   # below the nose tip: pull the jaw line in, so the feather
    P[lo] = P[lo] - (P[lo] - c) / np.linalg.norm(P[lo] - c, axis=1)[:, None] * 0.06 * io   # never lands on the collar
    m = T._poly(shape_, P)
    brow_top = min(L[T.BROW_L][:, 1].min(), L[T.BROW_R][:, 1].min()) - 0.12 * io
    band = np.array([[L[T.OVAL][:, 0].min() - 0.18 * io, brow_top], [L[T.OVAL][:, 0].max() + 0.18 * io, brow_top],
                     [L[T.OVAL][:, 0].max() + 0.18 * io, L[195, 1]], [L[T.OVAL][:, 0].min() - 0.18 * io, L[195, 1]]])
    m = np.maximum(m, T._poly(shape_, band))
    return np.clip(cv2.GaussianBlur(m, (0, 0), 0.04 * io), 0, 1)


def makeup(rgb, L, ref=None, conceal=0.45, even=0.5, lips=0.7, lash=0.18):
    """Light local makeup, no geometry: even the flush (a* blotches), conceal dark spots (freckles/moles) part way, move
    the lips toward a soft rose (or toward ref's lip colour), darken the upper lash line a touch. Brows never touched."""
    import cv2
    import numpy as np
    import tint_match as T
    ms = T.masks(rgb, L)
    io, lab, w = ms["io"], ms["lab"].copy(), ms["skin"]
    out = lab.copy()

    def wblur(x, wt, sg):
        return cv2.GaussianBlur(x * wt, (0, 0), sg) / (cv2.GaussianBlur(wt, (0, 0), sg) + 1e-4)
    exc = np.maximum(0, wblur(lab[..., 1], w, 0.08 * io) - wblur(lab[..., 1], w, 0.40 * io))
    out[..., 1] -= even * w * exc
    out[..., 2] -= 0.3 * even * w * exc
    base = wblur(lab[..., 0], w, 0.035 * io)
    dark = np.maximum(0, base - lab[..., 0] - 1.0)               # freckles / moles / blotches darker than their surround
    out[..., 0] += conceal * w * dark
    for ch in (1, 2):                                            # their brown tint goes part way to the local skin colour
        out[..., ch] += conceal * w * _ss01(dark / 6) * (wblur(lab[..., ch], w, 0.035 * io) - lab[..., ch])
    wl = ms["lips"]
    if ref is not None:
        tgt = T.stats(T.to_lab(ref), wl, 0.6)["mean"]
    else:
        cur = T.stats(lab, wl, 0.6)["mean"]
        tgt = [cur[0] - 2, cur[1] + 7, cur[2] + 1]               # a soft rose: a little redder, a touch deeper
    cur = T.stats(lab, wl, 0.6)["mean"]
    for ch in range(3):
        out[..., ch] += lips * wl * (tgt[ch] - cur[ch]) * (0.6 if ch == 0 else 1.0)
    lm = np.zeros(rgb.shape[:2], np.float32)
    for ix in (EYE_UP_R, EYE_UP_L):
        cv2.polylines(lm, [np.round(L[ix]).astype(np.int32)], False, 1.0, max(1, int(0.03 * io)))
    lm = cv2.GaussianBlur(lm, (0, 0), 0.012 * io)
    out[..., 0] *= 1 - lash * lm
    return T.from_lab(out)


def _ss01(x):
    import numpy as np
    t = np.clip(x, 0, 1)
    return t * t * (3 - 2 * t)


def hybrid(argv, cand_dir=OUT, look=None, src_path=SRC, tone=(0.5, 0.6, 0.6), sharpen=0.6, edge_tone_only=False,
           label=None, crop_invalid=False):
    """Her own face (selfie, 2x Lanczos) back onto a take, aligned by landmarks, with the local makeup on it. Works in
    the selfie's framing at 2x (1024x1366). Hair and jacket come from the take; face + hairline + glasses from her.
    look(rgb, L, ref) -> rgb replaces the round-1 makeup() (round 2 passes the glow look; round 3 passes no-op).
    edge_tone_only: tone her face toward the take's skin only in the feather ring (round 3: her own makeup stays)."""
    import cv2
    import numpy as np
    from PIL import Image
    import tint_match as T
    S2 = 2
    src = T.load(src_path)
    L0 = T.landmarks(src)
    big = np.asarray(Image.fromarray(src).resize((W0 * S2, H0 * S2), Image.LANCZOS))
    Lb = L0 * S2 + (S2 - 1) / 2
    io = _d(Lb, 33, 263)
    keys = [a for a in argv if not a.startswith("--")]
    for key in keys:
        d = json.load(open(os.path.join(cand_dir, key + ".json")))
        a = T.load(os.path.join(ROOT, d["out"][0]))
        L = T.landmarks(a)
        M, _ = cv2.estimateAffinePartial2D(L[T.STABLE].astype(np.float32), Lb[T.STABLE].astype(np.float32), method=cv2.LMEDS)
        w = cv2.warpAffine(a, M, (W0 * S2, H0 * S2), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REPLICATE)
        # her face, toned part way to the take's skin so the seam at the hairline/jaw disappears, then the makeup
        mb, mw = T.masks(big, Lb), T.masks(w, Lb)
        sb, sw = T.stats(mb["lab"], mb["skin"]), T.stats(mw["lab"], mb["skin"])
        lab = mb["lab"].copy()
        m = hybrid_face_mask(big.shape, Lb, io)[..., None]
        wt = np.clip(mb["skin"] * 1.5, 0, 1)
        if edge_tone_only:
            wt = wt * np.clip((1 - m[..., 0]) * 2.5, 0, 1)
        for ch, k in zip(range(3), tone):
            lab[..., ch] += k * (sw["mean"][ch] - sb["mean"][ch]) * wt
        face = (look or makeup)(T.from_lab(lab), Lb, ref=w).astype(np.float32)
        if sharpen:
            face = np.clip(face + sharpen * (face - cv2.GaussianBlur(face, (0, 0), 1.2)), 0, 255)   # the 2x upscale is soft
        out = np.clip(w * (1 - m) + face * m + 0.5, 0, 255).astype(np.uint8)
        if crop_invalid:   # gpt's 2:3 input leaves strips the take never covered: crop them instead of smearing
            valid = cv2.warpAffine(np.ones(a.shape[:2], np.uint8), M, (W0 * S2, H0 * S2), flags=cv2.INTER_NEAREST) > 0
            cols = np.where(valid.mean(0) > 0.98)[0]
            rows = np.where(valid[:, cols].mean(1) > 0.98)[0] if len(cols) else cols
            if len(cols) and len(rows) and (len(cols) < valid.shape[1] or len(rows) < valid.shape[0]):
                out = out[rows[0]:rows[-1] + 1, cols[0]:cols[-1] + 1]
                m = m[rows[0]:rows[-1] + 1, cols[0]:cols[-1] + 1]
        name = "hyb_" + key
        os.makedirs(os.path.join(cand_dir, "_in"), exist_ok=True)
        Image.fromarray(out).save(os.path.join(cand_dir, name + ".png"))
        Image.fromarray((m[..., 0] * 255).astype(np.uint8)).save(os.path.join(cand_dir, "_in", name + "_mask.png"))
        json.dump({"key": name, "model": label or ("hybrid (no paid call): selfie face + local " + ("glow" if look else "makeup") + " on " + key),
                   "base": key, "est_usd": 0, "out": [os.path.relpath(os.path.join(cand_dir, name + ".png"), ROOT)]},
                  open(os.path.join(cand_dir, name + ".json"), "w"), indent=1)
        print("wrote", name)


# ---------------------------------------------------------------------------------------------- check + sheet
VERDICT = {      # written after looking at every image at 2x face crops (see media/sing/selfie/README.md)
    "nbp_1": ("OK", "faithful; makeup barely visible; frames silver"),
    "nbp_2": ("REJECT", "eyes enlarged +19/+15%, mouth -8%"),
    "nb2_1": ("PICK", "within floor; light visible makeup"),
    "nb2_2": ("OK", "eyes a touch more open (visible)"),
    "nb2_3": ("REJECT", "eyes +11/+9%, brows re-arched +8%"),
    "nb2_4": ("OK", "faithful, close 2nd to nb2_1"),
    "gpt_1": ("REJECT", "eyes enlarged +10/+7%, smoothed"),
    "gpt_2": ("OK", "shape fine; skin smoothed; best jacket"),
    "gpt_3": ("OK", "shape fine; skin smoothed"),
    "sdr_1": ("REJECT", "red gradient lipstick, filter skin"),
    "sdr_2": ("OK", "shape fine; beauty-filter skin"),
    "sdr_3": ("REJECT", "chin +5.5%, red gradient lip again"),
    "kontext_1": ("REJECT", "a different, beautified person"),
    "kontext_2": ("REJECT", "a different person; brows reshaped"),
    "flux2_1": ("REJECT", "eyes +15/+9%, chin -6%, blotchy skin"),
    "flux2_2": ("REJECT", "nose +4%, mottled skin"),
    "tryon_1": ("REJECT", "floral top shows; no makeup"),
    "tryon_2": ("REJECT", "floral top shows; odd collar"),
    "hyb_nb2_2": ("PICK", "her face exactly + nb2_2 jacket/hair"),
    "hyb_nb2_1": ("OK", "her face exactly; patch half hidden"),
    "hyb_nb2_4": ("OK", "her face exactly"),
    "hyb_nbp_1": ("OK", "her face exactly; silver-frame temples"),
    "hyb_sdr_1": ("OK", "her face exactly; patch cut off"),
    "hyb_sdr_2": ("OK", "her face exactly; patch cut off"),
    "hyb_flux2_1": ("OK", "her face exactly (chin flag = neck ctx)"),
    "hyb_gpt_1": ("REJECT", "edge smears (gpt 2:3 crop)"),
    "hyb_gpt_2": ("REJECT", "edge smears (gpt 2:3 crop)"),
}


def _order(key):
    """Sort: route/round prefix, model order, take; hybrids last."""
    parts = key.split("_")
    hyb = parts[0] == "hyb"
    if hyb:
        parts = parts[1:]
    route = parts[0] if parts[0] not in MODELS else ""
    short = parts[1] if route else parts[0]
    return (hyb, route, list(MODELS).index(short) if short in MODELS else 99, key)


def skin_stats(img1x, ms):
    """Mean L*a*b* and texture energy (mean |L - blur(L, 1.2 px)|) in the cheek and lip regions, at the source's 1x scale."""
    import cv2
    import numpy as np
    import tint_match as T
    lab = T.to_lab(img1x)
    hp = np.abs(lab[..., 0] - cv2.GaussianBlur(lab[..., 0], (0, 0), 1.2))
    out = {}
    for n, w, thr in (("cheeks", ms["cheeks"], 0.5), ("lips", ms["lips"], 0.6), ("skin", ms["skin"], 0.8)):
        m = w > thr
        out[n] = {"Lab": lab[m].mean(0).round(2).tolist(), "tex": round(float(hp[m].mean()), 3)}
    return out


def skin_compare(s, s0):
    import numpy as np
    r = {}
    for n in s0:
        a, b = s[n]["Lab"], s0[n]["Lab"]
        r[n] = {"dL": round(a[0] - b[0], 2), "dE_ab": round(float(np.hypot(a[1] - b[1], a[2] - b[2])), 2),
                "tex_ratio": round(s[n]["tex"] / s0[n]["tex"], 3)}
    return r


SKIN_FLAG = {"tex_ratio_below": 0.60, "tex_note_below": 0.80, "dE_ab": 3.0, "dL": 4.0}   # beyond the floor's own deviation
# Jade (round 3): light smoothing / freckle removal is fine -> only texture below 0.6x (heavy airbrushing) is a flag;
# 0.6-0.8x is noted as "light smoothing". Recolouring (a*b* or L) stays a flag.


def skin_flags(sc, floor=None):
    out = []
    for n, v in sc.items():
        f = floor[n] if floor else {"dL": 0, "dE_ab": 0, "tex_ratio": 1}
        if v["tex_ratio"] < SKIN_FLAG["tex_ratio_below"] * min(1, f["tex_ratio"]):
            out.append(f"{n} airbrushed x{v['tex_ratio']:.2f}")
        if v["dE_ab"] - f["dE_ab"] > SKIN_FLAG["dE_ab"]:
            out.append(f"{n} recoloured dE{v['dE_ab']:.1f}")
        if abs(v["dL"]) - abs(f["dL"]) > SKIN_FLAG["dL"]:
            out.append(f"{n} L{v['dL']:+.1f}")
    return out


def check(argv, cand_dir=OUT, sheet="contact_sheet.jpg", metrics_name="metrics.json", head=(), verdict=None,
          src_path=SRC, skin=False, src_label="ORIGINAL selfie"):
    """head: [(label, path)] images shown right after the original (e.g. the round-1 pick), measured like candidates."""
    verdict = VERDICT if verdict is None else verdict
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    import tint_match as T
    src = T.load(src_path)
    L0 = T.landmarks(src)
    floor = noise_floor(src, L0)
    if skin:
        import io as _io
        ms0 = T.masks(src, L0)
        s0 = skin_stats(src, ms0)
        b = _io.BytesIO(); Image.fromarray(src).save(b, "JPEG", quality=75)
        up = np.asarray(Image.fromarray(src).resize((W0 * 3, H0 * 3), Image.LANCZOS).resize((W0, H0), Image.LANCZOS))
        fls = [skin_compare(skin_stats(v, ms0), s0) for v in (up, np.asarray(Image.open(b)))]
        floor["skin"] = {n: {k: (min(f[n][k] for f in fls) if k == "tex_ratio" else max(abs(f[n][k]) for f in fls))
                             for k in fls[0][n]} for n in fls[0]}
    S2 = 2
    big = np.asarray(Image.fromarray(src).resize((W0 * S2, H0 * S2), Image.LANCZOS))
    Lb = L0 * S2 + (S2 - 1) / 2
    cands = []
    for f in sorted(os.listdir(cand_dir)):
        if f.endswith(".json") and not f.startswith("metrics"):
            d = json.load(open(os.path.join(cand_dir, f)))
            if d.get("out") and os.path.exists(os.path.join(ROOT, d["out"][0])):
                cands.append(d)
    cands.sort(key=lambda d: _order(d["key"]))
    cands = [{"key": h[0], "model": "reference", "out": [os.path.relpath(h[1], ROOT)], "noalign": len(h) > 2 and h[2] == "noalign"}
             for h in head] + cands
    os.makedirs(os.path.join(cand_dir, "_in"), exist_ok=True)
    metrics, tiles = {"_noise_floor": floor}, {"original": big}
    for d in cands:
        a = T.load(os.path.join(ROOT, d["out"][0]))
        if d.get("noalign"):            # a different photo shown for comparison only: fitted into the frame, not measured
            im = Image.fromarray(a); im.thumbnail((W0 * S2, H0 * S2), Image.LANCZOS)
            t = Image.new("RGB", (W0 * S2, H0 * S2), (28, 28, 30)); t.paste(im, ((W0 * S2 - im.size[0]) // 2, (H0 * S2 - im.size[1]) // 2))
            tiles[d["key"]] = np.asarray(t)
            metrics[d["key"]] = {"model": d["model"], "out_size": [a.shape[1], a.shape[0]], "noalign": True}
            continue
        L = T.landmarks(a)
        if L is None:
            print("no face:", d["key"]); continue
        c, M = compare(L, L0)
        c["model"], c["out_size"] = d["model"], [a.shape[1], a.shape[0]]
        c["flags_over_3"] = flags(c)
        c["flags_beyond_floor+3"] = flags(c, floor)
        if skin:
            w1 = cv2.warpAffine(a, M, (W0, H0), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REPLICATE)
            c["skin"] = skin_compare(skin_stats(w1, ms0), s0)
            c["skin_flags"] = skin_flags(c["skin"], floor["skin"])
        metrics[d["key"]] = c
        M2 = M * S2; M2[:, 2] += (S2 - 1) / 2
        tiles[d["key"]] = cv2.warpAffine(a, M2, (W0 * S2, H0 * S2), flags=cv2.INTER_AREA, borderValue=(28, 28, 30))
        Image.fromarray(tiles[d["key"]]).save(os.path.join(cand_dir, "_in", d["key"] + "_aligned.jpg"), quality=92)
        rc = c["ratio_change_pct"]
        print(f"{d['key']:14s} {c['out_size']} resid {c['resid_px_mean']}/{c['resid_px_max']}px  "
              + " ".join(f"{k}:{v:+.1f}" for k, v in rc.items()) + "\n             brows " +
              " ".join(f"{k[4:]}:{v:+.1f}" for k, v in c["brow_pos_change_pct_io"].items()) +
              "\n             FLAGS(>3%): " + ", ".join(c["flags_over_3"]) + "  | beyond floor+3: " + ", ".join(c["flags_beyond_floor+3"]) +
              ("\n             skin " + json.dumps(c["skin"]) + "  FLAGS: " + ", ".join(c["skin_flags"]) if skin else ""))
    json.dump(metrics, open(os.path.join(cand_dir, metrics_name), "w"), indent=1)

    def font(sz):
        for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
            if os.path.exists(p):
                return ImageFont.truetype(p, sz)
        return ImageFont.load_default()

    def small(sz):
        p = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        return ImageFont.truetype(p, sz) if os.path.exists(p) else font(sz)

    keys = list(tiles)
    cols = min(7, len(keys))
    tw, th = 330, 440
    fx0, fy0 = int((L0[:, 0].min() - 0.35 * _d(L0, 33, 263)) * S2), int((L0[:, 1].min() - 0.45 * _d(L0, 33, 263)) * S2)
    fx1, fy1 = int((L0[:, 0].max() + 0.35 * _d(L0, 33, 263)) * S2), int((L0[:, 1].max() + 0.15 * _d(L0, 33, 263)) * S2)
    fh = round(tw * (fy1 - fy0) / (fx1 - fx0))
    lab_h, pad = (128 if skin else 114), 12
    rows = -(-len(keys) // cols)
    cell_h = lab_h + th + 6 + fh
    S = Image.new("RGB", (cols * (tw + pad) + pad, rows * (cell_h + pad) + pad + 26), (28, 28, 30))
    dr = ImageDraw.Draw(S)
    short = {"face_w/h": "fw/h", "jaw@mouth/face_h": "jaw", "io/face_w": "io/fw", "eyeR_h/w": "eyeR", "eyeL_h/w": "eyeL",
             "nose_w/io": "nose", "mouth_w/io": "mouth", "chin/face_h": "chin"}
    for i, k in enumerate(keys):
        x, y = pad + (i % cols) * (tw + pad), pad + (i // cols) * (cell_h + pad)
        S.paste(Image.fromarray(tiles[k]).resize((tw, th), Image.LANCZOS), (x, y + lab_h))
        S.paste(Image.fromarray(tiles[k][fy0:fy1, fx0:fx1]).resize((tw, fh), Image.LANCZOS), (x, y + lab_h + th + 6))
        if k == "original":
            dr.text((x + 2, y), src_label, fill=(255, 255, 255), font=font(19))
            dr.text((x + 2, y + 24), os.path.relpath(src_path, ROOT)[7:] + " 512x683", fill=(170, 170, 175), font=font(12))
            dr.text((x + 2, y + 40), f"floor: resid {floor['resid_px_mean']}/{floor['resid_px_max']}px", fill=(170, 170, 175), font=font(12))
            dr.text((x + 2, y + 56), "floor ratios: eyes up to %.1f%%," % max(floor["ratio_change_pct"]["eyeR_h/w"], floor["ratio_change_pct"]["eyeL_h/w"]),
                    fill=(170, 170, 175), font=font(12))
            dr.text((x + 2, y + 72), "  others up to %.1f%%" % max(v for kk, v in floor["ratio_change_pct"].items() if "eye" not in kk),
                    fill=(170, 170, 175), font=font(12))
            continue
        c = metrics[k]
        st, words = verdict.get(k, ("?", ""))
        col = {"PICK": (120, 220, 140), "OK": (200, 200, 120), "REJECT": (240, 120, 110)}.get(st, (200, 200, 200))
        if c.get("noalign"):
            dr.text((x + 2, y), f"{k}  {st}", fill=col, font=font(17))
            dr.text((x + 2, y + 21), f"{c['out_size'][0]}x{c['out_size'][1]}  different photo: not measured", fill=(170, 170, 175), font=small(11))
            dr.text((x + 2, y + 40), words[:46], fill=col, font=font(12))
            continue
        rc, bp = c["ratio_change_pct"], c["brow_pos_change_pct_io"]
        g = (170, 170, 175)
        dr.text((x + 2, y), f"{k}  {st}", fill=col, font=font(17))
        dr.text((x + 2, y + 21), f"{c['model'].split('/')[-1][:34]}  {c['out_size'][0]}x{c['out_size'][1]}", fill=g, font=small(11))
        dr.text((x + 2, y + 35), f"resid {c['resid_px_mean']}/{c['resid_px_max']}px  " + " ".join(f"{short[q]} {rc[q]:+.1f}" for q in list(short)[:3]), fill=g, font=small(11))
        dr.text((x + 2, y + 49), " ".join(f"{short[q]} {rc[q]:+.1f}" for q in list(short)[3:]), fill=g, font=small(11))
        dr.text((x + 2, y + 63), f"brow arch {rc['browR_arch/len']:+.1f}/{rc['browL_arch/len']:+.1f}  len {rc['browR_len/io']:+.1f}/{rc['browL_len/io']:+.1f}"
                f"  ends max {max(abs(v) for v in bp.values()):.1f}%io", fill=g, font=small(11))
        fl = c["flags_beyond_floor+3"]
        dr.text((x + 2, y + 78), ("FLAG " + ", ".join(f.replace("_h/w", "").replace("/face_h", "").replace("/io", "") for f in fl))[:52]
                if fl else "no flags beyond floor+3%", fill=(240, 120, 110) if fl else (120, 220, 140), font=small(11))
        if skin:
            sk, sf = c["skin"], c["skin_flags"]
            dr.text((x + 2, y + 92), f"skin tex x{sk['cheeks']['tex_ratio']:.2f}/lips x{sk['lips']['tex_ratio']:.2f} "
                    f"dE {sk['cheeks']['dE_ab']:.1f}/{sk['lips']['dE_ab']:.1f}" + ("  " + sf[0] if sf else ""),
                    fill=(240, 120, 110) if sf else (120, 220, 140), font=small(11))
        dr.text((x + 2, y + (108 if skin else 94)), words[:46], fill=col, font=font(12))
    dr.text((pad, S.size[1] - 24), "Each image mapped onto the selfie by a similarity fit (eyes/nose/brows/temples). Ratios are % change vs the selfie; "
            "FLAG = more than 3% beyond the noise floor. Face crops at the same scale.", fill=(170, 170, 175), font=font(13))
    S.save(os.path.join(OUT, sheet), quality=90)
    print("sheet", S.size)


if __name__ == "__main__":
    {"gen": gen, "hybrid": hybrid, "check": check}[sys.argv[1]](sys.argv[2:])
