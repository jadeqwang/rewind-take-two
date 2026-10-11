#!/usr/bin/env python3
"""Build docs/revisions/review_A.json from Jade's notes (BASE below) and the stream fragments in
docs/revisions/streams/*.json. A fragment entry replaces the base entry with the same v2_time (or, for notes
without a timestamp, the same `key`). Entries nobody has reported on yet keep status "pending".

    python3 tools/streams/merge_review_A.py            # rewrite review_A.json, print a status table
"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "docs", "revisions", "review_A.json")

# key, v2_time, note (verbatim), shots, before_range, stream
BASE = [
    ("intro", "0:00", "strong intro, especially love the fast rewind through the whole thing, maybe we don’t need the bullet, just muzzle flare for shots", ["C1"], [0.0, 2.6], "V1A"),
    ("watercolor", "0:12", "let’s use the watercolor version of me for singing, because part of the point, I realized, is that the art style I’m rendered in mismatches the surroundings (I’ve added images to /inputs)", ["S1", "E3", "V3S"], [12.6, 19.64], "SING"),
    ("env_lyrics", "", "let’s use the environment for some of the words, instead of all subtitles, which is also a good way of creating visual interest and keeping audience attention. I’m thinking of the way that in “Golden” from Kpop Demon Hunters, there’s large text lyrics that fit naturally into the environment (see Downloads/kdh_screenhots)", [], [20.0, 33.0], "rev-A"),
    ("0:24", "0:24", "0:24 where it currently says “hilbert vacancy” it can display a lyric", ["D2"], [22.5, 25.5], "V1A"),
    ("0:25", "0:25", "0:25 - pencil is not in a coherent straight line, we should just decide that she has 2 pencils if she’s going to have 2 and just always style it consistently. (maybe", ["D3"], [24.5, 28.6], "V1A"),
    ("0:29", "0:29", "0:29 - pulled over - the cars should not be facing each other with the girl in the back, and it should not be a limo. it should be the black car behind the Acura on the right side of the road", ["D4"], [28.0, 30.4], "V1A"),
    ("0:30", "0:30", "0:30 - I really like the idea of displaying the words on the shades. an idea: you see the 3 men in shades and suits and quickly cut to a closeup of the shades (still walking, but you see the words in the shades, rendered in an Escher woodcut native typeface)", ["D5"], [29.8, 32.2], "V1A"),
    ("0:35", "0:35", "0:35 - ID - test should not overlay fingers. you can just have redacted bars on the card image itself. also, the entire body is half-missing and weird. maybe you should use Three.js to figure out how to stage this shot", ["D7"], [33.4, 36.5], "V1B"),
    ("0:37", "0:37", "0:37 - he’s holding his own id looking at the back of it? you should only see the back of an ID", ["D8"], [36.0, 38.2], "V1B"),
    ("1:24", "1:24", "1:24 - facial expression is too happy for this high in the air, she’s still terrified and hasn’t landed the car safely yet", ["V2d2"], [82.8, 85.2], "V2"),
    ("1:26", "1:26", "1:26 - Chicago / US is where the steering wheel is always on the left side of the car", ["V2e2"], [85.6, 87.4], "V2"),
    ("1:33", "1:33", "1:33 - make the redacted blocks the same typeface (or at least size) as the text around it", ["V2h"], [92.6, 94.2], "V2"),
    ("1:52", "1:52", "1:52 - don’t use ‘continue’ voiceover", ["V2n"], [109.5, 114.0], "V2"),
    ("2:21", "2:21", "2:21 - arm patch text consistency", ["G1", "G2", "G3"], [140.0, 148.5], "GO"),
    ("3:21", "3:21", "3:21 - love the color and change in art style, no hime bangs, curtain bangs like in the other scenes, keep jacket styling consistent even though the world is colorful, shirt is still mock neck", ["F7_04", "F7_13"], [199.6, 202.4], "F"),
    ("3:05", "3:05", "3:05 - idea: what if, we see her swinging a pencil as though a sword but it turns into a drawing/writing motion, and the core of the pencil is rainbow colored?", ["F5a"], [183.0, 187.6], "F"),
    ("3:13", "3:13", "3:13 - great colors - good time for all of them to all be traveling clockwise instead of going from down to up, and for it to be an actual infinite staircase, Escher style (do as many web searches as you want for a reference on how to draw one)", ["F6b"], [191.8, 195.8], "F"),
    ("tabletop", "", "an idea: books and other tabletop objects alongside buildings", [], [183.0, 202.4], "F"),
    ("3:40", "3:40", "3:40 - jacket consistency, and putting hair in updo with pencil – do as many google searches as you need to to see how that actually works because this is incorrect, and the door opens the wrong way, and the label on the door is weird (may as well have the information in subtitle format)", ["O2"], [218.4, 223.2], "GO"),
]


def norm(s):
    return " ".join(str(s or "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').split()).lower()


def main():
    entries = {}
    for key, t, note, shots, rng, stream in BASE:
        entries[key] = {"note": note, "v2_time": t, "shots": shots, "status": "pending", "after": "",
                        "before_range": rng, "what_changed": f"In progress (stream {stream}).", "_stream": stream}
    by_time = {e["v2_time"]: k for k, e in entries.items() if e["v2_time"]}
    by_note = {norm(e["note"]): k for k, e in entries.items()}
    extra = []
    for path in sorted(glob.glob(os.path.join(ROOT, "docs", "revisions", "streams", "*.json"))):
        try:
            frag = json.load(open(path))
        except Exception as ex:  # a stream may be mid-write
            print(f"skip {os.path.basename(path)}: {ex}")
            continue
        for e in frag if isinstance(frag, list) else [frag]:
            k = e.get("key") if e.get("key") in entries else None
            ft = e.get("v2_time") or ""
            # a timed entry matches on its time; the note text only decides for untimed notes (a follow-up may
            # quote the same note under a different time and must stay its own entry)
            k = k or by_time.get(ft) or (by_note.get(norm(e.get("note"))) if not ft else None)
            if k is None and not e.get("v2_time"):      # untimed notes only: a timed follow-up is its own entry
                kn = norm(e.get("note"))
                k = next((kk for kk, be in entries.items() if kn and (kn in norm(be["note"]) or norm(be["note"]) in kn)), None)
            e = {kk: v for kk, v in e.items() if kk != "key"}
            e["_stream"] = os.path.basename(path)[:-5]
            if k is None:
                extra.append(e)
                continue
            base = entries[k]
            merged = {**base, **e, "note": base["note"]}       # the note stays verbatim
            if not merged.get("v2_time"):
                merged["v2_time"] = base["v2_time"]
            entries[k] = merged
    out = []
    for e in list(entries.values()) + extra:
        after = e.get("after") or ""
        missing = bool(after) and not os.path.exists(os.path.join(ROOT, after))
        print(f"{e.get('v2_time') or '-':>5}  {e['status']:<9} {e['_stream']:<6} {after}{'  (MISSING)' if missing else ''}")
        out.append({k: v for k, v in e.items() if not k.startswith("_") and not (k == "question" and not v)})
    json.dump(out, open(OUT, "w"), indent=2, ensure_ascii=False)
    print(f"wrote {os.path.relpath(OUT, ROOT)}: {len(out)} entries")


if __name__ == "__main__":
    main()
