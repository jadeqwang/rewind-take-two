"""v5-coda2 (Jade's Round 3 notes on the Hilbert Hotel scene): new stills, nano-banana-pro 2K, tag v5_coda2_<name>.
Each output gets a .json beside it with model, prompt, refs (and seed: the API takes none, so null).
Plan/log: docs/revisions/v5/coda2.md.

    $PY tools/sectionF/coda/gen_coda2.py [name ...] [--dry-run] [--suffix=_b]
names: jade_v2, glasses_v2, door_plate, door_press (needs door_plate), glove_press (default: those not yet made)
"""
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from PIL import Image

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
import cf  # noqa: E402

OUT = "media/shots/PC/gen2"
GREY = (0xbd, 0xbd, 0xbd)
NOR = ("Absolutely no red anywhere (use orange, gold, magenta, violet, pale blue, teal and green instead). No text, no "
       "captions, no watermark.")
FIG = ("one single standing full-length figure, head to toe, facing the viewer, standing calmly and patiently as if "
       "waiting in a queue, arms relaxed at her sides, feet flat, centred, the figure filling about 86% of the image "
       "height with her feet about 5% above the bottom edge, on a perfectly flat plain light grey background (#bdbdbd): "
       "no floor, no shadow, no props, no other people.")


def on_grey(sprite, out, h_frac=0.86, foot=0.05, W=1536, H=2752):
    """a cut-out sprite composited back on the flat grey ground, 9:16, placed like FIG says (the i2v first frame)"""
    im = Image.open(os.path.join(ROOT, sprite)).convert("RGBA")
    h = round(H * h_frac)
    w = round(im.width * h / im.height)
    im = im.resize((w, h), Image.LANCZOS)
    cv = Image.new("RGBA", (W, H), GREY + (255,))
    cv.alpha_composite(im, ((W - w) // 2, round(H * (1 - foot)) - h))
    cv.convert("RGB").save(os.path.join(ROOT, out), quality=95)
    return out


JOBS = {
    # note 4: the protagonist as she looks at the film's end (O2: bun back up with both pencils), no glasses
    "jade_v2": dict(aspect="9:16", refs=["media/design/jade_canon_turnaround.png", "media/design/jade_bun_two_pencils.png",
                                          "media/shots/PC/gen/committee_a.jpg"], prompt=(
        "Draw the young woman of the first two reference images (her character sheets: match her face, hair and outfit "
        "exactly) as " + FIG + " Same clean anime illustration style, line weight and cel colouring as the figures in "
        "the third reference, and the same standing pose and proportions as they have. Exactly her canon design: black "
        "hair pinned up in a loose messy bun at the back of her head with exactly two yellow hexagonal pencils crossed "
        "in an X through the bun, erasers up (one pencil with a pink eraser, the other with a pale-blue eraser), centre "
        "part with long curtain bangs framing her face, a few loose strands; dark brown eyes, calm small smile; NO "
        "glasses. An open white cropped bomber jacket with one orange band across the chest and both sleeves, a small "
        "pale-blue dot patch on her left chest, a round black-and-white patch on her left upper sleeve; a black mock-neck "
        "crop top; orange-and-black headphones resting around her neck; wide navy-blue cargo trousers with hanging orange "
        "straps and cargo pockets; chunky white sneakers. Her hands are empty (no pencil in her hands; the only two "
        "pencils are in her bun). " + NOR)),
    # note 4: Jade #2: rectangular-ish glasses, fuller hair, half-up ponytails ~40% less volume
    "glasses_v2": dict(aspect="9:16", refs=["@grey:media/shots/PC/sprites/glasses.png", "inputs/committee_v3_long_ponytails_ff.png"],
                       prompt=(
        "Edit the first image, keeping the same girl, the same pose, size and position, the same outfit, the same face "
        "and expression and the same clean anime style and flat grey background. Change only her hair and glasses: "
        "(1) replace her round glasses with slightly rectangular glasses: thin dark frames with softly rounded corners, "
        "a little wider than tall. (2) Her long loose black hair below the two half-up pigtails becomes fuller and "
        "denser: it falls as one solid, thick curtain of hair down her back and past her shoulders, with no gaps "
        "between the strands where the grey background shows through. (3) The two small half-up pigtails at the top of "
        "her head are about 40% smaller in volume than now: slimmer, shorter, neater bunches, so the overall silhouette "
        "of her head is narrower. The second image is only the reference for who she is (the girl with glasses who "
        "reads the notebook). " + NOR)),
    # jade_v2 came out on model but without the chest dot / sleeve roundel, and the pencils were faint: an edit of it
    "jade_v3": dict(aspect="9:16", refs=[f"{OUT}/jade_v2.jpg", "media/design/jade_canon_turnaround.png",
                                          "media/design/jade_bun_two_pencils.png"], prompt=(
        "Edit the first image, keeping the same girl, pose, size, position, face, expression, outfit, style and flat "
        "grey background exactly. Add only these details from her character sheets (second and third images): (1) a "
        "solid pale-blue (#8DB8E8) round dot patch on the white jacket on HER left chest (the right side of the image), "
        "above the orange band; (2) a small round white patch with a black ring on HER left upper sleeve (right side of "
        "the image), above the orange band; (3) make the two yellow hexagonal pencils crossed in an X through her bun "
        "clearly visible above her head, erasers up: one with a pink eraser and a silver ferrule, one with a pale-blue "
        "eraser and a silver ferrule, each pencil one straight line. No glasses. " + NOR)),
    # note 1: a brass push-plate with an engraved infinity-key on the stone pier right of the door
    "door_plate": dict(aspect="16:9", refs=["media/shots/PC/door.jpg"], prompt=(
        "Edit this image: add one small rectangular polished brass push-button plate mounted on the pale stone pier at "
        "the far right of the image, at about the height of the door handle (its centre about 11% in from the right "
        "edge and 57% down from the top), upright, about 4% of the image wide and 9% tall, with a round brass push "
        "button in its middle and a tiny engraved infinity sign shaped like the looped bow of a key above the button, "
        "four little screws in its corners. Drawn in exactly the same style as the rest of the image (fine engraved "
        "hatching with coloured pencil on warm paper). Change nothing else at all: the door, its glass, the gold HILBERT "
        "HOTEL emblem, the handle, the bell, the arch and the stained glass stay exactly as they are. " + NOR)),
    # note 1: the doorman's white-gloved hand pressing that plate (cut out by differencing against door_plate)
    "door_press": dict(aspect="16:9", refs=[f"{OUT}/door_plate.jpg"], prompt=(
        "Edit this image: add a hotel doorman's hand reaching in from the right edge of the image to press the round "
        "brass button on the small brass plate on the stone pier at the right. Only his right hand and forearm are seen: "
        "a crisp white cotton glove, the index finger extended and its tip pressing the button, the other fingers "
        "loosely curled; the wrist in a dark green livery sleeve with a thin gold braid at the cuff, the sleeve leaving "
        "the image at the right edge. A short, natural reach: the hand stays in the right-hand fifth of the image, close "
        "to the plate. Same drawing style as the image (fine engraved hatching with coloured pencil). Change nothing "
        "else at all. " + NOR)),
}


def run(name, dry, suffix=""):
    j = JOBS[name]
    out = f"{OUT}/{name}{suffix}.jpg"
    refs = []
    for r in j["refs"]:
        if r.startswith("@grey:"):
            r = on_grey(r[6:], f"{OUT}/_in_{name}.jpg")
        refs.append(r)
    inp = {"prompt": j["prompt"], "aspect_ratio": j["aspect"], "image_size": "2K", "image_input": [f"file:{r}" for r in refs]}
    paths = cf.generate("google/nano-banana-pro", inp, os.path.join(ROOT, out), tag=f"v5_coda2_{name}", dry_run=dry)
    if not dry:
        json.dump({"model": "google/nano-banana-pro", "prompt": j["prompt"], "refs": refs, "aspect_ratio": j["aspect"],
                   "image_size": "2K", "seed": None, "out": paths}, open(os.path.join(ROOT, f"{OUT}/{name}{suffix}.json"), "w"), indent=1)
    return name, paths


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    suffix = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--suffix=")), "")
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or [n for n in JOBS if not os.path.exists(os.path.join(ROOT, OUT, n + ".jpg"))]
    os.makedirs(os.path.join(ROOT, OUT), exist_ok=True)
    with ThreadPoolExecutor(5) as ex:
        for name, p in ex.map(lambda n: run(n, dry, suffix), names):
            print(name, p)
