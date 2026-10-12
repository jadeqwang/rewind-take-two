"""v4 phase 3 (Jade: "part of the pencil bridge mechanism is missing"): the drawbridge hinge at the NEAR lip, drawn as
an engraved iron bracket (B/W), and the plate patch that hides the pencil's short tail when the bridge is raised.
    ~/Documents/moongazing/.venv/bin/python tools/v4B/coop/hinge.py -> media/shots/C_coop/hinge.png, patch_tail.png"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

D = "/home/jade/Documents/rewind-take-two/media/shots/C_coop"
PX, PY = 700, 634                     # pivot (design px): the pencil's axis where it leaves the near desk
INK, PAPER = (24, 22, 20, 255), (241, 236, 226, 255)
S = 4
im = Image.new("RGBA", (1920 * S, 1080 * S), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
s = lambda *v: [x * S for x in v]
# bracket: two cheek plates either side of the pencil, bolted to the desk lip, a strap down the desk side
d.polygon(s(PX - 44, PY - 46, PX + 30, PY - 46, PX + 44, PY + 52, PX - 30, PY + 52), fill=PAPER, outline=INK)
d.line(s(PX - 44, PY - 46, PX + 30, PY - 46, PX + 44, PY + 52, PX - 30, PY + 52, PX - 44, PY - 46), fill=INK, width=5 * S)
for k in range(-40, 50, 7):           # engraved hatching on the plate, following its slope
    d.line(s(PX - 40 + 0.14 * (k + 46), PY + k, PX + 34 + 0.14 * (k + 46), PY + k), fill=INK, width=int(1.6 * S))
d.rectangle(s(PX - 30, PY + 52, PX + 40, PY + 66), fill=INK)                     # foot plate on the desk lip
for bx in (PX - 18, PX + 26):
    d.ellipse(s(bx - 5, PY + 55, bx + 5, PY + 63), fill=PAPER)                   # bolts
# the pin through the pencil: a white ring with a black centre and a highlight
d.ellipse(s(PX - 17, PY - 17, PX + 17, PY + 17), fill=PAPER, outline=INK, width=5 * S)
d.ellipse(s(PX - 7, PY - 7, PX + 7, PY + 7), fill=INK)
d.arc(s(PX - 12, PY - 12, PX + 12, PY + 12), 200, 260, fill=PAPER, width=2 * S)
im = im.resize((1920, 1080), Image.LANCZOS)
im.save(f"{D}/hinge.png")
plate = Image.open(f"{D}/plate.png").convert("RGBA")
m = Image.new("L", (1920, 1080), 0)
ImageDraw.Draw(m).polygon([(520, 672), (PX - 2, 672), (PX - 2, 900), (520, 900)], fill=255)
patch = plate.copy()
patch.putalpha(m)
patch.save(f"{D}/patch_tail.png")
print("hinge", PX, PY)
