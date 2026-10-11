"""Storyboard for the 2:00 co-op level (plan: docs/revisions/v4/plans/coop.md).
Rough stick-figure level diagrams, side view. Run:
  ~/Documents/moongazing/.venv/bin/python tools/v4B/coop/storyboard.py
-> media/reviews/v4/B/plans/coop/storyboard.jpg (1920 px wide)
  ... storyboard.py --animatic
-> media/shots/C_coop/animatic/p2.png .. p9.png: each level panel alone at 1920x1080 with its title, its caption and
   an ANIMATIC label, for the C1/C2 placeholder shots in tools/sections/D/build_timeline.py"""
import math
import os
import sys
from PIL import Image, ImageDraw, ImageFont

ROOT = "/home/jade/Documents/rewind-take-two"
OUT = f"{ROOT}/media/reviews/v4/B/plans/coop/storyboard.jpg"
ANIMATIC = "--animatic" in sys.argv
S = 2                                   # supersample
W = 1920
COLS, ROWS = 3, 3
M = 14                                  # margin
TITLE_H = 92
PW = (W - M * (COLS + 1)) // COLS       # panel width
PH = round(PW * 9 / 16)
HEAD_H, CAP_H = 34, 62
ROW_H = HEAD_H + PH + CAP_H + M
H = TITLE_H + ROWS * ROW_H + M

PAPER, INK, GREY, PALE = "#F4EFE4", "#1b1b1b", "#8a8478", "#d9d2c2"
ORANGE, BLUE = "#F08A24", "#3E6FD8"
DJ = "/usr/share/fonts/truetype/dejavu/"
if ANIMATIC:
    S = 1920 / PW                       # one panel fills a 1920x1080 frame
F = lambda name, size: ImageFont.truetype(name, int(round(size * S)))
f_title = F(DJ + "DejaVuSans-Bold.ttf", 24)
f_sub = F(DJ + "DejaVuSans.ttf", 15)
f_head = F(DJ + "DejaVuSans-Bold.ttf", 18)
f_cap = F(DJ + "DejaVuSans.ttf", 15)
f_lab = F(DJ + "DejaVuSans-Bold.ttf", 13)
f_lab_s = F(DJ + "DejaVuSans.ttf", 12)
f_px = F(f"{ROOT}/render/fonts/PressStart2P-Regular.ttf", 11)

img = Image.new("RGB", (16, 16) if ANIMATIC else (W * S, H * S), "#22201d")
d = ImageDraw.Draw(img)


def s(v):
    return int(round(v * S))


def line(pts, fill=INK, w=4):
    d.line([(s(x), s(y)) for x, y in pts], fill=fill, width=s(w), joint="curve")


def circ(x, y, r, fill=None, outline=INK, w=3):
    d.ellipse([s(x - r), s(y - r), s(x + r), s(y + r)], fill=fill, outline=outline, width=s(w))


def rect(x0, y0, x1, y1, fill=None, outline=INK, w=2):
    d.rectangle([s(x0), s(y0), s(x1), s(y1)], fill=fill, outline=outline, width=s(w) if outline else 0)


def text(x, y, t, font=f_lab, fill=INK, anchor="la"):
    d.text((s(x), s(y)), t, font=font, fill=fill, anchor=anchor)


def arrow(x0, y0, x1, y1, fill=INK, w=4, head=12, dash=False):
    if dash:
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 14))
        for k in range(n):
            if k % 2 == 0:
                a, b = k / n, (k + 1) / n
                line([(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a), (x0 + (x1 - x0) * b, y0 + (y1 - y0) * b)], fill, w)
    else:
        line([(x0, y0), (x1, y1)], fill, w)
    ang = math.atan2(y1 - y0, x1 - x0)
    p = [(x1, y1), (x1 - head * math.cos(ang - 0.45), y1 - head * math.sin(ang - 0.45)),
         (x1 - head * math.cos(ang + 0.45), y1 - head * math.sin(ang + 0.45))]
    d.polygon([(s(x), s(y)) for x, y in p], fill=fill)


