#!/usr/bin/env python3
"""v4 note 1:30 (the car, option C): keyframes for the built shot.

  V2f4 = the mirror close (the END of the push), generated first.
  V2f3 = the wide over her right shoulder (the START), painted outward from a canvas that already holds the finished
         mirror at its wide-shot size, so the engine's push ends in register (the Bean recipe, docs/revisions/v4/plans/bean.md).

    PY=~/Documents/moongazing/.venv/bin/python
    $PY tools/v4B/car/kf.py LIST
    $PY tools/v4B/car/kf.py run close_a close_b [--dry-run]
    $PY tools/v4B/car/kf.py canvas media/shots/V2f4/kf_close_a.jpg      # builds media/shots/V2f3/canvas.png for the wide jobs
    $PY tools/v4B/car/kf.py run wide_a wide_b

Layout references are the three.js blockout (tools/v4B/car/car_scene.html?kf=wide|close). No lettering is drawn by the
model: the road sign, the words on the mirror's lower edge and the plates are pinned by the engine.
Every call is tagged v4B_car_kf_<job>; prompts, model and refs are appended to media/shots/<shot>/kf_log.jsonl.
"""
import concurrent.futures as cfut
import json
import os
import sys
import time

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
sys.path.insert(0, os.path.join(ROOT, "tools/sectionA"))
import cf  # noqa: E402
from common import ref, trim_margins  # noqa: E402
from PIL import Image  # noqa: E402

NBP = "google/nano-banana-pro"
F3, F4 = "media/shots/V2f3", "media/shots/V2f4"

NIGHT = ("Drawn as an M.C. Escher wood engraving at night: the dark sky, the car interior and all shadows are carved "
         "from dense black ink with fine white engraved lines, every light (headlights, strobes, streetlamps) is a crisp "
         "white engraved starburst of radiating lines, warm off-white paper shows only in the lit areas. Crisp black ink "
         "lines, dense precise parallel hatching and cross-hatching that follows form, high contrast, no gray wash, no "
         "airbrush, no photographic shading. Full bleed, edge to edge, no border, no margin, no frame, 16:9. ")
NOTEXT = ("There is NO text, no letters, no numbers and no writing anywhere in the picture: every licence plate is a "
          "completely blank pale rectangle, the mirror carries no writing, there are no road signs with writing, no "
          "signature, no watermark, no caption. No red and no blue anywhere: every light is white. ")

FLEET = ("In the mirror glass, reflected through the car's rear window: a plain boxy black 1990s government sedan fills "
         "the centre of the glass, head-on and very close behind, tailgating. We see its windshield, its hood, a plain "
         "grille with no badge or emblem, two headlights blazing as white engraved starbursts, its front bumper and, in "
         "the middle of the bumper, a LARGE BLANK front licence plate: a plain pale rectangle with a thin dark border and "
         "nothing on it. On its roof, a light bar with white strobe starbursts. To its left and to its right, half a car "
         "length further back, two more identical black sedans, each with a blank pale plate; behind them a river of "
         "identical black sedans fills every lane of an expressway and recedes toward the Chicago skyline at night, "
         "white starburst strobes on every roof. Along the very bottom edge of the glass runs a narrow pale strip: the "
         "white boot lid of the car we are riding in. At the far left and right ends of the glass, the dark edges of the "
         "rear window. ")

CLOSE = ("Image 1 is a rough 3D staging blockout: follow its layout closely (a car's interior rear-view mirror seen "
         "squarely, filling about four fifths of the frame width, its glass in the upper two thirds and a deep blank "
         "lower edge under the glass; in the glass a black sedan dead centre between two others), but redraw everything "
         "properly in the style described below and do not copy its crude boxes. Image 2 shows the drawing style, the "
         "night and the black sedans of this film: match its engraving line work and its cars, not its composition. "
         "Night, inside a moving car, looking forward from between the front seats at the interior rear-view mirror. "
         "The mirror hangs on a short stalk from the top of the windshield and is seen squarely, exactly level, not "
         "tilted: a wide, shallow rectangle with gently rounded corners in a plain black plastic housing. The housing "
         "has a deep, plain lower edge: a smooth flat black band below the glass, about a third as tall as the glass and "
         "as wide as the mirror, completely blank and empty, with no buttons, no lights and no writing. " + FLEET +
         "Around the mirror: above it, the dark headliner and the top of the windshield; behind and below it, through "
         "the windshield, only black night sky and a few small distant white streetlights. Nothing else is in the "
         "picture: no people, no hands, no steering wheel. " + NIGHT +
         "The whole picture is black-and-white engraving with no color at all. " + NOTEXT)

