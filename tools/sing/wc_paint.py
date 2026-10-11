#!/usr/bin/env python3
"""Watercolor singing Jade (v3), step 2: the engraved Bean plate put round her kept watercolor portrait
(nano-banana-pro; after tools/sing/paint.py "paint2" and moongazing-public-version work/singer5/p_pool.txt).

    PY=~/Documents/moongazing/.venv/bin/python
    $PY tools/sing/wc_paint.py [--n=2] [--key=wc] [--dry-run]

Image 1 = media/sing/first/v3_base16.jpg (wc_base.py), image 2 = media/sing/plates/plate_close_1.jpg.
Outputs media/sing/first/v3_paint_<key>_<i>.png. Logged and capped by tools/gen/cf.py (tag revA_sing_paint).
The rule: she is never redrawn. The model only takes the old paper away, continues her sleeves and puts the plate
behind her; her own pixels go back afterwards (wc_restore.py). She stays a watercolor and the world stays an
engraving: the mismatch is the point of the shot."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
import cf  # noqa: E402

MODEL = "google/nano-banana-pro"
VER = os.environ.get("WC_VER", "v3")      # v4: WC_VER=v4 (new portrait: glossier hair, less smile); see docs/revisions/v4/A.md
BASE = f"media/sing/first/{VER}_base16.jpg"
# what the prompt says of her mouth and hair: v3 is the smiling portrait, v4 is whatever Jade picked (v4_pick.py)
MOUTH = "the same open smile" if VER == "v3" else "exactly the same expression and the same mouth, as painted"
HAIR = ("the long loose dark hair with all its wisps at its full length" if VER == "v3" else
        "the long dark hair exactly as it is painted, with its sheen, its locks and its full length")
PLATE = "media/sing/plates/plate_close_1.jpg"

KEEP_HER = (
    "Image 1 is a Chinese ink-and-wash watercolour portrait of a woman on cream textured paper (the plain cream bands at "
    "its left, right and top are blank paper). Image 2 is a plate from the film this picture belongs to: the place where "
    "she stands, right in front of the mirror of Cloud Gate ('the Bean') in Millennium Park, Chicago, at night, drawn as a "
    "black-and-white wood engraving in the manner of M.C. Escher.\n\n"
    "Make image 1 into a frame for that film by replacing only what is around her. Keep the woman exactly as she is "
    "painted: the same watercolour brushwork and paper grain inside her, the same face, head size, shape and tilt, the same "
    "high forehead and hairline, glasses, the two slightly different eyebrows, eyes, nose, " + MOUTH + ", " + HAIR + ", "
    "the cropped white jacket with its orange band, its small blue "
    "disc and the round black-and-white '1420 MHz' patch on the sleeve, the black mock-neck top, her pose, size and position "
    "in the picture: her head exactly as large as in image 1 and in the same spot, in the middle of the picture, the bottom "
    "edge cutting her at the chest. Do not redraw, move, resize, turn, beautify, slim or restyle her in any way: no makeup, "
    "no eyeliner, no outlined lips, no added lines, no smoothing. Nothing is added to her: no headphones, nothing round her "
    "neck, no jewellery. Where the edge of the old paper cut her sleeves off at the left and right, continue the jacket a "
    "little in the same watercolour brushwork (white with soft blue-grey shading and the same orange band round the "
    "sleeve), her arms hanging down at her sides and running out of the bottom of the picture.\n\n")

HER_COLOURS = (
    "Her colours stay exactly as painted, fully saturated: warm peach skin with pink cheeks; thin dark glasses frames with "
    "clear lenses; soft warm brown-black hair; the jacket white with its ember-orange band and pale-blue disc; the top "
    "black. She is not tinted, greyed, cooled or darkened for the night, and no engraving lines or hatching are drawn on "
    "her.\n\n")

PLACE = (
    "The place around her replaces everything else in image 1: the cream paper, the plum blossom branch with its pink "
    "flowers and the grey ink mountains all go, completely. Behind her is image 2, kept exactly as it is drawn, at the same "
    "size and position as in image 2: the Bean's mirror fills the whole background, with the reflected city skyline to the "
    "left and right of her head, the pale plaza with its lamp posts beside her shoulders, the flat rooftop with the small "
    "square stairwell in the lower left corner and the curving road with tiny headlights by the lake at the right edge. "
    "Everything around her is the black-and-white wood engraving of image 2: crisp black ink lines and cross-hatching on "
    "off-white paper, no colour and no watercolour wash in it anywhere. The mirror does not show her own reflection. Do not "
    "add another sculpture, bean shape, dome or frame behind her.\n\n")

MISMATCH = (
    "The two manners do not blend, on purpose: she is a soft colour watercolour and the world behind her is a hard "
    "black-and-white engraving, like a painted figure standing in a printed world. But she is not a pasted cutout: the "
    "engraving is drawn right up to her and shows between and around every wisp of her hair, with no cream paper left "
    "there, no pale fringe, no halo, no glow, no white outline and no drop shadow round her hair, head or shoulders.\n\n")

STRICT = (
    "Strict: 16:9, drawn to all four edges, no border, no cream paper left anywhere in the background. No pink or red "
    "anywhere. No text, letters, numbers or anything like writing anywhere except the sleeve patch she already wears; no "
    "seal, signature or logo. Nobody else in the foreground.")

PROMPTS = {"wc": KEEP_HER + HER_COLOURS + PLACE + MISMATCH + STRICT}


def main(argv):
    o = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    key, n = o.get("key", "wc"), int(o.get("n", 2))
    out = []
    for _ in range(n):
        i = 1
        while any(os.path.exists(os.path.join(ROOT, f"media/sing/first/{VER}_paint_{key}_{i}{e}")) for e in (".png", ".jpg", ".webp")):
            i += 1
        p = os.path.join(ROOT, f"media/sing/first/{VER}_paint_{key}_{i}.png")
        inp = {"prompt": PROMPTS[key], "aspect_ratio": "16:9", "image_size": "2K",
               "image_input": ["file:" + BASE, "file:" + PLATE]}
        out += cf.generate(MODEL, inp, p, tag="revA_sing_paint" if VER == "v3" else f"{VER}A_sing_paint", dry_run="--dry-run" in argv)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1:])