# ------------------------------------------------------------------ figures (x = hips, y = feet baseline)
def jade(x, y, pose, who, face=1, tag=True, h=104):
    """who: 'O' orange or 'B' blue (same girl, same outfit: only the ring, the tag and the trail differ)."""
    col = ORANGE if who == "O" else BLUE
    u = h / 100.0
    f = face
    # player ring on the floor
    if pose != "air":
        d.ellipse([s(x - 30 * u), s(y - 5 * u), s(x + 30 * u), s(y + 7 * u)], outline=col, width=s(4))
    if pose == "run":
        hip = (x, y - 46 * u)
        sh = (x + f * 16 * u, y - 80 * u)
        legs = [[hip, (x + f * 20 * u, y - 24 * u), (x + f * 30 * u, y)], [hip, (x - f * 18 * u, y - 30 * u), (x - f * 34 * u, y - 16 * u)]]
        arms = [[sh, (x + f * 30 * u, y - 68 * u), (x + f * 38 * u, y - 80 * u)], [sh, (x - f * 4 * u, y - 62 * u), (x - f * 16 * u, y - 56 * u)]]
    elif pose == "crouch":
        hip = (x - f * 4 * u, y - 24 * u)
        sh = (x + f * 8 * u, y - 52 * u)
        legs = [[hip, (x + f * 18 * u, y - 30 * u), (x + f * 14 * u, y)], [hip, (x - f * 2 * u, y - 4 * u), (x - f * 20 * u, y)]]
        arms = [[sh, (x + f * 22 * u, y - 30 * u), (x + f * 24 * u, y - 4 * u)], [sh, (x - f * 8 * u, y - 34 * u), (x - f * 6 * u, y - 12 * u)]]
    elif pose == "air":
        y = y - 26 * u
        hip = (x, y - 40 * u)
        sh = (x + f * 14 * u, y - 74 * u)
        legs = [[hip, (x + f * 22 * u, y - 30 * u), (x + f * 16 * u, y - 8 * u)], [hip, (x - f * 16 * u, y - 34 * u), (x - f * 30 * u, y - 22 * u)]]
        arms = [[sh, (x + f * 30 * u, y - 86 * u), (x + f * 40 * u, y - 98 * u)], [sh, (x - f * 8 * u, y - 78 * u), (x - f * 20 * u, y - 88 * u)]]
    else:  # stand
        hip = (x, y - 48 * u)
        sh = (x, y - 82 * u)
        legs = [[hip, (x + 8 * u, y - 24 * u), (x + 10 * u, y)], [hip, (x - 8 * u, y - 24 * u), (x - 10 * u, y)]]
        arms = [[sh, (x + f * 14 * u, y - 64 * u), (x + f * 20 * u, y - 48 * u)], [sh, (x - f * 10 * u, y - 62 * u), (x - f * 12 * u, y - 46 * u)]]
    for L in legs:
        line(L, "#1f2a44", 6 * u)                       # navy cargo pants
    line([hip, sh], "#fbfbf8", 13 * u)                   # white jacket
    line([hip, sh], INK, 15 * u) if False else None
    # jacket outline + the orange band
    mx, my = (hip[0] + sh[0]) / 2, (hip[1] + sh[1]) / 2
    line([(hip[0] + (sh[0] - hip[0]) * 0.55, hip[1] + (sh[1] - hip[1]) * 0.55), (hip[0] + (sh[0] - hip[0]) * 0.8, hip[1] + (sh[1] - hip[1]) * 0.8)], ORANGE, 13 * u)
    for A in arms:
        line(A, INK, 4 * u)
    hx, hy = sh[0] + f * 5 * u, sh[1] - 15 * u
    circ(hx, hy, 12 * u, fill="#fbf3e6", outline=INK, w=2.5)
    d.pieslice([s(hx - 12 * u), s(hy - 13 * u), s(hx + 12 * u), s(hy + 11 * u)], 180, 360, fill=INK)   # hair
    bx, by = hx - f * 8 * u, hy - 14 * u
    circ(bx, by, 6.5 * u, fill=INK, outline=INK, w=1)    # bun
    line([(bx - 10 * u, by - 9 * u), (bx + 9 * u, by + 7 * u)], "#E8C23A", 2.5 * u)   # two crossed pencils, in the bun
    line([(bx + 10 * u, by - 9 * u), (bx - 9 * u, by + 7 * u)], "#E8C23A", 2.5 * u)
    if tag:
        ty = hy - 36 * u
        text(hx, ty, "1P", f_px, col, "mb")
        d.polygon([(s(hx - 6), s(ty + 3)), (s(hx + 6), s(ty + 3)), (s(hx), s(ty + 11))], fill=col)
    return hx, hy


