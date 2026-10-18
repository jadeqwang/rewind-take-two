#!/usr/bin/env python
"""Before/after sheets for v10b F4 (v9 | front2) (docs/revisions/v10/f4/). Crops round her head and the reflection.
    ~/Documents/1-music-shipped/moongazing/.venv/bin/python tools/sectionF/f4_v10_sheets.py
"""
import json
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FF = os.path.expanduser("~/Documents/1-music-shipped/moongazing/.venv/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2")
S = os.path.join(ROOT, "media/shots/F4")
OUT = os.path.join(ROOT, "docs/revisions/v10/f4")
CLIPS = [("v9 (in the cut)", "take_2_engraved_dered_v9refl.mp4"),
         ("v10 front2", "take_2_engraved_dered_v10refl_front2.mp4")]
IN, RATE = 180.02, 1.3
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 17)
bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 19)
band = json.load(open(os.path.join(S, "v9_work/band.json")))


def frames(path, idx):
    raw = subprocess.run([FF, "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.uint8).reshape(-1, 1080, 1920, 3)
    return {i: a[i] for i in idx}


def label(i):
    t = IN + i / 24 / RATE
    return f"src {i}  song {int(t // 60)}:{t % 60:05.2f}  f{int(t * 24)}"


def sheet(idx, name, cw=520, ch=390, full=False):
    data = [(lab, frames(os.path.join(S, f), idx)) for lab, f in CLIPS]
    tw, th = (480, 270) if full else (cw, ch)
    im = Image.new("RGB", (220 + len(idx) * tw, len(data) * th + 30), (18, 18, 18))
    d = ImageDraw.Draw(im)
    for k, i in enumerate(idx):
        d.text((220 + k * tw + 6, 6), label(i), fill=(240, 240, 240), font=font)
    for r, (lab, fr) in enumerate(data):
        d.text((8, 30 + r * th + th // 2 - 10), lab, fill=(240, 160, 64), font=bold)
        for k, i in enumerate(idx):
            f = Image.fromarray(fr[i])
            if full:
                f = f.resize((tw, th), Image.LANCZOS)
            else:
                c = int(band[i]) + 112
                y0 = min(1080 - 585, max(0, c - 260))       # 780 x 585 round her crown
                f = f.crop((958 - 390, y0, 958 + 390, y0 + 585)).resize((tw, th), Image.LANCZOS)
            im.paste(f, (220 + k * tw, 30 + r * th))
    im.save(os.path.join(OUT, name), quality=88)
    print("wrote", name)


os.makedirs(OUT, exist_ok=True)
sheet([0, 20, 40, 52, 60, 66, 70, 74], "before_after_detail.jpg")
sheet([0, 30, 52, 66, 74, 84], "before_after_full.jpg", full=True)
