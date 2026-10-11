#!/usr/bin/env python3
"""Section C video takes on top of tools/gen/vgen.py, without editing the shared tools/gen/shots.py registry.

    $PY tools/sectionC/vid.py submit CLIP[:kf_name] [...] [--res=720p] [--takes=1] [--dry-run] [--prompt=...]
    $PY tools/sectionC/vid.py collect|wait [CLIP ...]
    $PY tools/sectionC/vid.py link [CLIP ...]     # hardlink media/gen/<CLIP>/take_N.mp4 + sheets into media/shots/<CLIP>/

The first frame is media/shots/<CLIP>/kf_<name>.png (default: the `kf` field below). Optional `last` = a last-frame
image (Seedance 2.0 `last_frame_image`). Takes land in media/gen/<CLIP>/ (vgen) and are linked into media/shots/<CLIP>/.
"""
import glob
import os
import sys

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
import vgen  # noqa: E402

SD20 = "bytedance/seedance-2.0"
KEEP = ("Keep the black-and-white wood-engraving look of the first frame on the whole world; only the anime girl is in "
        "color. No text, no letters, no logos.")
KEEP_NOGIRL = ("Keep the black-and-white wood-engraving look of the first frame; no color anywhere. No text, no letters, "
               "no logos.")
SIDE_TRACK = "The camera tracks sideways at exactly the same speed, side-scrolling like a 2D platformer. "

