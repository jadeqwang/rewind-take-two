"""Small DSP kit for the Rewind SFX layer: filters, envelopes, synth voices, reverb, loudness (BS.1770).

Everything is numpy/scipy at 48 kHz. Mono signals are 1-D arrays; stereo is (2, n).
"""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve, lfilter, resample_poly

SR = 48000


def secs(n):
    return n / SR


def N(t):
    return int(round(t * SR))


def tt(dur):
    return np.arange(N(dur)) / SR


# ----------------------------------------------------------------------------- filters
def lp(y, hz, order=4):
    return sosfilt(butter(order, hz, "low", fs=SR, output="sos"), y, axis=-1)


def hp(y, hz, order=4):
    return sosfilt(butter(order, hz, "high", fs=SR, output="sos"), y, axis=-1)


def bp(y, lo, hi, order=4):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), y, axis=-1)


def reson(y, hz, q):
    """Two-pole resonator (constant peak gain ~1)."""
    w = 2 * np.pi * hz / SR
    r = np.exp(-w / (2 * q))
    a = [1, -2 * r * np.cos(w), r * r]
    b = [(1 - r * r) / 2, 0, -(1 - r * r) / 2]
    return lfilter(b, a, y, axis=-1)


# ----------------------------------------------------------------------------- envelopes and helpers
def expdec(n, tau):
    return np.exp(-np.arange(n) / SR / tau)


def fade(y, a=0.0, r=0.0, shape=2.0):
    y = np.array(y, dtype=np.float64, copy=True)
    n = y.shape[-1]
    if a > 0:
        k = min(n, N(a))
        y[..., :k] *= np.linspace(0, 1, k) ** shape
    if r > 0:
        k = min(n, N(r))
        y[..., n - k:] *= np.linspace(1, 0, k) ** shape
    return y


def norm_peak(y, peak=1.0):
    m = np.max(np.abs(y))
    return y * (peak / m) if m > 0 else y


def db2a(db):
    return 10 ** (db / 20)


def a2db(a):
    return 20 * np.log10(np.maximum(a, 1e-12))


def pan(y, p=0.0):
    """Constant-power pan, p in [-1, 1] -> (2, n)."""
    th = (p + 1) * np.pi / 4
    return np.stack([y * np.cos(th), y * np.sin(th)]) * np.sqrt(2)


def stereo(y):
    return y if y.ndim == 2 else np.stack([y, y])


def add_at(dst, y, t):
    """Add y (mono or stereo) into dst (2, n) starting at time t (s); y may extend before/after."""
    y = stereo(y)
    i = N(t)
    a, b = max(0, i), min(dst.shape[1], i + y.shape[1])
    if b > a:
        dst[:, a:b] += y[:, a - i:b - i]


def noise(n, seed):
    return np.random.default_rng(seed).standard_normal(n)


# ----------------------------------------------------------------------------- synth voices
NOTE = {"F2": 87.307, "Bb2": 116.54, "C3": 130.81, "F3": 174.61, "Bb3": 233.08, "C4": 261.63, "Db4": 277.18,
        "Eb4": 311.13, "F4": 349.23, "Ab4": 415.30, "Bb4": 466.16, "C5": 523.25, "Db5": 554.37, "Eb5": 622.25,
        "F5": 698.46, "Ab5": 830.61, "Bb5": 932.33, "C6": 1046.5, "Db6": 1108.7, "Eb6": 1244.5, "F6": 1396.9,
        "Ab6": 1661.2, "Bb6": 1864.7, "C7": 2093.0, "F7": 2793.8}


def pulse(f, dur, duty=0.25, fmax=14000.0, sweep=None):
    """Band-limited pulse wave (NES-style), additive. f may be a scalar; sweep=(f_end) for a linear glide."""
    t = tt(dur)
    fr = np.full(len(t), f) if sweep is None else np.linspace(f, sweep, len(t))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    y = np.zeros(len(t))
    K = int(fmax / max(f, sweep or f))
    for k in range(1, K + 1):
        y += np.sin(np.pi * k * duty) / (np.pi * k) * np.cos(k * ph - np.pi * k * duty)
    return y - y.mean()


def click(seed, dur=0.012, lo=1500, hi=9000, tau=0.002, modes=()):
    """Short mechanical click: filtered noise burst + optional resonant modes [(hz, q, gain), ...]."""
    n = N(dur)
    x = bp(noise(n, seed), lo, hi, 2) * expdec(n, tau)
    for hz, q, g in modes:
        x = x + g * reson(noise(n, seed + 7) * expdec(n, tau * 0.5), hz, q) * 6
    return x


