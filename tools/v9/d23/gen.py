#!/usr/bin/env python3
"""v9 round 3 (D2+D3 three.js scene): Jade's plate for the passenger-seat camera. Paid calls tagged v9_d23_<job>.

    PY=~/Documents/1-music-shipped/moongazing/.venv/bin/python
    $PY tools/v9/d23/gen.py plate_a plate_b [--dry-run]

Input 1 is the scene's own layout render at 23.16 (media/shots/D23/guide_s0.png: grey mannequin in the driver's seat,
the real 3D car, mirror and wheel). The model only has to draw HER; everything else in its picture is thrown away
(she is matted out and laid on a card in the 3D scene at exactly that framing).
"""
import json, os, sys
ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
import cf  # noqa: E402

D = "media/shots/D23"
NIGHT = ("Drawn as an M.C. Escher wood engraving at night: the car interior and all shadows are carved from dense black "
         "ink with fine white engraved lines, crisp black ink lines, dense precise parallel hatching that follows form, "
         "high contrast, no gray wash, no airbrush. Full bleed, edge to edge, no border, 16:9. ")
NOTEXT = "There is NO text, no letters, no numbers and no writing anywhere, no watermark. No red anywhere. "
PLATE = (
    "Image 1 is a rough 3D LAYOUT render of one frame of an animated film: the inside of a white left-hand-drive 2001 "
    "Acura TL sedan at night, seen from the PASSENGER seat, looking across at the driver. The grey mannequin in the "
    "driver's (left) seat is a placeholder for the girl. Redraw this exact frame, keeping the layout, camera, and the "
    "size and place of everything exactly as in image 1: the car's roof, A-pillar, the open driver's window, the "
    "white door mirror outside the window just right of her head, the dashboard and the steering wheel. "
    "Replace the mannequin with the girl of images 2 and 3, at exactly the mannequin's size and place, in the same "
    "pose: she is DRIVING, sitting in the driver's seat with BOTH hands on the steering wheel (right hand at about two "
    "o'clock on the rim, clearly gripping it, her right forearm reaching from her shoulder to the wheel; left hand on "
    "the far side of the rim). Her HEAD IS TURNED to her left, away from us, looking out of her open side window at "
    "the door mirror: we see the BACK and right side of her head, her right ear, the curve of her right cheek and jaw "
    "from behind, a few loose strands; her face is turned away (no eyes visible, or only the tip of her eyelashes). "
    "Her black hair is worn up in a loose bun high on the back of her head with exactly TWO classic yellow wooden "
    "pencils pushed through the bun and crossed in an X, erasers up: one PINK eraser, one PALE-BLUE eraser, each "
    "pencil one straight stick. Orange over-ear headphones rest around her neck. She wears her white cropped bomber "
    "jacket with an orange band around the sleeve, over a black mock-neck top; her right sleeve, facing us, has no "
    "patch. Same anime drawing style as images 2 and 3, clean cel shading, in FULL COLOR: the girl is the ONLY colour "
    "in the picture; the car and the night are black-and-white engraving. " + NIGHT + NOTEXT)

PLATE_C = PLATE.replace("each pencil one straight stick.", "each pencil one straight stick whose LOWER end is a sharpened wooden point with a graphite tip (no eraser at the lower ends).").replace(
    "in FULL COLOR:", "in FULL COLOR (her skin warm light peach with soft cel shading on the ear, cheek, neck and hands; the jacket white with cool grey-blue cel shadows; the orange band and headphones saturated orange):")
SEDAN = (
    "Image 1 is a frame from the same film showing the TVA agents' black sedan. Draw that SAME car alone: a plain boxy "
    "black 1990s American four-door sedan (like a Ford Crown Victoria), seen almost HEAD-ON from the front, from about "
    "the height of a car's door mirror, turned just a few degrees so that a thin sliver of the car's own right-hand "
    "side shows at the LEFT edge of the car. The whole car is in the picture, centred, filling most of the width, with "
    "its wheels on an invisible ground line. Its HEADLIGHTS ARE OFF (dark glass lenses, no glow, no beams), plain "
    "chrome grille with NO badge, a large BLANK pale rectangular front licence plate centred on the bumper with nothing "
    "on it. Night: a streetlight above catches a long white highlight across the hood and the top of the windshield. "
    "Behind the windshield, two TVA agents in black suits, white shirts, black ties and black sunglasses, the driver on "
    "the right of the picture (left-hand-drive car seen from the front), both staring ahead, faint behind the glass. "
    "The car stands on a PLAIN FLAT LIGHT GREY BACKGROUND, nothing else, no road, no shadow beyond a soft dark contact "
    "shadow under the tyres. Drawn in the film's black-and-white wood-engraving style: black ink, fine precise parallel "
    "hatching following the body's curves, crisp ink outlines, high contrast, no colour at all. " + NOTEXT)
