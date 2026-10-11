#!/usr/bin/env python3
"""Write media/shots/<CLIP>/chosen.json + NOTES.md for every section C clip, from render/timeline/C.js (the cut table),
the vgen sidecars (media/gen/<CLIP>/take_N.json) and the keyframe prompts (tools/sectionC/kf.py).
    ~/Documents/moongazing/.venv/bin/python tools/sectionC/notes.py
"""
import glob
import json
import os
import re
import sys

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/sectionC"))
from kf import J  # noqa: E402

VERDICT = {}  # clip -> judgement line (filled from VERDICTS below)
VERDICTS = os.path.join(ROOT, "tools/sectionC/verdicts.json")
if os.path.exists(VERDICTS):
    VERDICT = json.load(open(VERDICTS))

src = open(os.path.join(ROOT, "render/timeline/C.js")).read()
rows = re.findall(r"\[(\d+\.\d+), (\d+\.\d+), '(V2\w+)', (\d+), ([\d.]+), ([\d.]+)", src)
uses = {}
for a, b, clip, take, cin, rate in rows:
    uses.setdefault(clip, []).append(dict(timeline_in=float(a), timeline_out=float(b), take=int(take), in_sec=float(cin),
                                          rate=float(rate)))
# the V2n freeze reuses V2m1
uses.setdefault("V2m1", []).append(dict(timeline_in=111.22, timeline_out=112.66, take=1, in_sec=0.79, rate=0, note="freeze + negative"))

for clip, us in sorted(uses.items()):
    d = os.path.join(ROOT, "media/shots", clip)
    u = us[0]
    dur = (u["timeline_out"] - u["timeline_in"]) * (u["rate"] or 0)
    chosen = {"take": u["take"], "file": f"media/shots/{clip}/take_{u['take']}_engraved.mp4",
              "in_sec": u["in_sec"], "out_sec": round(u["in_sec"] + dur, 3), "rate": u["rate"], "reverse": False,
              "notes": VERDICT.get(clip, ""), "uses": us,
              "matte": (f"media/shots/{clip}/take_{u['take']}_matte/matte.mp4"
                        if os.path.isdir(os.path.join(d, f"take_{u['take']}_matte")) else None)}
    json.dump(chosen, open(os.path.join(d, "chosen.json"), "w"), indent=1, ensure_ascii=False)

    lines = [f"# {clip} (section C)", ""]
    kfs = [k for k in J if k.startswith(clip + "_")]
    lines.append("## Keyframes")
    for k in kfs:
        j = J[k]
        lines.append(f"- `kf_{k[len(clip) + 1:]}` — {j['model']} (refs: {', '.join(j['refs']) or 'none'})")
        lines.append(f"  > {j['prompt'][:900]}")
    lines += ["", "## Takes"]
    for p in sorted(glob.glob(os.path.join(ROOT, "media/gen", clip, "take_*.json"))):
        if p.endswith(".spec.json"):
            continue
        s = json.load(open(p))
        lines.append(f"- take_{s['take']}: {s['model']} {s.get('res')} {s.get('duration')} s, est ${s.get('est_usd')}, "
                     f"first frame `{s.get('first_frame')}`, state {s.get('state')}")
        lines.append(f"  > {s.get('prompt', '')}")
    lines += ["", "## Use in the cut", ""]
    for x in us:
        lines.append(f"- {x['timeline_in']:.2f}–{x['timeline_out']:.2f}: take_{x['take']} from {x['in_sec']} s at rate {x['rate']}"
                     + (f" ({x['note']})" if x.get("note") else ""))
    lines += ["", "## Judgement", "", VERDICT.get(clip, "(see docs/sections/C.md)"), ""]
    open(os.path.join(d, "NOTES.md"), "w").write("\n".join(lines))
    print(clip, len(us), "uses")
