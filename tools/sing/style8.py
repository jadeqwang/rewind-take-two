#!/usr/bin/env python3
"""Style stills v8 (2026-10-18): Chinese watercolour looks for the two singing shots, built from Jade's two new selfies.
Look test only: STILLS, wired into nothing, no video. Question for Jade: can a painted Jade bring back what the original
watercolour had (a calm, slightly sultry painted portrait that mismatches the engraved plates) without losing likeness?

    S1  inputs/selfie_hairup_jade_jacket_retouch_v2.png  (via its v7 outpaint, media/sing/outpaint/v7/S1_nbp_2_merged.png)
    V3S inputs/selfie_hairdown_jade_jacket_retouch_v2.png (via media/sing/outpaint/v7/V3S_nbp_5_merged.png)
    The outpaint canvases carry her own pixels everywhere the selfie shows; they only add shoulders and lower chest.

Styles: wash (水彩/淡彩 Chinese watercolour), gongbi (淡彩工笔 light-colour fine line), xieyi (写意-leaning ink wash, face
controlled). Models: nbp = google/nano-banana-pro (strong style, drifts faces), gpt = openai/gpt-image-2.5-flare (keeps
faces), sdr = bytedance/seedream-5-pro.

Likeness-protecting routes (each writes a new still beside its parent):
    <key>__lock   landmark face lock: the painted face's geometry warped back onto her photo's landmarks (thin-plate
                  spline on MediaPipe landmarks, similarity-aligned, feathered to the face; mouth interior excluded)
    <key>__fix    model alternation: gpt-image-2.5-flare gets the painting AND her photo and is asked to correct only the
                  face's proportions to the photo, keeping the painting's style

    PY=~/Documents/1-music-shipped/moongazing/.venv/bin/python             # cf.py (spend log + cap)
    EPY=tools/engrave/.venv/bin/python                                      # torch + BiRefNet
    MPY=~/Documents/1-music-shipped/orbital-sunrise-video/video/out/.venv/bin/python   # OpenCV + MediaPipe
    $PY  tools/sing/style8.py prep                    -> media/sing/style/v8/_in/*.png (model inputs)
    $PY  tools/sing/style8.py gen [PATTERN ...] [--dry-run]   -> v8/<style>_<shot>__<model>_<n>.png + .json
    $PY  tools/sing/style8.py fix KEY [KEY ...] [--dry-run]   -> v8/<key>__fix.png + .json
    $MPY tools/sing/style8.py lock KEY [KEY ...]      -> v8/<key>__lock.png + .json
    $MPY tools/sing/style8.py metrics                 -> v8/likeness.json, v8/likeness.tsv
    $EPY tools/sing/style8.py matte [--force]         -> v8/_matte/<key>.png
    $MPY tools/sing/style8.py comp                    -> v8/<key>_comp.jpg (on the plate, v7 geometry, a little wider)
    $MPY tools/sing/style8.py faces                   -> v8/_faces.jpg (face crops at one scale, for checking)
    $MPY tools/sing/style8.py sheet KEY,KEY,.. KEY,KEY,..  -> v8/contact_sheet.jpg (row S1 keys, row V3S keys)

Calls are logged and capped by tools/gen/cf.py (tags style8_<style>, style8_fix)."""
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "media/sing/style/v8")
SHOTS = {
    "S1": dict(canvas="media/sing/outpaint/v7/S1_nbp_2_merged.png", source="inputs/selfie_hairup_jade_jacket_retouch_v2.png",
               plate="media/sing/plates/plate_close_1.jpg", v7="media/sing/first/v7_S1_first.jpg", pad_bottom=120),
    "V3S": dict(canvas="media/sing/outpaint/v7/V3S_nbp_5_merged.png", source="inputs/selfie_hairdown_jade_jacket_retouch_v2.png",
                plate="media/sing/plates/plate_truth_1.jpg", v7="media/sing/first/v7_V3S_first.jpg", pad_bottom=0),
}
WC_REF = "media/sing/S1/v4_sync_1080.mp4"           # the original watercolour singing take (reference frame at 1.0 s)

# model -> (catalog name, aspect of the input sent, request builder)
MODELS = {
    "nbp": ("google/nano-banana-pro", "native",
            lambda p, fs, ar: {"prompt": p, "aspect_ratio": ar, "image_size": "2K", "output_format": "png", "image_input": fs}),
    "gpt": ("openai/gpt-image-2.5-flare", "3:2",
            lambda p, fs, ar: {"prompt": p, "size": "1536x1024", "quality": "high", "output_format": "png", "images": fs}),
    "sdr": ("bytedance/seedream-5-pro", "native",
            lambda p, fs, ar: {"prompt": p, "size": "2240x1792" if ar == "5:4" else "2304x1728", "watermark": False,
                               "image": fs if len(fs) > 1 else fs[0]}),
}

