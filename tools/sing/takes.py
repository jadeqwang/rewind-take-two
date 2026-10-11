#!/usr/bin/env python3
"""Singing Jade, step 5: Seedance 2.5 takes from the first frames, with her isolated vocal as reference_audios
(generate_audio false, use_virtual_avatar true; docs/recon/pipeline.md section 2-3, the Orbital Sunrise method).

    PY=~/Documents/moongazing/.venv/bin/python
    $PY tools/sing/takes.py audio                       # cut the vocal slices -> media/sing/audio/
    $PY tools/sing/takes.py submit SHOT [--n=1] [--res=720p] [--dry-run] [--note=...]
    $PY tools/sing/takes.py collect [SHOT ...]          # fetch finished takes -> media/sing/<SHOT>/take_N.mp4 + sheet
    $PY tools/sing/takes.py wait [SHOT ...]             # collect until nothing is pending
    $PY tools/sing/takes.py status

Song time -> clip time: clip_t = song_t - ref_t0 + lag (lag > 0: the take's mouth runs late; measured by look.py).
Jobs go through tools/gen/gen.py (relay queue, prefix rewind2/, spend cap and log in media/genlog.jsonl)."""
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
import gen  # noqa: E402
import spend  # noqa: E402

VOC = os.path.join(ROOT, "analysis/cinematic/vocals_bs_roformer_48k.wav")
SING = os.path.join(ROOT, "media/sing")
MODEL = "bytedance/seedance-2.5"

P = ("A drawing comes to life and stays the same drawing in every frame: the woman is a soft colored-pencil drawing and the "
     "world around her a black-and-white wood engraving, with the same lines, hatching and paper as the first frame. The "
     "woman sings {WORDS} {ACT} Her forehead stays smooth and unlined for the whole clip: her brows stay relaxed and never "
     "knit, no frown, no creases, no grimace. Her head keeps the angle of the first frame: it does not tip back or turn; "
     "it sways only a very little. Her mouth opens naturally, as in gentle singing, never a wide shout. She stays the same "
     "person as in the first frame: the same large head, wide heart-shaped face with its tapering chin, high forehead, the "
     "two slightly different eyebrows, wide glasses, centre-parted hair. Do not redraw, beautify, slim, age or restyle her "
     "face; no makeup, no added lines. The hairline stays at the same height above her brows, and the top of her head "
     "stays in frame. Static locked-off camera, no zoom, never a face close-up: she stays framed chest-up exactly as in the "
     "first frame. {WHERE} No text.")
WHERE_SANE = ("She stands at night right in front of the mirror of Cloud Gate in Chicago. Everything behind her stays "
              "exactly as engraved in the first frame: the curved reflection of the city, the plaza, the lamps, the rooftop; "
              "only the tiny pair of headlights on the road in the reflection at the right moves slowly along it. The air "
              "is still; only a few loose hairs stir.")
WHERE_TRUTH = ("She stands at night right in front of the mirror of Cloud Gate in Chicago. Everything behind her stays "
               "exactly as engraved in the first frame: the curved reflection of the impossible city with its looping "
               "stairs and train tracks and its soft patches of orange and pale-blue colored pencil; nothing in it changes "
               "shape. The air is still; only a few loose hairs stir.")
LINE = ("the words 'The night before my dissertation defense' from the reference audio, her lips shaping each syllable in "
        "time with the voice: lips closing on the 'b' of 'before' and the 'm' of 'my', and moving quickly through "
        "'dissertation defense', the last syllable held softly.")
SHOTS = {
    "S1": dict(first="media/sing/first/S1_first.jpg", ref_t0=12.90, duration=8, in_out=(12.60, 19.64), WHERE=WHERE_SANE,
               words=[("The", 13.2), ("my", 16.286), ("defense", 17.428)], WORDS=LINE,
               ACT="She sings it quietly, as if remembering a dream, looking into the camera, open and calm, her eyes alive."),
    "E3": dict(first="media/sing/first/E3_first.jpg", ref_t0=119.14, duration=5, in_out=(119.44, 122.95), WHERE=WHERE_SANE,
               mute=[(119.14, 119.38)],   # the last of the thirteen "stop" chops sits in the pre-roll: silenced
               words=[("Rewind", 119.44)],
               WORDS=("one long held word, 'Rewind', from the reference audio: a short 're', then the vowel of 'wind' held "
                      "open for three and a half seconds with a steady, full voice; her mouth stays open on the vowel right up to the "
                      "end of the note and only narrows a little as it goes on; she sings clearly, mouth visibly open."),
               ACT=("She holds the note with quiet strength, eyes open, looking steadily into the camera; she breathes in "
                    "at the very end.")),
    "V3S": dict(first="media/sing/first/V3S_first.jpg", ref_t0=153.68, duration=7, in_out=(153.98, 159.14),
                WHERE=WHERE_TRUTH, words=[("The", 153.98), ("my", 157.12), ("defense", 158.288)], WORDS=LINE,
                ACT=("She sings it knowingly, looking into the camera, with the hint of a smile in her eyes, as if she has "
                     "seen through the dream.")),
}


def audio_path(shot):
    s = SHOTS[shot]
    return os.path.join(SING, "audio", f"{shot}_vocal_{s['ref_t0']:.2f}_{s['duration']}s.mp3")


