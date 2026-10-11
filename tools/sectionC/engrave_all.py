#!/usr/bin/env python3
"""Engrave every collected section C take that has no engraved version yet (sequential, GPU).
    ~/Documents/moongazing/.venv/bin/python tools/sectionC/engrave_all.py [CLIP ...] [--loop]
Writes media/shots/<CLIP>/take_N_engraved.mp4 (+ take_N_matte/ for clips with Jade in them), 1080p.
--loop keeps polling for new takes until every submitted take is engraved.
"""
import glob
import json
import os
import subprocess
import sys
import time

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/sectionC"))
from vid import C  # noqa: E402

ENG_PY = os.path.join(ROOT, "tools/engrave/.venv/bin/python")
ENG = os.path.join(ROOT, "tools/engrave/engrave.py")


def todo(clips):
    out = []
    for clip in clips:
        for mp4 in sorted(glob.glob(os.path.join(ROOT, "media/gen", clip, "take_*.mp4"))):
            n = os.path.basename(mp4)[5:-4]
            if not n.isdigit():
                continue
            dst = os.path.join(ROOT, "media/shots", clip, f"take_{n}_engraved.mp4")
            if not os.path.exists(dst):
                out.append((clip, n, mp4, dst))
    return out


def pending(clips):
    k = 0
    for clip in clips:
        for p in glob.glob(os.path.join(ROOT, "media/gen", clip, "take_*.json")):
            if p.endswith(".spec.json"):
                continue
            if json.load(open(p)).get("state") in ("queued", "running", "ready", "stale"):
                k += 1
    return k


def run(clip, n, src, dst):
    girl = C[clip][3]
    cmd = [ENG_PY, ENG, src, dst, "--out-height", "1080"]
    cmd += ["--matte-out", os.path.join(os.path.dirname(dst), f"take_{n}_matte")] if girl else ["--no-matte"]
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(f"{clip} take_{n}: {'ok' if r.returncode == 0 else 'FAILED ' + r.stderr[-400:]} {time.time() - t0:.0f}s",
          flush=True)


if __name__ == "__main__":
    clips = [a for a in sys.argv[1:] if not a.startswith("--")] or sorted(C)
    while True:
        jobs = todo(clips)
        for j in jobs:
            run(*j)
        if "--loop" not in sys.argv or (not jobs and not pending(clips)):
            break
        if not jobs:
            time.sleep(30)
    print("ENGRAVE_ALL_DONE", flush=True)
