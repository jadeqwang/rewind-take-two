#!/usr/bin/env python
"""Build section D's engine timeline (render/timeline/D.js) and the EDL mirror (media/shots/D_edl.json).

Section D = drop 2 + "Anomaly detected", 112.96-141.00, minus E3 (119.44-122.95, the singing shot owned by another
director). All ghost choreography lives in the tables below (GHOSTS_E2, E4_GHOSTS, ...): which clip, freeze/offset,
hue, opacity, position. Ghost positions are measured from the mattes (tools/sections/D/mtrack.py) so a ghost freezes
exactly where she was.

    tools/engrave/.venv/bin/python tools/sections/D/build_timeline.py
"""
import glob
import json
import math
import os
import sys

import cv2
import numpy as np

ROOT = "/home/jade/Documents/rewind-take-two"
os.chdir(ROOT)
FPS = 24
SH = "media/shots"

# 13 ghost hues: the Kandinsky spectrum (orange, blue, gold, magenta, green) then its in-betweens
HUE = ["#F08A24", "#3E6FD8", "#C9A227", "#C23B8E", "#3FA55B", "#E4572E", "#8DB8E8", "#E8D04A", "#8E5CC8", "#2BA59A",
       "#F28DB2", "#4B4FC4", "#9CCB3B"]
RES = ["#F08A24", "#8DB8E8"]            # residue gradient (orange band -> pale-blue dot)
INK, PAPER = "#0b0b0c", "#ece7dc"

# vocal chops (timing.json lyrics.vocal_chops, drop 2): hit k = ghost k
CHOPS = [113.89, 114.35, 114.78, 115.24, 115.67, 116.03, 116.52, 116.95, 117.39, 117.83, 118.25, 118.71, 119.15]
BEATS_E7 = [134.00, 134.44, 134.88, 135.32, 135.76, 136.19, 136.62, 137.06, 137.50, 137.94, 138.38, 138.82, 139.00]


# ------------------------------------------------------------------ media helpers
def clip(shot, name):
    """engraved take, matte dirs for a published take name like 'trk_sprint_1'."""
    stem = f"{SH}/{shot}/take_{name}"
    return dict(eng=stem + "_engraved.mp4", matte=stem + "_matte/matte.mp4", jmatte=stem + "_jmatte/matte.mp4",
                twin=stem + "_twin/matte.mp4", stem=stem)


def mstats(stem, t, suffix="_matte", box=None, exclude=None):
    """centroid / bbox in design px (centre origin, 1920x1080 cover) of the matte at source time t."""
    fs = sorted(glob.glob(f"{stem}{suffix}/*.png"))
    i = min(len(fs) - 1, max(0, round(t * FPS)))
    m = cv2.imread(fs[i], cv2.IMREAD_GRAYSCALE)
    h, w = m.shape
    b = m >= 128
    if box:
        k = np.zeros_like(b); k[int(box[1] * h):int(box[3] * h), int(box[0] * w):int(box[2] * w)] = True; b &= k
    if exclude:
        k = np.zeros_like(b); k[int(exclude[1] * h):int(exclude[3] * h), int(exclude[0] * w):int(exclude[2] * w)] = True; b &= ~k
    ys, xs = np.nonzero(b)
    if len(xs) < 50:
        return None
    sx, sy = 1920 / w, 1080 / h
    return dict(cx=xs.mean() * sx - 960, cy=ys.mean() * sy - 540, x0=xs.min() * sx - 960, x1=xs.max() * sx - 960,
                y0=ys.min() * sy - 540, y1=ys.max() * sy - 540, top=np.percentile(ys, 8) * sy - 540)


def path_of(stem, src_times, layer_times, suffix="_matte", point="mid", **kw):
    out = []
    for st, lt in zip(src_times, layer_times):
        s = mstats(stem, st, suffix, **kw)
        if s is None:
            continue
        y = s["cy"] if point == "centroid" else 0.5 * (s["cy"] + s["top"])
        out.append([round(lt, 4), round(s["cx"], 1), round(y, 1)])
    return out


