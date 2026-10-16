#!/usr/bin/env python3
"""v9 fix 1b (C10_V2b3, 1:06.28-1:07.16): re-staged keyframe. Jade in the LEFT (driver) seat of the left-hand-drive
Acura, wheel in front of her, two crossed pencils, orange headphones; the flipping sedan stays OUTSIDE the glass.

    PY=~/Documents/1-music-shipped/moongazing/.venv/bin/python
    $PY tools/v9/v2b3_kf.py VARIANT [--dry-run]       # writes media/shots/V2b3/kf_v9<VARIANT>.png

Refs: image 1 = the C_V2f_car wide (correct LHD staging and the film's Acura interior), image 2 = canon turnaround,
image 3 = the two-pencil bun sheet. Tag v9_1b_kf_<variant>.
"""
import json
import os
import sys

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
sys.path.insert(0, os.path.join(ROOT, "tools/sectionC"))
import cf  # noqa: E402
from common import inp_for, trim_margins  # noqa: E402

REFS = ["media/shots/V2f3/kf_wide_b_fix_engraved.png", "media/design/jade_canon_turnaround.png",
        "media/design/jade_bun_two_pencils.png"]

STAGING = (
    "Image 1 is a frame from this film: the same car, the same drawing style, the same girl. Follow its staging: we are "
    "in the back seat of her white Acura sedan, a LEFT-HAND-DRIVE car, looking forward between the two front seats. The "
    "steering wheel is on the LEFT side of the car and the girl sits in the LEFT front seat, the driver's seat, directly "
    "behind the wheel, the wheel right in front of her chest. The right front seat (the passenger seat, screen right) is "
    "EMPTY: just its plain engraved headrest and seatback. Same dashboard and centre console as image 1. "
    "This time the camera sits a little lower and further back, so the whole windshield is visible: the dark headliner "
    "and the top edge of the windshield frame run across the top of the picture, the two A-pillars frame the windshield "
    "at left and right, and the dashboard runs across the lower third. "
    "Through the windshield, OUTSIDE the car, beyond the glass: an upside-down black 1990s government sedan is tumbling "
    "through the air just above the hood, a few metres ahead, its underside facing us and engraved in detail (axles, "
    "exhaust, four wheels), its roof light bar a crisp white starburst. It is entirely outside the car, seen THROUGH the "
    "glass, its edges cut off cleanly by the windshield frame and the A-pillars; the car's own roof, headliner and "
    "pillars are solid and in FRONT of it. Engraved night road and white starburst streetlights beyond. "
    "The girl is in the driver's seat, seen from behind over her right shoulder, the upper third of her body: she ducks "
    "low behind the wheel, shoulders hunched, both hands gripping the steering wheel at ten and two, her head tilted up "
    "toward the upside-down car, so we see her right ear, cheek, jaw and one wide eye in three-quarter rear view. ")

JADE = (
    "She is EXACTLY the anime girl of the character sheets (images 2 and 3), in FULL COLOR with clean cel shading: black "
    "hair worn up in a loose bun high on the back of her head, with exactly TWO classic yellow wooden pencils pushed "
    "through the bun and crossed in an X, erasers up (one pink eraser, one pale-blue eraser), each pencil one perfectly "
    "straight stick; a few loose strands beside her cheek. Orange over-ear headphones rest around her NECK, clearly "
    "visible above her collar. Her white cropped bomber jacket: an orange band around each sleeve, the back panel plain "
    "white with one large pale-blue dot centred between her shoulder blades. ")

STYLE = (
    "Everything except the girl is drawn as an M.C. Escher wood engraving at night: black ink with fine white engraved "
    "lines in the shadows, every light a crisp white engraved starburst of radiating lines, warm off-white paper in the lit "
    "areas, dense precise parallel hatching and cross-hatching that follows form, high contrast, no gray wash, no "
    "airbrush, no color anywhere except the girl. Full bleed, edge to edge, no border, no frame, 16:9. No text, no "
    "letters, no numbers, no logos, no licence plates with writing, no signature, no watermark.")

PROMPTS = {"a": STAGING + JADE + STYLE}

# b: a's staging plus fixes seen on a (pencils not a clean X, the back dot split in two, her headrest beside her head)
FIX_B = ("Details that matter: the two pencils cross each other in a neat X right through the middle of the bun, each "
         "sticking out only a short way on both sides of the bun (no pencil reaches her neck or shoulders). The pale-blue "
         "dot on her back is ONE single round dot, whole, not split. Her own seat's headrest is directly behind her head, "
         "partly hidden by her, not beside her. The black sedan is completely upside-down: roof down, four wheels up. ")
PROMPTS["b"] = STAGING + JADE + FIX_B + STYLE

# c: a's staging (b drifted off-model: western cartoon face, her seat shifted toward the middle) + the pencil/dot fixes
FIX_C = ("Her face is the soft anime face of image 2 (large dark anime eyes, small nose), never a western cartoon. She sits "
         "squarely in the left seat, her own seat's headrest directly behind her head. The two pencils cross each other "
         "in a neat X right through the middle of the bun, each sticking out only a short way on both sides of it (no "
         "pencil reaches her neck). The pale-blue dot on her back is ONE single round dot, whole. ")
PROMPTS["c"] = STAGING + JADE + FIX_C + STYLE

if __name__ == "__main__":  # noqa: E305
    v = sys.argv[1]
    out = os.path.join(ROOT, f"media/shots/V2b3/kf_v9{v}.png")
    model = "google/nano-banana-pro"
    inp = inp_for(model, PROMPTS[v], REFS)
    if "--dry-run" in sys.argv:
        print(json.dumps({k: (x if k != "image_input" else len(x)) for k, x in inp.items()})[:400]); sys.exit()
    paths = cf.generate(model, inp, out, tag=f"v9_1b_kf_{v}")
    trim_margins(paths[0])
    with open(os.path.join(ROOT, "media/shots/V2b3/kf_log.jsonl"), "a") as f:
        f.write(json.dumps(dict(variant=v, model=model, refs=REFS, prompt=PROMPTS[v], out=paths[0])) + "\n")
    print(paths)

