#!/usr/bin/env python3
"""Section A video takes for the v3 revision pass (stream V1A), on top of tools/gen/vgen.py.

    $PY tools/sectionA/vid_v3.py submit C1 D3 ... [--dry-run]
    $PY tools/sectionA/vid_v3.py wait C1 D3 ...     # collect, then copy to media/shots/<SHOT>/take_<N>.mp4

Job dirs are media/gen/revA_v1a_<KEY>/ (so the spend tag is revA_v1a_<KEY>). Each entry names the shot folder and the
take number it lands on, beside the v2 takes (never over them).
"""
import os
import shutil
import sys
import time

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
import vgen  # noqa: E402

SD20 = "bytedance/seedance-2.0"
LOOK = ("Keep the exact drawing style of the first frame throughout: black-and-white wood engraving world, only the "
        "anime girl in color. No text, no letters, no subtitles, no logos, no watermark.")
LOOK_W = ("Keep the exact drawing style of the first frame throughout: a black-and-white wood engraving, no color at all. "
          "No new people or characters appear; only what is in the first frame. No text, no letters, no subtitles, no "
          "logos, no watermark.")
FACE = ("Her face stays exactly as in the first frame: forehead smooth, brows relaxed, head keeps the first frame's "
        "angle, never a face close-up.")
PENCILS = ("The two crossed yellow pencils in her hair bun stay exactly as in the first frame: two straight pencils, "
           "never bending, never multiplying, never disappearing.")

V3 = {
    "C1": dict(dst=("C1", 3), image="media/shots/C1/kf_v3_c.jpg", duration=4, camera_fixed=False, prompt=(
        "Time is frozen. Nothing moves except a few loose strands of the girl's hair drifting slowly and the small "
        "glowing orange and blue motes drifting very slowly in the air, like dust in still light. The girl, the white "
        "starburst muzzle flash at the centre pistol and the agents stay perfectly still, a paused frame. There is no "
        "bullet anywhere. Camera: very slow smooth push-in toward the girl. "
        f"{PENCILS} {FACE} {LOOK}")),
    "C4": dict(dst=("C4", 3), image="media/shots/C4/kf_v3_a.jpg", duration=4, camera_fixed=False, prompt=(
        "Night drive. The girl drives calmly, eyes on the road, hands steady on the wheel. Pools of white streetlight "
        "sweep across her, the dashboard and the dissertation on the seat, front to back, rhythmically; the car sways "
        "very slightly. The blank sticky note on the dissertation stays blank and still. Camera locked to the car, no "
        f"camera move. {PENCILS} {FACE} {LOOK}")),
    "D2": dict(dst=("D2", 2), image="media/shots/D2/kf_v3_d.jpg", duration=4, camera_fixed=False, prompt=(
        "Night, inside the slowly moving car. Outside the window the engraved city glides past slowly from right to "
        "left: the big rooftop billboard ringed with glowing bulbs drifts slowly toward the middle of the window and "
        "stays completely inside the window, fully visible, for the whole shot; its two pale panels stay blank, flat "
        "and evenly lit; the bulbs around it twinkle. The girl in the foreground stays still, looking out, a few hair "
        f"strands stirring. Camera locked to the car. {PENCILS} {LOOK}")),
    "D3": dict(dst=("D3", 2), image="media/shots/D3/kf_v3_c.jpg", duration=5, camera_fixed=True, prompt=(
        "Night, inside the moving car. In the rearview mirror the unlit black sedan follows steadily, staying the same "
        "distance behind, the road unrolling behind it; passing streetlights flicker across the mirror. The girl's eyes "
        "flick up to the mirror and hold there, wary; she does not turn her head. Static camera locked to the car. "
        f"{PENCILS} {FACE} {LOOK}")),
    "D4": dict(dst=("D4", 2), image="media/shots/D4/kf_v3_b.png", duration=4, camera_fixed=True, prompt=(
        "Night on the lakeshore road. The white car has just stopped on the gravel shoulder beside the guardrail and "
        "settles on its suspension. Directly behind it the black sedan rolls forward the last metre and stops; its "
        "headlight starbursts swell brighter, their long rays sweeping across the white car and the frame. Behind the "
        "windshield the girl glances up at her rearview mirror, uneasy, hands on the wheel. Waves roll in on the lake. "
        f"Both cars stay on the shoulder, one behind the other; no other cars. Static low camera, no camera move. {LOOK}")),
    "D5cu": dict(dst=("D5", 2), image="media/shots/D5/kf_v3_cu.jpg", duration=4, camera_fixed=False, prompt=(
        "Night, extreme close-up. The agent is walking steadily toward the camera: his head rises and dips gently with "
        "each footstep in a slow regular walking rhythm, about two steps per second, the big black sunglasses staying "
        "large and centred in frame. His face is blank and does not change. The two lenses stay flat, solid pure black "
        "and completely empty the whole time: no reflections, no highlights, no shapes inside them. The headlight glare "
        "behind his head flickers slightly. The camera moves backward at his walking pace, keeping the same tight "
        f"framing. {LOOK_W}")),
    "D5w": dict(dst=("D5", 3), image="media/shots/D5/kf_v3_w.jpg", duration=4, camera_fixed=False, prompt=(
        "Night on the lakeshore road. The three agents walk steadily toward the camera in perfect step, perfectly in "
        "sync, backlit by the blazing headlights of the parked black sedan behind them; their long shadows stretch "
        "toward us across the gravel; faces blank, sunglasses black. The sedan stays parked. Waves roll in on the lake. "
        "Camera: slow steady dolly back at their walking pace, keeping the centre agent large and centred. " + LOOK_W)),
    # C4 again: the roundel was on her right (near) sleeve; canon is her left sleeve, so the near sleeve is plain
    "C4b": dict(dst=("C4", 4), image="media/shots/C4/kf_v3_b.jpg", duration=4, camera_fixed=False, prompt=(
        "Night drive. The girl drives calmly, eyes on the road, hands steady on the wheel. Pools of white streetlight "
        "sweep across her, the dashboard and the dissertation on the seat, front to back, rhythmically; the car sways "
        "very slightly. The blank sticky note on the dissertation stays blank and still. Her jacket sleeve stays plain "
        "white with one orange band, no patch on it. Camera locked to the car, no camera move. "
        f"{PENCILS} {FACE} {LOOK}")),
}

for k, v in V3.items():
    spec = {kk: vv for kk, vv in v.items() if kk != "dst"}
    spec.setdefault("model", SD20)
    vgen.SHOTS["revA_v1a_" + k] = spec


def link(keys):
    for k in keys:
        shot, n = V3[k]["dst"]
        src = os.path.join(ROOT, "media/gen", "revA_v1a_" + k, "take_1.mp4")
        dst = os.path.join(ROOT, "media/shots", shot, f"take_{n}.mp4")
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)
            sh = src.replace(".mp4", "_sheet.jpg")
            if os.path.exists(sh):
                shutil.copy2(sh, dst.replace(".mp4", "_sheet.jpg"))
            print("linked", dst)


if __name__ == "__main__":
    cmd = sys.argv[1]
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    names = ["revA_v1a_" + a for a in args]
    if cmd == "submit":
        for s in names:
            for j in vgen.submit(s, "720p", 1, "--dry-run" in sys.argv, "v3 revision"):
                print(s, j)
        print("spend so far (est):", vgen.spend_total())
    elif cmd == "wait":
        t0 = time.time()
        while True:
            p = vgen.collect(names)
            if not p or time.time() - t0 > 1500:
                print("pending:", p)
                break
            time.sleep(30)
        link(args)
    elif cmd == "link":
        link(args)
