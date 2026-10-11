#!/usr/bin/env python3
"""v4 co-op level (C1, C2 at 129.18-134.88): keyframes, Seedance takes, engrave. Plan: docs/revisions/v4/plans/coop.md
Patterned on tools/sections/B/rb.py; spend tag prefix v4B_coop_. Media: media/shots/C_coop/ (+ NOTES.md there).

    PY=~/Documents/moongazing/.venv/bin/python
    $PY tools/v4B/coop/gen.py kf NAME [--v=2] [--dry-run]                 # nano-banana-pro keyframe -> kf_<NAME>_v<N>.png
    $PY tools/v4B/coop/gen.py edit NAME SRC "instruction" [--v=2] [REF ...]   # nano edit of an existing image
    $PY tools/v4B/coop/gen.py submit TAKE [--kf=NAME:v] [--res=720p] [--dry-run]
    $PY tools/v4B/coop/gen.py wait|collect [TAKE ...]
    $PY tools/v4B/coop/gen.py engrave TAKE:N
"""
import glob
import os
import subprocess
import sys
import time

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
sys.path.insert(0, os.path.join(ROOT, "tools/sectionC"))
sys.path.insert(0, os.path.join(ROOT, "tools/sections/B"))
import cf  # noqa: E402
import vgen  # noqa: E402
from common import inp_for, trim_margins  # noqa: E402
import prompts as P  # noqa: E402  (rev-B prompt blocks: DAY, SIDE, STYLE, AGENTS, LOCK, JREF)

OUT = os.path.join(ROOT, "media/shots/C_coop")
NANO = "google/nano-banana-pro"
SD20 = "bytedance/seedance-2.0"
TAG = "v4B_coop_"

# ---------------------------------------------------------------------------------------------------------- prompts
# Jade (v4, verbatim): "BLUE has white jacket with blue stripes, blue straps hanging from pants, and blue dots, and
# ORANGE has white jacket with orange stripes, orange straps, and orange dots." ORANGE is always the copy further LEFT.
# kf_c1 v1/v2 asked the image model to colour BLUE itself: the costumes drifted (no chest band) and the view came out
# in perspective with the pencil off the girls' path. From v3: the twins are generated identical in the canon outfit
# (rev-B's TWINS + JADE blocks), the composition comes from a flat layout sketch (layout.py), and BLUE is recoloured
# by recolor.py (keyframe before the take, every frame after the engrave).
LAYOUT = ("Redraw the attached LAYOUT SKETCH (the flat diagram of two tables, a pencil, two dome buttons and blocky "
          "mannequins) as a finished picture. Keep its composition EXACTLY: the same flat orthographic side elevation "
          "with NO perspective at all, the camera exactly level with the table top, so that each table is seen purely "
          "edge-on as a horizontal slab on legs and NONE of its upper surface is visible; the same positions and sizes "
          "of the two tables, of the empty gap between them, of the pencil lying across the gap on top of the two "
          "tables, of the two dome buttons standing on the table tops, and of the figures. The feet of the figures, "
          "the underside of the pencil and the bases of the buttons all sit on the same single horizontal line, the "
          "table top. The mannequins only mark where each person is, which way they face and their pose: draw the "
          "real characters there instead. Do not add a floor plane, do not tilt the camera, do not add depth to the "
          "tables. The two tables are completely separate; nothing connects them except the pencil. ")
SET = ("The place is the world of M.C. Escher's woodcut 'Still Life and Street', where a wooden table top is also a "
       "street, drawn as one screen of a 2D side-scrolling platformer. Two wooden tables seen exactly edge-on: each a "
       "thick horizontal slab of planks on square legs. The left table runs from the left edge of the frame to about "
       "36% across and ends in a sheer vertical edge; the right table begins at about 64% across and runs out of the "
       "right edge; between them is a wide empty gap, a drop that falls out of the bottom of the frame, dark with "
       "hatching low down. ONE enormous wooden pencil lies perfectly horizontal across the gap like a plank bridge, "
       "resting on the two table tops: its blunt end with the ribbed metal ferrule and the rubber eraser sits on the "
       "edge of the left table, its long six-sided shaft spans the gap, and its sharpened point rests on the edge of "
       "the right table. The pencil is about as thick as the girl's forearm is long, and it is engraved in black and "
       "white like the rest of the world, not colored. On each table top stands ONE large round push-button like a "
       "giant arcade button or desk bell: a smooth dome on a low round collar, about half as wide as the girl is tall "
       "and knee-high to her, engraved in black and white: one on the left table at about 15% across the frame, one on "
       "the right table at about 85% across. Behind, at the far left and the far right, enormous blank hardbound "
       "books as tall as buildings lean against brick house fronts; open paper-white sky in the middle. ")