def trail(x0, y0, x1, y1, who):
    col = ORANGE if who == "O" else BLUE
    pts = []
    for k in range(25):
        a = k / 24
        pts.append((x0 + (x1 - x0) * a, y0 + (y1 - y0) * a + 5 * math.sin(a * 9)))
    line(pts, col, 6)


def agent(x, y, pose="run", face=1, h=112):
    u = h / 100.0
    f = face
    if pose == "run":
        hip = (x, y - 46 * u)
        sh = (x + f * 12 * u, y - 82 * u)
        legs = [[hip, (x + f * 20 * u, y - 24 * u), (x + f * 28 * u, y)], [hip, (x - f * 16 * u, y - 28 * u), (x - f * 32 * u, y - 14 * u)]]
        arms = [[sh, (x + f * 30 * u, y - 70 * u), (x + f * 44 * u, y - 76 * u)], [sh, (x - f * 6 * u, y - 62 * u), (x - f * 18 * u, y - 58 * u)]]
    elif pose == "grab":
        hip = (x, y - 46 * u)
        sh = (x + f * 20 * u, y - 78 * u)
        legs = [[hip, (x + f * 22 * u, y - 22 * u), (x + f * 30 * u, y)], [hip, (x - f * 16 * u, y - 26 * u), (x - f * 34 * u, y - 8 * u)]]
        arms = [[sh, (x + f * 42 * u, y - 74 * u), (x + f * 60 * u, y - 70 * u)], [sh, (x + f * 40 * u, y - 86 * u), (x + f * 58 * u, y - 84 * u)]]
    elif pose == "teeter":
        hip = (x, y - 46 * u)
        sh = (x - f * 12 * u, y - 82 * u)
        legs = [[hip, (x + f * 6 * u, y - 22 * u), (x + f * 12 * u, y)], [hip, (x + f * 16 * u, y - 30 * u), (x + f * 36 * u, y - 22 * u)]]
        arms = [[sh, (x - f * 30 * u, y - 100 * u), (x - f * 44 * u, y - 116 * u)], [sh, (x + f * 14 * u, y - 100 * u), (x + f * 26 * u, y - 118 * u)]]
    elif pose == "stomp":
        hip = (x, y - 46 * u)
        sh = (x + f * 2 * u, y - 84 * u)
        legs = [[hip, (x - f * 8 * u, y - 22 * u), (x - f * 10 * u, y)], [hip, (x + f * 18 * u, y - 34 * u), (x + f * 16 * u, y - 10 * u)]]
        arms = [[sh, (x + f * 14 * u, y - 66 * u), (x + f * 22 * u, y - 52 * u)], [sh, (x - f * 10 * u, y - 64 * u), (x - f * 14 * u, y - 48 * u)]]
    else:  # down (in the heap)
        hip = (x, y - 14 * u)
        sh = (x + f * 30 * u, y - 26 * u)
        legs = [[hip, (x - f * 22 * u, y - 22 * u), (x - f * 40 * u, y - 4 * u)], [hip, (x - f * 20 * u, y - 4 * u), (x - f * 40 * u, y - 30 * u)]]
        arms = [[sh, (x + f * 44 * u, y - 8 * u)], [sh, (x + f * 20 * u, y - 44 * u)]]
    for L in legs:
        line(L, INK, 7 * u)
    line([hip, sh], INK, 17 * u)
    for A in arms:
        line(A, INK, 6 * u)
    hx, hy = sh[0] + f * 4 * u, sh[1] - 16 * u
    circ(hx, hy, 11 * u, fill="#f3ede0", outline=INK, w=2.5)
    line([(hx - 10 * u, hy - 2 * u), (hx + 10 * u, hy - 2 * u)], INK, 5 * u)   # sunglasses
    return hx, hy


