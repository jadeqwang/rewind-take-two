#!/usr/bin/env python
"""Build section D's engine timeline (render/timeline/D.js) and the EDL mirror (media/shots/D_edl.json).

Section D = drop 2 + "Anomaly detected", 112.96-141.00. Revision 5 (v3 pass, docs/sections/D.md): the restaged chase
from the rev-B level clips (media/shots/B_<take>/take_1*, tools/sections/B/). Rev 5b (Jade's notes on the v3 cut): v2's
opening (E1 + E2a, ghosts 1-3) is restored, then chops 4-8 replay the v3 level as retries and 9-13 build the wall
ladder; "Rewind." #2 climbs that ghost ladder and is hauled onto the roof; the hint is compressed into the slide (the
gold ghost points at the BANACH-TARSKI spine while they slide); the blue ghost boosts her over the swarm, the agents
collide beneath her, she atomizes and splits; the rainbow Jades follow. v4 (docs/revisions/v4/plans/coop.md): E3, the
sung "Rewind.", is out; R1 (the failed climb run backwards) takes the word at 119.44; E4a-E6c sit two bars earlier; the
co-op level C1/C2 (an animatic for now) fills 129.62-134.00. E7's meter insert and E8 still
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

# (not used since v4: E3 was removed; kept for reference)  E3 singing take (rev 5): rev-A's watercolor singer, lip sync baked in: file time 0 = song 119.44, rate 1, no lag
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


def sprite_of(c, freeze, color, matte="matte", scale=1.0, box=None, solo=False):
    """bake (once) the luminous line-art afterimage of clip c at `freeze`; returns (path, stats in design px).
    box = normalised [x0, y0, x1, y1] keeps only that part of the matte (agents out of the ghost).
    solo = keep only the largest blob of the baked sprite (v6, Jade 1:56: an agent's gun hand inside the box)."""
    os.makedirs(SPR, exist_ok=True)
    ol = int(round(min(12, max(4, 3.5 / max(scale, 0.05)))))      # outline/glow survive downscaling for distant ghosts
    tag = os.path.basename(os.path.dirname(c["stem"])) + "_" + os.path.basename(c["stem"])
    if c["eng"].endswith("_back.mp4"):
        tag += "_back"                                  # a repainted plate bakes its own sprite
    bx = "" if not box else "_b" + "-".join(f"{v:g}" for v in box)
    name = f"{tag}_{matte}_{freeze:.3f}_{color.lstrip('#')}_o{ol}{bx}{'_solo' if solo else ''}.png"
    path = f"{SPR}/{name}"
    meta = path[:-4] + ".json"
    if os.path.exists(path) and os.path.exists(meta) and os.path.getmtime(path) > os.path.getmtime(ghostsprite.__file__):
        return path, json.load(open(meta))
    st = ghostsprite.sprite(c["eng"], f"{c['stem']}_{matte}", freeze, color, path, outline=ol, glow=18 * ol / 4, box=box)
    if solo:
        im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        n, lab, cs, _ = cv2.connectedComponentsWithStats((im[..., 3] > 8).astype(np.uint8))
        if n > 2:
            im[..., 3][lab != 1 + int(np.argmax(cs[1:, cv2.CC_STAT_AREA]))] = 0
            cv2.imwrite(path, im)
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
    # v6 (jacket audit, docs/revisions/v6/f2_jacket_back.md): the lawn takes have the orange band taken off the
    # jacket's back (and B_lawn2 the big back dot painted in), tools/jacket_back.py; mattes are unchanged
    eng = stem + ("_engraved_back.mp4" if take in BACK_FIXED else "_engraved.mp4")
    return dict(eng=eng, matte=stem + "_matte/matte.mp4", ghost=stem + "_ghost/matte.mp4",
                live=stem + "_live/matte.mp4", jmatte=stem + "_jmatte/matte.mp4", stem=stem)


BACK_FIXED = ("lawn", "lawn2")


def doubling(id_, c, times_abs, shot_start, shot_dur, in0, rate=1.0, steps=(-4, 6, -2, 1), spacing=20, slot_time=2 / FPS,
             stagger=16, peel=0.3, tint=0.82, opacity=0.9, place=None, src_max=None):
    """Python port of render/timeline/_B_fx.js doubling() with every function sampled into keys (D.js is plain JSON).
    The number of Jades doubles on each time; a new copy starts stacked on its parent (same place, same frame) and
    peels to its own slot in a bar ahead of / behind her: slot q = q*slot_time s of her own clip and q*spacing px.
    Copy n takes HUE[(n-1) % 13]; times before the shot start are already peeled (the bar continues across a cut).
    src_max: a copy's layer ends once its source time passes this (v7: the agents enter the leap take's matte at 2.21;
    the keys sit on a 1/24 grid that is not frame-aligned, so leave a frame of margin)."""
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
        if src_max is not None:
            past = [lt for lt, v in k_in if v + rate * lt > src_max]
            if past:
                L["end"] = past[0]
        if "scale" in place:
            L["scale"] = place["scale"]
        out.append(L)
    return out


LEAP_GIRDER = 720 - 960          # B_leap: the girder's right end (centre-origin x); the beam starts at x 1030, level y 598


_SIL = {}


def silhouette(stem, t, step=4):
    """v7: a matte's silhouette at source time t as point arrays (absolute design px, every step-th pixel; the engine's
    frame pick: floor(t * 24))."""
    fs = sorted(glob.glob(f"{stem}_matte/*.png"))
    i = max(0, min(len(fs) - 1, int(t * FPS + 1e-4)))
    key = (stem, i, step)
    if key not in _SIL:
        m = cv2.imread(fs[i], cv2.IMREAD_GRAYSCALE)
        sx, sy = 1920 / m.shape[1], 1080 / m.shape[0]
        ys, xs = np.nonzero(m[::step, ::step] >= 128)
        _SIL[key] = (xs * step * sx, ys * step * sy)
    return _SIL[key]


def fall_pop(c, tag, col, tint, s0, x0, y0, t0, tm, fall_frames, vx, vy, g, opacity=0.9, R=220, size=30, flashR=95,
             wh=(1920, 1080), th=0.0, spin_t=0.17, pop=True, fade=None):
    """v7: a ghost that has missed, from t0 (the frame before the miss tm; shot-local): frozen in pose s0 (source s) at
    layer offset (x0, y0), it falls (vx, vy px/s, g px/s^2) until the pop at tm + (fall_frames - 1) frames, flashing
    white for the last two frames, and pops at its centroid (ghostpop.js). th (deg): it tumbles about its centroid,
    reaching th after spin_t s (the layer's rotate is about the frame centre, so x/y are compensated). pop=False: no
    blink or pop; it just falls for fall_frames frames, with opacity keys `fade`. Returns (layers, pop layer or None, tp)."""
    dt = 1 / FPS
    tp = r4(tm + (fall_frames - 1) * dt)
    fall = [r4(q * dt) for q in range(fall_frames + 1)]
    st0 = mstats(c["stem"], s0)
    gx, gy = st0["cx"], st0["cy"]                       # the pose's centroid, centre-origin source px
    ang = lambda u: th * min(1.0, u / spin_t)

    def xy(u):                                          # layer x/y at fall time u (rotation about the centroid)
        dx, dy = vx * u, vy * u + 0.5 * g * u * u
        if not th:
            return r4(x0 + dx), r4(y0 + dy)
        a_ = math.radians(ang(u))
        rx = math.cos(a_) * -gx - math.sin(a_) * -gy    # R(a) (C - G), C = the frame centre (0, 0 centre-origin)
        ry = math.sin(a_) * -gx + math.cos(a_) * -gy
        return r4(gx + x0 + rx + dx), r4(gy + y0 + ry + dy)

    def keys(us, shift=0.0):
        k = dict(x=[[r4(u), xy(u + shift)[0]] for u in us], y=[[r4(u), xy(u + shift)[1]] for u in us])
        if th:
            k["rotate"] = [[r4(u), r4(ang(u + shift))] for u in us]
        return k
    common = dict(type="ghosts", src=c["eng"], matte=dict(src=c["matte"], mode="luma"), keepColor=True, fit="cover")
    if not pop:
        L = dict(id=f"drop_{tag}", start=t0, end=r4(t0 + fall_frames * dt), **common, **keys(fall),
                 instances=[dict(freeze=s0, color=col, tint=tint, opacity=opacity)])
        if fade:
            L["opacity"] = fade
        return [L], None, None
    lay = [dict(id=f"fall_{tag}", start=t0, end=tp, **common, **keys(fall),
                instances=[dict(freeze=s0, color=col, tint=tint, opacity=opacity)]),
           dict(id=f"blink_{tag}", start=r4(tp - 2 * dt), end=tp, **common, **keys((0, dt, 2 * dt), tp - 2 * dt - t0),
                instances=[dict(freeze=s0, color="#ffffff", tint=1.0, opacity=0.95, grade=dict(lift="#d6d6d6"))])]
    u = tp - t0
    pop_l = dict(id=f"pop_{tag}", type="canvas", module="ghostpop", keepColor=True, start=tp, params=dict(
        at=0, x=r4(gx + x0 + vx * u + wh[0] / 2), y=r4(gy + y0 + vy * u + 0.5 * g * u * u + wh[1] / 2), color=col,
        dur=0.36, R=R, size=size, flashR=flashR))
    return lay, pop_l, tp


def leap_misses(c, cps, in0, a, miss, fall_frames=5, vx=200.0, g=9000.0):
    """v7: the copies of the E7 leap whose feet come down over the gap between the girder and the beam drop through it
    and pop (Celeste). miss: copy -> "contact" (the first frame her feet are at the beam's level) or n (the first frame on
    that level with her centroid n px past the girder's end). From the frame before the miss she is frozen in that pose
    and falls (vx px/s, g px/s^2, her own descent speed if she was still coming down) for fall_frames frames, flashes
    white for the last two and pops at her centroid. Copies born from a parent that has already died are dropped.
    Returns (layers, pop layers, notes)."""
    lay = {int(L["id"].rsplit("_", 1)[1]): L for L in cps}
    dt = 1 / FPS
    at = lambda keys, lt: min(keys, key=lambda k: abs(k[0] - lt))[1]
    born = lambda L: 0.0 if L["opacity"][0][1] > 0 else L["opacity"][1][0] + 0.01
    src = lambda L, lt: at(L["in"], lt) + lt
    death, out_pops, notes = {}, [], {}
    for n in sorted(lay):
        L = lay[n]
        gen = n.bit_length() - 1
        par = n - (1 << gen)
        if par and par in death and death[par] <= born(L) + 1e-6:
            notes[f"{n:02d} {L['instances'][0]['color']}"] = f"never born (parent copy {par} died at {a + death[par]:.2f})"
            del lay[n]
            continue
        if n not in miss:
            notes[f"{n:02d} {L['instances'][0]['color']}"] = "lands"
            continue
        lts = [k[0] for k in L["in"] if k[0] >= born(L) - 1e-6]
        tm = None
        for lt in lts:
            st = mstats(c["stem"], src(L, lt))
            if not st or st["y1"] < 45:                        # feet not yet at the beam's level (y 585 of 1080)
                continue
            if miss[n] == "contact" or st["cx"] + at(L["x"], lt) > LEAP_GIRDER + miss[n]:
                tm = lt
                break
        t0 = r4(tm - dt)                                        # the pose of the frame before the miss
        s0 = r4(src(L, t0))
        st0, stp = mstats(c["stem"], s0), mstats(c["stem"], src(L, t0 - dt))
        vy = max(250.0, (st0["y1"] - stp["y1"]) * FPS) if stp else 250.0
        col = L["instances"][0]["color"]
        L["end"] = t0
        L["_fall"], pop, tp = fall_pop(c, f"{n:02d}", col, L["instances"][0]["tint"], s0, at(L["x"], t0), at(L["y"], t0),
                                       t0, tm, fall_frames, vx, vy, g)
        out_pops.append(pop)
        death[n] = tp
        cm = mstats(c["stem"], src(L, tm))["cx"] + at(L["x"], tm) + 960
        notes[f"{n:02d} {col}"] = (f"misses the beam at {a + tm:.2f} (centroid x {cm:.0f}, gap 720-1030), "
                                   f"falls from {a + t0:.2f}, pops at {a + tp:.2f}")
    layers = []
    for L in cps:
        n = int(L["id"].rsplit("_", 1)[1])
        if n in lay:
            layers.append(L)
            layers.extend(L.pop("_fall", []))
    return layers, out_pops, notes


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
        path, st = sprite_of(c, frz, HUE[k], "matte", 1.0, box=box, solo=tk == "lawn")   # v6: no ghost gun
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

    # ---------------- E3: removed in v4 (Jade, v3 review at 2:00: "this REWIND singing seems unnecessary") ----------------
    # v3: shot E3_sing 119.44-122.95 = E3_TAKE (in 0, rate 1) under a 1.0 -> 1.08 push on her head (960, 380), seven
    # residue ribbons on an orbit (centre 960,600, radii 780x400, -8 deg) behind an occluder matted by E3_MATTE, and a
    # "Rewind." lower third (ink, size 112, y 1000). The code is in git (commit 2fb9b82). media/sing/E3/ is untouched.
    # v4 plan: docs/revisions/v4/plans/coop.md. Everything from the ghost ladder to the split moves two bars earlier.

    def twin_shot(id_, tk, gname, t0, t1, src_in, rate, g_t0, extra=(), under=(), fx=(), patch=True, g_op=0.9, ghost_stem=None,
                  plate=None):
        """a two-Jade take: the plate, a clean-plate patch where the ghost girl ever is, the ghost girl redrawn as a
        translucent line-art ghost (baked by ghostseq.py from the split matte), the live girl on top, in colour.
        plate = a re-coloured copy of the take for the bg and jade layers (same frames; the mattes stay the take's)."""
        c = dict(bclip(tk), **({"eng": plate} if plate else {}))
        tm = {"in": src_in, "rate": rate}
        return dict(id=id_, start=t0, end=t1, layers=[
            dict(id="bg", type="video", src=c["eng"], **tm),
            *([dict(id="clean", type="image", src=f"{V3}/patch_{gname}.png", fit="cover")] if patch else []),
            *under,
            dict(id="ghost", type="video", src=f"{ghost_stem or V3 + '/ghost_' + gname}_rgb.mp4", keepColor=True, opacity=g_op,
                 matte=dict(src=f"{ghost_stem or V3 + '/ghost_' + gname}_alpha.mp4", mode="luma"), **{"in": r4(src_in - g_t0), "rate": rate}),
            dict(id="jade", type="video", src=c["eng"], matte=dict(src=c["live"], mode="luma"), keepColor=True, **tm),
            *extra], fx=list(fx))

    # ---------------- E4: "Rewind." #2 = up her own ghost ladder, then the gold ghost hauls her onto the roof ----------------
    # rev 5b: no wall boost. She climbs the fire escape through her own five ghosts from E2 (each at its frozen pose,
    # so they are the rungs of a ladder of herself; each brightens as she passes through it) and arrives in ghost 13's
    # pose at the cornice on the cut. climb 3.45 -> 5.95 at x1.75 over 122.95-124.38, same x1.4 framing as E2.
    c = bclip("climb")
    # v4: R1 119.44-119.98 then E4a 119.98-121.30, same 3.45 -> 5.95 of the take (x1.894).  v3: 122.95-124.38 at x1.75
    E4_IN, E4_T0, E4_T1 = 3.45, 119.98, 121.30
    E4_RATE = r4((5.95 - E4_IN) / (E4_T1 - E4_T0))
    # v4: the word is sung at 119.44 (word:rewind#3) and painted from R1 on.  v3: times=["word:rewind#4"] (123.00)
    word = dict(type="canvas", module="pin", keepColor=True, blend="multiply", params=dict(
        style="ground", font="fell", text="Rewind.", times=["word:rewind#3"], size=170, color="#E07A14", grain=0.25,
        corners=E4_WORD))
    # ---- R1 (v4, new): on the held "Rewind." #1 the climb that just failed un-happens. Same wall framing; she runs
    # backwards from ghost 13's pose (5.85, where E2 9-13 froze her) down to 3.45 in 0.54 s (about x4.4 in reverse)
    # under the VHS search look and the Drop 1 rewind HUD. The five ghosts stay (a rewind leaves its ghosts); 11 and
    # 12, which stepped aside in E2, slide back to their frozen poses, so the ladder is whole when she turns round.
    R1_T0, R1_T1, R1_FROM = 119.44, 119.98, 5.85
    r1d = r4(R1_T1 - R1_T0)
    r1T = [[0, R1_FROM], [r1d, E4_IN]]
    r1_rungs = []
    for j, (k, path, frz) in enumerate(ladder):
        dx, dy = CL[j][2]
        tp = (R1_FROM - frz) / (R1_FROM - E4_IN) * r1d      # shot time she passes back through this pose
        op = [[0, 0.85]] + ([[r4(max(0.0, tp - 0.06)), 0.85], [r4(tp), 1.0], [r4(tp + 0.2), 0.75]] if 0.06 < tp < r1d else [[r1d, 0.75]])
        g = dict(id=f"rung{k + 1}", type="image", src=path, keepColor=True, fit="cover", scale=SC, x=PL["x"], y=PL["y"], opacity=op)
        if dx or dy:
            g["x"] = [[0, PL["x"] + dx, "inOutCubic"], [r4(r1d - 0.08), PL["x"]]]
            g["y"] = [[0, PL["y"] + dy, "inOutCubic"], [r4(r1d - 0.08), PL["y"]]]
        r1_rungs.append(g)
    shots.append(dict(id="R1_unclimb", start=R1_T0, end=R1_T1, layers=[
        dict(id="bg", type="video", src=c["eng"], srcTime=r1T, **PL),
        word, *r1_rungs,
        dict(id="jade", type="video", src=c["eng"], matte=dict(src=c["matte"], mode="luma"), keepColor=True, srcTime=r1T, **PL),
        # the Drop 1 rewind HUD on a paper chip (as the GHOSTS counter's chip), so it reads over the dark cornice
        dict(type="solid", stage="post", color=PAPER, opacity=0.88, rect=[40, 56, 236, 84]),
        dict(type="canvas", module="hud", stage="post", params=dict(mode="rewind", x=40, y=120, color=INK, accent="#F08A24",
                                                                   multiplier=4, steady=True))],
        # the word's flash, softened so the first frame is not washed out (v4 first pass: amount 0.5, as v3's E4a)
        fx=[dict(type="flash", at=[0], dur=0.1, amount=0.22, color="#ffffff"),
            dict(type="rewind", amount=[[0, 0.85], [r4(r1d - 0.1), 0.85], [r1d, 0]])]))
    notes["R1"] = dict(clip=c["eng"], srcTime=r1T, what="the failed climb runs backwards on 'Rewind.' #1; ghosts 11/12 slide home")
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
        # v4: the word's flash moved to R1; here a small flash on the bar line where she turns forwards again.
        # v3: dict(type="flash", at=["word:rewind#4"], dur=0.12, amount=0.5, color="#ffffff")
        fx=[dict(type="flash", at=[0], dur=0.06, amount=0.35, color="#8DB8E8"),
            dict(type="punch", on="beat", amount=0.02)]))
    shots[-1]["layers"][-1]["params"].pop("path")
    notes["E4a"] = dict(clip=c["eng"], in_=E4_IN, rate=E4_RATE, rungs="ghosts 9-13 at their frozen poses")
    # v4: 121.30-123.00 at x1.43 (the same 0.05 -> 2.48 of the take).  v3: 124.38, 126.25, 0.05, 1.3
    E4B_T0, E4B_T1, E4B_RATE = 121.30, 123.00, 1.43
    # v6 (eraser audit, docs/revisions/v6/o2_erasers.md): the take drew both bun erasers pink; *_blue = the live (climbing)
    # Jade's right-hand eraser recoloured pale blue in every frame (tools/blue_eraser.py). The gold ghost is baked separately.
    shots.append(twin_shot("E4b_haul", "haul_b", "haul", E4B_T0, E4B_T1, 0.05, E4B_RATE, 0.0,
                           plate=f"{SH}/B_haul_b/take_1_engraved_blue.mp4",
                           fx=[dict(type="flash", at=[0], dur=0.06, amount=0.35, color="#ffffff"),
                               dict(type="punch", on="beat", amount=0.02)]))
    notes["E4b"] = dict(clip=bclip("haul_b")["eng"], ghost="girl lying on the roof, gold #C9A227", in_=0.05, rate=E4B_RATE)

    # ---------------- E5 (rev 5b): the hint while sliding. slide_point: hand in hand down the giant book (Escher, Still
    # Life and Street); the leading girl (gold ghost) points at the blank label on the spine of the upright book at
    # frame right, which reads BANACH–/TARSKI. Locked-off camera: the label stays at 1507-1690 x 211-362 (tracked, no
    # drift). in 0.8 at x1.4: they leave the book's bottom edge on the cut.
    # rev 5b (Jade: "they should turn to look at what she's pointing at"): the retake slide_point_b, where both girls turn
    # their heads to the label while the gold ghost points. The camera is locked (label tracked: 1513-1697 x 208-358,
    # no drift). The engrave left black blots on the white cover: the cover's flat interior is laid from the nano clean
    # plate (inset from its edges, which nano redrew) under both girls. Split: splitpair.py on the colour-gated matte.
    lab = dict(id="label", type="canvas", module="pin", blend="multiply", params=dict(
        style="plain", font="fell", text="BANACH–\nTARSKI", size=96, color=INK, padding=4,
        corners=[1523, 222, 1687, 222, 1687, 345, 1523, 345]))
    cover = dict(id="cover", type="image", src=f"{V3}/patch_slideptb_cover.png", fit="cover")
    # v4: 123.00-125.26 at x1.52 (the same 0.9 -> 4.34 of the take), under "Rewind." #2, which is not lettered here.
    # v3: 126.25, 128.76, 0.9, 1.37
    E5_T0, E5_T1, E5_RATE = 123.00, 125.26, 1.52
    # v4 (Jade: "gold ethereal jade's arm pointing to Banach Tarski goes invisible for a moment"): the engrave matte lost
    # her pointing forearm and hand on take frames ~25-86, so the clean patch showed through. Re-segmented with BiRefNet
    # on a crop (tools/v4B/coop/armfix.py) and rebaked with ghostseq.py (same colour, times and parameters as v3).
    # v3: ghost from media/shots/_D/v3/ghost_slideptb_{rgb,alpha}.mp4
    # v6 (Jade, 2:03: "ethereal gold Jade's butt is opaque for a split second and protagonist Jade's sneaker is partly
    # erased"): the split gave the gold girl's left leg to the live matte on take frames 19-39 (painted opaque navy) and
    # the live matte had lost her sneaker soles (and a trouser patch on 45-49), so the cover showed through.
    # tools/v4B/coop/e5feet.py moves the leg to the ghost matte and puts the soles back (BiRefNet); ghost rebaked with
    # ghostseq.py (same colour, times and parameters). v4: ghost_slideptb_v4, jade matte take_1_live/matte.mp4
    shots.append(twin_shot("E5_slide_point", "slide_point_b", "slideptb", E5_T0, E5_T1, 0.9, E5_RATE, 0.85, under=[cover, lab],
                           ghost_stem=f"{SH}/C_coop/e5_arm/ghost_slideptb_v6",
                           fx=[dict(type="flash", at=[0], dur=0.06, amount=0.35, color="#ffffff")]))
    shots[-1]["layers"][-1]["matte"]["src"] = f"{SH}/C_coop/e5_arm/live_v6/matte.mp4"
    notes["E5"] = dict(clip=bclip("slide_point_b")["eng"], ghost="leading (pointing) girl, gold", in_=0.9, rate=E5_RATE,
                       label="BANACH–/TARSKI pinned on the upright book's spine label; both girls turn to look at it")

    # ---------------- E6 (rev 5b): swarm boost, atomize, two Jades ----------------
    # swarm_boost at x1.14 from 0.315: the kneeling girl (blue ghost; baked opaque by ghostfill.py, because the agents
    # pile through her and a static clean plate would erase them) heaves from 129.15 and her foot leaves the hands at
    # source 1.77 = 130.04 (beat); the agents from both sides crash into each other beneath her at source 2.80 = 130.94
    # (beat); she hangs at the peak to the freeze at source 3.30 (frame 79) = 131.38.
    E6_IN, E6_RATE = 0.315, 1.14
    # v4: the whole E6 block two bars earlier, same in-point and rate: 125.26-127.88, launch 126.56 (beat), collision
    # 127.44 (beat), freeze 127.88.  v3: 128.76-131.38, launch 130.04, collision 130.94, freeze 131.38
    E6_T0, E6_T1 = 125.26, 127.88
    E6_HIT = r4(E6_T0 + 2.18)                            # the collision, 2.18 s into the shot as in v3
    shots.append(twin_shot("E6a_swarm", "swarm_boost", "swarm", E6_T0, E6_T1, E6_IN, E6_RATE, 0.3, patch=False, g_op=0.95,
                           fx=[dict(type="flash", at=[0], dur=0.06, amount=0.35, color="#ffffff"),
                               dict(type="punch", at=[r4(E6_HIT - E6_T0)], amount=0.05, decay=0.14),
                               dict(type="shake", at=[r4(E6_HIT - E6_T0)], amp=10, decay=0.2)]))
    notes["E6a"] = dict(clip=bclip("swarm_boost")["eng"], ghost="kneeling girl, blue #3E6FD8 (opaque fill)", in_=E6_IN, rate=E6_RATE,
                        launch=r4(E6_T0 + (1.77 - E6_IN) / E6_RATE), collision=E6_HIT)
    # 131.38 (source 3.30, frame 79): freeze + flash; she bursts into 150 motes in mid-air over the frozen heap
    BX, BY = -8, -272
    E6B_T0, E6B_T1 = 127.88, 128.32                      # v3: 131.38, 131.82
    shots.append(dict(id="E6b_atomize", start=E6B_T0, end=E6B_T1, layers=[
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
    # v4 (Jade: "tag them at the moment of split"): from here on the left twin is ORANGE (orange band, straps, dots) and
    # the right twin is BLUE (blue band, straps, headphones, dots). Same take, recoloured by screen half:
    #   tools/engrave/.venv/bin/python tools/v4B/coop/recolor.py media/shots/B_two/take_1_engraved.mp4 \
    #       media/shots/C_coop/two_bo/take_1_engraved_bo.mp4 --split=960
    # v3: the take as engraved (c["eng"] = media/shots/B_two/take_1_engraved.mp4), both twins orange
    c = dict(c, eng=f"{SH}/C_coop/two_bo/take_1_engraved_bo.mp4")
    LX, RX_, GY = -269, 307, 108
    imp = lambda x, seed: dict(type="canvas", module="motes", keepColor=True, end=0.44, time=[[0, 0.44], [0.44, 0.0]], params=dict(
        at=0, x=x + 960, y=GY + 540, count=110, colors=RES + ["#ffffff"], speed=1300, drag=2.2, size=16, life=2.0, ring=False,
        glow=0.9, seed=seed))
    run = lambda s: 0.44 + (s - 0.55)        # source s -> shot time
    # her own path (read off the frames): off the mark at 0.6, out of the frame edge by about 1.05
    rib_l = [[r4(run(s)), r4(LX - 1000 * max(0.0, s - 0.6) / 0.45), r4(GY + 10 + 30 * math.sin(9 * s))] for s in [0.58 + 0.04 * q for q in range(16)]]
    rib_r = [[r4(run(s)), r4(RX_ + 1000 * max(0.0, s - 0.6) / 0.45), r4(GY + 10 + 30 * math.cos(9 * s))] for s in [0.58 + 0.04 * q for q in range(16)]]
    # v4: 128.32-129.18: implode 0.44 s, the sprint on the 128.76 bar line, cut one beat later as they leave frame (the
    # v3 tail of dazed agents is trimmed; the co-op level takes 129.18-134.88).  v3: start=131.82, end=134.00, sprint
    # on 132.26.  (v4 first pass ended at 129.62 and left 0.3 s of the heap alone.)
    E6C_T0, E6C_T1 = 128.32, 129.18
    shots.append(dict(id="E6c_two", start=E6C_T0, end=E6C_T1, layers=[
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

    # ---------------- C1, C2 (v4): the co-op level, 129.18-134.88 (Jade approved the storyboard with changes: the
    # twins are BLUE and ORANGE by costume, no tags; the world, the bridge and the buttons stay black and white).
    # A gap between two tables; a giant pencil is the drawbridge, hinged at the right lip; it is down only while a
    # floor button is held. ORANGE holds, BLUE crosses; BLUE holds, ORANGE crosses with the agents behind her; BLUE
    # lets go, the bridge swings up away from the agents, who are left at the lip.
    # Built from two Seedance takes (media/shots/C_coop/NOTES.md) over the clean plate: each girl from her own matte
    # (tools/v4B/coop/level.py: seam per frame, BLUE recoloured), the agents from their own matte, the pencil and the
    # buttons as sprites cut from the take (assets.py), so the engine can raise the bridge and sink the buttons.
    # v4 first pass: an animatic of storyboard panels 2-9 here (media/shots/C_coop/animatic/).
    CO = f"{SH}/C_coop"
    # v4 phase 3 (Jade: "part of the pencil bridge mechanism is missing", "maybe the pencil bridge can lift the other way
    # up"): the hinge is at the NEAR lip with a drawn iron bracket (tools/v4B/coop/hinge.py); raised = the point end up.
    # phase 2: UP = 72 about a hinge at the far lip (1185, 632), no bracket
    UP = -78                                               # bridge raised (deg; negative = counter-clockwise)
    HX, HY = 700, 634                                      # hinge, design px
    SINK = 18                                              # a held button (and the girl on it) drops this far

    def pencil(rot):
        return dict(id="pencil", type="image", src=f"{CO}/pencil.png", fit="cover", anchor=[r4(HX / 1920), r4(HY / 1080)],
                    x=HX - 960, y=HY - 540, rotate=rot)

    def btn(side, yk):
        return [dict(id=f"btn_{side}", type="image", src=f"{CO}/btn_{side}.png", fit="cover", y=yk),
                dict(id=f"strip_{side}", type="image", src=f"{CO}/patch_strip_{side}.png", fit="cover")]

    def girl(id_, take, side, sT, yk, start=None):
        L = dict(id=id_, type="video", src=f"{CO}/{take}_bo.mp4", keepColor=True, srcTime=sT, y=yk,
                 matte=dict(src=f"{CO}/{take}_{side}.mp4", mode="luma"))
        if start is not None:
            L["start"] = start
        return L

    def agents(take, sT, start=None):
        L = dict(id="agents", type="video", src=f"{CO}/{take}_bo.mp4", srcTime=sT, matte=dict(src=f"{CO}/{take}_ag.mp4", mode="luma"))
        if start is not None:
            L["start"] = start
        return L

    # v4 phase 3 (Jade: "agents look frozen instead of reacting to the pencil bridge", "the agents then get thrown back"):
    # the agents are one Seedance take of their own on blank paper (media/shots/C_coop/agents/, matte by
    # tools/v4B/coop/agents.py), one continuous layer across C1-C2b placed by song-time keys: they run in behind ORANGE
    # (131.38), lunge where she was (132.70), run out onto the bridge after her, and at 134.00, when BLUE lets go and the
    # far end lifts, the take's springboard throw flings them back over the hinge onto the near desk, where they land
    # (134.44) and sit up, dazed. Nobody falls into the gap.
    AG_T = [[131.38, 0.5], [131.60, 0.15], [131.82, 0.5], [132.04, 0.15], [132.26, 0.0], [134.00, 2.3], [134.88, 4.5]]
    AG_X = [[131.38, -1600, "outCubic"], [132.26, -872], [132.70, -472], [134.00, -57, "outCubic"], [134.44, -537]]
    AG_Y = [[131.38, -121], [132.70, -121], [132.85, -161], [134.00, -161, "inOutCubic"], [134.44, -111]]

    def agents_v4(t0, start=None):
        sh = lambda K: [[r4(k[0] - t0), *k[1:]] for k in K]
        L = dict(id="agents", type="video", src=f"{CO}/agents/take_1.mp4", fit="cover", scale=0.5, srcTime=sh(AG_T),
                 x=sh(AG_X), y=sh(AG_Y), matte=dict(src=f"{CO}/agents/take_1_matte.mp4", mode="luma"))
        if start is not None:
            L["start"] = start
        return L

    def level(id_, a, b, layers, fx):
        shots.append(dict(id=id_, start=a, end=b, layers=[
            dict(id="plate", type="image", src=f"{CO}/plate.png", fit="cover"), *layers[0],
            dict(id="tail", type="image", src=f"{CO}/patch_tail.png", fit="cover"),
            dict(id="hinge", type="image", src=f"{CO}/hinge.png", fit="cover"), *layers[1]], fx=fx))

    held = lambda t_on, t_off=None: ([[0, 0, "hold"], [r4(t_on), SINK]] if t_on is not None else [[0, SINK, "hold"]]) + \
        ([[r4(t_off), 0]] if t_off is not None else [])
    # C1 129.18-132.26: take c1/take_2. 129.18 both run in, the bridge is up; 130.50 (bar) ORANGE lands on the near
    # button, it sinks, the bridge swings down (lands 130.80); BLUE waits at the lip; 130.94 she crosses; 131.38 the
    # agents walk in behind ORANGE (their own matte from c1/take_1); ~132.1 BLUE crouches on the far button.
    C1T = [[0, 0.4], [1.32, 1.65], [1.76, 3.05], [2.64, 4.0], [3.08, 4.5]]
    level("C1_hold", 129.18, 132.26, (
        [pencil([[0, UP, "hold"], [1.32, UP, "inCubic"], [1.62, 0]]), *btn("l", held(1.34)), *btn("r", held(2.92))],
        # the agents of C2's first frames run in from the left edge (their legs cycle on a ping-pong of take 0.15-0.45
        # while they slide in), arriving exactly where C2a picks them up
        [agents_v4(129.18, start=2.20),
         girl("blue", "c1t2", "R", C1T, held(2.92)), girl("orange", "c1t2", "L", C1T, held(1.34))]),
        fx=[dict(type="flash", at=[0], dur=0.06, amount=0.35, color="#ffffff"), dict(type="punch", at=[1.34, 2.92], amount=0.025),
            dict(type="shake", at=[1.62], amp=6, decay=0.15)])
    # C2a 132.26-133.56: take c2/take_1 0-1.9 (x1.46). BLUE holds the far button; ORANGE springs off the near one (it
    # pops up, the bridge stays down: BLUE still holds), the agents' hands close on air (~132.77) and they stop at the
    # lip (their matte frozen at take 1.1; in the take they dive into the gap, which is never shown).
    # v6 (Jade, 2:13: "a few frames where a larger agent's head is visible"): ORANGE's matte held the take's own leading
    # agent (head and arm, at twice the agents layer's scale) on take frames 17-28 and 37-38 (132.71-133.04, 133.33); "Lc" is
    # her matte with him erased (tools/v4B/coop/unleak.py). The agents layer itself was never the cause; it is unchanged.
    C2T = [[0, 0.15], [1.30, 1.9]]
    level("C2a_swap", 132.26, 133.56, (
        [pencil(0), *btn("l", held(None, 0.20)), *btn("r", held(None))],
        [agents_v4(132.26),
         girl("blue", "c2t1", "R", C2T, held(None)), girl("orange", "c2t1", "Lc", C2T, held(None, 0.20))]),
        fx=[dict(type="punch", at=[0.20], amount=0.02)])
    # C2b 133.56-134.88: take c2/take_1 3.56-4.88 (jump cut over the landing; ORANGE stays the girl on the left).
    # 134.00 (bar) BLUE hops off, the far button pops up and the bridge swings up out of the agents' reach; 134.44
    # both run on, out of frame right; cut to E7 on 134.88.
    # v6 (Jade, 2:13-14: "part of the tip of the pencil is detached and visible"): the take's flat pencil point rode in
    # the left girl's matte on take frames 106-108 (134.417-134.500) while the pencil sprite is raised; "Lc" erases it.
    C2BT = [[0, 3.56], [1.32, 4.88]]
    level("C2b_letgo", 133.56, 134.88, (
        [pencil([[0, 0, "hold"], [0.44, 0, "outCubic"], [0.64, UP]]), *btn("l", 0), *btn("r", held(None, 0.46))],
        [agents_v4(133.56),
         girl("blue", "c2t1", "R", C2BT, 0), girl("orange", "c2t1", "Lc", C2BT, 0)]),
        # v4 (coordinator: "a visible double exposure ... make it a hard cut on the beat"): the white flash on the cut
        # washed both frames together; the cut is now plain. phase 2/3: flash at 0, dur 0.05, amount 0.3
        fx=[dict(type="punch", at=[0.44], amount=0.03)])
    notes["C_coop"] = dict(takes=["media/shots/C_coop/c1/take_2.mp4", "media/shots/C_coop/c2/take_1.mp4"], hinge=[HX, HY], up=UP,
                           beats=dict(press1=130.50, bridge_down=130.80, cross=130.94, agents=131.38, cut=132.26, orange_off=132.46,
                                      jump_cut=133.56, let_go=134.00, run=134.44))

    # ---------------- E7: the rainbow Jades, after the split. Doubling on every beat 134.88-136.19 ----------------
    # v4 (Jade: "cutting a little bit of stopwatch is fine to make space for co-op"): the stopwatch insert E7_03_meter
    # (135.76-136.62) is out, the platform and the leap sit two beats later and the co-op level runs to 134.88. The
    # chasm, the earpiece and the lawn (136.62-139.00) are where v3 had them.
    # v3: DB = [134.00, 134.44, 134.88, 135.32]; E7_01_plat 134.00-134.88, E7_02_leap 134.88-135.76, E7_03_meter 135.76-136.62
    E7_T0 = 134.88
    DB = [134.88, 135.32, 135.76, 136.19]

    def e7(id_, a, b, layers, fx=()):
        shots.append(dict(id=id_, start=a, end=b, layers=layers, fx=[dict(type="flash", at=[0], dur=0.05, amount=0.25, color="#ffffff"),
                                                                    dict(type="punch", at=[0], amount=0.04)] + list(fx)))
    # v4: the pair that leaves the co-op level is ORANGE (the untinted Jade here) and BLUE, so the first copy is the
    # blue one and the second the orange one (v3: copy 1 orange, copy 2 blue).
    # v7 (Jade on the v6 cut, 2:16: "some of the ghosts whose feet didn't land on the beam should fall through and not
    # make it ('pop' Celeste style)"; docs/revisions/v7/ghost_pop.md): the leap take's beam starts at x 1030 and the
    # girder of the platform she jumps from ends at x 720 (design px), so every copy peeled 4+ slots (300 px) behind her
    # lands in that gap. Copy 1 (slot -4) comes down with both feet over the gap at 136.01, and copy 13 (slot -5, born on
    # the girder's lip at 136.19) slips off it as it peels. They drop through and pop (ghostpop.js); copy 9, copy 1's
    # child at 136.19, is never born. BLUE (the co-op partner) must make it, so in the leap the gold and blue copies
    # trade places (blue takes copy 3's slot +2, on the beam ahead of her; gold takes copy 1's slot and falls), and copy
    # 15 (a second blue until v6) is violet, so the chasm's five survivors (orange, blue, magenta, green, violet) are all
    # on the beam at the cut. (Gold and lime fly again in the chasm: Jade wants the whole v6 swarm in the air there.)
    DBL_COLORS = dict(plat={1: HUE[1], 2: HUE[0]}, leap={1: HUE[2], 2: HUE[0], 3: HUE[1], 15: HUE[8]})
    LEAP_MISS = {1: "contact", 13: 40}       # copy -> "contact" (first frame on the beam's level) or px past the girder end
    for (id_, tk, a, b, in0, sp) in (("E7_01_plat", "plat", 134.88, 135.76, 0.55, 30), ("E7_02_leap", "leap", 135.76, 136.62, 0.85, 75)):
        c = bclip(tk)
        cps = doubling("dbl", c, DB, a, b - a, in0, spacing=sp, stagger=22, src_max=2.15 if tk == "leap" else None)
        for L_ in cps:
            n_ = int(L_["id"].rsplit("_", 1)[1])
            if n_ in DBL_COLORS[tk]:
                L_["instances"][0]["color"] = DBL_COLORS[tk][n_]
        pops = []
        if tk == "leap":
            cps, pops, notes["E7_leap"] = leap_misses(c, cps, in0, a, LEAP_MISS)
        e7(id_, a, b, [dict(id="bg", type="video", src=c["eng"], **{"in": in0, "rate": 1.0}), *cps, *pops,
                       dict(id="jade", type="video", src=c["eng"], matte=dict(src=c["matte"], mode="luma"), keepColor=True,
                            **{"in": in0, "rate": 1.0})],
           fx=[dict(type="flash", at=[r4(t - a) for t in DB if a <= t < b], dur=0.05, amount=0.12)])
    # v3: the stopwatch insert, removed in v4:
    #   m = take["e7_cuts"][1]; c = C["e7_meter"]
    #   e7("E7_03_meter", 135.76, 136.62, [dict(id="meter", type="video", src=c["eng"], **{"in": m["in"], "rate": m["rate"]})],
    #      fx=[dict(type="shake", at=[0], amp=12, decay=0.3)])
    # HILBERT on the hotel's rooftop billboard (rev 5b): rev-A's woodcut lettering, as their 0:24 sign (render/timeline/A.js
    # D2: Anton 'slab' capitals, ink on the lit panel, hatch .3, no flecks), corner-pinned, solid from the first frame
    # (`at` before the shot). Corners as the Verse 2 agent's (render/timeline/_B_verse2.js BB); the chasm plate draws
    # the panel hatched dark, so its lit face is painted first.
    WOODCUT = "tools/sectionA/modules/woodcut.js"
    BB = dict(chasm=[1626, 106, 1818, 22, 1820, 96, 1627, 161], lawn=[1621, 107, 1811, 27, 1812, 100, 1621, 167],
              ear=[1621, 108, 1811, 26, 1811, 97, 1622, 164])

    def hilbert(corners, face=False):
        return ([dict(id="bb_face", type="canvas", module="render/timeline/_B_quad.js", params=dict(corners=corners, color="#efe7da"))]
                if face else []) + [dict(id="hilbert", type="canvas", module=WOODCUT, params=dict(
                    # v4 (Jade: "HILBERT HOTEL (missing HOTEL on a blank sign above)"): one panel on these plates, so HOTEL
                    # is a second line (tools/v4B/gunfire/hotel_corners_D.json). v3: text "HILBERT", box [420, 140]
                    text="HILBERT\nHOTEL", at=-1, color=INK, flecks=0, hatch=0.15, box=[420, 230], pad=8, corners=corners))]

    # chasm (rev 5b): the Super Meat Boy replay. Fifteen copies leave the beam stacked on her and fan into separate arcs;
    # most don't make it: ten lose ground and sag below the ledge (v7: then fall through the gap or down the brick face
    # and pop, see SHORT below). Five survive and land behind the real (untinted) Jade on the wall top.
    # (docs/revisions/B_research_games.md, Super Meat Boy 4-5)
    c = bclip("chasm_dash")
    a, b, in0, rate = 136.62, 137.50, 1.1, 2.0
    d = b - a
    lts = [q / 24 for q in range(int(round(d * 24)) + 1)]
    ss = lambda x: x * x * (3 - 2 * x)

    SURV = [1, 2, 4, 5, 9]                          # orange, blue, magenta, green, violet
    # v6: FALL = {3: .34, 7: .40, 8: .46, 11: .52, 13: .58, 15: .64} (froze and dropped, fading), CLIP = [6, 10, 12, 14]
    # (ended on the wall face in a mote burst). The ten sagged linearly from frame 0 (y + A*u), which pushed their feet
    # into the beam at take-off and sank the back three (13 lime, 14 orange, 15 blue) through the beam end.
    # v7 (Jade on the v7 preview: every airborne ghost back; a gravity curve so they rise with the swarm and then fall
    # into the gap clear of the beam end, never through it; about four readable pops, the others drop out of the gap as
    # in v6; nothing passes through the beam or the wall):
    #  - flight: each copy's sag starts at its own take-off (her source 1.35 s; the copies run 0.02k s behind her) and
    #    follows a gravity curve, y + A*s^p; drift back -D*u as v6. (p, D and A multipliers) per copy in CH below;
    #  - solid: the beam (top y 597, ends x 780) and the far wall's near top edge (corner 1010,520, slope .62; canon
    #    Jade's feet land at y 733 against 738). A silhouette is through the beam if any of it is more than 15 px below
    #    the beam top while over the beam; through the wall if it straddles that edge right of x 1010 (the brick face is
    #    the near side of a cliff facing the gap, so a ghost wholly below the edge is falling in front of it);
    #  - miss: the first frame she is coming down with her feet below the ledge; from the frame before, she is frozen
    #    and falls (knock-back vx, g 9000) tumbling toward upright about her centroid (th, over 0.17 s); the first
    #    (th, vx) whose whole fall is clean is used. Pops: 5-frame fall, white blink, ghostpop. Drops: fall to the cut
    #    with v6's fade. Every flight and fall is checked here and the build fails if one is not clean.
    SHORT = [3, 6, 7, 8, 10, 11, 12, 13, 14, 15]
    CH = {12: (1.5, 0.3, 2.0, "pop"), 6: (1.5, 1.0, 2.0, "pop"), 7: (2.0, 1.0, 1.5, "pop"), 8: (2.0, 1.0, 1.0, "pop"),
          3: (2.0, 2.0, 1.25, "drop"), 10: (2.0, 0.6, 1.0, "drop"), 11: (2.0, 0.6, 1.0, "drop"),
          13: (2.0, 0.6, 1.0, "drop"), 14: (2.0, 0.3, 1.0, "drop"), 15: (2.0, 0.3, 1.0, "drop")}
    TAKEOFF = 1.35                                  # her feet leave the beam (source s)
    LAST = (math.ceil(b * FPS - 1e-6) - 1) / FPS - a                          # the shot's last frame, local
    diag = lambda X: 520 + (X - 1010) * 0.62                                  # absolute design px
    below = lambda X, Y: Y > (520 if X < 1010 else diag(X))

    def through(X, Y, tol=15):
        beam = bool(np.any((X < 780) & (Y > 597 + tol)))
        w = X > 1010
        wall = bool(np.any(w & (Y > diag(X) + tol)) and np.any(w & (Y < diag(X) - tol)))
        return beam, wall

    def tumble(X, Y, cx, cy, deg):
        c_, s_ = math.cos(math.radians(deg)), math.sin(math.radians(deg))
        return cx + c_ * (X - cx) - s_ * (Y - cy), cy + s_ * (X - cx) + c_ * (Y - cy)

    def fall_clean(X0, Y0, vx, vy, th, t0, t1):
        cx, cy = X0.mean(), Y0.mean()
        for q in range(1, 40):
            u = q / FPS
            if t0 + u > t1 + 1e-6:
                return True
            X, Y = tumble(X0, Y0, cx, cy, th * min(1.0, u / 0.17))
            X, Y = X + vx * u, Y + vy * u + 4500 * u * u
            if Y.min() > 1080:
                return True
            if any(through(X, Y)):
                return False
        return True

    back, front, bursts, fates = [], [], [], {}
    for k in range(1, 16):
        col = HUE[(k - 1) % 13]
        base = dict(type="ghosts", src=c["eng"], matte=dict(src=c["matte"], mode="luma"), keepColor=True, loop=False, fit="cover",
                    **{"in": in0, "rate": rate})
        if k in SURV:
            j = SURV.index(k)
            off = -0.025 * (j + 1)
            A = [-300, -170, -60, -380, 90][j]       # survivors fan up and converge on the far lip
            # v7: violet (the one survivor that flies lower than her, A > 0) dipped into the beam at take-off; its dip
            # now starts at its own take-off
            to = (TAKEOFF - in0 - off) / rate if A > 0 else 0.0
            sv = lambda lt, to=to: min(1.0, max(0.0, (lt - to) / (0.86 - to)))
            xo = lambda lt, j=j: -70 * (j + 1) * ss(min(1.0, lt / 0.86))
            yo = lambda lt, j=j, A=A, sv=sv: A * math.sin(math.pi * sv(lt)) - 14 * (j + 1) * ss(min(1.0, lt / 0.86))
            for t in lts:
                if t <= LAST + 1e-6:
                    X, Y = silhouette(c["stem"], in0 + rate * t + off)
                    assert not any(through(X + xo(t), Y + yo(t))), f"survivor {k} passes through at {t:.3f}"
            front.append(dict(id=f"surv{k:02d}", **base, x=[[r4(t), r4(xo(t))] for t in lts], y=[[r4(t), r4(yo(t))] for t in lts],
                              instances=[dict(offset=r4(off), color=col, tint=0.82, opacity=0.88)], opacity=[[0, 0.7], [0.08, 1.0]]))
            fates[k] = "lands"
            continue
        off = -0.02 * k
        rk = SHORT.index(k)
        p_, dm, am, fate = CH[k]
        A = (230 + 48 * rk) * am                  # each a lower, shorter arc than hers: sags below her ...
        D = (140 + 50 * rk) * dm                  # ... and loses ground
        to = (TAKEOFF - in0 - off) / rate
        xo = lambda lt, D=D: -D * min(lt, 0.86) / 0.86
        yo = lambda lt, A=A, to=to, p_=p_: A * min(1.0, max(0.0, (lt - to) / (0.86 - to))) ** p_
        sil = lambda lt: (lambda XY: (XY[0] + xo(lt), XY[1] + yo(lt)))(silhouette(c["stem"], in0 + rate * lt + off))
        found, prev = None, None
        for t in lts[1:]:
            X, Y = sil(t)
            assert not any(through(X, Y)), f"copy {k} passes through in flight at {t:.3f}"
            cx, cy = X.mean(), Y.mean()
            if prev is not None and cy > prev and below(cx, Y.max()):
                t0 = t - 1 / FPS
                X0, Y0 = sil(t0)
                vy = max(250.0, (cy - prev) * FPS)
                t1 = min(LAST, t0 + 5 / FPS) if fate == "pop" else LAST
                for th in (0, -30, -50, -70, 30, 50):
                    for vx in (0, 160, -200, 320, -350):
                        if fall_clean(X0, Y0, vx, vy, th, t0, t1):
                            found = (t, t0, vx, vy, th, cx, cy)
                            break
                    if found:
                        break
                if found:
                    break
            prev = cy
        assert found, f"copy {k}: no clean miss"
        tm, t0, vx, vy, th, cx, cy = found
        tm, t0 = r4(tm), r4(t0)
        back.append(dict(id=f"miss{k:02d}", **base, end=t0, x=[[r4(t), r4(xo(t))] for t in lts if t <= t0 + 0.05],
                         y=[[r4(t), r4(yo(t))] for t in lts if t <= t0 + 0.05],
                         instances=[dict(offset=r4(off), color=col, tint=0.82, opacity=0.85)]))
        where = "over the gap" if cx < 1010 else "at the brick face"
        if fate == "pop":
            lay, pop, tp = fall_pop(c, f"{k:02d}", col, 0.82, r4(in0 + rate * t0 + off), r4(xo(t0)), r4(yo(t0)), t0, tm, 5,
                                    vx, vy, 9000.0, opacity=0.85, R=170, size=24, flashR=60, th=th)
            back += lay
            bursts.append(pop)
            fates[k] = (f"comes down short at {a + tm:.2f} ({where}, centroid {cx:.0f},{cy:.0f}), falls from {a + t0:.2f} "
                        f"(knock-back {vx:.0f} px/s, tumbles {th:.0f} deg), pops at {a + tp:.2f}")
        else:
            nf = int(round((d - t0) * FPS)) + 1
            lay, _, _ = fall_pop(c, f"{k:02d}", col, 0.82, r4(in0 + rate * t0 + off), r4(xo(t0)), r4(yo(t0)), t0, tm, nf,
                                 vx, vy, 9000.0, opacity=0.85, th=th, pop=False, fade=[[0, 1.0], [0.18, 0.85], [0.42, 0.0]])
            back += lay
            fates[k] = (f"comes down short at {a + tm:.2f} ({where}, centroid {cx:.0f},{cy:.0f}), drops out of the gap from "
                        f"{a + t0:.2f} (knock-back {vx:.0f} px/s, tumbles {th:.0f} deg), no pop")
    notes["E7_chasm"] = {f"{k:02d} {HUE[(k - 1) % 13]}": fates[k] for k in sorted(fates)}   # v7: keyed by copy (14/15 repeat hues)
    e7("E7_04_chasm", a, b, [dict(id="bg", type="video", src=c["eng"], **{"in": in0, "rate": rate}), *hilbert(BB["chasm"], face=True),
                             *back, *bursts, *front[::-1],
                             dict(id="jade", type="video", src=c["eng"], matte=dict(src=c["matte"], mode="luma"), keepColor=True,
                                  **{"in": in0, "rate": rate})])
    c = bclip("ear")
    e7("E7_05_ear", 137.50, 138.38, [dict(id="ear", type="video", src=c["eng"], **{"in": 0.6, "rate": 1.0}), *hilbert(BB["ear"])])
    # the lawn: only the five survivors run away with her, spaced in two rows so each reads as a Jade
    c = bclip("lawn")
    # she starts at x ~620 and drifts left, so they fan out to her left in two interleaved rows (front / back)
    SP5 = [(-290, 40, 0.12), (430, -70, 0.30), (-145, -165, 0.21), (-435, -160, 0.40), (215, -150, 0.05)]
    fan = [dict(offset=r4(round(o * FPS) / FPS), x=dx, y=dy, color=HUE[k - 1], tint=0.8, opacity=0.88)
           for k, (dx, dy, o) in zip(SURV, SP5)]
    e7("E7_06_lawn", 138.38, 139.00, [
        dict(id="bg", type="video", src=c["eng"], **{"in": 1.3, "rate": 1.0}), *hilbert(BB["lawn"]),
        dict(id="fan", type="ghosts", src=c["eng"], matte=dict(src=c["jmatte"], mode="luma"), keepColor=True, loop=False,
             fit="cover", **{"in": 1.3, "rate": 1.0}, instances=fan),
        dict(id="jade", type="video", src=c["eng"], matte=dict(src=c["matte"], mode="luma"), keepColor=True, **{"in": 1.3, "rate": 1.0})],
       fx=[dict(type="flash", at=[0.56], dur=0.06, amount=1.0, color="#ffffff")])
    # residue ribbons pile up over every surface across E7 (one more per beat, capped at 10) + a rising colour wash
    rl = []
    E7_LATE = r4(E7_T0 - 134.0)                          # v4: the overlay starts 0.88 s later; its ribbons and wash keep
    for k in range(10):                                  # their v3 song times (the first two start together at 134.88)
        st = max(0.05 * k, 0.44 * k - E7_LATE)           # v3: st = 0.44 * k
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
    # v3: color=[[0, HUE[0]], [1.7, HUE[3]], [3.4, HUE[1]], [5.0, HUE[2]]], opacity=[[0, 0.06], [3.5, 0.22, "inCubic"], [5.0, 0.4]],
    #     overlay start=134.0
    rl.insert(0, dict(type="solid", keepColor=True, blend="multiply",
                      color=[[0, HUE[0]], [r4(1.7 - E7_LATE), HUE[3]], [r4(3.4 - E7_LATE), HUE[1]], [r4(5.0 - E7_LATE), HUE[2]]],
                      opacity=[[0, 0.06], [r4(3.5 - E7_LATE), 0.22, "inCubic"], [r4(5.0 - E7_LATE), 0.4]]))
    overlays.append(dict(id="D_E7_ribbons", start=E7_T0, end=139.0, layers=rl))
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
    TERM = ["TVA ALERT", dict(text="ANOMALY DETECTED.", sync="lyric")]
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
    js = ("// Section D: drop 2 + \"Anomaly detected\" (112.96-141.00). Revision 6 (v4 pass: E3 out, R1, co-op C1/C2, no stopwatch).\n"
          "// GENERATED by tools/sections/D/build_timeline.py from media/shots/_D/takes.json: edit those, not this file.\n"
          "// Ghost choreography (clip, freeze/offset, hue, opacity, position) is tabulated in docs/sections/D.md.\n"
          "export default " + json.dumps(sec, indent=1, ensure_ascii=False) + ";\n")
    os.makedirs("render/timeline", exist_ok=True)
    open("render/timeline/D.js", "w").write(js)
    json.dump(to_edl(sec), open(f"{SH}/D_edl.json", "w"), indent=1, ensure_ascii=False)
    json.dump(notes, open(f"{SH}/_D/ghost_table.json", "w"), indent=1, ensure_ascii=False, default=float)
    print("shots", len(sec["shots"]), "overlays", len(sec["overlays"]))
