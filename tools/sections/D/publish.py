#!/usr/bin/env python
"""Link a finished D_* take into media/shots/<E#>/ and run the tools/engrave pass (engraved world + Jade matte).

    PY=~/Documents/moongazing/.venv/bin/python
    $PY tools/sections/D/publish.py D_trk_sprint:1 [D_fld_vault:2 ...] [--no-engrave] [--strength=1.0] [--extra='--ramp-in 0.5']

Writes media/shots/<E#>/take_<clip>_<N>.mp4, take_<clip>_<N>_engraved.mp4, take_<clip>_<N>_matte/ (PNG + matte.mp4).
"""
import os
import shlex
import subprocess
import sys

ROOT = "/home/jade/Documents/rewind-take-two"
SHOT_OF = {"trk": "E2", "fld": "E2", "ring": "E2", "e4": "E4", "e5": "E5", "e6": "E6", "e7": "E7", "e8": "E8"}
ENGRAVE_PY = os.path.join(ROOT, "tools/engrave/.venv/bin/python")


def paths(name, take):
    clip = name[2:]                       # "trk_sprint"
    shot = SHOT_OF[clip.split("_")[0]]
    d = os.path.join(ROOT, "media/shots", shot)
    os.makedirs(d, exist_ok=True)
    stem = os.path.join(d, f"take_{clip}_{take}")
    return os.path.join(ROOT, "media/gen", name, f"take_{take}.mp4"), stem


def publish(spec, engrave=True, strength=None, extra=""):
    name, take = spec.split(":")
    src, stem = paths(name, int(take))
    if not os.path.exists(src):
        print("missing", src)
        return
    dst = stem + ".mp4"
    if os.path.exists(dst):
        os.remove(dst)
    os.link(src, dst)
    print("linked", os.path.relpath(dst, ROOT))
    if not engrave:
        return
    py = ENGRAVE_PY if os.path.exists(ENGRAVE_PY) else sys.executable
    cmd = [py, os.path.join(ROOT, "tools/engrave/engrave.py"), dst, stem + "_engraved.mp4", "--matte-out", stem + "_matte",
           "--out-height", "1080"]
    if strength is not None:
        cmd += ["--strength", str(strength)]
    cmd += shlex.split(extra)
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    opts = {a[2:].partition("=")[0]: a[2:].partition("=")[2] for a in sys.argv[1:] if a.startswith("--")}
    for s in [a for a in sys.argv[1:] if not a.startswith("--")]:
        publish(s, "no-engrave" not in opts, opts.get("strength"), opts.get("extra", ""))
