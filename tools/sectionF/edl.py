"""Section F edit decision list -> media/shots/F_edl.json (engine EDL fallback format, see render/engine/src/sections.js)
plus media/shots/<SHOT>/chosen.json for every GEN shot.

    $PY tools/sectionF/edl.py
All cut times are tracked beats/bars from analysis/cinematic/timing.json (see docs/sections/F.md for the cut list).
"""
import json
import os

ROOT = "/home/jade/Documents/rewind-take-two"
S = "media/shots/"

# chosen take per GEN shot. file = engine-ready 1080p plate (colour pass of the take, or a wipe composite),
# matte = Jade's matte from tools/engrave. in_sec/rate/reverse are the shot's own (first) use.
CHOSEN = {
    "F1": dict(take=3, file=S + "F1/take_3_wipe.mp4", in_sec=0.0, rate=1.1, reverse=False,
               notes="colour-flood wipe (tools/sectionF/wipe.py): engraved twin -> colour clip, radial from her, gold leading edge"),
    "F2": dict(take=3, in_sec=0.0, rate=1.0, reverse=False, notes="true wall-run up the tower (take 2); bar 100 jumps to 3.24 s (reaching the top and launching off it) with a 1.12x punch-in"),
    "F3": dict(take=1, in_sec=0.0, rate=1.0, reverse=False, notes="Relativity hall; the engine snaps a 90-degree roll on the downbeat"),
    "F4": dict(take=2, in_sec=0.0, rate=1.3, reverse=False, notes="take 2: dive, touches her reflection at ~3 s, plunges into concentric ripples"),
    "F5a": dict(take=2, in_sec=0.0, rate=1.0, reverse=False, notes="hero; Seedance slow push-in, giant pencil as sword"),
    "F5b": dict(take=2, in_sec=0.0, rate=1.0, reverse=False, notes="wide; ink drips become agents"),
    "F6a": dict(take=2, in_sec=0.0, rate=1.0, reverse=False, notes="the loop gesture; gold line encircles the clock"),
    "F6b": dict(take=2, in_sec=0.0, rate=1.0, reverse=False, notes="clock hands = Penrose stairs, agents march; reused at F7_03"),
    "F6c": dict(take=3, in_sec=0.3, rate=1.0, reverse=False, notes="take 2: side-on sprint with the ghost stream drawn in (keyframe kf_ghosts2); take 1 is reused reversed at F7_08 (the rewind that paints)"),
    "F7a": dict(take=2, in_sec=0.0, rate=1.0, reverse=False, notes="ghost stampede; reused at F7_06"),
    "F7b": dict(take=2, in_sec=0.0, rate=1.0, reverse=False, notes="her grin"),
    "F7c": dict(take=1, in_sec=0.0, rate=1.0, reverse=False, notes="BIG 1: Klimt gold sky"),
    "F7d": dict(take=1, in_sec=0.0, rate=1.4, reverse=False, notes="clock folds into itself; tail (collapse to a gold point) reused at F7_09"),
    "F7e": dict(take=1, in_sec=0.15, rate=1.0, reverse=False, notes="BIG 2: Banach-Tarski reunion, two Jades merge at ~0.8 s"),
    "F7_08": dict(take=3, file=S + "F6c/take_3_rewindpaint.mp4", matte=S + "F6c/take_3_cleanmatte.mp4", in_sec=3.24, rate=1.0,
                  reverse=True, notes="F6c played backward; wipe computed on the reversed clock so colour paints IN as it rewinds"),
    "F8": dict(take=2, in_sec=0.3, rate=1.0, reverse=False, notes="the committee"),
    "O2": dict(take=1, in_sec=0.0, rate=1.3, reverse=False, notes="dawn door: hair up + pencil at ~2.4-3.6 s source, door opens ~4.6 s"),
}
OVR = os.path.join(ROOT, "tools/sectionF/chosen_overrides.json")
if os.path.exists(OVR):
    for k, v in json.load(open(OVR)).items():
        CHOSEN.setdefault(k, {}).update(v)