# ------------------------------------------------------------------ the room
def room(ox, oy, bridge=0.0, glow=None, near=None, far=None, books=True):
    """bridge: 0 parked on the far side .. 1 across the gap. glow: colour of the bridge. near / far: colour of a
    pressed button (None = up). Returns geometry (floor y, lips, button x)."""
    fy = oy + PH * 0.70
    lx, rx = ox + PW * 0.37, ox + PW * 0.63
    if books:                                            # giant books standing behind, pale
        for (bx, bw, bh, tilt) in ((0.03, 0.09, 0.50, 4), (0.13, 0.07, 0.56, -3), (0.80, 0.08, 0.54, 3), (0.90, 0.08, 0.47, -5)):
            x0 = ox + PW * bx
            pts = [(x0 + tilt, fy - PH * bh), (x0 + PW * bw + tilt, fy - PH * bh), (x0 + PW * bw, fy), (x0, fy)]
            d.polygon([(s(x), s(y)) for x, y in pts], fill="#ebe5d6", outline=PALE)
            line([(x0 + PW * bw * 0.2 + tilt * 0.8, fy - PH * bh * 0.8), (x0 + PW * bw * 0.8 + tilt * 0.8, fy - PH * bh * 0.8)], PALE, 3)
    # two flat giant books as the ledges (cover on top, page edges facing us)
    for (x0, x1) in ((ox, lx), (rx, ox + PW)):
        rect(x0, fy, x1, oy + PH, fill="#e7e0cf", outline=None)
        for k in range(1, 9):
            yy = fy + 10 + k * (oy + PH - fy - 10) / 9
            line([(x0, yy), (x1, yy)], "#c9c1ae", 1.2)
        rect(x0, fy, x1, fy + 9, fill=INK, outline=None)   # the cover
    line([(lx, fy), (lx, oy + PH)], INK, 3)
    line([(rx, fy), (rx, oy + PH)], INK, 3)
    # the gap: dark hatching, falling away
    for k in range(9):
        xx = lx + 6 + k * (rx - lx - 12) / 8
        line([(xx, fy + 30 + (k % 3) * 12), (xx, oy + PH)], "#9c9585", 1.5)
    # the bridge: a giant pencil, eraser end leading, sliding out of the far book
    span = rx - lx
    tip = rx - bridge * (span + 4)                        # where the eraser end is
    by0, by1 = fy - 4, fy + 9
    if glow and bridge > 0.05:
        rect(tip - 6, by0 - 7, rx + 14, by1 + 7, fill=glow, outline=None)
    rect(tip + 14, by0, rx + 14, by1, fill="#f7f1df", outline=INK, w=2)       # barrel (runs into the far book)
    line([(tip + 20, (by0 + by1) / 2), (rx + 10, (by0 + by1) / 2)], GREY, 1.2)
    rect(tip + 8, by0, tip + 18, by1, fill="#bdb7aa", outline=INK, w=2)       # ferrule
    d.rounded_rectangle([s(tip - 6), s(by0), s(tip + 9), s(by1)], radius=s(5), fill="#efe9da", outline=INK, width=s(2))  # eraser
    # buttons
    nb, fb = lx - PW * 0.135, rx + PW * 0.135
    for (bx, col) in ((nb, near), (fb, far)):
        rect(bx - 38, fy - 6, bx + 38, fy, fill="#bdb7aa", outline=INK, w=2)          # base
        if col:                                                                      # pressed: flush, lit, rays
            rect(bx - 31, fy - 11, bx + 31, fy - 5, fill=col, outline=INK, w=2)
            for dx in (-52, -44, 44, 52):
                line([(bx + dx, fy - 4), (bx + dx * 1.25, fy - 20)], col, 3)
        else:                                                                        # up
            rect(bx - 31, fy - 22, bx + 31, fy - 5, fill="#f7f1df", outline=INK, w=2)
    return dict(fy=fy, lx=lx, rx=rx, nb=nb, fb=fb)


def panel(i, head, cap, draw):
    c, r = i % COLS, i // COLS
    ox = M + c * (PW + M)
    oy = TITLE_H + r * ROW_H + HEAD_H
    rect(ox, oy, ox + PW, oy + PH, fill=PAPER, outline=None)
    draw(ox, oy)
    # mask anything that spilled outside the panel
    rect(ox - M, oy - HEAD_H, ox + PW + M, oy - 1, fill="#22201d", outline=None)
    rect(ox - M, oy + PH, ox + PW + M, oy + PH + CAP_H + M - 1, fill="#22201d", outline=None)
    rect(ox - M, oy, ox - 1, oy + PH, fill="#22201d", outline=None)
    rect(ox + PW + 1, oy, ox + PW + M, oy + PH, fill="#22201d", outline=None)
    d.rectangle([s(ox), s(oy), s(ox + PW), s(oy + PH)], outline="#000000", width=s(2))
    text(ox + 2, oy - 27, head, f_head, "#ffd978")
    for k, ln in enumerate(cap):
        text(ox + 2, oy + PH + 6 + k * 19, ln, f_cap, "#eee9dc")