# ------------------------------------------------------------------------------------------------- prompts
STYLE = {
    "wash": (
        "Repaint this whole photograph as a Chinese watercolour portrait (水彩 / 淡彩) on warm, soft rice paper (宣纸). "
        "Soft, transparent washes of colour that bloom and feather into the paper, wet edges, gentle granulation, the white "
        "of the paper glowing through in the highlights; a few fluid, gentle ink lines only where a form needs them (the "
        "glasses frame, the eyelids, a few strands of hair, the collar). Her hair is layered ink wash, from deep black to "
        "soft grey, with a few loose painted strands. Her skin is warm and luminous, laid in with pale ochre and rose. "
        "Warm golden light falls on her from the picture's left side; the far side of her face turns into a soft, cool "
        "shadow under the cheekbone, with a gentle warm flush on her cheeks. Every area is visibly made of brushed washes "
        "on paper: no photographic texture, no gloss, not a filter over a photo. "),
    "glow": (
        "Repaint this whole photograph as a Chinese watercolour portrait (水彩 / 淡彩) on warm, soft rice paper (宣纸), lit "
        "like a quiet evening portrait. Soft, transparent washes that bloom and feather into the paper, wet edges, the white "
        "of the paper glowing through; a few fluid ink lines only where a form needs them. Her hair is layered ink wash with "
        "a few loose painted strands. A low, warm golden light falls across her from the picture's left: that side of her "
        "face and hair glows amber, the other side of her face turns into a soft, cool violet-grey shadow, with a clear "
        "shadow under the cheekbone and along the jaw, and a warm rose flush across her cheeks and the bridge of her nose. "
        "Her expression is calm, intimate and a little dreamy: brows relaxed and low (not raised), upper eyelids relaxed a "
        "touch lower over the eyes, which still look into the lens; lips soft and relaxed. Every area is visibly made of "
        "brushed washes on paper: no photographic texture, no gloss, not a filter over a photo. "),
    "gongbi": (
        "Repaint this whole photograph as a light-colour gongbi portrait (淡彩工笔) on warm cream xuan paper. A fine, even, "
        "unbroken ink line of uniform weight (铁线描) traces every contour: the outline of her face, her eyelids, brows, "
        "nose and lips, the glasses frame, the flowing locks of her hair, the jacket's collar, seams, snaps and zip. Inside "
        "the lines the colour is pale and transparent, laid in thin layered washes and gently graded for form (渲染), with "
        "plenty of paper left showing: pale pearl white for the jacket, cinnabar orange for its bands, azurite blue for the "
        "disc, soft ink for the turtleneck, layered ink for her hair, warm ochre and soft rose for her skin. A subtle warm "
        "light from the picture's left side, a soft flush on her cheeks. Refined, delicate and graphic; no oil paint, no "
        "gloss, no photographic texture. "),
    "xieyi": (
        "Repaint this whole photograph as a Chinese ink-and-colour portrait leaning toward xieyi (写意) on warm rice paper. "
        "Her hair and her jacket are painted with loose, confident, expressive brush strokes: the hair in wet, splashed ink "
        "(泼墨, 破墨) running from rich black to silver grey, with a few dry-brush flicks for loose strands; the white "
        "jacket suggested with a few broad, pale grey strokes and bare paper; the orange bands as single bold strokes of "
        "vermilion wash; the blue disc a single round dab of azurite; the black turtleneck a dark ink wash. Her face, in "
        "contrast, is painted with control and care in soft, transparent washes and a few fine lines, so that every feature "
        "stays exact. Warm light from the picture's left side with a soft flush on her cheeks. Painted by hand with a "
        "Chinese brush: not a photo, not a filter, not anime. "),
}
LIKENESS = (
    "This is a portrait of a specific real woman and she must stay instantly recognisable as herself. Keep her exact "
    "likeness and proportions from the photo: the same face shape and width, the same full cheeks, jaw and chin; the same "
    "forehead and hairline; her own two eyebrows, each keeping its own shape, thickness and height; her own eye shape and "
    "size (do not enlarge them, do not narrow them into almond eyes, no double eyelid that is not in the photo); the same "
    "nose; the same mouth at its real width and fullness. Do not beautify, slim, idealise, age or de-age her; no glossy "
    "lips, no lipstick, no heavy makeup; not a classical court lady, not a generic model. Keep her expression exactly as in "
    "the photo, with the lips softly parted as in the photo, not smiling; a calm, relaxed gaze into the lens. Keep the "
    "angle and tilt of her head. Her thin gunmetal-and-teal metal glasses keep exactly the same rectangular frame shape and "
    "size, with both lenses. ")
OUTFIT = {
    "S1": ("Her hair is up in the loose, messy bun with its flyaway strands, with two yellow pencils pushed through the "
           "bun like hairpins, pointing up and outward: the one on the picture's left has a pink eraser, the one on the "
           "picture's right a pale-blue eraser; both pencils and both erasers stay visible. "),
    "V3S": ("Her long dark hair is down, centre-parted, falling over her shoulders and the front of her jacket as in the "
            "photo. "),
}
JACKET = (
    "Keep her clothes exactly: the white jacket with its stand-up collar fastened with metal snaps, the snap studs on the "
    "shoulders, the silver zip, the horizontal orange bands across the chest and arms, the pale-blue circle on the chest, "
    "and the round black-rimmed sleeve patch on her left arm (the picture's right) whose text reads exactly \"1420\" over "
    "\"MHz\"; the black ribbed turtleneck. No headphones. Keep the framing, pose and composition of the photo exactly, the "
    "same size and position of her head and body; do not crop, zoom or move her. Paint her jacket all the way down to the "
    "bottom edge of the picture (any blurred strip at the bottom or sides is more of the same jacket, or empty paper). ")
