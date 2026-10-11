#!/usr/bin/env python3
"""Section C keyframe jobs. Usage:
    $PY tools/sectionC/kf.py list
    $PY tools/sectionC/kf.py run JOB [JOB ...]      (job ids or prefixes, e.g. V2c runs every V2c clip variant)
Outputs media/shots/<CLIP>/kf_<variant>.png and media/shots/_C_sheets/<label>.jpg
Job id = <CLIP>_<variant>; variant letter: s = seedream-5-pro, n = nano-banana-pro, f = gpt-image-2.5-flare.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (AGENT_SHEET, AGENTS, CAR, DAY, JADE, JADE_SHEET, NIGHT, SEDANS, SHEETS, SHOTS, SIDE,  # noqa: E402
                    STYLE, STYLE_NOGIRL, run_jobs, sheet)

NBP = "google/nano-banana-pro"
SDR = "bytedance/seedream-5-pro"
FLARE = "openai/gpt-image-2.5-flare"

J = {}


def job(jid, model, prompt, refs=()):
    clip = jid.split("_")[0]
    J[jid] = dict(id=jid, model=model, prompt=prompt, refs=list(refs),
                  out=os.path.join(SHOTS, clip, f"kf_{jid[len(clip) + 1:]}.png"))


def car_night(jid, body, model=SDR):
    job(jid, model, NIGHT + body + " " + STYLE_NOGIRL)


def jade_night(jid, body, agents=False):
    job(jid, NBP, NIGHT + body + " " + JADE + (AGENTS if agents else "") + STYLE,
        [JADE_SHEET] + ([AGENT_SHEET] if agents else []))


def jade_day(jid, body, agents=False):
    job(jid, NBP, DAY + body + " " + JADE + (AGENTS if agents else "") + STYLE,
        [JADE_SHEET] + ([AGENT_SHEET] if agents else []))


# ------------------------------------------------------------------------------------------- V2a car chase
car_night("V2a1_s", SIDE + f"Lake Shore Drive at night. {CAR} drives extremely fast from left to right, seen exactly "
          "side-on in profile, large in the center-right of the frame (about a third of the frame width), headlight beams "
          "reaching forward to the right. Behind the road, the black water of Lake Michigan with engraved moonlit "
          "ripples and a low horizon. Entering from the left edge of the frame, three pursuing " + SEDANS + ". Horizontal "
          "engraved speed lines streak the road.")
car_night("V2a2_s", "Extreme close-up, exact side view, tracking alongside the front wheel of a speeding white sedan at "
          "night: a five-spoke alloy rim, the tire spinning so fast the spokes blur into engraved concentric circles, the "
          "road surface streaking past in long horizontal engraved speed lines, grit sparks flying as tiny white "
          "starbursts. The white fender above the wheel drawn as bare paper with fine contour lines, the wheel well black.")
jade_night("V2a3_n", "Inside a car at night, side profile view from the passenger seat: the anime girl driving, large in "
           "frame from the waist up, both hands gripping the steering wheel at ten and two, eyes focused ahead, "
           "determined; the rearview mirror at the top of the frame; a soft white glow from the dashboard lights her "
           "face and hands; through the driver's window behind her, the engraved night city streaks past with white "
           "starburst streetlights.")
car_night("V2a4_s", SIDE + "A wide multi-lane highway at night: a dense pack of eight " + SEDANS + ", racing left to right "
          "in staggered rows, filling the frame; two more black sedans merge in from an on-ramp curving down from the "
          "upper right. Engraved city skyline behind, horizontal speed lines.")
car_night("V2a5_s", SIDE + f"Lake Shore Drive at night: {CAR} in the far lane drives fast left to right, centered; in the "
          "near lane just behind it, one of the " + SEDANS + " swerves toward it at a sharp angle, its nose turned in to "
          "ram the white car's rear door, only inches away. Engraved concrete barrier and the black lake behind.")

# ------------------------------------------------------------------------------------------- V2b kaizo road
car_night("V2b1_s", SIDE + f"A night highway that misbehaves like a video-game level. {CAR} races left to right on the "
          "left half of the frame; just ahead of it, a whole slab of the road has broken free and tilted up like a "
          "seesaw platform, pivoting on a steel hinge in the middle, its far end lifted high into the air, its riveted "
          "steel underside engraved in detail. Two pursuing " + SEDANS + " behind at the left edge.")
car_night("V2b2_s", SIDE + f"A night highway. A black government sedan flips upside-down in mid-air high above the road, "
          f"arcing over {CAR} which drives fast left to right underneath it; the black car's roof light bar flares as a "
          "white starburst, shards of debris spin off it; at the far left, a tilted slab of road like a seesaw ramp that "
          "launched it.")
jade_night("V2b3_n", "Inside the car at night, a low angle from the passenger footwell looking up past the girl and "
           "through the windshield: an upside-down black sedan is passing overhead just inches above the glass, its "
           "underside engraved in detail, its roof light bar a white starburst. The anime girl at the wheel fills the "
           "left half of the frame, ducking low with her shoulders hunched, eyes wide looking up, both hands on the "
           "wheel.")
car_night("V2b4_s", SIDE + f"A night boulevard. {CAR} races left to right toward a tall cast-iron streetlamp just ahead "
          "whose base has snapped: the lamp post is toppling across the road at a 45-degree angle, its lamp a white "
          "engraved starburst, sparks spraying from the broken base.")
car_night("V2b5_s", f"Chase camera low behind {CAR}, seen from behind and slightly above at night on a highway: two huge "
          "engraved semi trucks in the lanes on either side of it, their long trailers converging toward each other "
          "ahead, the gap between them narrowing to barely the width of the car. Tail lights as white starbursts.")
car_night("V2b6_s", "Directly top-down view from high above a night highway, looking straight down: two long semi trucks "
          "side by side, their trailers angled toward each other, and squeezing through the narrow gap between them, a "
          "small white sedan seen from above (white roof, black windows), moving up the frame, sparks flying where its "
          "side mirrors scrape; far behind at the bottom of the frame, black sedans with white starburst roof strobes. "
          "Engraved lane markings and asphalt texture.")

# ------------------------------------------------------------------------------------------- V2c the bridge
car_night("V2c1_s", f"Chase camera behind {CAR} at night on a downtown Chicago street leading onto a steel bascule bridge "
          "over the Chicago River: the bridge ahead still flat, black-and-white striped warning gate arms lowering "
          "across the road, a large bridge warning bell on a post at the right, signal lamps as white starbursts; "
          "engraved riverside skyscrapers on both sides.")
car_night("V2c2_s", "Dramatic low angle at street level at night: a massive Chicago River bascule bridge leaf rising up "
          "into the black engraved sky like a tilting wall of steel, rivets, girders and the road surface tipping "
          "upward, huge counterweight machinery and the bridge tender's house at the side; at the bottom center of the "
          "frame, a small white sedan seen from behind racing straight toward the rising leaf, its headlight beams on "
          "the steel. Escher-like dizzying scale.")
job("V2c2_n", NBP, NIGHT + "Dramatic low angle at street level at night: a massive Chicago River bascule bridge leaf "
    "rising up into the black engraved sky like a tilting wall of steel, rivets, girders and the road surface tipping "
    "upward, huge counterweight machinery; at the bottom center of the frame, a small white sedan seen from behind "
    "racing straight toward the rising leaf, its headlight beams on the steel. Escher-like dizzying scale. " + STYLE_NOGIRL)
car_night("V2c3_s", SIDE + f"A night highway: {CAR} in the middle of the frame, sandwiched between two " + SEDANS + ": "
          "one in the far lane pressing against its far side, one in the near lane pressing against its near side and "
          "partly overlapping it in the foreground; sparks where the doors scrape.")
jade_night("V2c4_n", "Close-up inside the car's dark footwell at night: the girl's chunky white sneaker, with the hem of her "
           "navy wide cargo pants and a hanging orange strap, stamping the accelerator pedal flat to the floor; the "
           "engraved pedals and floor mat; a slice of white dashboard glow.")
jade_night("V2c5_n", "Over-the-shoulder shot from the back seat at night: in the left foreground, the girl's right "
           "shoulder and the back of her head with the loose bun and the yellow pencil, white jacket with orange band, "
           "her hands on the wheel; in sharp focus at the center of the frame, a round speedometer gauge glowing white "
           "with tick marks only (no numbers), its needle near the top of the dial; through the windshield ahead, a "
           "bascule bridge leaf rising steeply into the black sky, the road becoming a ramp.")
car_night("V2c6_s", "Point of view through the windshield of a speeding car at night: the road ahead becomes the steeply "
          "tilted leaf of a rising bascule bridge, a ramp climbing into the black sky, rivets and grating rushing "
          "toward us; at its top edge, a gap opens with the black river far below and the far leaf rising opposite; the "
          "white hood of the car at the bottom of the frame.")
car_night("V2c7_s", "High wide aerial view from behind and above at night: a small white sedan at the apex races toward "
          "a raised bascule bridge across the Chicago River, and behind it a vast V formation of thirty " + SEDANS +
          " fanning out across all lanes, their headlight beams converging on the white car; engraved skyscrapers on "
          "both banks of the river.")
job("V2c7_n", NBP, NIGHT + "High wide aerial view from behind and above at night: a small white sedan at the apex races "
    "toward a raised bascule bridge across the Chicago River, and behind it a vast V formation of thirty " + SEDANS +
    " fanning out across all lanes, their headlight beams converging on the white car; engraved skyscrapers on both "
    "banks of the river. " + STYLE_NOGIRL)
car_night("V2c8_s", SIDE + f"At the foot of a bascule bridge at night: {CAR} smashes left to right through a striped "
          "wooden gate arm; the arm splinters into flying engraved fragments across the hood; the bridge's steel "
          "girders and warning bell behind.")

# ------------------------------------------------------------------------------------------- V2d the jump
car_night("V2d1_s", SIDE + f"At night: {CAR} races up the steeply tilted leaf of a raised Chicago River bascule bridge: "
          "the leaf is a long riveted steel ramp angled up to the right at about 30 degrees, the car halfway up it, "
          "headlights blazing; at the upper right the ramp ends in open air above the black river, and the opposite "
          "leaf rises on the far right.")
jade_night("V2d2_n", "A low angle from the river below at night, looking up: a white 2001 Acura TL sedan is huge in the "
           "frame, suspended mid-air in a jump across the gap between two raised bascule bridge leaves, wheels hanging, "
           "seen from the side and slightly below, its white paint drawn as bare paper; through the open driver's "
           "window the anime girl grins wildly, clearly visible in full color, one hand on the wheel; behind, the "
           "black night sky with a white engraved moon and the dark steel leaves; at the bottom, black river water.")

# ------------------------------------------------------------------------------------------- V2e landing
car_night("V2e1_s", SIDE + f"Low to the road at night: {CAR} crashes down onto the road after a huge jump, front wheels "
          "hitting first, suspension compressed, nose dipped, a burst of white engraved starburst sparks spraying from "
          "under the chassis; the raised bridge leaf behind it on the left.")
jade_night("V2e2_n", "Inside the car at night, a front three-quarter view from the passenger side: the anime girl "
           "laughing breathlessly with a huge relieved grin, both hands on the wheel, eyes glancing up at the rearview "
           "mirror; white dashboard glow on her face; the engraved night city through the windows.")
car_night("V2e3_s", SIDE + f"At night beyond a raised bascule bridge: {CAR} races away to the right on the road; behind it "
          "on the left, black government sedans with white starburst roof strobes are airborne off the raised bridge "
          "leaf, one landing hard with sparks, another still in mid-air.")

# ------------------------------------------------------------------------------------------- V2f mirror
car_night("V2f1_s", "High side-on view at night of a wide multi-lane road: a river of identical black government sedans "
          "packed into every lane bumper to bumper, stretching out of the frame to the left, every roof light bar a "
          "crisp white engraved starburst; the small white sedan at the far right leading them all. Engraved city "
          "behind.")
jade_night("V2f2_n", "Close-up of a car's rearview mirror at night, the mirror filling the center of the frame: reflected "
           "in its left part, the anime girl's eyes glancing into the mirror (in color, just her eyes and brows and a "
           "wisp of black hair); in the rest of the mirror, through the car's rear window, a swarm of black sedans "
           "with white engraved starburst strobes; around the mirror, the dark windshield with blurred white city "
           "lights.")

# ------------------------------------------------------------------------------------------- V2g kaizo trap
car_night("V2g1_s", "Point of view through the windshield of a speeding car at night: an elevated Chicago L train car "
          "(riveted steel, rows of windows) slams down nose-first onto the road directly in front, filling the whole "
          "frame, crushing the asphalt into flying slabs, a huge explosion of engraved debris and white starburst "
          "sparks, steel girders of the elevated track falling with it.")

# ------------------------------------------------------------------------------------------- V2h respawn (day)
jade_day("V2h1_n", SIDE + "On the wooden ties of the elevated L train tracks above Chicago's Loop: a small checkpoint "
         "flag on a thin pole (a plain triangular pennant, no markings) beside the anime girl, who is crouched low in a "
         "sprinter's ready stance facing right, as if she just materialized: a few glowing orange and pale-blue square "
         "motes swirl around her. Engraved rooftops, water towers and skyscrapers behind. She is large in frame.")

# ------------------------------------------------------------------------------------------- V2i race
jade_day("V2i1_n", SIDE + "The anime girl sprints extremely fast from left to right along the elevated L train tracks "
         "above Chicago's Loop, mid-stride, legs in a long powerful stride, arms pumping, large in the left-center of "
         "the frame; riveted steel girders, wooden ties, engraved brick buildings with water towers and distant "
         "skyscrapers behind. Leave open space ahead of her on the right.")
jade_day("V2i2_n", SIDE + "On the elevated L tracks: the anime girl in a feet-first baseball slide along the wooden ties, "
         "leaning far back, sliding left to right just under a heavy iron railway signal arm that swings down at chest "
         "height above her, missing her by inches; engraved girders and Loop buildings behind.")
jade_day("V2i3_n", "Close-up, side view at track level on the elevated L: the girl's chunky white sneakers and the hems "
         "of her navy wide cargo pants with hanging orange straps, mid-stride, pounding left to right over the wooden "
         "ties, splinters and dust flying, a steel rail in the foreground.")
jade_day("V2i4_n", SIDE + "The anime girl leaps off the end of the elevated L track structure into open air, body "
         "stretched horizontally in a dash, arms forward, heading right, a streak of orange and pale-blue light "
         "trailing behind her; below and ahead, the open lawns of Grant Park, engraved trees and the lakefront.")

# ------------------------------------------------------------------------------------------- V2j field (top-down)
jade_day("V2j1_n", "Directly top-down view from high above, looking straight down at Grant Park's lawn: engraved grass "
         "strokes cover the whole frame in flowing parallel hatching. The anime girl seen from directly above, small "
         "but clear in the center (white jacket, orange band, black hair bun with the yellow pencil visible from "
         "above), running diagonally; eight agents in black suits, seen from above, converge toward her from the edges "
         "of the frame, each with a long engraved shadow.", agents=True)
jade_day("V2j2_n", "Directly top-down view from above, closer, looking straight down at engraved grass: the anime girl "
         "in the center cuts sharply sideways in a low lunge, and two agents in black suits dive at her from the left "
         "and the right, arms outstretched, about to collide head-on with each other where she just was.", agents=True)

# ------------------------------------------------------------------------------------------- V2k too fast
jade_day("V2k1_n", "A low ground-level camera just behind the anime girl's right shoulder as she runs across an engraved "
         "grass field: her back and shoulder (white jacket with the pale-blue circle on the back, orange band) large in "
         "the left foreground, her head turned back over her shoulder so her three-quarter profile is visible; behind "
         "her in the field, five agents in black suits run after her at mid-distance; the engraved Chicago skyline far "
         "behind.", agents=True)
jade_day("V2k2_n", SIDE + "At ground level in a grass field: the anime girl sprints left to right, large in the frame; "
         "behind her on the left, a staggered line of agents in black suits running after her, the closest only a few "
         "strides behind; engraved Chicago skyline behind.", agents=True)
jade_day("V2k3_n", SIDE + "A close tracking shot in a grass field: the anime girl sprints left to right, large in frame, "
         "her head snapping toward the far side in shock; running neck and neck with her on her far side, an agent in "
         "a black suit and black sunglasses keeps pace effortlessly, blank-faced.", agents=True)

# ------------------------------------------------------------------------------------------- V2l / V2m / V2n
jade_day("V2l1_n", "Directly top-down high view of an engraved grass field: the anime girl standing small in the center, "
         "looking around, encircled by a perfect ring of twelve agents in black suits seen from above, all facing "
         "inward, evenly spaced, long shadows.", agents=True)
jade_day("V2l2_n", "Low angle, shallow focus in a grass field: an agent in a black suit and black sunglasses at the "
         "center of the frame draws a plain black pistol from inside his jacket, holding it low at his waist, pointed "
         "at body height; in the left foreground, out of focus, the white-and-orange shoulder of the anime girl; the "
         "ring of other agents blurred behind.", agents=True)
jade_day("V2m1_n", "A medium side view in a grass field: the anime girl recoils as she is hit in the side of the torso "
         "(never the head), her body bending away; from the impact point on her jacket a burst of glowing orange and "
         "pale-blue square motes explodes outward; at the left edge, a white engraved muzzle-flash starburst. Her face "
         "is turned away from the impact.")
jade_day("V2n1_n", "Extreme close-up: the girl's hand (white jacket cuff with an orange band at the wrist) slamming down "
         "on a big round convex arcade button set in an engraved arcade control panel; the button is blank and white; "
         "engraved motion lines around the hand.")


# ------------------------------------------------------------------------------------------- round 2 fixes
DRIVER_WIN = ("Seen from OUTSIDE the car through the open driver's window, the camera tracking alongside the car at "
              "night: the car drives from left to right, so we see the girl's LEFT side in profile as she faces right "
              "toward the windshield, large in frame from the waist up, her hands on the steering wheel in front of "
              "her; the window frame and the white door of the car around her; beyond her, through the passenger "
              "window, the engraved night city streaking past with white starburst streetlights. ")
jade_night("V2a3_n2", DRIVER_WIN + "She drives with total focus, eyes on the road ahead, jaw set.")
jade_night("V2e2_n2", DRIVER_WIN + "She laughs breathlessly with a huge relieved grin, eyes glancing up toward the "
           "rearview mirror.")
jade_night("V2c5_n2", "Over-the-shoulder shot from the back seat at night, behind her LEFT shoulder: in the left "
           "foreground, the back of her head with the loose bun and the yellow pencil, her left shoulder in the white "
           "jacket with the orange band, the orange headphones around her neck; her hands on the wheel; in sharp "
           "focus right of her head, a round speedometer gauge glowing white with tick marks only (no numbers), its "
           "needle near the top of the dial; through the windshield ahead, a bascule bridge leaf rising steeply into "
           "the black sky, the road becoming a ramp.")
job("V2c7_n2", NBP, NIGHT + "High wide aerial view from high above and BEHIND the chase at night, looking forward along "
    "a wide avenue toward a raised Chicago River bascule bridge in the distance. Every car faces AWAY from the camera, "
    "driving toward the bridge: we see their rear ends and small tail lights, their headlight beams projecting forward "
    "away from us. A small white sedan at the very front leads the chase toward the rising bridge, and behind it a vast "
    "V formation of thirty " + SEDANS + " fans out across all lanes. Engraved skyscrapers on both sides. " + STYLE_NOGIRL)
D2 = ("A dramatic low angle looking UP from the river surface at night: the white 2001 Acura TL sedan flies HIGH in the "
      "air, airborne in a jump across the open gap between two raised bascule bridge leaves, nothing under its wheels "
      "but empty air and the black river far below; we see it from the side and below, filling the upper middle of "
      "the frame, wheels hanging, its white paint drawn as bare paper. Through the open driver's window the anime "
      "girl's head and shoulders lean out slightly, grinning wildly, clearly visible in full color. Behind, the black "
      "night sky with a white engraved moon; the two raised steel leaves frame the car left and right. ")
jade_night("V2d2_n2", D2)
job("V2d2_f", FLARE, NIGHT + D2 + JADE + STYLE, [JADE_SHEET])
jade_night("V2f2_n2", "Match the composition of the attached car-interior frame exactly: the girl on the left third in "
           "the passenger-side view, the large side mirror on the right two thirds. But now the mirror is full of a "
           "river of black government sedans packed bumper to bumper behind her car, every roof light bar a crisp "
           "white engraved starburst, flashing. She glances at the mirror out of the corner of her eye.")
J["V2f2_n2"]["refs"] = [JADE_SHEET, "media/shots/D3/kf_nbp1.png"]
jade_day("V2i1_n2", SIDE + "The anime girl sprints extremely fast from left to right along the elevated L train tracks "
         "above Chicago's Loop, mid-stride, legs in a long powerful stride, arms pumping, large in the left-center of "
         "the frame; riveted steel girders, wooden ties, engraved brick buildings with water towers and distant "
         "skyscrapers behind. Leave open space ahead of her on the right.")
jade_day("V2i2_n2", SIDE + "On the elevated L tracks: the anime girl slides feet-first along the wooden ties at speed, "
         "body leaning far back almost flat, one arm trailing, moving left to right; a heavy iron railway signal arm is "
         "swinging down across the track just above her chest, missing her by inches; engraved girders and Loop "
         "buildings behind.")
jade_day("V2i3_n2", "Extreme close-up at rail level, exact side view: ONLY the girl's feet and lower legs fill the frame, "
         "chunky white sneakers and the hems of her navy wide cargo pants with hanging orange straps, mid-stride, "
         "pounding left to right over the wooden ties of the elevated tracks, splinters and dust flying, a steel rail "
         "running across the foreground. No upper body in frame.")
TOPDOWN = ("Orthographic view looking STRAIGHT DOWN from directly overhead, like a top-down video game map: the "
           "camera points vertically at the ground, no horizon, no sky, people seen only from above (tops of heads, "
           "shoulders), with short shadows. ")
jade_day("V2j1_n2", TOPDOWN + "Grant Park's lawn fills the whole frame, engraved grass strokes in flowing parallel "
         "hatching. The anime girl, seen from directly above, small but clear in the center (white jacket with the "
         "pale-blue circle on her back and orange bands, black hair bun with the yellow pencil), running diagonally "
         "toward the upper right; eight agents in black suits, seen from directly above, run in from the edges of the "
         "frame converging on her.", agents=True)
jade_day("V2j2_n2", TOPDOWN + "Closer, engraved grass fills the frame. The anime girl, seen from directly above in the "
         "center, cuts sharply to one side in a low lunge, and two agents in black suits, seen from directly above, "
         "dive at her from the left and the right, arms outstretched, about to collide head-on where she just was.",
         agents=True)

car_night("V2b5_s2", f"Chase camera low and close BEHIND {CAR} at night on a highway: we see the white car's REAR (trunk, "
          "tail lights as small white starbursts) in the lower center, driving away from us; on either side ahead of it, "
          "the backs of two huge engraved semi-truck trailers in the adjacent lanes, angled inward and converging, the "
          "gap between them narrowing to barely the width of the car.")
car_night("V2c2_s2", "Dramatic low angle at street level at night, behind a speeding white sedan: we see the white car's "
          "REAR (trunk, tail lights) small at the bottom center of the frame, driving AWAY from us toward a massive "
          "Chicago River bascule bridge whose leaf is rising up into the black engraved sky ahead like a tilting wall of "
          "steel, rivets and girders, the road surface tipping upward, huge counterweight machinery at the side. "
          "Escher-like dizzying scale.")
job("V2c2_n2", NBP, NIGHT + "Dramatic low angle at street level at night, behind a speeding white sedan: we see the white "
    "car's REAR (trunk, tail lights) small at the bottom center of the frame, driving AWAY from us toward a massive "
    "Chicago River bascule bridge whose leaf is rising up into the black engraved sky ahead like a tilting wall of "
    "steel, rivets and girders, the road surface tipping upward. Escher-like dizzying scale. " + STYLE_NOGIRL)
# ------------------------------------------------------------------------------------------- rough-cut v1 fixes
M3 = ("A medium side three-quarter view in an engraved grass field, the camera at chest height: the anime girl is hit "
      "in the side of her torso (never the head) and recoils, her body bending away from the impact, arms flung out. "
      "Her FACE IS CLEARLY DRAWN in three-quarter profile toward the camera: eyes squeezed tightly shut, brows pinched, "
      "mouth open in a gasp, a few strands of hair across her cheek, the loose bun with the yellow pencil intact. From "
      "the impact point on her jacket a burst of glowing orange and pale-blue square motes explodes outward. At the "
      "left edge, a white engraved muzzle-flash starburst far away. ")
jade_day("V2m1_n3", M3)
job("V2m1_f3", FLARE, DAY + M3 + JADE + STYLE, [JADE_SHEET])
LOOP_SKY = ("The skyline is unmistakably downtown CHICAGO: the Willis (Sears) Tower with its twin antennas, the tapered "
            "John Hancock Center with its X-braces, the two round corncob Marina City towers, Art Deco Loop towers; no "
            "Empire State Building, no New York water towers. ")
car_night("V2a4_s2", SIDE + "A wide multi-lane elevated highway at night: a dense pack of eight " + SEDANS + ", racing "
          "left to right in staggered rows, filling the lower two thirds of the frame; two more black sedans merge in "
          "from an on-ramp curving down from the upper right. Horizontal speed lines. " + LOOP_SKY)
job("V2a4_n2", NBP, NIGHT + SIDE + "A wide multi-lane elevated highway at night: a dense pack of eight " + SEDANS +
    ", racing left to right in staggered rows, filling the lower two thirds of the frame; two more black sedans merge "
    "in from an on-ramp at the upper right. Horizontal speed lines. " + LOOP_SKY + STYLE_NOGIRL)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "list":
        for k, j in J.items():
            print(k, j["model"], j["refs"])
    elif cmd == "run":
        sel = [k for k in J if any(k == a or k.startswith(a) for a in sys.argv[2:])]
        print("running", sel)
        res = run_jobs([J[k] for k in sel])
        label = "_".join(sys.argv[2:])[:60]
        out = sheet([(res[k], k) for k in sel], os.path.join(SHEETS, f"kf_{label}.jpg"), f"Section C keyframes {label}")
        print("sheet", out)
        for k in sel:
            print(k, res[k])
