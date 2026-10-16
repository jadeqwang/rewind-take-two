#!/usr/bin/env python3
"""Selfie round 2 (Jade, 2026-10-16): "a subtle no make-up make up glow-up". Healthy, rested, lightly dewy skin, even
tone, softened under-eye shadows, a hint of natural flush, tinted-balm lips near her own colour, fine lash definition;
light hair tidying. Geometry, brows, glasses and the film's jacket stay. Candidates only; nothing is wired in.

Two routes per model:
    A  from the original selfie + the jacket reference (makeup and jacket in one edit)      keys a_<model>_<n>
    B  from the round-1 model pick (media/sing/selfie/selfie_pick_model.png, jacket done): glow only   keys b_<model>_<n>
Both are measured against the ORIGINAL selfie (tools/sing/selfie_dress.py check), so B's two edits add up honestly.

    PY=~/Documents/1-music-shipped/moongazing/.venv/bin/python
    MPY=~/Documents/1-music-shipped/orbital-sunrise-video/video/out/.venv/bin/python
    $PY  tools/sing/selfie_glow.py gen KEY [KEY ...] [--prompt=a1|b1|...] [--dry-run]     (tags selfie_r2_<route>_<model>)
    $MPY tools/sing/selfie_glow.py hybrid KEY [KEY ...]     -> r2/hyb_<KEY>.png: her exact face + the local glow pass
    $MPY tools/sing/selfie_glow.py check                    -> media/sing/selfie/contact_sheet_r2.jpg, r2/metrics_r2.json
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selfie_dress as SD  # noqa: E402

ROOT = SD.ROOT
OUT = os.path.join(SD.OUT, "r2")
PICK1 = os.path.join(SD.OUT, "selfie_pick_model.png")      # round-1 model pick (nano-banana-2 nb2_1, 1792x2400)

GLOW = (
    "THE LOOK: a subtle 'no-makeup makeup' look, as if she simply had a great-skin day. Healthy, rested skin with a light, "
    "natural, dewy glow (fresh, not shiny or greasy), an even skin tone, the shadows under her eyes softened a little, a "
    "hint of natural flush on her cheeks, lips with a tinted lip balm close to her own lip colour, and her lashes finely "
    "defined. It must not look like makeup or a beauty filter: real skin texture and pores stay visible (freckles and "
    "small moles may be evened out). Light hair tidying is fine: smooth the flyaways and add a little shine; same length, "
    "colour, centre part and loose down style.\n\n")
GEOMETRY = (
    "This is a skin and colour retouch only, never a reshaping. Her face keeps exactly its geometry: the same face width "
    "and roundness, the same full cheeks and jawline, the same chin, the same nose width and shape, the same mouth width "
    "and lip shape, the same neutral expression and head tilt. Her eyes stay exactly the same size and shape, with the same "
    "relaxed, slightly hooded upper lids, the same eye opening and the same amount of iris showing; do not open her eyes "
    "wider or make them rounder or bigger. Her eyebrows keep exactly their shape, thickness, arch, length and colour: do "
    "not groom, fill, lift or reshape them. Do not slim her face, lift her cheeks, narrow her nose or jaw, shorten her "
    "chin, or make her look younger or like a model; a 'glow-up' here means skin and colour only.\n\n")
KEEP = (
    "Her glasses stay exactly as they are: thin dark gunmetal-green rectangular metal frames with teal on the temples and "
    "nose pads. Keep the soft window light from the left, the room behind her, and the framing and crop. It stays a real, "
    "natural phone photo of the same person.")
PROMPT_A = (
    "IMAGE 1 is a real, unretouched phone selfie of a woman. IMAGE 2 is only a clothing reference: a white jacket over a "
    "black turtleneck (the black area at its neck is not a person). Make exactly these changes to IMAGE 1:\n\n"
    "1. CLOTHES. Replace her black top with the floral velvet panel by the jacket in IMAGE 2: " + SD.JACKET_WORDS + ". It "
    "sits on her shoulders at the same pose, size and position as her current top, and her long hair falls over the "
    "jacket's shoulders and front exactly as it falls over her top now. Take only the jacket and turtleneck from IMAGE 2: "
    "no face, no hair, no skin, no background.\n\n2. " + GLOW + GEOMETRY + KEEP)
PROMPT_B = (
    "This is a real phone photo of a woman in a white jacket with orange bands over a black turtleneck. Change only her "
    "skin and makeup, nothing else.\n\n" + GLOW + GEOMETRY +
    "Her jacket with its orange bands, snaps, pale-blue disc and round '1420 MHz' patch, the black turtleneck, her hair "
    "and everything else stay exactly as they are. " + KEEP)
PROMPTS = {"a1": PROMPT_A, "b1": PROMPT_B}
DEFAULT = {"a": "a1", "b": "b1"}

SEL = "file:media/sing/selfie/_in/selfie.jpg"                # selfie as JPEG (same pixels as the PNG, q95)
JKT = "file:media/sing/selfie/_in/jacket_ref.png"
P1J = "file:media/sing/selfie/r2/_in/pick1.jpg"              # round-1 pick as JPEG q95 (keeps the data URI small)
P1C = "file:media/sing/selfie/r2/_in/pick1_crop2x3.jpg"      # ... cropped to 2:3 for gpt
S2C = "file:media/sing/selfie/_in/selfie_crop2x3.png"


def build(route, short, p):
    imgs = {"a": {"gpt": [S2C, JKT]}, "b": {"gpt": [P1C]}}[route].get(short) or ([SEL, JKT] if route == "a" else [P1J])
    return {
        "nbp": {"prompt": p, "aspect_ratio": "3:4", "image_size": "2K", "output_format": "png", "image_input": imgs},
        "nb2": {"prompt": p, "aspect_ratio": "3:4", "resolution": "2K", "output_format": "png", "image_input": imgs},
        "gpt": {"prompt": p, "size": "1024x1536", "quality": "high", "output_format": "png", "images": imgs},
        "sdr": {"prompt": p, "size": "1536x2048", "watermark": False, "image": imgs},
        "flux2": {"prompt": p, "input_images": imgs, "width": 1536, "height": 2048, "output_format": "png"},
    }[short]


def prep():
    from PIL import Image
    os.makedirs(os.path.join(OUT, "_in"), exist_ok=True)
    a = Image.open(PICK1).convert("RGB")
    a.save(os.path.join(OUT, "_in", "pick1.jpg"), quality=95)
    w, h = a.size                                          # 1792x2400 -> 2:3 = 1600x2400
    x0 = (w - h * 2 // 3) // 2
    a.crop((x0, 0, x0 + h * 2 // 3, h)).save(os.path.join(OUT, "_in", "pick1_crop2x3.jpg"), quality=95)
    SD.src_for("gpt")


def gen(argv):
    sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
    import cf
    from concurrent.futures import ThreadPoolExecutor
    o = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    dry = "--dry-run" in argv
    keys = [a for a in argv if not a.startswith("--")]
    prep()

    def one(key):
        route, short, _ = key.split("_")
        pk = o.get("prompt", DEFAULT[route])
        model = SD.MODELS[short][0]
        if os.path.exists(os.path.join(OUT, f"{key}.json")) and not dry:
            print("exists, skipped:", key); return key, None
        inp = build(route, short, PROMPTS[pk])
        tag = f"selfie_r2_{route}_{short}"
        try:
            est, why = cf.estimate(model, inp)
            paths = cf.generate(model, inp, os.path.join(OUT, key + ".png"), tag=tag, dry_run=dry)
        except Exception as e:  # noqa: BLE001
            print(f"[fail] {key}: {str(e)[:400]}", file=sys.stderr); return key, None
        if not dry:
            from PIL import Image
            json.dump({"key": key, "route": route, "model": model, "prompt_key": pk, "prompt": PROMPTS[pk], "tag": tag,
                       "inputs": [x for x in (inp.get("image_input") or inp.get("images") or inp.get("image") or inp.get("input_images"))],
                       "request": {k: v for k, v in inp.items() if k not in ("prompt", "images", "image_input", "image", "input_images")},
                       "est_usd": est, "est_basis": why, "out": [os.path.relpath(x, ROOT) for x in paths],
                       "out_size": list(Image.open(paths[0]).size)},
                      open(os.path.join(OUT, key + ".json"), "w"), indent=1)
        return key, est

    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(one, keys))
    print(json.dumps(res), f"est ${sum(e for _, e in res if e):.3f}{' (dry run)' if dry else ''}")


# ---------------------------------------------------------------------------------------------- local glow pass
def glow(rgb, L, ref=None, even=0.45, conceal=0.5, under=0.55, flush=2.0, dew=0.35, lips=0.5, lash=0.15):
    """No-makeup-makeup look, no geometry: even the blotchy flush, conceal dark spots part way, lift the under-eye
    shadows toward the cheek, a faint even flush on the cheek apples, a soft broad glow on the high planes (forehead,
    cheekbones, nose bridge), balm lips half way to ref's lip colour (or her own, slightly fresher), a touch of lash.
    Brows are never touched (they are holes in the skin mask)."""
    import cv2
    import numpy as np
    import tint_match as T
    ms = T.masks(rgb, L)
    io, lab, w = ms["io"], ms["lab"].copy(), ms["skin"]
    out = lab.copy()

    def wblur(x, wt, sg):
        return cv2.GaussianBlur(x * wt, (0, 0), sg) / (cv2.GaussianBlur(wt, (0, 0), sg) + 1e-4)
    # even tone + conceal (as round 1)
    exc = np.maximum(0, wblur(lab[..., 1], w, 0.08 * io) - wblur(lab[..., 1], w, 0.40 * io))
    out[..., 1] -= even * w * exc
    out[..., 2] -= 0.3 * even * w * exc
    base = wblur(lab[..., 0], w, 0.035 * io)
    dark = np.maximum(0, base - lab[..., 0] - 1.0)
    out[..., 0] += conceal * w * dark
    for ch in (1, 2):
        out[..., ch] += conceal * w * SD._ss01(dark / 6) * (wblur(lab[..., ch], w, 0.035 * io) - lab[..., ch])
    # under-eye: band under each lower lid, lifted toward the broad skin level below it
    ue = np.zeros(rgb.shape[:2], np.float32)
    down = (L[152] - L[168]) / np.linalg.norm(L[152] - L[168])
    for lid in ([33, 7, 163, 144, 145, 153, 154, 155, 133], [362, 382, 381, 380, 374, 373, 390, 249, 263]):
        P = L[lid]
        poly = np.vstack([P + down * 0.03 * io, (P + down * 0.30 * io)[::-1]])
        ue = np.maximum(ue, T._poly(rgb.shape, poly))
    ue = cv2.GaussianBlur(ue, (0, 0), 0.06 * io) * w
    broad = wblur(out[..., 0], w, 0.25 * io)
    out[..., 0] += under * ue * np.maximum(0, broad - out[..., 0])
    out[..., 2] -= 0.3 * under * ue * np.maximum(0, broad - lab[..., 0]) * 0.3     # shadows read violet-brown: neutralise a little
    # faint even flush on the cheek apples
    out[..., 1] += flush * ms["cheeks"]
    # dewy glow: broad highlight structure (medium-scale lightness above the face-scale level) gently accentuated
    med, big = wblur(out[..., 0], w, 0.08 * io), wblur(out[..., 0], w, 0.40 * io)
    out[..., 0] += dew * w * np.maximum(0, med - big)
    # balm lips
    wl = ms["lips"]
    cur = T.stats(lab, wl, 0.6)["mean"]
    tgt = T.stats(T.to_lab(ref), wl, 0.6)["mean"] if ref is not None else [cur[0], cur[1] + 4, cur[2]]
    for ch in range(3):
        out[..., ch] += lips * wl * (tgt[ch] - cur[ch]) * (0.5 if ch == 0 else 1.0)
    lbase = wblur(lab[..., 0], wl, 0.05 * io)
    out[..., 0] += 0.25 * lips * wl * np.maximum(0, lab[..., 0] - lbase)            # a little balm sheen on the lip highlight
    # lashes
    lm = np.zeros(rgb.shape[:2], np.float32)
    for ix in (SD.EYE_UP_R, SD.EYE_UP_L):
        cv2.polylines(lm, [np.round(L[ix]).astype(np.int32)], False, 1.0, max(1, int(0.03 * io)))
    out[..., 0] *= 1 - lash * cv2.GaussianBlur(lm, (0, 0), 0.012 * io)
    return T.from_lab(out)


def hybrid(argv):
    SD.hybrid(argv, cand_dir=OUT, look=glow)


VERDICT = {      # written after looking at every image at 2x face crops (see media/sing/selfie/README.md, round 2)
    "a_nbp_1": ("OK", "glow, faithful; skin a little smooth"),
    "a_nbp_2": ("OK", "faithful; glow very subtle"),
    "a_nb2_1": ("REJECT", "greasy shine on nose/forehead; eyes +6.7%"),
    "a_nb2_2": ("PICK", "within floor; real texture, soft glow"),
    "a_nb2_3": ("OK", "stronger flush, cheeks a bit red"),
    "a_nb2_4": ("REJECT", "shiny nose, reads greasy"),
    "a_gpt_1": ("OK", "faithful; airbrushed-smooth skin"),
    "a_gpt_2": ("OK", "faithful; airbrushed-smooth skin"),
    "a_sdr_1": ("OK", "natural, faithful; light flush"),
    "a_sdr_2": ("REJECT", "brow arch flattened -4.4%"),
    "b_nbp_1": ("OK", "soft-focus smooth; pink lips"),
    "b_nbp_2": ("OK", "smooth; brows within floor"),
    "b_nb2_1": ("OK", "r1 pick with a bit more glow"),
    "b_nb2_2": ("OK", "runner-up: even, rested, a bit smooth"),
    "b_nb2_3": ("OK", "eyes +5.3% (at floor edge)"),
    "b_gpt_1": ("REJECT", "eyes enlarged +7.3/+7.6%, smoothed"),
    "b_sdr_1": ("OK", "runner-up: most visible glow + flush"),
    "b_sdr_2": ("OK", "even, flushed; a bit smooth"),
    "b_sdr_3": ("OK", "smooth; mouth -4.5% (within floor)"),
    "hyb_a_nb2_2": ("PICK", "her face exactly + glow pass"),
    "hyb_a_nbp_1": ("OK", "her face exactly + glow pass"),
    "hyb_b_sdr_1": ("OK", "her face exactly + glow pass"),
}


def check(argv):
    SD.check(argv, cand_dir=OUT, sheet="contact_sheet_r2.jpg", metrics_name="metrics_r2.json",
             head=[("r1_pick", PICK1)], verdict={**VERDICT, "r1_pick": ("REF", "round-1 model pick (nb2_1)")})


if __name__ == "__main__":
    {"gen": gen, "hybrid": hybrid, "check": check}[sys.argv[1]](sys.argv[2:])