GROUND = ("Replace the room behind her with plain, empty, warm cream rice paper: nothing behind her, no landscape, no "
          "flowers, no branches, no objects, no seals, no inscription, no signature, no calligraphy, no text anywhere except "
          "the 1420 MHz patch. ")


def prompt_for(style, shot):
    return STYLE[style] + LIKENESS + OUTFIT[shot] + JACKET + GROUND


FIX_PROMPT = (
    "Image 1 is a hand-painted Chinese {style} portrait. Image 2 is a photograph of the same woman, in the same pose. "
    "Edit image 1 so that her face matches image 2 exactly in its proportions and features: the width and shape of her "
    "face, cheeks, jaw and chin; the size, shape and spacing of her eyes and eyelids; her eyebrows (shape, thickness and "
    "height); her nose; the width and fullness of her mouth and how far the lips are parted. Her lips are soft and matte, "
    "no gloss. Do not make her slimmer, younger, older or prettier than in image 2. Keep everything else of image 1 "
    "unchanged: the painting style, the brushwork, the paper, the colours, the warm side light and flush, the hair, the "
    "glasses, the jacket and its patch, the framing and the size of the picture. The result must still look entirely "
    "hand-painted in the style of image 1, not like a photo, with no text added.")
FIX_KEEP_EXPR = (
    " Exception: keep image 1's expression where it differs from the photo (her relaxed, low brows, her calm, slightly "
    "lowered eyelids, how far her lips are parted), and its warm side light, shadows and flush; correct only the "
    "structure and proportions of her face to image 2.")
FIX_HAIR = (" Her hair is black, as in image 2: where the warm light touches it, it is glossy black with a warm sheen, never "
            "brown or auburn.")
STYLE_NAME = {"glow": "watercolour (水彩)", "wash": "watercolour (水彩)", "gongbi": "light-colour gongbi (淡彩工笔)", "xieyi": "xieyi ink-wash (写意)"}

JOBS = [(st, sh, m) for st in STYLE for sh in SHOTS for m in MODELS if st != "glow" or m == "nbp"]


def rd(p, mode="RGB"):
    import numpy as np
    from PIL import Image
    return np.asarray(Image.open(p if os.path.isabs(p) else os.path.join(ROOT, p)).convert(mode))


# ------------------------------------------------------------------------------------------------- prep
def native(shot):
    """The outpaint canvas (2400x1800) with its bottom padded for the wider framing: 5:4 for S1, 4:3 for V3S."""
    import numpy as np
    from PIL import Image, ImageFilter
    p = os.path.join(OUT, "_in", f"{shot}_native.png")
    if os.path.exists(p):
        return p
    a = rd(SHOTS[shot]["canvas"])
    pb = SHOTS[shot]["pad_bottom"]
    if pb:
        b = np.pad(a, ((0, pb), (0, 0), (0, 0)), mode="edge")
        big = np.asarray(Image.fromarray(b).filter(ImageFilter.GaussianBlur(6)))
        b = b.copy()
        b[a.shape[0]:] = big[a.shape[0]:]
        a = b
    os.makedirs(os.path.dirname(p), exist_ok=True)
    Image.fromarray(a).save(p)
    return p


def wide(shot):
    """The native input padded left/right (blurred edge colour) to 3:2 for gpt-image."""
    import numpy as np
    from PIL import Image, ImageFilter
    p = os.path.join(OUT, "_in", f"{shot}_3x2.png")
    if os.path.exists(p):
        return p
    a = rd(native(shot))
    h, w = a.shape[:2]
    W = round(h * 1.5)
    px = (W - w) // 2
    b = np.pad(a, ((0, 0), (px, W - w - px), (0, 0)), mode="edge")
    big = Image.fromarray(b).filter(ImageFilter.GaussianBlur(30))
    big.paste(Image.fromarray(a), (px, 0))
    big.save(p)
    return p


def aspect(shot):
    return "5:4" if SHOTS[shot]["pad_bottom"] else "4:3"


def prep(argv):
    for s in SHOTS:
        print(native(s), wide(s))


# ------------------------------------------------------------------------------------------------- gen (PY)
def _call(key, model, inp, tag, meta, dry):
    sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
    import cf
    try:
        est, why = cf.estimate(model, inp)
        paths = cf.generate(model, inp, os.path.join(OUT, key + ".png"), tag=tag, dry_run=dry)
    except BaseException as e:  # one call failing (or refused) must not lose the rest of the batch
        print(f"[fail] {key}: {str(e)[:400]}", file=sys.stderr)
        return key, None
    if dry:
        return key, est
    json.dump(dict(meta, key=key, model=model, tag=tag,
                   request={k: v for k, v in inp.items() if k not in ("prompt", "images", "image_input", "image")},
                   est_usd=est, est_basis=why, out=[os.path.relpath(x, ROOT) for x in paths]),
              open(os.path.join(OUT, key + ".json"), "w"), indent=1)
    return key, est


def next_key(stem):
    i = 1
    while os.path.exists(os.path.join(OUT, f"{stem}_{i}.json")):
        i += 1
    return f"{stem}_{i}"


