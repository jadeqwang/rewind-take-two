#!/usr/bin/env python3
"""Previz-only sound for the v5 merge (docs/revisions/v5/merge.md): the current SFX mix slice plus three procedural
cues, muxed onto the engine previz clip. Not the shared mix: the Execution section moves these cues into
tools/sfx/build.py (one rebuild, coordinated with v5-coda).

    ~/Documents/moongazing/.venv/bin/python tools/v5/merge/previz_audio.py CLIP.mp4 T0 OUT.mp4

  merge_score 203.32  graphite scratch: the triangles scored across the frozen twins
  merge_lift  203.76  b_atomize's sparkle (same seed as the split at 127.88): the pieces lift on the swell
  merge_seat  204.64  b_implode's reversed sparkle (as at 128.32) gathering into a soft wooden latch click as they seat
"""
import os
import subprocess
import sys

import numpy as np
import soundfile as sf

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "sfx"))
from dsp import SR, N, tt, hp, bp, lp, noise, click, expdec, add_at, reverb, ir, db2a  # noqa: E402

FFMPEG = os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg")
MIX = os.path.join(ROOT, "media/sfx/Rewind_cinematic_sfx_mix.mp3")


def pings(dur, count, lo, hi, seed, tau=0.05):     # copy of tools/sfx/build.py pings()
    rng = np.random.default_rng(seed)
    y = np.zeros(N(dur + 0.2))
    for _ in range(count):
        f, t0 = rng.uniform(lo, hi), rng.uniform(0, dur)
        t = tt(0.15)
        g = np.sin(2 * np.pi * f * t) * np.exp(-t / tau) * rng.uniform(0.3, 1.0)
        i = N(t0)
        y[i:i + len(g)] += g[:len(y) - i]
    return y / (np.max(np.abs(y)) + 1e-9)


def cues():
    out = []
    # score: three short pencil strokes (band-passed noise with a rough, scratchy AM)
    y = np.zeros(N(0.42))
    for k, (t0, d) in enumerate(((0.0, 0.12), (0.14, 0.11), (0.27, 0.13))):
        s = bp(noise(N(d), 32300 + k), 1800, 7000, 2)
        s *= np.interp(tt(d), [0, 0.02, d * 0.7, d], [0, 1, 0.8, 0]) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 90 * tt(d))))
        y[N(t0):N(t0) + len(s)] += s
    out.append((203.32, np.stack([y, y]) / np.max(np.abs(y)) * db2a(-16)))
    # lift: the split's atomize sparkle
    y = hp(pings(0.4, 70, 3500, 9500, 13138), 3000, 2)
    out.append((203.76, np.stack([y, np.roll(y, N(0.004))]) * db2a(-12)))
    # seat: the implode (reversed sparkle) swelling into the click on 204.64
    y = hp(pings(0.6, 90, 3500, 9500, 13139), 3000, 2)[::-1][:N(0.62)]
    y = y * np.linspace(0.2, 1.0, len(y)) ** 2
    st = np.stack([np.roll(y, N(0.004)), y]) * db2a(-13)
    ck = click(32640, dur=0.05, lo=400, hi=4000, tau=0.008, modes=((520, 12, 1.0), (1240, 16, 0.5)))
    ck = ck / np.max(np.abs(ck)) * db2a(-11)
    full = np.zeros((2, N(0.62 + 0.3)))
    full[:, :st.shape[1]] += st
    add_at(full, ck, 0.62)
    full = reverb(full, ir(0.6, 0.5, 6000, seed=32641), -14)
    out.append((204.64 - 0.62, full))
    return out


def main(clip, t0, dst):
    t0 = float(t0)
    tmp = os.path.join(os.path.dirname(dst), "_mix_slice.wav")
    subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", f"{t0}", "-t", "7.2", "-i", MIX, "-ar", str(SR), "-ac", "2", tmp], check=True)
    y, sr = sf.read(tmp, always_2d=True)
    y = y.T.copy()
    for t, c in cues():
        add_at(y, c, t - t0)
    peak = np.max(np.abs(y))
    if peak > 0.99:
        y *= 0.99 / peak
    sf.write(tmp, y.T, SR)
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", clip, "-i", tmp, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", dst], check=True)
    os.remove(tmp)
    print(dst)


if __name__ == "__main__":
    main(*sys.argv[1:4])