def cut_audio(shot):
    s = SHOTS[shot]
    out = audio_path(shot)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    af = []
    for a, b in s.get("mute", []):
        a0, b0 = a - s["ref_t0"], b - s["ref_t0"]
        # volume to zero between a and b, with 20 ms ramps (clip-relative seconds)
        af.append(f"volume=enable='between(t,{a0:.3f},{b0:.3f})':volume=0")
    cmd = [gen.FFMPEG, "-v", "error", "-y", "-ss", f"{s['ref_t0']:.3f}", "-t", f"{s['duration']:.3f}", "-i", VOC]
    if af:
        cmd += ["-af", ",".join(af + ["afade=t=in:st=%.3f:d=0.03" % (s["mute"][-1][1] - s["ref_t0"])])]
    cmd += ["-vn", "-ac", "2", "-ar", "44100", "-c:a", "libmp3lame", "-b:a", "192k", out]
    subprocess.run(cmd, check=True)
    print(os.path.relpath(out, ROOT), gen.probe(out)["duration"], "s")
    return out


def sidecars(shot):
    d = os.path.join(SING, shot)
    out = []
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if f.startswith("take_") and f.endswith(".json") and f.count(".") == 1:
            try:
                out.append((int(f[5:-5]), os.path.join(d, f)))
            except ValueError:
                pass
    return sorted(out)


def submit(shot, n=1, res="720p", dry=False, note=""):
    s = SHOTS[shot]
    d = os.path.join(SING, shot)
    os.makedirs(d, exist_ok=True)
    aud = audio_path(shot)
    if not os.path.exists(aud):
        cut_audio(shot)
    img = gen.ref_image(os.path.join(ROOT, s["first"]), os.path.join(d, "first_2048.jpg"))
    prompt = P.format(WORDS=s["WORDS"], ACT=s["ACT"], WHERE=s["WHERE"])
    assert len(prompt) <= 2000, len(prompt)
    for _ in range(n):
        used = [k for k, _ in sidecars(shot)] + [int(f[5:].split(".")[0]) for f in os.listdir(d) if f.endswith(".spec.json")]
        k = max(used) + 1 if used else 1
        spec = {"model": MODEL, "tag": f"sing_{shot}", "notes": f"{shot} take_{k} {res} {note}".strip(),
                "input": {"prompt": prompt, "image": "file:" + os.path.relpath(img, ROOT),
                          "reference_audios": ["file:" + os.path.relpath(aud, ROOT)], "duration": s["duration"],
                          "resolution": res, "aspect_ratio": "16:9", "generate_audio": False,
                          "use_virtual_avatar": True, "camera_fixed": False}}
        sp = os.path.join(d, f"take_{k}.spec.json")
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
        json.dump(side, open(os.path.join(d, f"take_{k}.json"), "w"), indent=1, ensure_ascii=False)
        print(shot, f"take_{k}", jid, f"${est}")
    print(f"project spend now (est): ${spend.total()}")


def contact_sheet(mp4, out, label, n=6):
    import av
    from PIL import Image, ImageDraw
    with av.open(mp4) as c:
        allf = [f.to_image() for f in c.decode(c.streams.video[0])]
    idx = [round(i * (len(allf) - 1) / (n - 1)) for i in range(n)]
    W = 480
    tiles = []
    for i in idx:
        im = allf[i].convert("RGB")
        im = im.resize((W, round(W * im.height / im.width)))
        dr = ImageDraw.Draw(im)
        dr.rectangle((0, 0, 120, 14), fill=(0, 0, 0))
        dr.text((3, 2), f"{i / 24:.2f}s f{i}", fill=(255, 255, 0))
        tiles.append(im)
    H = max(t.height for t in tiles)
    sheet = Image.new("RGB", (W * 3, H * 2 + 18), (20, 20, 20))
    ImageDraw.Draw(sheet).text((4, 3), label, fill=(255, 255, 255))
    for k, t in enumerate(tiles):
        sheet.paste(t, ((k % 3) * W, 18 + (k // 3) * H))
    sheet.save(out, quality=85)


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
                dst = os.path.join(SING, shot, f"take_{k}.mp4")
                if os.path.exists(dst):
                    os.remove(dst)
                os.link(src, dst)
                side.update(file=os.path.relpath(dst, ROOT), raw_file=j["files"][0], probe=gen.probe(dst),
                            gen_secs=j.get("gen_secs"), latency_secs=j.get("latency_secs"))
                contact_sheet(dst, os.path.join(SING, shot, f"take_{k}_sheet.jpg"), f"{shot} take_{k} {side['res']}")
            elif j["state"] in ("error", "collected_error"):
                side["error"] = (j.get("error") or "")[:800]
            else:
                pending += 1
            json.dump(side, open(p, "w"), indent=1, ensure_ascii=False)
            print(shot, f"take_{k}", side["state"], side.get("file", side.get("error", ""))[:200])
    return pending


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    opts = {a[2:].partition("=")[0]: a[2:].partition("=")[2] or True for a in sys.argv[2:] if a.startswith("--")}
    if cmd == "audio":
        for s in args or SHOTS:
            cut_audio(s)
    elif cmd == "submit":
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
                print(s, f"take_{k}", j["state"], j.get("res"), j.get("est_usd"), j.get("file", ""))
        print(f"project spend (est): ${spend.total()}")
    else:
        print(__doc__)
