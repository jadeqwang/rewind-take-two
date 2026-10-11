"""Section F, v3 revision pass (stream F of instance A, docs/revisions/A.md): keyframe edits to Jade's review notes.

    $PY tools/sectionF/v3.py JOB [JOB ...]        # jobs: see JOBS below; writes media/shots/<SHOT>/kf_v3_<name>.png
Notes: 3:21 curtain bangs / canon jacket / mock neck (F7c, also F6a, F8); 3:05 sword swing that becomes drawing, rainbow
core (F5a); 3:13 real Penrose staircase (F6b plate; the agents are drawn by tools/sectionF/modules/penrose_march.js);
desk objects standing among the buildings. Every call is tagged revA_f_<job>.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import NANO, ROOT, SHOTS, run_parallel, sheet, st, to169  # noqa: E402

HAIR = ("HAIR: her long black hair is down, with a centre part and CURTAIN BANGS: long face-framing strands that start at "
        "the centre part and sweep down and outward to both sides of her face, leaving the middle of her forehead open, "
        "exactly as in the character sheet. No blunt fringe, no straight-cut bangs across the forehead, no hime cut.")
TOP = ("TOP: a plain black MOCK-NECK crop top: a short stand-up collar that covers the base of her neck, as in the "
       "character sheet. Not a scoop neck, not a tank top, no bare collarbones.")
JACKET = ("JACKET: white cropped bomber jacket with one orange band running across the chest and around both sleeves; one "
          "pale-blue dot on her left chest; one round white patch with a black ring on her left upper sleeve that reads "
          "1420 on the first line and MHz on the second. No other patches, badges, flags, stripes, logos or cuffs in other "
          "colours. Orange headphones round her neck.")
PENCIL = ("PENCIL: she holds exactly one pencil: a classic yellow hexagonal pencil with a silver ferrule and a pale-blue "
          "eraser; its sharpened point shows a core that is a multicolour rainbow swirl instead of grey graphite.")
DESK = ("DESK OBJECTS: the city is a drawing on a desk, so a few giant desk objects stand among the towers at building "
        "scale, drawn in the same coloured pencil over black engraved hatching so they sit naturally in the skyline: a "
        "stack of thick hardbound books standing upright like a tower with windows of light between the pages, books "
        "leaning against a building, a ceramic mug full of pencils as a round tower, a glass ink bottle, a wooden ruler "
        "laid between two roofs like a skybridge, a block eraser as a low building. Their spines and labels are blank: "
        "no words on them.")
KEEP = ("Keep everything else exactly the same: identical composition, camera, framing and pose, the same hand-drawn "
        "coloured-pencil-over-engraving style, the same colours. Full bleed, no border, no margin, no text other than "
        "the sleeve patch.")
CANON = "media/style_tests/refs/jade_action_pencil.jpg"

JOBS = {
    # name: (shot, [input images], prompt)
    "F7c": ("F7c", ["media/shots/F7c/kf_2.jpg", CANON],
            "Edit the first image (the second image is the girl's character sheet). Change only the girl and the skyline "
            f"at the bottom. {HAIR} {TOP} {JACKET} {PENCIL} {DESK} Keep the gold-leaf Klimt sky, the Kandinsky circles and "
            f"triangles, the elevated train and her soaring pose with arms spread. {KEEP}"),
    "F5a_a": ("F5a", ["media/shots/F5a/kf_r2.jpg", CANON],
              "Edit the first image (the second image is the girl's character sheet). She still winds the giant pencil "
              "back over her shoulder in both hands like a two-handed sword about to swing, but now we see her face in "
              f"three-quarter view, determined. {HAIR} {TOP} {JACKET} The giant pencil is a classic yellow hexagonal "
              "pencil with a silver ferrule and a PALE-BLUE eraser (not pink); its big sharpened point clearly shows a "
              "core that is a bright multicolour rainbow swirl instead of grey graphite, and a few rainbow sparks come "
              f"off the point. There is no other pencil. {DESK} Keep the melting gold clock, the agents dripping from it "
              f"and the Willis Tower. {KEEP}"),
    "F6a": ("F6a", ["media/shots/F6a/kf_r2.jpg", CANON],
            f"Edit the first image (the second image is the girl's character sheet). {HAIR} {TOP} {JACKET} {PENCIL} The "
            "loop she is drawing round the clock is a thick coloured-pencil line whose core is a rainbow swirl with a "
            f"gold outer edge. {KEEP}"),
    "F8": ("F8", ["media/shots/F8/kf_r2.jpg", CANON],
           f"Edit the first image (the second image is the girl's character sheet). Change only the girl in the middle. "
           f"{HAIR} {TOP} {JACKET} {PENCIL} The jacket's cuffs and hem are white, the band is orange (no red). {KEEP}"),
}

# round 2: the first edits fixed hair and top but kept off-model jackets / patches
JACKET2 = ("Redraw her jacket so it matches the character sheet exactly: a plain WHITE cropped bomber with white ribbed "
           "cuffs, white hem and white collar; exactly one flat ORANGE band that runs horizontally across the chest and "
           "continues round both upper sleeves at the same height; exactly one small pale-blue circle on her left chest "
           "above the band; exactly one round WHITE patch with a thin black ring on her LEFT upper sleeve, lettered in "
           "black 1420 on the first line and MHz on the second. Nothing else on the jacket: no square patches, no flags, "
           "no pocket flaps, no orange or red cuffs, no orange hem, no armbands, no patch on her right sleeve. Her "
           "headphones are orange (not red). Her eyes are dark brown.")
JOBS.update({
    "F7c_r2": ("F7c", ["media/shots/F7c/kf_v3_F7c.jpg", CANON, "media/style_tests/refs/jade_canon_turnaround.jpg"],
               "Edit the first image (the second and third images are the girl's character sheets). Change only her "
               f"jacket and the pencil's eraser. {JACKET2} The pencil in her hand has a PALE-BLUE eraser (not pink) and "
               f"a point with a rainbow swirl core. Her hair, face, mock-neck top, trousers and pose stay as they are. {KEEP}"),
    "F5a_a_r2": ("F5a", ["media/shots/F5a/kf_v3_F5a_a.jpg", CANON],
                 "Edit the first image (the second image is the girl's character sheet). Change only the sleeve nearest "
                 "the camera: remove the round blue patch from it, so that sleeve is plain white with the orange band "
                 f"only (her patch is on the other arm, out of view). Everything else stays exactly as it is. {KEEP}"),
    "F6a_r2": ("F6a", ["media/shots/F6a/kf_r2.jpg", CANON],
               "Edit the first image (the second image is the girl's character sheet). Change the girl's hair, top and "
               f"pencil, and the line she draws. {HAIR} Seen from the side, the long front strand falls from the parting "
               f"past her cheek to her collarbone; her forehead is not covered by a cut fringe. {TOP} {PENCIL} The loop "
               "round the clock stays one thin perfect circle as in the first image, but drawn as a coloured-pencil line "
               "with a narrow rainbow core and a gold outer edge; no wide rainbow bands, no spiral. The buildings keep "
               f"their colours (no bright red brick). {KEEP}"),
    "F8_r2": ("F8", ["media/shots/F8/kf_v3_F8.png", CANON, "media/style_tests/refs/jade_canon_turnaround.jpg"],
              "Edit the first image (the second and third images are the girl's character sheets). Change only the girl "
              f"in the middle. {JACKET2} Her hair, face shape, mock-neck top, trousers, pencil and pose stay as they "
              f"are. The drawing fills the whole frame edge to edge: no paper margin. {KEEP}"),
})

# round 3: single-change edits (the model keeps a wrong detail when a prompt asks for many changes), the rainbow pencil prop
# reference (media/design/jade_bun_two_pencils.png, lower pencil of the callout), and F5a's last frame
PROP = "media/style_tests/refs/jade_bun_two_pencils.jpg"
JOBS.update({
    "F7c_r3": ("F7c", ["media/shots/F7c/kf_v3_F7c_r2.png", PROP],
               "Edit the first image. Change only the pencil in her hand: make it the LOWER of the two pencils drawn at "
               "the bottom of the second image: a plain yellow hexagonal barrel with no stripes, a silver ferrule, a "
               "PALE-BLUE eraser, and a sharpened point with a rainbow core. Also make her headphones orange. Nothing "
               f"else changes. {KEEP}"),
    "F8_r3": ("F8", ["media/shots/F8/kf_v3_F8_r2.jpg"],
              "Edit this image. Change only three things on the girl in the middle: (1) the ribbed cuffs at her wrists "
              "and the ribbed hem of her jacket become WHITE, the same white as the jacket; (2) her headphones become "
              "ORANGE, the same orange as the band on her jacket; (3) the round patch on her sleeve becomes WHITE with a "
              "thin black ring, lettered in black 1420 on the first line and MHz on the second. Nothing else changes. "
              f"{KEEP}"),
    "F5a_b": ("F5a", ["media/shots/F5a/kf_v3_F5a_a_r2.jpg", PROP],
              "Redraw the first image as the same scene two seconds later, same camera, same place, same drawing style, "
              "same girl and outfit, same giant pencil (it is the lower pencil of the second image: yellow hexagonal "
              "barrel, silver ferrule, pale-blue eraser, rainbow core). Her sword swing has turned into drawing. She has "
              "swung the giant pencil forward and down across her body and now guides it with both hands like an "
              "enormous pen, the eraser end up behind her shoulder at the upper left, the rainbow point touching the air "
              "in front of her at the middle right of the frame, where it is writing. The point has left ONE long flowing "
              "line hanging in the air: it starts as the fast arc of the slash, sweeping down from the top of the frame "
              "above her head, and where the point slowed it becomes a calm handwritten curl that loops once and runs "
              "toward the melting clock. The line is a thick coloured-pencil stroke with a rainbow core and soft pencil "
              "grain. Her body leans into the stroke and her long hair swings forward with the motion; her face has "
              "relaxed from fierce to calm concentration, like someone writing. Curtain bangs, centre part, black "
              "mock-neck crop top, white cropped jacket with one orange band, orange headphones round her neck. The "
              "melting gold clock, the tiny agents dripping from it, the Willis Tower, the giant books, the mug of "
              "pencils, the ink bottle and the ruler stay where they are. Full bleed, no border, no text."),
})

# F6b plate: the clock with an empty face, larger in frame; the Penrose staircase and the marching agents are drawn on
# the face by the engine (tools/sectionF/modules/penrose_march.js), so the stairs are geometrically exact and every
# agent walks the same way round
JOBS.update({
    "F6b_plate": ("F6b", ["media/shots/F6b/kf_clean.jpg"],
                  "Redraw this image with these changes, in exactly the same hand-drawn style (coloured pencil over black "
                  "engraved hatching on warm paper) and the same colours. (1) The clock face is now EMPTY: remove the "
                  "square staircase, every little figure and both clock hands. The face is clean cream paper with only "
                  "the short dash tick marks round its rim; no numerals. (2) The gold melting pocket watch is bigger and "
                  "centred: its round face is about 80 percent of the frame height, the crown and ring touch the top of "
                  "the frame, the soft melting drip of the case hangs at the bottom centre. (3) The skyline along the "
                  f"bottom and sides is lower and smaller so the clock dominates. {DESK} Keep a few Kandinsky circles and "
                  "triangles in the sky corners; no rainbow arcs, no checkerboards. No people anywhere. Full bleed, no "
                  "border, no margin, no text."),
})

# follow-ups from rev-A's review: F7b (her grin: no bangs, garbled roundel) and F5b (desk objects in the establishing
# skyline of the boss section)
JOBS.update({
    "F7b": ("F7b", ["media/shots/F7b/kf_clean.jpg", CANON, "media/style_tests/refs/jade_canon_turnaround.jpg"],
            "Edit the first image (the second and third images are the girl's character sheets). Change only the girl's "
            f"hair at the front, her top and her jacket details. {HAIR} The wind blows her long hair back, but the two "
            f"curtain-bang strands still frame her face from the centre part. {TOP} {JACKET2} She keeps her big grin, her "
            f"pose and the pencil. {KEEP}"),
    "F5b": ("F5b", ["media/shots/F5b/kf_clean.jpg"],
            "Edit this image. Change only the skyline: a few giant desk objects now stand among the skyscrapers at "
            "building scale, drawn in the same coloured pencil over black engraved hatching so they sit naturally in the "
            "city: a tall stack of thick hardbound books standing like a tower left of the clock, two big books leaning "
            "against a building, a ceramic mug full of pencils as a round tower in the middle distance, a glass ink "
            "bottle on a rooftop, a wooden ruler laid between two roofs like a skybridge. Their spines and labels are "
            "blank: no words. Keep the Willis Tower, the gold melting clock, the ink drips turning into falling agents, "
            f"the girl seen from behind on the water tower, the sky and every colour exactly as they are. {KEEP}"),
})

# F6b redraw: the engine's exact Penrose geometry (kf_v3_F6b_guide.png, tools/sectionF/penrose_guide.py) redrawn in the
# plate's hand; and an ink-engraved agent sprite sheet for the march
JOBS.update({
    "F6b_redraw": ("F6b", ["media/shots/F6b/kf_v3_F6b_guide.png", "media/shots/F6b/kf_v3_F6b_plate_crop_dered.png"],
                   "Redraw the first image in the hand-drawn style of the rest of the first image (and of the second image): "
                   "M.C. Escher wood engraving with coloured pencil laid into the hatching on warm paper. The flat staircase "
                   "on the clock face is a guide drawing: redraw EXACTLY that staircase, block for block, keeping every "
                   "block's position, size and outline, the number of steps (22 treads: a long flight of 7 along the front "
                   "right, a landing, 2 steps, a landing on the left, 2 steps, a landing at the back, a long flight of 7 "
                   "along the back right, a landing at the right end) and the way each step sits a little higher than "
                   "the one before it all the way round. Do not add, remove, merge or move any step; do not straighten "
                   "the loop into a flat ring. Render the steps as carved stone: pale cream treads, the gold-ochre and "
                   "ultramarine side faces shaded with dense engraved parallel hatching and coloured-pencil grain, crisp "
                   "black ink outlines, a soft hatched contact shadow on the clock face beneath the staircase. No figures "
                   "on the stairs. Everything outside the staircase stays exactly as it is in the first image: the gold "
                   "melting clock, its tick marks, the books, the mug of pencils, the buildings, the Kandinsky shapes. "
                   "Full bleed, no border, no text."),
    "F6b_agents": ("F6b", ["media/style_tests/refs/agent_turnaround_male.jpg", "media/style_tests/refs/agent_action.jpg"],
                   "A sprite sheet of one man, drawn exactly like the reference images: a TIME VARIANCE agent in a black "
                   "suit, white shirt, black tie and black sunglasses, short neat hair, a small earpiece coil, drawn as a "
                   "pure black-and-white M.C. Escher wood engraving with fine hatching, no colour at all. Eight full-body "
                   "figures in one horizontal row on a plain flat white background, evenly spaced, each the same height, "
                   "feet on the same baseline, not overlapping, nothing else in the picture: figures 1-4 walk toward the "
                   "viewer and to the LEFT, seen from the front three-quarter, in a four-frame walk cycle (contact, "
                   "passing, contact with the other leg, passing); figures 5-8 walk away from the viewer and to the LEFT, "
                   "seen from the back three-quarter, in the same four-frame walk cycle. Marching, arms swinging stiffly. "
                   "No text, no numbers, no ground line, no shadows."),
})


def main():
    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    jobs, outs = [], []
    for n in names:
        shot, ims, prompt = JOBS[n]
        out = os.path.join(SHOTS, shot, f"kf_v3_{n}.png")
        open(os.path.join(SHOTS, shot, "kf_prompt.txt"), "a").write(f"--- v3 {n}\n{prompt}\nrefs={ims}\n")
        jobs.append((NANO, prompt, ims, out, f"revA_f_kf_{n}"))
        outs.append((ims[0], out, n))
    res = run_parallel(jobs, workers=6)
    items = []
    for src, out, n in outs:
        got = res.get(out)                      # the model may return .jpg for a .png request
        if isinstance(got, str):
            to169(got)
            items += [(os.path.join(ROOT, src), f"{n} before"), (got, f"{n} v3")]
    if items:
        sheet(items, os.path.join(SHOTS, "F_v3_kf_sheet_" + "_".join(names) + ".jpg"), cols=2, cell_w=1100, title="F v3 keyframes")


if __name__ == "__main__":
    st.png_ref(os.path.join(ROOT, "media/design/jade_action_pencil.png"))
    st.png_ref(os.path.join(ROOT, "media/design/jade_bun_two_pencils.png"))
    main()
