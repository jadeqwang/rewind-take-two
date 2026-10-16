#!/usr/bin/env python3
"""v9 fix #2 (D3): bake a slow push toward the rear-view mirror into the engraved take, so the TVA 1729 plate and the
etched lyric read (the interior mirror is ~30 % of the frame wide, where the old door mirror filled half of it). It
rhymes with the 1:30 push into the same mirror. The push runs over the shot's 3.06 s (A.js D3: in 0, rate 1), eased
in and out, about the mirror's centre, so the mirror stays put on screen and her bun slides out at the left.
    $PY tools/v9/mirrors/d3_push.py   -> media/shots/D3/v9_take_2_push.mp4
"""
import math
import os

import sys

import av
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stem import paint_stem  # noqa: E402

# round 2: the take's stem was two pale edges with the night between them; a solid stem from the mount (bottom
# y~176) into the mirror housing (top y~232), painted on every source frame (the mirror holds within 1 px in the take)
STEM = dict(top=(1216, 174), bottom=(1216, 230), w_top=26, w_bot=22, joint=False)   # ends on the housing's top edge
# the take's two pale stem edges (x 1191-1240) are covered first with the windshield's own line texture from 70 px right
CLEAR, CLEAR_DX = (1186, 178, 1247, 229), 70


def clear_stem(im):
    x0, y0, x1, y1 = CLEAR
    im.paste(im.crop((x0 + CLEAR_DX, y0, x1 + CLEAR_DX, y1)), (x0, y0))
    return im

ROOT = "/home/jade/Documents/rewind-take-two"
SRC = os.path.join(ROOT, "media/shots/D3/v9_take_2_engraved.mp4")
OUT = os.path.join(ROOT, "media/shots/D3/v9_take_2_push_r2.mp4")   # round 2 (v9_take_2_push.mp4 = round 1)
PIVOT = (1215.0, 300.0)      # mirror centre, design px
Z_END, DUR = 1.9, 3.06     # round 2: 1.38 -> 1.9, eased OUT: her eye for the first second ("me I"), then the mirror, so the plate and etch read at 540p
DROP0, DROP1 = 70.0, 0.0    # the picture sits lower at the start (70 px), so the 2.39 letterbox
                             # shows the roof liner and the stem's mount above the mirror, and her eye stays above the lower bar


def zoom(t):
    u = max(0.0, min(1.0, t / DUR))
    return 1 + (Z_END - 1) * (1 - (1 - u) ** 2)


def drop_at(z):
    return DROP0 + (DROP1 - DROP0) * (z - 1) / (Z_END - 1)


def main():
    src = av.open(SRC)
    vs = src.streams.video[0]
    out = av.open(OUT, "w")
    st = out.add_stream("libx264", rate=24)
    st.width, st.height, st.pix_fmt = 1920, 1080, "yuv420p"
    st.options = {"crf": "13", "preset": "slow"}
    for i, f in enumerate(src.decode(video=0)):
        src_im = Image.new("RGB", (1920, 1080 + 200))     # 200 px of black above: under the top letterbox bar
        src_im.paste(paint_stem(clear_stem(f.to_image().resize((1920, 1080), Image.LANCZOS)), 1.0, **STEM), (0, 200))
        z = zoom(i / 24)
        drop = drop_at(z)
        x0, y0 = PIVOT[0] - PIVOT[0] / z, PIVOT[1] - (PIVOT[1] + drop) / z + 200
        im = src_im.resize((1920, 1080), Image.LANCZOS, box=(x0, y0, x0 + 1920 / z, y0 + 1080 / z))
        for p in st.encode(av.VideoFrame.from_image(im)):
            out.mux(p)
    for p in st.encode():
        out.mux(p)
    out.close()
    print("wrote", os.path.relpath(OUT, ROOT), vs.width, vs.height)


if __name__ == "__main__":
    main()