R4 = (
    "Image 1 is a rough 3D LAYOUT render of one frame of an animated film: the inside of a white left-hand-drive 2001 "
    "Acura TL sedan at night, seen from the PASSENGER seat, looking LEFT across the driver at her side window. The grey "
    "mannequin in the driver's seat is a placeholder for the girl. Image 2 is a finished frame from the same film, seen "
    "from the same side: copy its drawing style exactly, both for the girl (fine, thin, clean anime line art with soft "
    "cel shading, delicate features, NOT thick comic outlines) and for the car interior (black-and-white wood engraving: "
    "fine parallel hatching and cross-hatching following every form, crisp thin ink lines). Image 3 is her character sheet. "
    "Redraw image 1 as a finished frame, keeping its camera, layout and the size and place of everything exactly: "
    "the driver's door on the left with its inner panel, armrest, door handle and window switch; the window frame and the "
    "B-pillar; the roof liner and grab handle at the top; the A-pillar running diagonally down to the right; the "
    "dashboard edge, instrument hood, vents and the top of the centre console on the right; the driver's seat with its "
    "stitched panels and headrest. "
    "IMPORTANT: every area that is FLAT BRIGHT GREEN in image 1 (the side window and the windshield) must stay exactly "
    "that flat bright green (#00FF00), perfectly uniform, with nothing drawn on it: no road, no sky, no lights, no mirror, "
    "no reflections, no glass texture. Only the girl's head, hair, pencils and shoulders may overlap the green, drawn "
    "solidly on top of it. "
    "Replace the mannequin with the girl, at exactly the mannequin's size and place: she is DRIVING, sitting in the "
    "driver's seat, BOTH hands on the steering wheel, which is right in front of her between her and the dashboard, "
    "seen from the side (three-quarter); her near (right) arm reaches forward to the rim. We see her face in PROFILE, "
    "facing right (forward), her head turned very slightly away from us, and her EYES glance to the far right, toward "
    "the front corner of her side window where her door mirror is: wary, mouth closed. Her black hair is worn up in a "
    "loose bun high on the back of her head with exactly TWO classic yellow wooden pencils pushed through the bun and "
    "crossed in an X: the upper ends are erasers, one PINK and one PALE-BLUE, the lower ends are sharpened points; each "
    "pencil one straight stick. Curtain bangs and a loose strand by her ear. Orange over-ear headphones rest around her "
    "neck. White cropped bomber jacket with an orange band around the sleeve, over a black mock-neck top; navy cargo "
    "trousers. Her right sleeve, facing us, has no patch. The girl is the ONLY colour in the picture. " + NIGHT + NOTEXT)
R4_EDIT = (
    "Edit image 1, a finished frame from an animated film (a girl driving at night, seen from the passenger seat). Keep "
    "EVERYTHING exactly as it is (the girl's face, hair, bun, pencils, headphones, jacket, trousers, the seat, the door, "
    "the dashboard, the drawing style and the flat bright green window areas), and change ONLY these things: "
    "1. LOWER the steering wheel and her two hands on it by about a third of the wheel's height, so the TOP of the wheel "
    "rim sits just BELOW the lower edge of the side window, in front of the dashboard; her arms follow her hands, still "
    "both gripping the rim. 2. REMOVE the door mirror drawn at the front lower corner of the side window (where the "
    "A-pillar meets the window's lower edge): that whole corner becomes the same perfectly flat bright green (#00FF00) as "
    "the rest of the window, with nothing drawn on it; the window's black rubber edge and the A-pillar stay. 3. The "
    "eraser on the upright pencil in her bun becomes PALE BLUE (the other eraser stays pink). " + NOTEXT)
FACE = ("Edit image 1, a close-up from an animated film: a girl in profile facing right, driving at night, the background "
        "flat bright green. Keep EVERYTHING exactly as it is, same drawing, same line weight, same colours, same framing, "
        "pixel for pixel: her hair, bangs, ear, cheek, nose, chin, the green background. Change ONLY: ")