def gen_one(style, shot, short, dry):
    model, asp, mk = MODELS[short]
    key = next_key(f"{style}_{shot}__{short}")
    src = wide(shot) if asp == "3:2" else native(shot)
    prompt = prompt_for(style, shot)
    inp = mk(prompt, ["file:" + os.path.relpath(src, ROOT)], aspect(shot))
    meta = dict(style=style, shot=shot, route="raw", prompt=prompt, input=os.path.relpath(src, ROOT),
                source=SHOTS[shot]["source"])
    return _call(key, model, inp, f"style8_{style}", meta, dry)


def run(jobs, fn):
    os.makedirs(OUT, exist_ok=True)
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(lambda j: fn(*j), jobs))
    print(json.dumps(res, indent=1))
    print(f"{len(res)} calls, {sum(1 for _, e in res if e is None)} failed, est ${sum(e for _, e in res if e):.2f}")


def gen(argv):
    dry = "--dry-run" in argv
    want = [a for a in argv if not a.startswith("--")]
    for s in SHOTS:
        native(s), wide(s)
    run([(st, sh, m, dry) for st, sh, m in JOBS if not want or any(w in f"{st}_{sh}__{m}" for w in want)], gen_one)


def meta_of(key):
    return json.load(open(os.path.join(OUT, key + ".json")))


def out_of(key):
    return os.path.join(ROOT, meta_of(key)["out"][0])


def fix_one(key, dry, keep_expr=False, hair=False):
    """gpt-image-2.5-flare: correct the painted face to the photo, keep the painting."""
    from PIL import Image
    d = meta_of(key)
    shot, style = d["shot"], d["style"]
    # the painting, padded to 3:2 the same way as the photo, so both images share a geometry
    im = Image.open(out_of(key)).convert("RGB")
    ref = Image.open(wide(shot)).convert("RGB")
    nat = Image.open(native(shot))
    s = ref.height / im.height
    im = im.resize((round(im.width * s), ref.height), Image.LANCZOS)
    canvas = Image.new("RGB", ref.size, (238, 230, 214))
    px = (ref.width - im.width) // 2
    canvas.paste(im, (px, 0))
    pin = os.path.join(OUT, "_in", f"{key}_3x2.png")
    canvas.save(pin)
    model, _, mk = MODELS["gpt"]
    prompt = FIX_PROMPT.format(style=STYLE_NAME[style])
    if keep_expr:
        prompt = prompt.replace(" and how far the lips are parted", "") + FIX_KEEP_EXPR
    if hair:
        prompt += FIX_HAIR
    inp = mk(prompt, ["file:" + os.path.relpath(pin, ROOT), "file:" + os.path.relpath(wide(shot), ROOT)], "3:2")
    meta = dict(style=style, shot=shot, route="fix", parent=key, prompt=prompt, input=os.path.relpath(pin, ROOT),
                source=d["source"], native_size=list(nat.size))
    stem = f"{key}__fix{'x' if keep_expr else ''}"
    k2, n = stem, 1
    while os.path.exists(os.path.join(OUT, k2 + ".json")):
        n += 1
        k2 = f"{stem}{n}"
    return _call(k2, model, inp, "style8_fix", dict(meta, keep_expr=keep_expr, hair=hair), dry)


def fix(argv):
    dry = "--dry-run" in argv
    run([(k, dry, "--keep-expr" in argv, "--black-hair" in argv) for k in argv if not k.startswith("--")], fix_one)


EXT_PROMPT = (
    "This is a hand-painted watercolour portrait whose bottom strip is blank paper. Continue the painting down into the "
    "blank strip so that her jacket, the black turtleneck, the orange bands and her long black hair carry on naturally "
    "to the bottom edge of the picture, in exactly the same style, brushwork, colours, warm side light and paper. Change "
    "nothing in the painted part above the strip: not her face, not her hair, not the glasses, not the patch. No text.")


def extend_one(key, dry):
    """nano-banana-pro paints the still on down to 5:4; the still's own pixels are pasted back above the seam."""
    from PIL import Image
    im = Image.open(out_of(key)).convert("RGB")
    w, h = im.size
    H = round(w * 4 / 5)
    canvas = Image.new("RGB", (w, H), (240, 233, 218))
    canvas.paste(im, (0, 0))
    pin = os.path.join(OUT, "_in", f"{key}_ext_in.png")
    canvas.save(pin)
    d = meta_of(key)
    model, _, mk = MODELS["nbp"]
    inp = mk(EXT_PROMPT, ["file:" + os.path.relpath(pin, ROOT)], "5:4")
    meta = dict(style=d["style"], shot=d["shot"], route="extend", parent=key, prompt=EXT_PROMPT, source=d["source"],
                input=os.path.relpath(pin, ROOT), seam_row=h, raw_size=[w, H])
    return _call(f"{key}__ext", model, inp, "style8_extend", meta, dry)


