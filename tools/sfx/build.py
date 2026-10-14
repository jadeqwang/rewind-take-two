#!/usr/bin/env python3
"""Rewind (cinematic edition): the sound-design layer.

Music first. Every cue is either synthesized here (8-bit blips, ticks, sirens, bells, pencil, cranks, tape stops
made from copies of the track itself) or is a generated source (tools/sfx/generate.py) that is trimmed and
processed here. Each cue is written as its own stem at its exact placement time, then summed into
sfx_only.wav and laid over the untouched original (sample-aligned) for mix_preview.wav and the mp3.

    ~/Documents/moongazing/.venv/bin/python tools/sfx/build.py            # render everything + metrics
    ~/Documents/moongazing/.venv/bin/python tools/sfx/build.py --only=shot1,continue_vo   # stems for a subset
    ~/Documents/moongazing/.venv/bin/python tools/sfx/build.py --coda     # v5: the film extended past the song (*_v5coda)

Outputs (media/sfx/, gitignored): stems/NN_<id>.wav, cues.json, sfx_only.wav, mix_preview.wav,
Rewind_cinematic_sfx_mix.mp3. Metrics per cue (level vs music, spectral overlap, vocal protection) go into
cues.json so the mix can be judged without ears.
"""
import json
import os
import subprocess
import sys

