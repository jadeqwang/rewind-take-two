#!/usr/bin/env python3
"""v5 note 0:13 & 2:35: candidate drawings of the impossible staircase on the rooftop (PAID, nano-banana-pro 2K).

    PY=~/Documents/moongazing/.venv/bin/python
    $PY tools/v5/stairs/gen.py crop                      # free: the rooftop context crop of plate_close_1 -> stairs_v5/roof_in.png
    $PY tools/v5/stairs/gen.py gen KEY [--dry-run]       # PAID: stairs_v5/cand_<KEY><i>.png + .json (prompt, model, refs, tag)

The crop is plate_close_1.jpg px CROP (4:3); candidates come back at 2K and are scaled back onto it by comp.py.
"""
import json
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
OUT = "media/sing/plates/stairs_v5"
CLOSE = "media/sing/plates/plate_close_1.jpg"
CROP = (0, 768, 1024, 1536)                              # plate px, 4:3
MODEL = "google/nano-banana-pro"

STYLE = ("Same wood-engraving technique as the rest of the picture: crisp black ink lines and parallel hatching on cream "
         "paper, strong black and white, no grey wash, no colour. Keep everything else in the picture exactly as it is: the "
         "other rooftops, the roof edges and parapets, the building facade with windows, the trees, the lamp post, the "
         "plaza, the framing and the paper border. Same size, same crop.")
PROMPTS = {
    # A: text only, the plate crop as the image
    "A": ("Edit this black-and-white wood engraving (a fish-eye reflection of Chicago rooftops seen from above). On the "
          "near flat rooftop at the left there is a small square stairwell: a square ring of steps round a dark pit. "
          "Replace ONLY that stairwell with a Penrose impossible staircase, like M. C. Escher's 'Ascending and "
          "Descending': a raised square loop of four flights of stairs standing on the roof, every flight climbing into "
          "the next, so the loop climbs forever and still meets its own start. Make it a little larger than the old "
          "stairwell, solid like masonry, with an open square courtyard in the middle, walls dropping to the roof, and "
          "about 30 bold, clearly readable steps round the loop (white treads, dark hatched risers), seen in the same "
          "steep downward view as the roof it stands on. " + STYLE),
    # B: as A, with the drawn z-buffer guide (penrose.py) pasted on the roof as the shape to follow
    "B": ("Edit this black-and-white wood engraving (a fish-eye reflection of Chicago rooftops seen from above). On the "
          "near flat rooftop at the left stands a rough, flat-shaded block model of a Penrose impossible staircase "
          "(Escher's 'Ascending and Descending'): a square loop of four flights of steps that climbs forever and meets its "
          "own start. Redraw that model as finished wood engraving: masonry steps with white treads and dark hatched "
          "risers, hatched walls, the courtyard in shadow, keeping its outline, its position, its size and every step "
          "where it is, so the loop still reads as impossible. " + STYLE),
}


def crop():
    os.makedirs(OUT, exist_ok=True)
    Image.open(CLOSE).convert("RGB").crop(CROP).save(f"{OUT}/roof_in.png"); print("wrote", f"{OUT}/roof_in.png")


def gen(key, dry=False, src=None):
    import cf
    src = src or f"{OUT}/roof_in.png"
    i = 1
    while any(os.path.exists(f"{OUT}/cand_{key}{i}{e}") for e in (".png", ".jpg", ".json")): i += 1
    p = f"{OUT}/cand_{key}{i}.png"
    inp = {"prompt": PROMPTS[key], "aspect_ratio": "4:3", "image_size": "2K", "output_format": "png", "image_input": [f"file:{src}"]}
    got = cf.generate(MODEL, inp, p, tag=f"v5_stairs_{key}{i}", dry_run=dry)
    if not dry:
        json.dump({"model": MODEL, "prompt": PROMPTS[key], "refs": [src], "crop_plate_px": CROP, "seed": None,
                   "tag": f"v5_stairs_{key}{i}", "out": got}, open(os.path.splitext(p)[0] + ".json", "w"), indent=1)
    print(got)


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    o = dict((x[2:].split("=", 1) + ["1"])[:2] for x in sys.argv[1:] if x.startswith("--"))
    if a and a[0] == "crop":
        crop()
    elif a and a[0] == "gen":
        gen(a[1], "dry-run" in o, o.get("src"))
    else:
        sys.exit(__doc__)
