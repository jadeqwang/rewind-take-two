#!/usr/bin/env python3
"""Checks for the SFX mix that stand in for ears.

1. Lyric intelligibility: Whisper (faster-whisper large-v3, CPU int8) transcribes the vocal lines that share time
   with a cue, from the original and from mix_preview.wav. Matching transcripts = the cue does not mask the lyric.
2. The announcer: transcribes the 'Continue?' stem alone and in the mix.
3. A spectrogram sheet (original | mix | sfx for each cue window) for visual review: media/sfx/review_sheet.png.

    ~/Documents/moongazing/.venv/bin/python tools/sfx/verify.py
"""
import json
import os
import sys

import numpy as np
import soundfile as sf
import librosa

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "media", "sfx")
SR = 48000

LINES = [  # (label, t0, t1, expected)
    ("P4/P6 shot ... and time stops", 39.7, 42.8, "I get shot and time stops"),
    ("V2d/e I'm back", 83.4, 86.3, "And now I'm back"),
    ("V2f sirens in my mirror", 90.0, 92.85, "sirens in my mirror"),
    ("V2g/h Reload", 92.6, 94.1, "Reload"),
    ("V2m/n shot ... and time stops", 110.2, 113.5, "I get shot and time stops"),
    ("E8 Anomaly detected", 138.8, 140.4, "Anomaly detected"),
    ("V3 down Lake Shore", 160.9, 163.4, "speeding down Lake Shore"),
    ("O4 Never stop", 225.8, 227.2, "Never stop"),
]


def main():
    from faster_whisper import WhisperModel
    m = WhisperModel("large-v3", device="cpu", compute_type="int8", cpu_threads=16)

    def asr(y):
        y16 = librosa.resample(np.ascontiguousarray(y.mean(1) if y.ndim == 2 else y, dtype=np.float32),
                               orig_sr=SR, target_sr=16000)
        segs, _ = m.transcribe(y16, language="en", beam_size=5, vad_filter=False,
                               condition_on_previous_text=False)
        return " ".join(s.text.strip() for s in segs)

    orig = sf.read(os.path.join(ROOT, "analysis", "cinematic", "source.wav"), dtype="float32")[0]
    mix = sf.read(os.path.join(OUT, "mix_preview.wav"), dtype="float32")[0]
    voc = sf.read(os.path.join(ROOT, "analysis", "cinematic", "vocals_bs_roformer_48k.wav"), dtype="float32")[0]
    res = {"lyrics": [], "announcer": {}}
    for lab, a, b, exp in LINES:
        i, j = int(a * SR), int(b * SR)
        r = dict(line=lab, window=[a, b], expected=exp, original=asr(orig[i:j]), mix=asr(mix[i:j]))
        res["lyrics"].append(r)
        print(f"{lab:32s} | orig: {r['original']!r:45s} | mix: {r['mix']!r}")
    cues = json.load(open(os.path.join(OUT, "cues.json")))["cues"]
    c = next((x for x in cues if x["id"] == "continue_vo"), None)   # disabled in build.py since the v3 pass
    if c:
        st = sf.read(os.path.join(OUT, c["file"]), dtype="float32")[0]
        res["announcer"]["stem"] = asr(st)
    else:
        res["announcer"]["stem"] = None
    i, j = int(111.1 * SR), int(111.95 * SR)
    res["announcer"]["mix_111.10-111.95"] = asr(mix[i:j])
    res["announcer"]["original_111.10-111.95"] = asr(orig[i:j])
    print("announcer:", res["announcer"])
    json.dump(res, open(os.path.join(OUT, "verify.json"), "w"), indent=1)
    sheet(cues, orig, mix)


def sheet(cues, orig, mix):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sfx = sf.read(os.path.join(OUT, "sfx_only.wav"), dtype="float32")[0]
    n = len(cues)
    fig, ax = plt.subplots(n, 3, figsize=(15, 1.6 * n))
    for r, c in enumerate(cues):
        a = max(0.0, c["start_s"] - 0.3)
        b = min(len(orig) / SR, max(c["end_s"], c["start_s"] + 0.6) + 0.3)
        b = min(b, a + 6.0)
        i, j = int(a * SR), int(b * SR)
        for k, (lab, x) in enumerate([("original", orig), ("mix", mix), ("sfx", sfx)]):
            S = librosa.amplitude_to_db(np.abs(librosa.stft(x[i:j].mean(1), n_fft=2048, hop_length=256)), ref=1.0)
            ax[r, k].imshow(S, origin="lower", aspect="auto", vmin=-90, vmax=-10, cmap="magma",
                            extent=[a, b, 0, SR / 2000])
            ax[r, k].set_ylim(0, 16)
            ax[r, k].tick_params(labelsize=6)
            ax[r, k].set_title(f"{c['id']} {lab} ({a:.2f}-{b:.2f}s, kHz)", fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "review_sheet.png"), dpi=70)
    print("wrote", os.path.join(OUT, "review_sheet.png"))


if __name__ == "__main__":
    sys.exit(main())
