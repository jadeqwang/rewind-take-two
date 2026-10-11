#!/usr/bin/env python
"""Section D video shots (Seedance 2.0, first-frame locked). Registers the D_* shots into tools/gen/vgen.py's
registry at run time so the shared tools/gen/shots.py is never edited by this section.

    PY=~/Documents/moongazing/.venv/bin/python
    $PY tools/sections/D/dgen.py submit D_trk_sprint [...] [--takes=N] [--res=720p] [--dry-run]
    $PY tools/sections/D/dgen.py collect|wait [D_... ...]      (default: every D_* shot)
    $PY tools/sections/D/dgen.py list
Takes land in media/gen/<SHOT>/take_N.mp4 (+ _sheet.jpg); link them into media/shots/<E#>/ with publish.py.
"""
import os
import sys

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
import vgen  # noqa: E402

SD20 = "bytedance/seedance-2.0"
LOOK = ("Keep the first frame's look: the world stays a crisp black-and-white Escher-style wood engraving, only the anime "
        "girl in full color with her exact outfit (white cropped bomber with orange band, navy cargo pants, orange "
        "headphones round her neck, black hair in a bun with a yellow pencil). Her face keeps its shape, forehead smooth, "
        "never a face close-up. No text, no letters, no logos.")
LOOK_AG = ("Keep the first frame's look: everything stays a crisp black-and-white Escher-style wood engraving, no color, "
           "no gray wash. No text, no letters, no numbers.")
LOCK = "Static locked-off camera: the camera does not move, pan or zoom at all; the background stays perfectly still. "

KF = {
    "trk": "media/shots/E2/kf_E2_trk_nano_t1.jpg",
    "fld": "media/shots/E2/kf_E2_fld_nano_t1.jpg",
    "ring": "media/shots/E2/kf_E2_ring_nano_t2.jpg",
    "gap": "media/shots/E4/kf_E4_gap_nano_t1.jpg",
    "boost": "media/shots/E5/kf_E5_boost_nano_t1.jpg",
    "hand": "media/shots/E5/kf_E5_hand_nano_t1.jpg",
    "slip": "media/shots/E5/kf_E5_slip_nano_t1.jpg",
    "single": "media/shots/E6/kf_E6_single_nano_t1.jpg",
    "split": "media/shots/E6/kf_E6_split_nano_t1.jpg",
    "hero": "media/shots/E7/kf_E7_hero_nano_t1.jpg",
    "meter": "media/shots/E7/kf_E7_meter_nano_t1.jpg",
    "city": "media/shots/E7/kf_E7_city_nano_t1.jpg",
    "e8ring": "media/shots/E8/kf_E8_ring_nano_t1.jpg",
    "e8line": "media/shots/E8/kf_E8_line_nano_t1.jpg",
}


def S(kf, prompt, dur=5, look=LOOK, fixed=True):
    return dict(model=SD20, image=KF[kf], duration=dur, camera_fixed=fixed, prompt=prompt + " " + look)


