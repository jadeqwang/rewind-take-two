#!/usr/bin/env python3
"""Singing Jade (v9w): eye patches on the TAKE itself (so the synced file and every ear-test clip show the patched eyes),
and ear-test clips that look like the film: the matted figure over the plate, the song under it.

    MPY=~/Documents/1-music-shipped/orbital-sunrise-video/video/out/.venv/bin/python
    EPY=tools/engrave/.venv/bin/python   PY=~/Documents/1-music-shipped/moongazing/.venv/bin/python
    $MPY tools/sing/v9w_post.py patch SHOT TAKE REF:FIRST-LAST[:FADE] [...]   (take frame numbers)
         -> media/sing/SHOT/TAKE_open.mp4 (720p, chained v4_noblink.py passes; checks in TAKE_open_check_<FIRST>.jpg)
    WC_VER=v9w $EPY tools/sing/wc_post.py matte SHOT TAKE_open        -> TAKE_open_matte/ (per take frame, 1920x1080)
    $PY  tools/sing/v9w_post.py ear SHOT TAKE_open LAG OUT [--audio=MIX]
         -> OUT: 960x540, song in-out of the shot, take frame = round((song_t - ref_t0 + LAG) * 24), the figure matted over
            the plate (the first-frame crop of media/sing/plates/...), the song under it. Before the take starts or after
            it ends the nearest take frame is held (reported).
"""
import json
import os
import subprocess
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SING = os.path.join(ROOT, "media/sing")
FF = os.environ.get("FFMPEG", "ffmpeg")
SHOTS = {"S1": (12.90, 12.60, 19.64, "media/sing/plates/plate_close_1.jpg"),
         "V3S": (153.68, 153.98, 159.14, "media/sing/plates/plate_truth_1.jpg")}
MIX = os.path.join(ROOT, "media/sfx/Rewind_cinematic_sfx_mix_v5coda.mp3")


def patch(shot, take, specs):
    import shutil
    src = os.path.join(SING, shot, take + ".mp4")
    out = os.path.join(SING, shot, take + "_open.mp4")
    tmp = [os.path.join(SING, shot, f"_{take}_p{i}.mp4") for i in range(len(specs))]
    cur = src
    for i, sp in enumerate(specs):
        parts = sp.split(":")
        ref = parts[0]
        f0, f1 = parts[1].split("-")
        fade = parts[2] if len(parts) > 2 else "2"
        dst = out if i == len(specs) - 1 else tmp[i]
        subprocess.run([sys.executable, os.path.join(ROOT, "tools/sing/v4_noblink.py"), cur, dst, ref, f0, f1, f"--fade={fade}"],
                       check=True, stderr=subprocess.DEVNULL)
        chk = os.path.splitext(dst)[0] + "_check.jpg"
        if os.path.exists(chk):
            shutil.move(chk, os.path.join(SING, shot, f"{take}_open_check_{f0}.jpg"))
        md = dst[:-4] + "_matte"
        if os.path.islink(md):
            os.remove(md)
        cur = dst
    for t in tmp:
        for f in (t, t[:-4] + "_matte"):
            if os.path.islink(f) or os.path.exists(f):
                os.remove(f)
    print(os.path.relpath(out, ROOT), "patched:", specs)


def ear(shot, take, lag, out, audio=MIX):
    import av
    from PIL import Image
    t0, a, b, plate = SHOTS[shot]
    crop = json.load(open(os.path.join(SING, "first/crop.json")))["box"]
    P = Image.open(os.path.join(ROOT, plate)).convert("RGB").crop(tuple(crop)).resize((960, 540), Image.LANCZOS)
    P = np.asarray(P, np.float32)
    with av.open(os.path.join(SING, shot, take + ".mp4")) as c:
        F = [f.to_ndarray(format="rgb24") for f in c.decode(c.streams.video[0])]
    md = os.path.join(SING, shot, take + "_matte")
    n = int(round((b - a) * 24))
    held = 0
    cmd = [FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "960x540", "-r", "24", "-i", "-",
           "-ss", f"{a:.3f}", "-t", f"{n / 24:.3f}", "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset",
           "slow", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    cache = {}
    for k in range(n):
        i = int(round((a + k / 24 - t0 + lag) * 24))
        if i < 0 or i >= len(F):
            held += 1
        i = min(max(i, 0), len(F) - 1)
        if i not in cache:
            fr = np.asarray(Image.fromarray(F[i]).resize((960, 540), Image.LANCZOS), np.float32)
            m = np.asarray(Image.open(os.path.join(md, f"{i:05d}.png")).resize((960, 540), Image.BILINEAR), np.float32)[..., None] / 255
            cache = {i: np.clip(fr * m + P * (1 - m) + 0.5, 0, 255).astype(np.uint8)}
        p.stdin.write(cache[i].tobytes())
    p.stdin.close()
    assert p.wait() == 0
    print(os.path.relpath(out, ROOT), f"lag {lag:+.2f}", f"({held} frames held at the take's ends)" if held else "")


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    o = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    if a[0] == "patch":
        patch(a[1], a[2], a[3:])
    elif a[0] == "ear":
        ear(a[1], a[2], float(a[3]), a[4], o.get("audio", MIX))
