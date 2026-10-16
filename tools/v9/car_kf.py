#!/usr/bin/env python3
"""v9 fix 1a + 9 (P2 0:38.90, P1/P1b 0:37.96 and 0:39.68): re-staged keyframes that agree with D7 (0:35).

D7 (media/shots/D7/kf_v3_2.jpg, the keyframe the 0:35 frame lands on) is the agent's view through her OPEN driver's
window: the Acura's nose is screen LEFT, she is in the left-hand-drive car's driver's seat, wheel in front of her. D6/D8
look out of that window at the agent with the lake behind him, so the agent and the lake are on the driver's side.

    PY=~/Documents/1-music-shipped/moongazing/.venv/bin/python
    $PY tools/v9/car_kf.py SHOT VARIANT [--dry-run]     # SHOT = P2 | P1; writes media/shots/SHOT/kf_v9<VARIANT>.png

Tag v9_1a_kf_<variant> (P2) / v9_9_kf_<variant> (P1).
"""
import json
import os
import sys

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
sys.path.insert(0, os.path.join(ROOT, "tools/sectionA"))
import cf  # noqa: E402
from common import inp_for, trim_margins  # noqa: E402

D7 = "media/shots/D7/kf_v3_2.jpg"            # the 0:35 frame's keyframe (no letterbox, no dialogue box)
P2_OLD = "media/shots/P2/kf_v3_1.jpg"        # her shocked face, two-pencil bun
P1_OLD = "media/shots/P1/kf_nbp2.jpg"        # the agent, the take_2 keyframe
BUN = "media/design/jade_bun_two_pencils.png"

JADE = (
    "She is EXACTLY the anime girl of the earlier film frames, in FULL COLOR with clean cel shading: black hair with a "
    "centre part and long curtain bangs, worn up in a loose bun with exactly TWO classic yellow wooden pencils pushed "
    "through the bun and crossed in an X, erasers up (one pink eraser, one pale-blue eraser), each pencil one perfectly "
    "straight stick; orange over-ear headphones resting around her NECK; white cropped bomber jacket worn open with an "
    "orange band across the chest and around both sleeves, a small pale-blue dot patch on her LEFT chest, a round white "
    "'1420 MHz' roundel on her LEFT upper sleeve; black mock-neck crop top. ")

STYLE = (
    "Everything except the girl is drawn as an M.C. Escher wood engraving at night, exactly like the reference frames: "
    "black ink with fine white engraved lines in the shadows, every light a crisp white engraved starburst, warm "
    "off-white paper in the lit areas, dense precise parallel hatching and cross-hatching that follows form, high "
    "contrast, no gray wash, no airbrush, no color anywhere except the girl. Full bleed, edge to edge, no border, no "
    "frame, 16:9. No text, no letters, no numbers, no logos, no signature, no watermark.")

P2 = (
    "Image 1 is a frame from this film: the point of view of a man standing outside the OPEN driver's window of her white "
    "LEFT-HAND-DRIVE Acura sedan at night, looking in at her. The car's nose points to the LEFT of the frame; the steering "
    "wheel and dashboard are at the left, the empty passenger seat and the dark passenger-side windows are behind her. "
    "Draw the next shot of the film from exactly the same side of the car, the same camera direction and the same car "
    "interior, but moved in closer: a medium close-up of the girl, head and shoulders down to mid-chest, centred. She "
    "sits in the DRIVER'S seat. The steering wheel is DIRECTLY in front of her body, at the left of the frame: its rim "
    "rises at the lower left, just in front of her chest, and both her hands grip the rim at ten and two (her hands and "
    "the rim are at the bottom left). Nothing is between her and the wheel. Her own seat's headrest is right behind her "
    "head. She has just turned her head to look straight at us, frozen in sudden shock, with the expression of image 2: "
    "eyes wide, small pupils, brows lifted, lips parted, a bead of sweat at her temple. Behind her, to the right: the "
    "empty passenger seat and the dark passenger window with a few small starburst lakefront lamps. The top edge of the "
    "frame is the car's dark roof lining and the top of the door opening; the bottom edge is the driver's door window "
    "sill. Framing for a wide 2.39 crop: the pencil erasers sit well inside the picture, at about one fifth of the "
    "height from the top, and her headphones and both hands on the wheel are above the bottom sixth. " + JADE + STYLE)