def seg_path(stem, src_in, rate, lt0, lt1, suffix="_matte", step=1 / 12, **kw):
    n = max(2, int(round((lt1 - lt0) / step)) + 1)
    lts = [lt0 + (lt1 - lt0) * k / (n - 1) for k in range(n)]
    return path_of(stem, [src_in + rate * (lt - lt0) for lt in lts], lts, suffix, **kw)


def r4(x):
    return round(x, 4)


# ------------------------------------------------------------------ layer builders
def live(id_, c, src_in, rate, start, end, snap=0.0, matte="matte", **kw):
    """Jade's current attempt, matted (keepColor). snap > 0: the clip first scrubs back `snap` s of source in 3 frames
    (the visible ◀◀ of each rewind) before playing forward."""
    L = dict(id=id_, type="video", src=c["eng"], matte=dict(src=c[matte], mode="luma"), keepColor=True, start=r4(start),
             end=r4(end))
    d = end - start
    if snap:
        L["srcTime"] = [[0, r4(src_in + snap)], [0.125, r4(src_in), "outCubic"], [r4(d), r4(src_in + rate * (d - 0.125))]]
    else:
        L["in"] = r4(src_in); L["rate"] = rate
    L.update(kw)
    return L


def plate(id_, c, src_in, rate, start, end, snap=0.0, **kw):
    L = dict(id=id_, type="video", src=c["eng"], start=r4(start), end=r4(end))
    d = end - start
    if snap:
        L["srcTime"] = [[0, r4(src_in + snap)], [0.125, r4(src_in), "outCubic"], [r4(d), r4(src_in + rate * (d - 0.125))]]
    else:
        L["in"] = r4(src_in); L["rate"] = rate
    L.update(kw)
    return L


GHOST = dict(blend=os.environ.get("D_GHOST_BLEND", "normal"), op=float(os.environ.get("D_GHOST_OP", "1.0")),
             tint=float(os.environ.get("D_GHOST_TINT", "0")))


def ghost(id_, c, freeze, color, hit_abs, matte="matte", x=0, y=0, scale=1.0, opacity=0.62, tint=0.82, flip=False):
    """One frozen iteration: the matted frame at source time `freeze`, colourised, revealed on the chop `hit_abs`."""
    inst = dict(freeze=r4(freeze), color=color, opacity=r4(min(1.0, opacity * GHOST["op"])), tint=GHOST["tint"] or tint)
    if GHOST["blend"] != "normal":
        inst["blend"] = GHOST["blend"]
    if flip:
        inst["flip"] = True
    return dict(id=id_, type="ghosts", src=c["eng"], matte=dict(src=c[matte], mode="luma"), keepColor=True, loop=False,
                x=r4(x), y=r4(y), scale=r4(scale), on=[hit_abs], instances=[inst])


def ribbon(id_, path, colors=RES, width=24, **kw):
    p = dict(path=path, colors=colors, width=width, twist=0.5, bloom=0.8, grain=0.5, motes=0.25)
    p.update(kw)
    return dict(id=id_, type="canvas", module="ribbon", keepColor=True, params=p)


def chop_fx(hits_local, extra=()):
    """per-chop rewind punctuation: a pale-blue flash, a VHS-rewind blip and a zoom punch."""
    rw = [[0, 0]]
    for h in hits_local:
        rw += [[r4(max(0, h - 0.001)), 0], [r4(h), 0.85], [r4(h + 0.12), 0]]
    fx = [dict(type="flash", at=[r4(h) for h in hits_local], dur=0.08, amount=0.35, color="#8DB8E8"),
          dict(type="rewind", amount=rw),
          dict(type="punch", on="vocal_chops", amount=0.035, decay=0.12)]
    return fx + list(extra)