R6 = {
    "r6_blink": FACE + "her EYE is CLOSED in a natural blink: the upper eyelid comes all the way down, drawn as one curved dark "
                "lash line with the lashes pointing down, no iris or white showing; the eyebrow stays where it is. " + NOTEXT,
    "r6_half": FACE + "her EYE is HALF CLOSED, mid-blink: the upper eyelid covers the top half of the iris, the lower half of "
               "the iris still visible, looking in the same direction (forward and slightly right); the eyebrow stays. " + NOTEXT,
    "r6_lip2": FACE + "her MOUTH stays CLOSED, but she presses her lips together a little harder in concentration: the lower "
               "lip draws in slightly so the line of the mouth becomes a touch shorter and tighter and the lower lip looks a "
               "little thinner. NO teeth, no open mouth, no grimace, no smile. The nose, chin and jaw outline do not move at "
               "all; the eye stays open exactly as it is. A very small change. " + NOTEXT,
    "r6_lip": FACE + "she presses her lips together in concentration, gently biting the lower lip: the lower lip is tucked "
              "slightly in under the upper teeth's edge, a small tight line at the mouth; nothing else on the face moves, "
              "the eye stays open exactly as it is. " + NOTEXT,
}
# round 7 (Jade: the mirror sits "unnaturally high"): the same passenger-seat camera, but the wheel at a real TL height
# (its top rim below the window sill), so the window's FRONT LOWER corner, where the TL's door mirror really is, is clear
R7 = R4.replace(
    "BOTH hands on the steering wheel, which is right in front of her between her and the dashboard, "
    "seen from the side (three-quarter); her near (right) arm reaches forward to the rim.",
    "BOTH hands on the steering wheel, which is right in front of her between her and the dashboard, "
    "seen from the side (three-quarter); her near (right) arm reaches forward and a little down to the rim. The wheel is "
    "LOW, exactly as in image 1: the TOP of the wheel rim is BELOW the lower edge of the side window (the door's window "
    "sill line), and her hands on it are below the sill too. The FRONT LOWER CORNER of the side window, where the A-pillar "
    "meets the window sill, is completely clear flat green: nothing in front of it, not the wheel, not her hands, and NO "
    "door mirror drawn there (it is added later).").replace(
    "her EYES glance to the far right, toward the front corner of her side window where her door mirror is",
    "her EYES glance to the far right and a little DOWN, toward the front LOWER corner of her side window where her door "
    "mirror is")
R7_PREV = R7 + (" Image 2 is in fact the previous version of this same frame: draw the girl and the interior just like image 2 (her "
    "face, hair, bun, pencils, headphones, jacket, the door, seat and dashboard), EXCEPT that the steering wheel and her "
    "hands are lower, as in image 1, so the front lower corner of the window is clear.")
R7_FIX = (
    "Image 1 is a rough PASTE-UP of a finished frame from an animated film (a girl driving at night, seen from the "
    "passenger seat): the steering wheel and her two hands were cut out and moved LOWER, which left seams, grey gaps and a "
    "broken join at her forearms. Image 2 is the frame before the change. Redraw image 1 as one clean finished frame in "
    "exactly the drawing style of image 2, keeping the camera, the layout and the place and size of everything exactly as "
    "in image 1, and keeping the girl, her face, hair, bun, pencils, headphones and jacket exactly as they are. "
    "The steering wheel stays exactly where it is in image 1, LOW: the top of its rim is BELOW the window sill. Repair "
    "everything round it: her forearms run naturally from her sleeves down to her hands, both hands gripping the rim "
    "(right hand at about two o'clock, left hand at about ten o'clock); the grey gaps become the dashboard, instrument "
    "hood, the foot of the A-pillar and the door panel, drawn in the same black-and-white wood engraving as the rest of "
    "the interior. The side window and the windshield stay perfectly flat bright green (#00FF00), including the window's "
    "FRONT LOWER CORNER where the A-pillar meets the sill: nothing drawn on the green, NO door mirror, no wheel, no hands "
    "over it. " + NOTEXT)
R7_CROP = (
    "Image 1 is a rough PASTE-UP, a detail of a finished frame from an animated film: a girl's hands on the steering wheel "
    "of a car at night, seen from the passenger seat, with the driver's side window (flat bright green) above the door "
    "sill on the left, the A-pillar and the dashboard with the instrument cluster on the right. The wheel and her hands "
    "were cut out and moved DOWN, leaving grey gaps and broken seams at her forearms. Image 2 is the same detail before the "
    "change. Redraw image 1 as a clean finished picture in exactly the drawing style of image 2 (black-and-white wood "
    "engraving for the car, clean anime line art and soft colour for her hands and white sleeves), with the SAME framing. "
    "The steering wheel must stay EXACTLY where it is in image 1, same size, same place, its top rim below the window "
    "sill: do not move it up. Fix only the seams: her forearms in the white sleeves with ribbed cuffs run smoothly down to "
    "her hands on the rim; the grey gaps become the dashboard, the instrument hood and the foot of the A-pillar behind "
    "the wheel, matching image 2. The green window area stays perfectly flat bright green (#00FF00) with nothing on it, "
    "and NO door mirror anywhere. " + NOTEXT)
