#!/usr/bin/env python
"""Zoomed crops round the reflection (1080p renders from render.mjs --w 1920 --h 1080 --modes 0,1).
    python zoom.py HI_DIR MEASURE.json OUT.jpg
Rows: cases; columns: frames; each crop is 2x the reflection's box (from the 960 id pass), normal over x-ray."""
import json, sys, os
from PIL import Image, ImageDraw, ImageFont
hi, meas, out = sys.argv[1], json.load(open(sys.argv[2])), sys.argv[3]
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
cases = sys.argv[4].split(",") if len(sys.argv) > 4 else ["A", "B", "C"]
frames = [0, 40, 60, 70, 76]
TW, TH = 300, 200
sheet = Image.new("RGB", (TW * len(frames), 2 * TH * len(cases)), (20, 20, 20))
for r, c in enumerate(cases):
    for k, f in enumerate(frames):
        m = meas[f"{c}_f{f}"]
        if "bbox" in m:
            x0, y0, x1, y1 = [2 * v for v in m["bbox"]]
        else:
            x0, y0, x1, y1 = 900, 600, 1020, 700
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        w = max(x1 - x0, 1.5 * (y1 - y0), 90) * 1.5
        h = w * TH / TW
        for mode in (0, 1):
            im = Image.open(os.path.join(hi, f"{c}_f{f:03d}_{mode}.png")).convert("RGB")
            crop = im.crop((int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2))).resize((TW, TH), Image.LANCZOS)
            d = ImageDraw.Draw(crop)
            d.rectangle([0, 0, TW, 20], fill=(0, 0, 0))
            d.text((4, 2), f"{c}  frame {f}  {m['dist_m']} m" + ("  x-ray" if mode else ""), fill=(255, 255, 255), font=font)
            sheet.paste(crop, (k * TW, (2 * r + mode) * TH))
sheet.save(out, quality=90)
