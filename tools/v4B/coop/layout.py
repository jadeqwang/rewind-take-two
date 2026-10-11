"""(Both mannequins are orange: the twins are generated identical and BLUE is recoloured afterwards, recolor.py.)
Composition sketches handed to the image model as a layout reference for the co-op room (no text in them).
    ~/Documents/moongazing/.venv/bin/python tools/v4B/coop/layout.py   -> media/shots/C_coop/layout_c1.png, layout_c2.png
Flat side elevation: table top line at 68% of the height, chasm from 36% to 64% of the width, the pencil lying across on
both table tops (eraser end left, point right), a dome button on each table (15% and 85%)."""
from PIL import Image, ImageDraw

W, H = 1920, 1080
OUT = "/home/jade/Documents/rewind-take-two/media/shots/C_coop/layout_%s.png"
TOP = int(H * 0.68)
LX, RX = int(W * 0.36), int(W * 0.64)
SLAB = 70
PT = 34                                  # pencil thickness
INK, GREY, PAPER = (20, 20, 20), (150, 150, 150), (244, 239, 228)


def base():
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    # giant leaning books behind (far left, far right)
    for pts in ([(40, TOP), (90, 150), (300, 170), (250, TOP)], [(1660, TOP), (1700, 170), (1900, 150), (1880, TOP)]):
        d.polygon(pts, fill=(228, 222, 208), outline=GREY)
    # the two tables, seen exactly edge-on: a slab and legs
    for x0, x1 in ((0, LX), (RX, W)):
        d.rectangle([x0, TOP, x1, TOP + SLAB], fill=(215, 208, 192), outline=INK, width=4)
        for lx in ((x0 + 60, x0 + 130), (x1 - 130, x1 - 60)):
            d.rectangle([lx[0], TOP + SLAB, lx[1], H], fill=(200, 193, 178), outline=INK, width=3)
    # the chasm: dark below
    d.rectangle([LX + 60, TOP + SLAB + 60, RX - 60, H], fill=(70, 70, 70))
    # the pencil: lying on both table tops, perfectly horizontal; eraser + ferrule at the left end, sharpened point right
    y0, y1 = TOP - PT, TOP
    x0, x1 = int(W * 0.315), int(W * 0.705)
    d.rectangle([x0 + 60, y0, x1 - 70, y1], fill=(250, 246, 236), outline=INK, width=3)
    d.line([x0 + 60, (y0 + y1) // 2, x1 - 70, (y0 + y1) // 2], fill=GREY, width=2)
    d.rectangle([x0 + 30, y0, x0 + 60, y1], fill=(180, 180, 180), outline=INK, width=3)          # ferrule
    d.rounded_rectangle([x0, y0, x0 + 30, y1], radius=8, fill=(235, 230, 220), outline=INK, width=3)  # eraser
    d.polygon([(x1 - 70, y0), (x1, (y0 + y1) // 2), (x1 - 70, y1)], fill=(240, 232, 215), outline=INK)   # sharpened cone
    d.polygon([(x1 - 22, (y0 + y1) // 2 - 7), (x1, (y0 + y1) // 2), (x1 - 22, (y0 + y1) // 2 + 7)], fill=INK)
    # the two buttons: a dome on a collar
    for bx in (int(W * 0.15), int(W * 0.85)):
        d.rectangle([bx - 95, TOP - 14, bx + 95, TOP], fill=(190, 184, 170), outline=INK, width=3)
        d.pieslice([bx - 80, TOP - 70, bx + 80, TOP + 42], 180, 360, fill=(250, 246, 236), outline=INK, width=3)
    return im, d


def fig(d, x, pose, col, face=1, h=330):
    """a crude mannequin: only says where a girl is, which way she faces, her pose and her accent colour"""
    y = TOP
    if pose == "run":
        hip, sh = (x, y - 0.46 * h), (x + face * 0.14 * h, y - 0.78 * h)
        legs = [[hip, (x + face * 0.2 * h, y - 0.24 * h), (x + face * 0.26 * h, y)], [hip, (x - face * 0.16 * h, y - 0.3 * h), (x - face * 0.34 * h, y - 0.18 * h)]]
    else:  # crouch, on a button (its dome top is 70 px above the table)
        y = TOP - 62
        hip, sh = (x - face * 0.04 * h, y - 0.24 * h), (x + face * 0.08 * h, y - 0.5 * h)
        legs = [[hip, (x + face * 0.18 * h, y - 0.3 * h), (x + face * 0.12 * h, y)], [hip, (x - face * 0.04 * h, y - 0.04 * h), (x - face * 0.2 * h, y)]]
    for L in legs:
        d.line(L, fill=(31, 42, 68), width=26, joint="curve")
    d.line([hip, sh], fill=(255, 255, 255), width=56)
    mid = lambda a: (hip[0] + (sh[0] - hip[0]) * a, hip[1] + (sh[1] - hip[1]) * a)
    d.line([mid(0.5), mid(0.75)], fill=col, width=56)
    hx, hy = sh[0] + face * 0.04 * h, sh[1] - 0.14 * h
    d.ellipse([hx - 36, hy - 36, hx + 36, hy + 36], fill=(250, 235, 220), outline=INK, width=3)
    d.ellipse([hx - face * 30 - 16, hy - 52, hx - face * 30 + 16, hy - 20], fill=INK)


def agent(d, x, h=350):
    y = TOP
    hip, sh = (x, y - 0.46 * h), (x + 0.14 * h, y - 0.8 * h)
    for L in ([hip, (x + 0.2 * h, y - 0.24 * h), (x + 0.26 * h, y)], [hip, (x - 0.16 * h, y - 0.3 * h), (x - 0.34 * h, y - 0.18 * h)]):
        d.line(L, fill=INK, width=30, joint="curve")
    d.line([hip, sh], fill=INK, width=64)
    d.line([sh, (sh[0] + 0.3 * h, sh[1] + 0.05 * h)], fill=INK, width=22)
    hx, hy = sh[0] + 0.04 * h, sh[1] - 0.14 * h
    d.ellipse([hx - 36, hy - 36, hx + 36, hy + 36], fill=(240, 240, 240), outline=INK, width=3)


ORANGE, BLUE = (240, 138, 36), (62, 111, 216)
im, d = base()
fig(d, int(W * 0.07), "run", ORANGE)
fig(d, int(W * 0.26), "run", ORANGE)
im.save(OUT % "c1")
im, d = base()
agent(d, int(W * 0.005))
agent(d, int(W * 0.065))
fig(d, int(W * 0.15), "crouch", ORANGE)
fig(d, int(W * 0.85), "crouch", ORANGE, face=-1)
im.save(OUT % "c2")
print(OUT % "c1", OUT % "c2")