# clip: (default keyframe, duration s, motion prompt, has_girl)
C = {
    "V2a1": ("s", 6, SIDE_TRACK + "The white sedan drives extremely fast to the right and stays in the same place in "
             "frame while the road, lamp posts and lake scroll past extremely fast from right to left. The black "
             "sedans behind accelerate and gain on it, their roof strobes flashing.", False),
    "V2a2": ("s", 4, "The camera tracks sideways alongside the wheel at high speed; the wheel spins extremely fast and "
             "stays in place in frame; the road streaks past from right to left; grit and sparks fly.", False),
    "V2a3": ("n", 6, "Static camera inside the speeding car. She drives: her eyes flick up to the rearview mirror, then "
             "she yanks the steering wheel hard to one side, her body leaning with the turn, then she grips the wheel and "
             "leans forward, flooring it. Streetlights streak past the window extremely fast. Her face keeps the first "
             "frame's angle, forehead smooth, never a face close-up.", True),
    "V2a4": ("s", 5, SIDE_TRACK + "The pack of black sedans races extremely fast to the right; more black sedans merge "
             "into the pack from the on-ramp and the pack grows; roof strobes flash; the skyline scrolls right to left.",
             False),
    "V2a5": ("s", 4, SIDE_TRACK + "The black sedan swerves into the white car to ram it; the white car brakes and jinks "
             "away at the last instant; the black sedan misses and smashes into the concrete barrier in a burst of white "
             "sparks. Extremely fast.", False),
    "V2b1": ("s", 5, SIDE_TRACK + "The white sedan races extremely fast to the right, hits the tilted road slab like a "
             "ramp, flies through the air and lands on the road beyond.", False),
    "V2b2": ("s", 4, SIDE_TRACK + "The upside-down black sedan tumbles through the air in an arc over the white sedan "
             "and crashes down on the road behind it; the white sedan keeps racing to the right. Extremely fast.", False),
    "V2b3": ("n", 4, "Camera fixed inside the car. The upside-down black car passes over the windshield from front to "
             "back extremely fast, inches above the glass; she ducks and flinches, then looks back up. Her face keeps "
             "the first frame's angle.", True),
    "V2b4": ("s", 4, SIDE_TRACK + "The streetlamp topples across the road; the white sedan races under it just in time; "
             "the lamp post crashes onto the road right behind the car in an explosion of white sparks. Extremely fast.",
             False),
    "V2b5": ("s", 4, "The camera follows close behind the white car. The two trucks squeeze together; the white sedan "
             "accelerates extremely fast into the narrowing gap between them.", False),
    "V2b6": ("s", 5, "Straight top-down camera moving with the white car: the car threads the narrowing gap between the "
             "two trucks extremely fast, its side mirrors sheared off in sparks, and bursts out ahead; behind it the "
             "trucks' trailers slam together. Straight top-down view throughout.", False),
    "V2c1": ("s", 4, "The camera follows behind the speeding car. The striped gate arms swing down across the road, the "
             "bell swings, warning lamps flash; the bridge deck ahead begins to lift.", False),
    "V2c2": ("s", 5, "The enormous bridge leaf rises steadily higher into the sky, tilting the road upward; the small "
             "white car races toward it. The camera slowly tilts up following the rising leaf. Heavy, grand motion.",
             False),
    "V2c3": ("s", 5, SIDE_TRACK + "The two black sedans slam into the white car's sides from both lanes, sparks flying; "
             "the white car accelerates and bursts forward out of the sandwich; then a black sedan clips its rear bumper "
             "and the white car fishtails and recovers. Extremely fast.", False),
    "V2c4": ("n", 4, "Camera fixed. The sneaker stamps the pedal down to the floor and holds it there hard, the leg "
             "straining; the car shudders with acceleration.", True),
    "V2c5": ("n", 5, "Camera fixed inside the car, the gauge in sharp focus. The speedometer needle sweeps up and past the "
             "end of the dial and pins there, trembling; through the windshield the rising bridge leaf rushes closer. "
             "Her hands grip the wheel.", True),
    "V2c6": ("s", 4, "The camera rushes forward up the steep ramp extremely fast; the gap at the top edge grows wider, "
             "revealing the river far below.", False),
    "V2c7": ("s", 5, "The high aerial camera glides forward behind the formation; the V of black sedans spreads wider "
             "across all lanes as they chase the white car toward the raised bridge; roof strobes flash in a ripple.",
             False),
    "V2c8": ("s", 4, SIDE_TRACK + "The white car smashes through the gate arm extremely fast, splinters exploding over "
             "the hood.", False),
    "V2d1": ("s", 5, SIDE_TRACK + "The white car races up the steep ramp extremely fast and launches off its upper end "
             "into the air above the river.", False),
    "V2d2": ("n", 5, "Extreme slow motion: the car hangs almost motionless in mid-air, drifting very slightly forward; "
             "the girl grins and her hair strands and jacket flutter; droplets and dust hang in the air. The camera is "
             "nearly still, a slight slow drift. Her face keeps the first frame's angle.", True),
    "V2e1": ("s", 4, SIDE_TRACK + "The car slams down onto the road, suspension bottoming out, a burst of white sparks; "
             "the car bounces once and races off to the right. The camera shakes with the impact.", False),
    "V2e2": ("n", 4, "Camera fixed inside the car. She exhales a breathless laugh, shoulders dropping, then glances up at "
             "the rearview mirror. Streetlights streak past outside. Her face keeps the first frame's angle.", True),
    "V2e3": ("s", 5, SIDE_TRACK + "The white car races away to the right extremely fast; behind it the black sedans fly "
             "off the bridge one after another and slam down onto the road with sparks, still chasing.", False),
    "V2f1": ("s", 5, SIDE_TRACK + "The river of black sedans surges forward to the right, more and more of them, their "
             "roof strobes flashing in waves rippling through the pack.", False),
    "V2f2": ("n", 6, "Camera fixed; the mirror shakes slightly with the road. Her eyes in the mirror glance and narrow; in "
             "the mirror the black sedans' strobes flash and pulse and the swarm draws closer.", True),
    "V2g1": ("s", 4, "The L train car smashes down onto the road directly ahead extremely fast, debris and sparks "
             "exploding toward the camera; the camera lurches forward into the impact.", False),
    "V2h1": ("n", 4, SIDE_TRACK + "The colored motes swirl into her and vanish as she launches out of her crouch into an "
             "extremely fast sprint to the right.", True),
    "V2i1": ("n", 6, SIDE_TRACK + "The girl sprints extremely fast to the right along the elevated tracks, legs a blur of "
             "long powerful strides, arms pumping, bun bouncing, staying in the same place in frame while the girders "
             "and buildings scroll past quickly from right to left.", True),
    "V2i2": ("n", 4, SIDE_TRACK + "She slides feet-first extremely fast under the swinging signal arm, which sweeps over "
             "her just inches above, then springs back up into a sprint to the right.", True),
    "V2i3": ("n", 4, "The camera tracks sideways alongside at foot level. Her sneakers pound the ties extremely fast in a "
             "sprint to the right, splinters flying.", True),
    "V2i4": ("n", 4, SIDE_TRACK + "She dashes through the air extremely fast to the right, the orange and blue streak "
             "stretching behind her, then begins to arc down toward the park.", True),
    "V2j1": ("n", 6, "Straight top-down camera looking straight down, slowly following her: she zigzags extremely fast "
             "across the lawn, cutting left and right sharply; the agents converge toward her from every edge, running.",
             True),
    "V2j2": ("n", 4, "Straight top-down camera, fixed. The two agents dive; she cuts away sideways extremely fast; the two "
             "agents collide with each other and tumble on the grass.", True),
    "V2k1": ("n", 5, "The camera tracks with her at ground level from just behind her shoulder. She runs extremely fast, "
             "looking back over her shoulder; the agents behind chase her, getting closer.", True),
    "V2k2": ("n", 5, SIDE_TRACK + "She sprints extremely fast to the right; the agents behind run after her, gaining.",
             True),
    "V2k3": ("n", 4, SIDE_TRACK + "She sprints extremely fast, her head snapping toward the agent who runs effortlessly "
             "beside her, keeping pace.", True),
    "V2l1": ("n", 4, "Straight top-down fixed camera: the ring of agents steps inward in unison, closing tighter around "
             "her; she turns, looking for a way out.", True),
    "V2l2": ("n", 4, "Camera fixed, shallow focus. The agent draws the pistol from his jacket and levels it low at body "
             "height, pointing at her torso. Slow and deliberate.", True),
    "V2m1": ("n", 4, "Camera fixed. She is struck in the side and recoils, her body bending; the orange and blue motes "
             "burst outward from the impact point and swirl in the air.", True),
    "V2n1": ("n", 4, "Camera fixed. Her hand slams down hard on the big round arcade button; the button presses in; the "
             "panel shakes.", True),
}