STYLE = ("Rendered as an M.C. Escher wood engraving / lithograph: crisp black ink lines on warm off-white paper, dense "
         "precise parallel hatching and cross-hatching that follows form, high contrast, no gray wash, no color "
         "anywhere except the two girls: the tables, the pencil, the buttons, the books and the buildings are strictly "
         "black and white. No red anywhere. The girls are full-color anime characters (clean cel shading) exactly "
         "matching the character reference sheet. Full bleed, edge to edge, no border, no margin, no paper edge, no "
         "frame, 16:9. No text, no letters, no numbers, no signature, no watermark.")
L1, L2 = "media/shots/C_coop/layout_c1.png", "media/shots/C_coop/layout_c2.png"

KF = {
    # C1 first frame: both on the left table, running in; the one ahead (right) becomes BLUE, the one behind ORANGE
    "c1": dict(refs=[L1, P.JREF], prompt=P.DAY + LAYOUT + P.TWINS + SET + (
        "Both copies of the girl are on the left table, sprinting to the right, full figures in profile, each about "
        "31% of the frame height, with clear empty space between them: the first copy at about 7% across the frame, "
        "just inside the left edge; the second copy at about 26% across, a few strides ahead of her, nearer the gap. "
        "Nobody else in the picture. ") + P.JADE + STYLE),
    # C2 first frame: one crouched on each button (left = ORANGE, right = BLUE), agents arriving at the left edge
    "c2": dict(refs=[L2, P.JREF, P.AGENT], prompt=P.DAY + LAYOUT + P.TWINS + SET + (
        "The first copy of the girl crouches low on top of the left button at about 15% across the frame, pressing it "
        "down with both feet and one hand, looking back over her shoulder to the left. The second copy crouches low on "
        "top of the right button at about 85% across, pressing it down with both feet and one hand, looking left "
        "across the gap at the other girl. At the very left edge of the frame two agents are running in toward the "
        "girl on the left button, arms reaching, partly cut off by the frame edge. ") + P.JADE + P.AGENTS + STYLE),
}

KEEP = ("Keep the first frame's look: the world stays a crisp black-and-white Escher-style wood engraving (tables, "
        "pencil, buttons, books, buildings all black and white), only the two identical anime girls in full color, "
        "both in the same outfit (white cropped bomber with an orange band, navy cargo pants with orange straps, orange "
        "headphones around the neck, black hair in a bun with two crossed pencils). Faces keep their shape, never a face "
        "close-up. The giant pencil, the two tables, the two round buttons and the gap stay perfectly still and "
        "unchanged. No text, no letters, no logos.")
MEN = ("men in identical plain black suits, white shirts, thin black ties and black sunglasses, drawn in the same "
       "black-and-white engraving as the world")

# The twins are generated identical; the one further right (BLUE in the cut) is recoloured after the engrave.
VID = {
    # take 1 (kf c1:6) had the girl ahead already standing over the gap in frame 1, so the bridge could not start up;
    # take 2 starts from kf_c1_v8.png, a composite (assets.py) with both girls moved back onto the left table.
    "c1": dict(kf="c1:8", dur=5, prompt=(
        "The girl behind (on the left) runs to the big round button on the left table, jumps onto it with both feet "
        "and drops into a low crouch on top of it, pressing it down with her feet and one hand, and she stays crouched "
        "there on the button, holding it down, for the rest of the shot. The girl ahead (on the right) runs to the very "
        "edge of the left table and stops there with her toes at the edge, balancing, and looks back over her shoulder "
        "at the crouching girl for a moment; then she sprints along the top of the giant pencil across the gap to the "
        "right table and runs on to the right button, where she crouches down on it too. The two girls never touch and "
        "never cross: the girl ahead is always to the right of the other one. No one else appears.")),
    "c2": dict(kf="c2:1", dur=5, prompt=(
        "The girl on the right stays crouched with her hand pressing the right button down, watching. The girl on the "
        "left springs off the left button and sprints to the right as fast as she can, along the top of the giant pencil across the "
        "gap to the right table, just as the agents lunge for her: their hands close on empty air where she was. The "
        "agents run after her only as far as the edge of the left table and stop dead at the edge, arms windmilling, "
        "teetering over the drop; they never step onto the pencil. The running girl reaches the right table and stops "
        "just left of the other girl, never passing her. Then the girl on the right hops up off the button and both "
        "girls sprint away to the right and out of the right edge of the frame. The two girls never touch and never "
        "cross.")),
}


# ---------------------------------------------------------------------------------------------------------- commands
def kf_path(name, v=1):
    return os.path.join(OUT, f"kf_{name}_v{v}.png")


