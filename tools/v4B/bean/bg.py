#!/usr/bin/env python3
"""v4 note 0:13 (the Bean): the wide plates' push, pre-rendered as a 1080p frame sequence (free).

    ~/Documents/moongazing/.venv/bin/python tools/v4B/bean/bg.py      # -> media/shots/S1_wide/bg_1080/ (00000.jpg.., fps.txt)

Why: drawn by the engine, the 5504 px Bean plane is minified about 5.7x into a 540p frame (2.9x at 1080p) with no
mipmaps, so its fine hatching crawled frame to frame during the hold (inter-frame change 11.8 grey levels in the Bean
vs 3.6 on the landed take). Here every frame is resampled with PIL's antialiased Lanczos (resize with a box, so the
filter widens with the minification) and given a slight motion blur (3 sub-frames over 0.2 frame).

The far plane (towers) and the Bean plane are composited here; her, the take and the arc lyric stay in the engine.
The transforms are the ones in render/timeline/A.js (`BEAN`): keep the two in step. Frame k is the song frame 303 + k
(lt = 0.025 + k/24 in S1); A.js plays the sequence with `in: -0.024` so sample times land on the frames.
"""
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.chdir(ROOT)
OUT = "media/shots/S1_wide/bg_1080"
BEAN_IMG, FAR_IMG = "media/sing/plates/plate_wide_v4_bean.png", "media/sing/plates/plate_wide_v4_far.jpg"

# --- the same numbers as BEAN in render/timeline/A.js -----------------------------------------------------------------
HER0, BEAN0, C, HZ, FAR1, FAR_K = 0.42, 0.47429, (955.79, 113.91), 752, 1.5, 1.55521
T0, T1, CREEP, DUR = 0.44, 1.32, 0.03, 3.54
PHASE = 303 / 24 - 12.6                      # lt of the first frame of S1 (12.625)
N = 34                                       # to lt 1.40, where the layer ends (the take is opaque from 1.32)
SUBS, SHUTTER = 3, 0.2                       # motion blur: sub-frames, shutter in frames (0.5 smeared the Bean behind a sharp her and lyric)


def ss(x):
    x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)


def e(lt):
    return CREEP * max(0.0, lt) / T0 if lt <= T0 else CREEP + (1 - CREEP) * (1 - (1 - ss((lt - T0) / (T1 - T0))) ** 1.4)


def g(lt):
    return 1 + 0.04 * min(1.0, max(0.0, lt / DUR))


def planes(lt):
    """(scale, x, y) per plane in the engine's convention: screen = 960 + x + scale * (p - 960), p in fitted design px"""
    sB = BEAN0 ** (1 - e(lt)); r = sB / BEAN0; rF = FAR1 ** e(lt); G = g(lt)
    bean = (G * r, G * (C[0] - 960) * (1 - r), G * (C[1] - 540) * (1 - r))
    far = (G * FAR_K * rF, G * (C[0] + r * (960 - C[0]) - 960), G * (C[1] + r * (HZ - C[1]) - 540 + rF * (540 - HZ)))
    return bean, far


def view(img, S, X, Y, size=(1920, 1080)):
    """the 1920x1080 frame of a fit-cover layer with transform (S, X, Y), antialiased"""
    f = max(1920 / img.width, 1080 / img.height)
    ox, oy = (1920 - img.width * f) / 2, (1080 - img.height * f) / 2            # cover centring
    box = []
    for u, v in ((0, 0), (1920, 1080)):
        px, py = 960 + (u - 960 - X) / S, 540 + (v - 540 - Y) / S              # fitted design px
        box += [(px - ox) / f, (py - oy) / f]
    return img.resize(size, Image.LANCZOS, box=tuple(box))


def main():
    os.makedirs(OUT, exist_ok=True)
    bean = Image.open(BEAN_IMG).convert("RGBa")                                  # premultiplied, so the edge filters right
    far = Image.open(FAR_IMG).convert("RGB")
    for k in range(N):
        lt = PHASE + k / 24
        acc = None
        for j in range(SUBS):
            t = lt + (j / (SUBS - 1) - 0.5) * SHUTTER / 24
            (bs, bx, by), (fs, fx, fy) = planes(t)
            fr = view(far, fs, fx, fy).convert("RGBA")
            fr.alpha_composite(view(bean, bs, bx, by).convert("RGBA"))
            fr = fr.convert("RGB")
            acc = fr if acc is None else Image.blend(acc, fr, 1 / (j + 1))       # running mean
        acc.save(f"{OUT}/{k:05d}.jpg", quality=94)
    open(f"{OUT}/fps.txt", "w").write("24\n")
    print("wrote", OUT, N, "frames")


if __name__ == "__main__":
    main()
