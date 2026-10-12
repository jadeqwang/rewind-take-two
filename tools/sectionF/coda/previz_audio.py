"""v5-coda previz sound: the coda SFX mix (tools/sfx/build.py --coda, to 234.00) padded to the post-credits end, plus
the post-credits sounds (procedural, in the ring-out's Ab): the door's little spring bell when the door starts to move,
a latch click, and a warm lobby room tone that opens with the door. No speech. Candidate stems are written too.

    $PY tools/sectionF/coda/previz_audio.py [--chime=procedural|musicv2]
Outputs (media/reviews/v5/plans/coda/): chime_procedural.wav, previz_audio.wav (48 kHz 24-bit, t = 0 = film start).
When signed off, these cues move into tools/sfx/build.py (coda mode) with CODA_END raised; see docs/revisions/v5/coda.md.
"""
import os
import sys

import numpy as np
import soundfile as sf
import librosa

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/sfx"))
from dsp import *  # noqa: E402,F401,F403

OUT = os.path.join(ROOT, "media/reviews/v5/plans/coda")
END = 245.20                 # PC2 ends (cut to black)
DOOR_IN = 234.70             # PC1 starts (after 0.70 s of black and silence)
DOOR_MOVE = 235.75           # the door starts to swing in take_1 (clip 1.45 s, used from clip 0.40 s)
PC2 = 237.70


def spring_bell(seed=5):
    """A small shop-door bell on a curled spring: 3-4 quick uneven strikes as the door jolts it, dying away (Ab6/Eb7)."""
    rng = np.random.default_rng(seed)
    y = np.zeros(N(2.6))
    partials = ((1.0, 1.0, 0.55), (2.0, 0.35, 0.3), (2.76, 0.28, 0.22), (4.07, 0.12, 0.12), (5.4, 0.06, 0.08))
    for k, (dt, a) in enumerate([(0.0, 1.0), (0.11, 0.55), (0.19, 0.35), (0.34, 0.22), (0.52, 0.12)]):
        f0 = NOTE["Ab6"] * (1 + rng.uniform(-0.004, 0.004)) if k % 2 == 0 else 2489.0 * (1 + rng.uniform(-0.004, 0.004))
        b = bell(f0, 2.0, partials) * a
        i = N(dt)
        y[i:i + len(b)] += b[:len(y) - i]
    y = hp(y, 900, 2)
    rattle = bp(noise(N(0.45), seed + 3), 3000, 9000, 2) * np.interp(tt(0.45), [0, 0.02, 0.45], [0, 1, 0]) * 0.05
    y[:len(rattle)] += rattle
    return reverb(y / np.max(np.abs(y)), ir(1.4, 0.9, 7000, seed=seed + 9, predelay=0.008), -12)


def latch():
    c = click(901, dur=0.03, lo=900, hi=8000, tau=0.004, modes=((1400, 20, 0.6), (3300, 25, 0.4)))
    return reverb(c / np.max(np.abs(c)), ir(0.6, 0.4, 6000, seed=902), -16)


def room_tone(dur, seed=950):
    """Warm, quiet lobby air: brown-ish noise, low-passed, with a faint 60 Hz-free hum of a big room."""
    n = N(dur)
    x = np.cumsum(noise(n, seed)); x = hp(x - np.mean(x), 40, 2)
    x = lp(x, 900, 2)
    x /= np.max(np.abs(x))
    return np.stack([x, np.roll(x, N(0.013))])


def main(argv):
    chime_kind = next((a.split("=", 1)[1] for a in argv if a.startswith("--chime=")), "procedural")
    mix, sr = sf.read(os.path.join(ROOT, "media/sfx/mix_preview_v5coda.wav"), always_2d=True)
    assert sr == SR
    y = np.zeros((2, N(END)))
    y[:, :mix.shape[0]] = mix.T
    ch = spring_bell()
    sf.write(os.path.join(OUT, "chime_procedural.wav"), (ch.T / np.max(np.abs(ch)) * db2a(-6)).astype(np.float32), SR,
             subtype="FLOAT")
    if chime_kind == "musicv2":
        g, _ = librosa.load(os.path.join(OUT, "chime_musicv2.mp3"), sr=SR, mono=False)
        ch = stereo(g)
    add_at(y, ch / np.max(np.abs(ch)) * db2a(-21), DOOR_MOVE)
    add_at(y, latch() * db2a(-30), DOOR_MOVE - 0.06)
    # lobby room tone: outside it is barely there; it opens with the door and holds under the receptionist's POV
    t0 = DOOR_IN
    rt = room_tone(END - t0)
    t = t0 + tt(END - t0)
    env = db2a(np.interp(t, [t0, t0 + 0.3, DOOR_MOVE, DOOR_MOVE + 0.8, END - 0.12, END], [-90, -38, -38, -24, -24, -90]))
    add_at(y, rt * env, t0)
    peak = np.max(np.abs(y))
    assert peak < db2a(-1.0)
    sf.write(os.path.join(OUT, "previz_audio.wav"), y.T, SR, subtype="PCM_24")
    print("wrote previz_audio.wav", round(len(y[0]) / SR, 3), "s; chime:", chime_kind)


if __name__ == "__main__":
    main(sys.argv[1:])
