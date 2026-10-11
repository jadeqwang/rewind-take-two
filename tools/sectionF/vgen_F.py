"""Section F video takes: injects section-F shots into tools/gen/vgen.py (without editing the shared shots.py) and adds
last_frame_image support for Seedance 2.0.

    $PY tools/sectionF/vgen_F.py submit F1 F2 ... [--takes=1] [--res=720p] [--dry-run]
    $PY tools/sectionF/vgen_F.py wait F1 F2 ...
Takes land in media/gen/<SHOT>/take_N.mp4 (vgen convention) and are linked into media/shots/<SHOT>/ by link().
"""
import os
import sys

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
import gen  # noqa: E402
import vgen  # noqa: E402

SD20 = "bytedance/seedance-2.0"
LOOK = ("Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, "
        "the girl in clean anime cel shading. No text, no letters, no logos, no watermark.")
FACE = "Her face keeps the first frame's design, forehead smooth, brows relaxed, never a face close-up."
K = "media/shots/"

F = {
    "F1": (K + "F1/kf_1.jpg", 5, "Extremely fast: the girl sprints straight toward the camera along the elevated tracks, closing "
           "the distance until she fills the frame from the knees up, long hair streaming behind her, pencil in her hand. "
           "Behind her the giant wave of color curls and crashes forward over the skyline, rolling after her. The camera "
           "pulls back quickly ahead of her, low to the tracks. " + FACE),
    "F2": (K + "F2/kf_2.jpg", 5, "Extremely fast: the girl runs straight up the vertical face of the skyscraper toward its top, "
           "her pencil dragging a glowing colored line along the wall behind her, the two translucent ghost copies running "
           "alongside in step. The camera rushes upward with them, looking up the tower."),
    "F3": (K + "F3/kf_2.jpg", 5, "Extremely fast: the girl sprints along the underside of the staircase, upside down, hair "
           "streaming; the black-suited agents lose their footing and tumble away, falling in different directions. The "
           "camera slowly rolls, rotating the whole impossible hall."),
    "F4": (K + "F4/kf_1.jpg", 5, "Extremely fast: the girl dives straight down toward the mirror-polished Bean; the camera "
           "plunges down right behind her; the Bean and her own reflection rush up to fill the frame until her outstretched "
           "hands touch her reflection."),
    "F5a": (K + "F5a/kf_2.jpg", 5, "Slow motion: the girl rises through the air toward the giant melting clock, winding the "
            "pencil back over her shoulder like a sword about to strike, hair flowing; the clock drips slowly and tiny agents "
            "fall from its edge. The camera pushes in slowly and tilts up. " + FACE),
    "F5b": (K + "F5b/kf_2.jpg", 5, "The colossal melting clock sags further over the skyline; thick drips of black ink stretch "
            "and fall from its lower edge and turn into black-suited agents tumbling down onto the rooftops; the girl's hair "
            "and jacket blow in the wind. Slow camera push-in toward the clock."),
    "F5c": (K + "F5c/kf_1.jpg", 4, "Tight insert: the melting lip of the giant gold clock sags and stretches; thick black ink drips lengthen "
            "and snap off one after another, each drip turning into a tiny black-suited agent who tumbles down out of frame, arms "
            "flailing; gold flecks drift. Slow camera push-in toward the lip. Static framing otherwise."),
    "F6a": (K + "F6a/kf_2.jpg", 5, "The girl sweeps her pencil in one huge circle above her head, the glowing gold line from its "
            "tip drawing a full loop around the giant clock in the sky; the camera orbits around her fast, in the same "
            "direction as her arm. " + FACE),
    "F6b": (K + "F6b/kf_2.jpg", 5, "The single file of black-suited agents marches around the endless square staircase on the "
            "clock face, round and round, climbing forever; the clock face slowly droops and drips. Slow camera push-in."),
    "F6c": (K + "F6c/kf_2.jpg", 5, "Side-on tracking shot: the girl sprints extremely fast from left to right along the tracks, "
            "long powerful strides, hair streaming; the camera tracks sideways with her at the same speed, keeping her in the "
            "same place in frame while the colored buildings scroll past quickly from right to left."),
    "F7a": (K + "F7a/kf_2.jpg", 4, "Extremely fast: the real girl and the crowd of translucent colored ghost copies of her "
            "stampede toward the camera along the tracks; the camera pulls back fast, low to the tracks."),
    "F7b": (K + "F7b/kf_1.jpg", 4, "The girl runs toward the camera, grinning, hair whipping in the wind; the camera tracks "
            "backward in front of her, fast and handheld. " + FACE),
    "F7c": (K + "F7c/kf_2.jpg", 4, "The girl soars upward through the gold-leaf sky, arms spread, hair fanning out; the gold "
            "spirals and Kandinsky circles swirl and turn around her; the camera rises with her, slowly rotating. " + FACE),
    "F7d": (K + "F7d/kf_2.jpg", 4, "The giant melting clock folds in on itself like soft paper, curling and twisting into a "
            "loop and shrinking toward a single bright point of gold; ink drips fly off. Static camera."),
    "F7e": (K + "F7e/kf_2.jpg", 5, "Extremely fast: the two identical girls fly toward each other and collide in mid-air, "
            "merging into one single girl in a burst of colored motes and gold flakes; one girl remains and lands. Static camera."),
    "F8": (K + "F8/kf_1.jpg", 5, "The girl stands still, breathing hard, shoulders rising and falling, her hair and jacket "
           "moving gently in the wind; the translucent ghost copies behind her settle and stand still in a row. Locked-off "
           "static camera. " + FACE),
    "O2": (K + "O2/kf_1.jpg", 6, "The girl twists her long hair up into a loose bun with one hand and pushes the yellow pencil "
           "through it to hold it, then reaches out, pushes the heavy wooden door open and walks in. Static camera, soft dawn "
           "light slowly brightening."),
}

