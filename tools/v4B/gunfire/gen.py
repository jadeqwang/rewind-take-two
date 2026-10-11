#!/usr/bin/env python3
"""v4 gunfire build: keyframes, Seedance takes and engraves for the restaged lawn shots (plan: docs/revisions/v4/plans/gunfire.md).
Reuses rev-B's runner (tools/sections/B/rb.py) with its own prompts and the spend tag v4B_gun_.

    PY=~/Documents/moongazing/.venv/bin/python
    $PY tools/v4B/gunfire/gen.py kf NAME [NAME ...] [--v=2] [--dry-run]         # media/shots/B_<NAME>/kf_v<N>.*
    $PY tools/v4B/gunfire/gen.py edit NAME SRC "instruction" [--v=2] [REF ...]   # nano edit of an image
    $PY tools/v4B/gunfire/gen.py submit TAKE [--res=720p] [--kf=NAME:v] [--dry-run]
    $PY tools/v4B/gunfire/gen.py wait TAKE [TAKE ...]
Shots: g1world (lawn + Jade, G1's plate), gagent (one agent on paper: A, B and C are copies), g2 (the whole of G2),
g3ear (earpiece close-up, an edit of v3's B_ear keyframe).
"""
import os
import sys

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/sections/B"))
import rb  # noqa: E402
import prompts as P  # noqa: E402
from rb import vgen  # noqa: E402

rb.TAG = "v4B_gun_"
G1REF, G2REF = "media/shots/B_g1world/ref_blockout.jpg", "media/shots/B_g2/ref_blockout.jpg"
SKETCH = ("One attached image is a flat grey-box layout sketch: use it ONLY as a layout guide (where each figure and "
          "object stands, how large it is, where the horizon is) and match that composition closely; do not copy its "
          "flat grey shapes or its look. ")
BACK = ("We see the girl only from BEHIND: the back of her white cropped bomber jacket with ONE large pale-blue circle "
        "in the middle of the back and the orange band around the sleeves, the back of her head with her black hair in "
        "a high bun and TWO yellow pencils crossed through it, orange headphones round her neck, navy-blue cargo pants "
        "with hanging orange straps, chunky white sneakers. Her face is not visible. ")

P.KF.update({
    "g1world": dict(refs=[P.JREF, P.HOTEL, G1REF], prompt=P.DAY + SKETCH + (
        "Wide shot from standing eye height looking straight down a broad, flat, completely open mown lawn carved as "
        "flowing engraved strokes; the lawn fills the lower half of the frame and the level horizon runs across the "
        "middle, with a calm lake on the horizon at the left and a few small trees far away. In the right distance "
        "stands the hotel of the attached hotel reference in three-quarter view, about a fifth of the frame wide, its "
        "roof near the top of the frame, with a completely blank white billboard panel on its roof. There are no "
        "agents and no other people anywhere, no path, no bench, no objects on the lawn. The girl is FAR AWAY and "
        "TINY in this wide shot: a small distant figure at the centre of the frame, only about one seventh of the "
        "frame height from her sneakers to the top of her bun (the hotel is four times taller than she is in the "
        "picture), her feet on the lawn a little below the horizon line, with a wide stretch of empty lawn between "
        "the camera and her. She sprints directly away from the camera toward the hotel, mid-stride, leaning hard "
        "into a sharp cut to the right. ") +
        BACK + P.JADE + P.STYLE),
    "gagent": dict(refs=[P.AGENT], prompt=P.DAY + (
        "One single agent alone on a completely blank sheet of warm off-white paper: no ground, no horizon, no shadow, "
        "no scenery, nothing else in the picture. He is seen from BEHIND and a little from his right side, a rear "
        "three-quarter view: we see his back, the back of his slicked head, his right ear with the coiled earpiece "
        "wire running down into his collar; his face is not visible. He stands in the left third of the frame in a "
        "steady firing stance, feet apart, both arms stretched straight out in front of him, away from the camera, "
        "holding a black semi-automatic pistol in a two-handed grip. Because we look past his right shoulder, his "
        "forearms, hands and the whole pistol are clearly visible to the right of his body, pointing away into the "
        "picture toward the upper right; the barrel is one clear straight line. He is framed from the knees to the top "
        "of his head and fills the full height of the frame. ") + P.AGENTS + P.STYLE_NOGIRL + " " + P.NOTEXT),
    "g2": dict(refs=[P.JREF, P.AGENT, G2REF], prompt=P.DAY + SKETCH + (
        "A long-lens shot from behind three agents, looking past them down a broad flat mown lawn carved as flowing "
        "engraved strokes; level horizon just above the middle of the frame. All three agents have their BACKS to the "
        "camera. At the left edge of the frame, large, cut off by the frame at the hips: an agent seen from behind "
        "who has lowered his pistol to his side in his left hand and presses two fingers of his raised right hand to "
        "the coiled earpiece at his right ear, elbow out. At the right edge of the frame, large, cut off at the hips: "
        "a second agent seen from behind with his arms down, a pistol lowered in his right hand, his left hand open at "
        "his side. Between them, further away and smaller, left of centre, framed from the knees up: the third agent "
        "seen from behind in a firing stance, both arms stretched out in front of him away from the camera, aiming a "
        "black pistol toward the girl; his arms and the pistol are visible past his right shoulder, the barrel a clear "
        "straight line pointing into the distance. Beyond him, right of centre, stands a large park notice board on two "
        "wooden posts: a completely blank cream panel about 25% of the frame wide and 30% of the frame high, nothing "
        "written or drawn on it. In front of the lower edge of the board, small, about 20% of the frame height, the "
        "girl sprints away from the camera across the lawn, leaning into a sharp cut to the right. Behind everything, "
        "filling the right background, the lower storeys of a grand 1920s limestone hotel with tall arched ground-floor "
        "windows and one sharp corner. ") + BACK + P.JADE + P.AGENTS + P.STYLE),
})

