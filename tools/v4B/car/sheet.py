#!/usr/bin/env python
"""Contact sheet for the 1:30 car blockout: media/reviews/v4/B/plans/car/contact_sheet.jpg
   ~/Documents/moongazing/.venv/bin/python tools/v4B/car/sheet.py
Reads the stills written by capture.mjs and the measured numbers in info.json."""
import json, os
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
D = os.path.join(REPO, 'media/reviews/v4/B/plans/car')
info = json.load(open(os.path.join(D, 'info.json')))
font = lambda s, w=600: ImageFont.truetype(os.path.join(REPO, 'render/fonts/Overpass-wght.ttf'), s)
TW, TH, CAP, HEAD, PAD = 640, 360, 30, 46, 10
PAPER, INK, ORANGE = (236, 231, 220), (17, 17, 19), (240, 138, 36)

def plate(n):
    i = info[n]; return f"mirror {i['mirrorWidth_px']} px wide, lead plate {i['heroPlateWidth_px']} px (at 960x540)"

ROWS = [
    ("A (recommended)  Her eyes, then her view. The mirror stays where she would set it: no cheat.", [
        ("A_1_start", "90.14  over her right shoulder: wheel, dash, her eyes in the mirror"),
        ("A_2_cutin", "91.02  cut to her eye line: the mirror at real size, the fleet in it"),
        ("A_3_end", "92.79  end of the push: " + plate("A_3_end"))]),
    ("B  Mirror turned 18.6 degrees to the lens (film-set cheat): wide, then cut in along the same line.", [
        ("B_1_start", "90.14  same wide shot, but the mirror shows the fleet"),
        ("B_2_cutin", "91.02  cut in between the front seats"),
        ("B_3_end", "92.79  end: " + plate("B_3_end"))]),
    ("C  B as one take: hold wide, then push between the seats to the mirror (no cut at 91.02).", [
        ("C_1_start", "90.14  start"),
        ("C_2_mid", "91.35  mid-push: both lyric surfaces are on screen at once"),
        ("C_3_end", "92.79  end: " + plate("C_3_end"))]),
    ("Checks", [
        ("X_true_plates", "ordinary plates read backwards in any mirror (A's last frame)"),
        ("X_plan_A", "top view, A: orange = her sight line (out the back), blue = lens (her face)"),
        ("X_plan_B", "top view, B: mirror re-aimed so the lens sees out the back instead")]),
]
W = PAD + 3 * (TW + PAD)
Hh = PAD + sum(HEAD + TH + CAP + PAD for _ in ROWS)
sheet = Image.new('RGB', (W, Hh), PAPER); d = ImageDraw.Draw(sheet)
y = PAD
for title, tiles in ROWS:
    d.text((PAD, y + 8), title, font=font(25), fill=ORANGE if title.startswith('A') else INK)
    y += HEAD
    for k, (name, cap) in enumerate(tiles):
        x = PAD + k * (TW + PAD)
        im = Image.open(os.path.join(D, name + '.png')).convert('RGB').resize((TW, TH), Image.LANCZOS)
        sheet.paste(im, (x, y)); d.text((x + 2, y + TH + 5), cap, font=font(17), fill=INK)
    y += TH + CAP + PAD
out = os.path.join(D, 'contact_sheet.jpg'); sheet.save(out, quality=90); print('wrote', out, sheet.size)