def extend_merge(key):
    """Paste the parent still back over the extended painting (feathered over 40 px above the seam)."""
    import numpy as np
    from PIL import Image
    d = meta_of(key + "__ext")
    E = Image.open(out_of(key + "__ext")).convert("RGB").resize(tuple(d["raw_size"]), Image.LANCZOS)
    E = np.asarray(E, np.float32)
    P = rd(out_of(key)).astype(np.float32)
    h = P.shape[0]
    a = np.ones((E.shape[0], 1, 1), np.float32) * 0
    a[:h, 0, 0] = np.clip((h - 8 - np.arange(h)) / 40, 0, 1)
    out = E.copy()
    out[:h] = P * a[:h] + E[:h] * (1 - a[:h])
    o = os.path.join(OUT, key + "__ext.png")
    raw = os.path.join(OUT, key + "__ext_raw.png")
    if not os.path.exists(raw):
        os.replace(out_of(key + "__ext"), raw)
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(o)
    d["out"] = [os.path.relpath(o, ROOT)]
    d["raw_out"] = os.path.relpath(raw, ROOT)
    json.dump(d, open(os.path.join(OUT, key + "__ext.json"), "w"), indent=1)
    print(o)


def extend(argv):
    dry = "--dry-run" in argv
    keys = [k for k in argv if not k.startswith("--")]
    run([(k, dry) for k in keys], extend_one)
    if not dry:
        for k in keys:
            extend_merge(k)


# ------------------------------------------------------------------------------------------------- landmarks (MPY)
def landmarks(rgb):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    os.environ.setdefault("FACE_LANDMARKER", os.path.expanduser(
        "~/Documents/1-music-shipped/moongazing/tools/sync/models/face_landmarker.task"))
    import numpy as np
    import mouth as MT
    H, W = rgb.shape[:2]
    r = MT.detect(rgb, (0, 0, W, H))
    if r is None:
        for b in MT.grid_boxes(W, H):
            r = MT.detect(rgb, b)
            if r is not None:
                break
    if r is None:
        return None
    L = r[0]
    # second pass on a box around the face, for precision
    x0, y0 = L.min(0)
    x1, y1 = L.max(0)
    m = 0.45 * max(x1 - x0, y1 - y0)
    r2 = MT.detect(rgb, (max(0, x0 - m), max(0, y0 - m), min(W, x1 + m), min(H, y1 + m)))
    return np.asarray((r2 or r)[0], np.float64)


_LMC = {}


def lm_of(path):
    if path not in _LMC:
        _LMC[path] = landmarks(rd(path))
    return _LMC[path]


def eye_c(L, side):
    import numpy as np
    idx = [33, 133, 159, 145, 160, 144, 158, 153] if side == "r" else [263, 362, 386, 374, 387, 373, 385, 380]
    return L[idx].mean(0)


def dist(a, b):
    import numpy as np
    return float(np.linalg.norm(np.asarray(a) - np.asarray(b)))


def measures(L):
    """Scale-free face measures (MediaPipe indices). io = eye-centre distance; fh = forehead 10 to chin 152."""
    io = dist(eye_c(L, "r"), eye_c(L, "l"))
    fh = dist(L[10], L[152])
    fw = dist(L[234], L[454])
    ew = (dist(L[33], L[133]) + dist(L[362], L[263])) / 2
    eh = (dist(L[159], L[145]) + dist(L[386], L[374])) / 2
    jaw = dist(L[172], L[397])          # lower jaw (gonial) width
    jaw2 = dist(L[136], L[365])         # jaw nearer the chin
    lower = dist(L[2], L[152])          # nose base to chin
    nose = dist(L[98], L[327])
    mouth = dist(L[61], L[291])
    return {"io/fh": io / fh, "io/fw": io / fw, "eye_w/io": ew / io, "eye_h/eye_w": eh / ew, "fw/fh": fw / fh,
            "jaw/fw": jaw / fw, "jaw2/fw": jaw2 / fw, "lower/fh": lower / fh, "nose/io": nose / io, "mouth/io": mouth / io}


CORE = list(range(0, 468))
INNER_MOUTH = {13, 14, 78, 308, 80, 81, 82, 87, 88, 95, 178, 191, 310, 311, 312, 317, 318, 324, 402, 415}
# every lip point but the corners: the lock must not stretch a closed painted mouth to the photo's parted lips
LIPS = {61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 185, 40, 39, 37, 0, 267, 269, 270, 409} | INNER_MOUTH
LOCK_SKIP = LIPS - {61, 291}


def similarity(A, B):
    """Least-squares similarity (scale, rotation, shift) mapping A onto B: returns 2x3."""
    import numpy as np
    ma, mb = A.mean(0), B.mean(0)
    a, b = A - ma, B - mb
    U, S, Vt = np.linalg.svd(a.T @ b)
    R = (U @ Vt).T
    if np.linalg.det(R) < 0:
        Vt[-1] *= -1
        R = (U @ Vt).T
    s = S.sum() / (a ** 2).sum()
    t = mb - s * R @ ma
    return np.hstack([s * R, t[:, None]])


def nme(Ls, Lp):
    """Mean landmark error of the still against the photo after similarity alignment, as % of the photo's io."""
    import numpy as np
    idx = [i for i in CORE if i not in INNER_MOUTH]
    M = similarity(Ls[idx], Lp[idx])
    A = Ls[idx] @ M[:, :2].T + M[:, 2]
    io = dist(eye_c(Lp, "r"), eye_c(Lp, "l"))
    return float(np.linalg.norm(A - Lp[idx], axis=1).mean() / io * 100)


