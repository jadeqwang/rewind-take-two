"""v5-coda post-credits video candidates: injects the shots into tools/gen/vgen.py (shared shots.py untouched).

    $PY tools/sectionF/coda/vgen_coda.py submit v5_coda_door [--res=720p] [--dry-run]
    $PY tools/sectionF/coda/vgen_coda.py wait v5_coda_door
Takes land in media/gen/<SHOT>/take_N.mp4 (+ take_N_sheet.jpg). Plan: docs/revisions/v5/coda.md.
"""
import os
import sys

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
import vgen  # noqa: E402

SD20 = "bytedance/seedance-2.0"
LOOK = ("Keep the exact hand-drawn look of the first frame: colored pencil laid into black engraved hatching on warm "
        "paper. The gold emblem and its lettering on the glass stay exactly as in the first frame and move only with "
        "the door. No new text, no logos, no watermark. No red.")
CODA = {
    # PC1: Jade's POV at the hotel door; a doorman's white-gloved hand (only the hand and cuff) opens it for her
    "v5_coda_door": ("media/reviews/v5/plans/coda/door_color.jpg", 5,
                     "A hand in a crisp white cotton glove, with the dark green sleeve cuff of a hotel doorman's livery "
                     "trimmed with a thin gold braid, reaches in from the right edge of the frame, takes the long brass "
                     "handle and smoothly pulls the glass door open toward the right; the small brass bell on its curled "
                     "spring above the door swings and jiggles; warm golden light from the lobby spills out through the "
                     "opening. Then the camera glides slowly forward toward the open doorway at walking pace, as if "
                     "stepping inside. Only the gloved hand and the cuff are ever seen, never the doorman's body or face."),
}
for name, (img, dur, prompt) in CODA.items():
    vgen.SHOTS[name] = dict(model=SD20, image=img, duration=dur, camera_fixed=False, prompt=f"{prompt} {LOOK}")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    opts = {a[2:].partition("=")[0]: a[2:].partition("=")[2] or True for a in sys.argv[2:] if a.startswith("--")}
    if cmd == "submit":
        for s in args:
            for j in vgen.submit(s, opts.get("res", "720p"), int(opts.get("takes", 1)), "dry-run" in opts):
                print(s, j)
    elif cmd == "wait":
        import time
        t0 = time.time()
        while True:
            p = vgen.collect(args or list(CODA))
            if not p or time.time() - t0 > float(opts.get("timeout", 1800)):
                print("pending:", p)
                break
            time.sleep(30)
    else:
        print(__doc__)