def note(x, y, t, fill=INK, anchor="la", font=f_lab, back=False):
    if back:
        bb = d.textbbox((s(x), s(y)), t, font=font, anchor=anchor)
        d.rectangle([bb[0] - s(4), bb[1] - s(3), bb[2] + s(4), bb[3] + s(3)], fill=PAPER)
    text(x, y, t, font, fill, anchor)


# ------------------------------------------------------------------ panels
def p1(ox, oy):                                          # E6c, exists in v3
    fy = oy + PH * 0.74
    rect(ox, fy, ox + PW, oy + PH, fill="#e7e0cf", outline=None)
    line([(ox, fy), (ox + PW, fy)], INK, 4)
    for (bx, bw, bh, tilt) in ((0.02, 0.10, 0.60, 6), (0.88, 0.10, 0.60, -6)):
        x0 = ox + PW * bx
        pts = [(x0 + tilt, fy - PH * bh), (x0 + PW * bw + tilt, fy - PH * bh), (x0 + PW * bw, fy), (x0, fy)]
        d.polygon([(s(x), s(y)) for x, y in pts], fill="#ebe5d6", outline=PALE)
    cx = ox + PW / 2
    for k, dx in enumerate((-46, -14, 20, 50)):
        agent(cx + dx, fy - (6 if k % 2 else 0), "down", 1 if k % 2 else -1, h=92)
    note(cx, fy - 78, "agents, in a heap", GREY, "ma", f_lab_s)
    trail(cx - 30, fy - 52, ox + PW * 0.20, fy - 52, "O")
    trail(cx + 30, fy - 52, ox + PW * 0.80, fy - 52, "B")
    jade(ox + PW * 0.17, fy, "run", "O", -1)
    jade(ox + PW * 0.83, fy, "run", "B", 1)
    arrow(ox + PW * 0.11, fy - 118, ox + PW * 0.04, fy - 118, ORANGE)
    arrow(ox + PW * 0.89, fy - 118, ox + PW * 0.96, fy - 118, BLUE)
    note(ox + 10, oy + 8, "EXISTS (v3 take B_two), moved 3.5 s earlier", GREY)


def p2(ox, oy):
    g = room(ox, oy)
    fy = g["fy"]
    trail(ox + 2, fy - 52, ox + PW * 0.05, fy - 52, "B")
    trail(ox + PW * 0.10, fy - 44, ox + PW * 0.185, fy - 44, "O")
    jade(ox + PW * 0.085, fy, "run", "B")
    jade(ox + PW * 0.215, fy, "run", "O")
    arrow(ox + PW * 0.27, fy - 70, ox + PW * 0.35, fy - 70, INK)
    note((g["lx"] + g["rx"]) / 2, fy + 40, "GAP", INK, "ma", f_head, True)
    note((g["lx"] + g["rx"]) / 2, fy + 68, "too wide to jump", INK, "ma", f_lab_s, True)
    note(g["nb"], fy + 20, "button", GREY, "ma", f_lab_s)
    note(g["fb"], fy + 20, "button", GREY, "ma", f_lab_s)
    note(g["rx"] - 6, fy - 44, "bridge (a giant pencil), parked", GREY, "ma", f_lab_s)
    arrow(g["rx"] - 6, fy - 24, g["rx"] - 2, fy - 8, GREY, 2, 7)
    note(ox + 10, oy + 8, "street of giant books (the E5/E6 tabletop)", GREY)


def p3(ox, oy):
    g = room(ox, oy, bridge=0.62, glow=ORANGE, near=ORANGE)
    fy = g["fy"]
    jade(g["nb"], fy - 10, "crouch", "O")
    jade(ox + PW * 0.07, fy, "stand", "B")
    arrow(g["rx"] - 14, fy - 30, g["lx"] + 46, fy - 30, ORANGE, 5, 14)
    note((g["lx"] + g["rx"]) / 2 + 20, fy - 54, "bridge slides out", ORANGE, "ma")
    note(g["nb"], fy + 20, "HELD DOWN", ORANGE, "ma")


def p4(ox, oy):
    g = room(ox, oy, bridge=1.0, glow=ORANGE, near=ORANGE)
    fy = g["fy"]
    jade(g["nb"], fy - 10, "crouch", "O")
    trail(g["lx"] - 10, fy - 56, (g["lx"] + g["rx"]) / 2 - 24, fy - 56, "B")
    jade((g["lx"] + g["rx"]) / 2 + 4, fy - 5, "run", "B")
    arrow((g["lx"] + g["rx"]) / 2 + 46, fy - 60, g["rx"] + 30, fy - 60, BLUE, 5, 14)
    note(g["nb"] - 10, fy + 20, "must not move", ORANGE, "ma")