JADE = ("The driver is EXACTLY the anime girl of the character sheets (images 2 and 3), seen from behind: same anime "
        "drawing style with clean cel shading, in FULL COLOR. Black hair worn up in a loose bun high on the back of her "
        "head, with exactly TWO classic yellow wooden pencils pushed through the bun and crossed in an X, erasers up "
        "(one pink eraser, one pale-blue eraser), each pencil one perfectly straight stick; a few loose strands and "
        "her long curtain bangs fall beside her cheek. Her head is turned a little to her right, up toward the mirror, "
        "so we see her right ear, her cheek, the line of her jaw and the corner of her eye. Orange over-ear headphones "
        "rest around her neck, clearly visible above her collar. She wears her white cropped bomber jacket with ONE "
        "orange band around each sleeve, over a black mock-neck top. Both of her hands are on the steering wheel, at "
        "ten and two. ")

WIDE = ("Image 1 is a rough 3D staging blockout in which ONE thing is already finished: the small interior rear-view "
        "mirror at the upper right, a wood engraving of black sedans seen in the glass. Keep that mirror exactly where "
        "it is, at exactly that size, and do not redraw or change it. Redraw everything else properly in the style "
        "described below, following the blockout's camera angle and layout, without copying its crude shapes. "
        "Images 2 and 3 are character sheets of the girl. "
        "Night, inside a moving LEFT-HAND-DRIVE car (a white 2001 Acura TL sedan), seen from the back seat over the "
        "driver's RIGHT shoulder, the lens low, at the height of her shoulders, looking forward and slightly up. The "
        "driver sits in the front LEFT seat, on the left of the picture, large in the foreground and seen from behind: "
        "the back of her head and her bun in the upper left, her shoulders across the lower left; her seat's headrest "
        "is pushed right down so that her whole head shows. In front of her, left of centre, the STEERING WHEEL with "
        "both of her hands on it, the instrument binnacle with two round dials behind the wheel, and the dashboard "
        "running across the frame to the right; the centre console and radio at the lower right; the edge of the empty "
        "front passenger seat at the far right. Through the wide windshield: a dark expressway at night with white lane "
        "dashes rushing toward us and curving gently to the left, low concrete barriers, and only two or three small "
        "distant streetlights close to the horizon. Between her head and the mirror, above the steering wheel, the "
        "windshield shows a LARGE EMPTY area of plain black night sky with nothing in it at all (no sign, no gantry, no "
        "lamp posts, no moon, no clouds). The windshield header and the dark headliner run across the top; the mirror "
        "hangs from the header. " + JADE + NIGHT +
        "The car interior, the road and the night are black-and-white engraving; the ONLY color in the picture is the "
        "girl (her skin, the yellow pencils with their pink and pale-blue erasers, the orange headphones, the orange "
        "sleeve bands). " + NOTEXT)

# corrective edit of close_b (chosen): the agents' sedans carry no badge (canon), and nothing but night below the mirror
CLOSE_FIX = ("Edit the attached image. Keep the whole picture exactly as it is: same composition, same framing, same mirror "
             "at the same size and place, the same cars in the same places, the same black-and-white wood-engraving line "
             "work. Change ONLY the following. 1. Every car's grille: remove the oval badge / emblem and any marks inside "
             "it, and continue the grille's plain horizontal bars across where it was, so each grille is plain with no "
             "badge, no logo and no writing. 2. Below the mirror, at the bottom of the picture: remove all the starburst "
             "lights and their poles, leaving that whole area plain flat black, empty. 3. The lower edge of the mirror "
             "housing, under the glass: make it a plain smooth flat black band running the full width of the mirror, "
             "completely blank. The three licence plates stay blank pale rectangles. No text, no letters, no numbers "
             "anywhere. No color. Full bleed, 16:9, no border.")

