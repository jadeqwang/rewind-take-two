#!/usr/bin/env python
"""Build section D's engine timeline (render/timeline/D.js) and the EDL mirror (media/shots/D_edl.json).

Section D = drop 2 + "Anomaly detected", 112.96-141.00. Revision 5 (v3 pass, docs/sections/D.md): the restaged chase
from the rev-B level clips (media/shots/B_<take>/take_1*, tools/sections/B/). Rev 5b (Jade's notes on the v3 cut): v2's
opening (E1 + E2a, ghosts 1-3) is restored, then chops 4-8 replay the v3 level as retries and 9-13 build the wall
ladder; "Rewind." #2 climbs that ghost ladder and is hauled onto the roof; the hint is compressed into the slide (the
gold ghost points at the BANACH-TARSKI spine while they slide); the blue ghost boosts her over the swarm, the agents
collide beneath her, she atomizes and splits; the rainbow Jades follow. E3 is rev-A's watercolor singing take (lip sync baked in). E7's meter insert and E8 still
use v2 takes from media/shots/_D/takes.json. Ghost twins: tools/sections/D/split2.py (split the shared matte),
patch.py (clean-plate patch), ghostseq.py (moving line-art ghost), ghostfill.py (opaque ghost, no plate); assets in
media/shots/_D/v3/.

    tools/engrave/.venv/bin/python tools/sections/D/build_timeline.py
"""
import glob
import json
import math
import os
import sys

import cv2
import numpy as np

# E3 singing take (rev 5): rev-A's watercolor singer, lip sync baked in: file time 0 = song 119.44, rate 1, no lag
E3_TAKE = "media/sing/E3/v3_sync_1080.mp4"
E3_MATTE = "media/sing/E3/v3_sync_1080_matte/"             # her per-frame matte (24 fps PNGs): the ribbon occluder

ROOT = "/home/jade/Documents/rewind-take-two"
os.chdir(ROOT)
FPS = 24
SH = "media/shots"

