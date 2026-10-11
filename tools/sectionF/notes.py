"""Write media/shots/<SHOT>/NOTES.md for section F from the vgen sidecars, the keyframe prompt log and the judgements below."""
import glob
import json
import os

ROOT = "/home/jade/Documents/rewind-take-two"
JUDGE = json.load(open(os.path.join(ROOT, "tools/sectionF/judgements.json")))


def main():
    for shot, j in JUDGE.items():
        d = os.path.join(ROOT, "media/shots", shot)
        if not os.path.isdir(d):
            continue
        L = [f"# {shot}: {j.get('title', '')}", "", j.get("idea", ""), ""]
        kp = os.path.join(d, "kf_prompt.txt")
        L += ["## Keyframe", "", f"Model: google/nano-banana-pro (2K, 16:9), $0.134 per image. Chosen: `{j.get('kf', 'kf_1')}`.", ""]
        if os.path.exists(kp):
            last = open(kp).read().strip().split("--- ")[-1].strip()
            L += ["Prompt (last round):", "", "```", last[:3000], "```", ""]
        L += ["## Takes", ""]
        tot = 0.0
        for p in sorted(glob.glob(os.path.join(ROOT, "media/gen", shot, "take_*.json"))):
            if p.endswith((".spec.json",)):
                continue
            s = json.load(open(p))
            tot += s.get("est_usd", 0) if s.get("state") == "done" or not s.get("refunded") else 0
            L += [f"- take_{s['take']}: {s['model']} {s.get('res')} {s.get('duration')} s, est ${s.get('est_usd')}, state {s.get('state')}, "
                  f"first frame `{s.get('first_frame')}`. {s.get('notes', '')}",
                  f"  - prompt: {s.get('prompt', '')}"]
            v = j.get("takes", {}).get(str(s["take"]))
            if v:
                L.append(f"  - verdict: {v}")
        L += ["", f"Video cost for this shot: ${tot:.2f} (list-price estimate).", "", "## Judgement", "", j.get("judgement", ""), ""]
        if os.path.exists(os.path.join(d, "chosen.json")):
            L += ["## chosen.json", "", "```json", open(os.path.join(d, "chosen.json")).read().strip(), "```", ""]
        open(os.path.join(d, "NOTES.md"), "w").write("\n".join(L))
        print("wrote", os.path.relpath(os.path.join(d, "NOTES.md"), ROOT))


if __name__ == "__main__":
    main()
