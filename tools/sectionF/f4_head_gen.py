#!/usr/bin/env python
"""v10c F4 (front3, Jade 2026-10-18): paint the BACK of her head over the face the video model drew under her crown.
In front3 her back is barely arched and her head is in line with her spine, so the camera (behind her) sees the back of
her head and the Bean sees her face. One nano-banana-pro edit of a 400 px crop round her head at src 30 (the v10b clean
plate, scaled to 1024), with the outfit sheet's BACK view as the hair reference; f4_reflection_v10.py --head tracks the
painted head onto every frame.

    ~/Documents/1-music-shipped/moongazing/.venv/bin/python tools/sectionF/f4_head_gen.py [--n 2] [--k0 1] [--dry-run]
Writes media/shots/F4/v10_head/head_<k>.png (spend tag v10c_f4head).
"""
import argparse
import concurrent.futures as cfut
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
import cf  # noqa: E402

OUT = os.path.join(ROOT, "media/shots/F4/v10_head")
PROMPT = (
    "Edit the first image and repaint ONLY her head. She is falling head-first and we see her from directly behind, so "
    "her head is at the bottom of the girl, her feet are above the top of the picture. Replace her face with the BACK of "
    "her head: a rounded mass of glossy black hair seen from behind, covering the whole area where the face is now, with "
    "the hair strands running up toward the top of the picture and merging into the long black hair already there. The "
    "lower edge of her head is a smooth rounded crown of black hair, a little higher than her chin is now. Keep the orange "
    "headphone band crossing her hair and both orange ear cups exactly where they are. Keep everything else exactly as it "
    "is, pixel for pixel: the white jacket sleeves, the '1420 MHz' patch, the collar, the background, the framing and size. "
    "Same hand-drawn black ink and colored-pencil style as the rest of the picture. No face, no skin, no eyes, no ears.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=2)
    ap.add_argument("--k0", type=int, default=1)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    inp = {"prompt": PROMPT, "aspect_ratio": "1:1", "image_size": "2K", "output_format": "png",
           "image_input": ["file:media/shots/F4/v10_head/kf030_in.png", "file:inputs/jade_in_outfit.png"]}

    def one(k):
        return cf.generate("google/nano-banana-pro", inp, os.path.join(OUT, f"head_{k}.png"), tag="v10c_f4head",
                           dry_run=a.dry_run)
    with cfut.ThreadPoolExecutor(a.n) as ex:
        for r in ex.map(one, range(a.k0, a.k0 + a.n)):
            print(r)


if __name__ == "__main__":
    main()