P1 = (
    "Image 1 is a frame from this film. Keep the agent EXACTLY as in image 1: the same man, same black suit, white shirt, "
    "thin black tie, opaque black sunglasses, earpiece wire, lapel pin, the same pose (his right hand slipping inside his "
    "jacket toward the holster, his left hand holding the lapel open), the same size and the same place at the right of "
    "the frame, waist up, facing us. Redraw everything BEHIND him: he stands right beside the driver's door of the white "
    "Acura sedan of image 2, with his back to it. The car is parked behind him and fills the left half of the frame, "
    "seen from its DRIVER'S side (the car's left side), almost side-on: its NOSE points to the LEFT edge of the frame "
    "(front wheel, headlight and wing mirror at the left), its rear is hidden behind the agent. Same car as image 2: "
    "white, late-1990s Acura TL, smooth rounded body, chrome door handles. The driver's window is wide open, just to the "
    "left of the agent's shoulder, at the left-centre of the frame, and through it we clearly see the anime girl of "
    "image 2 sitting in the driver's seat, both hands on the steering wheel in front of her, her head turned toward the "
    "agent's back, wary: her face, her bun with the two crossed pencils, her orange headphones and white jacket in full "
    "colour, framed by the window. The lake is behind the camera, not visible. Beyond the car: the empty lanes of Lake "
    "Shore Drive, tall lamp posts with crisp starburst lights, a dark strip of park trees, and the Chicago skyline far "
    "away under a dark cloudy sky. " + JADE + STYLE)

SHOTS = {
    "P2": dict(prompt=P2, refs=[D7, P2_OLD, BUN], tag="v9_1a_kf_{}"),
    "P1": dict(prompt=P1, refs=[P1_OLD, D7, BUN], tag="v9_9_kf_{}"),
}
EXTRA = {}   # (shot, variant) -> extra prompt text, filled in after looking at earlier variants

# round 2. P2 a is right (driver's seat, wheel in front of her, nose left, two pencils pink + blue) but her face is only
# worried, and beyond the passenger windows there is water: the lake belongs on the driver's side (D6/D8). Edit only those.
P2_EDIT = (
    "Edit image 1. Keep everything else exactly the same: the camera, the framing, the car and its interior, the girl's "
    "pose, both hands, her hair, bun and the two crossed pencils with their pink and pale-blue erasers, her headphones, "
    "jacket, roundel and dot, the steering wheel, the wing mirror, and every line of the engraving. Change only two "
    "things. (1) Her face: frozen in sudden shock like the girl in image 2: eyes opened very wide with small pupils, "
    "eyebrows raised high, mouth open in a small round gasp, a bead of sweat at her temple; same face, same anime "
    "drawing style, head in the same position and angle. (2) Beyond the car's far (passenger-side) windows: no water. "
    "Replace the water and its reflections with a dark engraved park lawn, black tree silhouettes and a few small "
    "starburst lamp posts on the land; the sky above stays black with stars. No text, no letters.")
SHOTS["P2"]["prompt_c"] = P2_EDIT
SHOTS["P2"]["refs_c"] = ["media/shots/P2/kf_v9a.png", P2_OLD]

if __name__ == "__main__":  # noqa: E305
    shot, v = sys.argv[1], sys.argv[2]
    s = SHOTS[shot]
    prompt = s.get("prompt_" + v, s["prompt"]) + EXTRA.get((shot, v), "")
    refs = s.get("refs_" + v, s["refs"])
    out = os.path.join(ROOT, f"media/shots/{shot}/kf_v9{v}.png")
    model = "google/nano-banana-pro"
    inp = inp_for(model, prompt, refs)
    if "--dry-run" in sys.argv:
        print(json.dumps({k: (x if k != "image_input" else len(x)) for k, x in inp.items()})[:300])
        paths = cf.generate(model, inp, out, tag=s["tag"].format(v), dry_run=True)
        print(paths); sys.exit()
    paths = cf.generate(model, inp, out, tag=s["tag"].format(v))
    trim_margins(paths[0])
    with open(os.path.join(ROOT, f"media/shots/{shot}/kf_log_v9.jsonl"), "a") as f:
        f.write(json.dumps(dict(variant=v, model=model, refs=refs, prompt=prompt, out=paths[0])) + "\n")
    print(paths)
