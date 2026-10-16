#!/usr/bin/env python3
"""Selfie round 3 (Jade, 2026-10-16): she put on light makeup in real life (inputs/light_makeup_irl.png, 512x683,
never overwritten). Jacket only: replace the black/floral velvet top with the film's jacket fitted to her own build
(both shoulders and epaulets, the '1420 MHz' patch on her left sleeve). Face, her own makeup, skin, brows, eyes,
glasses, hair, pose stay exactly as photographed; no retouch, smoothing or glow. Candidates only; nothing is wired in.

    PY=~/Documents/1-music-shipped/moongazing/.venv/bin/python
    MPY=~/Documents/1-music-shipped/orbital-sunrise-video/video/out/.venv/bin/python
    $PY  tools/sing/selfie_r3.py gen KEY [KEY ...] [--prompt=j1|...] [--dry-run]     KEY = <model>_<n> (tags selfie_r3_<model>)
    $MPY tools/sing/selfie_r3.py hybrid KEY [KEY ...]     -> r3/hyb_<KEY>.png: her exact face, NO makeup pass
    $MPY tools/sing/selfie_r3.py check                    -> media/sing/selfie/contact_sheet_r3.jpg, r3/metrics_r3.json

`check` = round-1/2 likeness + brow metrics against light_makeup_irl.png, plus a skin/makeup check: mean L*a*b* and
texture energy (|L - blur|) in the cheeks, lips and skin, candidate mapped to the source's 1x frame, vs the source;
flags smoothing (texture < 0.8x) or recolouring (a*b* shift > 3, L shift > 4, beyond the floor).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selfie_dress as SD  # noqa: E402

ROOT = SD.ROOT
SRC = os.path.join(ROOT, "inputs/light_makeup_irl.png")
OUT = os.path.join(SD.OUT, "r3")
PICK2 = os.path.join(SD.OUT, "selfie_r2_pick_model.png")

PROMPT = (
    "IMAGE 1 is a real, unretouched phone photo of a woman. IMAGE 2 is only a clothing reference: a white jacket over a "
    "black turtleneck (the black area at its neck is not a person). Make exactly one change to IMAGE 1: replace her black "
    "top with the floral velvet panel by the jacket in IMAGE 2: " + SD.JACKET_WORDS + ".\n\n"
    "Fit the jacket to her own body exactly as she is: the same shoulders, shoulder width and build, the same pose, with "
    "both shoulders and both epaulets visible, the round '1420 MHz' patch fully visible on her left upper sleeve (on the "
    "viewer's right) and the pale-blue disc on her chest. Her long hair falls over the jacket's shoulders and front exactly "
    "as it falls over her top now, every strand in the same place. Take only the jacket and turtleneck from IMAGE 2: no "
    "face, no hair, no skin, no background.\n\n"
    "Everything else in IMAGE 1 stays exactly as photographed, pixel for pixel: her face, her own light makeup, her skin "
    "and its texture, her lip colour, her eyebrows, her eyes, her expression and head pose, her glasses (thin dark "
    "gunmetal-green rectangular frames with teal on the temples and nose pads), her hair, the room and the light, the "
    "framing and crop. This is a clothing swap only: do not retouch, smooth, brighten, sharpen or recolour her face, do "
    "not add makeup or glow, and do not change her face shape, eyes, nose, mouth, jaw or proportions in any way. At most, "
    "tidy two or three stray flyaway hairs. It stays the same real phone photo, just at a higher resolution.")
PROMPTS = {"j1": PROMPT}

SEL = "file:media/sing/selfie/r3/_in/src.jpg"
SEL_C = "file:media/sing/selfie/r3/_in/src_crop2x3.jpg"
JKT = "file:media/sing/selfie/_in/jacket_ref.png"


def build(short, p):
    return {
        "nbp": {"prompt": p, "aspect_ratio": "3:4", "image_size": "2K", "output_format": "png", "image_input": [SEL, JKT]},
        "nb2": {"prompt": p, "aspect_ratio": "3:4", "resolution": "2K", "output_format": "png", "image_input": [SEL, JKT]},
        "gpt": {"prompt": p, "size": "1024x1536", "quality": "high", "output_format": "png", "images": [SEL_C, JKT]},
        "sdr": {"prompt": p, "size": "1536x2048", "watermark": False, "image": [SEL, JKT]},
        "flux2": {"prompt": p, "input_images": [SEL, JKT], "width": 1536, "height": 2048, "output_format": "png"},
    }[short]


def prep():
    from PIL import Image
    os.makedirs(os.path.join(OUT, "_in"), exist_ok=True)
    a = Image.open(SRC).convert("RGB")
    a.save(os.path.join(OUT, "_in", "src.jpg"), quality=95)
    x0, x1, y0, y1 = SD.CROP2x3
    a.crop((x0, y0, x1, y1)).save(os.path.join(OUT, "_in", "src_crop2x3.jpg"), quality=95)


def gen(argv):
    sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
    import cf
    from concurrent.futures import ThreadPoolExecutor
    o = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    dry = "--dry-run" in argv
    keys = [a for a in argv if not a.startswith("--")]
    prep()

    def one(key):
        short = key.split("_")[0]
        pk = o.get("prompt", "j1")
        model = SD.MODELS[short][0]
        if os.path.exists(os.path.join(OUT, f"{key}.json")) and not dry:
            print("exists, skipped:", key); return key, None
        inp = build(short, PROMPTS[pk])
        tag = f"selfie_r3_{short}"
        try:
            est, why = cf.estimate(model, inp)
            paths = cf.generate(model, inp, os.path.join(OUT, key + ".png"), tag=tag, dry_run=dry)
        except Exception as e:  # noqa: BLE001
            print(f"[fail] {key}: {str(e)[:400]}", file=sys.stderr); return key, None
        if not dry:
            from PIL import Image
            json.dump({"key": key, "model": model, "prompt_key": pk, "prompt": PROMPTS[pk], "tag": tag,
                       "inputs": [x for x in (inp.get("image_input") or inp.get("images") or inp.get("image") or inp.get("input_images"))],
                       "request": {k: v for k, v in inp.items() if k not in ("prompt", "images", "image_input", "image", "input_images")},
                       "est_usd": est, "est_basis": why, "out": [os.path.relpath(x, ROOT) for x in paths],
                       "out_size": list(Image.open(paths[0]).size)},
                      open(os.path.join(OUT, key + ".json"), "w"), indent=1)
        return key, est

    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(one, keys))
    print(json.dumps(res), f"est ${sum(e for _, e in res if e):.3f}{' (dry run)' if dry else ''}")


def conceal_only(rgb, L, ref=None):
    """Jade (round 3): light smoothing / freckle concealing is fine on the hybrids, her makeup colours stay. So only the
    dark-spot lift of round 1's pass (part way), no flush evening, no lip or lash change."""
    return SD.makeup(rgb, L, ref=None, conceal=0.35, even=0.0, lips=0.0, lash=0.0)


def hybrid(argv):
    """Her exact face (no makeup pass, no sharpening, light freckle concealing only); toned toward the take's skin only
    inside the feather ring so the jaw/hairline seam disappears."""
    SD.hybrid(argv, cand_dir=OUT, look=conceal_only, src_path=SRC, sharpen=0, edge_tone_only=True,
              label="hybrid (no paid call): her exact face (light_makeup_irl), light conceal only")


VERDICT = {}     # filled in after looking (see media/sing/selfie/README.md, round 3)


def check(argv):
    SD.check(argv, cand_dir=OUT, sheet="contact_sheet_r3.jpg", metrics_name="metrics_r3.json",
             head=[("r2_pick", PICK2)], verdict={**VERDICT, "r2_pick": ("REF", "round-2 model pick (other photo)")},
             src_path=SRC, skin=True, src_label="ORIGINAL light makeup")


if __name__ == "__main__":
    {"gen": gen, "hybrid": hybrid, "check": check}[sys.argv[1]](sys.argv[2:])