def find_kf(name, v=None):
    c = sorted(p for p in glob.glob(os.path.join(OUT, f"kf_{name}_v{v or '*'}.*")) if "_raw" not in p and not p.endswith(".txt"))
    assert c, f"no keyframe {name} v={v}"
    return c[-1]


def save_prompt(out, model, prompt, refs):
    open(out + ".prompt.txt", "w").write(f"model: {model}\nrefs: {list(refs)}\ntag prefix: {TAG}\n\n{prompt}\n")


def run_kf(name, v=1, dry=False):
    k = KF[name]
    out = kf_path(name, v)
    os.makedirs(OUT, exist_ok=True)
    p = cf.generate(NANO, inp_for(NANO, k["prompt"], k.get("refs", ())), out, tag=f"{TAG}kf_{name}", timeout=600, dry_run=dry)
    if p:
        trim_margins(p[0])
        save_prompt(p[0], NANO, k["prompt"], k.get("refs", ()))
    return p[0] if p else None


def edit(name, src, instruction, v=1, refs=()):
    out = kf_path(name, v)
    os.makedirs(OUT, exist_ok=True)
    p = cf.generate(NANO, inp_for(NANO, instruction, (src, *refs)), out, tag=f"{TAG}edit_{name}", timeout=600)
    trim_margins(p[0])
    save_prompt(p[0], NANO, instruction, (src, *refs))
    return p[0]


def register(take, kf=None):
    t = VID[take]
    name, _, v = (kf or t["kf"]).partition(":")
    img = os.path.relpath(find_kf(name, int(v) if v else None), ROOT)
    vgen.SHOTS["C_coop_" + take] = dict(model=SD20, image=img, duration=t.get("dur", 5), camera_fixed=True,
                                        prompt=P.LOCK + t["prompt"] + " " + KEEP)


_orig_build = vgen.build_spec


def _build(shot, res, note="", over=None):
    spec = _orig_build(shot, res, note, over)
    spec["tag"] = TAG + spec["tag"].replace("C_coop_", "")
    return spec


vgen.build_spec = _build


def link(takes):
    for t in takes:
        for mp4 in sorted(glob.glob(os.path.join(ROOT, "media/gen", "C_coop_" + t, "take_*.mp4"))):
            for src in (mp4, mp4[:-4] + "_sheet.jpg"):
                dst = os.path.join(OUT, t, os.path.basename(src))
                if os.path.exists(src) and not os.path.exists(dst):
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    os.link(src, dst)


def engrave(spec, extra=()):
    take, _, n = spec.partition(":")
    n = n or "1"
    d = os.path.join(OUT, take)
    src, dst = os.path.join(d, f"take_{n}.mp4"), os.path.join(d, f"take_{n}_engraved.mp4")
    if os.path.exists(dst):
        print(f"{take} take_{n}: already engraved")
        return
    free = os.statvfs(ROOT)
    assert free.f_bavail * free.f_frsize > 1.5e9, "under 1.5 GB free"
    cmd = ["flock", os.path.join(ROOT, "media/.engrave.lock"),
           os.path.join(ROOT, "tools/engrave/.venv/bin/python"), os.path.join(ROOT, "tools/engrave/engrave.py"), src, dst,
           "--out-height", "1080", "--matte-out", os.path.join(d, f"take_{n}_matte"), *extra]
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(f"{take} take_{n}: {'ok' if r.returncode == 0 else 'FAILED ' + r.stderr[-800:]} {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    opts = {a[2:].partition("=")[0]: a[2:].partition("=")[2] or True for a in sys.argv[2:] if a.startswith("--")}
    v = int(opts.get("v", 1))
    if cmd == "list":
        print("keyframes:", " ".join(KF), "| takes:", " ".join(VID))
    elif cmd == "kf":
        for n in args:
            print(n, run_kf(n, v, "dry-run" in opts))
    elif cmd == "edit":
        print(edit(args[0], args[1], args[2], v, tuple(args[3:])))
    elif cmd == "submit":
        for t in args:
            register(t, opts.get("kf"))
            for j in vgen.submit("C_coop_" + t, opts.get("res", "720p"), int(opts.get("takes", 1)), "dry-run" in opts):
                print(t, j)
        print(f"project spend so far (est): ${vgen.spend_total()}")
    elif cmd in ("collect", "wait"):
        takes = args or sorted(VID)
        for t in takes:
            vgen.SHOTS.setdefault("C_coop_" + t, {})
        t0 = time.time()
        while True:
            pend = vgen.collect(["C_coop_" + t for t in takes])
            link(takes)
            if cmd == "collect" or not pend or time.time() - t0 > float(opts.get("timeout", 1500)):
                print("pending:", pend)
                break
            time.sleep(30)
    elif cmd == "engrave":
        for a in args:
            engrave(a)