# round 7, camera moved (the model would not draw the wheel below the sill from round 4's camera: r7_a-f): the
# passenger leans ~23 cm forward, so the wheel is LEFT of the window's front lower corner (guide_r7b.png)
R7B = R7.replace("looking LEFT across the driver at her side window.",
    "looking LEFT across the driver at her side window, from a little FORWARD of her (the passenger leans forward).").replace(
    "her head turned very slightly away from us,", "her head turned very slightly TOWARD us,").replace(
    "and NO door mirror drawn there (it is added later).",
    "and NO door mirror drawn there (it is added later). The steering wheel is to the LEFT of that corner, as in image 1.")
R7_DASH = (
    "Edit image 1, a finished frame from an animated film (a girl driving at night, seen from the passenger seat). Keep "
    "EVERYTHING exactly as it is, in place and in style: the girl (face, eyes, hair, bun, headphones, jacket, hands, "
    "trousers), the steering wheel exactly where it is, the door panel, the seat and headrest, the roof liner, grab "
    "handle and A-pillar, and the flat bright green windows. Change ONLY these two things: "
    "1. The DASHBOARD on the right is a plain box: redraw it as the real dashboard of a 2001 Acura TL, drawn exactly like "
    "the dashboard in image 2 (black-and-white wood engraving, fine hatching): the curved instrument hood with the round "
    "gauges behind the steering wheel, the dash top sweeping forward under the windshield, the centre stack with its "
    "vents and the radio at the right edge. It stays inside the area the box covers now, BELOW the green windshield and "
    "the green side window. The side window's FRONT LOWER CORNER, where the A-pillar meets the window sill, stays flat "
    "bright green (#00FF00) with nothing drawn on it, and NO door mirror anywhere. "
    "2. The two yellow pencils in her bun CROSS in an X: one with a PINK eraser pointing up and back, one with a "
    "PALE-BLUE eraser pointing up and forward, their lower ends sharpened points. " + NOTEXT)
R7_DASH2 = R7_DASH.replace("drawn exactly like the dashboard in image 2", "drawn in the style of the dashboard in image 2 (a different shot from the same film; take ONLY the dashboard's look from it, nothing else)")
R7_DASH3 = (
    "Edit image 1, a finished frame from an animated film (a girl driving at night, seen from the passenger seat). Keep "
    "EVERYTHING exactly as it is, pixel for pixel, in place and in style: the girl, the steering wheel (exactly where and "
    "as big as it is: LOW, its top below the window sill), the door panel, the seat, the roof liner, the A-pillar and the "
    "flat bright green windows. Change ONLY the DASHBOARD on the right, which is a plain featureless box: redraw it, in "
    "the same place and the same black-and-white wood-engraving style (fine parallel hatching, crisp ink lines), as the "
    "real dashboard of a 2001 Acura TL seen from the passenger seat: a curved, padded dash top sweeping forward under the "
    "windshield; the instrument hood, a soft curved cowl over the round gauges, behind and to the right of the steering "
    "wheel; a round side air vent at the door end; the centre stack at the right edge with two vents and the radio. The "
    "side window's FRONT LOWER CORNER, where the A-pillar meets the window sill, stays flat bright green (#00FF00) with "
    "nothing drawn on it, and there is NO door mirror anywhere. " + NOTEXT)
