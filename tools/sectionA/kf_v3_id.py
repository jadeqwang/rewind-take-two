#!/usr/bin/env python3
"""v3 revision, stream V1B: keyframes for the restaged ID shots D7 (0:35) and D8 (0:37).

Staging comes from the three.js blockout (tools/sectionA/blockout/, renders in media/shots/D7|D8/blockout_*.png):
D7 is the agent's point of view through her open driver's window (she holds the card's FRONT up to us), D8 is the
reverse angle from her seat (he reads the front, we see only the BACK). Shot / reverse shot on one card.

    $PY tools/sectionA/kf_v3_id.py LIST
    $PY tools/sectionA/kf_v3_id.py run D7_v3_1 D8_v3_1
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, SHOTS, STYLE_NIGHT, AGENTS, JADE_SHEET, AGENT_SHEET, run_jobs, sheet  # noqa: E402

NBP = "google/nano-banana-pro"

# canon v3 (docs/revisions/A_streams.md): two pencils crossed in the bun, mock-neck top, roundel on her LEFT sleeve
JADE_V3 = ("The girl is EXACTLY the anime girl from the attached character turnaround sheet: same face, same anime "
           "drawing style and clean cel shading, black hair with a centre part and long curtain bangs, worn up in a "
           "loose bun with TWO classic yellow wooden pencils crossed in an X through the bun (one with a pink eraser, "
           "one with a pale-blue eraser, erasers up, each pencil perfectly straight). Exactly her outfit: white cropped "
           "bomber jacket worn open, with one orange band across the chest and around both sleeves, a small pale-blue "
           "dot patch on her left chest, a round white roundel patch with a black ring on her LEFT upper sleeve reading "
           "'1420' over 'MHz' on two lines, a black mock-neck crop top, navy-blue cargo pants, orange over-ear "
           "headphones resting around her neck. ")

LOOK = ("Rendered as an M.C. Escher wood engraving / lithograph: crisp black ink lines on warm off-white paper, dense "
        "precise parallel hatching and cross-hatching that follows form, high contrast, no gray wash. Full bleed, edge to "
        "edge, no border, no margin, no paper edge, no frame, 16:9. No signature, no watermark, no caption, no subtitle. ")

CARD_FRONT = ("THE ID CARD is in FULL COLOR, large and sharp, its FRONT squarely toward the viewer and completely "
              "unobstructed: she pinches it by its bottom edge only, no finger crosses its face. It is a white plastic "
              "card with a pale sky-blue header band across the top, a small square portrait photo of the same anime "
              "girl on the left side, and on the right side four lines of personal information that are each completely "
              "covered by a solid black rectangular REDACTION BAR of a different length. There are no letters, no "
              "numbers and no readable writing on the card at all: only the blue band, the photo and the black bars. ")

D7 = ("Image 1 is a rough 3D staging blockout: follow its camera angle, her pose and where the card sits in the frame, "
      "but redraw everything properly in the style described below (do not copy its crude shapes). "
      "Night. The camera stands just outside the OPEN driver's window of a left-hand-drive sedan, looking in and "
      "slightly down at the driver: this is the point of view of someone standing at her window. The anime girl sits in "
      "the driver's seat with her upper body turned toward us. Her whole body is drawn, complete and natural: head, "
      "neck, both shoulders, both arms and her torso in the open jacket and black top down to her lap; nothing is cut "
      "off or missing. Her LEFT arm is raised toward the window and her left hand holds her ID card up to us, beside "
      "her shoulder, in the left-centre of the frame. Her right hand holds open the front of her jacket, where the card "
      "has just come out of the inside pocket. She looks up at us, wary and polite, lips closed. The steering wheel is "
      "at the left edge of the frame (left-hand drive), the empty passenger seat and the dark passenger window are "
      "behind her, the headrest behind her head. The top edge of the driver's door and its window sill run along the "
      "bottom of the frame. Keep her face, her hands and the card in the upper two thirds of the picture; the bottom "
      "fifth is only dark door and lap. " + CARD_FRONT + JADE_V3 + STYLE_NIGHT + LOOK +
      "The car interior and the night are black-and-white engraving; the only color in the picture is the girl and her "
      "ID card. No text anywhere except the '1420 MHz' roundel on her left sleeve.")

D8 = ("Image 1 is a rough 3D staging blockout: follow its camera angle and layout (agent's head top centre, the meter "
      "in his hand at the left, the small card in his other hand at the right), but redraw everything properly in the "
      "style described below (do not copy its crude shapes). "
      "Night. The camera is inside a car, in the driver's seat, looking out through the open driver's window at an "
      "agent who stands outside bending down to the window; chest-up, centre frame. The window frame and the slanting "
      "windshield pillar are at the right edge, the door's window sill along the bottom edge, all engraved. He holds a "
      "small plastic ID card up in front of his chest in one hand (right side of the frame) and studies its printed "
      "side through his opaque black sunglasses, head tilted slightly to one side, uncanny. THE CARD FACES HIM, so the "
      "viewer is behind it and sees ONLY THE BACK OF THE CARD: a plain blank white plastic card back with one thin pale "
      "sky-blue stripe along its top edge and one black magnetic stripe below it, nothing else. No photo, no portrait, "
      "no face, no print and no writing is visible on the card anywhere in the picture. The card is held by its lower "
      "edge so the whole back is visible. Faint glowing orange and sky-blue square motes shimmer and drift up off the "
      "card. In his other hand (left side of the frame) he holds up the residue meter at chest height, its dial facing "
      "us: a palm-sized brass device like a pocket stopwatch crossed with a Geiger counter, round case with a crown "
      "button, a gauge dial with tick marks but no numbers, and a single needle slammed hard against the far right end "
      "of the dial. Both hands, the card and the meter are in the upper two thirds of the picture. Behind him the dark "
      "lakefront night, a few streetlights as crisp engraved starbursts. " + AGENTS + STYLE_NIGHT + LOOK +
      "The agent, the meter, the car and the night are pure black-and-white engraving with no color. The only color in "
      "the whole picture is the card's pale-blue stripe and the small orange and sky-blue motes rising from it. No "
      "girl, no other people. No text, no letters, no numbers anywhere.")

# round 2. D7: the first keyframe was right but ran from pencil tips to card bottom over 83 % of the frame height, more
# than the 2.39 letterbox shows. kf_v3_2_canvas.png is that keyframe at 80 % on a grey canvas (made by hand: see
# media/shots/D7/NOTES.md); the model only continues the drawing into the margins.
D7_OUT = ("Image 1 is a finished drawing surrounded by flat blank grey margins. Complete the picture: extend the drawing "
          "seamlessly into all of the grey margins in exactly the same style and line work, so that no grey remains "
          "and no seam or frame line shows. Above: more of the car's roof and the black engraved night sky with a few "
          "crisp starburst lights. Below: more of the white car door under the window sill. Left: more of the white "
          "car's front fender and hood. Right: the rear door and rear window of the same car. Do NOT change, move, "
          "resize or redraw anything inside the existing drawing: the girl, her face, her two crossed pencils, her "
          "jacket, the ID card with its photo and black bars, the steering wheel and seats stay exactly as they are, "
          "at exactly the same size and position. Black-and-white wood engraving everywhere except the girl and her "
          "card. Full bleed, 16:9, no border, no text added.")
# D8: the first keyframe had the meter in a huge foreground hand from the corner (whose hand?) and in brass colour.
D8_EDIT = ("Edit image 1. Keep everything exactly the same (the agent, his face and sunglasses, his suit, the hand "
           "holding up the card, the plain white back of the card with its pale-blue stripe and black magnetic stripe, "
           "the orange and sky-blue motes rising from it, the car window frame, the night background) EXCEPT the meter "
           "and the hand that holds it. Remove the large foreground hand that enters from the lower right corner. "
           "Instead the agent's OWN other arm is bent at the elbow at his side and his own hand, drawn at the same size "
           "as his hand with the card, holds the residue meter up beside his chest on the right side of the frame, its "
           "dial toward us, clearly attached to his own sleeve and shoulder. The meter is drawn in black-and-white "
           "engraving like the rest (no gold, no brass color, no color at all): a palm-sized pocket-stopwatch-like "
           "round case with a crown button; its dial is a half-circle gauge arc with tick marks and no numbers, and "
           "its single needle is pinned hard against the stop at the far right end of the arc, at maximum. The lower "
           "right corner now shows only the engraved door and steering wheel rim. The only color in the picture stays "
           "the card's pale-blue stripe and the motes. No text, no letters, no numbers.")

# round 3 (rev-A follow-ups). D6: restaged so D6 -> D7 -> D8 are one place (blockout shot D6: from the passenger seat
# past her shoulder, same direction of view as D8, agents at HER driver's window), with the two-pencil bun.
BUN = "media/design/jade_bun_two_pencils.png"
D6 = ("Image 1 is a rough 3D staging blockout: follow its camera position and layout (the back of her head with the bun "
      "left of centre, the agent's face in the driver's window just beyond her, the steering wheel at the right), but "
      "redraw everything properly in the style described below (do not copy its crude shapes). "
      "Night. The camera is inside a left-hand-drive sedan, at the front passenger seat, looking across the cabin past "
      "the driver toward the driver's side window. The steering wheel is at the right of the frame, directly in front "
      "of the driver, with the dashboard and the slanting windshield pillar beyond it at the right edge; the dark edge "
      "of the passenger seat is in the left foreground. The anime girl sits in the driver's seat, seen from behind her "
      "right shoulder in back three-quarter view, left of centre: the back of her head with her hair bun and the TWO "
      "crossed pencils of image 2 clearly visible (one pink eraser, one pale-blue eraser, erasers up, each pencil "
      "straight), a sliver of her cheek and one eye as she looks up and away from us at the men outside, both her "
      "hands on the steering wheel, the orange band on her white jacket sleeve, her orange headphones round her neck. "
      "Right outside her OPEN driver's window, very close to her, stand two agents. The nearer agent bends down to the "
      "window so his blank face and opaque black sunglasses are framed in the window opening just beyond her, in the "
      "centre of the frame, and he holds a residue meter in through the window toward her at the height of her "
      "shoulder, its dial toward us: the same meter as in image 3, a palm-sized pocket-stopwatch-like round case with a "
      "crown button and one needle, drawn in black-and-white engraving. The second agent stands upright right beside "
      "him toward the front of the car, his head partly cut by the roof line. Both agents are EXACTLY the man of image "
      "3: plain black narrow suit, white shirt, thin black tie, opaque black sunglasses, short hair carved as tight "
      "parallel lines, coiled earpiece wire, tiny clock-face lapel pin. Behind them the dark lakefront night with a few "
      "streetlights as crisp engraved starbursts. Nobody holds a card or any paper. Keep the heads, the meter and her "
      "hands in the upper three quarters of the picture. " + JADE_V3 + STYLE_NIGHT + LOOK +
      "The car, the agents, the meter and the night are black-and-white engraving with no color; the only color in "
      "the picture is the girl. No text, no letters, no numbers anywhere.")
# P2: the v2 keyframe with only the bun changed to the two-pencil canon (the shot itself is left-hand drive: checked).
P2_EDIT = ("Edit image 1. Keep everything exactly the same: her face and shocked expression, her pose, her jacket, the "
           "headphones, the car interior, the steering wheel, the night outside, the engraving style and the framing. "
           "Change ONLY the pencil in her hair bun: there are now TWO classic yellow wooden pencils crossed in an X "
           "through the bun, exactly as in image 2: one with a pink eraser and one with a pale-blue eraser, both "
           "erasers up with silver ferrules, each pencil perfectly straight from eraser to point, the two sharpened "
           "points leaving the lower far side of the bun. No single pencil, no third pencil. Nothing else changes. No "
           "text added.")

# D6 round 2: the first keyframe gave the jacket extra orange bands at the cuffs and the hem (canon: one band only).
D6_EDIT = ("Edit image 1. Keep everything exactly the same (composition, the girl's pose and face, the two agents, the "
           "meter, the car interior, the night, the engraving style) EXCEPT two details of the girl. "
           "1) Her white cropped bomber jacket has exactly ONE orange band: a single horizontal orange stripe around "
           "the upper sleeve at the level of her chest. Remove the orange bands at her wrists and remove the orange "
           "band along the bottom hem of the jacket: the cuffs and the hem are plain white ribbed knit, like the rest "
           "of the jacket. Under the jacket she wears a black top. "
           "2) The two pencils crossed in her hair bun match image 2 exactly: two classic yellow wooden pencils forming "
           "a clear X through the bun, one with a pink eraser and one with a pale-blue eraser, erasers up, each pencil "
           "perfectly straight. Nothing else changes. No text added.")

JOBS = {
    "D7_v3_1": dict(model=NBP, prompt=D7, out="media/shots/D7/kf_v3_1.png",
                    refs=["media/shots/D7/blockout_D7c.png", JADE_SHEET, "media/shots/D7/ref_D6_interior.jpg"]),
    "D8_v3_1": dict(model=NBP, prompt=D8, out="media/shots/D8/kf_v3_1.png",
                    refs=["media/shots/D8/blockout_D8.png", AGENT_SHEET, "media/shots/D8/ref_D6_agents.jpg"]),
    "D7_v3_2": dict(model=NBP, prompt=D7_OUT, out="media/shots/D7/kf_v3_2.png", refs=["media/shots/D7/kf_v3_2_canvas.png"]),
    "D8_v3_2": dict(model=NBP, prompt=D8_EDIT, out="media/shots/D8/kf_v3_2.png", refs=["media/shots/D8/kf_v3_1.jpg"]),
    "D6_v3_1": dict(model=NBP, prompt=D6, out="media/shots/D6/kf_v3_1.png",
                    refs=["media/shots/D6/blockout_D6.png", BUN, "media/shots/D6/ref_D8_agent_meter.jpg"]),
    "D6_v3_2": dict(model=NBP, prompt=D6_EDIT, out="media/shots/D6/kf_v3_2.png", refs=["media/shots/D6/ref_D6_kf_v3_1.jpg", BUN]),
    "P2_v3_1": dict(model=NBP, prompt=P2_EDIT, out="media/shots/P2/kf_v3_1.png", refs=["media/shots/P2/ref_P2_v2_keyframe.jpg", BUN]),
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] == "LIST":
        for k, j in JOBS.items():
            print(k, j["out"], j["refs"])
        return
    os.chdir(ROOT)
    # the style reference for both: the v2 D6 keyframe (same car, same agents, same meter), under shot-unique names
    for dst in ("media/shots/D7/ref_D6_interior.jpg", "media/shots/D8/ref_D6_agents.jpg"):
        if not os.path.exists(dst):
            shutil.copy2("media/shots/D6/kf_sdr1.jpg", dst)
    ids = sys.argv[2:]
    jobs = [dict(id=k, tag="revA_v1b_" + k, **{**JOBS[k], "out": os.path.join(ROOT, JOBS[k]["out"])}) for k in ids]
    res = run_jobs(jobs)
    print(res)
    sheet([(p, k) for k, p in res.items()], os.path.join(SHOTS, "D7", "kf_v3_sheet_" + "_".join(ids) + ".jpg"), "V1B keyframes", cols=2)


if __name__ == "__main__":
    main()
