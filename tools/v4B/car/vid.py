#!/usr/bin/env python3
"""v4 1:30 car shot: a Seedance 2.0 take from the WIDE still, so she and the road move (Jade: "the main weakness is
actually that she's completely still, no hair fidget, no breathing or a bit of expression like a normal person would,
not an exaggerated expression because she's just trying to concentrate").

    PY=~/Documents/moongazing/.venv/bin/python
    $PY tools/v4B/car/vid.py submit v4B_car_wide [--dry-run]
    $PY tools/v4B/car/vid.py wait v4B_car_wide          # collects media/gen/v4B_car_wide/take_N.mp4 -> media/shots/V2f3/take_N.mp4
The shot name is the spend tag. The mirror's fleet stays the engine's animation (tools/v4B/car/car_shot.js).
"""
import glob
import os
import shutil
import sys
import time

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
import vgen  # noqa: E402

FACE = ("Her face stays exactly as in the first frame: same face, same profile, head keeps the first frame's angle, "
        "never a face close-up.")
LOOK = ("Keep the exact drawing style of the first frame throughout: black-and-white wood engraving world, only the "
        "anime girl in color. No text, no letters, no subtitles, no logos, no watermark. No red anywhere.")

SHOTS = {
    "v4B_car_wide": dict(model="bytedance/seedance-2.0", image="media/shots/V2f3/kf_wide_b_fix.jpg", duration=4, camera_fixed=True, prompt=(
        "Night, inside a car driving fast on an expressway. Locked-off camera on the back seat, it does not move. "
        "Through the windshield the road streams toward us: the white lane dashes rush toward the car and pass under "
        "it, the streetlights glide past on both sides, the car sways very slightly with the road. The girl drives, "
        "calm and focused, concentrating on the road: she breathes naturally, her shoulders rising and falling a "
        "little; loose strands of her hair and her curtain bangs beside her face stir slightly; she blinks once or "
        "twice; her eyes flick up to the rear-view mirror for a moment and back to the road; her brow and jaw tighten "
        "very slightly as she concentrates. Her hands stay on the steering wheel and make one small steering "
        "correction. Understated: no smile, mouth closed, no big head turn. The two yellow pencils stay crossed in her "
        "bun exactly as in the first frame. The overhead sign and its gantry stay where they are, far ahead. The "
        "rear-view mirror stays exactly as drawn. " + FACE + " " + LOOK)),
}
DEST = {"v4B_car_wide": "V2f3"}
vgen.SHOTS.update(SHOTS)


def link(shots):
    for s in shots:
        dst = os.path.join(ROOT, "media/shots", DEST[s])
        for f in sorted(glob.glob(os.path.join(ROOT, "media/gen", s, "take_*.mp4"))):
            for src in (f, f.replace(".mp4", "_sheet.jpg")):
                t = os.path.join(dst, os.path.basename(src))
                if os.path.exists(src) and not os.path.exists(t):
                    shutil.copy2(src, t)
                    print("->", os.path.relpath(t, ROOT))


if __name__ == "__main__":
    cmd = sys.argv[1]
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    opts = {a[2:].partition("=")[0]: a[2:].partition("=")[2] or True for a in sys.argv[2:] if a.startswith("--")}
    if cmd == "submit":
        for s in args:
            for j in vgen.submit(s, opts.get("res", "720p"), int(opts.get("takes", 1)), "dry-run" in opts, opts.get("note", "")):
                print(s, j)
    elif cmd == "wait":
        t0 = time.time()
        while True:
            p = vgen.collect(args)
            if not p or time.time() - t0 > float(opts.get("timeout", 1500)):
                print("pending:", p)
                break
            time.sleep(30)
        link(args)
