"""v9 round 2: a solid rear-view-mirror stem, drawn in the engraving's hand: a mid-grey body (paper crossed by fine ink
lines, like the mount above it), an ink contour, a shadow side, one paper highlight, and a ball joint where it enters
the mirror housing. The models drew the stem as two pale edges with the night showing between them, which read as a
mirror hanging free of the car (Jade's #2/#3); a dark painted body still read that way (the lead's note), so the body
is lighter than the windshield behind it.

    paint_stem(img, k, top, bottom, w_top, w_bot)   img: RGB or RGBA PIL image; k: image px per design px;
                                                     top/bottom: (x, y) design px of the stem's centre line
"""
from PIL import Image, ImageDraw

INK, PAPER, MID = (12, 12, 13), (236, 231, 220), (168, 164, 156)


def paint_stem(img, k, top, bottom, w_top, w_bot, joint=True):
    ss = 4                                   # draw supersampled, then shrink: clean anti-aliased edges
    x0 = min(top[0], bottom[0]) - max(w_top, w_bot) - 12
    x1 = max(top[0], bottom[0]) + max(w_top, w_bot) + 12
    y0, y1 = top[1] - 4, bottom[1] + max(w_top, w_bot)
    bx0, by0 = int(x0 * k), int(y0 * k)
    bw, bh = int(x1 * k) - bx0, int(y1 * k) - by0
    L = Image.new("RGBA", (bw * ss, bh * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    f = lambda x, y: ((x * k - bx0) * ss, (y * k - by0) * ss)
    # x of the point at fraction u across the stem, at height y (the stem tapers from w_top to w_bot)
    hx = lambda u, y: (top[0] - w_top / 2 + u * w_top) * (1 - (y - top[1]) / (bottom[1] - top[1])) + \
        (bottom[0] - w_bot / 2 + u * w_bot) * ((y - top[1]) / (bottom[1] - top[1]))
    px = lambda w: max(1, round(w * k * ss))
    tl, tr = f(top[0] - w_top / 2, top[1]), f(top[0] + w_top / 2, top[1])
    br, bl = f(bottom[0] + w_bot / 2, bottom[1]), f(bottom[0] - w_bot / 2, bottom[1])
    d.polygon([tl, tr, br, bl], fill=MID + (255,))
    y = top[1] + 1.2
    while y < bottom[1]:                                                 # fine ink lines across the body
        d.line([f(hx(0.0, y), y), f(hx(1.0, y), y)], fill=INK + (150,), width=px(0.7))
        y += 2.3
    d.line([f(hx(0.72, top[1]), top[1]), f(hx(0.72, bottom[1]), bottom[1])], fill=INK + (200,), width=px(0.25 * w_bot))   # shadow side
    d.line([f(hx(0.28, top[1]), top[1]), f(hx(0.28, bottom[1]), bottom[1])], fill=PAPER + (255,), width=px(0.12 * w_bot))  # highlight
    d.line([tl, bl], fill=INK + (255,), width=px(1.6))                   # contour
    d.line([tr, br], fill=INK + (255,), width=px(1.6))
    if joint:
        r = w_bot * 0.7
        cx, cy = bottom
        d.ellipse([f(cx - r, cy - r), f(cx + r, cy + r)], fill=MID + (255,), outline=INK + (255,), width=px(1.6))
        d.arc([f(cx - r * 0.6, cy - r * 0.6), f(cx + r * 0.6, cy + r * 0.6)], 200, 290, fill=PAPER + (255,), width=px(0.8))
    L = L.resize((bw, bh), Image.LANCZOS)
    base = img.convert("RGBA")
    base.alpha_composite(L, (bx0, by0))
    return base if img.mode == "RGBA" else base.convert("RGB")
