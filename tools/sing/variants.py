#!/usr/bin/env python3
"""Singing Jade, step 7: lip-timing variants for her to pick by ear (the handbook: offer several timings, A/B/C side by
side in one composite so they cannot drift).

    PY=~/Documents/moongazing/.venv/bin/python
    $PY tools/sing/variants.py SHOT take_N LAG [--step=0.15]

B plays the take at the measured LAG (clip_time = song_time - ref_t0 + LAG); A = lips `step` s earlier (LAG + step),
C = lips `step` s later (LAG - step). Each covers the shot's in-out (tools/sing/takes.py SHOTS) with the song mix
(analysis/cinematic/source.wav) under it; if the take does not reach, its first/last frame is held (reported).
Writes media/sing/review/<SHOT>_<take>_{A,B,C}.mp4 (1280x720) and <SHOT>_<take>_ABC.mp4 (three across, 1920x360)."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen  # noqa: E402
from takes import SHOTS  # noqa: E402

MIX = os.path.join(ROOT, "analysis/cinematic/source.wav")
REV = os.path.join(ROOT, "media/sing/review")
FF = gen.FFMPEG
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
X = ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
     "-movflags", "+faststart"]


def label(text, out, w=640, h=34):
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, h), fill=(0, 0, 0, 150))
    d.text((8, 6), text, font=ImageFont.truetype(FONT, 18), fill=(255, 220, 90, 255))
    im.save(out)
    return out


def one(shot, take, lag, out):
    s = SHOTS[shot]
    t_in, t_out = s["in_out"]
    D = t_out - t_in
    mp4 = os.path.join(ROOT, "media/sing", shot, take + ".mp4")
    L = gen.probe(mp4)["duration"]
    cs = t_in - s["ref_t0"] + lag
    head = max(0.0, -cs)
    tail = max(0.0, cs + D - L)
    vf = (f"tpad=start_mode=clone:start_duration={head + 0.05:.3f}:stop_mode=clone:stop_duration={tail + 0.5:.3f},"
          f"trim=start={cs + head + 0.05:.4f}:duration={D:.4f},setpts=PTS-STARTPTS,fps=24,"
          f"scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2")
    subprocess.run([FF, "-v", "error", "-y", "-i", mp4, "-ss", f"{t_in:.3f}", "-t", f"{D:.3f}", "-i", MIX,
                    "-filter_complex", f"[0:v]{vf}[v]", "-map", "[v]", "-map", "1:a", "-shortest"] + X + [out], check=True)
    return dict(clip_in=round(cs, 3), clip_out=round(cs + D, 3), held_head_s=round(head, 3), held_tail_s=round(tail, 3))


def main(shot, take, lag, step=0.15):
    os.makedirs(REV, exist_ok=True)
    V = {"A": lag + step, "B": lag, "C": lag - step}
    info = {}
    paths = {}
    for k, L in V.items():
        p = os.path.join(REV, f"{shot}_{take}_{k}.mp4")
        info[k] = dict(lag=round(L, 3), **one(shot, take, L, p))
        paths[k] = p
    names = {"A": f"A  lips {step:.2f}s earlier", "B": "B  measured", "C": f"C  lips {step:.2f}s later"}
    labs = [label(f"{names[k]}  (lag {V[k]:+.2f})", os.path.join(REV, f"_lab_{k}.png")) for k in V]
    comp = os.path.join(REV, f"{shot}_{take}_ABC.mp4")
    fc = ""
    for i, k in enumerate(V):
        fc += f"[{i}:v]scale=640:360[s{i}];[s{i}][{i + 3}:v]overlay=0:0[l{i}];"
    fc += "[l0][l1][l2]hstack=inputs=3[v]"
    cmd = [FF, "-v", "error", "-y"] + sum([["-i", paths[k]] for k in V], []) + sum([["-i", lb] for lb in labs], [])
    subprocess.run(cmd + ["-filter_complex", fc, "-map", "[v]", "-map", "1:a"] + X + [comp], check=True)
    for lb in labs:
        os.remove(lb)
    js = os.path.join(REV, f"{shot}_{take}_ABC.json")
    json.dump({"shot": shot, "take": take, "ref_t0": SHOTS[shot]["ref_t0"], "in_out": SHOTS[shot]["in_out"],
               "rule": "clip_time = song_time - ref_t0 + lag", "variants": info}, open(js, "w"), indent=1)
    print(json.dumps(info))
    print(comp)


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    o = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    main(a[0], a[1], float(a[2]), float(o.get("step", 0.15)))
