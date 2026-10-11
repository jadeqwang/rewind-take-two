#!/usr/bin/env python3
"""Section A keyframes for the v3 revision pass (stream V1A: C1, C4, D2, D3, D4, D5). Usage:
    $PY tools/sectionA/kf_v3.py list | show JOB | run JOB [JOB ...]
Edits keep the v2 keyframe as image 1 and change only what Jade's note asks for.
Outputs media/shots/<SHOT>/kf_v3_<variant>.png (v2 keyframes are never overwritten). Tags: revA_v1a_<job>.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import AGENT_SHEET, AGENTS, CAR, JADE_SHEET, ROOT, SHOTS, STYLE_NIGHT, STYLE_NOGIRL, run_jobs, sheet  # noqa

NBP = "google/nano-banana-pro"

# v3 canon (docs/revisions/A_streams.md): two pencils, crossed in an X through the bun
PENCILS = ("Her hair bun now holds exactly TWO classic yellow hexagonal wooden pencils with silver metal ferrules, "
           "pushed through the bun so they cross each other in an X at the centre of the bun, like two crossed hair "
           "sticks. Each pencil is one perfectly straight unbroken line: its eraser end sticks out above the bun and its "
           "sharpened point comes out of the opposite side below the bun, exactly in line with the eraser end. One "
           "pencil has a pink eraser and a dark graphite point; the other has a pale-blue eraser and a point whose core "
           "is a tiny multicolour swirl. There are no other pencils or pencil pieces anywhere else in her hair or on "
           "her head. ")
KEEP = ("Edit the attached image (image 1). Keep everything not mentioned below pixel-for-pixel identical: the same "
        "composition, framing, drawing style, engraved black-and-white hatching, the same anime girl in colour with the "
        "same face, pose and outfit. Full bleed 16:9, no border, no margin. No text, no letters, no watermark. ")

J = {}


def uref(path):
    """common.ref() caches by basename, so D2/kf_sdr1.jpg and D5/kf_sdr1.jpg collide. Give every ref a unique name."""
    import shutil
    if "/media/design/" in "/" + path:
        return path
    dst = os.path.join(ROOT, "media/shots/_A_refs/v3src", path.replace("media/shots/", "").replace("/", "__"))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(os.path.join(ROOT, path), dst)
    return os.path.relpath(dst, ROOT)


def job(jid, prompt, refs, model=NBP):
    shot = jid.split("_")[0]
    refs = [uref(r) for r in refs]
    J[jid] = dict(id=jid, model=model, prompt=prompt, refs=refs, tag="revA_v1a_" + jid,
                  out=os.path.join(SHOTS, shot, f"kf_v3_{jid[len(shot) + 1:]}.png"))


# C1: no bullet, a muzzle flare instead; two pencils
job("C1_a", KEEP +
    "Changes: (1) REMOVE the brass bullet hanging in the air below the girl and REMOVE the concentric ripple rings and "
    "speed lines around it; fill that area with the plain pale engraved sky and distant buildings that are already "
    "behind it. (2) At the muzzle of the centre agent's pistol (bottom centre, the pistol pointing straight up) add a "
    "muzzle flare: a crisp white engraved starburst with sharp radiating black-and-white engraved rays, about the size "
    "of the agent's two hands, drawn in the same wood-engraving line work, pure black and white, no colour, no smoke "
    "cloud, no bullet. (3) " + PENCILS +
    "The small glowing orange and blue square motes in the air stay as they are.",
    ["media/shots/C1/kf_hero.jpg"])

# C4: two pencils
job("C4_a", KEEP + "Change only her hair bun: remove the single pencil and the stray pencil tip. " + PENCILS,
    ["media/shots/C4/kf_sdr1f.jpg"])

# D3: two pencils through the bun (v2: an eraser end above her head and a tip at her nape, on different lines)
job("D3_a", KEEP +
    "Change only the pencils in her hair: remove the pencil end with the pink eraser that sticks up above the top of "
    "her head, and remove the pencil tip that pokes out near the nape of her neck. Her bun sits at the back of her "
    "head (the left side of the frame). " + PENCILS +
    "Both pencils are short enough to sit entirely around the bun; nothing sticks up from the top of her head. The "
    "rearview mirror, the dark sedan in it, her face and her eyes stay exactly as they are.",
    ["media/shots/D3/kf_sdr3.jpg"])

# D2: the bulb billboard becomes the lyric surface: much bigger, both panels blank and lit
job("D2_a", KEEP +
    "Changes: (1) The rooftop billboard with the frame of round glowing light bulbs is now MUCH bigger and closer: it "
    "stands on the roof of the nearest building right outside the car window and fills most of the right two thirds of "
    "the window view, a tall steel-truss gantry carrying two very large rectangular panels stacked one above the "
    "other, each panel wide and completely BLANK, smooth, flat, evenly lit pale paper-white, each ringed by a single "
    "row of round glowing bulbs drawn as small engraved starbursts. No letters on the panels. The night skyline with "
    "its towers and water tanks is still visible to the left of and below the billboard. (2) " + PENCILS,
    ["media/shots/D2/kf_sdr1.jpg"])

# D4: restage. Both cars on the right shoulder pointing the same way, a plain black sedan behind the Acura.
D4 = ("Night on Lake Shore Drive in Chicago, the dark lake with engraved waves beyond the guardrail and the downtown "
      "Chicago skyline (Willis Tower with its two antennas, the John Hancock Center) small in the far distance. "
      "Camera: low, standing on the gravel shoulder a few metres in FRONT of the cars, looking back at them in a front "
      "three-quarter view. In the foreground, " + CAR + " has pulled over and stopped on the right-hand gravel "
      "shoulder of the road, beside the guardrail, facing toward the camera; we see its front and its driver's side. "
      "It is a left-hand-drive American car: through the windshield the anime girl sits in the DRIVER'S seat, which "
      "is the front seat on the right side of the picture, both hands on the steering wheel, looking up at her "
      "rearview mirror, uneasy. Nobody else is in the white car; the back seat is empty. Directly BEHIND the white "
      "car, on the same shoulder, in the same lane line, pointing the same way, a plain black four-door sedan (an "
      "ordinary mid-size unmarked government sedan, NOT a limousine, NOT stretched) has pulled up close and stopped; "
      "its two headlights blaze toward the camera as big engraved white starbursts with long radiating rays that "
      "wash past the white car. The empty road lanes run along the left of the cars. No red anywhere: any tail light "
      "or marker light is white or amber. The girl is EXACTLY the anime girl from the attached character turnaround "
      "sheet (white cropped jacket with an orange band, black mock-neck top, orange headphones round her neck, black "
      "hair in a bun), in full anime colour, small in the frame behind the windshield. ")
job("D4_a", D4 + STYLE_NIGHT +
    "Rendered as an M.C. Escher wood engraving: crisp black ink lines on warm off-white paper, dense precise parallel "
    "hatching, high contrast, no gray wash, no color anywhere except the girl. Match the engraving style of the second "
    "attached image. Full bleed, edge to edge, no border, no margin, 16:9. No text, no letters, no numbers, no "
    "licence-plate characters, no signature, no watermark.",
    [JADE_SHEET, "media/shots/D4/kf_nbp1.png"])

# D5 close-up: the shades fill the frame, lenses blank and black for the engine's woodcut lyric
D5 = ("Night. Extreme close-up of an agent's face, cropped tight from the eyebrows to the tip of the nose, straight on, "
      "perfectly symmetrical: his big opaque black sunglasses FILL the frame, the two wide rectangular lenses (classic "
      "wayfarer shape) each taking up more than a third of the picture width, side by side with the thin bridge "
      "between them in the exact centre. The lenses are flat, solid, pure black ink, completely empty and unbroken: no "
      "reflections, no highlights, no hatching, no shapes, no text inside them. Around them: the engraved skin of his "
      "brow, nose bridge and cheeks carved in fine parallel hatching, a little of his short hair at the top edge, and "
      "behind his head at the far left and right edges the blazing white engraved starbursts of car headlights "
      "back-lighting him, night-black sky. " + AGENTS)
job("D5_cu", D5 + STYLE_NIGHT + STYLE_NOGIRL, [AGENT_SHEET, "media/shots/D5/kf_sdr1.jpg"])

# ---- round 2
# D3: round 1 left one correct pencil through the bun plus two stray eraser ends on top of her head
job("D3_b", KEEP +
    "Changes, only in her hair: (1) REMOVE the two pencil ends that stick up out of the top of her head (the one with "
    "the pink eraser and the one with the pale-blue eraser, both in the upper middle of her hair): plain black hair "
    "there instead, nothing sticking up from the top of her head. (2) KEEP the long yellow pencil with the pink eraser "
    "that already passes through her bun on the left. (3) ADD exactly one second yellow hexagonal pencil through the "
    "same bun, crossing the first one in an X at the centre of the bun: its PALE-BLUE eraser end points up and to the "
    "right above the bun, its sharpened point (a tiny multicolour swirl core) comes out below the bun on the left, the "
    "whole pencil one straight line. Final count in the picture: exactly two pencils, two erasers, two points, both "
    "through the bun.",
    ["media/shots/D3/kf_v3_a.png"])

# D2: round 1 redrew the whole frame. Local edits only.
job("D2_b", KEEP +
    "This is a local edit: do NOT redraw the picture, do not change the girl, her pose, her clothes, the car window or "
    "the art style. Changes: (1) Make the rooftop billboard (the steel frame ringed with glowing bulbs carrying two "
    "blank pale panels, right of centre) about TWICE as big: it now stands on the nearest rooftop, its top near the "
    "top of the window and its two blank panels each about a third of the picture wide, still completely blank, flat "
    "and pale with a row of glowing bulbs round each. It covers the buildings that were behind it; the skyline towers "
    "on the left stay. (2) In her bun (top left), next to the existing yellow pencil, add a second yellow hexagonal "
    "pencil with a pale-blue eraser crossing the first in an X through the bun, each pencil one straight line.",
    ["media/shots/D2/kf_sdr1.jpg"])

# D4: round 1 mirrored (so the cars are on THEIR right shoulder, lake on their right = northbound), then the driver
# moved back to the car's left seat
job("D4_b", KEEP +
    "Changes: (1) In the white car, move the girl and the steering wheel to the OTHER front seat: she now sits "
    "behind the windshield on the RIGHT side of the picture (the car's left-hand driver's seat), both hands on the "
    "steering wheel, looking up at her mirror, same size, same colours, same anime drawing. The front seat on the left "
    "side of the picture is now empty (just the engraved headrest). (2) Remove the small signature scribble in the "
    "bottom corner. Nothing else changes: the black sedan stays directly behind the white car with its headlight "
    "starburst, the road stays on the right, the guardrail and the lake stay on the left.",
    ["media/shots/D4/kf_v3_a_flip.jpg"])

# ---- round 3: with the two-pencil reference sheet (media/design/jade_bun_two_pencils.png, image 2)
BUN = "media/design/jade_bun_two_pencils.png"
PENCILS_REF = ("Her bun holds exactly two crossed pencils exactly as in the bun reference sheet (image 2): two classic "
               "yellow hexagonal pencils with silver ferrules crossed in a narrow X through the bun, erasers up (one "
               "pink eraser, one pale-blue eraser), sharpened points coming out below the bun, each pencil one straight "
               "unbroken line from eraser to point. Exactly two pencils in the whole picture, no stray pencil ends. ")
job("D3_c", KEEP +
    "Change only the pencils in her hair. Remove the pencil end that sticks up above the top of her head and the "
    "pencil tip near the nape of her neck. Her bun is at the back of her head, at the left of the picture. " +
    PENCILS_REF + "Like the three-quarter head in the reference sheet (mirrored, because she faces right here): the two "
    "pencils cross AT the bun, both eraser ends rise from the bun at the upper left of her head, close together in a "
    "narrow V, and both points come out just below the bun at the left. Nothing sticks up from the top or the right "
    "side of her head. Her face, eyes, the rearview mirror and the dark sedan stay exactly as they are.",
    ["media/shots/D3/kf_sdr3.jpg", BUN])
job("D2_c", KEEP +
    "This is a local clean-up, do NOT redraw or restyle the picture, do not change the girl, her clothes or the car "
    "window. Changes: (1) The big rooftop billboard on the right (steel truss frame ringed with glowing round bulbs, "
    "two blank pale panels) was pasted in: redraw only its line work crisply in the same fine wood-engraving hatching "
    "as the buildings around it and blend its edges into the night sky and the rooftop it stands on, so there is no "
    "soft halo or seam. Keep its exact size, position and shape. Its two panels stay completely BLANK, flat, evenly "
    "pale paper-white, no letters. (2) Replace the single pencil in her bun (top left): " + PENCILS_REF,
    ["media/shots/D2/kf_v3_comp.jpg", BUN])
job("C1_b", KEEP +
    "Two tiny corrections on the girl only: (1) the round patch on her upper sleeve must read exactly '1420' on the "
    "first line and 'MHz' on the second line, in clean black sans-serif capitals on white inside a black ring. (2) The "
    "two crossed pencils in her bun stay where they are, but one eraser is pink and the other eraser is pale blue, as "
    "in the bun reference sheet (image 2). Nothing else changes: the muzzle flare starburst, the agents, the buildings "
    "and the motes stay identical, and there is no bullet.",
    ["media/shots/C1/kf_v3_a.png", BUN])

# ---- round 4
# D5 wide: the three men on the same lakefront shoulder as the restaged D4 (the v2 wide was a wooded road)
D5W = ("Night on Lake Shore Drive in Chicago, the same place as the attached location image (image 2): gravel shoulder, "
       "steel guardrail and the dark lake with engraved waves on the left, the road on the right, the small downtown "
       "Chicago skyline far behind. Three agents have stepped out of a plain black four-door sedan parked on the "
       "shoulder behind them and walk straight toward the camera in perfect symmetry, shoulder to shoulder in a shallow "
       "V, mid-stride. They are backlit by the sedan's two blazing headlights behind them (big white engraved "
       "starbursts with long rays), long hard shadows stretching toward us across the gravel. Low camera angle. The "
       "centre agent is closest and largest, framed from the knees up, his face in the upper middle of the picture; all "
       "three wear big opaque black wayfarer sunglasses, solid black lenses. No other people, no white car in the "
       "picture. ")
job("D5_w", D5W + AGENTS + STYLE_NIGHT + STYLE_NOGIRL, [AGENT_SHEET, "media/shots/D4/kf_v3_b.png"])
# (D6 belongs to stream V1B: tools/sectionA/kf_v3_id.py)

# C4 round 2: the camera sees her RIGHT side here; the 1420 MHz roundel belongs on her LEFT sleeve (canon), so the near
# sleeve shows only the orange band
job("C4_b", KEEP +
    "Change only her near sleeve: REMOVE the round black-and-white '1420 MHz' patch from the upper sleeve facing the "
    "camera. In its place the sleeve is plain white jacket fabric with its folds, and the single orange band continues "
    "unbroken around the sleeve. No patch, no badge, no text anywhere on that sleeve. Everything else stays identical: "
    "the two crossed pencils in her bun, her face, the headphones, the steering wheel, the dissertation and the blank "
    "sticky note.",
    ["media/shots/C4/kf_v3_a.jpg"])

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "list":
        for k, j in J.items():
            print(k, j["model"], os.path.relpath(j["out"], ROOT), len(j["prompt"]))
    elif cmd == "show":
        for k in sys.argv[2:]:
            print(k, J[k]["prompt"], J[k]["refs"])
    elif cmd == "run":
        sel = [k for k in J if k in sys.argv[2:]]
        print("running", sel)
        res = run_jobs([J[k] for k in sel], workers=6)
        os.makedirs(os.path.join(SHOTS, "_A_sheets"), exist_ok=True)
        out = os.path.join(SHOTS, "_A_sheets", f"v3_{sel[0]}_{len(sel)}.jpg")
        sheet([(res[k], k) for k in sel], out, title=" ".join(sel))
        print(out)
