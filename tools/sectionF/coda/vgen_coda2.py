"""v5-coda2 idle takes (Jade, Round 3: "all the Jade's should move slightly ... each one a little different and out of
sync with the others, not bob up and down like a cardboard cutout"). One Seedance 2.0 i2v take per front figure, from
her standing still on the flat grey ground, 9:16, 5 s, locked camera, and with the SAME image as first and last frame,
so the take loops back to the pose it started from. Shots v5_coda2_idle_<name>; takes in media/gen/<shot>/.

    $PY tools/sectionF/coda/vgen_coda2.py firstframes
    $PY tools/sectionF/coda/vgen_coda2.py submit jade [glasses ...] [--res=720p] [--dry-run]
    $PY tools/sectionF/coda/vgen_coda2.py wait jade [...]
Plan / log: docs/revisions/v5/coda2.md.
"""
import os
import sys

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
sys.path.insert(0, os.path.join(ROOT, "tools/sectionF/coda"))
import gen  # noqa: E402
import vgen  # noqa: E402

SD20 = "bytedance/seedance-2.0"
FF = "media/shots/PC/gen2/ff"            # first (= last) frames, 1536x2752 on #bdbdbd
COMMON = ("Locked-off static camera: the camera never moves, pans or zooms, and the framing stays exactly the same. "
          "The plain flat light grey background stays completely empty and flat: no floor, no shadow, no objects. She "
          "stays standing on the same spot, her whole figure in frame from head to toe at the same size. Subtle, natural "
          "idle motion, like someone waiting patiently in a queue: she breathes gently and {act}, then settles back into "
          "exactly the same pose as at the start. Her face, hair{glasses} and outfit keep the first frame's design "
          "exactly, in the same clean anime illustration style and colours. No text, no logos, no watermark. No red.")
IDLE = {   # name: (first-frame source, action, glasses?)
    "jade": ("media/shots/PC/gen2/jade_v3.jpg",
             "shifts her weight a little from one foot to the other, then straightens the collar of her open white jacket "
             "with one hand and lowers the hand back to her side", False),
    "glasses": ("media/shots/PC/gen2/glasses_v2.jpg",
                "pushes her glasses up her nose with one finger, then lowers the hand back to her side", True),
    "teal": ("@media/shots/PC/sprites_v2/teal.png",
             "tucks a strand of her teal-tipped hair behind one ear with one hand, then lowers the hand back to her side", False),
    "purple": ("@media/shots/PC/sprites_v2/purple.png",
               "taps one foot a few times with a small impatient bounce and glances to the side, then stands still", False),
    "braids": ("@media/shots/PC/sprites_v2/braids.png",
               "fiddles with the end of one braid with her fingers, then lets it go and lowers the hand", False),
    "plain": ("@media/shots/PC/sprites_v2/plain.png",
              "scratches the side of her head with the hand that holds the pen, then lowers the hand back to her side", False),
    "sleepy": ("@media/shots/PC/sprites_v2/sleepy.png",
               "dozes standing up: her head slowly droops forward, then she starts awake a little and her head tilts back "
               "to where it was; her eyes stay closed", False),
    "rainbow": ("@media/shots/PC/sprites_v2/rainbow.png",
                "takes one chip out of her small bag of chips and eats it, then holds the bag as before", False),
    "mint": ("@media/shots/PC/sprites_v2/mint.png",
             "rocks gently on her heels, swaying a little from side to side, while her pink bubblegum bubble slowly grows "
             "a little and shrinks back", False),
}


def first_frame(name):
    src = IDLE[name][0]
    out = f"{FF}/{name}.jpg"
    if src.startswith("@"):
        from gen_coda2 import on_grey
        os.makedirs(os.path.join(ROOT, FF), exist_ok=True)
        on_grey(src[1:], out)
        return out
    return src


for name, (src, act, gl) in IDLE.items():
    ff = f"{FF}/{name}.jpg" if src.startswith("@") else src
    vgen.SHOTS[f"v5_coda2_idle_{name}"] = dict(model=SD20, image=ff, last=ff, duration=5, camera_fixed=True, aspect="9:16",
                                               prompt=COMMON.format(act=act, glasses=", glasses" if gl else ""))

_orig = vgen.build_spec


def build_spec(shot, res, note="", over=None):
    spec = _orig(shot, res, note, over)
    s = {**vgen.SHOTS[shot], **(over or {})}
    if s.get("last"):
        spec["input"]["last_frame_image"] = "file:" + os.path.relpath(gen.ref_image(os.path.join(ROOT, s["last"])), ROOT)
    return spec


vgen.build_spec = build_spec

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    opts = {a[2:].partition("=")[0]: a[2:].partition("=")[2] or True for a in sys.argv[2:] if a.startswith("--")}
    shots = [f"v5_coda2_idle_{a}" for a in (args or IDLE)]
    if cmd == "firstframes":
        for n in (args or IDLE):
            print(n, first_frame(n))
    elif cmd == "submit":
        for s in shots:
            for j in vgen.submit(s, opts.get("res", "720p"), int(opts.get("takes", 1)), "dry-run" in opts, "v5-coda2 idle"):
                print(s, j)
        print(f"spend so far (est): ${vgen.spend_total()}")
    elif cmd == "wait":
        import time
        t0 = time.time()
        while True:
            p = vgen.collect(shots)
            if not p or time.time() - t0 > float(opts.get("timeout", 1800)):
                print("pending:", p)
                break
            time.sleep(30)
    else:
        print(__doc__)