for name, (img, dur, prompt) in F.items():
    vgen.SHOTS[name] = dict(model=SD20, image=img, duration=dur, camera_fixed=False, prompt=f"{prompt} {LOOK}")

_orig = vgen.build_spec


def build_spec(shot, res, note="", over=None):
    spec = _orig(shot, res, note, over)
    s = {**vgen.SHOTS[shot], **(over or {})}
    if s.get("last"):
        spec["input"]["last_frame_image"] = "file:" + os.path.relpath(gen.ref_image(os.path.join(ROOT, s["last"])), ROOT)
    if os.environ.get("F_TAG_PREFIX"):          # v3 pass: spend tags per stream (e.g. revA_f_)
        spec["tag"] = os.environ["F_TAG_PREFIX"] + spec["tag"]
    return spec


vgen.build_spec = build_spec

if __name__ == "__main__":
    import runpy
    sys.argv[0] = vgen.__file__
    # re-run vgen's CLI with our patched module state
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    opts = {a[2:].partition("=")[0]: a[2:].partition("=")[2] or True for a in sys.argv[2:] if a.startswith("--")}
    if cmd == "submit":
        for s in args:
            over = {k: (int(v) if k == "duration" else v) for k, v in opts.items() if k in ("duration", "prompt", "last", "image")}
            for j in vgen.submit(s, opts.get("res", "720p"), int(opts.get("takes", 1)), "dry-run" in opts, opts.get("note", ""), over):
                print(s, j)
        print(f"spend so far (est): ${vgen.spend_total()}")
    elif cmd == "collect":
        print("pending:", vgen.collect(args or list(F)))
    elif cmd == "wait":
        import time
        t0 = time.time()
        while True:
            p = vgen.collect(args or list(F))
            if not p or time.time() - t0 > float(opts.get("timeout", 3600)):
                print("pending:", p)
                break
            time.sleep(30)
    else:
        print(__doc__)