D_SHOTS = {
    # E2 setup 1: L tracks, side-on. Same first frame, three different attempts (ghosts 1-3).
    "D_trk_sprint": S("trk", LOCK + "The girl bursts out of her crouch and sprints extremely fast from left to right along "
                      "the track deck, long powerful strides, arms pumping, and runs out of frame on the right."),
    "D_trk_walljump": S("trk", LOCK + "The girl bursts out of her crouch, sprints extremely fast to the right, leaps at the "
                        "tall steel column, kicks off it with one foot high in the air and flips backward in a big "
                        "acrobatic arc, landing on the deck in a crouch. Extremely fast."),
    "D_trk_dash": S("trk", LOCK + "The girl springs out of her crouch into a long horizontal flying dive to the right, body "
                    "stretched flat in the air like a superhero dash, then lands in a forward shoulder roll and springs "
                    "back up to her feet running. Extremely fast."),
    # E2 setup 2: Grant Park lawn, ground level (ghosts 4-8).
    "D_fld_slide": S("fld", LOCK + "The girl sprints extremely fast at the agents and drops into a low baseball slide on "
                     "her hip across the grass, sliding underneath their grabbing arms and out past them on the right; "
                     "the agents grab at empty air."),
    "D_fld_vault": S("fld", LOCK + "The girl sprints extremely fast at the agents, plants both hands on the shoulders of "
                     "the nearest agent and vaults clean over him in a high leapfrog, legs tucked, landing behind him; the "
                     "agents turn around, bewildered."),
    "D_fld_spin": S("fld", LOCK + "The girl sprints extremely fast at the agents and spins in a fast full pirouette "
                    "sidestep around the reaching arms of the nearest agent, then darts past them; the agents stumble "
                    "into each other."),
    "D_fld_cartwheel": S("fld", LOCK + "The girl sprints extremely fast at the agents and throws an extremely fast "
                         "no-handed aerial cartwheel right over their outstretched arms, landing on her feet behind them; "
                         "the agents duck and flinch."),
    # E2 setup 3: high wide over the agent ring (ghosts 9-13).
    "D_ring_circle": S("ring", LOCK + "The girl sprints extremely fast in a full circle around the ring of agents across the "
                       "open grass, staying in frame; the agents swivel their heads and shuffle, bewildered, trying to "
                       "follow her."),
    # E4: Super Meat Boy replay (the engine multiplies her into a stream).
    "D_e4_stream": S("gap", LOCK + "The girl sprints extremely fast to the right, leaps across the gap between the two "
                     "track sections in one long soaring jump, lands on the right section beside the agents and keeps "
                     "running out of frame on the right. The agents flinch and turn their heads, bewildered."),
    # E5: co-op boost, slip of paper.
    "D_e5_boost": S("boost", LOCK + "The running girl on the right sprints extremely fast to the kneeling girl at the wall, "
                    "steps one foot into her cupped hands, and the kneeling girl heaves her straight up; she flies up the "
                    "brick wall, grabs the rooftop cornice and vaults up over it onto the roof. The kneeling girl stays "
                    "below, looking up."),
    "D_e5_hand": S("hand", LOCK + "The girl on the left hands the small folded slip of paper to the girl on the right, who "
                   "takes it, and they exchange a quick knowing nod. Small natural movements, hair and jackets stirring "
                   "in the wind.", dur=4),
    "D_e5_slip": S("slip", LOCK + "Close-up: her two hands hold the small slip of paper steady and flat toward the camera; "
                   "only a slight breeze makes one corner flutter and her fingers shift a little. The paper stays "
                   "completely blank and stays in the same place in frame.", dur=4),
    # E6: Banach-Tarski.
    "D_e6_single": S("single", LOCK + "The agents creep in slowly from both sides, reaching for her; the girl stands her "
                     "ground in the center, her smirk widening, jacket and hair stirring in the wind.", dur=4),
    "D_e6_split": S("split", LOCK + "The two girls burst apart in opposite directions, sprinting extremely fast, one to the "
                    "left and one to the right, straight past the agents; the agents spin around, collide with each "
                    "other and split up, half of them chasing each girl."),
    # E7: colour everywhere.
    "D_e7_hero": S("hero", "The camera tracks backward at the same speed as she sprints extremely fast straight toward "
                   "the camera along the tracks, euphoric grin, arms pumping, the rails rushing beneath her; she stays "
                   "the same size in frame.", fixed=False),
    "D_e7_meter": S("meter", "Static camera, close-up. The needle on the meter spins wildly around and around, faster and "
                    "faster, the meter trembling in his hand as he shakes it.", dur=4, look=LOOK_AG),
    "D_e7_city": S("city", "The camera flies slowly forward and descends over the city in one smooth continuous move, the "
                   "rooftops and the elevated tracks passing below.", look=LOOK_AG, fixed=False),
    # E8: anomaly detected.
    "D_e8_ring": S("e8ring", "Static camera. For a moment the agents stand still, searching; then all of them at exactly "
                   "the same instant snap their heads and turn their bodies to stare straight into the camera, perfectly "
                   "in unison, and freeze, motionless.", dur=4, look=LOOK_AG),
    "D_e8_line": S("e8line", "Static camera. The agents stand in profile, then all six at exactly the same instant snap "
                   "their heads to face straight into the camera, perfectly in unison, and freeze, motionless.", dur=4,
                   look=LOOK_AG),
}
vgen.SHOTS.update(D_SHOTS)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    opts = {a[2:].partition("=")[0]: a[2:].partition("=")[2] or True for a in sys.argv[2:] if a.startswith("--")}
    if cmd == "submit":
        for s in args:
            over = {k: (int(v) if k == "duration" else v) for k, v in opts.items() if k in ("duration", "prompt", "model")}
            for j in vgen.submit(s, opts.get("res", "720p"), int(opts.get("takes", 1)), "dry-run" in opts,
                                 opts.get("note", ""), over):
                print(s, j)
        print(f"spend so far (est): ${vgen.spend_total()}")
    elif cmd in ("collect", "wait"):
        import time
        t0 = time.time()
        while True:
            p = vgen.collect(args or sorted(D_SHOTS))
            if cmd == "collect" or not p or time.time() - t0 > float(opts.get("timeout", 3600)):
                print("pending:", p)
                break
            time.sleep(30)
    elif cmd == "list":
        for k, v in D_SHOTS.items():
            print(k, v["duration"], v["image"])
    else:
        print(__doc__)