def p5(ox, oy):
    g = room(ox, oy, bridge=1.0, glow=ORANGE, near=ORANGE)
    fy = g["fy"]
    agent(ox + PW * 0.0, fy, "run")
    agent(ox + PW * 0.085, fy, "run")
    jade(g["nb"], fy - 10, "crouch", "O", tag=True)
    jade(g["rx"] - 26, fy - 5, "run", "B")
    note(ox + 10, oy + 8, "AGENTS", INK, "la", f_head)
    note(ox + 10, oy + 32, "closing on her from behind", GREY, "la", f_lab_s)
    note((g["lx"] + g["rx"]) / 2, fy + 40, "if she lets go,", INK, "ma", f_lab_s, True)
    note((g["lx"] + g["rx"]) / 2, fy + 60, "her double falls", INK, "ma", f_lab_s, True)


def p6(ox, oy):
    g = room(ox, oy, bridge=1.0, glow=BLUE, near=ORANGE, far=BLUE)
    fy = g["fy"]
    agent(ox + PW * 0.02, fy, "run")
    agent(ox + PW * 0.125, fy, "grab")
    jade(g["nb"], fy - 10, "crouch", "O")
    jade(g["fb"], fy - 10, "crouch", "B", -1)
    note(g["fb"], fy + 20, "HELD DOWN", BLUE, "ma")
    note((g["lx"] + g["rx"]) / 2, fy - 40, "bridge turns blue", BLUE, "ma")
    note(ox + PW - 10, oy + 8, "CUT (closer)", GREY, "ra")


def p7(ox, oy):
    g = room(ox, oy, bridge=1.0, glow=BLUE, far=BLUE)
    fy = g["fy"]
    agent(ox + PW * 0.06, fy, "run")
    agent(g["nb"] - 4, fy - 20, "grab")
    note(g["nb"] + 44, fy - 172, "grabs air", GREY, "ma", f_lab_s)
    trail(g["lx"] - 6, fy - 56, (g["lx"] + g["rx"]) / 2 - 30, fy - 56, "O")
    jade((g["lx"] + g["rx"]) / 2 - 2, fy - 5, "run", "O")
    arrow((g["lx"] + g["rx"]) / 2 + 40, fy - 60, g["rx"] + 4, fy - 60, ORANGE, 5, 14)
    jade(g["fb"], fy - 10, "crouch", "B", -1)


def p8(ox, oy):
    g = room(ox, oy, bridge=0.18, glow=None)
    fy = g["fy"]
    agent(g["lx"] - 16, fy, "teeter")
    agent(g["nb"] - 10, fy - 20, "stomp")
    agent(ox + PW * 0.03, fy, "run")
    note(ox + PW * 0.185, fy + 18, "dead: it only answers to her colour", INK, "ma", f_lab_s)
    arrow(g["lx"] + 40, fy - 30, g["rx"] - 40, fy - 30, INK, 5, 14)
    note((g["lx"] + g["rx"]) / 2, fy - 54, "bridge snaps back", INK, "ma")
    jade(g["rx"] + 34, fy, "stand", "O", -1)
    jade(g["fb"] + 20, fy - 22, "air", "B", 1)
    note(g["lx"] + 4, fy - 166, "stops at the lip", GREY, "ma", f_lab_s)
    note(ox + PW - 10, oy + 8, "nobody falls", GREY, "ra")


def p9(ox, oy):
    g = room(ox, oy, bridge=0.0)
    fy = g["fy"]
    agent(g["lx"] - 22, fy, "teeter", 1)
    agent(g["nb"] - 10, fy - 20, "stomp")
    trail(g["rx"] + 10, fy - 52, ox + PW * 0.74, fy - 52, "O")
    trail(g["rx"] + 50, fy - 60, ox + PW * 0.86, fy - 60, "B")
    jade(ox + PW * 0.77, fy, "run", "O")
    jade(ox + PW * 0.90, fy, "run", "B")
    arrow(ox + PW * 0.80, fy - 176, ox + PW * 0.97, fy - 176, INK, 5, 14)
    note(ox + PW * 0.985, fy - 204, "cut to E7 on 134.00: 2, 4, 8, 16", INK, "ra")


