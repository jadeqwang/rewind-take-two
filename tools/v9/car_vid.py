#!/usr/bin/env python3
"""v9 fix 1a + 9: Seedance 2.0 takes for the re-staged P2 (0:38.90) and P1/P1b (0:37.96, 0:39.68).

Keyframes from tools/v9/car_kf.py (they carry D7's 0:35 staging: Seedance 2.0 cannot take reference images together
with a first frame, so the D7 context goes in through the keyframe).

    PY=~/Documents/1-music-shipped/moongazing/.venv/bin/python
    $PY tools/v9/car_vid.py submit v9_1a_P2 v9_9_P1 [--dry-run]
    $PY tools/v9/car_vid.py wait v9_1a_P2 v9_9_P1

Job dirs are media/gen/<NAME>/ (the name is the spend tag); finished takes are copied to media/shots/P2|P1/ as
take_v9_<N>.mp4 (new names: the engine caches by path).
"""
import glob
import os
import shutil
import sys
import time

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/sectionA"))
import vid  # noqa: E402,F401  (registers section A's shots and the last-frame hook on vgen)
from vid import SD20, LOOK, vgen  # noqa: E402

V9 = {
    "v9_1a_P2": dict(image="media/shots/P2/kf_v9d.png", duration=4, camera_fixed=True, prompt=(
        "Night. The girl sits in the driver's seat of the parked car, frozen in sudden shock, staring straight at us: "
        "her wide eyes stay wide, a small quick intake of breath, her shoulders tense up and her fingers tighten on the "
        "steering wheel and on the door sill; then she holds perfectly still. Her head stays in the same place and "
        "angle; her two crossed pencils, her bun, her headphones and her jacket do not change. The car does not move, "
        "the steering wheel does not move. Static locked-off camera. " + LOOK)),
    "v9_9_P1": dict(image="media/shots/P1/kf_v9a.jpg", duration=4, camera_fixed=True, prompt=(
        "Night. The agent's right hand slides smoothly inside his black suit jacket toward the holster, the lapel "
        "lifting; his blank face and sunglasses do not change. Behind him, the girl stays seated in the driver's seat "
        "of the parked white car, both hands on the steering wheel, watching him through the open window; she does "
        "not get out and nobody else appears. The car does not move. Static camera. " + LOOK)),
}
DEST = {"v9_1a_P2": "P2", "v9_9_P1": "P1"}

for k, v in V9.items():
    v.setdefault("model", SD20)
vgen.SHOTS.update(V9)


def link(shots):
    for s in shots:
        dst = os.path.join(ROOT, "media/shots", DEST[s])
        for f in sorted(glob.glob(os.path.join(ROOT, "media/gen", s, "take_*.mp4"))):
            n = os.path.basename(f)[5:-4]
            for src, t in ((f, f"take_v9_{n}.mp4"), (f.replace(".mp4", "_sheet.jpg"), f"take_v9_{n}_sheet.jpg")):
                if os.path.exists(src) and not os.path.exists(os.path.join(dst, t)):
                    shutil.copy2(src, os.path.join(dst, t))
                    print("->", os.path.join("media/shots", DEST[s], t))


if __name__ == "__main__":
    cmd = sys.argv[1]
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    opts = {a[2:].partition("=")[0]: a[2:].partition("=")[2] or True for a in sys.argv[2:] if a.startswith("--")}
    if cmd == "submit":
        for s in args:
            for j in vgen.submit(s, opts.get("res", "720p"), int(opts.get("takes", 1)), "dry-run" in opts, opts.get("note", "")):
                print(s, j)
        print("spend so far (est):", vgen.spend_total())
    elif cmd == "wait":
        t0 = time.time()
        while True:
            p = vgen.collect(args)
            if not p or time.time() - t0 > float(opts.get("timeout", 3000)):
                print("pending:", p)
                break
            time.sleep(30)
        link(args)
    elif cmd == "link":
        link(args)
