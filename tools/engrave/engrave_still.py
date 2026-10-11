#!/usr/bin/env python
"""Engrave still images: everything but Jade becomes a wood/line engraving.

  engrave_still.py IN.png [IN2.jpg ...] -o OUTDIR [--strength 0..1] [--upscale 2] [--matte-out DIR]
  engrave_still.py IN.png -o OUT.png ...         (single input -> explicit file name)

Each still is rendered with a few extra Gabor iterations (no previous frame to inherit from).
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from cli_common import add_look_args, params_from_args  # noqa: E402
from pipeline import Pipeline  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("-o", "--out", required=True, help="output file (single input) or directory")
    ap.add_argument("--matte-out", help="directory for matte PNGs")
    ap.add_argument("--matte-in", help="use this matte image instead of segmenting (white = Jade)")
    ap.add_argument("--bloom", help="grayscale mask: where colored-pencil colour shows in the world")
    ap.add_argument("--bloom-color", help="colour source for --bloom (default: the input itself)")
    ap.add_argument("--side-by-side", action="store_true", help="also write IN | OUT comparison")
    add_look_args(ap)
    a = ap.parse_args()
    params = params_from_args(a)
    params.iters_first = max(params.iters_first, 18)

    single = len(a.inputs) == 1 and os.path.splitext(a.out)[1].lower() in (".png", ".jpg", ".jpeg", ".webp")
    if not single:
        os.makedirs(a.out, exist_ok=True)
    if a.matte_out:
        os.makedirs(a.matte_out, exist_ok=True)

    pipe = None
    for path in a.inputs:
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        if img is None:
            print(f"!! cannot read {path}")
            continue
        rgb = img[:, :, ::-1].copy()
        h, w = rgb.shape[:2]
        if pipe is None or (pipe.sw, pipe.sh) != (w, h):
            pipe = Pipeline(w, h, params, upscale=a.upscale, out_height=a.out_height, upscaler=a.upscaler, world_upscaler=a.world_upscaler,
                            matte=not a.no_matte, keep_color=a.keep_color, seed=a.seed)
        pipe.reset()
        ext = cv2.imread(a.matte_in, cv2.IMREAD_GRAYSCALE) if a.matte_in else None
        bloom = cv2.imread(a.bloom, cv2.IMREAD_GRAYSCALE) if a.bloom else None
        bcol = cv2.imread(a.bloom_color)[:, :, ::-1].copy() if a.bloom_color else None
        if bloom is not None and bcol is None:
            bcol = cv2.resize(rgb, (pipe.ow, pipe.oh), interpolation=cv2.INTER_LANCZOS4)
        out, m = pipe(rgb, strength=a.strength, bloom=bloom, bloom_rgb=bcol, ext_matte=ext)
        stem = os.path.splitext(os.path.basename(path))[0]
        dst = a.out if single else os.path.join(a.out, stem + "_engraved.png")
        cv2.imwrite(dst, out[:, :, ::-1])
        if a.matte_out:
            cv2.imwrite(os.path.join(a.matte_out, stem + "_matte.png"), m)
        if a.side_by_side:
            src = cv2.resize(rgb, (pipe.ow, pipe.oh), interpolation=cv2.INTER_LANCZOS4)
            sbs = np.concatenate([src, out], 1)
            cv2.imwrite(os.path.splitext(dst)[0] + "_sbs.jpg", sbs[:, :, ::-1], [cv2.IMWRITE_JPEG_QUALITY, 92])
        print(f"{path} -> {dst}  ({pipe.ow}x{pipe.oh})")


if __name__ == "__main__":
    main()