GRAPHITE = "#3c3a37"
# paper margins that nano-banana drew around some keyframes survive into the clips: crop them (tools/sectionF/crops.json,
# measured by edge-strip variance; normalised [x0, y0, x1, y1], already 16:9)
CROPS = json.load(open(os.path.join(ROOT, "tools/sectionF/crops.json"))) if os.path.exists(os.path.join(ROOT, "tools/sectionF/crops.json")) else {}


def plate(shot):
    c = dict(CHOSEN[shot])
    t = c["take"]
    c.setdefault("file", f"{S}{shot}/take_{t}_engraved.mp4")
    c.setdefault("matte", f"{S}{shot}/take_{t}_matte/matte.mp4")
    return {"take": t, "file": c["file"], "in_sec": c["in_sec"], "out_sec": None, "rate": c["rate"], "reverse": c["reverse"],
            "notes": c.get("notes", ""), "matte": c["matte"]}


def never_stop(t0, t1, x, y, rot=0, size=46, hold=None, corners=None, color=GRAPHITE):
    """Whispered 'never stop': handwritten in pencil (engine module pencil.js), small, in the world, written while it is
    whispered (letters swept in over the whisper), then held to the cut."""
    d = {"style": "pencil", "text": "never stop", "in": t0, "out": hold or round(t1 + 1.2, 2), "at": 0,
         "cps": round(10 / max(0.4, t1 - t0), 1), "x": x, "y": y, "rotate": rot, "size": size, "color": color,
         "align": "center", "point": True}
    if corners:
        d["corners"] = corners
    return d


def cut(cid, tin, tout, src, clip_in=None, rate=None, reverse=None, text=None, fx=None, layers=None, **kw):
    c = plate(src)
    e = {"shot": cid, "file": c["file"], "in": tin, "out": tout,
         "clip_in": c["in_sec"] if clip_in is None else clip_in,
         "rate": c["rate"] if rate is None else rate,
         "reverse": c["reverse"] if reverse is None else reverse}
    if CROPS.get(src):
        e["crop"] = CROPS[src]
        e["fit"] = "cover"
    e["_matte"] = c.get("matte")          # NOT passed as the plate's matte (that would cut the world out); ghosts use it
    if text:
        e["text"] = text
    if fx:
        e["fx"] = fx
    if layers:
        e["layers"] = layers
    e.update(kw)
    return e


def FLASH(amt=0.6, col="#fff6e0", dur=0.08, at=0):
    return {"type": "flash", "at": [at], "dur": dur, "amount": amt, "color": col}