def thump(f0, dur, tau, f_start=None, seed=0):
    """Pitched low body hit with a quick downward pitch glide."""
    t = tt(dur)
    fs = f_start or f0 * 1.6
    fr = f0 + (fs - f0) * np.exp(-t / 0.03)
    y = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / tau)
    return y * (1 - np.exp(-t / 0.0015))


def bell(f0, dur, partials=((1.0, 1.0, 0.9), (2.0, 0.45, 0.5), (3.0, 0.25, 0.3), (4.16, 0.12, 0.15),
                             (5.43, 0.08, 0.08), (2.4, 0.18, 0.4))):
    """Struck bell: partials (ratio, amp, tau)."""
    t = tt(dur)
    y = np.zeros(len(t))
    for r, a, tau in partials:
        y += a * np.sin(2 * np.pi * f0 * r * t + r) * np.exp(-t / tau)
    y *= 1 - np.exp(-t / 0.0008)
    return y


def ir(dur, rt60, lp_hz=6000, seed=0, predelay=0.0, width=1.0):
    """Synthetic stereo reverb IR (exponentially decaying filtered noise)."""
    n = N(dur)
    t = np.arange(n) / SR
    env = 10 ** (-3 * t / rt60)
    l = lp(noise(n, seed) * env, lp_hz, 2)
    r = lp(noise(n, seed + 1) * env, lp_hz, 2)
    m = (l + r) / 2
    l, r = m + width * (l - m), m + width * (r - m)
    pd = np.zeros(N(predelay))
    out = np.stack([np.concatenate([pd, l]), np.concatenate([pd, r])])
    return out / np.sqrt(np.sum(out ** 2) / 2)


def reverb(y, impulse, wet_db=-10, dry=1.0):
    """y mono or stereo -> stereo, dry + wet."""
    y = stereo(y)
    w = np.stack([fftconvolve(y[0], impulse[0]), fftconvolve(y[1], impulse[1])])
    out = np.zeros((2, w.shape[1]))
    out[:, :y.shape[1]] += dry * y
    out += db2a(wet_db) * w
    return out


def varispeed(x, start, speed, backwards=False):
    """Read mono x from sample index `start` at per-output-sample `speed` (array). Linear interpolation."""
    pos = start + (-1 if backwards else 1) * np.concatenate([[0.0], np.cumsum(speed[:-1])])
    pos = np.clip(pos, 0, len(x) - 2)
    return np.interp(pos, np.arange(len(x)), x)


def tapestop(x, start_t, dur, curve=1.6):
    """Tape stop of stereo x (2, n) read from start_t: speed 1 -> 0 over dur (s)."""
    n = N(dur)
    s = (1 - np.arange(n) / n) ** curve
    st = N(start_t)
    return np.stack([varispeed(x[c], st, s) for c in range(x.shape[0])]), s


# ----------------------------------------------------------------------------- loudness (ITU-R BS.1770-4, 48 kHz)
_K1 = ([1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585])
_K2 = ([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621])


def kweight(y):
    y = stereo(y)
    return lfilter(*_K2, lfilter(*_K1, y, axis=-1), axis=-1)


def loudness(y):
    """Ungated loudness (LUFS) of a stereo segment."""
    k = kweight(y)
    return -0.691 + 10 * np.log10(np.sum(np.mean(k ** 2, axis=-1)) + 1e-15)


def integrated(y):
    k = kweight(y)
    blk, hop = N(0.4), N(0.1)
    p = np.array([np.sum(np.mean(k[:, i:i + blk] ** 2, axis=-1)) for i in range(0, k.shape[1] - blk + 1, hop)])
    lk = -0.691 + 10 * np.log10(p + 1e-15)
    g = p[lk > -70]
    rel = -0.691 + 10 * np.log10(g.mean()) - 10
    g2 = p[(lk > -70) & (lk > rel)]
    return -0.691 + 10 * np.log10(g2.mean())


def true_peak_db(y):
    y = stereo(y)
    up = resample_poly(y, 4, 1, axis=-1)
    return a2db(np.max(np.abs(up)))


THIRD_OCT = [63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000,
             5000, 6300, 8000, 10000, 12500, 16000]


def band_energies(y):
    """Third-octave band energies (dB) of a (mono-summed) segment."""
    m = stereo(y).mean(0)
    nfft = 1 << int(np.ceil(np.log2(max(len(m), 4096))))
    P = np.abs(np.fft.rfft(m * np.hanning(len(m)), nfft)) ** 2
    f = np.fft.rfftfreq(nfft, 1 / SR)
    out = []
    for fc in THIRD_OCT:
        sel = (f >= fc / 2 ** (1 / 6)) & (f < fc * 2 ** (1 / 6))
        out.append(10 * np.log10(P[sel].sum() + 1e-20))
    return np.array(out)
