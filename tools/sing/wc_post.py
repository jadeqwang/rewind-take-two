#!/usr/bin/env python3
"""Watercolor singing Jade (v3), step 7: engine files and review clips from a chosen take. Every frame stays the take's
own frame (no push-in, no grain, no recolour: she is meant to mismatch the engraved world, and the engine adds grain).

    PY=~/Documents/moongazing/.venv/bin/python      EPY=tools/engrave/.venv/bin/python
    $PY  tools/sing/wc_post.py up SHOT v3_take_N                 -> media/sing/SHOT/v3_take_N_1080.mp4 (Lanczos, CRF 12)
    $EPY tools/sing/wc_post.py matte SHOT v3_take_N              -> media/sing/SHOT/v3_take_N_matte/00000.png ... + fps.txt
                                                                    (her matte per frame, 1920x1080, L; BiRefNet)
    $PY  tools/sing/wc_post.py sync SHOT [--name=N]              -> media/sing/SHOT/v3_sync_1080.mp4 (or N.mp4): the chosen take, lip-
                                                                    synced by the SYNC knots below; file time 0 = shot in
    $PY  tools/sing/wc_post.py review_sync SHOT OUT              -> OUT: 960x540 review clip of the same, song under it
    $PY  tools/sing/wc_post.py review SHOT v3_take_N LAG OUT [--audio=MIX] [--pad=0]
                                                                 -> OUT: 960x540 H.264 of the shot's song range with the
                                                                    song under it (clip_time = song_time - ref_t0 + LAG)
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SING = os.path.join(ROOT, "media/sing")
FF = os.environ.get("FFMPEG", os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg"))
MIX = os.path.join(ROOT, "media/sfx/Rewind_cinematic_sfx_mix.mp3")
SHOTS = {"S1": (12.90, 12.60, 19.64), "E3": (119.14, 119.44, 122.95), "V3S": (153.68, 153.98, 159.14)}   # ref_t0, in, out


def up(shot, take):
    src = os.path.join(SING, shot, take + ".mp4")
    out = os.path.join(SING, shot, take + "_1080.mp4")
    subprocess.run([FF, "-v", "error", "-y", "-i", src, "-vf", "scale=1920:1080:flags=lanczos", "-an", "-c:v", "libx264",
                    "-preset", "slow", "-crf", "12", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709",
                    "-color_trc", "bt709", "-movflags", "+faststart", out], check=True)
    print(os.path.relpath(out, ROOT), os.path.getsize(out) // 1024, "KB")


def matte(shot, take):
    import av
    import numpy as np
    import torch
    from PIL import Image
    sys.path.insert(0, os.path.join(ROOT, "tools/engrave"))
    from gpulock import GpuSlot
    from matte import get_birefnet
    src = os.path.join(SING, shot, take + ".mp4")
    d = os.path.join(SING, shot, take + "_matte")
    os.makedirs(d, exist_ok=True)
    slot = GpuSlot(label="wc_post matte")
    slot.acquire()
    net = get_birefnet("cuda")
    n = 0
    with av.open(src) as c:
        for f in c.decode(c.streams.video[0]):
            a = f.to_ndarray(format="rgb24").astype(np.float32) / 255
            x = torch.from_numpy(a).permute(2, 0, 1)[None].cuda()
            m = net(x)[0, 0].clamp(0, 1).cpu().numpy()
            Image.fromarray((m * 255).astype(np.uint8)).resize((1920, 1080), Image.LANCZOS).save(os.path.join(d, f"{n:05d}.png"))
            n += 1
    open(os.path.join(d, "fps.txt"), "w").write("24\n")
    print(os.path.relpath(d, ROOT), n, "frames")


def review(shot, take, lag, out, audio=MIX, pad=0.0):
    t0, a, b = SHOTS[shot]
    a, b = a - pad, b + pad
    src = os.path.join(SING, shot, take + ".mp4")
    cin = a - t0 + lag
    hold = max(0.0, -cin)                       # the take starts after the shot: its first frame is held (reported)
    vf = f"tpad=start_mode=clone:start_duration={hold:.3f}," if hold else ""
    vf += "tpad=stop_mode=clone:stop_duration=2,scale=960:540:flags=lanczos"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.run([FF, "-v", "error", "-y", "-ss", f"{max(cin, 0):.3f}", "-i", src, "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}",
                    "-i", audio, "-filter_complex", f"[0:v]{vf}[v]", "-map", "[v]", "-map", "1:a", "-t", f"{b - a:.3f}",
                    "-r", "24", "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac",
                    "-b:a", "192k", "-movflags", "+faststart", out], check=True)
    print(os.path.relpath(out, ROOT), os.path.getsize(out) // 1024, "KB; clip", round(cin, 3), "to", round(b - t0 + lag, 3),
          f"(first frame held {hold:.2f} s)" if hold else "")


# Lip sync as knots (song time, clip time), linear between them and rate 1 outside. Where a stretch is not rate 1
# the neighbouring frames are cross-faded; at rate 1 the nearest frame is used untouched.
#   S1: the take's lag grows through the phrase (0.58 s at "before", about 1.0 s from "my" on), so the clip runs 1.3x
#       through the silence between the two halves (14.70-16.10).
#   E3: Seedance closes the vowel about 1 s before the sung note ends (both takes), so the open vowel (clip 0.86-3.30)
#       is stretched over the whole note (rate 0.74) and the mouth closes on the note's end.
#   V3S: one lag, +0.16 s (lip closures on 'b' of before and 'm' of my).
VER = os.environ.get("WC_VER", "v3")      # v4: WC_VER=v4 reads SYNC_V4 and writes v4_sync_1080.mp4 (v5: SYNC_V5, v5_sync_1080.mp4)
SYNC = {
    "S1": ("v3_take_1", [(12.60, 0.28), (14.70, 2.38), (16.10, 4.20), (19.64, 7.74)]),
    "E3": ("v3_take_1", [(119.44, 0.86), (122.75, 3.30), (122.95, 3.50)]),
    "V3S": ("v3_take_2", [(153.98, 0.46), (159.14, 5.62)]),
}
# v4 (glossier hair, less smile): filled in once the v4 takes are measured (look.py SHOT v4_take_N). E3 is gone in v4.
#   S1 v4_take_1: lip closures 'b' +0.47, 'm' +0.41, opening +0.49: one lag, +0.45 s, untouched frames. (v4_take_2 drifts
#       0.39 -> 0.66 and blinks at 12.9.)
#   V3S v4_take_2: closures +0.04 / +0.06, correlation +0.13 (r .68): one lag, +0.09 s, untouched frames. (v4_take_1 has no
#       blink but its mouth runs at about 0.9x for the first three seconds, lag 0 -> -0.3, so it would need a retime.)
SYNC_V4 = {
    "S1": ("v4_take_1", [(12.60, 0.15), (19.64, 7.19)]),
    "V3S": ("v4_take_2", [(153.98, 0.39), (159.14, 5.55)]),
}
# v5 (Jade's two photos, 2026-10-16; media/sing/NOTES.md "v5"). Lags from look.py plus a windowed check (best lag of
# the mouth against the vocal level in 2 s windows every 0.5 s):
#   S1 v5_take_2: open +0.45, 'b' of before +0.55, windows 13.0-15.0: +0.41 / +0.30 / +0.53 / +0.39 / +0.53 (r .5-.85):
#       one lag, +0.46 s, untouched frames. Only "The night before" (13.20-14.60) is sung while she is on screen (S1 cuts
#       away at 16.14). (v5_take_1: windows jump -0.15 .. +1.35, its mouth does not follow the voice.)
#   V3S v5_take_1: 'b' of before closes at +0.00, window 154.5 +0.03; from 155.5 on every window is +0.29/+0.30
#       (r .76-.96). So +0.05 through "before" (ends 155.50), the clip runs 1.24x through the silence 155.60-156.60
#       (cross-faded frames, no words there), then +0.29 for "my dissertation defense". (v5_take_2: windows jump
#       -0.18 .. +1.14, r .24-.6.)
#   S1 re-sync (Jade on the v5 preview: "the video lags behind audio"): at +0.46 the take's 'b' closure lands at 13.93
#       against the voice's dip at 13.85, and its widest opening (14.35) trails the "be-FORE" vowel (13.90-14.20).
#       Over the on-screen phrase alone (13.05-14.95) the inner-lip gap correlates best at +0.55 (r .66), the jaw at
#       +0.55; the 'b' closure says +0.59. Now +0.61 (written as v5_sync_1080_l061*; the +0.46 files are kept).
#       Ear-test variants: media/sing/review/v5_S1_lag+0.61/0.76/0.91_*.mp4. Was: [(12.60, 0.16), (19.64, 7.20)].
SYNC_V5 = {
    "S1": ("v5_take_2", [(12.60, 0.31), (19.64, 7.35)]),
    "V3S": ("v5_take_1", [(153.98, 0.35), (155.60, 1.97), (156.60, 3.21), (159.14, 5.75)]),
}
# v5b: the V3S shoulder retake (Jade: "yes, do the shoulder retake"), first frame tools/sing/v5_first.py V5_REV=b.
#   v5b_take_1 came back 21:9 (1470x630): rejected. v5b_take_2 (16:9): 'b' of before closes at -0.13, 'm' of my -0.23,
#   opening +0.12, phrase end +0.04; correlation -0.04 (r .66); every 2 s window from 156.0 to 158.0 -0.07..-0.02
#   (r .58-.83; the windows that reach into the silent pre-roll say +0.87/+1.08 and disagree with every closure).
#   One lag, -0.05 s, untouched frames.
SYNC_V5B = {
    "V3S": ("v5b_take_2", [(153.98, 0.25), (159.14, 5.41)]),
}
# v5c: S1 from the re-tinted pencils photo (Jade: "local_a is good"; first frame v5_first.py V5_REV=c).
#   v5c_take_1: its mouth runs against the voice over "The night before" (best -0.45, r .33): reject.
#   v5c_take_2: over the on-screen phrase (13.05-14.95) the inner-lip gap correlates best at +0.10 (r .82); at +0.10 the
#   mouth opens at 13.17 (voice 13.15), closes for 'b' at 13.88 (voice dip 13.85) and is widest on "fore" (14.15-14.40).
#   Wired at +0.15 (lips 0.05 s ahead of the measurement, leaning early after Jade's note on the old take; r .78).
#   Ear-test variants +0.00 / +0.15 / +0.30: media/sing/review/v5c_S1_lag*.mp4. The shot starts 0.15 s before the take:
#   its first frame (the start image) is held for 4 frames (12.60-12.75).
#   Jade by ear (2026-10-16): +0.30 "closer but the lips are still late"; +0.90 "about right, for the first half" ("my
#   dissertation defense" is on the cutaway). Wired at +0.90 as v5c_sync_1080_l090 (--name); +0.15 was:
#   [(12.60, -0.15), (19.64, 6.89)] -> v5c_sync_1080.mp4.
SYNC_V5C = {
    "S1": ("v5c_take_2", [(12.60, 0.60), (19.64, 7.64)]),
}
# v5d: V3S from the outpainted first frame (couch removed; tools/sing/v5_outpaint.py, v5_first.py V5_REV=d).
#   v5d_take_1: closures +0.42 / +0.52, opening +0.74; 2 s windows jump -0.49 .. +1.37, phrase r .34; eyes shut 0.6-1.1 s
#       and 3.9-4.2 s of the clip: reject (unsteady). v5d_take_2: closures 'b' +0.17, 'm' +0.14, phrase end -0.00;
#       inner-lip gap over the whole phrase best at +0.15 (r .48); sung windows 156.0-157.5 +0.21..+0.39 (r .73-.92).
#   Jade (on v5b): "the timing on the original v5b is good" -> V3S is wired at the MEASURED lag, +0.15, untouched frames.
SYNC_V5D = {
    "V3S": ("v5d_take_2", [(153.98, 0.45), (159.14, 5.61)]),
}
if VER == "v4":
    SYNC = SYNC_V4
elif VER == "v5":
    SYNC = SYNC_V5
elif VER == "v5b":
    SYNC = SYNC_V5B
elif VER == "v5c":
    SYNC = SYNC_V5C
elif VER == "v5d":
    SYNC = SYNC_V5D


def clip_time(keys, t):
    if t <= keys[0][0]:
        return keys[0][1] + (t - keys[0][0]), 1.0
    for (t0, c0), (t1, c1) in zip(keys, keys[1:]):
        if t <= t1:
            r = (c1 - c0) / (t1 - t0)
            return c0 + (t - t0) * r, r
    return keys[-1][1] + (t - keys[-1][0]), 1.0


def synced_frames(shot, a, b):
    """Frames (uint8 RGB, the take's size) for song times a..b at 24 fps; stops where the take ends."""
    import av
    import numpy as np
    take, keys = SYNC[shot]
    with av.open(os.path.join(SING, shot, take + ".mp4")) as c:
        F = [f.to_ndarray(format="rgb24") for f in c.decode(c.streams.video[0])]
    out, blended = [], 0
    for k in range(int(round((b - a) * 24))):
        ct, r = clip_time(keys, a + k / 24)
        pos = ct * 24
        if pos > len(F) - 1 + 0.5:
            break
        if pos < -0.5:                  # the shot starts before the take does (small lag): hold the take's first frame,
            out.append(F[0])            # which is the start image itself (v5c S1 at +0.15: 4 frames, 12.60-12.75)
            continue
        if abs(r - 1) < 0.02:
            out.append(F[int(min(max(round(pos), 0), len(F) - 1))])
        else:
            i = int(min(max(np.floor(pos), 0), len(F) - 2))
            w = float(min(max(pos - i, 0), 1))
            out.append((F[i].astype(np.float32) * (1 - w) + F[i + 1].astype(np.float32) * w + 0.5).astype(np.uint8))
            blended += 1
    return out, blended


def encode(frames, out, size, crf, audio=None, ss=0.0):
    h, w = frames[0].shape[:2]
    cmd = [FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", "24", "-i", "-"]
    if audio:
        cmd += ["-ss", f"{ss:.3f}", "-t", f"{len(frames) / 24:.3f}", "-i", audio, "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-vf", f"scale={size}:flags=lanczos", "-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-pix_fmt", "yuv420p",
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(f.tobytes())
    p.stdin.close()
    assert p.wait() == 0


def sync(shot, tail=0.4, name=None):
    """media/sing/SHOT/v3_sync_1080.mp4 (or NAME.mp4): file time 0 = the shot's in-point, lip-synced."""
    _, a, b = SHOTS[shot]
    frames, bl = synced_frames(shot, a, b + tail)
    out = os.path.join(SING, shot, f"{name or VER + '_sync_1080'}.mp4")
    encode(frames, out, "1920:1080", 12)
    print(os.path.relpath(out, ROOT), len(frames), "frames =", round(len(frames) / 24, 3), "s (shot", round(b - a, 3), "s);",
          bl, "cross-faded frames;", os.path.getsize(out) // 1024, "KB; take", SYNC[shot][0])


def review_sync(shot, out, audio=MIX):
    _, a, b = SHOTS[shot]
    frames, _ = synced_frames(shot, a, b)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    encode(frames, out, "960:540", 20, audio, a)
    print(os.path.relpath(out, ROOT), os.path.getsize(out) // 1024, "KB,", round(len(frames) / 24, 2), "s")


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    o = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    if a[0] == "up":
        up(a[1], a[2])
    elif a[0] == "matte":
        matte(a[1], a[2])
    elif a[0] == "sync":
        sync(a[1], float(o.get("tail", 0.4)), o.get("name"))
    elif a[0] == "review_sync":
        review_sync(a[1], a[2], o.get("audio", MIX))
    elif a[0] == "review":
        review(a[1], a[2], float(a[3]), a[4], o.get("audio", MIX), float(o.get("pad", 0)))