def register(clip, kf=None, last=None, prompt=None, duration=None):
    k, dur, p, girl = C[clip]
    kf = kf or k
    cands = [c for c in glob.glob(os.path.join(ROOT, f"media/shots/{clip}/kf_{kf}.*")) if "_raw" not in c]
    assert len(cands) == 1, (clip, kf, cands)
    img = os.path.relpath(cands[0], ROOT)
    vgen.SHOTS[clip] = dict(model=SD20, image=img, duration=duration or dur, camera_fixed=False,
                            prompt=(prompt or p) + " " + (KEEP if girl else KEEP_NOGIRL), last=last)


_orig_build = vgen.build_spec


def _build(shot, res, note="", over=None):
    spec = _orig_build(shot, res, note, over)
    last = vgen.SHOTS[shot].get("last")
    if last:
        spec["input"]["last_frame_image"] = "file:" + os.path.relpath(vgen.gen.ref_image(os.path.join(ROOT, last)), ROOT)
    return spec


vgen.build_spec = _build


def link(clips):
    for clip in clips:
        for mp4 in sorted(glob.glob(os.path.join(ROOT, "media/gen", clip, "take_*.mp4"))):
            for src in (mp4, mp4[:-4] + "_sheet.jpg"):
                dst = os.path.join(ROOT, "media/shots", clip, os.path.basename(src))
                if os.path.exists(src) and not os.path.exists(dst):
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    os.link(src, dst)


if __name__ == "__main__":
    cmd = sys.argv[1]
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    opts = {a[2:].partition("=")[0]: a[2:].partition("=")[2] or True for a in sys.argv[2:] if a.startswith("--")}
    if cmd == "submit":
        for a in args:
            clip, _, kf = a.partition(":")
            register(clip, kf or None, opts.get("last"), opts.get("prompt"), int(opts["duration"]) if "duration" in opts else None)
            for j in vgen.submit(clip, opts.get("res", "720p"), int(opts.get("takes", 1)), "dry-run" in opts,
                                 opts.get("note", "")):
                print(clip, j)
        print(f"spend so far (est): ${vgen.spend_total()}")
    elif cmd in ("collect", "wait"):
        clips = args or sorted(C)
        for c in clips:
            vgen.SHOTS.setdefault(c, {})
        import time
        t0 = time.time()
        while True:
            p = vgen.collect(clips)
            link(clips)
            if cmd == "collect" or not p or time.time() - t0 > float(opts.get("timeout", 3600)):
                print("pending:", p)
                break
            time.sleep(30)
    elif cmd == "link":
        link(args or sorted(C))