# ------------------------------------------------------------------ the shots
def build():
    shots, overlays, notes = [], [], {}
    take = json.load(open(f"{SH}/_D/takes.json"))     # chosen take numbers (written by hand after review)
    C = {k: clip(v["shot"], f"{k}_{v['take']}") for k, v in take.items() if isinstance(v, dict) and "shot" in v}

    # ---------------- E1 + E2a: the L tracks (impact, ghosts 1-3) ----------------
    t0, t1 = 112.96, CHOPS[2] + 0.125
    h = [c - t0 for c in CHOPS[:3]]                       # local hit times 0.93, 1.39, 1.82
    sp, da, wj = C["trk_sprint"], C["trk_dash"], C["trk_walljump"]
    WJ = take["trk_walljump"]                             # {in, rate, freeze}
    # (clip, freeze = her pose on the chop, rate, start, end, snap). Each attempt ends on its chop: the source in-point
    # is solved backwards from the freeze so the pose at the chop is exactly the ghost's pose.
    seg = [(sp, 2.75, 1.0, 0.0, h[0], 0.0),
           (da, 1.96, 1.65, h[0], h[1], 0.25),
           (wj, WJ["freeze"], WJ["rate"], h[1], h[2], 0.25)]
    layers = [dict(id="plate", type="image", src=f"{SH}/E2/plate_trk.png")]
    ghosts, ribs = [], []
    for k, (c, frz, rate, a, b, snap) in enumerate(seg):
        play = (b - a) - (0.125 if snap else 0.0)          # forward playback after the 3-frame ◀◀ scrub
        si = frz - rate * play
        layers.append(live(f"live{k + 1}", c, si, rate, a, b, snap=snap))
        pth = seg_path(c["stem"], si, rate, a + (0.125 if snap else 0.0), b)
        ribs.append(ribbon(f"res{k + 1}", pth, colors=[HUE[k], RES[1]], width=26))
        ghosts.append(ghost(f"g{k + 1}", c, frz, HUE[k], CHOPS[k]))
        notes[f"g{k + 1}"] = dict(clip=c["eng"], freeze=frz, hue=HUE[k], where="L tracks (as frozen)", hit=CHOPS[k])
    s1 = mstats(sp["stem"], 2.75 - h[0])
    layers += ribs + ghosts
    # E1 impact: the frame fills with residue colour, then clears; a mote burst from her as she bursts off the mark
    layers += [
        dict(id="flood", type="solid", keepColor=True, end=0.93, color=RES[0], opacity=[[0, 1.0], [0.07, 1.0], [0.6, 0.0, "outCubic"]]),
        dict(id="flood2", type="solid", keepColor=True, end=0.93, color=RES[1], blend="multiply",
             opacity=[[0, 0.0], [0.1, 0.0], [0.22, 0.55], [0.8, 0.0]]),
        dict(id="burst", type="canvas", module="motes", keepColor=True, end=1.6,
             params=dict(at=0.0, x=r4(s1["cx"] + 960), y=r4(s1["cy"] + 540), count=260, colors=HUE[:5] + RES, speed=3400,
                         drag=2.4, size=34, life=1.1, ring=True, glow=1.0, seed=65)),
    ]
    shots.append(dict(id="E1_E2a_tracks", start=t0, end=r4(t1), layers=layers,
                      fx=[dict(type="flash", at=[0], dur=0.06, amount=1.0, color="#ffffff"),
                          dict(type="shake", at=[0], amp=14, decay=0.3)] + chop_fx(h)))

    # ---------------- E2b: Grant Park, ground level (ghosts 4-7; each chop a hard cut) ----------------
    t0, t1 = t1, CHOPS[7]
    FLD = [  # (clip key, freeze source time = pose at the chop, rate) ; each segment ends on its chop
        ("fld_slide", 3.15, 1.0), ("fld_cartwheel", 1.83, 1.0), ("fld_vault", 3.00, 1.0), ("fld_spin", 2.30, 1.0),
        ("fld_spin", 0.95, 1.0)]
    ends = CHOPS[3:8]
    layers, ghosts, ribs = [], [], []
    a = 0.0
    for k, (key, fz, rate) in enumerate(FLD):
        c = C[key]
        b = ends[k] - t0
        si = fz - rate * (b - a)
        layers.append(plate(f"field{k + 1}", c, si, rate, a, b))
        ribs.append(ribbon(f"res{k + 4}", seg_path(c["stem"], si, rate, a, b, suffix="_jmatte"),
                           colors=[HUE[3 + k], RES[1]], width=24, end=r4(t1 - t0)))
        if k < 4:   # the 5th (spin @0.95 = ghost 8) is born on the cut to the ring shot
            ghosts.append(ghost(f"g{k + 4}", c, fz, HUE[3 + k], CHOPS[3 + k], matte="jmatte"))
        notes[f"g{k + 4}"] = dict(clip=c["eng"], freeze=fz, hue=HUE[3 + k], where="Grant Park ground level", hit=CHOPS[3 + k])
        a = b
    layers += ribs + ghosts
    shots.append(dict(id="E2b_field", start=r4(t0), end=t1, layers=layers,
                      fx=[dict(type="flash", at=[0], dur=0.06, amount=0.5, color="#ffffff")] +
                      chop_fx([c - t0 for c in CHOPS[3:7]])))

    # ---------------- E2c: high wide over the ring of agents (ghosts 8-13, the constellation) ----------------
    t0, t1 = CHOPS[7], 119.44
    R = take["ring_circle"]          # {take, in, rate, freezes: [5 source times], placed: [[clip, freeze, matte, x, y, h, flip] x8]}
    if R.get("freezes"):
        rc = C["ring_circle"]
        layers = [dict(id="ring", type="video", src=rc["eng"], matte=dict(src=rc["jmatte"], mode="luma"), keepColor=True,
                       srcTime=R["srcTime"])]
        # earlier iterations pasted into the wide: 1-3 small on the elevated tracks, 4-8 on the lawn around the agents
        placed = []
        for gi, (key, fz, matte, tx, ty, th, flip) in enumerate(R["placed"]):
            c = C[key]
            s = mstats(c["stem"], fz, "_" + matte)
            sc = th if th < 3 else th / max(1.0, s["y1"] - s["y0"])   # th < 3: a scale, else a target bbox height (px)
            cx = -s["cx"] if flip else s["cx"]          # matte centroid lands on (tx, ty)
            g = ghost(f"g{gi + 1}", c, fz, HUE[gi], CHOPS[7], matte=matte, x=tx - sc * cx, y=ty - sc * s["cy"], scale=sc,
                      opacity=0.7 if gi < 3 else 0.62, flip=flip)
            if gi != 7:            # 1-7 are already standing there; 8 pops on the cut (its own chop)
                g.pop("on")
            placed.append(g)
            notes.setdefault(f"g{gi + 1}", {})["ring_pos"] = dict(x=tx, y=ty, height_px=th, scale=round(sc, 3), flip=flip)
        new = []
        for j, k in enumerate(range(8, 13)):
            fz = R["freezes"][j]
            new.append(ghost(f"g{k + 1}", rc, fz, HUE[k], CHOPS[k], matte="jmatte", opacity=0.7, tint=0.85))
            notes[f"g{k + 1}"] = dict(clip=rc["eng"], freeze=fz, hue=HUE[k], where="ring wide (where she was)", hit=CHOPS[k])
        lts = [k / 12 for k in range(int((t1 - t0) * 12) + 1)]
        rp = path_of(rc["stem"], [float(np.interp(x, [k[0] for k in R["srcTime"]], [k[1] for k in R["srcTime"]])) for x in lts],
                     lts, "_jmatte")
        layers += [ribbon("res_ring", rp, colors=[HUE[8], HUE[12]], width=16)] + placed + new
        shots.append(dict(id="E2c_ring", start=t0, end=t1, layers=layers,
                          fx=[dict(type="flash", at=[0], dur=0.06, amount=0.5, color="#ffffff")] +
                          chop_fx([c - t0 for c in CHOPS[8:]], extra=[dict(type="zoom", amount=[[0, 1.0], [2.49, 1.06]])])))

    # ghost counter over E2 (Press Start 2P, top right, ink on paper): one more per chop, odometer roll
    keys = [[0, 0, "hold"]]
    for k, c in enumerate(CHOPS):
        keys += [[r4(c - 113.89 - 0.07), k, "linear"], [r4(c - 113.89), k + 1, "hold"]]
    overlays.append(dict(id="D_ghost_counter", start=113.89, end=119.44, layers=[
        dict(type="solid", stage="post", color=PAPER, opacity=0.88, rect=[1580, 40, 312, 56]), dict(
        type="canvas", module="hud", stage="post", params=dict(mode="iteration", label="GHOSTS", value=keys[1:] if keys[1][0] <= 0 else keys,
                                                               snap=True, side="right", color=INK, size=26))]))

    # ---------------- E4: "Rewind." #2, the Super Meat Boy replay ----------------
    t0, t1 = 122.95, 126.25
    E4 = take["e4_stream"]
    c = C["e4_stream"]
    inst = []
    for k, off in enumerate([-0.33, 0.33, -0.67, 0.67, -1.0, 1.0]):   # earlier/later attempts on the same route
        inst.append(dict(offset=r4(round(off * FPS) / FPS), x=0, y=r4((-1) ** k * 30),
                         color=HUE[(k + 1) % 13], opacity=0.72, tint=0.8))
    notes["E4"] = dict(clip=c["eng"], in_=E4["in"], rate=E4["rate"], ghosts=inst)
    layers = [dict(id="jade", type="video", src=c["eng"], matte=dict(src=c["jmatte"], mode="luma"), keepColor=True,
                   **{"in": E4["in"], "rate": E4["rate"]}),
              dict(id="swarm", type="ghosts", src=c["eng"], matte=dict(src=c["jmatte"], mode="luma"), keepColor=True, loop=False,
                   **{"in": E4["in"], "rate": E4["rate"]}, instances=inst,
                   show=[[0, 0], [0.05, 0], [0.6, 6, "outCubic"]]),
              ribbon("res", None, follow=dict(layer="jade", point="centroid", smooth=3), colors=RES, width=30, trail=1.6),
              dict(type="canvas", module="lowerthird", stage="post", params=dict(color="#F08A24", size=140, y=965, halo=0.9))]
    layers[2]["params"].pop("path")      # follow instead of a keyed path
    shots.append(dict(id="E4_replay", start=t0, end=t1, layers=layers,
                      fx=[dict(type="flash", at=["word:rewind#2"], dur=0.12, amount=0.6, color="#ffffff"),
                          dict(type="punch", on="beat", amount=0.025), dict(type="shake", on="downbeat", amp=8, decay=0.15)]))

    # ---------------- E5: co-op boost, the slip of paper ----------------
    B = take["e5_boost"]; c = C["e5_boost"]
    t0, t1 = 126.25, 127.88
    jp = seg_path(c["stem"], B["in"], B["rate"], 0, t1 - t0, exclude=[0, 0.33, 0.345, 1.0])
    layers = [dict(id="jade", type="video", src=c["eng"], matte=dict(src=c["matte"], mode="luma"), keepColor=True,
                   **{"in": B["in"], "rate": B["rate"]}),
              dict(id="twin", type="ghosts", src=c["eng"], matte=dict(src=c["twin"], mode="luma"), keepColor=True, loop=False,
                   **{"in": B["in"], "rate": B["rate"]}, instances=[dict(offset=0, color=HUE[1], tint=0.85, opacity=0.9)]),
              ribbon("res", jp, colors=RES, width=26)]
    notes["E5a"] = dict(clip=c["eng"], twin_matte=c["twin"], hue=HUE[1])
    shots.append(dict(id="E5a_boost", start=t0, end=t1, layers=layers, fx=[dict(type="punch", on="beat", amount=0.02)]))

    Hd = take["e5_hand"]; c = C["e5_hand"]
    t0, t1 = 127.88, 128.76
    shots.append(dict(id="E5b_handoff", start=t0, end=t1, layers=[
        dict(id="jade", type="video", src=c["eng"], matte=dict(src=c["matte"], mode="luma"), keepColor=True, **{"in": Hd["in"], "rate": Hd["rate"]}),
        dict(id="twin", type="ghosts", src=c["eng"], matte=dict(src=c["twin"], mode="luma"), keepColor=True, loop=False,
             **{"in": Hd["in"], "rate": Hd["rate"]}, instances=[dict(offset=0, color=HUE[2], tint=0.85, opacity=0.9)])]))
    notes["E5b"] = dict(clip=c["eng"], twin_matte=c["twin"], hue=HUE[2])

    Sl = take["e5_slip"]; c = C["e5_slip"]
    t0, t1 = 128.76, 130.50
    shots.append(dict(id="E5c_slip", start=t0, end=t1, layers=[
        dict(id="jade", type="video", src=c["eng"], matte=dict(src=c["matte"], mode="luma"), keepColor=True, **{"in": Sl["in"], "rate": Sl["rate"]}),
        dict(type="canvas", module="pencil", keepColor=True, params=dict(
            text="What's an anagram of\nBanach–Tarski?", at=-3, cps=40, size=64, color="#3c3a37",
            corners=Sl["corners"], point=False))]))

    # ---------------- E6: Banach-Tarski ----------------
    S1 = take["e6_single"]; c = C["e6_single"]
    t0, t1 = 130.50, 131.38
    burst = 130.94 - t0
    s = mstats(c["stem"], S1["in"] + burst)
    shots.append(dict(id="E6a_atomize", start=t0, end=t1, layers=[
        dict(id="jade", type="video", src=c["eng"], matte=dict(src=c["matte"], mode="luma"), keepColor=True,
             **{"in": S1["in"], "rate": 1.0}, freeze=r4(burst)),
        dict(id="clean", type="image", src=f"{SH}/E6/plate_e6_clean_eng.png", start=r4(burst), opacity=[[0, 0], [0.16, 1, "inCubic"]]),
        dict(id="motes", type="canvas", module="motes", keepColor=True, params=dict(
            at=r4(burst), x=r4(s["cx"] + 960), y=r4(s["cy"] + 540), count=150, colors=RES + ["#ffffff", "#1f2a44", "#F08A24"],
            speed=700, drag=1.6, gravity=-20, size=12, life=2.0, ring=False, glow=0.9, seed=31))],
        fx=[dict(type="flash", at=[r4(burst)], dur=0.1, amount=0.6, color="#ffffff")]))
    SP = take["e6_split"]; c = C["e6_split"]
    t0, t1 = 131.38, 134.00
    sl = mstats(c["stem"], SP["in"], box=[0, 0, 0.5, 1]); sr = mstats(c["stem"], SP["in"], box=[0.5, 0, 1, 1])
    lp = seg_path(c["stem"], SP["in"], 1.0, 0.3, t1 - t0, box=[0, 0, 0.5, 1])
    rp = seg_path(c["stem"], SP["in"], 1.0, 0.3, t1 - t0, box=[0.5, 0, 1, 1])
    shots.append(dict(id="E6b_split", start=t0, end=t1, layers=[
        dict(id="jade", type="video", src=c["eng"], matte=dict(src=c["matte"], mode="luma"), keepColor=True, **{"in": SP["in"], "rate": 1.0}),
        dict(type="canvas", module="motes", keepColor=True, end=0.42, time=[[0, 0.42], [0.42, 0.0]],
             params=dict(at=0, x=r4(sl["cx"] + 960), y=r4(sl["cy"] + 540), count=80, colors=RES + ["#ffffff"], speed=700, drag=1.6,
                         size=12, life=2.0, ring=False, glow=0.9, seed=32)),
        dict(type="canvas", module="motes", keepColor=True, end=0.42, time=[[0, 0.42], [0.42, 0.0]],
             params=dict(at=0, x=r4(sr["cx"] + 960), y=r4(sr["cy"] + 540), count=80, colors=RES + ["#ffffff"], speed=700, drag=1.6,
                         size=12, life=2.0, ring=False, glow=0.9, seed=33)),
        ribbon("resL", lp, colors=[HUE[0], RES[1]], width=24), ribbon("resR", rp, colors=[HUE[1], RES[0]], width=24)],
        fx=[dict(type="punch", on="beat", amount=0.025)]))

    # ---------------- E7: colour everywhere, a cut on every beat ----------------
    E7 = take["e7_cuts"]
    for k, cut in enumerate(E7):
        a, b = BEATS_E7[k], BEATS_E7[k + 1]
        c = C[cut["clip"]]
        L = [dict(id="jade", type="video", src=c["eng"], keepColor=True, **{"in": cut["in"], "rate": cut.get("rate", 1.0)},
                  **({"matte": dict(src=c[cut.get("matte", "matte")], mode="luma")} if cut.get("jade") else {}),
                  **({"scale": cut["scale"]} if "scale" in cut else {}))]
        if cut.get("ghosts"):
            n, spread, sc = cut["ghosts"], cut.get("spread", 380), cut.get("gscale", 0.85)
            inst = [dict(offset=r4(-round((0.08 + 0.07 * j) * FPS) / FPS), x=r4(spread * math.sin(j * 2.1 + k)),
                         y=r4(cut.get("gy", -30) + 30 * math.cos(j * 1.3)), scale=r4(sc + 0.08 * math.sin(j * 1.7)),
                         color=HUE[(j + k) % 13], opacity=0.55, tint=0.8) for j in range(n)]
            # drawn over the plate but under her live layer (a copy of the plate goes underneath)
            L.insert(0, dict(id="bg", type="video", src=c["eng"], **{"in": cut["in"], "rate": cut.get("rate", 1.0)},
                             **({"scale": cut["scale"]} if "scale" in cut else {})))
            L.insert(1, dict(id="ghosts", type="ghosts", src=c["eng"], keepColor=True, loop=False,
                             matte=dict(src=c[cut.get("matte", "matte")], mode="luma"),
                             **{"in": cut["in"], "rate": cut.get("rate", 1.0)}, instances=inst,
                             **({"scale": cut["scale"]} if "scale" in cut else {})))
            L[2]["matte"] = dict(src=c[cut.get("matte", "matte")], mode="luma")
        fx = [dict(type="flash", at=[0], dur=0.05, amount=min(0.35, 0.2 + 0.02 * k), color="#ffffff"), dict(type="punch", at=[0], amount=0.04)]
        if cut["clip"] == "e7_meter":
            fx.append(dict(type="shake", at=[0], amp=6 + 3 * k, decay=0.3))
        if k == len(E7) - 1:
            fx.append(dict(type="flash", at=[r4(b - a - 0.06)], dur=0.06, amount=1.0, color="#ffffff"))
        shots.append(dict(id=f"E7_{k + 1:02d}_{cut['clip']}", start=a, end=b, layers=L, fx=fx))
    # residue ribbons pile up over every surface across E7 (one more per beat, each a different iteration hue)
    rl = []
    for k in range(24):                        # one more residue ribbon every half beat; they pile up, never leave
        st = 0.21 * k
        y0 = -440 + 880 * ((k * 0.618) % 1)
        pts = []
        for j in range(25):
            u = j / 24
            x = -1150 + 2300 * u if k % 2 == 0 else 1150 - 2300 * u
            y = y0 + (120 + 8 * (k % 5)) * math.sin(6.28 * u * (1.1 + 0.12 * (k % 6)) + k)
            pts.append([r4(st + 0.9 * u), r4(x), r4(y)])
        rl.append(dict(type="canvas", module="ribbon", keepColor=True, params=dict(
            path=pts, colors=[HUE[k % 13], HUE[(k + 5) % 13]], width=22 + 9 * (k % 5), twist=0.6, bloom=0.9, grain=0.5,
            motes=0.35, seed=50 + k)))
    # the frame saturates: a Kandinsky colour wash rising under the ribbons (screen), strongest on the last bar
    rl.insert(0, dict(type="solid", keepColor=True, blend="multiply", color=[[0, HUE[0]], [1.7, HUE[3]], [3.4, HUE[1]], [5.0, HUE[2]]],
                      opacity=[[0, 0.06], [3.5, 0.22, "inCubic"], [5.0, 0.4]]))
    overlays.append(dict(id="D_E7_ribbons", start=134.0, end=139.0, layers=rl))

    # ---------------- E8: "Anomaly detected." ----------------
    E8 = take["e8"]
    c = C["e8_ring"]
    shots.append(dict(id="E8a_ring_turns", start=139.00, end=139.68, layers=[
        dict(id="agents", type="video", src=c["eng"], **{"in": E8["ring_in"], "rate": E8["ring_rate"]})],
        fx=[dict(type="negative", amount=[[0, 1]]), dict(type="flash", at=[0], dur=0.08, amount=1.0, color="#ffffff"),
            dict(type="hold", at=0, until=0.08), dict(type="shake", at=[0], amp=10, decay=0.2)]))
    c = C["e8_line"]
    shots.append(dict(id="E8b_line_turns", start=139.68, end=140.12, layers=[
        dict(id="agents", type="video", src=c["eng"], **{"in": E8["line_in"], "rate": E8["line_rate"]})],
        fx=[dict(type="negative", amount=1), dict(type="flash", at=[0], dur=0.06, amount=0.7, color="#ffffff"),
            dict(type="punch", at=[0], amount=0.05)]))
    TERM = ["TIME VARIANCE █████████", dict(text="ANOMALY DETECTED.", sync="lyric")]
    shots.append(dict(id="E8c_terminal", start=140.12, end=141.00, background=INK, layers=[
        dict(type="canvas", module="terminal", params=dict(mode="full", lines=TERM + [dict(text="TRACE: LOCKED", at=0.42, cps=36)],
                                                           cps=200, alarm=1, blink=0, size=88, x=170, y=400))]))
    overlays.append(dict(id="D_terminal_panel", start=139.00, end=140.12, layers=[dict(
        type="canvas", module="terminal", stage="post",
        params=dict(mode="panel", rect=[300, 770, 1320, 230], lines=TERM, cps=200, alarm=1, size=50))]))

    # a matted video draws only Jade: every shot whose bottom layer is a matted take gets the full frame underneath
    for sh in shots:
        L0 = sh["layers"][0]
        if L0.get("type") == "video" and L0.get("matte"):
            bg = {k: v for k, v in L0.items() if k not in ("matte", "keepColor", "id", "freeze")}
            if "freeze" in L0:
                bg["freeze"] = L0["freeze"]
            sh["layers"].insert(0, dict(id="bg", **bg))
    return dict(section="D", shots=shots, overlays=overlays), notes


