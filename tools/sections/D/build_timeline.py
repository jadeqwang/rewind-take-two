#!/usr/bin/env python
"""Build section D's engine timeline (render/timeline/D.js) and the EDL mirror (media/shots/D_edl.json).

Section D = drop 2 + "Anomaly detected", 112.96-141.00, including E3 (119.44-122.95): the singing take made by the singing
director, placed here with ribbons (E3_VARIANT below picks the lip-sync lag). All ghost choreography lives in the tables below (GHOSTS_E2, E4_GHOSTS, ...): which clip, freeze/offset,
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

# E3 singing take lip-sync variant (media/sing/review/E3_take_3_lips_ABC.json): flip after Jade listens.
#   A = lips 0.15 s earlier (lag 0.90), B = measured (lag 0.75), C = lips 0.15 s later (lag 0.60)
E3_VARIANT = "B"
E3_LAGS = {"A": 0.90, "B": 0.75, "C": 0.60}
E3_TAKE, E3_REF_T0 = "media/sing/E3/take_3_lips.mp4", 119.14      # clip_time = song_time - ref_t0 + lag

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


sys.path.insert(0, os.path.join(ROOT, "tools/sections/D"))
import ghostsprite  # noqa: E402

SPR = f"{SH}/_D/sprites"


def sprite_of(c, freeze, color, matte="matte", scale=1.0):
    """bake (once) the luminous coloured-pencil afterimage of clip c at `freeze`; returns (path, stats in design px)."""
    os.makedirs(SPR, exist_ok=True)
    ol = int(round(min(12, max(4, 3.5 / max(scale, 0.05)))))      # outline/glow survive downscaling for distant ghosts
    name = f"{os.path.basename(c['stem'])}_{matte}_{freeze:.3f}_{color.lstrip('#')}_o{ol}.png"
    path = f"{SPR}/{name}"
    meta = path[:-4] + ".json"
    if os.path.exists(path) and os.path.exists(meta) and os.path.getmtime(path) > os.path.getmtime(ghostsprite.__file__):
        return path, json.load(open(meta))
    st = ghostsprite.sprite(c["eng"], f"{c['stem']}_{matte}", freeze, color, path, outline=ol, glow=18 * ol / 4)
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
    E2A_SPREAD = [(-640, None), (-120, -40), (560, -80)]          # frozen where she was, then each drifts aside so the next attempt has room
    for k, (c, frz, rate, a, b, snap) in enumerate(seg):
        play = (b - a) - (0.125 if snap else 0.0)          # forward playback after the 3-frame ◀◀ scrub
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
        notes[f"g{k + 1}"] = dict(clip=c["eng"], freeze=frz, hue=HUE[k], where="L tracks (as frozen)", hit=CHOPS[k])
    s1 = mstats(sp["stem"], 2.75 - h[0])
    layers[1:1] = [
        # a coloured-pencil radial bloom of residue floods outward from her, then clears
        dict(id="bloom", type="image", src=f"{SH}/_D/e1_bloom.png", keepColor=True, fit="none", end=0.93,
             x=r4(s1["cx"]), y=r4(s1["cy"]), scale=[[0, 0.1, "outCubic"], [0.85, 1.5]],
             rotate=[[0, 0], [0.93, 14]], opacity=[[0, 1.0], [0.45, 0.9, "inCubic"], [0.93, 0.0]]),
        dict(id="bloom_glow", type="image", src=f"{SH}/_D/e1_bloom.png", keepColor=True, fit="none", end=0.6, blend="add",
             x=r4(s1["cx"]), y=r4(s1["cy"]), scale=[[0, 0.08, "outCubic"], [0.6, 1.1]], opacity=[[0, 0.5], [0.6, 0.0]]),
    ]
    layers += ribs + ghosts
    # E1 impact: the frame fills with residue colour, then clears; a mote burst from her as she bursts off the mark
    layers += [
        dict(id="burst", type="canvas", module="motes", keepColor=True, end=1.6,
             params=dict(at=0.0, x=r4(s1["cx"] + 960), y=r4(s1["cy"] + 540), count=220,
                         colors=[RES[0], RES[0], RES[1], RES[1], "#C9A227"], shape="circle", speed=2600, drag=2.4, size=13,
                         life=1.2, ring=False, glow=1.0, seed=65)),
    ] + [ribbon(f"e1_flow{j}", [[r4(0.02 * j), r4(s1["cx"]), r4(s1["cy"])]] +
                [[r4(0.02 * j + 0.07 * q), r4(s1["cx"] + (210 * q) * math.cos(j * 0.698 + 0.1 * q * (1 if j % 2 else -1))),
                  r4(s1["cy"] + (170 * q) * math.sin(j * 0.698 + 0.1 * q * (1 if j % 2 else -1)))] for q in range(1, 9)],
                colors=[RES[0], "#C9A227" if j % 4 == 0 else RES[1]], width=46, trail=0.7, pencil=bool(j % 2), bloom=1.0,
                grain=0.8, motes=0.4, seed=80 + j) | dict(end=1.0) for j in range(9)] + [
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
    E2B_SPREAD = [(-780, 250), (-470, -150), (-150, 170), (130, -60)]   # fan out away from the agents (right)
    a = 0.0
    for k, (key, fz, rate) in enumerate(FLD):
        c = C[key]
        b = ends[k] - t0
        si = fz - rate * (b - a)
        layers.append(plate(f"field{k + 1}", c, si, rate, a, b))
        ribs.append(ribbon(f"res{k + 4}", seg_path(c["stem"], si, rate, a, b, suffix="_jmatte"),
                           colors=[HUE[3 + k], RES[1]], width=24, end=r4(t1 - t0)))
        if k < 4:   # the 5th (spin @0.95 = ghost 8) is born on the cut to the ring shot
            g, st = ghost(f"g{k + 4}", c, fz, HUE[3 + k], b, matte="jmatte")
            tx, ty = E2B_SPREAD[k]
            g["x"] = [[r4(b), 0, "outCubic"], [r4(b + 0.35), r4(tx - st["cx"])]]
            g["y"] = [[r4(b), 0, "outCubic"], [r4(b + 0.35), r4(ty - st["cy"])]]
            ghosts.append(g)
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
            _, s = sprite_of(c, fz, HUE[gi], matte, th if th < 3 else 0.3)
            sc = th if th < 3 else th / max(1.0, s["y1"] - s["y0"])   # th < 3: a scale, else a target bbox height (px)
            cx = -s["cx"] if flip else s["cx"]          # sprite centroid lands on (tx, ty)
            g, _ = ghost(f"g{gi + 1}", c, fz, HUE[gi], 0.0, matte=matte, x=tx - sc * cx, y=ty - sc * s["cy"], scale=sc,
                         flip=flip, born=(gi == 7))       # 1-7 are already standing there; 8 pops on the cut (its chop)
            placed.append(g)
            notes.setdefault(f"g{gi + 1}", {})["ring_pos"] = dict(x=tx, y=ty, height_px=th, scale=round(sc, 3), flip=flip)
        new = []
        for j, k in enumerate(range(8, 13)):
            fz = R["freezes"][j]
            new.append(ghost(f"g{k + 1}", rc, fz, HUE[k], CHOPS[k] - t0, matte="jmatte")[0])
            notes[f"g{k + 1}"] = dict(clip=rc["eng"], freeze=fz, hue=HUE[k], where="ring wide (where she was)", hit=CHOPS[k])
        lts = [k / 12 for k in range(int((t1 - t0) * 12) + 1)]
        rp = path_of(rc["stem"], [float(np.interp(x, [k[0] for k in R["srcTime"]], [k[1] for k in R["srcTime"]])) for x in lts],
                     lts, "_jmatte")
        layers += [ribbon("res_ring", rp, colors=[HUE[8], HUE[12]], width=16)] + placed + new
        shots.append(dict(id="E2c_ring", start=t0, end=t1, layers=layers,
                          fx=[dict(type="flash", at=[0], dur=0.06, amount=0.5, color="#ffffff")] +
                          chop_fx([c - t0 for c in CHOPS[8:]], extra=[dict(type="zoom", amount=[[0, 1.1, "inOutSine"], [2.49, 1.22]])])))

    # ghost counter over E2 (Press Start 2P, top right, ink on paper): one more per chop, odometer roll
    keys = [[0, 0, "hold"]]
    for k, c in enumerate(CHOPS):
        keys += [[r4(c - 113.89 - 0.07), k, "linear"], [r4(c - 113.89), k + 1, "hold"]]
    overlays.append(dict(id="D_ghost_counter", start=113.89, end=119.44, layers=[
        dict(type="solid", stage="post", color=PAPER, opacity=0.88, rect=[1580, 40, 312, 56]), dict(
        type="canvas", module="hud", stage="post", params=dict(mode="iteration", label="GHOSTS", value=keys[1:] if keys[1][0] <= 0 else keys,
                                                               snap=True, side="right", color=INK, size=26))]))

    # ---------------- E3: SINGING #2 "Rewind." (pencil Jade at the Bean; take made by the singing director) ----------------
    t0, t1 = 119.44, 122.95
    lag = E3_LAGS[E3_VARIANT]
    occ = f"{SH}/E3/occluder_mask.mp4"
    if not os.path.exists(occ):        # her first-frame silhouette (singing director's mask) as a static matte clip
        import subprocess
        os.makedirs(f"{SH}/E3", exist_ok=True)
        m = cv2.resize(cv2.imread("media/sing/first/her_mask_first_frame.png", 0), (1920, 1080), interpolation=cv2.INTER_AREA)
        m = (m > 128).astype(np.uint8) * 255
        m[:860, :640] = 0                # stray plaza blob left of her (trace artefact); keeps head, hair, torso, arm
        m = cv2.GaussianBlur(cv2.erode(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))), (0, 0), 2.5)
        cv2.imwrite(occ[:-4] + ".png", m)
        subprocess.run([os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg"), "-y", "-loglevel", "error", "-loop", "1",
                        "-framerate", "24", "-i", occ[:-4] + ".png", "-t", "5.1", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-crf", "10", occ], check=True)
    e3_in = r4(t0 - E3_REF_T0 + lag)
    # residue ribbons spiral in from the frame edges and orbit her head and shoulders; where an orbit crosses her body
    # it is hidden by an occluder (the same take, matted by her first-frame silhouette), so they circle BEHIND her and
    # never touch her face (the orbit clears the head: top y≈130 vs hair top ≈190, sides x≈330/1470 vs head 700-1100).
    CX, CY, RX, RY, TILT = 900, 470, 570, 335, math.radians(-10)
    e3_ribs = []
    for k in range(7):
        st = 0.18 * k                          # staggered entries
        a0 = math.radians(25 + 52 * k)         # entry angle around the frame
        sc = 0.92 + 0.07 * (k % 3)
        w = 2 * math.pi / (2.6 + 0.25 * (k % 3))
        pts = []
        for j in range(int((t1 - t0 - st) * 12) + 1):
            tt = j / 12
            r = sc * (1 + 1.25 * math.exp(-tt / 0.45))                # far outside the frame -> settles on the orbit
            a = a0 + w * tt
            x, y = RX * r * math.cos(a), RY * r * math.sin(a)
            xr, yr = x * math.cos(TILT) - y * math.sin(TILT), x * math.sin(TILT) + y * math.cos(TILT)
            pts.append([r4(st + tt), r4(CX + xr), r4(CY + yr)])
        e3_ribs.append(dict(type="canvas", module="ribbon", keepColor=True, params=dict(
            path=pts, colors=[RES[k % 2], RES[(k + 1) % 2]], width=40 + 10 * (k % 3), trail=1.5, twist=0.7, bloom=0.9,
            grain=0.75, pencil=False, motes=0.3, seed=120 + k)))
    shots.append(dict(id="E3_sing", start=t0, end=t1, layers=[
        dict(id="jade", type="video", src=E3_TAKE, fit="cover", **{"in": e3_in, "rate": 1.0}),
        *e3_ribs,
        dict(id="occluder", type="video", src=E3_TAKE, fit="cover", **{"in": e3_in, "rate": 1.0},
             matte=dict(src=f"{SH}/E3/occluder_mask.mp4", mode="luma")),
        dict(type="canvas", module="lowerthird", stage="post", params=dict(color="#F08A24", size=120, y=975, halo=0.6))],
        fx=[dict(type="grain", amount=0.045, size=1.2, seed="twos"), dict(type="paper", amount=0.18),
            dict(type="flash", at=[0], dur=0.06, amount=0.35, color="#ffffff")]))
    notes["E3"] = dict(take=E3_TAKE, variant=E3_VARIANT, lag=lag, clip_in=e3_in, clip_out=r4(t1 - E3_REF_T0 + lag))

    # ---------------- E4: "Rewind." #2, the Super Meat Boy replay ----------------
    t0, t1 = 122.95, 126.25
    E4 = take["e4_stream"]
    c = C["e4_stream"]
    inst = []
    for k, off in enumerate([-0.33, 0.33, -0.67, 0.67, -1.0, 1.0]):   # earlier/later attempts on the same route
        inst.append(dict(offset=r4(round(off * FPS) / FPS), x=0, y=r4((-1) ** k * 30),
                         color=HUE[(k + 1) % 13], opacity=0.8, tint=0.75))
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
                         color=HUE[(j + k) % 13], opacity=0.75, tint=0.75) for j in range(n)]
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
            pts.append([r4(st + 0.9 * u), r4(x + 960), r4(y + 540)])
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
    js = ("// Section D: drop 2 + \"Anomaly detected\" (112.96-141.00, incl. E3 singing take; lip-sync variant: E3_VARIANT).\n"
          "// GENERATED by tools/sections/D/build_timeline.py from media/shots/_D/takes.json: edit those, not this file.\n"
          "// Ghost choreography (clip, freeze/offset, hue, opacity, position) is tabulated in docs/sections/D.md.\n"
          "export default " + json.dumps(sec, indent=1, ensure_ascii=False) + ";\n")
    os.makedirs("render/timeline", exist_ok=True)
    open("render/timeline/D.js", "w").write(js)
    json.dump(to_edl(sec), open(f"{SH}/D_edl.json", "w"), indent=1, ensure_ascii=False)
    json.dump(notes, open(f"{SH}/_D/ghost_table.json", "w"), indent=1, ensure_ascii=False, default=float)
    print("shots", len(sec["shots"]), "overlays", len(sec["overlays"]))
