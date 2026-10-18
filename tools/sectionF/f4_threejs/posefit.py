#!/usr/bin/env python
"""Pose check: F4 source frames next to the check's case A from the same camera (and a 50% overlay).
    ~/Documents/1-music-shipped/moongazing/.venv/bin/python tools/sectionF/f4_threejs/posefit.py RAW_DIR OUT.jpg [frames]
RAW_DIR holds A_f{frame}_0.png from render.mjs (960x540)."""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
FF = os.path.expanduser("~/Documents/1-music-shipped/moongazing/.venv/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2")
raw, out = sys.argv[1], sys.argv[2]
frames = [int(v) for v in (sys.argv[3] if len(sys.argv) > 3 else "0,20,60").split(",")]
case = sys.argv[4] if len(sys.argv) > 4 else "A"
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
rows = []
for f in frames:
    b = subprocess.run([FF, "-v", "error", "-i", os.path.join(ROOT, "media/shots/F4/take_2_engraved_dered.mp4"), "-vf",
                        f"select=eq(n\\,{f}),scale=960:540", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       capture_output=True).stdout
    src = np.frombuffer(b, np.uint8).reshape(540, 960, 3).astype(float)
    ren = np.asarray(Image.open(os.path.join(raw, f"{case}_f{f:03d}_0.png")).convert("RGB")).astype(float)
    crop = lambda a: a[0:400, 230:730]       # her, feet to crown, and the reflection under her
    row = np.hstack([crop(src), crop(ren), crop(src * 0.5 + ren * 0.5)]).astype(np.uint8)
    im = Image.fromarray(row)
    d = ImageDraw.Draw(im)
    for k, t in enumerate([f"F4 src {f}", f"check, case {case}", "50/50"]):
        d.rectangle([k * 500, 0, k * 500 + 160, 22], fill=(0, 0, 0))
        d.text((k * 500 + 5, 2), t, fill=(255, 255, 255), font=font)
    rows.append(np.asarray(im))
Image.fromarray(np.vstack(rows)).save(out, quality=90)