JOBS = {
    # name: (shot dir, prompt, refs)
    "close_a": (F4, CLOSE, [F4 + "/blockout_close.png", "media/shots/V2f1/kf_s.jpg"]),
    "close_b": (F4, CLOSE, [F4 + "/blockout_close.png", "media/shots/V2f2/kf_v3d.jpg"]),
    "close_b2": (F4, CLOSE_FIX, [F4 + "/kf_close_b.jpg"]),
    "wide_a": (F3, WIDE, [F3 + "/canvas.png", "media/design/jade_canon_turnaround.png", "media/design/jade_bun_two_pencils.png"]),
    "wide_b": (F3, WIDE, [F3 + "/canvas.png", "media/design/jade_canon_turnaround.png", "media/design/jade_bun_two_pencils.png"]),
}

# where the finished mirror sits in the wide frame (1920x1080 design px): the close keyframe, whole, is pasted here.
# From the blockout: the mirror body is 360 px wide in the wide reference and ~1757 px in the close reference.
INSET = dict(cx=1310, cy=452, k=0.205)   # centre of the pasted close frame, and its scale (wide px per close px)


def canvas(close_path):
    """media/shots/V2f3/canvas.png: the wide blockout with the finished close keyframe laid in at the mirror."""
    base = Image.open(os.path.join(ROOT, F3, "blockout_wide.png")).convert("RGB")
    W, H = base.size
    s = W / 1920
    cl = Image.open(os.path.join(ROOT, close_path)).convert("RGB")
    w = round(1920 * INSET["k"] * s)
    h = round(w * cl.height / cl.width)
    cl = cl.resize((w, h), Image.LANCZOS)
    x, y = round(INSET["cx"] * s - w / 2), round(INSET["cy"] * s - h / 2)
    base.paste(cl, (x, y))
    out = os.path.join(ROOT, F3, "canvas.png")
    base.save(out)
    json.dump({"close": close_path, "rect_design_px": [x / s, y / s, w / s, h / s], **INSET},
              open(os.path.join(ROOT, F3, "canvas.json"), "w"), indent=1)
    print("wrote", out, "inset rect (design px)", [round(v / s, 1) for v in (x, y, w, h)])


def run(name, dry=False):
    shot, prompt, refs = JOBS[name]
    out = os.path.join(ROOT, shot, f"kf_{name}.png")
    inp = {"prompt": prompt, "aspect_ratio": "16:9", "image_size": "2K", "output_format": "png",
           "image_input": ["file:" + ref(r, 2048) for r in refs]}
    paths = cf.generate(NBP, inp, out, tag=f"v4B_car_kf_{name}", dry_run=dry)
    if dry:
        return name, None
    p = paths[0]
    trim_margins(p)
    jpg = os.path.splitext(p)[0] + ".jpg"
    Image.open(p).convert("RGB").save(jpg, quality=93)
    with open(os.path.join(ROOT, shot, "kf_log.jsonl"), "a") as f:
        f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "job": name, "model": NBP, "image_size": "2K",
                            "seed": None, "refs": refs, "prompt": prompt, "out": os.path.relpath(jpg, ROOT)}) + "\n")
    return name, jpg


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "LIST":
        for k, (shot, _, refs) in JOBS.items():
            print(k, shot, refs)
    elif a[0] == "canvas":
        canvas(a[1])
    elif a[0] == "run":
        dry = "--dry-run" in a
        names = [x for x in a[1:] if not x.startswith("--")]
        with cfut.ThreadPoolExecutor(4) as ex:
            for name, p in ex.map(lambda n: run(n, dry), names):
                print(name, "->", p)
