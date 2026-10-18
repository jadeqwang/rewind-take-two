#!/usr/bin/env python
"""v10 F4: paint Jade's BACK in the F4 dive pose (one nano-banana-pro call per variant, ~$0.134 each).
The physically right Bean reflection in F4 shows her back (docs/revisions/v10/f4_reflection.md), and no clip has her
back in this pose. Refs: her own F4 frame 40 (pose, style) and the outfit sheet (the back of the jacket).

    ~/Documents/1-music-shipped/moongazing/.venv/bin/python tools/sectionF/f4_back_gen.py [--n 2] [--dry-run]
Writes media/shots/F4/v10_back/back_<k>.png (spend logged under tag v10_f4back).
"""
import argparse
import concurrent.futures as cfut
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
import cf  # noqa: E402

OUT = os.path.join(ROOT, "media/shots/F4/v10_back")
FFMPEG = os.environ.get("FFMPEG", os.path.expanduser(
    "~/Documents/1-music-shipped/moongazing/.venv/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"))
POSE = os.path.join(OUT, "ref_pose_f40.png")

PROMPT = (
    "Redraw the girl from the first image in EXACTLY the same pose, size and placement - upside down, falling head-first: "
    "her head at the bottom, her feet at the top, both arms stretched straight out to the sides and slightly up, legs "
    "together - but seen from directly BEHIND her, so we see her back, not her face. Show: the back of her head at the "
    "bottom, covered by her long loose black hair, which streams upward along her back toward her feet; the orange "
    "headphones around her neck seen from behind; the BACK of her white cropped bomber jacket, with the large pale-blue "
    "circle on the back and the small words RARE EARTH under it, exactly as in the BACK view of the second image, and "
    "the orange bands round both sleeves; the back of her navy wide cargo pants with back pockets and orange straps; "
    "the heels of her chunky white sneakers at the top. Her hands are open; the hand on the RIGHT side of the picture "
    "holds a small yellow pencil. Same hand-drawn look as the first image: clean anime cel shading with black ink "
    "outlines and light colored-pencil hatching. Plain flat white background, nothing else in the picture: no city, "
    "no sculpture, no reflection, no shadow. Only one girl, with exactly two arms. Zoom out so her WHOLE figure fits "
    "inside the picture with a clear white margin all round: both chunky white sneakers at the top fully visible, her "
    "head at the bottom fully visible, both hands fully visible.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=2)
    ap.add_argument("--k0", type=int, default=1, help="first output index")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if not os.path.exists(POSE):     # her F4 frame 40, cropped round her (feet to crown, hands)
        subprocess.run([FFMPEG, "-v", "error", "-y", "-i", os.path.join(ROOT, "media/shots/F4/take_2_engraved_dered_patch.mp4"),
                        "-vf", "select=eq(n\\,40),crop=900:640:510:0", "-frames:v", "1", POSE], check=True)
    inp = {"prompt": PROMPT, "aspect_ratio": "16:9", "image_size": "2K", "output_format": "png",
           "image_input": ["file:" + os.path.relpath(POSE, ROOT), "file:inputs/jade_in_outfit.png"]}

    def one(k):
        return cf.generate("google/nano-banana-pro", inp, os.path.join(OUT, f"back_{k}.png"), tag="v10_f4back",
                           dry_run=a.dry_run)
    with cfut.ThreadPoolExecutor(a.n) as ex:
        for r in ex.map(one, range(a.k0, a.k0 + a.n)):
            print(r)


if __name__ == "__main__":
    main()