# round 7: the DRAWN housing (Jade: the CG cap "looks visually different from other mirrors of the acura model tl in this
# video"). Image 1 is the CG cap from the shot's own housing camera (housing_guide_r7.png); images 2 and 3 are the film's
# drawn TL mirrors (P1 0:38.5, D4 0:28.6). The card is keyed and registered back onto the guide (housing_r7.py).
HOUSING = (
    "Image 1 is a rough 3D render of ONE object from an animated film: the driver's door mirror of a white 2001 Acura TL "
    "sedan, seen from INSIDE the car, from the passenger seat, looking forward and left out through the side window. We "
    "see the mirror's GLASS side (the flat bright green area in the middle), the thin rim of the cap round the glass, and "
    "on the right the cap's rounded back seen from the car's side: a smooth rounded shell that bulges and curves forward "
    "toward the car. Images 2 and 3 are the SAME car's door mirror as the film draws it in two other shots, seen from "
    "outside. Redraw image 1 as a finished drawing of this mirror in exactly the style of images 2 and 3: a bold black ink "
    "outline, a fat, pillowy, rounded cap in warm off-white body colour, shaded with fine black engraved hatching and "
    "cross-hatching that follows its curves, a crisp highlight along its top. Round the glass only a THIN dark seam and a "
    "thin pale lip of the cap (not a thick picture frame). Keep the exact size, place, angle and silhouette of image 1: "
    "the same outline of the glass and the same outline of the cap. The GLASS area and the whole BACKGROUND stay perfectly "
    "flat bright green (#00FF00) with nothing drawn on them: no reflection, no sky, no road, no shadow, no window frame, "
    "no door, no arm. Only the mirror. " + NOTEXT)
HOUSING2 = HOUSING.replace("Keep the exact size, place, angle and silhouette of image 1",
    "The cap is soft and rounded everywhere, no hard box edges. Keep the exact size, place, angle and silhouette of image 1")