def build():
    shots = [
        # ---- bars 97-98: the colour flood (wipe baked into the plate) ---------------------------------------------------
        cut("F1", 169.40, 172.96, "F1", fx=[FLASH(0.9, "#ffffff", 0.12), {"type": "shake", "on": "downbeat", "amp": 14, "decay": 0.2},
                                            {"type": "punch", "on": "beat", "amount": 0.02}]),
        # ---- bars 99-100: wall-run; punch-in on bar 100 -------------------------------------------------------------------
        cut("F2", 172.96, 174.72, "F2", fx=[FLASH(0.5)]),
        cut("F2b", 174.72, 176.48, "F2", clip_in=3.24, scale=1.12,
            text=[never_stop(175.59, 176.46, 1530, 960, rot=-6, size=60, color="#ece6da")], fx=[FLASH(0.35)]),
        # ---- bars 101-102: Relativity flip: the frame snaps through 90 degrees on the downbeat ----------------------------
        cut("F3", 176.48, 180.02, "F3", fx=[FLASH(0.5), {"type": "spin", "amount": [[0, -90, "outBack"], [0.32, 0]]},
                                            {"type": "zoom", "amount": [[0, 1.75, "outCubic"], [0.32, 1.0]]}],
            text=[never_stop(179.10, 179.82, 300, 140, rot=-6, size=60, color="#ece6da")]),
        # ---- bars 103-104: Bean dive ----------------------------------------------------------------------------------------
        cut("F4", 180.02, 183.56, "F4", fx=[FLASH(0.4), {"type": "zoom", "amount": [[0, 1.0, "inCubic"], [3.54, 1.1]]},
                                            {"type": "flash", "at": [3.44], "dur": 0.12, "amount": 0.9, "color": "#ffffff"}],
            text=[never_stop(182.65, 183.33, 960, 140, size=60)]),
        # ---- bars 105-108: the boss --------------------------------------------------------------------------------------------
        cut("F5a", 183.56, 187.08, "F5a", fx=[FLASH(1.0, "#ffffff", 0.16), {"type": "shake", "on": "downbeat", "amp": 10, "decay": 0.25}]),
        cut("F5b", 187.08, 190.58, "F5b", fx=[FLASH(0.5), FLASH(0.35, "#ffe9a8", 0.1, at=round(189.54 - 187.08, 2))]),
        # ---- bars 109-112: the perspective move --------------------------------------------------------------------------------
        cut("F6a", 190.58, 192.34, "F6a", fx=[FLASH(0.5)]),
        # the payoff: the clock's hands are Ascending and Descending, agents march it (2D, same hand as the rest of F).
        # Section E's 3D render/three/scenes/f6_clock.js was tried here (192.34-195.86, then 194.10-195.42) and dropped:
        # at the clunk it reads as a flat gold disc in a different hand. It is still available if wanted.
        cut("F6b", 192.34, 195.42, "F6b", fx=[FLASH(0.4), {"type": "shake", "on": [194.10], "amp": 10, "decay": 0.22}]),
        cut("F6c", 195.42, 197.60, "F6c", fx=[FLASH(0.4)], text=[never_stop(196.68, 197.48, 1120, 1052, rot=-2, size=50)]),
        # ---- bars 113-119: escalating hero cuts every 2 beats ---------------------------------------------------------------------
        cut("F7_01", 197.60, 198.48, "F7a", fx=[FLASH(0.5)]),
        cut("F7_02", 198.48, 199.38, "F7b", fx=[FLASH(0.4)]),
        cut("F7_03", 199.38, 200.24, "F6b", clip_in=3.6, rate=1.0, fx=[FLASH(0.4)]),
        cut("F7_04", 200.24, 202.02, "F7c", fx=[FLASH(1.0, "#ffe9a8", 0.16)]),                                               # BIG 1
        cut("F7_05", 202.02, 202.88, "F7d", fx=[FLASH(0.5)]),
        cut("F7_06", 202.88, 203.76, "F7a", clip_in=2.0, scale=1.12, fx=[FLASH(0.4)]),
        cut("F7_07", 203.76, 205.52, "F7e", fx=[FLASH(1.0, "#ffffff", 0.16)]),                                               # BIG 2
        cut("F7_08", 205.52, 207.28, "F7_08", fx=[FLASH(0.5, "#d6e8ff"), {"type": "rewind", "amount": 0.45}],
            text=[{"style": "rewind", "in": 205.52, "out": 207.28, "multiplier": [[0, 2, "hold"], [0.88, 4]], "color": "#0b0b0c",
                   "side": "left"}]),
        cut("F7_09", 207.28, 208.14, "F7d", clip_in=2.2, rate=1.15, fx=[FLASH(0.7, "#ffe9a8")]),
        cut("F7_10", 208.14, 208.58, "F1", clip_in=2.3, fx=[FLASH(0.6)]),
        cut("F7_11", 208.58, 209.02, "F5a", clip_in=1.6, fx=[FLASH(0.6)]),
        cut("F7_12", 209.02, 209.46, "F6a", clip_in=1.2, fx=[FLASH(0.6)]),
        cut("F7_13", 209.46, 209.90, "F7c", clip_in=1.8, fx=[FLASH(0.7, "#ffe9a8")]),
        # ---- bar 120: the committee; band drop-out 210.90 ---------------------------------------------------------------------------
        cut("F8", 209.90, 211.64, "F8", fx=[FLASH(0.5)], text=[never_stop(210.77, 211.52, 1250, 110, rot=-3, size=60)]),
    ]
    # ---- outro ------------------------------------------------------------------------------------------------------------------
    shots.append(cut("O2", 218.92, 222.78, "O2", fx=[FLASH(0.8, "#fff1d6", 0.12)],
                     text=[{"style": "plain", "in": 218.92, "out": 222.78, "text": "DISSERTATION DEFENSE\n9:00 AM", "font": "fell",
                            "size": 54, "color": "#1b1a18", "panel": "#efe9da", "border": "#1b1a18", "padding": 30, "align": "center",
                            "corners": "O2_PLAQUE"}]))
    # O3: hard cut to black at 222.78; the ring-out sits on black until O4
    shots.append({"shot": "O3_black", "in": 222.78, "out": 226.00, "layers": [{"type": "solid", "color": "#000000"}]})
    shots.append({"shot": "O4", "in": 226.00, "out": 227.96, "layers": [{"type": "solid", "color": "#000000"}],
                  "text": [{"style": "pencil", "in": 226.00, "out": 227.96, "text": "never stop.", "at": 0, "cps": 13,
                            "x": 960, "y": 610, "size": 216, "color": "#9a958b", "align": "center", "point": True},
                           {"style": "iteration", "in": 226.00, "out": 227.96, "side": "right", "margin": 64, "y": 1016,
                            "base": 4097, "from": 0.45, "rate": 3.0, "flicker": 0.35, "size": 28, "color": "#ece7dc"}],
                  "fx": [{"type": "fade", "out": [227.0, 227.96]}]})
    overlays = [{"id": "O1_variance_report", "start": 211.64, "end": 218.92, "layers": [
        {"type": "canvas", "module": "tools/sectionF/modules/variance_report.js", "stage": "post", "params": {
            "slideIn": ["211.90", "212.20"], "cps": 50, "size": 28, "rect": [1040, 640, 800, 330],
            "lines": ["TIME VARIANCE █████████", "VARIANCE REPORT", "CASE 4,097", "SUBJECT: ████ NOT FOUND", "RESIDUE: UNTRACEABLE"],
            "unwrite": ["215.22", "217.04"], "stamp": {"text": "TIMELINE IS NOW CANON", "at": "217.04"}}}]}]
    return {"section": "F", "overlays": overlays, "note": "Section F: final drop + outro (169.40-227.96). Generated by tools/sectionF/edl.py; see docs/sections/F.md.",
            "fx": [{"type": "grain", "amount": 0.03, "seed": "twos"}],
            "shots": shots}


