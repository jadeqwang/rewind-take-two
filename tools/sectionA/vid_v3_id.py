#!/usr/bin/env python3
"""v3 revision, stream V1B: Seedance takes for the restaged ID shots (D7 0:35, D8 0:37).

    $PY tools/sectionA/vid_v3_id.py submit revA_v1b_D7 revA_v1b_D8 [--dry-run]
    $PY tools/sectionA/vid_v3_id.py wait revA_v1b_D7 revA_v1b_D8     # collect, then copy beside the v2 takes
    (also revA_v1b_D6 and revA_v1b_P2: follow-ups for the two-pencil canon and the D6/D7/D8 geography)

Job dirs are media/gen/revA_v1b_<SHOT>/ (the shot name is the spend tag). Finished takes are copied to
media/shots/D7/take_<2+>.mp4 and media/shots/D8/take_<3+>.mp4, beside the v2 takes, never over them.
"""
import glob
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vid  # noqa: E402  (registers section A's shots and the last-frame hook on vgen)
from vid import ROOT, SD20, FACE, LOOK, vgen  # noqa: E402

V3 = {
    # D7 is generated as the action in REVERSE (she puts the card away) and played backward by the engine, so the shot
    # is "she reaches into her jacket, draws the card out and holds it up", ending exactly on the keyframe.
    "revA_v1b_D7": dict(image="media/shots/D7/kf_v3_2.jpg", duration=4, camera_fixed=True, prompt=(
        "Night. For the first second she holds the ID card perfectly still, out of the car window toward the camera. "
        "Then, slowly and smoothly, she draws her arm back in through the window, bringing the card to her chest, and "
        "slips the card into the inside pocket of her open jacket, which her other hand holds open; her hand stays "
        "inside the jacket. The card's printed face (the small portrait photo and the solid black bars) stays exactly "
        "as drawn in the first frame for as long as it is visible; nothing on the card changes. Her eyes follow her "
        f"hand down. Her two crossed pencils and her bun do not change. The car does not move. Static camera. {FACE} {LOOK}")),
    "revA_v1b_D8": dict(image="media/shots/D8/kf_v3_2.jpg", duration=4, camera_fixed=True, prompt=(
        "Night. The agent holds the small plastic card perfectly still at chest height with its plain blank back "
        "toward the camera; the card never turns, never flips and never shows its other side: it stays exactly as in "
        "the first frame. Small glowing orange and sky-blue square motes keep drifting up off the card and fading. He "
        "slowly tilts his head to one side while looking down at the card, uncanny and blank. In his other hand the "
        "meter's needle suddenly whips clockwise, slams against the end of the dial and quivers there, pinned at "
        "maximum. Static camera. Keep the exact drawing style of the first frame throughout: black-and-white wood "
        "engraving, the only color is the card's pale-blue stripe and the motes; no new people or characters appear. "
        "No text, no letters, no subtitles, no logos, no watermark.")),
    # follow-ups asked by rev-A: D6 restaged to share one geography with D7/D8 (and two pencils); P2 with two pencils
    "revA_v1b_D6": dict(image="media/shots/D6/kf_v3_2.jpg", duration=4, camera_fixed=True, prompt=(
        "Night. The agent at the driver's window leans in a little and holds the meter closer to the girl; its needle "
        "starts twitching and ticking upward in small jerks. The second agent stands perfectly still. The girl keeps "
        "both hands on the steering wheel and stays still, looking up at the agent, wary; her two crossed pencils and "
        "her bun do not change. Nobody holds a card. The car does not move. Static camera. "
        f"{FACE} {LOOK}")),
    "revA_v1b_P2": dict(image="media/shots/P2/kf_v3_1.jpg", duration=4, camera_fixed=True, prompt=(
        "Her eyes widen in sudden shock, a small quick intake of breath, shoulders tense up; then she freezes. Her two "
        "crossed pencils and her bun do not change. Static locked-off camera. "
        f"{FACE} {LOOK}")),
}
DEST = {"revA_v1b_D7": ("D7", 2), "revA_v1b_D8": ("D8", 3), "revA_v1b_D6": ("D6", 2), "revA_v1b_P2": ("P2", 2)}   # (shot folder, first free take number there)

for k, v in V3.items():
    v.setdefault("model", SD20)
vgen.SHOTS.update(V3)


def link(shots):
    for s in shots:
        folder, first = DEST[s]
        dst = os.path.join(ROOT, "media/shots", folder)
        for f in sorted(glob.glob(os.path.join(ROOT, "media/gen", s, "take_*.mp4"))):
            n = int(os.path.basename(f)[5:-4]) - 1 + first
            for src, t in ((f, f"take_{n}.mp4"), (f.replace(".mp4", "_sheet.jpg"), f"take_{n}_sheet.jpg")):
                if os.path.exists(src) and not os.path.exists(os.path.join(dst, t)):
                    shutil.copy2(src, os.path.join(dst, t))
                    print("->", os.path.join("media/shots", folder, t))


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