JOBS = {
    **{k.replace("r6_", "r7_"): dict(prompt=R6[k], refs=[f"{D}/r7_face_crop.png"], out=f"{D}/{k.replace('r6_', 'r7_')}.png", ar="1:1") for k in ("r6_half", "r6_blink")},
    "r7_house_c": dict(prompt=HOUSING2, refs=[f"{D}/housing_guide_r7b.png", f"{D}/ref_tl_mirror_p1.png", f"{D}/ref_tl_mirror_d4.png"], out=f"{D}/housing_r7_c.png"),
    "r7_house_d": dict(prompt=HOUSING2, refs=[f"{D}/housing_guide_r7b.png", f"{D}/ref_tl_mirror_p1.png", f"{D}/ref_tl_mirror_d4.png"], out=f"{D}/housing_r7_d.png"),
    "r7_house_a": dict(prompt=HOUSING, refs=[f"{D}/housing_guide_r7.png", f"{D}/ref_tl_mirror_p1.png", f"{D}/ref_tl_mirror_d4.png"], out=f"{D}/housing_r7_a.png"),
    "r7_house_b": dict(prompt=HOUSING, refs=[f"{D}/housing_guide_r7.png", f"{D}/ref_tl_mirror_p1.png", f"{D}/ref_tl_mirror_d4.png"], out=f"{D}/housing_r7_b.png"),
    "r7_m": dict(prompt=R7_DASH3, refs=[f"{D}/plate_r7_h.png"], out=f"{D}/plate_r7_m.png"),
    "r7_n": dict(prompt=R7_DASH3, refs=[f"{D}/plate_r7_h.png"], out=f"{D}/plate_r7_n.png"),
    "r7_k": dict(prompt=R7_DASH2, refs=[f"{D}/plate_r7_h.png", "media/shots/D6/kf_v3_2.jpg"], out=f"{D}/plate_r7_k.png"),
    "r7_l": dict(prompt=R7_DASH2, refs=[f"{D}/plate_r7_h.png", "media/shots/D6/kf_v3_2.jpg"], out=f"{D}/plate_r7_l.png"),
    "r7_i": dict(prompt=R7_DASH, refs=[f"{D}/plate_r7_h.png", f"{D}/plate_r4_e2.png"], out=f"{D}/plate_r7_i.png"),
    "r7_j": dict(prompt=R7_DASH, refs=[f"{D}/plate_r7_h.png", f"{D}/plate_r4_e2.png"], out=f"{D}/plate_r7_j.png"),
    "r7_g": dict(prompt=R7B, refs=[f"{D}/guide_r7b.png", "media/shots/D6/kf_v3_2.jpg", "inputs/jade_in_outfit.png"], out=f"{D}/plate_r7_g.png"),
    "r7_h": dict(prompt=R7B, refs=[f"{D}/guide_r7b.png", "media/shots/D6/kf_v3_2.jpg", "inputs/jade_in_outfit.png"], out=f"{D}/plate_r7_h.png"),
    "r7_e": dict(prompt=R7_CROP, refs=[f"{D}/pasteup_r7_crop.png", f"{D}/plate_r4_e2_crop.png"], out=f"{D}/plate_r7_e_crop.png"),
    "r7_f": dict(prompt=R7_CROP, refs=[f"{D}/pasteup_r7_crop.png", f"{D}/plate_r4_e2_crop.png"], out=f"{D}/plate_r7_f_crop.png"),
    "r7_c": dict(prompt=R7_FIX, refs=[f"{D}/pasteup_r7.png", f"{D}/plate_r4_e2.png", "inputs/jade_in_outfit.png"], out=f"{D}/plate_r7_c.png"),
    "r7_d": dict(prompt=R7_FIX, refs=[f"{D}/pasteup_r7.png", f"{D}/plate_r4_e2.png", "inputs/jade_in_outfit.png"], out=f"{D}/plate_r7_d.png"),
    "r7_a": dict(prompt=R7, refs=[f"{D}/guide_r7.png", "media/shots/D6/kf_v3_2.jpg", "inputs/jade_in_outfit.png"], out=f"{D}/plate_r7_a.png"),
    "r7_b": dict(prompt=R7_PREV, refs=[f"{D}/guide_r7.png", f"{D}/plate_r4_e2.png", "inputs/jade_in_outfit.png"], out=f"{D}/plate_r7_b.png"),
    **{k: dict(prompt=v, refs=[f"{D}/r6_face_crop.png"], out=f"{D}/{k}.png", ar="1:1") for k, v in R6.items()},
    "r4_e1": dict(prompt=R4_EDIT, refs=[f"{D}/plate_r4_a.png"], out=f"{D}/plate_r4_e1.png"),
    "r4_e2": dict(prompt=R4_EDIT, refs=[f"{D}/plate_r4_a.png"], out=f"{D}/plate_r4_e2.png"),
    "r4_a": dict(prompt=R4, refs=[f"{D}/guide_r4.png", "media/shots/D6/kf_v3_2.jpg", "inputs/jade_in_outfit.png"], out=f"{D}/plate_r4_a.png"),
    "r4_b": dict(prompt=R4, refs=[f"{D}/guide_r4.png", "media/shots/D6/kf_v3_2.jpg", "inputs/jade_in_outfit.png"], out=f"{D}/plate_r4_b.png"),
    "sedan_a": dict(prompt=SEDAN, refs=["media/shots/D4/kf_nbp1.png"], out=f"{D}/sedan_a.png"),
    "sedan_b": dict(prompt=SEDAN, refs=["media/shots/D3/kf_v9.png"], out=f"{D}/sedan_b.png"),
    "plate_c": dict(prompt=PLATE_C, refs=[f"{D}/guide_s0.png", "media/shots/D2/kf_v3_d.jpg", "inputs/jade_in_outfit.png"], out=f"{D}/plate_c.png"),
    "plate_d": dict(prompt=PLATE_C, refs=[f"{D}/guide_s0.png", "media/shots/D2/kf_v3_d.jpg", "inputs/jade_in_outfit.png"], out=f"{D}/plate_d.png"),
    "plate_a": dict(prompt=PLATE, refs=[f"{D}/guide_s0.png", "media/shots/D2/kf_v3_d.jpg", "inputs/jade_in_outfit.png"], out=f"{D}/plate_a.png"),
    "plate_b": dict(prompt=PLATE, refs=[f"{D}/guide_s0.png", "media/shots/D2/kf_v3_d.jpg", "media/shots/D3/kf_v3_c.jpg"], out=f"{D}/plate_b.png"),
}

if __name__ == "__main__":
    os.chdir(ROOT)
    dry = "--dry-run" in sys.argv
    for name in [a for a in sys.argv[1:] if not a.startswith("--")]:
        j = JOBS[name]
        inp = {"prompt": j["prompt"], "aspect_ratio": j.get("ar", "16:9"), "image_size": "2K" if not j.get("ar") else "1K", "image_input": ["file:" + r for r in j["refs"]]}
        if dry:
            print(name, "dry-run"); cf.generate("google/nano-banana-pro", inp, j["out"], tag=(f"v9_2_{name}" if name.startswith(("r6_", "r7_")) else f"v9_d23_{name}"), dry_run=True) if "dry_run" in cf.generate.__code__.co_varnames else print("(no dry_run kwarg)")
            continue
        paths = cf.generate("google/nano-banana-pro", inp, j["out"], tag=(f"v9_2_{name}" if name.startswith(("r6_", "r7_")) else f"v9_d23_{name}"))
        print(name, paths)
        with open(f"{D}/kf_log.jsonl", "a") as f:
            f.write(json.dumps({"job": name, "refs": j["refs"], "prompt": j["prompt"], "out": paths}) + "\n")
