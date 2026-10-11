#!/usr/bin/env python3
"""Section A video takes on top of tools/gen/vgen.py, without touching the shared tools/gen/shots.py.

    $PY tools/sectionA/vid.py submit A_C3 [A_C4 ...] [--takes=N] [--res=720p] [--dry-run]
    $PY tools/sectionA/vid.py wait A_C3 ...      # collect, then link media/gen/A_X/take_N.mp4 -> media/shots/X/take_N.mp4
    $PY tools/sectionA/vid.py link               # (re)link every finished take

Shot names are A_<SHOT> (job dirs media/gen/A_<SHOT>/). Entries may carry last=<image> (Seedance last_frame_image).
"""
import glob
import os
import shutil
import sys
import time

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
import gen  # noqa: E402
import vgen  # noqa: E402

SD20 = "bytedance/seedance-2.0"
KF = "media/shots/{}/{}"
LOOK = ("Keep the exact drawing style of the first frame throughout: black-and-white wood engraving world, only the "
        "anime girl in color. No text, no letters, no subtitles, no logos, no watermark.")
LOOK_W = ("Keep the exact drawing style of the first frame throughout: a black-and-white wood engraving, no color at all. "
          "No new people or characters appear; only what is in the first frame. No text, no letters, no subtitles, no "
          "logos, no watermark.")
FACE = ("Her face stays exactly as in the first frame: forehead smooth, brows relaxed, head keeps the first frame's "
        "angle, never a face close-up.")

A = {
    "A_C1": dict(image=KF.format("C1", "kf_hero.jpg"), duration=5, camera_fixed=False, prompt=(
        "Time is frozen. Nothing moves except a few loose strands of the girl's hair drifting slowly and the small "
        "glowing orange and blue motes drifting very slowly in the air, like dust in still light. The girl, the bullet, "
        "its wake and the agents stay perfectly still, a paused frame. Camera: very slow smooth push-in toward the "
        f"girl. {FACE} {LOOK}")),
    "A_C3": dict(image=KF.format("C3", "kf_sdr2.jpg"), duration=5, camera_fixed=False, prompt=(
        "Night. Slow steady aerial drift forward over the dark lake toward the skyline. The tiny white car glides along "
        "the curving lakeside drive, its headlights moving; the lake ripples shimmer gently; city windows twinkle. "
        f"Camera: slow smooth push-in, no cuts. {LOOK_W}")),
    "A_C4": dict(image=KF.format("C4", "kf_sdr1f.jpg"), duration=4, camera_fixed=False, prompt=(
        "Night drive. The girl drives calmly, eyes on the road, hands steady on the wheel, one slow blink. Pools of "
        "white streetlight sweep across her, the dashboard and the dissertation on the seat, front to back, "
        "rhythmically; the car sways very slightly. Camera locked to the car, no camera move. "
        f"{FACE} {LOOK}")),
    "A_S2": dict(image=KF.format("S2", "kf_nbp1.jpg"), duration=4, camera_fixed=False, prompt=(
        "Night. The white car speeds along the curving lakeside drive; the camera swoops down and forward toward it, "
        "fast smooth push-in, the car stays centered while streetlights slide past. " + LOOK_W)),
    "A_D1": dict(image=KF.format("D1", "kf_sdr1.jpg"), duration=4, camera_fixed=False, prompt=(
        "Night. Chase camera following close behind the white car at high speed, extremely fast. The overhead sign "
        "gantry with its two blank panels rushes toward the camera and passes overhead, leaving the top of the frame; "
        "streetlights stream past on both sides; the road lines rush under the car. The camera keeps the same distance "
        "behind the car. " + LOOK_W)),
    "A_D2": dict(image=KF.format("D2", "kf_sdr1.jpg"), duration=4, camera_fixed=False, prompt=(
        "Night, inside the moving car. Outside the passenger window the engraved city slides past from right to left at "
        "speed; the rooftop sign with its ring of glowing bulbs passes by. The girl in the foreground stays still, "
        "looking out, a few hair strands stirring. Camera locked to the car. " + LOOK)),
    "A_D4": dict(image=KF.format("D4", "kf_nbp1.png"), duration=4, camera_fixed=True, prompt=(
        "Night. The white car rolls slowly to a stop on the gravel shoulder; the black sedan behind it glides in and "
        "stops; its headlight starbursts swell brighter and their rays wash across the frame. Static low camera, no "
        "camera move. " + LOOK)),
    "A_P2": dict(image=KF.format("P2", "kf_sdr1.jpg"), duration=4, camera_fixed=True, prompt=(
        "Her eyes widen in sudden shock, a small quick intake of breath, shoulders tense up; then she freezes. Static "
        f"locked-off camera. {FACE} {LOOK}")),
    "A_P4": dict(image=KF.format("P4", "kf_torso1.jpg"), duration=4, camera_fixed=True, prompt=(
        "Extremely fast: the cloud of glowing orange and sky-blue square motes bursts outward from her side, more and "
        "more of her torso dissolving into motes that fly outward toward the camera, then everything slows down and the "
        "motes hang suspended in the air. No blood. Static camera. " + LOOK)),
    "A_D3": dict(image=KF.format("D3", "kf_sdr3.jpg"), duration=5, camera_fixed=True, prompt=(
        "Night, inside the moving car. In the rearview mirror the unlit black sedan follows steadily, staying the same "
        "distance behind, the road unrolling behind it; passing streetlights flicker across the mirror. The girl's eyes "
        "flick up to the mirror and hold there, wary; she does not turn her head. Static camera locked to the car. "
        f"{FACE} {LOOK}")),
    "A_D5": dict(image=KF.format("D5", "kf_sdr1.jpg"), duration=4, camera_fixed=False, prompt=(
        "Night. The three agents walk slowly toward the camera in perfect step, perfectly in sync, backlit by the blazing "
        "headlights; their long shadows stretch toward us; ties and jackets still, faces blank. Camera: slow steady "
        "dolly back, keeping the center agent large. " + LOOK_W)),
    "A_D6": dict(image=KF.format("D6", "kf_sdr1.jpg"), duration=4, camera_fixed=True, prompt=(
        "Night. The agent at the car window leans in and holds the brass residue meter out toward the girl; its needle "
        "starts twitching and ticking upward in small jerks. The second agent stands still behind him. The girl stays "
        f"still, looking up at them. Static camera. {FACE} {LOOK}")),
    "A_D7": dict(image=KF.format("D7", "kf_nbp1.jpg"), duration=4, camera_fixed=True, prompt=(
        "Her hands raise the colored ID card a little and hold it out steadily toward the car window, the card staying "
        "flat and facing the camera, fingers adjusting their grip. Slow, careful motion. Static camera. " + LOOK)),
    "A_D8": dict(image=KF.format("D8", "kf_nbp1.jpg"), duration=4, camera_fixed=True, prompt=(
        "Night. The agent holds the small ID card perfectly still; the card and the tiny portrait on it stay exactly as "
        "in the first frame, unchanged. Faint orange and sky-blue motes drift up off the card. In his other hand the "
        "brass meter's needle swings hard to the far right end of the dial and quivers there. His head tilts slowly to "
        "one side, uncanny. Static camera. Keep the exact drawing style of the first frame throughout: black-and-white "
        "wood engraving; no new people or characters appear. No text, no letters, no subtitles, no logos.")),
    "A_P1": dict(image=KF.format("P1", "kf_sdr1.jpg"), duration=4, camera_fixed=True, prompt=(
        "Night. The agent's hand slides smoothly inside his black suit jacket toward the holster, the lapel lifting; his "
        "blank face does not change. Static camera. " + LOOK_W)),
    "A_P3": dict(image=KF.format("P3", "kf_sdr1.jpg"), duration=4, camera_fixed=True, prompt=(
        "Night. The agent's pistol rises quickly into frame and levels at the girl's body through the open car window, "
        "aimed low at her torso, then holds steady. The other agents stay still. Static camera. " + LOOK)),
}

