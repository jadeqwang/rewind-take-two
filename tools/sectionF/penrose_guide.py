"""F6b (v3): the Penrose staircase of tools/sectionF/modules/penrose_march.js as a flat guide drawing on the clock plate,
at the magic angle, for the image model to redraw in the plate's hand. Same geometry and placement as the module
(keep build()/project in step with it). Also writes the step table (tread centres in plate px and design px).

    $PY tools/sectionF/penrose_guide.py            -> media/shots/F6b/kf_v3_F6b_guide.png, kf_v3_F6b_steps.json
"""
import json
import math
import os

from PIL import Image, ImageDraw

ROOT = "/home/jade/Documents/rewind-take-two"
D = os.path.join(ROOT, "media/shots/F6b")
PLATE = os.path.join(D, "kf_v3_F6b_plate_crop_dered.png")       # 2400x1350 = design px * 1.25
PAR = dict(cx=960, cy=468, width=580, n=[7, 2, 2, 7], w=1.6, wall=1.1)   # design px, as in edl.py penrose()
MAGIC = math.atan(1 / math.sqrt(2))
R2 = math.sqrt(2)


def build(n, w):
    nA, nB, nC, nD = n
    hw = w / 2
    m = nA - nC
    N = nA + nB + nC + nD + 4
    h = m / N
    steps = []

    def add(x0, x1, z0, z1, fl):
        steps.append(dict(x0=x0, x1=x1, z0=z0, z1=z1, y=len(steps) * h, flight=fl, i=len(steps)))
    add(-hw, hw, -hw, hw, "R")
    for j in range(nA):
        add(-hw, hw, hw + j, hw + j + 1, "A")
    zB = w + nA
    add(-hw, hw, zB - hw, zB + hw, "B0")
    for j in range(nB):
        add(-hw - j - 1, -hw - j, zB - hw, zB + hw, "B")
    xL = -(w + nB)
    add(xL - hw, xL + hw, zB - hw, zB + hw, "L")
    for j in range(nC):
        add(xL - hw, xL + hw, zB - hw - j - 1, zB - hw - j, "C")
    zT = zB - (w + nC)
    add(xL - hw, xL + hw, zT - hw, zT + hw, "T")
    for j in range(nD):
        add(xL + hw + j, xL + hw + j + 1, zT - hw, zT + hw, "D")
    return steps, N, h


def projector(steps, par, k=1.0):
    """Returns P(x, y, z) -> px (design px * k), centred like the module does."""
    def p0(x, y, z, S=1.0):
        return (S * (x - z) / R2, S * ((x + z) * math.sin(MAGIC) / R2 - y * math.cos(MAGIC)))
    pts = [p0(x, s["y"], z) for s in steps for x, z in ((s["x0"], s["z0"]), (s["x1"], s["z0"]), (s["x1"], s["z1"]), (s["x0"], s["z1"]))]
    bx0, bx1 = min(p[0] for p in pts), max(p[0] for p in pts)
    by0, by1 = min(p[1] for p in pts), max(p[1] for p in pts)
    S = par["width"] / (bx1 - bx0)
    ox, oy = par["cx"] - S * (bx0 + bx1) / 2, par["cy"] - S * (by0 + by1) / 2
    return (lambda x, y, z: ((p0(x, y, z, S)[0] + ox) * k, (p0(x, y, z, S)[1] + oy) * k)), S


def main():
    steps, N, h = build(PAR["n"], PAR["w"])
    im = Image.open(PLATE).convert("RGB")
    k = im.width / 1920
    P, S = projector(steps, PAR, k)
    d = ImageDraw.Draw(im)
    INK, TOP, RIGHT, LEFT = (30, 28, 30), (240, 232, 214), (214, 170, 92), (112, 120, 176)
    wall = PAR["wall"]
    far = [s for s in steps if s["flight"][0] in "CTD"]
    near = [s for s in steps if s["flight"][0] not in "CTD"]
    for grp in (far, near):
        for s in sorted(grp, key=lambda s: s["x0"] + s["x1"] + s["z0"] + s["z1"]):
            yb = s["y"] - wall
            faces = []
            if s["flight"] != "D":
                faces.append(([P(s["x1"], s["y"], s["z0"]), P(s["x1"], s["y"], s["z1"]), P(s["x1"], yb, s["z1"]), P(s["x1"], yb, s["z0"])], RIGHT))
            if s["flight"] not in ("A", "R"):
                faces.append(([P(s["x0"], s["y"], s["z1"]), P(s["x1"], s["y"], s["z1"]), P(s["x1"], yb, s["z1"]), P(s["x0"], yb, s["z1"])], LEFT))
            faces.append(([P(s["x0"], s["y"], s["z0"]), P(s["x1"], s["y"], s["z0"]), P(s["x1"], s["y"], s["z1"]), P(s["x0"], s["y"], s["z1"])], TOP))
            for pts, col in faces:
                d.polygon(pts, fill=col)
                d.line(pts + [pts[0]], fill=INK, width=3, joint="curve")
    im.save(os.path.join(D, "kf_v3_F6b_guide.png"))
    table = []
    for s in steps:
        c = P((s["x0"] + s["x1"]) / 2, s["y"], (s["z0"] + s["z1"]) / 2)
        table.append(dict(i=s["i"], flight=s["flight"], y=round(s["y"], 3), plate=[round(c[0], 1), round(c[1], 1)],
                          design=[round(c[0] / k, 1), round(c[1] / k, 1)]))
    json.dump(dict(par=PAR, N=N, riser=h, px_per_unit_design=S, steps=table), open(os.path.join(D, "kf_v3_F6b_steps.json"), "w"), indent=1)
    print("steps", N, "riser", round(h, 4), "S", round(S, 2), "design px/unit")
    for t in table:
        print(t["i"], t["flight"], t["design"])


if __name__ == "__main__":
    main()