# 13 ghost hues: the Kandinsky spectrum (orange, blue, gold, magenta, green) then its in-betweens (rev 5: #E4572E
# vermilion -> #E9A23B amber; nothing in this section may read as red)
HUE = ["#F08A24", "#3E6FD8", "#C9A227", "#C23B8E", "#3FA55B", "#E9A23B", "#8DB8E8", "#E8D04A", "#8E5CC8", "#2BA59A",
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


sys.path.insert(0, os.path.join(ROOT, "tools/sections/D"))
import ghostsprite  # noqa: E402

SPR = f"{SH}/_D/sprites"


def sprite_of(c, freeze, color, matte="matte", scale=1.0, box=None):
    """bake (once) the luminous line-art afterimage of clip c at `freeze`; returns (path, stats in design px).
    box = normalised [x0, y0, x1, y1] keeps only that part of the matte (agents out of the ghost)."""
    os.makedirs(SPR, exist_ok=True)
    ol = int(round(min(12, max(4, 3.5 / max(scale, 0.05)))))      # outline/glow survive downscaling for distant ghosts
    tag = os.path.basename(os.path.dirname(c["stem"])) + "_" + os.path.basename(c["stem"])
    bx = "" if not box else "_b" + "-".join(f"{v:g}" for v in box)
    name = f"{tag}_{matte}_{freeze:.3f}_{color.lstrip('#')}_o{ol}{bx}.png"
    path = f"{SPR}/{name}"
    meta = path[:-4] + ".json"
    if os.path.exists(path) and os.path.exists(meta) and os.path.getmtime(path) > os.path.getmtime(ghostsprite.__file__):
        return path, json.load(open(meta))
    st = ghostsprite.sprite(c["eng"], f"{c['stem']}_{matte}", freeze, color, path, outline=ol, glow=18 * ol / 4, box=box)
    json.dump(st, open(meta, "w"))
    return path, st


def ghost(id_, c, freeze, color, hit_local, matte="matte", x=0, y=0, scale=1.0, flip=False, glide=None, born=True):
    """One frozen iteration as a baked sprite image layer (full-frame RGBA, same framing as the clip).
    Revealed on its chop (`hit_local`, shot-local s); optional glide [dx, dy] over .35 s so ghosts fan out."""
    path, st = sprite_of(c, freeze, color, matte, scale)
    L = dict(id=id_, type="image", src=path, keepColor=True, fit="cover", scale=[r4(-scale), r4(scale)] if flip else r4(scale))
    if glide:
        h = hit_local
        L["x"] = [[r4(h), r4(x), "outCubic"], [r4(h + 0.35), r4(x + glide[0])]]
        L["y"] = [[r4(h), r4(y), "outCubic"], [r4(h + 0.35), r4(y + glide[1])]]
    else:
        L["x"], L["y"] = r4(x), r4(y)
    if born:
        L["opacity"] = [[0, 0, "hold"], [r4(hit_local), 1.0]]
    return L, st


def ribbon(id_, path, colors=RES, width=24, **kw):
    """path keys are centre-origin design px here; the ribbon module wants absolute design px (0..1920, 0..1080)."""
    if path:
        path = [[k[0], r4(k[1] + 960), r4(k[2] + 540)] for k in path]
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


# ------------------------------------------------------------------ rev 5 (v3 pass): the restaged level clips
V3 = f"{SH}/_D/v3"                 # rev 5 plates, patches and baked ghost sequences
E4_WORD = [400, 820, 1170, 820, 1170, 1055, 400, 1055]     # "Rewind." painted on the lower-left brickwork of the climb wall


def bclip(take):
    """a rev-B take (media/shots/B_<take>/take_1*): engraved plate, engrave matte, split twin mattes, colour-gated matte."""
    stem = f"{SH}/B_{take}/take_1"
    return dict(eng=stem + "_engraved.mp4", matte=stem + "_matte/matte.mp4", ghost=stem + "_ghost/matte.mp4",
                live=stem + "_live/matte.mp4", jmatte=stem + "_jmatte/matte.mp4", stem=stem)


def doubling(id_, c, times_abs, shot_start, shot_dur, in0, rate=1.0, steps=(-4, 6, -2, 1), spacing=20, slot_time=2 / FPS,
             stagger=16, peel=0.3, tint=0.82, opacity=0.9, place=None):
    """Python port of render/timeline/_B_fx.js doubling() with every function sampled into keys (D.js is plain JSON).
    The number of Jades doubles on each time; a new copy starts stacked on its parent (same place, same frame) and
    peels to its own slot in a bar ahead of / behind her: slot q = q*slot_time s of her own clip and q*spacing px.
    Copy n takes HUE[(n-1) % 13]; times before the shot start are already peeled (the bar continues across a cut)."""
    place = place or {}
    tb = [t - shot_start for t in times_abs]
    G = len(tb)
    ease = lambda u: 1 - (1 - min(1.0, max(0.0, u))) ** 3
    slot_of = lambda i: sum(s for g, s in enumerate(steps[:G]) if (i >> g) & 1)
    copies = []
    for n in range(1, 1 << G):
        gen = n.bit_length() - 1
        copies.append(dict(n=n, slot=slot_of(n), frm=slot_of(n - (1 << gen)), t=tb[gen]))
    lts = [k / 24 for k in range(int(round(shot_dur * 24)) + 1)]
    out = []
    for cp in sorted(copies, key=lambda c_: (-abs(c_["slot"]), c_["n"])):
        if cp["t"] > shot_dur:
            continue
        sl = lambda lt: cp["frm"] + (cp["slot"] - cp["frm"]) * ease((lt - cp["t"]) / peel)
        row = (stagger if cp["slot"] % 2 else -stagger)
        k_in = [[r4(lt), r4(in0 + sl(lt) * slot_time)] for lt in lts]
        k_x = [[r4(lt), r4(place.get("x", 0) + sl(lt) * spacing)] for lt in lts]
        k_y = [[r4(lt), r4(place.get("y", 0) + row * ease((lt - cp["t"]) / peel))] for lt in lts]
        op = [[0, 1.0]] if cp["t"] <= 0 else [[0, 0, "hold"], [r4(cp["t"] - 0.01), 0], [r4(cp["t"] + 2 / FPS), 1]]
        L = dict(id=f"{id_}_{cp['n']:02d}", type="ghosts", src=c["eng"], matte=dict(src=c["matte"], mode="luma"), keepColor=True,
                 loop=False, rate=rate, fit="cover", x=k_x, y=k_y, opacity=op,
                 instances=[dict(color=HUE[(cp["n"] - 1) % 13], tint=tint, opacity=opacity)])
        L["in"] = k_in
        if "scale" in place:
            L["scale"] = place["scale"]
        out.append(L)
    return out


def build():
    shots, overlays, notes = [], [], {}
    take = json.load(open(f"{SH}/_D/takes.json"))     # v2 takes still used: E7 meter insert, E8
    C = {k: clip(v["shot"], f"{k}_{v['take']}") for k, v in take.items() if isinstance(v, dict) and "shot" in v}

    # ---------------- E1 + E2a (v2, restored in rev 5b): the L tracks (impact, ghosts 1-3) ----------------
    # Jade's note on the v3 cut: keep v2's opening (residue bloom, sprint, superman dive and roll, column kick, ghosts
    # 1-3) exactly as v2 had it, 112.96-114.905, then cut to the v3 level retries.
    t0, t1 = 112.96, CHOPS[2] + 0.125
    h = [c_ - t0 for c_ in CHOPS[:3]]                     # local hit times 0.93, 1.39, 1.82
    sp, da, wj = C["trk_sprint"], C["trk_dash"], C["trk_walljump"]
    WJ = take["trk_walljump"]                             # {in, rate, freeze}
    seg = [(sp, 2.75, 1.0, 0.0, h[0], 0.0),
           (da, 1.96, 1.65, h[0], h[1], 0.25),
           (wj, WJ["freeze"], WJ["rate"], h[1], h[2], 0.25)]
    layers = [dict(id="plate", type="image", src=f"{SH}/E2/plate_trk.png")]
    ghosts, ribs = [], []
    E2A_SPREAD = [(-640, None), (-120, -40), (560, -80)]
    for k, (c, frz, rate, a, b, snap) in enumerate(seg):
        play = (b - a) - (0.125 if snap else 0.0)
        si = frz - rate * play
        layers.append(live(f"live{k + 1}", c, si, rate, a, b, snap=snap))
        pth = seg_path(c["stem"], si, rate, a + (0.125 if snap else 0.0), b)
        ribs.append(ribbon(f"res{k + 1}", pth, colors=[HUE[k], RES[1]], width=26))
        g, st = ghost(f"g{k + 1}", c, frz, HUE[k], b, glide=None)
        tx, ty = E2A_SPREAD[k]
        g["x"] = [[r4(b), 0, "outCubic"], [r4(b + 0.35), r4(tx - st["cx"])]]
        if ty is not None:
            g["y"] = [[r4(b), 0, "outCubic"], [r4(b + 0.35), r4(ty - st["cy"])]]
        ghosts.append(g)
        notes[f"g{k + 1}"] = dict(clip=c["eng"], freeze=frz, hue=HUE[k], where="L tracks (v2, as frozen)", hit=CHOPS[k])
    s1 = mstats(sp["stem"], 2.75 - h[0])
    layers[1:1] = [
        dict(id="bloom", type="image", src=f"{SH}/_D/e1_bloom.png", keepColor=True, fit="none", end=0.93,
             x=r4(s1["cx"]), y=r4(s1["cy"]), scale=[[0, 0.1, "outCubic"], [0.85, 1.5]],
             rotate=[[0, 0], [0.93, 14]], opacity=[[0, 1.0], [0.45, 0.9, "inCubic"], [0.93, 0.0]]),
        dict(id="bloom_glow", type="image", src=f"{SH}/_D/e1_bloom.png", keepColor=True, fit="none", end=0.6, blend="add",
             x=r4(s1["cx"]), y=r4(s1["cy"]), scale=[[0, 0.08, "outCubic"], [0.6, 1.1]], opacity=[[0, 0.5], [0.6, 0.0]]),
    ]
    layers += ribs + ghosts
    layers += [
        dict(id="burst", type="canvas", module="motes", keepColor=True, end=1.6,
             params=dict(at=0.0, x=r4(s1["cx"] + 960), y=r4(s1["cy"] + 540), count=220,
                         colors=[RES[0], RES[0], RES[1], RES[1], "#C9A227"], shape="circle", speed=2600, drag=2.4, size=13,
                         life=1.2, ring=False, glow=1.0, seed=65)),
    ] + [ribbon(f"e1_flow{j}", [[r4(0.02 * j), r4(s1["cx"]), r4(s1["cy"])]] +
                [[r4(0.02 * j + 0.07 * q), r4(s1["cx"] + (210 * q) * math.cos(j * 0.698 + 0.1 * q * (1 if j % 2 else -1))),
                  r4(s1["cy"] + (170 * q) * math.sin(j * 0.698 + 0.1 * q * (1 if j % 2 else -1)))] for q in range(1, 9)],
                colors=[RES[0], "#C9A227" if j % 4 == 0 else RES[1]], width=46, trail=0.7, pencil=bool(j % 2), bloom=1.0,
                grain=0.8, motes=0.4, seed=80 + j) | dict(end=1.0) for j in range(9)]
    shots.append(dict(id="E1_E2a_tracks", start=t0, end=r4(t1), layers=layers,
                      fx=[dict(type="flash", at=[0], dur=0.06, amount=1.0, color="#ffffff"),
                          dict(type="shake", at=[0], amp=14, decay=0.3)] + chop_fx(h)))

    # ---------------- E2 chops 4-8: the v3 level as fast retries, a hard cut on every chop ----------------
    # Each attempt ends exactly on its chop; its in-point is solved backwards from the freeze, so the pose on the chop
    # frame IS the ghost. Attempts 5-8 open with the 3-frame ◀◀ scrub (0.25 s of source); the first is a hard cut from
    # v2's tracks. Ghost k pops where she froze and hangs over attempt k+1, fading out by the next chop. Left to right.
    #        (take, freeze s = her pose on the chop, rate, sprite box (normalised; keeps agents out of the ghost), what)
    LEVEL = [("leap", 0.54, 1.6, None, "off the platform, mid-leap"),
             ("chasm_short", 3.67, 1.6, None, "reaching, short of the far wall"),
             ("lawn", 0.75, 1.3, [0.4, 0, 1, 1], "a zig on the lawn"),
             ("lawn2", 1.30, 1.3, [0.25, 0, 1, 1], "a zag past the notice board"),
             ("kick", 2.08, 1.3, [0, 0, 0.5, 1], "the wall-kick at the hotel corner")]
    starts = [t1] + CHOPS[3:7]
    prev_ghost = None
    for j, (tk, frz, rate, box, what) in enumerate(LEVEL):
        k = 3 + j                                       # global chop / ghost index (hues continue from v2's 1-3)
        c = bclip(tk)
        a, b = starts[j], CHOPS[k]
        d = b - a
        snap = 0.0 if j == 0 else 0.25
        si = frz - rate * (d - (0.125 if snap else 0.0))
        L = [plate("bg", c, si, rate, 0, d, snap=snap),
             live("jade", c, si, rate, 0, d, snap=snap)]
        pth = seg_path(c["stem"], si, rate, 0.125 if snap else 0.0, d, box=box)
        L.append(ribbon(f"res{k + 1}", pth, colors=[HUE[k], RES[1]], width=24))
        if prev_ghost:
            L.insert(1, prev_ghost)          # under her live layer
        fx = [dict(type="flash", at=[0], dur=0.08, amount=0.35, color="#8DB8E8")] if j else \
             [dict(type="flash", at=[0], dur=0.06, amount=0.5, color="#ffffff")]
        if snap:
            fx.append(dict(type="rewind", amount=[[0, 0.85], [0.12, 0]]))
            fx.append(dict(type="punch", at=[0], amount=0.035, decay=0.12))
        shots.append(dict(id=f"E2_{k + 1:02d}_{tk}", start=r4(a), end=r4(b), layers=L, fx=fx))
        path, st = sprite_of(c, frz, HUE[k], "matte", 1.0, box=box)
        nd = (CHOPS[k + 1] - CHOPS[k]) if k < 7 else 0.44
        prev_ghost = dict(id=f"g{k + 1}", type="image", src=path, keepColor=True, fit="cover",
                          opacity=[[0, 1.0], [r4(nd * 0.55), 0.85, "inCubic"], [r4(nd - 0.02), 0.0]], end=r4(nd))
        notes[f"g{k + 1}"] = dict(clip=c["eng"], freeze=frz, hue=HUE[k], where=what, hit=CHOPS[k], h_frac=round((st["y1"] - st["y0"]) / 1080, 3))

    # ---------------- E2 chops 9-13: the Hilbert's side wall, one held shot, a ladder of five ghosts ----------------
    # The plate is scaled 1.4 from the top edge (cornice stays in frame), so she and her ghosts are ~28-38% of frame
    # height. Five attempts, each ending on its chop higher up the facade; ghosts 11/12 step aside so 13 can hang by them.
    t0, t1 = CHOPS[7], 119.44
    c = bclip("climb")
    SC = 1.4
    PL = dict(fit="cover", scale=SC, x=54, y=r4(540 * (SC - 1)))
    CL = [(1.12, 1.6, (0, 0), "on the awning"), (1.75, 1.6, (0, 0), "springing for the window ledge"),
          (3.62, 1.8, (-380, -80), "on the fire-escape stairs"), (4.25, 1.8, (-200, 0), "climbing to the top landing"),
          (5.85, 1.3, (0, 0), "hanging just short of the cornice")]
    starts = [t0] + CHOPS[8:12]
    L, gl, ladder = [], [], []
    for j, (frz, rate, (dx, dy), what) in enumerate(CL):
        k = 8 + j
        a, b = starts[j] - t0, CHOPS[k] - t0
        end = b if k < 12 else t1 - t0
        si = frz - rate * (b - a - 0.125)
        seg = dict(start=r4(a), end=r4(end))
        # the attempt plays to its chop, then holds that frame (it is the ghost) until the next attempt's ◀◀
        sT = [[0, r4(si + 0.25)], [0.125, r4(si), "outCubic"], [r4(b - a), r4(frz), "hold"], [r4(end - a), r4(frz)]]
        L.append(dict(id=f"bg{k + 1}", type="video", src=c["eng"], srcTime=sT, **seg, **PL))
        L.append(dict(id=f"jade{k + 1}", type="video", src=c["eng"], matte=dict(src=c["matte"], mode="luma"), keepColor=True,
                      srcTime=sT, **seg, **PL, opacity=[[0, 1, "hold"], [r4(b - a), 0]]))
        path, st = sprite_of(c, frz, HUE[k], "matte", SC)
        ladder.append((k, path, frz))
        g = dict(id=f"g{k + 1}", type="image", src=path, keepColor=True, fit="cover",
                 scale=SC, y=PL["y"], x=PL["x"], opacity=[[0, 0, "hold"], [r4(b - 0.01), 0], [r4(b), 1.0], [r4(b + 0.12), 0.85]])
        if dx or dy:
            g["x"] = [[r4(b + 0.1), PL["x"], "outCubic"], [r4(b + 0.42), PL["x"] + dx]]
            g["y"] = [[r4(b + 0.1), PL["y"], "outCubic"], [r4(b + 0.42), PL["y"] + dy]]
        gl.append(g)
        notes[f"g{k + 1}"] = dict(clip=c["eng"], freeze=frz, hue=HUE[k], where=what, hit=CHOPS[k],
                                  h_frac=round(SC * (st["y1"] - st["y0"]) / 1080, 3), step_aside=[dx, dy])
    L.append(ribbon("res_climb", None, follow=dict(layer="jade9", point="centroid", smooth=3), colors=[HUE[8], HUE[12]], width=16)
             | dict(end=r4(CHOPS[8] - t0)))
    L[-1]["params"].pop("path")
    # last level ghost (the wall-kick) dissolves over the first wall attempt
    g8 = prev_ghost
    g8["opacity"] = [[0, 1.0], [0.3, 0.0]]
    shots.append(dict(id="E2_09_climb", start=t0, end=t1, layers=L + gl + [g8],
                      fx=[dict(type="flash", at=[0], dur=0.08, amount=0.35, color="#8DB8E8"),
                          dict(type="rewind", amount=[[0, 0.85], [0.12, 0]] + sum(
                              [[[r4(c_ - t0 - 0.001), 0], [r4(c_ - t0), 0.85], [r4(c_ - t0 + 0.12), 0]] for c_ in CHOPS[8:12]], [])),
                          dict(type="flash", at=[r4(c_ - t0) for c_ in CHOPS[8:]], dur=0.08, amount=0.35, color="#8DB8E8"),
                          dict(type="punch", on="vocal_chops", amount=0.035, decay=0.12)]))

    # ghost counter over E2 (Press Start 2P, top right, ink on paper): one more per chop, odometer roll
    keys = [[0, 0, "hold"]]
    for k, c_ in enumerate(CHOPS):
        keys += [[r4(c_ - 113.89 - 0.07), k, "linear"], [r4(c_ - 113.89), k + 1, "hold"]]
    overlays.append(dict(id="D_ghost_counter", start=113.89, end=119.44, layers=[
        dict(type="solid", stage="post", color=PAPER, opacity=0.88, rect=[1580, 40, 312, 56]), dict(
            type="canvas", module="hud", stage="post", params=dict(mode="iteration", label="GHOSTS", value=keys[1:] if keys[1][0] <= 0 else keys,
                                                                   snap=True, side="right", color=INK, size=26))]))

    # ---------------- E3: SINGING #2 "Rewind." (rev-A's watercolor take; lip sync baked in) ----------------
    t0, t1 = 119.44, 122.95
    HEAD = (960, 380)
    KB = {"kenBurns": {"from": {"scale": 1.0, "x": 0, "y": 0},
                       "to": {"scale": 1.08, "x": r4(-(HEAD[0] - 960) * 0.08), "y": r4(-(HEAD[1] - 540) * 0.08)}, "ease": "linear"}}
    # ribbons spiral in from beyond the frame edges and settle on an orbit round her head and shoulders; the occluder
    # (the same take matted by her own per-frame matte) is drawn over them, so they always pass BEHIND her.
    CX, CY, RX, RY, TILT = 960, 600, 780, 400, math.radians(-8)
    e3_ribs = []
    for k in range(7):
        st = 0.18 * k
        a0 = math.radians(25 + 52 * k)
        sc = 0.92 + 0.07 * (k % 3)
        w = 2 * math.pi / (2.6 + 0.25 * (k % 3))
        pts = []
        for j in range(int((t1 - t0 - st) * 12) + 1):
            tt = j / 12
            r = sc * (1 + 1.25 * math.exp(-tt / 0.45))
            a = a0 + w * tt
            x, y = RX * r * math.cos(a), RY * r * math.sin(a)
            xr, yr = x * math.cos(TILT) - y * math.sin(TILT), x * math.sin(TILT) + y * math.cos(TILT)
            pts.append([r4(st + tt), r4(CX + xr), r4(CY + yr)])
        e3_ribs.append(dict(type="canvas", module="ribbon", keepColor=True, params=dict(
            path=pts, colors=[RES[k % 2], RES[(k + 1) % 2]], width=40 + 10 * (k % 3), trail=1.5, twist=0.7, bloom=0.9,
            grain=0.75, pencil=False, motes=0.3, seed=120 + k)))
    shots.append(dict(id="E3_sing", start=t0, end=t1, background=INK, layers=[
        dict(id="jade", type="video", src=E3_TAKE, fit="cover", **{"in": 0.0, "rate": 1.0}, **KB),
        *e3_ribs,
        dict(id="occluder", type="video", src=E3_TAKE, fit="cover", **{"in": 0.0, "rate": 1.0}, **KB,
             matte=dict(src=E3_MATTE, mode="luma")),
        dict(type="canvas", module="lowerthird", stage="post", params=dict(color=INK, size=112, y=1000, halo=1.0))],
        fx=[dict(type="flash", at=[0], dur=0.06, amount=0.35, color="#ffffff")]))
    notes["E3"] = dict(take=E3_TAKE, clip_in=0.0, push="1.0 -> 1.08 on her head", orbit=[CX, CY, RX, RY, -8])

    def twin_shot(id_, tk, gname, t0, t1, src_in, rate, g_t0, extra=(), under=(), fx=(), patch=True, g_op=0.9):
        """a two-Jade take: the plate, a clean-plate patch where the ghost girl ever is, the ghost girl redrawn as a
        translucent line-art ghost (baked by ghostseq.py from the split matte), the live girl on top, in colour."""
        c = bclip(tk)
        tm = {"in": src_in, "rate": rate}
        return dict(id=id_, start=t0, end=t1, layers=[
            dict(id="bg", type="video", src=c["eng"], **tm),
            *([dict(id="clean", type="image", src=f"{V3}/patch_{gname}.png", fit="cover")] if patch else []),
            *under,
            dict(id="ghost", type="video", src=f"{V3}/ghost_{gname}_rgb.mp4", keepColor=True, opacity=g_op,
                 matte=dict(src=f"{V3}/ghost_{gname}_alpha.mp4", mode="luma"), **{"in": r4(src_in - g_t0), "rate": rate}),
            dict(id="jade", type="video", src=c["eng"], matte=dict(src=c["live"], mode="luma"), keepColor=True, **tm),
            *extra], fx=list(fx))

    # ---------------- E4: "Rewind." #2 = up her own ghost ladder, then the gold ghost hauls her onto the roof ----------------
    # rev 5b: no wall boost. She climbs the fire escape through her own five ghosts from E2 (each at its frozen pose,
    # so they are the rungs of a ladder of herself; each brightens as she passes through it) and arrives in ghost 13's
    # pose at the cornice on the cut. climb 3.45 -> 5.95 at x1.75 over 122.95-124.38, same x1.4 framing as E2.
    c = bclip("climb")
    E4_IN, E4_RATE, E4_T0, E4_T1 = 3.45, 1.75, 122.95, 124.38
    word = dict(type="canvas", module="pin", keepColor=True, blend="multiply", params=dict(
        style="ground", font="fell", text="Rewind.", times=["word:rewind#4"], size=170, color="#E07A14", grain=0.25,
        corners=E4_WORD))
    rungs = []
    for (k, path, frz) in ladder:
        tp = (frz - E4_IN) / E4_RATE                    # shot time she passes through this pose
        op = [[0, 0.75]] + ([[r4(tp - 0.12), 0.75], [r4(tp), 1.0], [r4(tp + 0.35), 0.6]] if 0 < tp < E4_T1 - E4_T0 + 0.1 else [])
        rungs.append(dict(id=f"rung{k + 1}", type="image", src=path, keepColor=True, fit="cover", scale=SC, x=PL["x"], y=PL["y"],
                          opacity=op))
    shots.append(dict(id="E4a_ladder", start=E4_T0, end=E4_T1, layers=[
        dict(id="bg", type="video", src=c["eng"], **{"in": E4_IN, "rate": E4_RATE}, **PL),
        word, *rungs,
        dict(id="jade", type="video", src=c["eng"], matte=dict(src=c["matte"], mode="luma"), keepColor=True,
             **{"in": E4_IN, "rate": E4_RATE}, **PL),
        ribbon("res_ladder", None, follow=dict(layer="jade", point="centroid", smooth=3), colors=[HUE[8], HUE[12]], width=18)],
        fx=[dict(type="flash", at=["word:rewind#4"], dur=0.12, amount=0.5, color="#ffffff"),
            dict(type="punch", on="beat", amount=0.02)]))
    shots[-1]["layers"][-1]["params"].pop("path")
    notes["E4a"] = dict(clip=c["eng"], in_=E4_IN, rate=E4_RATE, rungs="ghosts 9-13 at their frozen poses")
    shots.append(twin_shot("E4b_haul", "haul_b", "haul", 124.38, 126.25, 0.05, 1.3, 0.0,
                           fx=[dict(type="flash", at=[0], dur=0.06, amount=0.35, color="#ffffff"),
                               dict(type="punch", on="beat", amount=0.02)]))
    notes["E4b"] = dict(clip=bclip("haul_b")["eng"], ghost="girl lying on the roof, gold #C9A227", in_=0.05, rate=1.3)

    # ---------------- E5 (rev 5b): the hint while sliding. slide_point: hand in hand down the giant book (Escher, Still
    # Life and Street); the leading girl (gold ghost) points at the blank label on the spine of the upright book at
    # frame right, which reads BANACH–/TARSKI. Locked-off camera: the label stays at 1507-1690 x 211-362 (tracked, no
    # drift). in 0.8 at x1.4: they leave the book's bottom edge on the cut.
    lab = dict(id="label", type="canvas", module="pin", blend="multiply", params=dict(
        style="plain", font="fell", text="BANACH–\nTARSKI", size=96, color=INK, padding=4,
        corners=[1517, 226, 1680, 226, 1680, 348, 1517, 348]))
    shots.append(twin_shot("E5_slide_point", "slide_point", "slidept", 126.25, 128.76, 0.8, 1.4, 0.8, under=[lab],
                           fx=[dict(type="flash", at=[0], dur=0.06, amount=0.35, color="#ffffff")]))
    notes["E5"] = dict(clip=bclip("slide_point")["eng"], ghost="leading (pointing) girl, gold", in_=0.8, rate=1.4,
                       label="BANACH–/TARSKI pinned on the upright book's spine label")

    # ---------------- E6 (rev 5b): swarm boost, atomize, two Jades ----------------
    # swarm_boost at x1.14 from 0.315: the kneeling girl (blue ghost; baked opaque by ghostfill.py, because the agents
    # pile through her and a static clean plate would erase them) heaves from 129.15 and her foot leaves the hands at
    # source 1.77 = 130.04 (beat); the agents from both sides crash into each other beneath her at source 2.80 = 130.94
    # (beat); she hangs at the peak to the freeze at source 3.30 (frame 79) = 131.38.
    E6_IN, E6_RATE = 0.315, 1.14
    shots.append(twin_shot("E6a_swarm", "swarm_boost", "swarm", 128.76, 131.38, E6_IN, E6_RATE, 0.3, patch=False, g_op=0.95,
                           fx=[dict(type="flash", at=[0], dur=0.06, amount=0.35, color="#ffffff"),
                               dict(type="punch", at=[r4(130.94 - 128.76)], amount=0.05, decay=0.14),
                               dict(type="shake", at=[r4(130.94 - 128.76)], amp=10, decay=0.2)]))
    notes["E6a"] = dict(clip=bclip("swarm_boost")["eng"], ghost="kneeling girl, blue #3E6FD8 (opaque fill)", in_=E6_IN, rate=E6_RATE, launch=130.04, collision=130.94)
    # 131.38 (source 3.30, frame 79): freeze + flash; she bursts into 150 motes in mid-air over the frozen heap
    BX, BY = -8, -272
    shots.append(dict(id="E6b_atomize", start=131.38, end=131.82, layers=[
        dict(id="clean", type="image", src=f"{V3}/swarm_clean_79.png", fit="cover"),
        dict(id="ghost", type="image", src=f"{V3}/ghost_swarm_00079.png", keepColor=True, fit="cover", opacity=0.95),
        dict(id="jade", type="image", src=f"{V3}/swarm_her_79.png", keepColor=True, fit="cover", opacity=[[0, 1.0], [0.1, 0.0, "inCubic"]]),
        dict(id="motes", type="canvas", module="motes", keepColor=True, params=dict(
            at=0.0, x=BX + 960, y=BY + 540, count=150, colors=RES + ["#ffffff", "#1f2a44", "#F08A24"],
            speed=1500, drag=2.2, gravity=-20, size=17, life=2.0, ring=True, glow=1.0, seed=31))],
        fx=[dict(type="flash", at=[0], dur=0.1, amount=0.8, color="#ffffff"), dict(type="shake", at=[0], amp=8, decay=0.2)]))
    # 131.82: two mote clouds implode (time-reversed burst) into two crouched Jades over the heap; on the bar line 132.26
    # they sprint apart, out of both edges, with an orange and a blue ribbon; the agents get up into the empty street
    c = bclip("two")
    LX, RX_, GY = -269, 307, 108
    imp = lambda x, seed: dict(type="canvas", module="motes", keepColor=True, end=0.44, time=[[0, 0.44], [0.44, 0.0]], params=dict(
        at=0, x=x + 960, y=GY + 540, count=110, colors=RES + ["#ffffff"], speed=1300, drag=2.2, size=16, life=2.0, ring=False,
        glow=0.9, seed=seed))
    run = lambda s: 0.44 + (s - 0.55)        # source s -> shot time
    # her own path (read off the frames): off the mark at 0.6, out of the frame edge by about 1.05
    rib_l = [[r4(run(s)), r4(LX - 1000 * max(0.0, s - 0.6) / 0.45), r4(GY + 10 + 30 * math.sin(9 * s))] for s in [0.58 + 0.04 * q for q in range(16)]]
    rib_r = [[r4(run(s)), r4(RX_ + 1000 * max(0.0, s - 0.6) / 0.45), r4(GY + 10 + 30 * math.cos(9 * s))] for s in [0.58 + 0.04 * q for q in range(16)]]
    shots.append(dict(id="E6c_two", start=131.82, end=134.00, layers=[
        dict(id="still", type="video", src=c["eng"], end=0.44, **{"in": 0.4, "rate": 1.0}, freeze=0),
        dict(id="clean", type="image", src=f"{V3}/patch_two.png", fit="cover", end=0.44, opacity=[[0, 1.0], [0.28, 1.0], [0.42, 0.0]]),
        dict(id="play", type="video", src=c["eng"], start=0.44, **{"in": 0.55, "rate": 1.0}, grade=dict(residueRim=1.0)),
        # the take's own rainbow speed streaks over the heap (source ~0.8-1.45) are hidden under the clean heap plate
        # once both girls have cleared the middle; the ribbons carry the colour instead
        dict(id="unstreak", type="image", src=f"{V3}/patch_two.png", fit="cover", start=r4(run(0.9)), end=r4(run(1.5)),
             opacity=[[0, 0.0], [0.08, 1.0], [r4(run(1.5) - run(0.9) - 0.1), 1.0], [r4(run(1.5) - run(0.9)), 0.0]]),
        imp(LX, 32), imp(RX_, 33),
        ribbon("resL", rib_l, colors=[RES[0], "#C9A227"], width=150, trail=0.9, twist=0.9) | dict(start=0.44),
        ribbon("resR", rib_r, colors=[RES[1], "#3E6FD8"], width=150, trail=0.9, twist=0.9) | dict(start=0.44)],
        fx=[dict(type="flash", at=[0.44], dur=0.08, amount=0.6, color="#ffffff"), dict(type="punch", on="beat", amount=0.025)]))

    # ---------------- E7: the rainbow Jades, after the split. Doubling on every beat 134.00-135.32 ----------------
    DB = [134.00, 134.44, 134.88, 135.32]

    def e7(id_, a, b, layers, fx=()):
        shots.append(dict(id=id_, start=a, end=b, layers=layers, fx=[dict(type="flash", at=[0], dur=0.05, amount=0.25, color="#ffffff"),
                                                                    dict(type="punch", at=[0], amount=0.04)] + list(fx)))
    for (id_, tk, a, b, in0, sp) in (("E7_01_plat", "plat", 134.00, 134.88, 0.55, 30), ("E7_02_leap", "leap", 134.88, 135.76, 0.85, 75)):
        c = bclip(tk)
        cps = doubling("dbl", c, DB, a, b - a, in0, spacing=sp, stagger=22)
        e7(id_, a, b, [dict(id="bg", type="video", src=c["eng"], **{"in": in0, "rate": 1.0}), *cps,
                       dict(id="jade", type="video", src=c["eng"], matte=dict(src=c["matte"], mode="luma"), keepColor=True,
                            **{"in": in0, "rate": 1.0})],
           fx=[dict(type="flash", at=[r4(t - a) for t in DB if a <= t < b], dur=0.05, amount=0.12)])
    m = take["e7_cuts"][1]
    c = C["e7_meter"]
    e7("E7_03_meter", 135.76, 136.62, [dict(id="meter", type="video", src=c["eng"], **{"in": m["in"], "rate": m["rate"]})],
       fx=[dict(type="shake", at=[0], amp=12, decay=0.3)])
    # chasm: sixteen time-offset copies; each arc fans out from the stack in flight and they all dash (a sheaf of arcs)
    c = bclip("chasm_dash")
    a, b, in0, rate = 136.62, 137.50, 1.1, 2.0
    sheaf = []
    for k in range(1, 16):
        off = -0.03 * k                        # a stream of attempts on the same route, each a little later ...
        A = (k - 8) * 30                       # ... fanned into a sheaf of arcs in flight, converging on the far lip
        ys = [[r4(lt), r4(A * math.sin(math.pi * min(1.0, lt / 0.86)))] for lt in [q / 12 for q in range(12)]]
        xs = [[r4(lt), r4(-38 * k * math.sin(math.pi * min(1.0, lt / 0.86)))] for lt in [q / 12 for q in range(12)]]
        sheaf.append(dict(id=f"sheaf{k:02d}", type="ghosts", src=c["eng"], matte=dict(src=c["matte"], mode="luma"), keepColor=True,
                          loop=False, fit="cover", x=xs, y=ys, **{"in": in0, "rate": rate},
                          instances=[dict(offset=r4(off), color=HUE[(k - 1) % 13], tint=0.82, opacity=0.85)],
                          opacity=[[0, 0.0], [0.12, 1.0]]))
    e7("E7_04_chasm", a, b, [dict(id="bg", type="video", src=c["eng"], **{"in": in0, "rate": rate}), *sheaf[::-1],
                             dict(id="jade", type="video", src=c["eng"], matte=dict(src=c["matte"], mode="luma"), keepColor=True,
                                  **{"in": in0, "rate": rate})])
    c = bclip("ear")
    e7("E7_05_ear", 137.50, 138.38, [dict(id="ear", type="video", src=c["eng"], **{"in": 0.6, "rate": 1.0})])
    # the lawn: the copies fanned across it, all running away from the firing line toward the hotel
    c = bclip("lawn")
    fan = []
    for k in range(12):                        # later selves only (further on, smaller), never back toward the agents
        u = k / 11
        fan.append(dict(offset=r4(round((0.12 + 0.85 * ((k * 0.618) % 1)) * FPS) / FPS), x=r4(-170 + 340 * ((k * 0.382) % 1)),
                        y=r4(-30 + 60 * u), color=HUE[k % 13], tint=0.8, opacity=0.85))
    e7("E7_06_lawn", 138.38, 139.00, [
        dict(id="bg", type="video", src=c["eng"], **{"in": 1.3, "rate": 1.0}),
        dict(id="fan", type="ghosts", src=c["eng"], matte=dict(src=c["jmatte"], mode="luma"), keepColor=True, loop=False,
             fit="cover", **{"in": 1.3, "rate": 1.0}, instances=fan, show=[[0, 5], [0.3, 12, "outCubic"]]),
        dict(id="jade", type="video", src=c["eng"], matte=dict(src=c["matte"], mode="luma"), keepColor=True, **{"in": 1.3, "rate": 1.0})],
       fx=[dict(type="flash", at=[0.56], dur=0.06, amount=1.0, color="#ffffff")])
    # residue ribbons pile up over every surface across E7 (one more per beat, capped at 10) + a rising colour wash
    rl = []
    for k in range(10):
        st = 0.44 * k
        y0 = -440 + 880 * ((k * 0.618) % 1)
        pts = []
        for j in range(25):
            u = j / 24
            x = -1150 + 2300 * u if k % 2 == 0 else 1150 - 2300 * u
            y = y0 + (120 + 8 * (k % 5)) * math.sin(6.28 * u * (1.1 + 0.12 * (k % 6)) + k)
            pts.append([r4(st + 0.9 * u), r4(x + 960), r4(y + 540)])
        rl.append(dict(type="canvas", module="ribbon", keepColor=True, params=dict(
            path=pts, colors=[HUE[k % 13], HUE[(k + 5) % 13]], width=20 + 6 * (k % 4), twist=0.6, bloom=0.7, grain=0.9,
            motes=0.35, seed=50 + k)))
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
    js = ("// Section D: drop 2 + \"Anomaly detected\" (112.96-141.00, incl. E3 singing take). Revision 5 (v3 pass).\n"
          "// GENERATED by tools/sections/D/build_timeline.py from media/shots/_D/takes.json: edit those, not this file.\n"
          "// Ghost choreography (clip, freeze/offset, hue, opacity, position) is tabulated in docs/sections/D.md.\n"
          "export default " + json.dumps(sec, indent=1, ensure_ascii=False) + ";\n")
    os.makedirs("render/timeline", exist_ok=True)
    open("render/timeline/D.js", "w").write(js)
    json.dump(to_edl(sec), open(f"{SH}/D_edl.json", "w"), indent=1, ensure_ascii=False)
    json.dump(notes, open(f"{SH}/_D/ghost_table.json", "w"), indent=1, ensure_ascii=False, default=float)
    print("shots", len(sec["shots"]), "overlays", len(sec["overlays"]))