EAR_EDIT = (
    "Edit this wood engraving into a CLOSE shot, keeping exactly the same drawing style, ink line work and paper. Zoom "
    "in on the nearest agent, the large man at the left with two fingers at his earpiece who is speaking: his head, "
    "his raised hand and his shoulders now fill the left half of the frame from top to bottom, his face in profile "
    "facing right, mouth slightly open, the coiled earpiece wire clear behind his ear. Change the second agent: he "
    "now stands just beyond the first man's shoulder, a little smaller, also facing right in profile, and he too has "
    "LOWERED his pistol out of sight and presses two fingers to the earpiece at his ear, mouth slightly open, "
    "speaking; he does not aim. Remove the third agent completely: there are exactly two agents in the picture and "
    "no pistol is raised. Keep the far right background: the flat mown lawn, the tiny girl in full color seen from "
    "behind running away toward the hotel at the right edge, the hotel's rooftop billboard blank. The agents are plain "
    "identical men in black suits, white shirts, thin black ties and opaque black sunglasses, drawn in black and "
    "white. No text, no letters, no numbers anywhere. Full bleed 16:9, no border.")

P.VID.update({
    "g1world": dict(kf="g1world", dur=5, prompt=(
        "The girl sprints away from the camera across the open lawn toward the hotel in a wide, sharp zigzag: she cuts "
        "hard to the right and runs diagonally, then cuts hard to the left and runs diagonally, then right again, low "
        "and fast, always getting further away and smaller. We only ever see her from behind; she never turns round "
        "and never looks back. The lawn, the hotel and the trees stay perfectly still and nobody else appears.")),
    "gagent": dict(kf="gagent", dur=5, girl=False, prompt=(
        "The man keeps his back to the camera in his firing stance and never turns round. He fires his pistol four "
        "times, about once a second: with each shot his hands and the pistol kick sharply upward a little and come "
        "straight back down on target, and his shoulders rock. Between shots he tracks a distant moving target, his "
        "arms swinging slightly left and right. No muzzle flash, no smoke, no shell casings. The background stays "
        "blank paper.")),
    "g2": dict(kf="g2", dur=4, prompt=(
        "The girl sprints away across the lawn in front of the notice board in a tight, sharp zigzag, cutting right "
        "and left every half second, getting smaller. The far agent in the middle keeps aiming at her and fires twice, "
        "his hands kicking up with each shot. The agent on the left keeps two fingers pressed to his earpiece and nods "
        "slightly as he speaks. The agent on the right raises his left hand and presses two fingers to his left ear. "
        "All three keep their backs to the camera. The notice board stays blank and perfectly still. No muzzle "
        "flashes, no smoke.")),
    "g3ear": dict(kf="g3ear", dur=4, prompt=(
        "The nearest agent keeps two fingers pressed to his earpiece and calmly speaks a few words, then gives one "
        "small nod. The agent behind him also speaks into his earpiece. Far away the tiny girl keeps running toward "
        "the hotel.")),
})

if __name__ == "__main__":
    cmd = sys.argv[1]
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    opts = {a[2:].partition("=")[0]: a[2:].partition("=")[2] or True for a in sys.argv[2:] if a.startswith("--")}
    v = int(opts.get("v", 1))
    if cmd == "kf":
        for n, p in rb.run_kf(args, opts.get("model", "nano"), v, "dry-run" in opts).items():
            print(n, p)
    elif cmd == "edit":
        instr = EAR_EDIT if args[2] == "EAR_EDIT" else args[2]
        print(rb.edit(args[0], args[1], instr, v, tuple(args[3:])))
    elif cmd == "submit":
        for t in args:
            rb.register(t, opts.get("kf"))
            for j in vgen.submit("B_" + t, opts.get("res", "720p"), 1, "dry-run" in opts):
                print(t, j)
        print(f"spend so far (est): ${vgen.spend_total()}")
    elif cmd in ("collect", "wait"):
        import time
        for t in args:
            vgen.SHOTS.setdefault("B_" + t, {})
        t0 = time.time()
        while True:
            pend = vgen.collect(["B_" + t for t in args])
            rb.link(args)
            if cmd == "collect" or not pend or time.time() - t0 > float(opts.get("timeout", 1500)):
                print("pending:", pend)
                break
            time.sleep(30)