import numpy as np
import soundfile as sf
import librosa

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dsp import *  # noqa: E402,F401,F403
import dsp  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = os.path.join(ROOT, "analysis", "cinematic")
OUT = os.path.join(ROOT, "media", "sfx")
GEN = os.path.join(OUT, "gen")
FFMPEG = os.environ.get("FFMPEG", os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg"))
INPUT_MP3 = os.path.join(ROOT, "inputs", "Rewind - cinematic edition (Remastered).mp3")

SRC = MIX = VOC = INS = None
BEATS = []

# v5 coda (docs/revisions/v5/coda.md; Jade: "credits sound fades out gradually as the life count ticks up in the
# corner"). `--coda` (or REWIND_SFX_CODA=1) builds the extended film: the song is padded with silence to CODA_END, the
# ring-out chord is held (a spectral freeze of the instrumental stem) and fades out slowly under the credits, the 8th
# clock carries on, and every tick of the ITERATION counter gets a soft blip that fades with it. Outputs go beside the
# v4 ones with the suffix _v5coda (stems_v5coda/, cues_v5coda.json, sfx_only_v5coda.wav, mix_preview_v5coda.wav,
# Rewind_cinematic_sfx_mix_v5coda.mp3). Without the flag the v4 mix is rebuilt exactly as before.
CODA = "--coda" in sys.argv[1:] or os.environ.get("REWIND_SFX_CODA") == "1"
# v7 ghost pops (docs/revisions/v7/ghost_pop.md): `--v7pop` = the v5coda film mix (which v6 shipped) plus a Celeste-style
# pop on every ghost that misses at 2:16-2:17 (E7 leap and chasm), minus b_wall_burst (v6's wall-clip motes are gone
# in v7). Outputs get the suffix _v7pop (stems_v7pop/, cues_v7pop.json, sfx_only_v7pop.wav, mix_preview_v7pop.wav,
# Rewind_cinematic_sfx_mix_v7pop.mp3); every other mix is left as it is. Without the flag nothing changes.
V7POP = "--v7pop" in sys.argv[1:]
CODA = CODA or V7POP
CODA_BEAT = 0.4526           # the ring-out beat (timing.json beats 224.137 ... 226.400, interpolated)
CODA_T0 = 226.400            # bar 129 downbeat: the counter reads 4,097 here and ticks +1 every CODA_BEAT
COUNTER_TICKS = [round(CODA_T0 + k * CODA_BEAT, 4) for k in range(1, 17)]   # 4,098 at 226.853 ... 4,113 at 233.642
# v5-build (Jade: "the sound fade of the credits can build right into the coda, actually, so the ticking up of the
# lives is followed by the hotel door ring"): no silent black between them. The beat grid runs on: the door's bell
# rings one beat after the last counter tick, as the door starts to swing (PC1), and the film ends on the grid too.
# Keep in step with tools/sectionF/edl.py (CODA_* there).
CODA_BELL = round(CODA_T0 + 17 * CODA_BEAT, 4)     # 234.0942: the bell = the tick after 4,113
CODA_DOOR_IN = 232.80                              # PC1 fades up from black as the credits finish fading
CODA_END = round(CODA_T0 + 39 * CODA_BEAT, 2)      # 244.05: PC2 cuts to black (the film ends)
CODA_FADE = (226.90, CODA_BELL)   # the held chord and clock fall from 0 dB (whisper end) to -40 dB at the bell
CODA_SUFFIX = "_v7pop" if V7POP else "_v5coda"


def coda_fade_db(t):
    """dB gain of the coda tail at time t: 0 until the whisper ends, then -40 * x^1.7 (x = 0..1 over CODA_FADE: slow
    at first, so the tail is heard fading for several seconds), then a 0.4 s close to silence."""
    t = np.asarray(t, dtype=np.float64)
    a, b = CODA_FADE
    g = -40.0 * np.clip((t - a) / (b - a), 0, 1) ** 1.7
    return np.where(t > b + 0.4, -200.0, np.where(t > b, -40.0 - 160.0 * (t - b), g))


def load():
    global SRC, MIX, VOC, INS, BEATS
    SRC, sr = sf.read(os.path.join(A, "source.wav"), dtype="int16", always_2d=True)
    assert sr == SR
    VOC = sf.read(os.path.join(A, "vocals_bs_roformer_48k.wav"), dtype="float64", always_2d=True)[0].T
    INS = sf.read(os.path.join(A, "instrumental_bs_roformer_48k.wav"), dtype="float64", always_2d=True)[0].T
    if CODA:                                   # pad the song (and its stems) with digital silence to the new film end
        n = N(CODA_END)
        SRC = np.concatenate([SRC, np.zeros((n - SRC.shape[0], SRC.shape[1]), dtype=SRC.dtype)])
        VOC = np.concatenate([VOC, np.zeros((2, n - VOC.shape[1]))], axis=1)
        INS = np.concatenate([INS, np.zeros((2, n - INS.shape[1]))], axis=1)
    MIX = (SRC.astype(np.float64) / 32768.0).T
    BEATS = [b["t"] for b in json.load(open(os.path.join(A, "timing.json")))["beats"]]


def grid(t0, t1, div):
    """Subdivide the tracked beats between t0 and t1 into `div` equal steps per beat (no constant-BPM grid)."""
    out = []
    for a, b in zip(BEATS[:-1], BEATS[1:]):
        for k in range(div):
            t = a + (b - a) * k / div
            if t0 - 1e-6 <= t < t1 - 1e-6:
                out.append(t)
    return out


def gen_src(name, sr_trim_db=-40):
    y, _ = librosa.load(os.path.join(GEN, name), sr=SR, mono=True)
    return y.astype(np.float64)


def onset_index(y, frac=0.5):
    """First sample whose |y| reaches frac * peak (the hit)."""
    pk = np.max(np.abs(y))
    return int(np.argmax(np.abs(y) >= frac * pk))


# ============================================================================= cue generators
# Each returns (stereo array, offset_s): offset is where the array's sample 0 sits relative to the cue's anchor
# time (negative = starts before the anchor). Arrays are normalized to 0 dBFS peak by the framework.
CUES = []
# Cues kept in the file (source, processing, placement) but left out of the mix. They keep their slot in the stem
# numbering so the other stems' file names do not shift.
#   continue_vo: Jade, v2 review at 1:52: "don't use 'continue' voiceover" (2026-10-11).
DISABLED = {"continue_vo"}
V7POP_ONLY = {"g_pop_leap", "g_pop_chasm"}       # v7: the ghost pops, only in the --v7pop mix
V7POP_DROPS = {"b_wall_burst"}                    # v7: no ghost clips the wall in a mote burst any more


def cue(id, t, what, src, priority, gain_db, duck_vocal_db=0.0, duck_music_db=0.0):
    def deco(fn):
        CUES.append(dict(id=id, anchor_s=t, what=what, source=src, priority=priority, gain_db=gain_db,
                         duck_vocal_db=duck_vocal_db, duck_music_db=duck_music_db, fn=fn))
        return fn
    return deco


def tick_sound(seed, tock=False, bright=1.0):
    m = 0.86 if tock else 1.0
    return click(seed, dur=0.014, lo=2500, hi=14000, tau=0.0011,
                 modes=[(3400 * m, 18, 0.5), (5600 * m, 22, 0.4 * bright), (8200 * m, 25, 0.3 * bright)])


ROOM = None


def room():
    global ROOM
    if ROOM is None:
        ROOM = ir(0.6, 0.35, 7000, seed=11, predelay=0.004)
    return ROOM


# ---------------------------------------------------------------- cold open (C2 rewind teaser)
@cue("rew_button", 1.90, "C2 starts: cassette REWIND key goes down (press + latch)", "procedural", "optional", -31)
def _():
    y = np.zeros(N(0.12))
    p = click(1, dur=0.03, lo=800, hi=7000, tau=0.003, modes=[(1250, 30, 0.6), (2900, 40, 0.4)])
    l = click(2, dur=0.03, lo=1200, hi=9000, tau=0.002, modes=[(1900, 30, 0.5), (4100, 40, 0.3)])
    y[:len(p)] += p
    y[N(0.034):N(0.034) + len(l)] += 0.7 * l
    y[:N(0.08)] += 0.35 * thump(140, 0.08, 0.018)
    return reverb(y, room(), -16), 0.0


SPEED_STEPS = [(1.90, 2), (3.68, 4), (5.48, 8), (6.36, 16)]   # HUD: <<x2 x4 x8 x16 (bar 2, bar 3, bar 4, bar 4 beat 3)
REW_END = 7.24


def speed_curve(t):
    s = np.zeros_like(t)
    for i, (ts, v) in enumerate(SPEED_STEPS):
        prev = SPEED_STEPS[i - 1][1] if i else 0.0
        ramp = 0.30 if i == 0 else 0.14
        x = np.clip((t - ts) / ramp, 0, 1)
        x = x * x * (3 - 2 * x)
        s = np.where(t >= ts, prev + (v - prev) * x, s)
    return s


@cue("rewind_whir", 1.90, "C2 tape-rewind whir: the song itself read backwards at x2/x4/x8/x16 (octave steps keep "
     "it in key) through tape-head colour, + motor tone on Bb + hiss; hard stop at 7.24", "procedural (from the mix)",
     "essential", -29)
def _():
    dur = REW_END - 1.90
    t = 1.90 + np.arange(N(dur)) / SR
    s = speed_curve(t)
    mono = MIX.mean(0)
    P0 = N(213.0)                                  # start reading at the outro and run backwards through the film
    reads, cuts = [], []
    for v in (2, 4, 8, 16):
        src = lp(mono, 0.45 * (SR / 2) / v, 8)
        reads.append(varispeed(src, P0, s, backwards=True))
    # choose the anti-aliased read for the current speed (next power of two up), crossfaded over ramps
    w = np.zeros((4, len(t)))
    lv = np.log2(np.maximum(s, 2.0)) - 1        # 0..3
    for k in range(4):
        w[k] = np.clip(1 - np.abs(lv - k), 0, 1)
    w /= w.sum(0, keepdims=True)
    ch = sum(w[k] * reads[k] for k in range(4))
    ch = bp(ch, 650, 7500, 4)
    ch = np.tanh(2.0 * ch / (np.max(np.abs(ch)) + 1e-9))
    ch *= 1 + 0.18 * np.sin(2 * np.pi * 6.3 * (t - 1.9)) * np.sin(2 * np.pi * 0.7 * (t - 1.9))   # flutter
    f = 58.27 * s                                                     # motor: Bb1 * speed -> Bb2..Bb5
    ph = 2 * np.pi * np.cumsum(f) / SR
    motor = lp(np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.2 * np.sin(3 * ph), 3000, 2)
    hiss = hp(noise(len(t), 21), 4000, 2)
    y = ch / np.max(np.abs(ch)) + 0.10 * motor / np.max(np.abs(motor)) + 0.05 * hiss / np.max(np.abs(hiss))
    cres = db2a(np.interp(t, [1.9, 3.68, 5.48, 6.36, 7.24], [-9, -6, -3, -1.5, 0]))
    y *= cres * np.clip(s / 2, 0, 1) ** 0.7
    y = fade(y, 0, 0.008)
    l = y
    r = np.concatenate([np.zeros(N(0.0035)), y[:-N(0.0035)]])
    return np.stack([l, 0.7 * l + 0.3 * r]), 0.0


@cue("rewind_ticks", 1.90, "C2 accelerating clock ticks: 8ths (bar 2) -> 16ths (bar 3) -> 32nds (5.48) -> 64ths "
     "(6.36) into the 7.24 landing; on the tracked beats", "procedural", "essential", -26)
def _():
    y = np.zeros((2, N(REW_END - 1.90 + 0.05)))
    plan = [(1.90, 3.68, 2, 1.0), (3.68, 5.48, 4, 0.78), (5.48, 6.36, 8, 0.6), (6.36, REW_END, 16, 0.5)]
    i = 0
    for a, b, div, amp in plan:
        ts = grid(a, b, div)
        for j, tk in enumerate(ts):
            g = amp * (1 + 0.5 * (tk - 6.36) / 0.88 if div == 16 else 1)
            s = tick_sound(100 + i, tock=(i % 2 == 1)) * g * (0.92 if i % 2 else 1.0)
            add_at(y, pan(s, 0.15 if i % 2 else -0.15), tk - 1.90)
            i += 1
    return y, 0.0


@cue("rewind_stop", 7.24, "C3 landing: STOP key clack + transport thunk as the whir cuts (sub swell, title)",
     "procedural", "essential", -21)
def _():
    y = np.zeros(N(0.25))
    c = click(5, dur=0.04, lo=600, hi=11000, tau=0.004, modes=[(900, 25, 0.8), (2100, 30, 0.4)])
    y[:len(c)] += c
    y[:N(0.15)] += 0.6 * thump(90, 0.15, 0.04)
    return reverb(y, room(), -14), 0.0


# ---------------------------------------------------------------- pre-drop shot, tape stop, pause menu
def gunshot(speed, lpf, rt60, tail_end, seed, pan_p):
    g = gen_src("gunshot_far.mp3")
    i0 = max(0, onset_index(g, 0.3) - N(0.004))
    g = g[i0:i0 + N(1.6)]
    g = varispeed(g, 0, np.full(int(len(g) / speed), speed))      # slower = deeper, dreamier
    g = lp(g, lpf, 4)
    g = g / np.max(np.abs(g))
    body = thump(52, 0.4, 0.11) * 0.8
    crack = lp(noise(N(0.02), seed) * expdec(N(0.02), 0.003), 1800, 2) * 0.5
    y = np.zeros(max(len(g), N(0.4)))
    y[:len(g)] += g
    y[:len(body)] += body
    y[:len(crack)] += crack
    y = reverb(pan(y, pan_p), ir(2.0, rt60, 2200, seed=seed, predelay=0.02, width=1.0), -4, dry=0.8)
    n = N(tail_end)
    y = y[:, :n]
    return fade(y, 0, tail_end * 0.55, shape=1.5)


@cue("shot1", 40.24, "P4 whispered 'shot': muffled, slowed distant gunshot (lowpassed under the whisper's "
     "fricative band) with a dreamy tail into the freeze", "music-v2 'gunshot_far' + procedural body",
     "essential", -19, duck_vocal_db=3)
def _():
    return gunshot(0.8, 1400, 1.4, 1.05, 31, -0.1), 0.0


@cue("tapestop1", 40.65, "P5 tape stop: a copy of the last instrumental beat (40.21-40.65, stem) slowed to a halt "
     "over 0.6 s after the band's hard stop", "procedural (instrumental stem copy)", "essential", -26)
def _():
    y, s = tapestop(INS, 40.21, 0.5, 1.6)
    y = lp(y, 7000, 2) * np.sqrt(s)
    return fade(y, 0.004, 0.08), 0.0


def blip_seq(notes, duty=0.25, gap=0.008, decay=0.06):
    parts = []
    for nm, d in notes:
        p = pulse(NOTE[nm], d, duty) * expdec(N(d), decay)
        parts += [fade(p, 0.002, 0.004, 1), np.zeros(N(gap))]
    return np.concatenate(parts)


@cue("pause_open", 41.40, "P6 pause menu appears: 2-note 8-bit chime Bb5 -> F6 (in the hole 41.22-41.89)",
     "procedural (pulse wave)", "essential", -31, duck_vocal_db=2)
def _():
    y = blip_seq([("Bb5", 0.05), ("F6", 0.08)])
    return reverb(y, room(), -20), 0.0


@cue("cursor_move", 41.62, "P6 cursor RESUME -> REWIND: single 8-bit tick Bb6", "procedural (pulse wave)",
     "essential", -33, duck_vocal_db=2)
def _():
    y = blip_seq([("Bb6", 0.028)], duty=0.5, decay=0.02)
    return reverb(y, room(), -20), 0.0


@cue("menu_select", 42.06, "P6 REWIND selected on 'st-': rising 8-bit arpeggio F5 Bb5 C6 F6 over the riser",
     "procedural (pulse wave)", "essential", -31, duck_vocal_db=2)
def _():
    y = blip_seq([("F5", 0.022), ("Bb5", 0.022), ("C6", 0.022), ("F6", 0.09)], gap=0.004, decay=0.08)
    return reverb(y, room(), -18), 0.0


# ---------------------------------------------------------------- verse 2: chase
def siren(t, f_lo, f_hi, period, phase, doppler=0.006):
    tn = (t - t[0]) / (t[-1] - t[0])
    x = 0.5 - 0.5 * np.cos(2 * np.pi * (t - t[0]) / period + phase)
    f = np.exp(np.log(f_lo) + (np.log(f_hi) - np.log(f_lo)) * x) * (1 + doppler * (1 - 2 * tn))
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = sum(np.sin(k * ph) / k ** 1.2 for k in range(1, 7))
    return bp(y, 450, 3200, 2)


def distant(y, lpf, rt60, seed, wet=-3, dry=0.6, p=0.0):
    y = lp(y, lpf, 2)
    return reverb(pan(y, p), ir(2.8, rt60, lpf, seed=seed, predelay=0.03), wet, dry)


@cue("siren_v2a", 56.54, "V2a car chase: two distant police sirens (wail Bb4<->F5 and C5<->F5, 2-bar period), "
     "lowpassed and reverberant, swelling in and out over 56.54-63.62", "procedural", "optional", -25)
def _():
    dur = 63.62 - 56.54
    t = 56.54 + np.arange(N(dur)) / SR
    a = siren(t, NOTE["Bb4"], NOTE["F5"], 3.54, 0.0) * np.interp(t, [56.54, 57.8, 59.4, 61.4], [0, 1, 0.8, 0], right=0)
    b = siren(t, NOTE["C5"], NOTE["F5"], 3.54, 2.2) * np.interp(t, [59.4, 61.0, 62.6, 63.62], [0, 0.85, 0.6, 0],
                                                                  left=0, right=0)
    y = distant(a, 2200, 2.4, 41, p=-0.35) + distant(b, 2000, 2.4, 43, p=0.4)
    return fade(y, 0.05, 1.2), 0.0


@cue("bridge_bell", 72.48, "V2c the bascule bridge rises: distant warning bell (Bb5 bell partials) on 8ths, "
     "72.48-75.9, ducked under the 'oh' swell", "procedural", "optional", -25, duck_vocal_db=8)
def _():
    y = np.zeros((2, N(4.8)))
    rng = np.random.default_rng(5)
    for i, tk in enumerate(grid(72.48, 75.9, 2)):
        b = bell(NOTE["Bb5"], 0.9) * (1.0 if i % 2 == 0 else 0.78) * rng.uniform(0.9, 1.05)
        add_at(y, pan(b, -0.25), tk - 72.48)
    t = 72.48 + np.arange(y.shape[1]) / SR
    y *= np.interp(t, [72.48, 72.9, 75.0, 76.0], [0.55, 1.0, 0.9, 0.0])
    y = lp(y, 5000, 2)
    w = reverb(y.mean(0), ir(2.4, 1.8, 4500, seed=51, predelay=0.025), -5, 0.0)
    return y + w[:, :y.shape[1]], 0.0


@cue("jump_whoosh", 84.04, "V2d car airborne in the full-band hole: slow-motion air (sub rumble + high air, "
     "skipping the vocal band of the held 'I'm')", "procedural", "optional", -31, duck_vocal_db=0)
def _():
    n = N(0.80)
    t = np.arange(n) / SR
    env = np.interp(t, [0, 0.45, 0.74, 0.80], [0.0, 1.0, 0.9, 0.0])
    rum = lp(noise(n, 61), 220, 4) * 2.0
    air = bp(noise(n, 62), 4500, 10000, 2) * (0.25 + 0.75 * t / t[-1])
    y = (rum / np.max(np.abs(rum)) + 0.5 * air / np.max(np.abs(air))) * env
    return np.stack([y, np.roll(y, N(0.006))]), 0.0


@cue("car_slam", 84.86, "V2e 'back' lands on the bar-49 downbeat: car slam (generated hit) + sub thud + "
     "spark scrape sweeping L->R", "music-v2 'car_slam' + procedural", "essential", -15, duck_vocal_db=3)
def _():
    g = gen_src("car_slam.mp3")
    i0 = max(0, onset_index(g, 0.4) - N(0.003))
    g = g[i0:i0 + N(0.9)]
    g = fade(hp(g, 70, 2), 0, 0.5) / np.max(np.abs(g))
    th = thump(48, 0.35, 0.1)
    n = N(0.9)
    tt_ = np.arange(n) / SR
    crackle = np.zeros(n)
    rng = np.random.default_rng(71)
    for k in rng.integers(0, n, 160):
        crackle[k] = rng.uniform(-1, 1) * np.exp(-k / SR / 0.25)
    sparks = bp(noise(n, 72) * np.exp(-tt_ / 0.2) * 0.2 + crackle, 3000, 11000, 2)
    sparks = sparks / (np.max(np.abs(sparks)) + 1e-9)
    y = np.zeros((2, n))
    y[:, :len(g)] += pan(g, 0.0)
    y[:, :len(th)] += pan(0.7 * th, 0.0)
    sp = np.cos(np.linspace(0, np.pi / 2, n))
    y += 0.35 * np.stack([sparks * sp, sparks * np.sqrt(1 - sp ** 2)])
    return y, 0.0


@cue("siren_v2f", 88.60, "V2f 'sirens in my mirror': one far siren swelling into the vocal rest 89.26-90.19, "
     "fading as the line starts and ducked under it", "procedural", "optional", -26, duck_vocal_db=10)
def _():
    dur = 92.70 - 88.60
    t = 88.60 + np.arange(N(dur)) / SR
    a = siren(t, NOTE["Bb4"], NOTE["F5"], 3.54, -1.2) * np.interp(t, [88.6, 89.3, 90.1, 90.5, 92.0, 92.7],
                                                                  [0, 1, 1, 0.3, 0.12, 0])
    return fade(distant(a, 1600, 2.6, 81, p=0.3), 0.05, 0.4), 0.0


@cue("train_smash", 92.79, "V2g Kaizo trap: L train smashes down (generated metal crash + sub), hard-cut at "
     "92.935 with the cut to black", "music-v2 'train_smash' + procedural", "essential", -20)
def _():
    g = gen_src("train_smash.mp3")
    i0 = max(0, onset_index(g, 0.4) - N(0.003))
    g = g[i0:i0 + N(0.145)] / np.max(np.abs(g))
    th = thump(42, 0.145, 0.09)
    y = np.zeros(N(0.145))
    y[:len(g)] += g
    y[:len(th)] += 0.8 * th
    return fade(pan(y, 0.0), 0.0, 0.012, 1), 0.0


@cue("reload_click", 92.955, "V2g->h gun-slide reload in the 0.28 s vocal gap: 'chk' (92.955) + 'chk' (93.015)",
     "procedural", "essential", -17)
def _():
    y = np.zeros(N(0.1))
    a = click(91, dur=0.03, lo=1500, hi=12000, tau=0.0025, modes=[(2400, 30, 0.6), (4300, 35, 0.5), (6800, 40, 0.4)])
    b = click(92, dur=0.03, lo=1200, hi=12000, tau=0.003, modes=[(2100, 30, 0.6), (3900, 35, 0.5), (7400, 40, 0.3)])
    y[:len(a)] += a
    y[:N(0.03)] += 0.3 * thump(180, 0.03, 0.008)
    y[N(0.06):N(0.06) + len(b)] += 1.1 * b
    return reverb(y, room(), -18), 0.0


@cue("loading_blip", 93.07, "V2h LOADING screen: soft 8-bit boot blip F6 -> Bb6 on 'Reload.' (ducked under it)",
     "procedural (pulse wave)", "optional", -35, duck_vocal_db=4)
def _():
    return reverb(blip_seq([("F6", 0.03), ("Bb6", 0.05)], duty=0.5, gap=0.0, decay=0.05), room(), -20), 0.0


# ---------------------------------------------------------------- build shot, continue?
@cue("shot2", 110.78, "V2m whispered 'shot' #2: the same muffled gunshot from another angle (slower, panned R, "
     "shorter tail cleared before 'Continue?')", "music-v2 'gunshot_far' + procedural body", "essential", -20,
     duck_vocal_db=3)
def _():
    return gunshot(0.75, 1300, 1.0, 0.62, 33, 0.25), 0.0


@cue("tapestop2", 111.22, "V2n freeze: tape stop of the last beat (instrumental 110.78-111.22) over 0.36 s",
     "procedural (instrumental stem copy)", "optional", -30)
def _():
    y, s = tapestop(INS, 110.78, 0.36, 1.4)
    y = lp(y, 6000, 2) * np.sqrt(s)
    return fade(y, 0.004, 0.06), 0.0


@cue("continue_vo", 111.27, "V2n arcade announcer 'Continue?' (eleven-v3, Arnold; tape-slowed to 0.89x for depth, "
     "cabinet-speaker EQ, short hall) in the quiet window 111.26-111.62, clearing before 'time' (111.94)",
     "eleven-v3 'continue_arnold_a'", "essential", -19)
def _():
    v = gen_src("continue_arnold_a.mp3")
    e = np.abs(v) > db2a(-40) * np.max(np.abs(v))
    idx = np.where(e)[0]
    v = v[max(0, idx[0] - N(0.005)): idx[-1] + N(0.03)]
    v = varispeed(v, 0, np.full(int(len(v) / 0.89), 0.89))
    v = bp(v, 150, 5200, 2)
    v = v + 0.25 * reson(v, 2600, 2.0) * 4
    v = np.tanh(1.6 * v / np.max(np.abs(v)))
    y = reverb(v, ir(0.9, 0.55, 5000, seed=99, predelay=0.012), -15)
    return fade(y[:, :len(v) + N(0.12)], 0.002, 0.10), 0.0


@cue("rewind_slam", 112.66, "V2n her hand slams the arcade REWIND button on 'st-': plastic microswitch clack",
     "procedural", "optional", -30, duck_vocal_db=3)
def _():
    y = np.zeros(N(0.1))
    c = click(95, dur=0.04, lo=900, hi=9000, tau=0.003, modes=[(1800, 20, 0.6), (3200, 25, 0.4)])
    y[:len(c)] += c
    y[:N(0.06)] += 0.5 * thump(120, 0.06, 0.015)
    return reverb(y, room(), -16), 0.0


# ---------------------------------------------------------------- anomaly detected, glitch break
@cue("anomaly_glitch", 139.00, "E8 'Anomaly detected.': sparse HUD glitch ticks / bit-crushed bursts / micro-"
     "stutters on a 32nd grid, high-passed above the robot voice", "procedural (+ grains of the mix)", "optional",
     -15)
def _():
    T0, T1 = 139.00, 140.20
    y = np.zeros((2, N(T1 - T0 + 0.1)))
    rng = np.random.default_rng(139)
    mono = MIX.mean(0)
    for tk in grid(T0, T1, 8):
        r = rng.random()
        if r > 0.55:
            continue
        kind = rng.choice(["click", "crush", "stutter"], p=[0.55, 0.3, 0.15])
        if kind == "click":
            s = click(int(rng.integers(1e6)), dur=0.006, lo=3000, hi=15000, tau=0.0008)
        elif kind == "crush":
            n = N(rng.uniform(0.015, 0.035))
            hold = int(SR / rng.choice([2000, 3000, 4000]))
            s = np.repeat(noise(n // hold + 1, int(rng.integers(1e6))), hold)[:n]
            s = np.round(s * 3) / 3 * expdec(n, 0.012)
            s = hp(s, 2500, 2)
        else:
            g = hp(mono[N(tk):N(tk + 0.012)], 2500, 2)
            g = fade(g / (np.max(np.abs(g)) + 1e-9), 0.001, 0.002, 1)
            s = np.concatenate([g, g, g]) * np.repeat([1.0, 0.7, 0.45], len(g))
        add_at(y, pan(s / (np.max(np.abs(s)) + 1e-9) * rng.uniform(0.5, 1.0), rng.uniform(-0.6, 0.6)), tk - T0)
    return y, 0.0


@cue("pencil_stroke", 146.32, "G3 she draws one stroke in the air: graphite-on-paper scratch (velocity-shaped "
     "grainy noise, paper resonances), panned L->R with the stroke", "procedural", "essential", -28)
def _():
    dur = 1.25
    n = N(dur)
    t = np.arange(n) / SR
    v = np.interp(t, [0, 0.07, 0.35, 0.6, 0.85, 1.0, dur], [0, 1.0, 0.8, 1.0, 0.7, 0.35, 0])
    grain = lp(noise(n, 141), 110, 2)
    grain = 1 + 0.8 * grain / np.max(np.abs(grain))
    base = bp(noise(n, 142), 1800, 9500, 2)
    base = base + 0.3 * reson(noise(n, 143), 3300, 4) + 0.2 * reson(noise(n, 144), 5800, 5)
    crack = np.zeros(n)
    rng = np.random.default_rng(145)
    for k in rng.integers(0, n, 220):
        crack[k] = rng.uniform(-1, 1) * v[k]
    crack = bp(crack, 3000, 12000, 2)
    y = base / np.max(np.abs(base)) * v ** 1.2 * grain + 0.6 * crack / np.max(np.abs(crack))
    bright = lp(y, 4500, 2)
    y = bright + (y - bright) * v                                   # faster stroke -> brighter
    sp = np.linspace(0.2, 1.3, n)
    st = np.stack([y * np.cos(sp), y * np.sin(sp)])
    return reverb(st.mean(0), room(), -20, 0.0)[:, :n] + st, 0.0


@cue("crank_ratchet", 147.64, "G4 Monument Valley crank wind-up: wooden ratchet clicks on 32nds 147.64-148.03",
     "procedural", "essential", -26)
def _():
    y = np.zeros((2, N(0.5)))
    ts = grid(147.64, 148.04, 8)
    for i, tk in enumerate(ts):
        c = click(150 + i, dur=0.025, lo=700, hi=7000, tau=0.0025, modes=[(1500, 12, 0.7), (3100, 15, 0.4)])
        c[:N(0.02)] += 0.25 * thump(260, 0.02, 0.006)
        add_at(y, pan(c * (0.5 + 0.5 * i / max(1, len(ts) - 1)), -0.1), tk - 147.64)
    return reverb(y, room(), -16), 0.0


@cue("crank_clunk", 148.08, "G4 the city clunks 90 deg on the returning kick: tuned wooden/stone clunk (F2 body, "
     "F3 knock, short grind)", "procedural", "essential", -21)
def _():
    n = N(0.6)
    y = np.zeros(n)
    y[:N(0.45)] += thump(NOTE["F2"], 0.45, 0.14, f_start=130)
    y[:N(0.3)] += 0.35 * thump(NOTE["F3"], 0.3, 0.06)
    k = noise(N(0.12), 160) * expdec(N(0.12), 0.02)
    knock = reson(k, 350, 8) + 0.6 * reson(k, 720, 10)
    y[:len(knock)] += 0.8 * knock / np.max(np.abs(knock))
    gr = bp(noise(N(0.14), 161), 200, 1500, 2) * np.interp(np.arange(N(0.14)), [0, N(0.02), N(0.14)], [0, 1, 0])
    y[N(0.01):N(0.01) + len(gr)] += 0.25 * gr / np.max(np.abs(gr))
    return reverb(y, ir(1.2, 0.8, 3000, seed=162, predelay=0.01), -14), 0.0


@cue("mobius_crank", 161.64, "M2 Jade turns the crank on the Mobius road: ratchet clicks on 16ths through the "
     "instrumental hole 161.63-162.27, soft clunk on the 162.30 chord re-attack", "procedural", "optional", -29,
     duck_vocal_db=3)
def _():
    y = np.zeros((2, N(1.2)))
    ts = grid(161.64, 162.27, 4)
    for i, tk in enumerate(ts):
        c = click(170 + i, dur=0.025, lo=700, hi=7000, tau=0.0025, modes=[(1500, 12, 0.7), (3100, 15, 0.4)])
        add_at(y, pan(c * 0.8, 0.2), tk - 161.64)
    cl = thump(NOTE["F2"], 0.4, 0.1, f_start=120) * 0.9
    k = noise(N(0.1), 171) * expdec(N(0.1), 0.02)
    cl[:len(k)] += 0.5 * reson(k, 350, 8) / np.max(np.abs(reson(k, 350, 8)))
    add_at(y, pan(cl, 0.0), 162.30 - 161.64)
    return reverb(y, room(), -16), 0.0


# ---------------------------------------------------------------- end of the final drop, outro, new game+
OUTRO_TICKS = [223.685 + 0.226 * k for k in range(18)]          # ring-out 8ths (beats interpolated, 0.452 s)


@cue("outro_clock", 223.685, "Ring-out -> O4: the intro's 8th-note clock returns, fading in under the decaying "
     "pad, ducked under the final whisper, fading by 227.6", "procedural", "essential", -25, duck_vocal_db=9)
def _():
    y = np.zeros((2, N(4.2)))
    for i, tk in enumerate([x for x in OUTRO_TICKS if x < 227.6]):
        g = np.interp(tk, [223.685, 225.0, 226.9, 227.6], [0.25, 1.0, 0.9, 0.35])
        add_at(y, pan(tick_sound(300 + i, tock=i % 2 == 1) * g, -0.12 if i % 2 else 0.12), tk - 223.685)
    return reverb(y, room(), -16), 0.0


@cue("counter_roll", 226.852, "O4 ITERATION 4,097 keeps rolling: 8-bit digit flicks after the whisper, "
     "accelerating like the cold-open rewind and fading out (the film loops)", "procedural (pulse wave)",
     "essential", -32)
def _():
    gaps = [0.226, 0.17, 0.13, 0.10, 0.08, 0.066, 0.056]
    ts = np.concatenate([[0], np.cumsum(gaps)])
    y = np.zeros(N(ts[-1] + 0.1))
    for i, tk in enumerate(ts):
        b = blip_seq([("F6" if i % 2 == 0 else "Bb6", 0.022)], duty=0.5, gap=0.0, decay=0.015)
        g = db2a(-2.2 * i)
        y[N(tk):N(tk) + len(b)] += b * g
    return reverb(y, room(), -18), 0.0


# ---------------------------------------------------------------- v3: instance B's restaged chase (94.06-141.00)
# Cue list from rev-B (2026-10-11). Appended after the v2 cues so the v2 stem numbers do not shift. Agents stand at
# frame left in every Verse 2 shot, so their sounds pan left.
def whoosh_rise(dur, f0, f1, seed):
    """Air whoosh whose band rises f0 -> f1: overlap-added 20 ms grains of band-passed noise."""
    n, hop = N(dur), N(0.01)
    y = np.zeros(n + N(0.04))
    win = np.hanning(N(0.02))
    for k, i in enumerate(range(0, n, hop)):
        f = f0 * (f1 / f0) ** (i / n)
        g = bp(noise(N(0.02), seed + k), f * 0.7, min(f * 1.5, 18000), 2) * win
        y[i:i + len(g)] += g
    return y[:n] / (np.max(np.abs(y)) + 1e-9)


def pings(dur, count, lo, hi, seed, tau=0.05):
    """Crystalline sparkle: short random sine pings between lo and hi Hz over dur."""
    rng = np.random.default_rng(seed)
    y = np.zeros(N(dur + 0.2))
    for _ in range(count):
        f, t0 = rng.uniform(lo, hi), rng.uniform(0, dur)
        t = tt(0.15)
        g = np.sin(2 * np.pi * f * t) * np.exp(-t / tau) * rng.uniform(0.3, 1.0)
        i = N(t0)
        y[i:i + len(g)] += g[:len(y) - i]
    return y / (np.max(np.abs(y)) + 1e-9)


def turf(seed, p):
    """A round hitting turf: low 'thup' + a short grass/dirt scuff."""
    th = thump(90, 0.09, 0.02, seed=seed)
    sc = bp(noise(N(0.07), seed + 1), 900, 5000, 2) * expdec(N(0.07), 0.015)
    y = np.zeros(N(0.1))
    y[:len(th)] += th
    y[:len(sc)] += 0.5 * sc / np.max(np.abs(sc))
    return pan(y, p)


def miss(seed, turf_p, tail=0.3):
    """Suppressed distant pop (gunshot_far, quicker and shorter than shot2) from frame left, turf 40 ms later."""
    y = np.zeros((2, N(max(tail, 0.2) + 0.12)))
    g = gunshot(1.05, 1700, 0.5, tail, seed, -0.6)
    y[:, :g.shape[1]] += g
    add_at(y, db2a(-3) * turf(seed + 5, turf_p), 0.04)
    return y


@cue("b_shadow_crumble", 97.18, "V2i her graphite shadow crumbles at the chasm wall: dry pencil-lead crumble", "procedural",
     "optional", -33)
def _():
    dur = 0.28
    rng = np.random.default_rng(9718)
    y = np.zeros(N(dur + 0.03))
    for t0 in np.sort(rng.uniform(0, dur, 40)):
        c = click(int(rng.integers(1e6)), dur=0.008, lo=2000, hi=9000, tau=0.0015)
        add = c * rng.uniform(0.3, 1.0) * (1 - t0 / dur) ** 0.7
        i = N(t0)
        y[i:i + len(add)] += add
    return reverb(y, room(), -20), 0.0


@cue("b_dash", 97.92, "V2i Celeste dash on 'race' (after an 80 ms 2-frame freeze): bright rising air whoosh + soft "
     "glassy ring ping for the white ring", "procedural", "essential", -20, duck_vocal_db=3)   # B: +6 dB (masked at -26)
def _():
    w = whoosh_rise(0.26, 900, 9000, 9792) * np.interp(tt(0.26), [0, 0.03, 0.18, 0.26], [0, 1, 0.8, 0])
    t = tt(0.5)
    ring = (np.sin(2 * np.pi * 2637 * t) + 0.4 * np.sin(2 * np.pi * 3951 * t)) * np.exp(-t / 0.12)
    y = np.zeros((2, N(0.55)))
    add_at(y, pan(w, -0.3), 0.0)
    add_at(y, 0.35 * stereo(ring), 0.05)
    return reverb(y, room(), -16), 0.0


@cue("b_land_skid", 98.16, "V2j she lands on the lawn and skids to 98.28: soft thud + 0.12 s grass scuff", "procedural",
     "optional", -31)
def _():
    y = np.zeros(N(0.2))
    th = thump(70, 0.15, 0.04)
    y[:len(th)] += th
    sc = bp(noise(N(0.12), 9816), 1200, 6000, 2) * np.interp(tt(0.12), [0, 0.01, 0.12], [0, 1, 0])
    y[N(0.02):N(0.02) + len(sc)] += 0.5 * sc / np.max(np.abs(sc))
    return y, 0.0


for _k, (_t, _p, _pri, _g) in enumerate([(98.94, 0.25, "essential", -21), (99.38, 0.35, "optional", -27),   # B: miss_1 +6 dB
                                         (99.82, 0.15, "optional", -27), (100.26, 0.3, "optional", -27)]):
    def _mk(k=_k, p=_p):
        return lambda: (miss(9894 + 10 * k, p), 0.0)
    cue(f"b_miss_{_k + 1}", _t, f"V2j agent's shot #{_k + 1} misses her: suppressed distant pop from frame left + turf "
        "'thup' 40 ms later at screen centre-right", "music-v2 'gunshot_far' + procedural", _pri, _g,
        duck_vocal_db=3)(_mk())


# v4: this miss now lands in turf (the gunfire restage), so it gets the turf-miss sound of the 102.00 miss, new seed.
# v3: "punches through the park notice board": gunshot + dry wood crack and splinters (gain -28)
@cue("b_miss_board", 101.14, "V2j a miss into the turf behind her (was the notice-board crack in v3)",
     "music-v2 'gunshot_far' + procedural", "optional", -30, duck_vocal_db=3)
def _():
    return miss(10114, 0.2), 0.0


@cue("b_miss_turf", 102.00, "V2j the last miss, into turf behind her", "music-v2 'gunshot_far' + procedural", "optional",
     -30, duck_vocal_db=3)
def _():
    return miss(10200, -0.1), 0.0


@cue("b_spawn", 107.75, "V2k an agent flickers into existence at the hotel corner, on/off/on: three tiny 8-bit blips "
     "at 107.75 / 107.79 / 107.83", "procedural (pulse wave)", "essential", -24)   # B: +6 dB (masked at -30)
def _():
    b = pulse(NOTE["C7"], 0.022, duty=0.5) * expdec(N(0.022), 0.008)
    y = np.zeros(N(0.13))
    for t0, g in [(0.0, 1.0), (0.04, 0.8), (0.08, 0.9)]:
        y[N(t0):N(t0) + len(b)] += g * b
    return pan(hp(y, 1500, 2), -0.4), 0.0


def scuff(d, seed):
    """Sneaker scuff on pavement: a squeak gliding down + scraped noise, d seconds."""
    t = tt(d)
    f = 2300 - 500 * t / d + 60 * np.sin(2 * np.pi * 23 * t)
    sq = np.sin(2 * np.pi * np.cumsum(f) / SR)
    scr = bp(noise(len(t), seed), 800, 5000, 2)
    y = 0.35 * sq + scr / np.max(np.abs(scr))
    return fade(y * np.interp(t, [0, 0.02, 0.6 * d, d], [0, 1, 0.6, 0]), 0.0, 0.05)


@cue("b_bump", 108.31, "V2k she rounds the corner and runs smack into the agent's chest (shoulder meets chest 108.29-108.33): soft body-thump, "
     "cloth, no impact sting (replaces b_skid)", "procedural", "optional", -30)
def _():
    y = np.zeros(N(0.25))
    th = thump(80, 0.18, 0.04, seed=10816)
    y[:len(th)] += th
    cl = lp(bp(noise(N(0.12), 10817), 300, 2500, 2), 2000, 2) * expdec(N(0.12), 0.03)
    y[:len(cl)] += 0.4 * cl / np.max(np.abs(cl))
    return lp(y, 1800, 2), 0.0


# v4 (docs/revisions/v4/plans/coop.md): E3 is out and the picture from the ghost ladder to the split sits two bars
# earlier, so these four cues move 3.50 s earlier with it, onto the same beats of the earlier bars.
# v3: b_boost 130.04, b_pileup 130.94, b_atomize 131.38, b_implode 131.82 (swelling into 132.26).
@cue("b_boost", 126.56, "E6a the blue ghost launches her straight up out of the agents' swarm: short upward air-whoosh "
     "(heave from about 125.65) with a soft palm-slap on 126.56", "procedural", "optional", -28)
def _():
    pre = 0.25
    w = whoosh_rise(0.45, 400, 6000, 13004) * np.interp(tt(0.45), [0, 0.2, 0.3, 0.45], [0, 0.6, 1.0, 0])
    slap = bp(noise(N(0.03), 13005), 600, 4000, 2) * expdec(N(0.03), 0.006)
    y = np.zeros((2, N(0.5)))
    add_at(y, w, 0.0)
    add_at(y, 0.6 * slap / np.max(np.abs(slap)), pre)
    return reverb(y, room(), -16), -pre        # the whoosh leads in; the slap lands on the anchor (v3: 130.04)


@cue("b_pileup", 127.44, "E6a the agents crash into each other beneath her: dull cloth-and-bodies thump, low-passed, "
     "no impact sting", "procedural", "optional", -30)
def _():
    y = np.zeros(N(0.35))
    th, th2 = thump(60, 0.3, 0.07), thump(85, 0.2, 0.05)
    y[:len(th)] += th
    y[:len(th2)] += 0.6 * th2
    cl = lp(noise(N(0.25), 13094), 900, 2) * expdec(N(0.25), 0.06)
    y[:len(cl)] += 0.5 * cl / np.max(np.abs(cl))
    return lp(y, 1200, 2), 0.0


@cue("b_atomize", 127.88, "E6b freeze, flash, burst into motes mid-air: crystalline shatter sparkle, high-passed above "
     "the supersaw", "procedural", "optional", -28)
def _():
    y = hp(pings(0.4, 70, 3500, 9500, 13138), 3000, 2)
    return np.stack([y, np.roll(y, N(0.004))]), 0.0


@cue("b_implode", 128.32, "E6c the motes implode into two Jades: the sparkle reversed, swelling into the 128.76 downbeat",
     "procedural", "optional", -30)
def _():
    y = hp(pings(0.4, 70, 3500, 9500, 13138), 3000, 2)[::-1][:N(0.44)]
    y = y * np.linspace(0.3, 1.0, len(y)) ** 2
    return np.stack([np.roll(y, N(0.004)), y]), 0.0


@cue("b_fall_short", 136.96, "E8 six rainbow copies give out over the chasm and drop away (136.96-137.26, every 60 ms): "
     "a tiny descending 8-bit pitch-blip per copy, like a lost life", "procedural (pulse wave)", "optional", -34)
def _():
    y = np.zeros((2, N(0.36)))
    for k in range(6):
        f0 = NOTE["F6"] * 2 ** (-k / 12)
        b = pulse(f0, 0.05, duty=0.25, sweep=f0 / 3) * np.interp(tt(0.05), [0, 0.003, 0.05], [0, 1, 0])
        add_at(y, pan(b, -0.5 + 0.2 * k), 0.06 * k)
    return reverb(y, room(), -20), 0.0


@cue("b_wall_burst", 137.32, "E8 four copies clip the far wall and burst into motes: a small sparkle cluster (b_atomize, "
     "shorter)", "procedural", "optional", -32)
def _():
    y = hp(pings(0.15, 28, 3500, 9500, 13732, tau=0.035), 3000, 2)
    return np.stack([y, np.roll(y, N(0.004))]), 0.0


@cue("b_stagger", 109.40, "V2k she staggers back off the agent, feet scuffing (109.40-109.70)", "procedural",
     "optional", -32)
def _():
    return scuff(0.30, 10940), 0.0


@cue("b_wallslap", 109.85, "V2k her palm slaps the stone wall as she catches herself", "procedural", "optional", -32)
def _():
    y = np.zeros(N(0.15))
    sl = bp(noise(N(0.04), 10985), 700, 5000, 2) * expdec(N(0.04), 0.007)
    y[:len(sl)] += sl / np.max(np.abs(sl))
    th = thump(140, 0.08, 0.015, seed=10986)
    y[:len(th)] += 0.4 * th
    return reverb(y, room(), -20), 0.0

# ---- v4: the co-op level (docs/revisions/v4/plans/coop.md), all procedural. The times follow the picture beats in
# tools/sections/D/build_timeline.py (COOP_* there): a floor button pressed, the giant pencil drawbridge lowering and
# landing, the second button, and the bridge swinging back up.
COOP_BTN1, COOP_DOWN, COOP_BTN2, COOP_UP = 130.50, 130.80, 132.10, 134.00


def _button(seed):
    """a big desk-bell-sized button pushed flush: a soft plastic clunk with a low body and a short latch click"""
    y = np.zeros((2, N(0.25)))
    th = thump(95, 0.18, 0.04, f_start=150, seed=seed)
    add_at(y, th, 0.0)
    ck = click(seed + 1, dur=0.02, lo=1200, hi=6000, tau=0.004, modes=((1900, 18, 0.6),))
    add_at(y, 0.7 * ck / np.max(np.abs(ck)), 0.012)
    return reverb(lp(y, 5000, 2), room(), -20)


@cue("coop_btn1", COOP_BTN1, "C1 ORANGE stamps the near floor button: soft clunk + latch click", "procedural", "optional", -27)
def _():
    return _button(13050), 0.0


@cue("coop_bridge_down", COOP_DOWN, "C1 the giant pencil swings down across the gap: a short wooden creak leading in, and a "
     "hollow wooden clack as it lands on the far table", "procedural", "optional", -24)
def _():
    pre = 0.28
    y = np.zeros((2, N(pre + 0.35)))
    cr = reson(noise(N(pre), 13080) * np.interp(tt(pre), [0, pre * 0.6, pre], [0.0, 0.5, 0.2]), 420, 12)
    add_at(y, 0.4 * cr / np.max(np.abs(cr)), 0.0)
    clack = click(13081, dur=0.06, lo=300, hi=3500, tau=0.012, modes=((260, 10, 1.0), (610, 14, 0.6)))
    add_at(y, clack / np.max(np.abs(clack)), pre)
    th = thump(70, 0.2, 0.05, seed=13082)
    add_at(y, 0.5 * th, pre)
    return reverb(y, room(), -16), -pre


@cue("coop_btn2", COOP_BTN2, "C2 BLUE presses the far button: the same clunk, a touch higher", "procedural", "optional", -28)
def _():
    return _button(13226), 0.0


@cue("coop_bridge_up", COOP_UP, "C2 BLUE lets go: the button pops back up and the pencil swings up out of the agents' reach "
     "with a rising whoosh and a wooden knock", "procedural", "optional", -27)
def _():
    y = np.zeros((2, N(0.5)))
    pop = click(13400, dur=0.02, lo=1500, hi=7000, tau=0.003)
    add_at(y, 0.6 * pop / np.max(np.abs(pop)), 0.0)
    w = whoosh_rise(0.3, 300, 3000, 13401) * np.interp(tt(0.3), [0, 0.15, 0.3], [0, 1.0, 0.2])
    add_at(y, 0.7 * w / np.max(np.abs(w)), 0.02)
    kn = click(13402, dur=0.05, lo=300, hi=3000, tau=0.01, modes=((300, 10, 1.0),))
    add_at(y, 0.6 * kn / np.max(np.abs(kn)), 0.3)
    return reverb(y, room(), -16), 0.0


@cue("coop_bridge_throw", 134.00, "C2b the far end of the pencil kicks up under the two agents and flings them back onto the "
     "near desk: a springboard twang, a cloth whoosh, two soft landing thumps (134.44, 134.52); slapstick, nobody hurt",
     "procedural", "optional", -26)
def _():
    y = np.zeros((2, N(0.75)))
    t = tt(0.35)
    tw = np.sin(2 * np.pi * np.cumsum(np.interp(t, [0, 0.35], [180, 120])) / SR) * np.exp(-t / 0.12) * (1 + 0.5 * np.sin(2 * np.pi * 14 * t))
    add_at(y, 0.8 * tw, 0.0)
    w = whoosh_rise(0.3, 600, 4000, 13410) * np.interp(tt(0.3), [0, 0.1, 0.3], [0, 1.0, 0])
    add_at(y, pan(0.5 * w / np.max(np.abs(w)), -0.4), 0.05)
    for k, (dt, f0) in enumerate(((0.44, 75), (0.52, 90))):
        th = thump(f0, 0.18, 0.05, seed=13420 + k)
        cl = lp(noise(N(0.12), 13430 + k), 900, 2) * expdec(N(0.12), 0.03)
        add_at(y, pan(0.7 * th, -0.5), dt)
        add_at(y, pan(0.3 * cl / np.max(np.abs(cl)), -0.5), dt)
    return reverb(y, room(), -18), 0.0


# ---------------------------------------------------------------- v5 coda (only with --coda; see CODA above)
# Registered last so the stem numbers of every earlier cue stay as they were.
# In coda mode outro_clock and counter_roll are replaced by coda_clock and coda_counter (same sounds, longer, fading),
# and coda_pad holds the ring-out chord so the credits' sound fades out instead of being cut at the whisper (226.0).
CODA_ONLY = {"coda_pad", "coda_clock", "coda_counter", "coda_door_latch", "coda_door_bell", "coda_lobby_tone"}
CODA_REPLACES = {"outro_clock", "counter_roll"}


def freeze(x, t0, t1, dur, seed, nfft=8192):
    """Spectral freeze: the mean magnitude spectrum of x[t0:t1] (mono) resynthesized with random phases for dur s."""
    seg = x[N(t0):N(t1)]
    mag = np.abs(librosa.stft(seg, n_fft=nfft, hop_length=nfft // 4)).mean(axis=1, keepdims=True)
    frames = int(np.ceil((N(dur) + 2 * nfft) / (nfft // 4))) + 4
    ph = np.random.default_rng(seed).uniform(-np.pi, np.pi, (mag.shape[0], frames))
    y = librosa.istft(mag * np.exp(1j * ph), hop_length=nfft // 4, n_fft=nfft)
    y = y[nfft:nfft + N(dur)]
    return y / (np.max(np.abs(y)) + 1e-12)


@cue("coda_pad", 225.00, "Credits (v5 coda): the ring-out Ab chord held as a spectral freeze of the instrumental stem "
     "(223.3-224.5), entering as the original decays through -36 dB, under the whisper (ducked), then fading out "
     "slowly (0 -> -40 dB, 226.9 -> the door bell at 234.09, slow at first) while its low-pass closes towards 1.2 kHz", "procedural "
     "(instrumental stem copy)", "essential", -25.5, duck_vocal_db=6)
def _():
    dur = CODA_FADE[1] + 0.45 - 225.00
    t = 225.00 + tt(dur)
    lo, hi = INS[0], INS[1]
    a = np.stack([freeze(lo, 223.3, 223.9, dur, 2251), freeze(hi, 223.3, 223.9, dur, 2252)])
    b = np.stack([freeze(lo, 223.9, 224.5, dur, 2253), freeze(hi, 223.9, 224.5, dur, 2254)])
    w = 0.5 + 0.5 * np.sin(2 * np.pi * (t - 225.0) / 7.0)            # slow drift between the two freezes
    y = a * np.sqrt(1 - w) + b * np.sqrt(w)
    dark = lp(y, 1200, 2)
    k = np.clip((t - 226.9) / (CODA_FADE[1] - 226.9), 0, 1)           # brightness closes as it fades
    y = dark + (y - dark) * (1 - k) ** 1.5
    env = np.interp(t, [225.0, 225.7], [0.0, 1.0]) * db2a(coda_fade_db(t))
    return y * env, 0.0


@cue("coda_clock", 223.685, "Credits (v5 coda): the intro's 8th-note clock (outro_clock's ticks) carries on past the "
     "whisper and fades with the held chord, last tick on the last counter tick (233.64)", "procedural", "essential", -25, duck_vocal_db=9)
def _():
    ticks = [223.685 + 0.226 * k for k in range(60)]
    ticks = [x for x in ticks if x < COUNTER_TICKS[-1] + 0.01]      # v5-build: the clock stops on the last counter tick
    y = np.zeros((2, N(ticks[-1] - 223.685 + 0.5)))
    for i, tk in enumerate(ticks):
        g = np.interp(tk, [223.685, 225.0, 226.9], [0.25, 1.0, 0.9]) * db2a(coda_fade_db(tk))
        add_at(y, pan(tick_sound(300 + i, tock=i % 2 == 1) * g, -0.12 if i % 2 else 0.12), tk - 223.685)
    return reverb(y, room(), -16), 0.0


@cue("coda_counter", COUNTER_TICKS[0], "Credits (v5 coda): one soft 8-bit blip (F6/Bb6) per ITERATION tick, on the "
     "ring-out beat (4,098 at 226.853 ... 4,113 at 233.642). v5-build: they fade only to -12 dB while the chord fades "
     "out, so the last tick is still heard and the door bell answers it one beat later (CODA_BELL)",
     "procedural (pulse wave)", "essential", -33)
def _():
    t0 = COUNTER_TICKS[0]
    y = np.zeros(N(COUNTER_TICKS[-1] - t0 + 0.2))
    for i, tk in enumerate(COUNTER_TICKS):
        g = db2a(-12.0 * np.clip((tk - CODA_FADE[0]) / (CODA_FADE[1] - CODA_FADE[0]), 0, 1))
        b = blip_seq([("F6" if i % 2 == 0 else "Bb6", 0.022)], duty=0.5, gap=0.0, decay=0.015)
        y[N(tk - t0):N(tk - t0) + len(b)] += b * g
    return reverb(y, room(), -18), 0.0


# ---------------------------------------------------------------- v5 merge (3:23, both mixes; docs/revisions/v5/merge.md)
# BLUE and ORANGE reassemble into her (F7_07m, 202.88-205.52). The split's two sounds (b_atomize 127.88, b_implode
# 128.32) come back in the same order, so the ear hears the 2:00 split undone. Levels are the previz's (Jade: "merge
# looks good"), which sit 13-20 dB RMS under the final drop. Registered after the coda cues so no stem number shifts.
@cue("merge_score", 203.32, "F7_07m the twins freeze and graphite lines score them into triangles: three short pencil "
     "strokes", "procedural", "optional", -16)
def _():
    y = np.zeros(N(0.42))
    for k, (t0, d) in enumerate(((0.0, 0.12), (0.14, 0.11), (0.27, 0.13))):
        s = bp(noise(N(d), 32300 + k), 1800, 7000, 2)
        s *= np.interp(tt(d), [0, 0.02, d * 0.7, d], [0, 1, 0.8, 0]) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 90 * tt(d))))
        y[N(t0):N(t0) + len(s)] += s
    return np.stack([y, y]), 0.0


@cue("merge_lift", 203.76, "F7_07m the pieces lift off on the swell: b_atomize's sparkle (same synthesis as the split at "
     "127.88)", "procedural", "optional", -12)
def _():
    y = hp(pings(0.4, 70, 3500, 9500, 13138), 3000, 2)
    return np.stack([y, np.roll(y, N(0.004))]), 0.0


@cue("merge_seat", 204.64, "F7_07m the pieces seat into one Jade: b_implode's reversed sparkle swelling from 204.02 into "
     "a soft wooden latch click on bar 117", "procedural", "optional", -11)
def _():
    y = hp(pings(0.6, 90, 3500, 9500, 13139), 3000, 2)[::-1][:N(0.62)]
    y = y * np.linspace(0.2, 1.0, len(y)) ** 2
    st = np.stack([np.roll(y, N(0.004)), y]) * db2a(-13)
    ck = click(32640, dur=0.05, lo=400, hi=4000, tau=0.008, modes=((520, 12, 1.0), (1240, 16, 0.5)))
    ck = ck / np.max(np.abs(ck)) * db2a(-11)
    full = np.zeros((2, N(0.62 + 0.3)))
    full[:, :st.shape[1]] += st
    add_at(full, ck, 0.62)
    return reverb(full, ir(0.6, 0.5, 6000, seed=32641), -14), -0.62


# ---------------------------------------------------------------- v5 post-credits: the Hilbert Hotel (coda mode only)
# Ported from tools/sectionF/coda/previz_audio.py (v5-coda). PC1 fades up at CODA_DOOR_IN while the counter is still
# ticking; the gloved hand pushes the door open on CODA_BELL, the beat after the last tick; PC2 (the lobby) has room tone
# only (no speech) and cuts to black at CODA_END.
@cue("coda_door_latch", CODA_BELL - 0.06, "PC1 the door's latch gives as the gloved hand pushes the handle", "procedural",
     "optional", -30)
def _():
    c = click(901, dur=0.03, lo=900, hi=8000, tau=0.004, modes=((1400, 20, 0.6), (3300, 25, 0.4)))
    return reverb(c / np.max(np.abs(c)), ir(0.6, 0.4, 6000, seed=902), -16), 0.0


@cue("coda_door_bell", CODA_BELL, "PC1 the little brass bell on its spring rings as the door starts to swing: 4-5 quick "
     "uneven strikes (Ab6 / Eb7, the ring-out's key), the counter's next tick", "procedural", "essential", -27)
def _():
    rng = np.random.default_rng(5)
    y = np.zeros(N(2.6))
    partials = ((1.0, 1.0, 0.55), (2.0, 0.35, 0.3), (2.76, 0.28, 0.22), (4.07, 0.12, 0.12), (5.4, 0.06, 0.08))
    for k, (dt, a) in enumerate([(0.0, 1.0), (0.11, 0.55), (0.19, 0.35), (0.34, 0.22), (0.52, 0.12)]):
        f0 = NOTE["Ab6"] * (1 + rng.uniform(-0.004, 0.004)) if k % 2 == 0 else 2489.0 * (1 + rng.uniform(-0.004, 0.004))
        b = bell(f0, 2.0, partials) * a
        i = N(dt)
        y[i:i + len(b)] += b[:len(y) - i]
    y = hp(y, 900, 2)
    rattle = bp(noise(N(0.45), 8), 3000, 9000, 2) * np.interp(tt(0.45), [0, 0.02, 0.45], [0, 1, 0]) * 0.05
    y[:len(rattle)] += rattle
    return reverb(y / np.max(np.abs(y)), ir(1.4, 0.9, 7000, seed=14, predelay=0.008), -12), 0.0


@cue("coda_lobby_tone", CODA_DOOR_IN, "PC1-PC2 warm lobby air: barely there outside, opens with the door, holds under "
     "the receptionist's POV, cut with the picture at the end", "procedural", "optional", -24)
def _():
    dur = CODA_END - CODA_DOOR_IN
    n = N(dur)
    x = np.cumsum(noise(n, 950))
    x = lp(hp(x - np.mean(x), 40, 2), 900, 2)
    x /= np.max(np.abs(x))
    t = CODA_DOOR_IN + tt(dur)
    env = db2a(np.interp(t, [CODA_DOOR_IN, CODA_DOOR_IN + 0.6, CODA_BELL, CODA_BELL + 0.8, CODA_END - 0.1, CODA_END],
                         [-70, -14, -14, 0, 0, -70]))
    return np.stack([x, np.roll(x, N(0.013))]) * env, 0.0


# ---------------------------------------------------------------- v7 ghost pops (--v7pop only; last in CUES so no
# other stem is renumbered)
# v7 (docs/revisions/v7/ghost_pop.md): Celeste's death pop for each ghost that misses. Sound on the first frame the
# pop is drawn (render/timeline/D.js pop_* start, rounded up to the 24 fps frame). Pitched in the track's key.
def ghost_pop(f, seed):
    """A bubble 'bwip' (sine flicking up from 0.55 f to f in ~10 ms, 35 ms decay) + a 3 ms click + a short sparkle."""
    t = tt(0.16)
    fr = f * (0.55 + 0.45 * (1 - np.exp(-t / 0.005)))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    env = np.minimum(1, t / 0.0015) * np.exp(-t / 0.035)
    y = (np.sin(ph) + 0.25 * np.sin(2 * ph)) * env
    ck = bp(noise(N(0.004), seed), 2000, 8000, 2) * expdec(N(0.004), 0.0012)
    y[:len(ck)] += 0.35 * ck / (np.max(np.abs(ck)) + 1e-9)
    sp = hp(pings(0.05, 5, 4000, 9500, seed + 1, tau=0.018), 3000, 2)
    i = N(0.008)
    y[i:i + len(sp)] += 0.18 * sp[:len(y) - i]
    return y / np.max(np.abs(y))


def frame_up(t):
    return float(np.ceil(t * 24 - 1e-6) / 24)


V7_LEAP_POPS = [(136.1767, "F5", -0.25), (136.4684, "Ab5", -0.2)]             # gold, lime (x 738, 774 of 1920)
V7_CHASM_POPS = [(137.1617, -0.03), (137.2034, -0.04), (137.245, -0.06), (137.2867, 0.06), (137.2867, -0.09),
                 (137.2867, -0.13), (137.3284, -0.15), (137.37, -0.19), (137.4117, -0.23), (137.4534, -0.29)]
V7_RUN = ["F5", "Ab5", "Bb5", "C6", "Db6", "F6", "Ab6", "Bb6", "C7", "F7"]     # the chasm run climbs, one note per pop


@cue("g_pop_leap", frame_up(V7_LEAP_POPS[0][0]), "v7 E7 leap: gold (136.18) and lime (136.47) fall through the gap "
     "and pop, Celeste style: a bubble bwip F5 / Ab5 + click + sparkle", "procedural", "essential", -15)
def _():
    t0 = frame_up(V7_LEAP_POPS[0][0])
    y = np.zeros((2, N(0.5)))
    for k, (tp, nm, pn) in enumerate(V7_LEAP_POPS):
        add_at(y, pan(ghost_pop(NOTE[nm], 13600 + k) * (1.0 if k == 0 else 0.8), pn), frame_up(tp) - t0)
    return reverb(y, room(), -18), 0.0


@cue("g_pop_chasm", frame_up(V7_CHASM_POPS[0][0]), "v7 E7 chasm: ten copies fall short and pop 137.16-137.45, a quick "
     "rising run F5 ... F7 (simultaneous pops 8 ms apart)", "procedural", "essential", -17)
def _():
    t0 = frame_up(V7_CHASM_POPS[0][0])
    y = np.zeros((2, N(0.55)))
    seen = {}
    for k, (tp, pn) in enumerate(V7_CHASM_POPS):
        ft = frame_up(tp)
        d = 0.008 * seen.get(ft, 0)
        seen[ft] = seen.get(ft, 0) + 1
        add_at(y, pan(ghost_pop(NOTE[V7_RUN[k]], 13700 + k) * (0.7 + 0.3 * k / 9), pn), ft - t0 + d)
    return reverb(y, room(), -18), 0.0


# ============================================================================= framework
def vocal_env_db():
    v = VOC.mean(0)
    h = N(0.005)
    fr = np.sqrt(np.mean(v[:len(v) // h * h].reshape(-1, h) ** 2, axis=1))
    db = a2db(fr)
    out = np.empty_like(db)
    a_att, a_rel = np.exp(-0.005 / 0.015), np.exp(-0.005 / 0.150)
    s = -120.0
    for i, x in enumerate(db):
        c = a_att if x > s else a_rel
        s = c * s + (1 - c) * x
        out[i] = s
    return out, h


def render(only=None):
    load()
    venv, hop = vocal_env_db()
    n_total = MIX.shape[1]
    sfx = np.zeros((2, n_total))
    music_gain = np.ones(n_total)
    stems = "stems" + (CODA_SUFFIX if CODA else "")
    os.makedirs(os.path.join(OUT, stems), exist_ok=True)
    meta = []
    for k, c in enumerate(CUES):
        if only and c["id"] not in only:
            continue
        if c["id"] in DISABLED and not (only and c["id"] in only):
            continue
        if c["id"] in (CODA_REPLACES if CODA else CODA_ONLY):     # v5 coda: one set of ending cues or the other
            continue
        if c["id"] in (V7POP_DROPS if V7POP else V7POP_ONLY):    # v7 pops: one or the other
            continue
        y, off = c["fn"]()
        y = stereo(np.asarray(y, dtype=np.float64))
        y = y / np.max(np.abs(y)) * db2a(c["gain_db"])
        start = c["anchor_s"] + off
        i0 = N(start)
        if c["duck_vocal_db"] > 0:
            idx = np.clip((i0 + np.arange(y.shape[1])) // hop, 0, len(venv) - 1)
            red = np.clip((venv[idx] - (-42.0)) * 0.5, 0, c["duck_vocal_db"])
            y = y * db2a(-red)
        if c["duck_music_db"] > 0:
            assert c["duck_music_db"] <= 2.0
            m = np.ones(n_total)
            a, b = i0, i0 + y.shape[1]
            m[a:b] = db2a(-c["duck_music_db"])
            r = N(0.15)
            m[max(0, a - N(0.03)):a] = np.linspace(1, db2a(-c["duck_music_db"]), a - max(0, a - N(0.03)))
            m[b:b + r] = np.linspace(db2a(-c["duck_music_db"]), 1, len(m[b:b + r]))
            music_gain = np.minimum(music_gain, m)
        tail = np.where(np.max(np.abs(y), axis=0) > db2a(-90))[0]
        y = y[:, :tail[-1] + 1]                                   # drop the sub -90 dBFS reverb tail
        add_at(sfx, y, start)
        fn = f"{k + 1:02d}_{c['id']}.wav"
        sf.write(os.path.join(OUT, stems, fn), y.T.astype(np.float32), SR, subtype="FLOAT")
        meta.append(dict(id=c["id"], file=f"{stems}/{fn}", start_s=round(start, 6), start_sample=i0,
                         end_s=round(start + y.shape[1] / SR, 4), anchor_s=c["anchor_s"], what=c["what"],
                         source=c["source"], priority=c["priority"], gain_db=c["gain_db"],
                         duck_vocal_db_max=c["duck_vocal_db"], duck_music_db=c["duck_music_db"], _y=y))
    return sfx, music_gain, meta


def frame_sv(s, v):
    """p90 over vocal-active frames of (SFX - vocal) power in 250 Hz-4 kHz, dB. None if the vocal is silent."""
    nf, hop = 4096, 480
    if s.shape[1] < nf:
        return None
    S = np.abs(librosa.stft(s.mean(0), n_fft=nf, hop_length=hop, center=False)) ** 2
    V = np.abs(librosa.stft(v.mean(0), n_fft=nf, hop_length=hop, center=False)) ** 2
    f = librosa.fft_frequencies(sr=SR, n_fft=nf)
    band = (f >= 250) & (f <= 4000)
    vs, ss = V[band].sum(0), S[band].sum(0)
    vrms = np.sqrt(V.sum(0) / (nf * nf / 2.66))               # approx frame RMS (hann)
    on = a2db(vrms) > -45
    if on.sum() < 3:
        return None
    return round(float(np.percentile(10 * np.log10((ss[on] + 1e-15) / (vs[on] + 1e-15)), 90)), 1)


def momentary_diff(s, o):
    w, hop = N(0.4), N(0.05)
    if s.shape[1] <= w:
        return round(loudness(s) - loudness(o), 1)
    ks, ko = kweight(s), kweight(o)
    best = -99.0
    for i in range(0, s.shape[1] - w + 1, hop):
        ps = np.sum(np.mean(ks[:, i:i + w] ** 2, axis=-1))
        po = np.sum(np.mean(ko[:, i:i + w] ** 2, axis=-1))
        best = max(best, 10 * np.log10((ps + 1e-15) / (po + 1e-15)))
    return round(best, 1)


def metrics(sfx, mix_out, meta):
    """Objective listening proxies per cue."""
    for m in meta:
        a, b = m["start_sample"], N(m["end_s"])
        s, o, v = m.pop("_y"), MIX[:, a:b], VOC[:, a:b]
        b = a + s.shape[1]
        o, v = MIX[:, a:b], VOC[:, a:b]
        e = np.sqrt(np.mean(s.mean(0)[:len(s[0]) // 240 * 240].reshape(-1, 240) ** 2, axis=1))
        act = np.where(e > np.max(e) * db2a(-20))[0]
        wa, wb = act[0] * 240, (act[-1] + 1) * 240              # active window (within 20 dB of the cue's max)
        s, o, v, mo = s[:, wa:wb], o[:, wa:wb], v[:, wa:wb], mix_out[:, a + wa:a + wb]
        Ls, Lo, Lm = loudness(s), loudness(o), loudness(mo)
        Bs, Bo, Bv = band_energies(s), band_energies(o), band_energies(v)
        ps, po = 10 ** (Bs / 10), 10 ** (Bo / 10)
        cos = float(np.sum(np.sqrt(ps * po)) / np.sqrt(np.sum(ps) * np.sum(po)))   # Bhattacharyya-style overlap 0..1
        masked = float(np.sum(ps[Bo > Bs + 15]) / np.sum(ps))
        dominant = float(np.sum(ps[Bs > Bo]) / np.sum(ps))
        speech = [i for i, f in enumerate(THIRD_OCT) if 250 <= f <= 4000]
        vocal_on = loudness(v) > -45
        svr = float(10 * np.log10(np.sum(ps[speech]) / np.sum(10 ** (Bv[speech] / 10)))) if vocal_on else None
        # frame-wise (10 ms hop, 85 ms frames): speech-band SFX/vocal ratio where the vocal is active (p90), and the
        # worst 400 ms window of SFX loudness minus music loudness (momentary)
        sv = frame_sv(s, v)
        mom = momentary_diff(s, o)
        m.update(active_s=[round((a + wa) / SR, 3), round((a + wb) / SR, 3)], peak_dbfs=round(float(a2db(np.max(np.abs(s)))), 1),
                 sfx_lufs=round(Ls, 1), music_lufs=round(Lo, 1), sfx_minus_music_lu=round(Ls - Lo, 1),
                 mix_rise_lu=round(Lm - Lo, 2), spectral_overlap=round(cos, 2), sfx_energy_masked=round(masked, 2),
                 sfx_energy_above_music=round(dominant, 2),
                 sfx_minus_vocal_speechband_db=None if svr is None else round(svr, 1),
                 sfx_minus_vocal_p90_when_singing_db=sv, sfx_minus_music_momentary_max_lu=mom,
                 mix_peak_dbfs=round(float(a2db(np.max(np.abs(mo)))), 1))
    return meta


def main(argv):
    only = None
    for a in argv:
        if a.startswith("--only="):
            only = set(a.split("=", 1)[1].split(","))
    sfx, mg, meta = render(only)
    mix_out = MIX * mg + sfx
    meta = metrics(sfx, mix_out, meta)
    for m in meta:
        print(f"{m['id']:17s} {m['start_s']:8.3f} gain {m['gain_db']:5.1f} | S-M {m['sfx_minus_music_lu']:6.1f} LU "
              f"(sfx {m['sfx_lufs']:6.1f} mus {m['music_lufs']:6.1f}) rise {m['mix_rise_lu']:5.2f} | overlap "
              f"{m['spectral_overlap']:.2f} masked {m['sfx_energy_masked']:.2f} above {m['sfx_energy_above_music']:.2f}"
              f" | S-V {m['sfx_minus_vocal_speechband_db']} p90 {m['sfx_minus_vocal_p90_when_singing_db']}"
              f" | mom {m['sfx_minus_music_momentary_max_lu']} | pk {m['peak_dbfs']}")
    if only:
        return
    # ---- full renders
    sx = CODA_SUFFIX if CODA else ""
    F_SFX, F_MIX, F_MP3, F_CUES = f"sfx_only{sx}.wav", f"mix_preview{sx}.wav", f"Rewind_cinematic_sfx_mix{sx}.mp3", f"cues{sx}.json"
    sf.write(os.path.join(OUT, F_SFX), sfx.T, SR, subtype="PCM_24")
    peak = float(np.max(np.abs(mix_out)))
    assert peak < db2a(-1.0), f"mix peak {a2db(peak):.2f} dBFS"
    sf.write(os.path.join(OUT, F_MIX), mix_out.T, SR, subtype="PCM_24")
    # bit-exactness of the original where there is no SFX and no ducking
    back, _ = sf.read(os.path.join(OUT, F_MIX), dtype="int32", always_2d=True)
    silent = (np.max(np.abs(sfx), axis=0) == 0) & (mg == 1.0)
    exact = bool(np.all(back[silent] == (SRC[silent].astype(np.int32) << 16)))
    I_src, I_mix = integrated(MIX), integrated(mix_out)
    mp3 = os.path.join(OUT, F_MP3)
    subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", os.path.join(OUT, F_MIX),
                    "-c:a", "libmp3lame", "-b:a", "320k", "-metadata", "title=Rewind (cinematic edition) + SFX",
                    "-metadata", "artist=Jade Wang", mp3], check=True)
    dec = librosa.load(mp3, sr=SR, mono=False)[0]
    nn = min(dec.shape[1], mix_out.shape[1])
    seg = slice(N(84.0), N(86.0))
    xc = [float(np.dot(dec[0, seg.start + d:seg.stop + d], mix_out[0, seg])) for d in range(-48, 49)]
    lag = int(np.argmax(xc)) - 48
    summary = dict(
        sample_rate=SR, source=os.path.relpath(INPUT_MP3, ROOT), base_wav="analysis/cinematic/source.wav",
        length_samples=int(MIX.shape[1]), n_cues=len(meta),
        integrated_lufs=dict(original=round(I_src, 2), mix_preview=round(I_mix, 2), delta=round(I_mix - I_src, 3)),
        true_peak_dbtp=dict(original=round(true_peak_db(MIX), 2), mix_preview=round(true_peak_db(mix_out), 2),
                            mp3_decoded=round(true_peak_db(dec[:, :nn]), 2)),
        mp3_offset_samples_vs_wav=lag, mp3_length_samples=int(dec.shape[1]),
        original_bit_exact_outside_cues=exact, music_ducking_used=bool(np.any(mg < 1.0)),
        files=dict(sfx_only=F_SFX, mix_preview=F_MIX, mp3=F_MP3), coda=dict(end_s=CODA_END, counter_ticks=COUNTER_TICKS,
                                                                             fade=CODA_FADE) if CODA else None,
        notes="start_s/start_sample = where sample 0 of the stem file sits on the song timeline (48 kHz, same "
              "zero as analysis/cinematic/source.wav = the mp3 with encoder delay removed). Stems are float32 at final "
              "gain (vocal ducking baked in): summing them at start_sample reproduces sfx_only.wav. gain_db = stem "
              "peak in dBFS before vocal ducking.")
    json.dump(dict(summary=summary, cues=meta), open(os.path.join(OUT, F_CUES), "w"), indent=1, default=float)
    print(json.dumps(summary, indent=1, default=float))


if __name__ == "__main__":
    main(sys.argv[1:])