O2_PLAQUE = None   # set from tools/sectionF/o2_plaque.json (corner-pin of the brass plaque, design px)


def main():
    edl = build()
    plaque = os.path.join(ROOT, "tools/sectionF/o2_plaque.json")
    for s in edl["shots"]:
        for l in s.get("layers", []):
            if l.get("src") == "PLATE":
                l["src"] = s["file"]
                if s.get("_matte"):
                    l["matte"] = {"src": s["_matte"], "mode": "luma"}
                l["in"] = s.get("clip_in", 0)
        for t in s.get("text", []):
            if t.get("corners") == "O2_PLAQUE":
                if os.path.exists(plaque):
                    cr = CROPS.get("O2") or [0, 0, 1, 1]
                    fx = lambda v, i: (v / 1920 - cr[0]) / (cr[2] - cr[0]) * 1920 if i % 2 == 0 else (v / 1080 - cr[1]) / (cr[3] - cr[1]) * 1080
                    t["corners"] = [[k, [round(fx(v, i), 1) for i, v in enumerate(c)]] for k, c in json.load(open(plaque))]
                else:
                    del t["corners"]
                    t.update(x=470, y=310)
    for s in edl["shots"]:
        m = s.pop("_matte", None)
        if m:
            s["matte_file"] = m            # informational: Jade's matte for this plate (engine key "matte" would mask the plate)
    json.dump(edl, open(os.path.join(ROOT, S, "F_edl.json"), "w"), indent=1, ensure_ascii=False)
    for shot in CHOSEN:
        if shot == "F7_08":
            continue
        json.dump(plate(shot), open(os.path.join(ROOT, S, shot, "chosen.json"), "w"), indent=1)
    print("wrote", S + "F_edl.json", len(edl["shots"]), "shots")


if __name__ == "__main__":
    main()