PANELS = [
    ("1 · 128.32  ONE BECOMES TWO  (E6c)", ["Banach–Tarski: the motes land as two Jades,", "who sprint apart (orange trail, blue trail)."], p1),
    ("2 · 129.62  THE ROOM  (shot C1)", ["Cut. Both run in from the left. A gap, a bridge", "parked on the far side, a floor button each side."], p2),
    ("3 · 130.50  HOLD", ["Bar line. Orange stamps the near button. It lights", "orange and the bridge slides out in her colour."], p3),
    ("4 · 130.94  CROSS", ["Blue sprints across. Orange has to stay down:", "the bridge is only there while the button is held."], p4),
    ("5 · 131.38  THREAT", ["Agents come in behind Orange. She cannot run", "until her double is over."], p5),
    ("6 · 131.82  SWAP  (shot C2)", ["Cut, closer. Blue lands on the far button.", "The bridge turns blue: now it is held from her side."], p6),
    ("7 · 132.26  GO", ["Bar line. Orange springs off; the agent's grab", "closes on air. She runs the blue bridge."], p7),
    ("8 · 133.12  LET GO", ["Orange is over. Blue hops off, the bridge snaps", "back. One agent teeters; one stamps a dead button."], p8),
    ("9 · 133.56  OUT", ["Both run on, right. Cut on 134.00 to the replay,", "where two become four, eight, sixteen."], p9),
]

def storyboard():
    # title bar
    text(M, 12, "REWIND v4 · 2:00 · the co-op level  (129.62–134.00 s · ten beats · two new shots)", f_title, "#ffffff")
    text(M, 48, "Storyboard, not final art. Side view. Final look: the engraved street of giant books; the two Jades are identical and in full colour.", f_sub, "#cfc9bb")
    lx0 = M
    ly = 70
    d.ellipse([s(lx0), s(ly + 2), s(lx0 + 30), s(ly + 14)], outline=ORANGE, width=s(4))
    text(lx0 + 38, ly - 2, "Orange (1P)", f_sub, ORANGE)
    d.ellipse([s(lx0 + 150), s(ly + 2), s(lx0 + 180), s(ly + 14)], outline=BLUE, width=s(4))
    text(lx0 + 188, ly - 2, "Blue (also 1P: neither is the copy)", f_sub, BLUE)
    rect(lx0 + 470, ly, lx0 + 490, ly + 16, fill=INK, outline="#cfc9bb", w=1)
    text(lx0 + 498, ly - 2, "agents", f_sub, "#cfc9bb")
    text(lx0 + 590, ly - 2, "Bridge: a giant pencil off the desk (an object, not a drawn line).  Times are song seconds on tracked beats.", f_sub, "#cfc9bb")
    for i, (head, cap, fn) in enumerate(PANELS):
        panel(i, head, cap, fn)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.resize((W, H), Image.LANCZOS).save(OUT, quality=90)
    print(OUT, (W, H))


def animatic():
    """panels 2-9, each alone at 1920x1080: the drawing, a top strip with the title and the caption, ANIMATIC label."""
    global img, d
    out = f"{ROOT}/media/shots/C_coop/animatic"
    os.makedirs(out, exist_ok=True)
    f_t, f_c, f_a = F(DJ + "DejaVuSans-Bold.ttf", 13), F(DJ + "DejaVuSans.ttf", 10.5), F(f"{ROOT}/render/fonts/PressStart2P-Regular.ttf", 9)
    for n, (head, cap, fn) in enumerate(PANELS, start=1):
        if n == 1:
            continue                                     # panel 1 is E6c, which exists
        img = Image.new("RGB", (1920, 1080), PAPER)
        d = ImageDraw.Draw(img)
        fn(0, 0)
        rect(0, 37, PW * 0.45, 48, fill=PAPER, outline=None)   # the panel's own top-left note is said by the caption
        rect(0, 0, PW + 2, 37, fill="#22201d", outline=None)
        text(8, 4, head.split("  (")[0], f_t, "#ffd978")
        text(8, 21, " ".join(cap), f_c, "#eee9dc")
        text(PW - 8, 6, "ANIMATIC", f_a, "#ffffff", "ra")
        img.save(f"{out}/p{n}.png")
        print(f"{out}/p{n}.png", img.size)


if __name__ == "__main__":
    animatic() if ANIMATIC else storyboard()
