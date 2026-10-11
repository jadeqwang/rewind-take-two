#!/usr/bin/env python3
"""v4 note 0:13 (the Bean): the WIDE plate, painted outward from the close plate (nano-banana-pro, 4K).

    PY=~/Documents/moongazing/.venv/bin/python
    $PY tools/v4B/bean/plate.py guides                 # free: the two input canvases (media/sing/plates/plate_wide_v4_guide_{A,B}.jpg)
    $PY tools/v4B/bean/plate.py gen A|B [--n=1] [--dry-run]   # PAID ($0.24 a picture): plate_wide_v4_<A|B><i>.png + .json
    $PY tools/v4B/bean/plate.py edit SRC KEY [--dry-run]      # PAID: a corrective edit of a candidate (EDITS[KEY])
    $PY tools/v4B/bean/plate.py finish SRC             # free: close plate's own pixels laid back -> plate_wide_v4.png, planes

Geometry (4K canvas 5504x3072 = the wide frame; plate px = px of media/sing/plates/plate_close_1.jpg, 2752x1536):
  the close plate sits UNSCALED at PASTE = (1350, 106). The v4 take's own background is that plate at
  0.7355 design px per plate px, offset (-66.5, -48.3) (SIFT fit on the take, tools/v4B/bean notes), so the wide frame
  shows the Bean plane at 0.34884 / 0.7355 = 0.4743 of its landed scale, fixed point (955.8, 114.0) design px.
  A = grey canvas round the plate + plate_sane_1 as a shape reference.  B = a rough collage of the whole frame
  (the previz stand-in) round the plate, to be redrawn as finished engraving.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
sys.path.insert(0, HERE)

MODEL = "google/nano-banana-pro"
PLATES = "media/sing/plates"
CLOSE = PLATES + "/plate_close_1.jpg"
SANE = PLATES + "/plate_sane_1.jpg"
CW, CH = 5504, 3072
PASTE = (1350, 106)
TAKE_FIT = (0.7355, -66.5, -48.3)            # plate px -> landed design px (scale, tx, ty)
WIDE = 1920 / CW                             # canvas px -> wide design px
BEAN0 = WIDE / TAKE_FIT[0]                   # 0.4743
BEAN_C = ((PASTE[0] * WIDE - BEAN0 * TAKE_FIT[1]) / (1 - BEAN0), (PASTE[1] * WIDE - BEAN0 * TAKE_FIT[2]) / (1 - BEAN0))

ENGRAVING = ("Black-and-white wood engraving in the style of M.C. Escher's woodcuts and lithographs: dense, precise "
             "cross-hatching and engraved parallel lines, crisp solid black ink on off-white paper; every tone is built "
             "only from lines and hatching; no gray wash, no gradients, no airbrush, no photographic shading. Night is "
             "drawn the engraver's way: dark tones from dense parallel lines and cross-hatching, every light left as white "
             "paper with a small halo of radiating lines. Very high detail, architectural precision. No text, no letters, "
             "no signs, no signature, no border, no frame.")

SCENE = ("The finished picture is a wide view of Cloud Gate ('the Bean') in Millennium Park, Chicago, at night, seen "
         "from the side at eye level from across the plaza: the whole sculpture is in the picture with night sky above "
         "it and to both sides, one seamless polished-steel kidney-bean shape about twice as wide as it is tall, "
         "filling a little under two thirds of the picture's width, with the low arch underneath its middle (we can "
         "see through the arch to lamps and trees beyond), resting on the stone paving of the plaza. Its mirror "
         "surface reflects the city, and below the skyline it goes on reflecting the plaza, curving under toward the "
         "arch. Behind the Bean, dark towers of the Chicago Loop stand along the far side of the plaza and rise out "
         "of the top of the picture, their windows tiny white cells, darker and quieter than the Bean, so the "
         "polished steel is the brightest thing in the picture; a low hedge, trees and a row of lamp posts run along "
         "the far edge of the plaza. Six or seven tiny pedestrians stand or walk on the paving near the foot of the "
         "Bean to its left and right, each about a sixth of its height, drawn as small engraved figures in coats; "
         "none of them in the bottom centre of the picture. The paving is square stone slabs in perspective. The "
         "bottom centre of the picture is empty paving in MID-TONE engraved hatching, clearly darker than white paper "
         "(a pale figure will be placed there later); the pool of lamp light, left as white paper, lies under and "
         "beside the Bean. Light: the bright highlight sits on the Bean's upper right, as in the existing engraving. "
         "The parts outside the existing engraving are seen small, so draw them with a slightly bolder, more open "
         "line. Black ink on off-white paper only: no colour anywhere, no red, no text, no lettering, no signs, no "
         "signature, no border, no margin, drawn to all four edges. 16:9. ")

PROMPTS = {
    "A": ("Image 1 is an unfinished picture: a finished black-and-white wood engraving sits in its upper middle, and "
          "the flat grey round it is empty canvas that has not been drawn yet. The finished engraving is a close view of "
          "the upper part of Cloud Gate: its top edge is the top of the sculpture, and what it shows is the sculpture's "
          "mirror surface reflecting a city skyline and a plaza. Paint the rest of the picture: replace every bit of "
          "the grey with engraving that continues the existing one seamlessly, so that no rectangle, seam or change of "
          "style can be seen where the existing engraving ends. Keep the existing engraving exactly as it is, where "
          "it is, at the size it is: every building, line and star of it; do not redraw, move, shrink or crop it. The "
          "curved top edge of the sculpture in the existing engraving continues outward and down on both sides as the "
          "sculpture's outline. Image 2 is a reference for the form of the lower body and the arch only: copy their "
          "form, not its reflection, its framing or its border. " + SCENE + ENGRAVING),
    "B": ("Image 1 is a rough layout collage for a picture. In its upper middle sits a finished black-and-white wood "
          "engraving: the upper part of Cloud Gate's mirror surface, reflecting a city skyline and a plaza. Everything "
          "round it is rough paste-up that only shows where things go: the rest of the sculpture's outline, its lower "
          "body and arch, the plaza, a skyline strip, and crude black placeholder shapes for pedestrians. Redraw the "
          "whole picture as one finished, seamless wood engraving with the same layout: the sculpture's outline, arch, "
          "foot and the plaza's horizon stay exactly where the collage puts them. Keep the finished engraving in the "
          "upper middle exactly as it is, where it is, at the size it is: every building, line and star of it; do not "
          "redraw, move, shrink or crop it. Everything else is drawn new, properly, in the same hand: no seam, no "
          "rectangle and no change of style where the collage's pieces met; the placeholder figures become small "
          "engraved pedestrians; the flat skyline strip becomes real towers standing behind the plaza; the ruled "
          "paving becomes stone slabs in perspective. " + SCENE + ENGRAVING),
}

EDITS = {
    # filled in when a candidate needs a correction; each is "keep everything, change only X"
    "paving": ("Image 1 is a black-and-white wood engraving of Cloud Gate in Chicago at night. Keep everything exactly as "
               "it is: the sculpture, its reflection, the towers, the people, the framing. Change only the paving in the "
               "bottom centre of the picture, below the sculpture's arch: shade it in mid-tone engraved hatching, clearly "
               "darker than white paper, the slabs still visible. No colour, no text, no border. 16:9."),
    "towers": ("Image 1 is a black-and-white wood engraving of Cloud Gate in Chicago at night. Keep everything exactly as "
               "it is: the sculpture, its reflection, the plaza, the people, the framing. Change only what stands behind "
               "the sculpture: dark towers of the Chicago Loop along the far side of the plaza, rising out of the top of "
               "the picture, windows as tiny white cells, darker than the sculpture. No colour, no text, no border. 16:9."),
}


def canvas_a():
    c = Image.new("RGB", (CW, CH), (128, 128, 128))
    c.paste(Image.open(CLOSE).convert("RGB"), PASTE)
    return c


def rim_mask(feather=60):
    """plate-px mask of the close plate that is safe to lay back: inside the Bean's rim and away from the plate's
    left, right and bottom edges (where the outpaint has to blend), feathered. The top corners (sky) are left to the model."""
    import numpy as np
    yy, xx = np.mgrid[0:1536, 0:2752].astype(np.float32)
    s, tx, ty = TAKE_FIT
    dx, dy = xx * s + tx, yy * s + ty                       # landed design px
    rim = 1 - ((dx - 965) / 1235) ** 2 - ((dy - 715) / 712) ** 2
    a = np.clip(rim / 0.05, 0, 1)
    a *= np.clip(xx / 320, 0, 1) * np.clip((2752 - xx) / 320, 0, 1) * np.clip((1536 - yy) / 360, 0, 1)
    return Image.fromarray((a * 255).astype(np.uint8))


def canvas_b():
    sys.argv = sys.argv[:1]
    import previz as pz
    pz.BEAN_FRAC0 = BEAN0 * pz.BEAN_W_END / 1920; pz.BEAN0 = BEAN0; pz.BEAN_C = BEAN_C
    pz.BEAN_TOP0 = (PASTE[1] + (0 - TAKE_FIT[2]) / TAKE_FIT[0]) * WIDE          # the rim top (design y 0 landed) in the wide frame
    far, geo, P = pz.build_standin()
    if os.environ.get("BEAN_GUIDE", "2") != "1":
        # guide 2 (B2 on): the stand-in's skyline is one strip mirrored about the centre, and B1 copied that faithfully
        # (the same X-braced tower left and right). Here: the strip unflipped on the left (the X-braced tower) and
        # flipped on the right (the stepped tower with two antennas), the seam hidden behind the Bean.
        import numpy as np
        sk = Image.open(pz.SKY).convert("L").crop((690, 0, 2560, 712))
        sk = Image.merge("RGB", [sk.point(lambda v, f=f: int(v * f)) for f in (0.80, 0.78, 0.74)])
        top = np.linspace(0, 1, 200)[:, None] ** 1.5
        arr = np.asarray(sk).astype(np.float32); arr[:200] = arr[:200] * top[..., None] + 16 * (1 - top[..., None])
        sk = Image.fromarray(arr.astype(np.uint8))
        far.paste((16, 16, 18), (0, far.height - sk.height, far.width, far.height))
        far.paste(sk, (960 - 1265 - geo[0], far.height - sk.height))
        far.paste(sk.transpose(Image.FLIP_LEFT_RIGHT), (1087 - geo[0], far.height - sk.height))
    # mid-tone hatching over the near paving, so the layout says "not bare paper here"
    d = ImageDraw.Draw(P); hz = int(pz.HORIZON0 * pz.SS)
    for y in range(hz + 300, P.height, 9):
        d.line([0, y, P.width, y], fill=pz.INK + (255,), width=3)
    fr = pz.far_layer(far, geo, BEAN0, 0).resize((CW, CH), Image.LANCZOS).convert("RGBA")
    fr.alpha_composite(P.resize((CW, CH), Image.LANCZOS))
    fr = fr.convert("RGB")
    fr.paste(Image.open(CLOSE).convert("RGB"), PASTE, rim_mask())
    return fr


def guides():
    """guide_A and guide_B (mirrored skyline, used for A1 and B1) are kept; guide_B2 is the asymmetric one"""
    for k, fn in (("A", canvas_a), ("B2", canvas_b)):
        p = f"{PLATES}/plate_wide_v4_guide_{k}.jpg"
        if os.path.exists(p): continue
        fn().resize((2752, 1536), Image.LANCZOS).save(p, quality=92); print("wrote", p)


def gen(key, n=1, dry=False):
    import cf
    out = []
    refs = [f"{PLATES}/plate_wide_v4_guide_{'A' if key == 'A' else 'B2'}.jpg"] + ([SANE] if key == "A" else [])   # B1 used guide_B
    for _ in range(n):
        i = 1
        while os.path.exists(f"{PLATES}/plate_wide_v4_{key}{i}.png") or os.path.exists(f"{PLATES}/plate_wide_v4_{key}{i}.jpg"):
            i += 1
        p = f"{PLATES}/plate_wide_v4_{key}{i}.png"
        inp = {"prompt": PROMPTS[key], "aspect_ratio": "16:9", "image_size": "4K", "image_input": ["file:" + r for r in refs]}
        if dry:
            print("DRY", p, cf.estimate(MODEL, inp), refs); cf.validate(MODEL, inp); continue
        got = cf.generate(MODEL, inp, p, tag=f"v4B_bean_wide_{key}{i}")
        json.dump({"model": MODEL, "image_size": "4K", "aspect_ratio": "16:9", "refs": refs, "prompt": PROMPTS[key],
                   "tag": f"v4B_bean_wide_{key}{i}", "out": got}, open(os.path.splitext(p)[0] + ".json", "w"), indent=1)
        out += got; print("wrote", got)
    return out


def edit(src, key, dry=False):
    import cf
    base = os.path.splitext(os.path.basename(src))[0]
    p = f"{PLATES}/{base}_{key}.png"
    small = f"{PLATES}/{base}_in2k.jpg"
    if not os.path.exists(small):
        Image.open(src).convert("RGB").resize((2752, 1536), Image.LANCZOS).save(small, quality=93)
    inp = {"prompt": EDITS[key], "aspect_ratio": "16:9", "image_size": "4K", "image_input": ["file:" + small]}
    if dry:
        print("DRY", p, cf.estimate(MODEL, inp)); cf.validate(MODEL, inp); return
    got = cf.generate(MODEL, inp, p, tag=f"v4B_bean_edit_{key}")
    json.dump({"model": MODEL, "image_size": "4K", "refs": [small], "prompt": EDITS[key], "tag": f"v4B_bean_edit_{key}", "out": got},
              open(os.path.splitext(p)[0] + ".json", "w"), indent=1)
    print("wrote", got)


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    o = dict((x[2:].split("=", 1) + ["1"])[:2] for x in sys.argv[1:] if x.startswith("--"))
    if a[0] == "guides":
        guides()
    elif a[0] == "gen":
        gen(a[1], int(o.get("n", 1)), "dry-run" in o)
    elif a[0] == "edit":
        edit(a[1], a[2], "dry-run" in o)
    else:
        sys.exit(__doc__)