# ------------------------------------------------------------------------------------------------- lock (MPY)
def lock_one(key):
    """Warp the painted face's geometry back to the photo's landmarks; everything else of the painting stays."""
    import cv2
    import numpy as np
    from PIL import Image
    from scipy.interpolate import RBFInterpolator
    d = meta_of(key)
    P = rd(out_of(key)).astype(np.float32)
    H, W = P.shape[:2]
    Ls = lm_of(out_of(key))
    Lp = lm_of(os.path.join(ROOT, SHOTS[d["shot"]]["canvas"]))
    idx = [i for i in CORE if i not in INNER_MOUTH]
    # the photo's face, similarity-placed onto the painting (keeps the painting's own position, size and roll)
    M = similarity(Lp[idx], Ls[idx])
    T = Lp @ M[:, :2].T + M[:, 2]
    io = dist(eye_c(Ls, "r"), eye_c(Ls, "l"))
    # control points: the face landmarks (target -> source displacement), plus a ring of fixed anchors well outside
    keep = idx[::2] + [10, 152, 234, 454, 172, 397, 136, 365, 33, 133, 263, 362, 159, 145, 386, 374, 61, 291]
    keep = sorted(set(keep) - LOCK_SKIP)
    c = Ls[[10, 152, 234, 454]].mean(0)
    rx, ry = dist(Ls[234], Ls[454]) * 0.95, dist(Ls[10], Ls[152]) * 0.85
    ang = np.linspace(0, 2 * np.pi, 48, endpoint=False)
    ring = np.stack([c[0] + rx * np.cos(ang), c[1] + ry * np.sin(ang)], 1)
    src = np.vstack([T[keep], ring])                      # where pixels go (output positions)
    dsp = np.vstack([Ls[keep] - T[keep], np.zeros_like(ring)])   # output -> painting offset
    rbf = RBFInterpolator(src, dsp, kernel="thin_plate_spline", smoothing=2.0)
    st = 4
    gy, gx = np.mgrid[0:H:st, 0:W:st].astype(np.float64)
    g = np.stack([gx.ravel(), gy.ravel()], 1)
    D = rbf(g).reshape(gy.shape + (2,)).astype(np.float32)
    D = cv2.resize(D, (W, H), interpolation=cv2.INTER_LINEAR)
    # feather: full inside the face ellipse, zero outside the anchor ring
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - c[0]) / rx) ** 2 + ((yy - c[1]) / ry) ** 2)
    f = np.clip((1.0 - r) / 0.25, 0, 1)[..., None]
    D *= f
    mx, my = xx + D[..., 0], yy + D[..., 1]
    Q = cv2.remap(P, mx, my, cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    key2 = f"{key}__lock"
    o = os.path.join(OUT, key2 + ".png")
    Image.fromarray(np.clip(Q, 0, 255).astype(np.uint8)).save(o)
    mxd = float(np.abs(D).max())
    json.dump(dict(d, key=key2, route="lock", parent=key, out=[os.path.relpath(o, ROOT)], est_usd=0,
                   lock=dict(max_shift_px=round(mxd, 1), max_shift_io=round(mxd / io, 3), n_ctrl=len(keep))),
              open(os.path.join(OUT, key2 + ".json"), "w"), indent=1)
    print(key2, "max shift", round(mxd, 1), "px")


def lock(argv):
    for k in argv:
        lock_one(k)


# ------------------------------------------------------------------------------------------------- metrics (MPY)
def all_keys():
    ks = []
    for f in sorted(os.listdir(OUT)):
        if f.endswith(".json") and "__" in f and not f.startswith("_"):
            d = json.load(open(os.path.join(OUT, f)))
            if d.get("out") and os.path.exists(os.path.join(ROOT, d["out"][0])):
                ks.append(d["key"])
    return ks


def metrics(argv):
    res = {}
    for shot, S in SHOTS.items():
        Lp = lm_of(os.path.join(ROOT, S["canvas"]))
        res[f"photo_{shot}"] = {k: round(v, 4) for k, v in measures(Lp).items()}
    for k in all_keys():
        d = meta_of(k)
        L = lm_of(out_of(k))
        if L is None:
            res[k] = {"error": "no face"}
            continue
        Lp = lm_of(os.path.join(ROOT, SHOTS[d["shot"]]["canvas"]))
        m, mp_ = measures(L), measures(Lp)
        row = {f"{n}%": round((m[n] / mp_[n] - 1) * 100, 1) for n in m}
        row["nme%io"] = round(nme(L, Lp), 2)
        row["route"] = d.get("route")
        res[k] = row
    json.dump(res, open(os.path.join(OUT, "likeness.json"), "w"), indent=1)
    cols = ["nme%io", "io/fh%", "io/fw%", "eye_w/io%", "eye_h/eye_w%", "fw/fh%", "jaw/fw%", "jaw2/fw%", "lower/fh%",
            "nose/io%", "mouth/io%"]
    lines = ["key\t" + "\t".join(cols)]
    for k, r in res.items():
        if k.startswith("photo_") or "error" in r:
            continue
        lines.append(k + "\t" + "\t".join(f"{r[c]:+.1f}" if c != "nme%io" else f"{r[c]:.2f}" for c in cols))
    open(os.path.join(OUT, "likeness.tsv"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


# ------------------------------------------------------------------------------------------------- matte (EPY)
def matte(argv):
    import numpy as np
    import torch
    from PIL import Image
    from scipy import ndimage as ndi
    sys.path.insert(0, os.path.join(ROOT, "tools/engrave"))
    from matte import get_birefnet
    from gpulock import GpuSlot
    slot = GpuSlot(label="style8")
    slot.acquire()
    try:
        net = get_birefnet("cuda")
        os.makedirs(os.path.join(OUT, "_matte"), exist_ok=True)
        want = [a for a in argv if not a.startswith("--")]
        for k in all_keys():
            if want and k not in want:
                continue
            p = os.path.join(OUT, "_matte", k + ".png")
            if os.path.exists(p) and "--force" not in argv:
                continue
            a = np.asarray(Image.open(out_of(k)).convert("RGB"), np.float32) / 255
            H, W = a.shape[:2]
            x = torch.from_numpy(a).permute(2, 0, 1)[None].cuda()
            with torch.no_grad():
                m = net(x)[0, 0].cpu().numpy()
                for x0, x1 in ((0, W * 5 // 8), (W * 3 // 8, W)):      # two overlapping halves for hair wisps
                    m[:, x0:x1] = np.maximum(m[:, x0:x1], net(x[..., x0:x1])[0, 0].cpu().numpy() * (m[:, x0:x1] > 0.02))
            lab, n = ndi.label(m > 0.5)
            if n > 1:                                                   # keep her: the largest component
                sizes = ndi.sum(np.ones_like(m), lab, range(1, n + 1))
                keep = 1 + int(np.argmax(sizes))
                m = m * ndi.binary_dilation(lab == keep, iterations=20)
            Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8)).save(p)
            print(k, "coverage", round(float((m > 0.5).mean()), 3))
    finally:
        slot.release() if hasattr(slot, "release") else None


# ------------------------------------------------------------------------------------------------- comp (MPY)
FIRST = os.path.join(ROOT, "media/sing/first")
CROP = json.load(open(os.path.join(FIRST, "crop.json")))["box"]        # [88, 43, 2664, 1492] of the 2752x1536 plate
FACE_H_V7, EYE_V7 = 504.6, (1262.1, 575.5)                             # v6/v7 geometry, crop px
WIDER = 0.88                                                           # "a little wider" than v7
EYE_Y = {"S1": 600.0, "V3S": 560.0}


def place(k):
    """Scale + shift of a still into the 2752x1536 plate: face height = 0.88 x v7's, eyes at v7's x."""
    import numpy as np
    d = meta_of(k)
    L = lm_of(out_of(k))
    fh = dist(L[10], L[152])
    s = FACE_H_V7 * WIDER / fh
    eye = (eye_c(L, "r") + eye_c(L, "l")) / 2
    ex, ey = EYE_V7[0] + CROP[0], EYE_Y[d["shot"]] + CROP[1]
    return np.float32([[s, 0, ex - s * eye[0]], [0, s, ey - s * eye[1]]]), s


def comp(argv):
    import cv2
    import numpy as np
    from PIL import Image
    want = [a for a in argv if not a.startswith("--")]
    x0, y0, x1, y1 = CROP
    info = {}
    for k in all_keys():
        if want and k not in want:
            continue
        mp_ = os.path.join(OUT, "_matte", k + ".png")
        if not os.path.exists(mp_):
            print("no matte:", k)
            continue
        d = meta_of(k)
        F = rd(out_of(k)).astype(np.float32)
        A = np.asarray(Image.open(mp_), np.float32) / 255
        h, w = A.shape
        M, s = place(k)
        Fw = cv2.warpAffine(F, M, (2752, 1536), flags=cv2.INTER_LANCZOS4 if s > 1 else cv2.INTER_AREA,
                            borderMode=cv2.BORDER_REPLICATE)
        Aw = cv2.warpAffine(A, M, (2752, 1536), flags=cv2.INTER_LINEAR, borderValue=0)
        Aw = np.clip((cv2.GaussianBlur(Aw, (0, 0), 1.0) - 0.08) / 0.84, 0, 1)
        # the still's own bottom edge, if it is inside the frame, would cut the figure: report it
        bottom = M[1, 1] * h + M[1, 2]
        P = rd(SHOTS[d["shot"]]["plate"]).astype(np.float32)
        C = (Fw * Aw[..., None] + P * (1 - Aw[..., None]))[y0:y1, x0:x1]
        o = os.path.join(OUT, k + "_comp.jpg")
        Image.fromarray(np.clip(C, 0, 255).astype(np.uint8)).save(o, quality=93)
        info[k] = dict(comp=os.path.relpath(o, ROOT), scale=round(float(s), 4),
                       still_bottom_in_crop=round(float(bottom - y0), 1), crop_h=y1 - y0)
        print(k, info[k])
    p = os.path.join(OUT, "_matte", "comp.json")
    old = json.load(open(p)) if os.path.exists(p) else {}
    old.update(info)
    json.dump(old, open(p, "w"), indent=1)


# ------------------------------------------------------------------------------------------------- sheet (MPY)
def font(sz, bold=True):
    from PIL import ImageFont
    p = f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf"
    return ImageFont.truetype(p, sz) if os.path.exists(p) else ImageFont.load_default()


def face_crop(path, L, size=520, span=1.9):
    """A square crop centred on the face, side = span x face height, resized to size."""
    import numpy as np
    from PIL import Image
    im = Image.open(path).convert("RGB")
    fh = dist(L[10], L[152])
    c = (L[10] + L[152]) / 2
    half = fh * span / 2
    return im.crop((int(c[0] - half), int(c[1] - half), int(c[0] + half), int(c[1] + half))).resize((size, size), Image.LANCZOS)


def wc_frame():
    p = os.path.join(OUT, "_in", "wc_v4_frame.jpg")
    if not os.path.exists(p):
        import subprocess
        ff = os.environ.get("FFMPEG", "ffmpeg")
        subprocess.run([ff, "-loglevel", "error", "-y", "-ss", "1.0", "-i", os.path.join(ROOT, WC_REF), "-frames:v", "1",
                        "-q:v", "2", p], check=True)
    return p


def faces(argv):
    from PIL import Image, ImageDraw
    import numpy as np
    keys = [a for a in argv if not a.startswith("--")] or all_keys()
    tiles = []
    for shot, S in SHOTS.items():
        p = os.path.join(ROOT, S["canvas"])
        tiles.append((f"photo {shot}", face_crop(p, lm_of(p))))
    for k in keys:
        L = lm_of(out_of(k))
        if L is not None:
            tiles.append((k, face_crop(out_of(k), L)))
    n = 6
    rows = (len(tiles) + n - 1) // n
    S_ = Image.new("RGB", (n * 530, rows * 560), (24, 24, 26))
    dr = ImageDraw.Draw(S_)
    for i, (t, im) in enumerate(tiles):
        x, y = (i % n) * 530, (i // n) * 560
        S_.paste(im, (x + 5, y + 35))
        dr.text((x + 8, y + 8), t, fill=(255, 230, 150), font=font(18, False))
    o = os.path.join(OUT, "_faces.jpg")
    S_.save(o, quality=90)
    print(o, S_.size)


def sheet(argv):
    """contact_sheet.jpg: one block per shot. Top row: source photo crop, v7 first frame, the original watercolour (v4)
    frame, then each chosen still on its plate. Bottom row, under each: the face at one scale (face height = 1/1.9 tile)."""
    from PIL import Image, ImageDraw
    import numpy as np
    rows_keys = [a.split(",") for a in argv if not a.startswith("--")]
    lik = json.load(open(os.path.join(OUT, "likeness.json")))
    TH, pad, lab = 360, 12, 54

    def fit(im, h):
        return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)

    def fc(path):
        L = lm_of(path)
        return face_crop(path, L, TH) if L is not None else None

    blocks = []
    for shot, keys in zip(SHOTS, rows_keys):
        S = SHOTS[shot]
        src, v7, wc = os.path.join(ROOT, S["source"]), os.path.join(ROOT, S["v7"]), wc_frame()
        cols = [("source photo", os.path.basename(S["source"]), face_crop(src, lm_of(src), TH, 2.6), fc(src)),
                ("v7 first frame (photo)", "first/" + os.path.basename(S["v7"]), fit(Image.open(v7).convert("RGB"), TH), fc(v7)),
                ("original watercolour", "S1/v4_sync_1080.mp4 @ 1.0 s", fit(Image.open(wc).convert("RGB"), TH), fc(wc))]
        for k in keys:
            r = lik.get(k, {})
            stat = (f"NME {r.get('nme%io', 0):.2f}%  fw/fh {r.get('fw/fh%', 0):+.1f}%  eye w {r.get('eye_w/io%', 0):+.1f}%"
                    f"  mouth {r.get('mouth/io%', 0):+.1f}%")
            cols.append((k, stat, fit(Image.open(os.path.join(OUT, k + "_comp.jpg")).convert("RGB"), TH), fc(out_of(k))))
        blocks.append((shot, cols))
    Wd = max(sum(c[2].width + pad for c in cols) + pad for _, cols in blocks)
    Hd = 74 + len(blocks) * (2 * TH + lab + 2 * pad + 30)
    C = Image.new("RGB", (Wd, Hd), (26, 26, 28))
    dr = ImageDraw.Draw(C)
    dr.text((pad, 14), "Rewind style stills v8: Chinese watercolour (look test, stills only).  Per shot: references, then each "
                       "style on its plate; below each, the face at one scale.", fill=(235, 235, 235), font=font(24))
    dr.text((pad, 44), "NME = mean landmark error vs her photo after similarity alignment, % of eye distance; the other numbers "
                       "are ratios vs the photo (fw/fh face width/height, eye w = eye width/eye distance, mouth = width/eye distance).",
            fill=(170, 170, 175), font=font(15, False))
    y = 74
    for shot, cols in blocks:
        x = pad
        for a, b, im, face in cols:
            C.paste(im, (x, y + lab))
            dr.text((x + 4, y + 2), a, fill=(255, 220, 140), font=font(18))
            dr.text((x + 4, y + 28), b, fill=(170, 170, 175), font=font(14, False))
            if face is not None:
                C.paste(face, (x + (im.width - face.width) // 2, y + lab + TH + pad))
            x += im.width + pad
        y += 2 * TH + lab + 2 * pad + 30
    o = os.path.join(OUT, "contact_sheet.jpg")
    C.save(o, quality=90)
    print(o, C.size)


if __name__ == "__main__":
    {"prep": prep, "gen": gen, "fix": fix, "extend": extend, "lock": lock, "metrics": metrics, "matte": matte, "comp": comp,
     "faces": faces, "sheet": sheet}[sys.argv[1]](sys.argv[2:])
