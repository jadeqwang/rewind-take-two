#!/usr/bin/env python3
"""Watercolor singing Jade (v3), step 5: Seedance 2.5 takes from the v3 first frames (after tools/sing/takes.py and
moongazing-public-version work/singer5/shots.py). Same model, vocal slices, ref_t0 and durations as the v2 pencil takes;
takes are written BESIDE the v2 ones as media/sing/<SHOT>/v3_take_N.*.

    PY=~/Documents/moongazing/.venv/bin/python
    $PY tools/sing/wc_takes.py submit SHOT [--n=1] [--res=720p] [--dry-run] [--note=...]
    $PY tools/sing/wc_takes.py collect [SHOT ...]
    $PY tools/sing/wc_takes.py wait [SHOT ...]
    $PY tools/sing/wc_takes.py status

Song time -> clip time: clip_t = song_t - ref_t0 + lag (measure with: MPY tools/sing/look.py SHOT v3_take_N).
Prompt lessons carried over from moongazing: do not say "Chinese ink-and-wash watercolour" (the model then paints a
Chinese painting on white paper and lets the edges fade); say the picture stays as dark and as drawn as the first frame;
smooth forehead, head keeps its angle, eyes open."""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen  # noqa: E402
import spend  # noqa: E402
import takes as V2  # noqa: E402  (vocal slices, contact sheet)

SING = os.path.join(ROOT, "media/sing")
MODEL = "bytedance/seedance-2.5"
VER = os.environ.get("WC_VER", "v3")      # v4: WC_VER=v4 (new first frames: glossier hair, less smile); docs/revisions/v4/A.md
PRE = f"{VER}_take_"

P = ("A picture comes to life and stays the same picture in every frame: the woman is a soft colour painting in gentle brushed "
     "washes, and the world behind her is a hard black-and-white wood engraving, drawn to all four edges with the same lines and "
     "hatching as the first frame. The two never blend: she stays painted in full warm colour, the world stays black ink. Nothing "
     "fades or washes out; no bare paper, no mist. {BEGIN} "
     "sings {WORDS} {ACT} Her eyes stay open, {EYES}; a quick blink is fine. Her forehead stays "
     "smooth: brows relaxed, never knit, no frown. Her head keeps the angle of the first frame: it does not tip back or turn; it "
     "sways only a very little. Her mouth opens naturally, as in gentle singing. She stays the same person as in "
     "the first frame: the same large head, wide heart-shaped face, high forehead, the two slightly different eyebrows, glasses, {HAIRPRE}"
     "{HAIR}. Do not redraw, beautify, slim, age or restyle her; no makeup. Her white jacket with its orange "
     "band, blue disc and the round '1420 MHz' patch on the sleeve stays exactly as painted, the patch sharp and unchanged. No "
     "headphones. Static locked-off camera, no zoom: she stays framed chest-up exactly as in the first frame. {WHERE} No new text.")
WHERE_SANE = ("She stands at night right in front of the mirror of Cloud Gate in Chicago. Everything behind her stays exactly as "
              "engraved: the curved reflection of the city, the plaza, the lamps, the rooftop; only the tiny headlights on the road "
              "at the right move slowly along it. A faint breeze stirs a few loose strands of her hair.")
WHERE_TRUTH = ("She stands at night right in front of the mirror of Cloud Gate in Chicago. Everything behind her stays exactly as "
               "engraved: the curved reflection of the impossible city with its looping stairs and train tracks and its "
               "patches of orange and pale-blue pencil; nothing changes shape. A faint breeze stirs a few loose strands of "
               "her hair.")
LINE = ("the words 'The night before my dissertation defense' from the reference audio, her lips shaping each syllable in time "
        "with the voice: lips closing on the 'b' of 'before' and the 'm' of 'my', and moving quickly through 'dissertation "
        "defense', the last syllable held softly.")