for k, v in A.items():
    v.setdefault("model", SD20)
vgen.SHOTS.update(A)

_orig_build = vgen.build_spec


def build_spec(shot, res, note="", over=None):
    spec = _orig_build(shot, res, note, over)
    last = A.get(shot, {}).get("last")
    if last:
        spec["input"]["last_frame_image"] = "file:" + os.path.relpath(gen.ref_image(os.path.join(ROOT, last)), ROOT)
    return spec


vgen.build_spec = build_spec


def link(shots=None):
    for d in sorted(glob.glob(os.path.join(ROOT, "media/gen/A_*"))):
        shot = os.path.basename(d)
        if shots and shot not in shots:
            continue
        dst = os.path.join(ROOT, "media/shots", shot[2:])
        os.makedirs(dst, exist_ok=True)
        for f in glob.glob(os.path.join(d, "take_*.mp4")) + glob.glob(os.path.join(d, "take_*_sheet.jpg")):
            t = os.path.join(dst, os.path.basename(f))
            if not os.path.exists(t):
                try:
                    os.link(f, t)
                except OSError:
                    shutil.copy2(f, t)


if __name__ == "__main__":
    cmd = sys.argv[1]
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    opts = {a[2:].partition("=")[0]: a[2:].partition("=")[2] or True for a in sys.argv[2:] if a.startswith("--")}
    if cmd == "submit":
        for s in args:
            for j in vgen.submit(s, opts.get("res", "720p"), int(opts.get("takes", 1)), "dry-run" in opts,
                                 opts.get("note", "")):
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
    elif cmd == "collect":
        print("pending:", vgen.collect(args))
        link(args)
    elif cmd == "link":
        link(args or None)