def to_edl(sec):
    """EDL mirror (fallback format): every layer explicit, so it renders identically if the .js is ever removed."""
    out = dict(section="D", overlays=sec["overlays"], fx=[], shots=[])
    for s in sec["shots"]:
        e = dict(shot=s["id"], **{"in": s["start"], "out": s["end"]}, layers=s["layers"], fx=s.get("fx", []))
        if s.get("background"):
            e["background"] = s["background"]
        out["shots"].append(e)
    return out


if __name__ == "__main__":
    sec, notes = build()
    js = ("// Section D: drop 2 + \"Anomaly detected\" (112.96-141.00; E3 119.44-122.95 belongs to the singing director).\n"
          "// GENERATED by tools/sections/D/build_timeline.py from media/shots/_D/takes.json: edit those, not this file.\n"
          "// Ghost choreography (clip, freeze/offset, hue, opacity, position) is tabulated in docs/sections/D.md.\n"
          "export default " + json.dumps(sec, indent=1, ensure_ascii=False) + ";\n")
    os.makedirs("render/timeline", exist_ok=True)
    open("render/timeline/D.js", "w").write(js)
    json.dump(to_edl(sec), open(f"{SH}/D_edl.json", "w"), indent=1, ensure_ascii=False)
    json.dump(notes, open(f"{SH}/_D/ghost_table.json", "w"), indent=1, ensure_ascii=False, default=float)
    print("shots", len(sec["shots"]), "overlays", len(sec["overlays"]))