SHOTS = {
    "S1": dict(first="media/sing/first/v3_S1_first.jpg", WHERE=WHERE_SANE, WORDS=LINE,
               ACT="She sings it quietly, as if remembering a dream, looking into the camera, open and calm."),
    "E3": dict(first="media/sing/first/v3_S1_first.jpg", WHERE=WHERE_SANE,
               WORDS=("one long held word, 'Rewind', from the reference audio: a short 're', then the vowel of 'wind' held open "
                      "for three and a half seconds with a steady, full voice; her mouth stays open on the vowel right up to the "
                      "end of the note and only narrows a little as it goes on; mouth visibly open."),
               ACT="She holds the note with quiet strength, looking steadily into the camera; she breathes in at the very end."),
    "V3S": dict(first="media/sing/first/v3_V3S_first.jpg", WHERE=WHERE_TRUTH, WORDS=LINE,
                ACT=("She sings it knowingly, looking into the camera, the smile staying in her eyes, as if she has seen through "
                     "the dream.")),
}
# Round 2 (takes 2+; round 1 = the entries above, take 1). E3 take 1 closed the vowel about 1 s before the note ends
# (the slice also holds the start of the next "Rewind" at 123.0, so the prompt now says so). V3S take 1 barely shaped
# the words, shut her eyes for a second near the end and tinted the jacket's grey shading cyan.
R2 = {
    "E3": dict(WORDS=("the word 'Rewind' twice, from the reference audio: a short 're', then the vowel of 'wind' held wide open "
                      "for a full three and a half seconds, steady and strong, her mouth staying clearly open on the vowel the "
                      "whole time, never closing or going back to a smile while the note lasts; then a quick breath and "
                      "'Rewind' again."),
               ACT="She holds the long note with quiet strength, eyes open, looking into the camera."),
    "V3S": dict(ACT="She sings it clearly, her lips shaping every word, eyes open, looking into the camera. Her jacket stays "
                    "white, never cyan."),
}
# The parts of the prompt that describe her face and hair. v3 = the smiling portrait. v4 = Jade's pick (v4 note:
# "reduce smiling magnitude in order to fit the mood of the song"; hair "more glossy and natural looking").
LOOK = {
    "v3": dict(BEGIN="The woman begins on her painted smile and sings from it: she", EYES="warm and alive",
               HAIRPRE="long ", HAIR="loose dark hair"),
    "v4": dict(BEGIN="She never smiles: from the calm, serious, closed mouth of the first frame she", EYES="steady",
               HAIRPRE="", HAIR="long glossy dark hair"),
}[VER]
V4 = {   # v4 acting: tense and determined, not warm (the lyric is about being hunted the night before her defense)
    "S1": dict(ACT="She sings it quietly and intently, looking into the camera: wide awake, a little tense, determined."),
    "V3S": dict(ACT="She sings it clearly, lips shaping every word, eyes on the camera, resolute. Her jacket stays "
                    "white, never cyan."),
}
if os.environ.get("WC_ROUND", "2") == "2":
    for _k, _d in R2.items():
        SHOTS[_k].update(_d)
if VER != "v3":
    for _k, _d in V4.items():
        SHOTS[_k].update(_d)
        SHOTS[_k]["first"] = SHOTS[_k]["first"].replace("/v3_", f"/{VER}_")
for _k, _s in SHOTS.items():      # same slices and windows as v2
    _s.update({k: V2.SHOTS[_k][k] for k in ("ref_t0", "duration", "in_out")})


def sidecars(shot):
    d = os.path.join(SING, shot)
    out = []
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if f.startswith(PRE) and f.endswith(".json") and f.count(".") == 1:
            try:
                out.append((int(f[len(PRE):-5]), os.path.join(d, f)))
            except ValueError:
                pass
    return sorted(out)


