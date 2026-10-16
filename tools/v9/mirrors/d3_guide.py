#!/usr/bin/env python3
"""v9 fix #2 (D3): layout guide for the new D3 keyframe, built from the roof-fixed 1:30 wide so both shots are the
same car interior (the shotlist calls V2f "same composition as D3").

The camera moves in, close behind her right ear: the interior (roof liner, header, mirror on its stem, windshield,
dash) is the v9 wide scaled 1.5x about the mirror; she is the same still's cut-out (its matte) scaled 1.5x and shifted
right toward the mirror (parallax: she is much nearer the lens than the mirror is).
    $PY tools/v9/mirrors/d3_guide.py   -> media/shots/D3/v9_guide.png
"""
import os

from PIL import Image

ROOT = "/home/jade/Documents/rewind-take-two"
WIDE = os.path.join(ROOT, "media/shots/V2f3/v9_roof_a.png")
MATTE = os.path.join(ROOT, "media/shots/V2f3/v9_roof_a_matte/v9_roof_a_matte.png")
OUT = os.path.join(ROOT, "media/shots/D3/v9_guide.png")
W, H = 2752, 1548                 # 2K 16:9, design px x 1.4333
k = W / 1920
MIRROR_C = (1335.8, 436.5)        # mirror centre in the wide (design px)
BG_S, BG_DST = 1.5, (1210, 330)   # interior: scale, where the mirror centre lands (design px)
JADE_S, JADE_DX, JADE_DY = 1.4, -30, -60


def place(src, s, a_src, a_dst):
    """src (design-scaled 1920x1080 RGBA) scaled by s so that point a_src lands on a_dst; returns a WxH RGBA."""
    big = src.resize((round(1920 * s * k), round(1080 * s * k)), Image.LANCZOS)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(big, (round((a_dst[0] - a_src[0] * s) * k), round((a_dst[1] - a_src[1] * s) * k)))
    return out


def main():
    wide = Image.open(WIDE).convert("RGB").resize((1920, 1080), Image.LANCZOS).convert("RGBA")
    m = Image.open(MATTE).convert("L").resize((1920, 1080), Image.LANCZOS)
    # only her head and shoulders (not her seat back / arms below the shoulder line)
    jade = wide.copy()
    jade.putalpha(m)
    # the interior without her: her own (scaled) figure would show twice, so it becomes flat grey for the model to fill
    from PIL import ImageFilter
    hole = m.filter(ImageFilter.MaxFilter(9))
    empty = wide.copy()
    empty.paste((128, 128, 128, 255), (0, 0), hole)
    bg = place(empty, BG_S, MIRROR_C, BG_DST)
    fg = place(jade, JADE_S, (0, 0), (JADE_DX, JADE_DY))
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    canvas.alpha_composite(bg)
    canvas.alpha_composite(fg)
    canvas.convert("RGB").save(OUT)
    print("wrote", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
