#!/usr/bin/env python3
"""Revision B (v3 pass): the restaged chase, 94.06-141.00. Keyframes, Seedance takes, engrave. Plan: docs/revisions/B_research.md

    PY=~/Documents/moongazing/.venv/bin/python
    $PY tools/sections/B/rb.py list
    $PY tools/sections/B/rb.py kf NAME [NAME ...] [--model=nano|flare|seedream] [--v=2] [--dry-run]
    $PY tools/sections/B/rb.py edit NAME SRC_IMAGE "instruction" [--v=2]        # nano edit of an existing image
    $PY tools/sections/B/rb.py sheet OUT.jpg NAME[:v] [...]                      # keyframe contact sheet
    $PY tools/sections/B/rb.py submit TAKE [TAKE ...] [--kf=NAME:v] [--res=720p] [--dry-run]
    $PY tools/sections/B/rb.py wait|collect [TAKE ...]
    $PY tools/sections/B/rb.py engrave TAKE:N [...]                              # take_N_engraved.mp4 + take_N_matte/

Keyframes: media/shots/B_<name>/kf_v<N>.png. Takes: media/gen/B_<take>/take_N.mp4, hard-linked into
media/shots/B_<take>/ with the engraved plate and matte beside them (the layout render/timeline/C.js expects).
Prompts live in tools/sections/B/prompts.py. Spend tags are prefixed revB_.
"""
import concurrent.futures as cfut
import glob
import os
import subprocess
import sys
import time
import traceback

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
sys.path.insert(0, os.path.join(ROOT, "tools/sectionC"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cf  # noqa: E402
import vgen  # noqa: E402
from common import inp_for, sheet, trim_margins  # noqa: E402  (section C helpers: refs, margins, sheets)
import prompts as P  # noqa: E402

SHOTS = os.path.join(ROOT, "media/shots")
MODELS = {"nano": "google/nano-banana-pro", "flare": "openai/gpt-image-2.5-flare", "seedream": "bytedance/seedream-5-pro"}
SD20 = "bytedance/seedance-2.0"
TAG = "revB_"


def kf_path(name, v=1):
    return os.path.join(SHOTS, "B_" + name, f"kf_v{v}.png")


def find_kf(name, v=None):
    c = sorted(p for p in glob.glob(os.path.join(SHOTS, "B_" + name, "kf_v*.*")) if "_raw" not in p)
    if v:
        c = [p for p in c if os.path.splitext(os.path.basename(p))[0] == f"kf_v{v}"]
    assert c, f"no keyframe for {name} v={v}"
    return c[-1]


def run_kf(names, model="nano", v=1, dry=False):
    def one(n):
        k = P.KF[n]
        out = kf_path(n, v)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        m = MODELS[k.get("model", model)]
        try:
            p = cf.generate(m, inp_for(m, k["prompt"], k.get("refs", ())), out, tag=f"{TAG}kf_{n}", timeout=600, dry_run=dry)
            if p:
                trim_margins(p[0])
            return n, p[0] if p else None
        except Exception as e:  # noqa: BLE001
            print(f"FAILED {n}: {e}", file=sys.stderr)
            traceback.print_exc()
            return n, None
    with cfut.ThreadPoolExecutor(8) as ex:
        return dict(ex.map(one, names))


def edit(name, src, instruction, v=1, refs=()):
    out = kf_path(name, v)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    m = MODELS["nano"]
    p = cf.generate(m, inp_for(m, instruction, (src, *refs)), out, tag=f"{TAG}edit_{name}", timeout=600)
    trim_margins(p[0])
    return p[0]


def register(take, kf=None):
    t = P.VID[take]
    name, _, v = (kf or t["kf"]).partition(":")
    img = os.path.relpath(find_kf(name, int(v) if v else None), ROOT)
    look = P.KEEP if t.get("girl", True) else P.KEEP_NOGIRL
    vgen.SHOTS["B_" + take] = dict(model=SD20, image=img, duration=t.get("dur", 5), camera_fixed=bool(t.get("fixed", True)),
                                   prompt=(P.LOCK if t.get("fixed", True) else "") + t["prompt"] + " " + look)


_orig_build = vgen.build_spec


def _build(shot, res, note="", over=None):
    spec = _orig_build(shot, res, note, over)
    spec["tag"] = TAG + spec["tag"]
    return spec


vgen.build_spec = _build


def link(takes):
    for t in takes:
        for mp4 in sorted(glob.glob(os.path.join(ROOT, "media/gen", "B_" + t, "take_*.mp4"))):
            for src in (mp4, mp4[:-4] + "_sheet.jpg"):
                dst = os.path.join(SHOTS, "B_" + t, os.path.basename(src))
                if os.path.exists(src) and not os.path.exists(dst):
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    os.link(src, dst)


def engrave(spec, extra=()):
    take, _, n = spec.partition(":")
    n = n or "1"
    d = os.path.join(SHOTS, "B_" + take)
    src = os.path.join(d, f"take_{n}.mp4")
    dst = os.path.join(d, f"take_{n}_engraved.mp4")
    if os.path.exists(dst):
        print(f"B_{take} take_{n}: already engraved", flush=True)
        return
    free = os.statvfs(ROOT)
    if free.f_bavail * free.f_frsize < 1.5e9:      # shared rule with rev-A: hold below 1.5 GB free
        print(f"B_{take} take_{n}: HELD, under 1.5 GB free", flush=True)
        return
    # one engrave at a time across both revision instances (each run writes a few hundred MB of temporary mattes)
    cmd = ["flock", os.path.join(ROOT, "media/.engrave.lock"),
           os.path.join(ROOT, "tools/engrave/.venv/bin/python"), os.path.join(ROOT, "tools/engrave/engrave.py"), src, dst,
           "--out-height", "1080"]
    cmd += ["--matte-out", os.path.join(d, f"take_{n}_matte")] if P.VID[take].get("girl", True) else ["--no-matte"]
    cmd += list(extra)
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(f"B_{take} take_{n}: {'ok' if r.returncode == 0 else 'FAILED ' + r.stderr[-600:]} {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    opts = {a[2:].partition("=")[0]: a[2:].partition("=")[2] or True for a in sys.argv[2:] if a.startswith("--")}
    v = int(opts.get("v", 1))
    if cmd == "list":
        print("keyframes:", " ".join(P.KF))
        print("takes:", " ".join(f"{k}({t['kf']})" for k, t in P.VID.items()))
    elif cmd == "kf":
        for n, p in run_kf(args, opts.get("model", "nano"), v, "dry-run" in opts).items():
            print(n, p)
    elif cmd == "edit":
        print(edit(args[0], args[1], args[2], v, tuple(args[3:])))
    elif cmd == "sheet":
        tiles = []
        for a in args[1:]:
            n, _, vv = a.partition(":")
            tiles.append((find_kf(n, int(vv) if vv else None), a))
        print(sheet(tiles, os.path.join(ROOT, args[0]), title="rev B keyframes", cols=int(opts.get("cols", 3)), width=2400))
    elif cmd == "submit":
        for t in args:
            register(t, opts.get("kf"))
            for j in vgen.submit("B_" + t, opts.get("res", "720p"), int(opts.get("takes", 1)), "dry-run" in opts):
                print(t, j)
        print(f"spend so far (est): ${vgen.spend_total()}")
    elif cmd in ("collect", "wait"):
        takes = args or sorted(P.VID)
        for t in takes:
            vgen.SHOTS.setdefault("B_" + t, {})
        t0 = time.time()
        while True:
            pend = vgen.collect(["B_" + t for t in takes])
            link(takes)
            if cmd == "collect" or not pend or time.time() - t0 > float(opts.get("timeout", 1500)):
                print("pending:", pend)
                break
            time.sleep(30)
    elif cmd == "engrave":
        for a in args:
            engrave(a)