def submit(shot, n=1, res="720p", dry=False, note=""):
    s = SHOTS[shot]
    d = os.path.join(SING, shot)
    aud = V2.audio_path(shot)
    assert os.path.exists(aud), aud
    img = gen.ref_image(os.path.join(ROOT, s["first"]), os.path.join(d, f"{VER}_first_2048.jpg"))
    prompt = P.format(WORDS=s["WORDS"], ACT=s["ACT"], WHERE=s["WHERE"], **LOOK)
    assert len(prompt) <= 2000, len(prompt)
    for _ in range(n):
        used = [k for k, _ in sidecars(shot)] + [int(f[len(PRE):].split(".")[0]) for f in os.listdir(d)
                                                 if f.startswith(PRE) and f.endswith(".spec.json")]
        k = max(used) + 1 if used else 1
        spec = {"model": MODEL, "tag": f"revA_sing_{shot}" if VER == "v3" else f"{VER}A_sing_{shot}", "notes": f"{shot} {PRE}{k} {res} {note}".strip(),
                "input": {"prompt": prompt, "image": "file:" + os.path.relpath(img, ROOT),
                          "reference_audios": ["file:" + os.path.relpath(aud, ROOT)], "duration": s["duration"],
                          "resolution": res, "aspect_ratio": "16:9", "generate_audio": False,
                          "use_virtual_avatar": True, "camera_fixed": False}}
        sp = os.path.join(d, f"{PRE}{k}.spec.json")
        json.dump(spec, open(sp, "w"), indent=1, ensure_ascii=False)
        if dry:
            gen.submit(sp, dry_run=True)
            os.remove(sp)
            continue
        jid = gen.submit(sp)
        _, _, _, _, est, why, _ = gen.prepare(sp)
        side = {"shot": shot, "take": k, "job": jid, "model": MODEL, "res": res, "duration": s["duration"], "est_usd": est,
                "est_basis": why, "state": "queued", "submitted": time.time(), "ref_t0": s["ref_t0"],
                "audio": os.path.relpath(aud, ROOT), "first_frame": s["first"], "prompt": prompt, "notes": note}
        json.dump(side, open(os.path.join(d, f"{PRE}{k}.json"), "w"), indent=1, ensure_ascii=False)
        print(shot, f"{PRE}{k}", jid, f"${est}")
    print(f"project spend now (est): ${spend.total()}")


def collect(shots=None):
    pending = 0
    for shot in shots or list(SHOTS):
        for k, p in sidecars(shot):
            side = json.load(open(p))
            if side["state"] not in ("queued", "running", "ready", "stale"):
                continue
            gen.collect_one(side["job"])
            j = gen.read_manifest()["jobs"][side["job"]]
            side["state"] = j["state"]
            if j["state"] == "done":
                src = os.path.join(ROOT, j["files"][0])
                dst = os.path.join(SING, shot, f"{PRE}{k}.mp4")
                if os.path.exists(dst):
                    os.remove(dst)
                os.link(src, dst)
                side.update(file=os.path.relpath(dst, ROOT), raw_file=j["files"][0], probe=gen.probe(dst),
                            gen_secs=j.get("gen_secs"), latency_secs=j.get("latency_secs"))
                V2.contact_sheet(dst, os.path.join(SING, shot, f"{PRE}{k}_sheet.jpg"), f"{shot} {PRE}{k} {side['res']}")
            elif j["state"] in ("error", "collected_error"):
                side["error"] = (j.get("error") or "")[:800]
            else:
                pending += 1
            json.dump(side, open(p, "w"), indent=1, ensure_ascii=False)
            print(shot, f"{PRE}{k}", side["state"], side.get("file", side.get("error", ""))[:200])
    return pending


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    opts = {a[2:].partition("=")[0]: a[2:].partition("=")[2] or True for a in sys.argv[2:] if a.startswith("--")}
    if cmd == "submit":
        for s in args:
            submit(s, int(opts.get("n", 1)), opts.get("res", "720p"), "dry-run" in opts, opts.get("note", ""))
    elif cmd == "collect":
        print("pending:", collect(args or None))
    elif cmd == "wait":
        t0 = time.time()
        while collect(args or None) and time.time() - t0 < float(opts.get("timeout", 2400)):
            time.sleep(30)
    elif cmd == "status":
        for s in SHOTS:
            for k, p in sidecars(s):
                j = json.load(open(p))
                print(s, f"{PRE}{k}", j["state"], j.get("res"), j.get("est_usd"), j.get("file", ""))
        print(f"project spend (est): ${spend.total()}")
    else:
        print(__doc__)
