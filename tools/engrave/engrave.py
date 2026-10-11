#!/usr/bin/env python
"""Engrave a video: the world becomes a black-ink wood engraving, Jade (the matte) stays in colour.

  engrave.py IN.mp4 OUT.mp4 [--matte-out DIR] [--strength 0..1] [--preview] [--upscale 2]

--strength          0..1 (default 1). Lower it for frames that are already engraved.
--ramp-in SECONDS   ramp strength from --strength-start (default 0.25) up to --strength over the first
                    N seconds: a plate's crisp first frame is kept, the engraving takes over as the
                    video model drifts into gray wash.
--preview           also write OUT_sbs.mp4 (source | engraved | matte) for review.
--bloom MASK.mp4    grayscale mask video/image: colored-pencil colour shows through the world there,
                    taken from --bloom-color (video/image; default: the input).
Audio is copied from IN when present.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import av  # noqa: E402
import cv2  # noqa: E402
import numpy as np  # noqa: E402

from cli_common import add_look_args, params_from_args  # noqa: E402
from pipeline import Pipeline  # noqa: E402


def find_ffmpeg():
    for c in (os.environ.get("FFMPEG"), os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg"),
              shutil.which("ffmpeg")):
        if c and os.path.exists(c):
            return c
    sys.exit("ffmpeg not found (set FFMPEG=)")


class Writer:
    def __init__(self, path, w, h, fps, audio_from=None, crf=14):
        self.path = path
        cmd = [find_ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{w}x{h}", "-r", str(fps), "-i", "-"]
        if audio_from:
            cmd += ["-i", audio_from, "-map", "0:v", "-map", "1:a?", "-c:a", "copy", "-shortest"]
        cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p",
                "-tune", "grain", "-movflags", "+faststart", path]
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    def write(self, rgb):
        self.p.stdin.write(np.ascontiguousarray(rgb).tobytes())

    def close(self):
        self.p.stdin.close()
        self.p.wait()


class FrameSource:
    """Video or still image (repeated) as RGB uint8 frames, resized to (w,h) if given."""

    def __init__(self, path, gray=False):
        self.gray = gray
        self.img = None
        if os.path.splitext(path)[1].lower() in (".png", ".jpg", ".jpeg", ".webp"):
            flag = cv2.IMREAD_GRAYSCALE if gray else cv2.IMREAD_COLOR
            im = cv2.imread(path, flag)
            self.img = im if gray else im[:, :, ::-1].copy()
        else:
            self.c = av.open(path)
            self.it = self.c.decode(video=0)
            self.last = None

    def next(self):
        if self.img is not None:
            return self.img
        try:
            fr = next(self.it)
            self.last = fr.to_ndarray(format="gray" if self.gray else "rgb24")
        except StopIteration:
            pass
        return self.last


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--matte-out", help="directory: matte PNG sequence (output res) + matte.mp4")
    ap.add_argument("--matte-in", help="matte video/PNG to use instead of segmenting (white = Jade)")
    ap.add_argument("--preview", action="store_true", help="also write OUT_sbs.mp4 (source | engraved | matte)")
    ap.add_argument("--ramp-in", type=float, default=0.0, help="seconds to ramp strength in from --strength-start")
    ap.add_argument("--strength-start", type=float, default=0.25)
    ap.add_argument("--bloom", help="grayscale mask video/image for colored-pencil colour in the world")
    ap.add_argument("--bloom-color", help="colour source video/image for --bloom (default: input)")
    ap.add_argument("--max-frames", type=int, default=0)
    ap.add_argument("--crf", type=int, default=16, help="x264 CRF (line art is bitrate-hungry: ~10-15 MB/s at 1080p)")
    add_look_args(ap)
    a = ap.parse_args()
    params = params_from_args(a)

    cin = av.open(a.input)
    vs = cin.streams.video[0]
    fps = vs.average_rate
    has_audio = len(cin.streams.audio) > 0
    sw, sh = vs.codec_context.width, vs.codec_context.height
    pipe = Pipeline(sw, sh, params, upscale=a.upscale, out_height=a.out_height, upscaler=a.upscaler, world_upscaler=a.world_upscaler,
                    matte=not a.no_matte, keep_color=a.keep_color, seed=a.seed)
    ow, oh = pipe.ow, pipe.oh
    os.makedirs(os.path.dirname(os.path.abspath(a.output)), exist_ok=True)
    wr = Writer(a.output, ow, oh, fps, a.input if has_audio else None, crf=a.crf)
    sbs = None
    if a.preview:
        pw = (ow // 2) // 2 * 2
        ph = (oh // 2) // 2 * 2
        sbs = Writer(os.path.splitext(a.output)[0] + "_sbs.mp4", pw * 2, ph * 2, fps, crf=18)
    mw = None
    if a.matte_out:
        os.makedirs(a.matte_out, exist_ok=True)
        mw = Writer(os.path.join(a.matte_out, "matte.mp4"), ow, oh, fps, crf=12)
    mat_src = FrameSource(a.matte_in, gray=True) if a.matte_in else None
    bloom_src = FrameSource(a.bloom, gray=True) if a.bloom else None
    bcol_src = FrameSource(a.bloom_color) if a.bloom_color else None

    t0 = time.time()
    n = 0
    for fr in cin.decode(vs):
        rgb = fr.to_ndarray(format="rgb24")
        tsec = n / float(fps)
        s = a.strength
        if a.ramp_in > 0 and tsec < a.ramp_in and s != "auto":
            u = tsec / a.ramp_in
            u = u * u * (3 - 2 * u)
            s = a.strength_start + (a.strength - a.strength_start) * u
        ext = mat_src.next() if mat_src else None
        bl = bloom_src.next() if bloom_src else None
        bc = bcol_src.next() if bcol_src else None
        if bl is not None and bc is None:
            bc = rgb
        out, m = pipe(rgb, strength=s, bloom=bl, bloom_rgb=bc, ext_matte=ext)
        wr.write(out)
        if mw:
            cv2.imwrite(os.path.join(a.matte_out, f"{n:05d}.png"), m)
            mw.write(np.repeat(m[:, :, None], 3, 2))
        if sbs:
            src = cv2.resize(rgb, (pw, ph), interpolation=cv2.INTER_AREA)
            o2 = cv2.resize(out, (pw, ph), interpolation=cv2.INTER_AREA)
            m2 = cv2.resize(m, (pw, ph), interpolation=cv2.INTER_AREA)
            tint = (src * 0.35 + np.repeat(m2[:, :, None], 3, 2) / 255.0 * src * 0.65).astype(np.uint8)
            top = np.concatenate([src, o2], 1)
            bot = np.concatenate([tint, cv2.resize(out[oh // 4: oh // 4 + oh // 2, ow // 4: ow // 4 + ow // 2],
                                                   (pw, ph), interpolation=cv2.INTER_NEAREST)], 1)
            sbs.write(np.concatenate([top, bot], 0))
        n += 1
        if n % 24 == 0:
            el = time.time() - t0
            print(f"  frame {n}  {n / el:.2f} fps", flush=True)
        if a.max_frames and n >= a.max_frames:
            break
    wr.close()
    if sbs:
        sbs.close()
    if mw:
        mw.close()
    el = time.time() - t0
    T = pipe.timing
    k = max(1, T["n"])
    print(f"{a.input} -> {a.output}  {n} frames {ow}x{oh}  {el:.1f}s  {n / el:.2f} fps  "
          f"(per frame ms: flow {1000 * T['flow'] / k:.0f}, matte {1000 * T['matte'] / k:.0f}, "
          f"upscale {1000 * T['up'] / k:.0f}, engrave {1000 * T['engrave'] / k:.0f})")


if __name__ == "__main__":
    main()
