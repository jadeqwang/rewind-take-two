#!/usr/bin/env python3
"""v9 fix #2 (D3): the final keyframe, free composite of two nano-banana edits.

kf_v9_e has the right mirror optics (the sedan is OUTSIDE, seen through her rear window above the rear seats and
parcel shelf) but its bumper and plate are hidden by the shelf; kf_v9_d has the same sedan with its plate but sitting
between the rear seats (inside the cabin). D's sedan is laid into E's rear-window opening 37 px higher (it covers E's own sedan), clipped to the
opening, so its blank plate (TVA 1729 is pinned by the engine) shows just above the shelf.
    $PY tools/v9/mirrors/d3_kf_fix.py   -> media/shots/D3/kf_v9.png (+ .jpg)
"""
import os

from PIL import Image, ImageDraw, ImageFilter

ROOT = "/home/jade/Documents/rewind-take-two"
BASE, CAR = "media/shots/D3/kf_v9_e.png", "media/shots/D3/kf_v9_d.png"
OUT = "media/shots/D3/kf_v9.png"
# design px (1920x1080)
OPENING = [(972, 232), (1458, 232), (1484, 338), (950, 338)]          # E's rear window, seen in the mirror
CAR_POLY = [(1170, 256), (1276, 256), (1290, 286), (1304, 290), (1304, 304), (1296, 308), (1296, 372),
            (1148, 372), (1148, 308), (1140, 304), (1140, 290), (1154, 286)]   # D's sedan
SHIFT = -37
SCALE, ANCHOR = 1.0, (1222, 372)   # (scale < 1 lets E's own sedan show round it)


def main():
    base = Image.open(os.path.join(ROOT, BASE)).convert("RGB")
    k = base.width / 1920
    car0 = Image.open(os.path.join(ROOT, CAR)).convert("RGB").resize(base.size, Image.LANCZOS)
    # scale D about ANCHOR (the bumper), so the polygon below is scaled the same way
    big = car0.resize((round(base.width * SCALE), round(base.height * SCALE)), Image.LANCZOS)
    car = Image.new("RGB", base.size)
    car.paste(big, (round(ANCHOR[0] * k * (1 - SCALE)), round(ANCHOR[1] * k * (1 - SCALE))))
    sc = lambda p, dy=0: [(x * k, (y + dy) * k) for x, y in p]
    m_car = Image.new("L", base.size, 0)
    poly = [(ANCHOR[0] + SCALE * (x - ANCHOR[0]), ANCHOR[1] + SCALE * (y - ANCHOR[1])) for x, y in CAR_POLY]
    ImageDraw.Draw(m_car).polygon(sc(poly), fill=255)
    m_car = m_car.filter(ImageFilter.GaussianBlur(1.5 * k))
    shifted = Image.new("RGB", base.size)
    shifted.paste(car, (0, round(SHIFT * k)))
    m_shift = Image.new("L", base.size, 0)
    m_shift.paste(m_car, (0, round(SHIFT * k)))
    m_open = Image.new("L", base.size, 0)
    ImageDraw.Draw(m_open).polygon(sc(OPENING), fill=255)
    m_open = m_open.filter(ImageFilter.GaussianBlur(1.0 * k))
    from PIL import ImageChops
    m = ImageChops.multiply(m_shift, m_open)
    base.paste(shifted, (0, 0), m)
    base.save(os.path.join(ROOT, OUT))
    base.save(os.path.join(ROOT, OUT.replace(".png", ".jpg")), quality=93)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
