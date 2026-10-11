#!/usr/bin/env python3
"""Section A keyframe jobs. Usage:
    $PY tools/sectionA/kf.py list
    $PY tools/sectionA/kf.py run JOB [JOB ...]      (JOB ids or prefixes, e.g. C1_ runs every C1 variant)
Outputs media/shots/<SHOT>/kf_<variant>.png and media/shots/_A_sheets/<first job>.jpg
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (AGENT_ACTION, AGENT_SHEET, AGENTS, CAR, JADE, JADE_ACTION, JADE_EXPR, JADE_SHEET, ROOT,  # noqa
                    SHOTS, STYLE, STYLE_NIGHT, STYLE_NOGIRL, run_jobs, sheet)

NBP = "google/nano-banana-pro"
FLARE = "openai/gpt-image-2.5-flare"
SDR = "bytedance/seedream-5-pro"

MOTES = ("Dozens of small glowing square motes of bright orange (#F08A24) and pale sky-blue (#8DB8E8) hang frozen in the "
         "air around her like suspended sparks, the only color in the world besides the girl. ")
BULLET = ("Time is frozen. A single small brass bullet hangs motionless in mid-air about an arm's length from her ribs "
          "(never near her head), pointed at her side, with an engraved wake behind it: a cone of concentric air-ripple "
          "rings and straight engraved speed lines trailing back down toward the street. ")
AGENTS_BELOW = ("Far below, on the street at the bottom of the canyon, five identical agents in black suits and black "
                "sunglasses stand in a tight arc, all aiming plain black pistols straight up at her, small and foreshortened "
                "but clearly readable as silhouettes. ")
LOOP = ("two tall ornate 1920s Chicago Loop skyscrapers (carved stone cornices, rows of tall windows, iron fire escapes) "
        "facing each other across a narrow street, with the steel girders of the elevated L train tracks crossing the "
        "street far below")

C1_BASE = JADE + BULLET + AGENTS_BELOW + MOTES

J = {}


def job(jid, model, prompt, refs):
    shot = jid.split("_")[0]
    J[jid] = dict(id=jid, model=model, prompt=prompt, refs=refs,
                  out=os.path.join(SHOTS, shot, f"kf_{jid[len(shot) + 1:]}.png"))


# --------------------------------------------------------------------------------------------------- C1 hero
C1_A = ("A breathtaking frozen moment, seen from a camera floating in the air at her height, angled steeply down into a "
        f"deep canyon between {LOOP}. The anime girl is large in the frame, slightly above center, frozen mid-wall-jump: "
        "her right sneaker has just kicked off the brick wall on the left, her body arcs in a long diagonal across the gap "
        "toward the building on the right, arms flung wide, jacket flaring, a few strands of black hair floating loose. "
        "Strong vertical three-point perspective falling away beneath her, dizzying depth, Escher-like vertigo. ")
C1_B = ("A breathtaking frozen moment, bullet-time. Side view at her height, the camera level with her in the middle "
        f"of the air between {LOOP}. The anime girl fills the center of the frame horizontally, frozen mid-leap from the "
        "wall on the left toward the wall on the right, body stretched out, one knee tucked, arms reaching, jacket and "
        "orange straps flying, a few hair strands floating. The street with the agents is visible far below through the "
        "gap at the bottom of the frame. Slight dutch angle. ")
C1_C = ("A breathtaking frozen moment, seen from below. Low angle looking up the canyon between two tall ornate 1920s "
        "Chicago Loop skyscrapers that converge toward a pale engraved sky, iron fire escapes zig-zagging up the walls. "
        "The anime girl is big in the upper half of the frame, frozen mid-wall-jump, kicking off the left wall, arms "
        "flung out, jacket flaring, her face turned down toward the bullet below her. In the near foreground at the "
        "bottom of the frame, the black-suited shoulders and raised arms of five agents seen from behind aim pistols up "
        "at her. ")
for v, comp in (("a", C1_A), ("b", C1_B), ("c", C1_C)):
    body = comp + (C1_BASE.replace(AGENTS_BELOW, "") if v == "c" else C1_BASE) + STYLE
    job(f"C1_nbp{v}", NBP, body, [JADE_SHEET, JADE_ACTION, AGENT_SHEET])
    job(f"C1_flr{v}", FLARE, body, [JADE_SHEET, AGENT_SHEET])

# C1 round 2: fix the bullet direction (it must rise FROM the agents TOWARD her ribs) and make her bigger
BULLET2 = ("Time is frozen. A single small brass bullet hangs motionless in mid-air about an arm's length below-side of "
           "her ribs, its pointed tip aimed at her ribs (never at her head); behind the bullet, trailing back DOWN toward "
           "the pistol that fired it, an engraved wake: concentric air-ripple rings and long straight speed lines. ")
C1_BASE2 = JADE + BULLET2 + MOTES
C1_C2 = ("A breathtaking frozen moment, seen from below. Low angle looking up a canyon between two tall ornate 1920s "
         "Chicago Loop skyscrapers whose iron fire escapes zig-zag up the walls and converge toward a pale engraved sky "
         "in strict symmetric perspective. The anime girl is LARGE, filling most of the upper half of the frame, frozen "
         "mid-wall-jump: the sole of one sneaker still touching the brick wall on the left where she kicked off (a few "
         "brick chips frozen in the air), her body arcing out across the gap, arms flung wide, jacket flaring, a few "
         "strands of hair floating, her eyes looking down at the bullet. In the near foreground across the bottom of the "
         "frame, five agents seen from behind in a symmetric row, black-suited shoulders and the backs of their heads, "
         "arms raised, aiming pistols up at her; the bullet's wake leads back to the muzzle of one of them. ")
C1_A2 = ("A breathtaking frozen moment, seen from a camera floating in the air just above and beside her, angled steeply "
         f"down into a deep canyon between {LOOP}. The anime girl is LARGE in the frame, frozen mid-wall-jump: one "
         "sneaker still touching the brick wall on the left where she kicked off, body arcing out over the drop toward "
         "the building on the right, arms flung wide, jacket flaring, a few strands of hair floating. Far below on the "
         "street five agents in black suits stand in a tight ring aiming pistols straight up at her, and the bullet's "
         "wake leads back down to them. Dizzying vertical perspective, Escher-like vertigo. ")
C1_B2 = ("A breathtaking frozen moment, bullet-time. Camera level with her in the air between "
         f"{LOOP}. The anime girl fills the center of the frame, frozen mid-leap from the wall on the left toward the "
         "wall on the right, body stretched out, one knee tucked, arms reaching, jacket and orange straps flying, a few "
         "hair strands floating. Below her, rising diagonally from the street, the bullet climbs toward her ribs. On the "
         "street far below, five agents in black suits aim pistols up at her. Slight dutch angle. ")
for v, comp in (("c2", C1_C2), ("c3", C1_C2), ("a2", C1_A2), ("b2", C1_B2)):
    job(f"C1_nbp{v}", NBP, comp + C1_BASE2 + STYLE, [JADE_SHEET, JADE_ACTION, AGENT_SHEET])

# --------------------------------------------------------------------------------------------------- intro, verse 1
NIGHT_LSD = ("Lake Shore Drive in Chicago at night, the car heading south: Lake Michigan on the LEFT, the downtown "
             "skyline on the RIGHT. ")
C3 = ("Wide establishing shot at night from high above Lake Michigan, looking west at the downtown Chicago skyline: "
      "Willis Tower, the John Hancock Center and the Aon Center rising as engraved towers with tiny lit windows, behind "
      "the long curve of Lake Shore Drive sweeping along the shoreline as an arc of streetlights reflected in the black "
      "water. One tiny white car on the drive, small, alone, heading south (toward the left). Calm lake in engraved "
      "horizontal ripples across the foreground, a thin crescent moon. The upper-middle sky is open and calm. ")
job("C3_sdr1", SDR, C3 + STYLE_NIGHT + STYLE_NOGIRL, [])
job("C3_sdr2", SDR, C3 + STYLE_NIGHT + STYLE_NOGIRL, [])
job("C3_nbp1", NBP, C3 + STYLE_NIGHT + STYLE_NOGIRL, [])

C4 = ("Night, inside a moving car. Side profile of the anime girl driving, seen from the passenger seat: both hands on "
      "the steering wheel, eyes on the road, calm and a little tired, orange headphones round her neck, bun with the "
      "yellow pencil. A soft white glow from the dashboard lights her face from below; streetlights streak past outside "
      "the driver's window behind her. She fills the right half of the frame. In the near foreground on the passenger "
      "seat, a thick bound dissertation (a heavy stack of paper with a plain card cover and a black spiral or tape "
      "binding) with one small square sticky note stuck on the cover, angled toward the camera, the note completely "
      "blank. The car interior, seats, dashboard and window are engraved. " + JADE)
job("C4_sdr1", SDR, C4 + STYLE_NIGHT + STYLE, [JADE_SHEET])
job("C4_nbp1", NBP, C4 + STYLE_NIGHT + STYLE, [JADE_SHEET, JADE_EXPR])

S2 = ("Night, high three-quarter view from above and behind " + CAR + " driving along " + NIGHT_LSD +
      "The car is exactly in the center of the frame, small but clear, headlights throwing engraved beams ahead; the "
      "curving road, the line of streetlights and the skyline wrap around it. ")
job("S2_sdr1", SDR, S2 + STYLE_NIGHT + STYLE_NOGIRL, [])
job("S2_nbp1", NBP, S2 + STYLE_NIGHT + STYLE_NOGIRL, [])

D1 = ("Night. Chase-cam directly behind " + CAR + " at speed on " + NIGHT_LSD + "The car fills the lower middle of the "
      "frame, tail lights glowing white. Ahead, an overhead highway sign gantry made of steel trusses spans the road, "
      "carrying two large rectangular sign panels: the panels are completely BLANK, smooth, pale, with a thin border "
      "line, absolutely no text or arrows. Streetlights as engraved starbursts. ")
job("D1_sdr1", SDR, D1 + STYLE_NIGHT + STYLE_NOGIRL, [])
job("D1_nbp1", NBP, D1 + STYLE_NIGHT + STYLE_NOGIRL, [])

D2 = ("Night, from inside the car, looking out the passenger-side window at the city sliding by: engraved towers and "
      "rooftops, water tanks, and on one rooftop a big old-fashioned hotel sign frame lined with round light bulbs whose "
      "two panels are completely BLANK (no letters). The window frame and door edge frame the view. At the left edge "
      "of the frame, soft in the foreground, the anime girl's shoulder and the back of her head with the bun and yellow "
      "pencil, headphones round her neck. " + JADE)
job("D2_sdr1", SDR, D2 + STYLE_NIGHT + STYLE, [JADE_SHEET])
job("D2_nbp1", NBP, D2 + STYLE_NIGHT + STYLE, [JADE_SHEET])

D3 = ("Night, tight shot inside the car. The rectangular rearview mirror fills the right half of the frame; in the "
      "mirror: the dark engraved road behind and, following close, a black sedan with its headlights OFF, a dark "
      "looming shape. Along the bottom edge of the mirror glass, a clean empty strip. On the left of the frame, the "
      "anime girl's face in three-quarter profile, her eyes glancing up toward the mirror, wary, brows relaxed, the "
      "bun and pencil visible. " + JADE)
job("D3_sdr1", SDR, D3 + STYLE_NIGHT + STYLE, [JADE_SHEET, JADE_EXPR])
job("D3_nbp1", NBP, D3 + STYLE_NIGHT + STYLE, [JADE_SHEET, JADE_EXPR])

D4 = ("Night, low camera on the road shoulder of " + NIGHT_LSD + CAR + " has just rolled to a stop on the gravel "
      "shoulder, its rear in the left foreground. Behind it a long black sedan pulls in, its two headlights flaring "
      "toward the camera as huge engraved white starbursts with radiating lines that wash across the frame. ")
job("D4_sdr1", SDR, D4 + STYLE_NIGHT + STYLE_NOGIRL, [])
job("D4_nbp1", NBP, D4 + STYLE_NIGHT + STYLE_NOGIRL, [])

D5 = ("Night. Three agents have stepped out of a black sedan and walk toward the camera in perfect symmetry, backlit by "
      "the sedan's blazing headlights behind them (engraved starbursts), long hard shadows stretching toward us. Low "
      "angle. The center agent is closest and largest, framed from the knees up; his opaque black sunglasses are large "
      "and glossy with clean curved highlights. " + AGENTS)
job("D5_sdr1", SDR, D5 + STYLE_NIGHT + STYLE_NOGIRL, [AGENT_SHEET])
job("D5_nbp1", NBP, D5 + STYLE_NIGHT + STYLE_NOGIRL, [AGENT_SHEET, AGENT_ACTION])

D6 = ("Night, low angle from inside the car past the anime girl's shoulder: she sits in the driver's seat in the left "
      "foreground (back of her shoulder, white jacket, bun with the yellow pencil, headphones), looking up through the "
      "open driver's window at two agents standing at the window, looming over the car. The nearer agent holds out a "
      "residue meter toward her: a palm-sized brass device like a pocket stopwatch crossed with a Geiger counter, round "
      "case with a crown button, a needle-gauge dial, a coiled cable to a small wand probe. " + JADE + AGENTS)
job("D6_sdr1", SDR, D6 + STYLE_NIGHT + STYLE, [JADE_SHEET, AGENT_ACTION])
job("D6_nbp1", NBP, D6 + STYLE_NIGHT + STYLE, [JADE_SHEET, AGENT_ACTION, AGENT_SHEET])

D7 = ("Night, close-up on the anime girl's hands (full color) pulling an ID card out of the inside pocket of her white "
      "bomber jacket; the orange band of the jacket and the black crop top are visible, her face is out of frame above. "
      "The ID card is in FULL COLOR and faces the camera almost flat: a white card with a pale-blue header band and a "
      "small anime portrait photo of the girl on the left; every text area on the card is completely BLANK. The car "
      "interior behind is engraved. " + JADE)
job("D7_nbp1", NBP, D7 + STYLE_NIGHT + STYLE, [JADE_SHEET])
job("D7_sdr1", SDR, D7 + STYLE_NIGHT + STYLE, [JADE_SHEET])

D8 = ("Night, medium close-up at the car window: an agent holds the girl's ID card (the only colored object: white card, "
      "pale-blue header band, tiny portrait; faint orange and sky-blue glowing motes shimmer up off it) in one hand, and "
      "in the other hand the residue meter (brass stopwatch / Geiger counter with a needle dial) whose needle is pinned "
      "hard at the maximum. His blank face with opaque sunglasses above, head tilted slightly to one side, uncanny. "
      + AGENTS)
job("D8_nbp1", NBP, D8 + STYLE_NIGHT + STYLE_NOGIRL.replace("no color anywhere.", "no color anywhere except the ID card and its motes."), [AGENT_SHEET, AGENT_ACTION])
job("D8_sdr1", SDR, D8 + STYLE_NIGHT + STYLE_NOGIRL.replace("no color anywhere.", "no color anywhere except the ID card and its motes."), [AGENT_SHEET])

P1 = ("Night, close shot at waist height of an agent standing beside the car: his hand slides inside his black suit "
      "jacket, the lapel lifting to reveal a shoulder holster strap; the car door edge in the foreground. " + AGENTS)
job("P1_nbp1", NBP, P1 + STYLE_NIGHT + STYLE_NOGIRL, [AGENT_SHEET])
job("P1_sdr1", SDR, P1 + STYLE_NIGHT + STYLE_NOGIRL, [AGENT_SHEET])

P2 = ("Night, close shot of the anime girl in the driver's seat, three-quarter view, her eyes widening in sudden shock, "
      "small pupils, lips parted, a sweat drop; the bun and pencil and headphones visible; engraved car interior and the "
      "dark window behind her. " + JADE)
job("P2_nbp1", NBP, P2 + STYLE_NIGHT + STYLE, [JADE_SHEET, JADE_EXPR])
job("P2_sdr1", SDR, P2 + STYLE_NIGHT + STYLE, [JADE_SHEET, JADE_EXPR])

P3 = ("Night, shallow focus. In the sharp foreground, an agent's hand raising a plain black pistol in profile, aimed LOW "
      "and level at body height (never at a head). Through the open car window beyond, soft and out of focus, the "
      "girl's torso in the driver's seat: white jacket with its orange band, black crop top; her head is out of frame. "
      + JADE + AGENTS)
job("P3_nbp1", NBP, P3 + STYLE_NIGHT + STYLE, [JADE_SHEET, AGENT_ACTION])
job("P3_sdr1", SDR, P3 + STYLE_NIGHT + STYLE, [JADE_SHEET, AGENT_ACTION])

P4a = ("Night. A muzzle flash fills the frame: a huge engraved starburst of radiating black-and-white lines exploding "
       "from the muzzle of a plain black pistol held by an agent's hand at the left edge; concentric shock rings in the "
       "air, a few engraved sparks. Pure woodcut graphic. ")
job("P4_flash1", NBP, P4a + STYLE_NIGHT + STYLE_NOGIRL, [])
P4b = ("Night, close shot of the anime girl's torso only (chest to waist, her head out of frame above): white cropped "
       "bomber with the orange band across the chest, the pale-blue dot patch, black crop top, the headphones' lower edge "
       "at the top of the frame. At her side, over her ribs, her body is beginning to burst into a cloud of small glowing "
       "square motes of bright orange and pale sky-blue, flying outward like a video-game death, no blood, no wound. "
       "Engraved car interior behind. " + JADE)
job("P4_torso1", NBP, P4b + STYLE_NIGHT + STYLE, [JADE_SHEET])
job("P4_torso2", SDR, P4b + STYLE_NIGHT + STYLE, [JADE_SHEET])


# C1 round 3: refine the chosen composition (nbpc2): bigger, clearer bullet, cleaner agents
C1_C4 = C1_C2.replace("a few brick chips frozen in the air", "a burst of brick chips and dust frozen in the air") + (
    "The bullet is clearly readable: a glinting brass bullet, slightly larger than life, its tip pointing up at her "
    "ribs, its engraved wake of rings and speed lines drawing a clean straight line back down to the center agent's "
    "pistol. Each agent holds one pistol in both hands; no extra hands. ")
job("C1_nbpc4", NBP, C1_C4 + C1_BASE2 + STYLE, [JADE_SHEET, JADE_ACTION, AGENT_SHEET])
job("C1_nbpc5", NBP, C1_C4 + C1_BASE2 + STYLE, [JADE_SHEET, JADE_ACTION, AGENT_SHEET])

# D3 reroll: the following sedan must be UNLIT
D3b = D3.replace("a black sedan with its headlights OFF, a dark looming shape",
                 "a black sedan running with NO lights at all: dark unlit headlights, a black looming silhouette, "
                 "only its outline and windshield picked out by faint engraved lines")
job("D3_sdr2", SDR, D3b + STYLE_NIGHT + STYLE, [JADE_SHEET, JADE_EXPR])
job("D3_sdr3", SDR, D3b + STYLE_NIGHT + STYLE, [JADE_SHEET, JADE_EXPR])

# --------------------------------------------------------------------------------------------------- R2: 13 deaths
DEATH = ("Time is frozen at the instant of a video-game death: the girl's body (torso and limbs, never the head) is "
         "bursting apart into a cloud of small glowing square motes of bright orange and pale sky-blue, like a Celeste "
         "death, frozen mid-burst; no blood, no wound, no gore; her face stays intact, eyes wide. She is large in the "
         "frame. " + JADE)
R2 = [
    ("01train", "On the elevated L tracks of the Chicago Loop, the flat front of an old steel L train is a foot from "
                "her, about to hit her; she stands on the rails between the girders, arms raised; engraved headlight "
                "starburst. Low angle along the tracks.", True),
    ("02marina", "Falling headfirst past the round scalloped balconies of Marina City's twin corncob towers, the river "
                 "far below; the motes stream upward from her as she falls. Vertical, vertiginous view.", False),
    ("03picasso", "In Daley Plaza, the huge rusted-steel Chicago Picasso sculpture has toppled over onto her, she is "
                  "pinned beneath its curved steel plates and bursting into motes. Wide plaza, civic center building "
                  "behind.", False),
    ("04bridge", "A Chicago River bascule bridge leaf is rising under her, tilting up steeply like a ramp, flinging her "
                 "into the air above the dark river; huge gears and counterweights; she is bursting mid-air.", False),
    ("05fountain", "At Buckingham Fountain, a massive vertical jet of water blasts her into the air above the tiered "
                   "fountain basin; spray engraved in white lines; she is bursting mid-air.", True),
    ("06watertower", "On a Chicago rooftop, a giant wooden water tower on stilts has broken loose and is falling onto "
                     "her from above, filling the top of the frame, water spilling; she looks up, bursting.", False),
    ("07riverwalk", "On the Chicago Riverwalk at night, she is swarmed by a dozen identical agents in black suits and "
                    "black sunglasses closing in from every side, hands reaching for her; she is bursting into motes in "
                    "the middle of the ring. " + AGENTS, True),
    ("08skydeck", "The glass box of the Willis Tower Skydeck ledge has shattered under her; she falls out among the "
                  "glass shards with the whole grid of the city a hundred floors below; bursting.", False),
    ("09lightning", "On the roof of the John Hancock Center between its two antenna masts at night, a bolt of engraved "
                    "lightning strikes her; she is bursting into motes.", True),
    ("10gears", "Caught inside a giant tower clock mechanism: enormous brass gears and the back of a huge clock face, "
                "the gear teeth closing on her; she is bursting into motes between the gears.", False),
    ("11ferris", "Flung off the top of the Navy Pier Ferris wheel, the spokes and gondolas behind her, the lake and "
                 "pier below; she is bursting mid-air.", False),
    ("12ice", "On frozen Lake Michigan in winter, the ice cracking open in a star pattern under her, black water "
              "beneath, the skyline far behind; she is falling through, bursting into motes.", False),
    ("13sedan", "On Lake Shore Drive at night, a black sedan's grille and blazing headlight starbursts are inches from "
                "her, about to hit her; she is bursting into motes, side view.", True),
]
for rid, scene, night in R2:
    job(f"R2_{rid}", NBP, scene + " " + DEATH + (STYLE_NIGHT if night else "") + STYLE,
        [JADE_SHEET, JADE_ACTION] + ([AGENT_SHEET] if "agents" in scene else []))


# R2 rerolls (02 came back portrait with paper bars, 10 drew two girls and gold gears, 13 was daytime and limp)
R2b = {
    "02marinab": ("Wide horizontal 16:9 composition. Seen from the side, she falls through the air between Marina "
                  "City's two round corncob towers with their scalloped balconies, the river and bridges far below; the "
                  "motes stream upward from her as she falls.", False),
    "10gearsb": ("Wide horizontal 16:9 composition. Inside a giant tower-clock mechanism: enormous engraved gears (black "
                 "ink only, NOT gold, no color) and the back of a huge translucent clock face; the gear teeth are closing "
                 "on ONE single girl (only one girl in the picture); she is bursting into motes between the gears.", False),
    "13sedanb": ("Night on Lake Shore Drive. Low side view: a black sedan's chrome grille and two blazing headlight "
                 "starbursts are inches from her as she leaps sideways too late, her body already bursting into motes "
                 "on impact; streetlights and the dark lake behind.", True),
}
for rid, (scene, night) in R2b.items():
    job(f"R2_{rid}", NBP, scene + " " + DEATH + (STYLE_NIGHT if night else "") + STYLE, [JADE_SHEET, JADE_ACTION])


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "list":
        for k, j in J.items():
            print(k, j["model"], os.path.relpath(j["out"], ROOT), len(j["prompt"]))
    elif cmd == "show":
        for k in sys.argv[2:]:
            print(k, J[k]["prompt"], J[k]["refs"])
    elif cmd == "run":
        args = [a for a in sys.argv[2:] if not a.startswith("--")]
        sel = [k for k in J if any(k == a or (a.endswith("_") and k.startswith(a)) for a in args)]
        if "--missing" in sys.argv:
            sel = [k for k in sel if not any(os.path.exists(os.path.splitext(J[k]["out"])[0] + e) for e in (".png", ".jpg"))]
        print("running", sel)
        res = run_jobs([J[k] for k in sel], workers=int(os.environ.get("WORKERS", 4)))
        os.makedirs(os.path.join(SHOTS, "_A_sheets"), exist_ok=True)
        out = os.path.join(SHOTS, "_A_sheets", f"{sel[0]}_{len(sel)}.jpg")
        sheet([(res[k], k) for k in sel], out, title=" ".join(sel))
        print(out)
