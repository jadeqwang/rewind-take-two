#!/usr/bin/env python3
"""v4 note 0:13 (the Bean): FREE previz of "start wide, then move in" for shot S1 (12.60-16.14).

    PY=~/Documents/moongazing/.venv/bin/python
    $PY tools/v4B/bean/previz.py            # stand-in plate, 960x540 clip with audio, stills, contact sheet
    $PY tools/v4B/bean/previz.py --late     # variant: land on the bar-9 downbeat (14.36) instead of beat 8:4 (13.92)

No paid call, no engine, no GPU: PIL + numpy + PyAV, ffmpeg for the encode. Reads only existing media:
  media/sing/S1/v3_sync_1080.mp4 + v3_sync_1080_matte/   the v3 singer (v4-A's file is a path change: SINGER below)
  media/sing/plates/plate_sane_1.jpg                      a v2 reject plate, used as the STAND-IN whole Bean
  media/sing/plates/plate_close_1_crop.jpg                the close plate (the END of the move = the take's own plate)
  media/shots/C3/kf_sdr2.jpg                              an engraved skyline, used as the STAND-IN towers behind
  deliverables/wip/rewind_roughcut_v3_preview.mp4         v3 frames either side of the shot (cut context) + audio
Writes media/reviews/v4/B/plans/bean/. Everything is in 1920x1080 "design px"; the clip is scaled to 960x540.

Geometry (see docs/revisions/v4/plans/bean.md):
  three planes, each a similarity about its own fixed point, all driven by one eased progress e(t) in 0..1 and
  log-interpolated (a zoom is exponential in scale):
    her    scale HER0  -> 1 about the bottom-centre of frame (the frame cuts her at the chest at both ends)
    Bean   scale BEAN0 -> 1 about BEAN_C (Bean + plaza + the arc lyric + the close plate dissolving in)
    far    sky and towers behind: relative scale 1 -> FAR1 (a cheat: slower than the Bean), horizon locked to the plaza's
  on top of all of it v3's slow push (1.00 -> 1.04 over the shot), so the framing after the move is v3's.
"""
import math
import os
import subprocess
import sys

import av
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.chdir(ROOT)
FFMPEG = os.path.expanduser(os.environ.get("FFMPEG", "~/Documents/moongazing/.venv/bin/ffmpeg"))
OUT = "media/reviews/v4/B/plans/bean"
LATE = "--late" in sys.argv          # variant: land on the bar-9 downbeat (14.36) instead of beat 8:4 (13.92)
NAME = "previz" + ("_late" if LATE else "")

# ---- inputs (the swap to v4-A's take is these two paths) -----------------------------------------------------------
SINGER = "media/sing/S1/v3_sync_1080.mp4"
SINGER_MATTE = "media/sing/S1/v3_sync_1080_matte/"
V3 = "deliverables/wip/rewind_roughcut_v3_preview.mp4"
SANE = "media/sing/plates/plate_sane_1.jpg"
CLOSE = "media/sing/plates/plate_close_1_crop.jpg"
SKY = "media/shots/C3/kf_sdr2.jpg"
FONT = "render/fonts/anton-latin-400-normal.woff2"

# ---- timing (song seconds) -----------------------------------------------------------------------------------------
FPS = 24
S1_IN, S1_OUT = 12.60, 16.14
CLIP_IN, CLIP_OUT = 12.10, 16.60
MOVE_T0 = 13.04                      # beat 8:2: the wide holds one beat
MOVE_T1 = 14.36 if LATE else 13.92   # beat 8:4 = onset of "before" (13.89)
HOLD_CREEP = 0.03                    # share of the move spent creeping during the hold
WORDS = [("THE", 13.20), ("NIGHT", 13.421), ("BEFORE", 13.89)]

# ---- framing (design px) -------------------------------------------------------------------------------------------
W, H = 1920, 1080
HER0 = 0.42                          # her scale in the wide frame (1 = v3)
HER_C = (960.0, 1080.0)              # her fixed point: bottom-centre
BEAN_W_END = 2550.0                  # Bean outline width at the v3 framing (plate_sane_1 at 1.0 design px / plate px)
BEAN_FRAC0 = 0.62                    # Bean width / frame width in the wide frame
BEAN0 = BEAN_FRAC0 * W / BEAN_W_END  # 0.467
BEAN_TOP0 = 60.0                     # y of the Bean's top edge in the wide frame (it is 0 at the end)
BEAN_C = ((960 - BEAN0 * 965) / (1 - BEAN0), BEAN_TOP0 / (1 - BEAN0))   # fixed point of the Bean plane
HORIZON0 = 640.0                     # plaza horizon in the wide frame
FAR1 = 1.5                           # far plane's growth over the move (Bean plane: 1 / BEAN0 = 2.14)
V3_PUSH = (1.0, 1.04)                # v3's slow push over the whole shot, about the frame centre
SANE_TOP, SANE_CX = 76.0, 1380.0     # Bean top and centre x in plate_sane_1 px
PAPER, INK = (236, 231, 220), (11, 11, 12)


def ease(x):
    """smoothstep pushed a little early: fastest just before the middle beat (8:3), soft landing on 8:4.
    (2.2 instead of 1.4 was tried first: all the travel was over by 13.55 and the landing no longer sat on the beat.)"""
    x = min(1.0, max(0.0, x)); s = x * x * (3 - 2 * x)
    return 1 - (1 - s) ** 1.4


def progress(t):
    """0 at the cut, HOLD_CREEP at MOVE_T0, 1 at MOVE_T1"""
    if t <= MOVE_T0:
        return HOLD_CREEP * (t - S1_IN) / (MOVE_T0 - S1_IN)
    return HOLD_CREEP + (1 - HOLD_CREEP) * ease((t - MOVE_T0) / (MOVE_T1 - MOVE_T0))


def planes(t):
    """per plane (scale, fixed point): current = c + s * (end_coords - c). End coords = the v3 framing."""
    e = progress(t)
    return dict(e=e, her=(HER0 ** (1 - e), HER_C), bean=(BEAN0 ** (1 - e), BEAN_C))


def warp(img, s, c, size=(W, H), resample=Image.BICUBIC):
    """similarity about c: out = c + s * (in - c). img is in the plane's own END coords, same size as the frame."""
    return img.transform(size, Image.AFFINE, (1 / s, 0, c[0] - c[0] / s, 0, 1 / s, c[1] - c[1] / s), resample)


# ---- the stand-in wide plate, built in END coords of the Bean plane ------------------------------------------------
# The Bean plane image is drawn in "wide coords x SS" (the wide frame supersampled) and mapped to the frame by
#   wide -> current: p = c + (s / BEAN0) * (p_wide - c)
SS = 2


def bean_mask():
    """hand-traced outline of the Bean in plate_sane_1 (plate px), feathered"""
    pts = [(690, 38), (500, 50), (380, 80), (280, 120), (200, 175), (140, 240), (100, 320), (70, 400), (55, 480),
           (48, 580), (55, 660), (78, 722), (120, 754), (1262, 754), (1302, 722), (1325, 660), (1332, 580),
           (1325, 480), (1310, 400), (1280, 320), (1240, 240), (1180, 175), (1100, 120), (1000, 80), (880, 50)]
    m = Image.new("L", (2752, 1536), 0)
    ImageDraw.Draw(m).polygon([(x * 2, y * 2) for x, y in pts], fill=255)
    return m.filter(ImageFilter.GaussianBlur(14)).point(lambda v: min(255, max(0, (v - 96) * 4)))


def person(d, x, y, h, col=INK):
    """a tiny engraved pedestrian: feet at (x, y), height h"""
    w = h * 0.3
    d.ellipse([x - h * 0.085, y - h, x + h * 0.085, y - h * 0.83], fill=col)
    d.polygon([(x - w / 2, y - h * 0.8), (x + w / 2, y - h * 0.8), (x + w * 0.36, y - h * 0.38), (x + w * 0.3, y),
               (x + w * 0.04, y), (x, y - h * 0.36), (x - w * 0.04, y), (x - w * 0.3, y), (x - w * 0.36, y - h * 0.38)], fill=col)


def build_standin():
    """returns (far RGB with its own geometry, bean-plane RGBA at wide coords x SS). Crude on purpose."""
    rng = np.random.default_rng(7)
    # far plane: wide coords x in [-700, 2620], y in [-1000, 640]; skyline base on the horizon
    FX0, FY0, FW, FH = -700, -1000, 3320, 1640
    far = Image.new("RGB", (FW, FH), (16, 16, 18)); d = ImageDraw.Draw(far)
    for _ in range(420):
        x, y = rng.uniform(0, FW), rng.uniform(0, FH - 500); r = rng.uniform(0.8, 2.2)
        d.ellipse([x - r, y - r, x + r, y + r], fill=PAPER)
    sk = Image.open(SKY).convert("L").crop((690, 0, 2560, 712))
    sk = Image.merge("RGB", [sk.point(lambda v: int(v * f)) for f in (0.80, 0.78, 0.74)])   # sits back: darker than the Bean
    k = 1.0; tw, th = int(sk.width * k), int(sk.height * k); sk = sk.resize((tw, th), Image.LANCZOS)
    top = np.linspace(0, 1, 200)[:, None] ** 1.5                                                # fade its sky into ours
    a = np.asarray(sk).astype(np.float32); a[:200] = a[:200] * top[..., None] + 16 * (1 - top[..., None])
    sk = Image.fromarray(a.astype(np.uint8))
    x = 960 - FX0 - tw
    for i, tile in enumerate([sk.transpose(Image.FLIP_LEFT_RIGHT), sk]):
        far.paste(tile, (x + i * tw, FH - th))
    far_geo = (FX0, FY0)

    # Bean plane: plaza + Bean + people, wide coords x SS, RGBA (transparent above the horizon)
    P = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(P)
    hz = HORIZON0 * SS
    d.rectangle([0, hz, W * SS, H * SS], fill=PAPER + (255,))
    vp = (960 * SS, hz)
    for gx in range(-9000, 12000, 230):                                   # paving joints running to the vanishing point
        d.line([vp, (gx, H * SS)], fill=(70, 68, 64, 255), width=2)
    yy = 9.0
    while hz + yy < H * SS:                                               # cross joints, closing up toward the horizon
        d.line([0, hz + yy, W * SS, hz + yy], fill=(70, 68, 64, 255), width=2 if yy < 200 else 3)
        yy *= 1.32
    # night falls off toward the edges of the plaza: engraved horizontal hatching, denser away from the lit centre
    hatch = Image.new("L", (W * SS, H * SS), 0); hd = ImageDraw.Draw(hatch)
    for y in range(int(hz), H * SS, 7):
        f = (y - hz) / (H * SS - hz)
        half = (520 + 900 * f) * SS / 2 * 1.2
        hd.line([0, y, 960 * SS - half, y], fill=255, width=4); hd.line([960 * SS + half, y, W * SS, y], fill=255, width=4)
        hd.line([0, y + 3, 960 * SS - half * 1.5, y + 3], fill=255, width=2); hd.line([960 * SS + half * 1.5, y + 3, W * SS, y + 3], fill=255, width=2)
    P.paste(Image.new("RGBA", P.size, INK + (255,)), (0, 0), hatch)
    # the far edge of the plaza: a dark hedge and tree line with lamps, hiding the foot of the towers
    for x in range(-20, W * SS + 40, 26):
        r = rng.uniform(26, 54)
        d.ellipse([x - r, hz - r * 1.5, x + r, hz + 10], fill=INK + (255,))
    d.rectangle([0, hz - 6, W * SS, hz + 14], fill=INK + (255,))
    for x in range(130, W * SS, 420):
        d.line([x, hz - 150, x, hz + 6], fill=PAPER + (255,), width=4)
        d.ellipse([x - 13, hz - 176, x + 13, hz - 150], fill=PAPER + (255,))
    # the Bean (plate_sane_1 cut out), with a contact shadow
    s = BEAN_FRAC0 * W / BEAN_W_END * SS                                   # plate px -> wide px x SS (uses the multiplane value)
    sane = Image.open(SANE).convert("RGB"); m = bean_mask()
    bw, bh = int(2752 * s), int(1536 * s)
    bx, by = int(960 * SS - SANE_CX * s), int(BEAN_TOP0 * SS - SANE_TOP * s)
    base_y = by + int(1508 * s)
    sh = Image.new("L", P.size, 0)
    ImageDraw.Draw(sh).ellipse([bx + 60 * s, base_y - 70 * s, bx + bw - 60 * s, base_y + 110 * s], fill=235)
    P.paste(Image.new("RGBA", P.size, INK + (255,)), (0, 0), sh.filter(ImageFilter.GaussianBlur(22)))
    P.paste(sane.resize((bw, bh), Image.LANCZOS), (bx, by), m.resize((bw, bh), Image.LANCZOS))
    # people for scale: the Bean is 10 m tall, so a person is about a sixth of its height
    ph = 0.167 * (1508 - SANE_TOP) * s
    for fx, dy, k in [(0.205, 30, 1.0), (0.225, 34, 0.95), (0.33, 70, 1.12), (0.71, 60, 1.1), (0.735, 64, 1.04),
                      (0.80, 24, 0.97), (0.14, 150, 1.5), (0.155, 156, 1.42), (0.875, 190, 1.7), (0.60, -6, 0.9)]:
        person(d, fx * W * SS, base_y + dy * SS / 2, ph * k)
    return far, far_geo, P


def far_layer(far, far_geo, s_bean, t_e):
    """sky and towers: grows 1 -> FAR1, its horizon locked to the plaza's horizon on the Bean plane"""
    sF = FAR1 ** t_e if FAR1 != 1 else 1.0
    rel = s_bean / BEAN0
    hy = BEAN_C[1] + rel * (HORIZON0 - BEAN_C[1]); cx = BEAN_C[0] + rel * (960 - BEAN_C[0])
    # out = (cx, hy) + sF * (wide - (960, HORIZON0)); wide = far px + far_geo
    a = 1 / sF
    return far.transform((W, H), Image.AFFINE, (a, 0, 960 - far_geo[0] - cx * a, 0, a, HORIZON0 - far_geo[1] - hy * a), Image.BICUBIC)


def bean_layer(P, s_bean):
    rel = s_bean / BEAN0; a = SS / rel
    return P.transform((W, H), Image.AFFINE, (a, 0, (BEAN_C[0] - BEAN_C[0] / rel) * SS, 0, a, (BEAN_C[1] - BEAN_C[1] / rel) * SS), Image.BICUBIC)


def close_plate():
    """the close plate in END coords with a soft mask: inside the Bean's rim, feathered toward the frame edges"""
    img = Image.open(CLOSE).convert("RGB").resize((W, H), Image.LANCZOS)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rim = 1 - ((xx - 965) / 1235) ** 2 - ((yy - 715) / 712) ** 2          # > 0 inside the Bean's outline
    a = np.clip(rim / 0.06, 0, 1)
    a *= np.clip(xx / 260, 0, 1) * np.clip((W - xx) / 260, 0, 1) * np.clip((H - yy) / 300, 0, 1)
    return img, Image.fromarray((a * 255).astype(np.uint8))


# ---- the arc lyric (a PIL approximation of render/timeline/_arc_lyric.js, END coords) -------------------------------
def arc_lyric(t, font):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    size = 88; track = size * 0.03; space = size * 0.26
    rows = [([w for w in WORDS[:2]], 1014), ([WORDS[2]], 930)]
    for words, r in rows:
        glyphs = []; x = 0.0
        for wi, (word, t0) in enumerate(words):
            if wi: x += space
            for ch in word:
                a = font.getlength(ch); glyphs.append((ch, x + a / 2, t0)); x += a + track
            x -= track
        a0 = math.radians(-31) - x / r
        for ch, gx, t0 in glyphs:
            if t < t0: continue
            ang = a0 + gx / r
            px, py = 965 + r * math.sin(ang), 981 - r * math.cos(ang)
            g = Image.new("RGBA", (220, 220), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
            gd.text((110, 150), ch, font=font, anchor="ms", fill=PAPER + (255,), stroke_width=5, stroke_fill=INK + (255,))
            g = g.rotate(-math.degrees(ang), resample=Image.BICUBIC, center=(110, 150))
            L.alpha_composite(g, (int(px - 110), int(py - 150)))
    return L


def v3_frames(t0, t1):
    """v3 preview frames (960x540) for song times [t0, t1)"""
    c = av.open(V3); st = c.streams.video[0]; out = {}
    c.seek(int(max(0, t0 - 1.5) / st.time_base), stream=st)
    for f in c.decode(st):
        n = round(float(f.pts * st.time_base) * FPS)
        if n > round(t1 * FPS): break
        if n >= round(t0 * FPS) - 1: out[n] = f.to_image()
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, "_frames_" + NAME); os.makedirs(tmp, exist_ok=True)
    font = ImageFont.truetype(FONT, 88)
    label_font = ImageFont.truetype("render/fonts/IBMPlexMono-Bold.ttf", 15)
    far, far_geo, P = build_standin()
    close_img, close_mask = close_plate()
    # the stand-in wide plate as a still (what a generated wide plate replaces)
    st = far_layer(far, far_geo, BEAN0, 0).convert("RGBA"); st.alpha_composite(bean_layer(P, BEAN0))
    st.convert("RGB").resize((960, 540), Image.LANCZOS).save(os.path.join(OUT, "standin_wide_plate.jpg"), quality=90)

    singer = av.open(SINGER); sst = singer.streams.video[0]; takes = singer.decode(sst)
    n0, n1 = round(CLIP_IN * FPS), round(CLIP_OUT * FPS)
    s0, s1 = math.ceil(S1_IN * FPS - 1e-6), math.ceil(S1_OUT * FPS - 1e-6)   # first frame of S1, first frame after it
    ctx = v3_frames(CLIP_IN, CLIP_OUT)
    stills = {}; ti = -1
    for n in range(n0, n1):
        t = n / FPS
        if not (s0 <= n < s1):
            fr = ctx[n].convert("RGB")
        else:
            k = round((t - S1_IN) * FPS)                                          # file time 0 = song 12.60
            while ti < k: tf = next(takes); ti += 1
            take = tf.to_image().convert("RGB")
            matte = Image.open(os.path.join(SINGER_MATTE, "%05d.png" % k)).convert("L")
            pl = planes(t); e = pl["e"]; sJ, cJ = pl["her"]; sB, cB = pl["bean"]
            # 1-2. far plane, Bean plane
            fr = far_layer(far, far_geo, sB, e).convert("RGBA")
            fr.alpha_composite(bean_layer(P, sB))
            # 3. the close plate dissolves in on the Bean plane, hidden in the fast part of the move
            dz = min(1.0, max(0.0, (e - 0.30) / 0.45))
            if dz > 0:
                cp = warp(close_img, sB, cB); cm = warp(close_mask, sB, cB).point(lambda v: int(v * dz))
                fr.paste(cp, (0, 0), cm)
            # 4. once the move has landed the take's own frame takes over (its plate is the close plate, alive)
            dl = min(1.0, max(0.0, (t - MOVE_T1) / (4 / FPS) + 1.0)) if e > 0.985 else 0.0
            if dl > 0:
                fr = Image.blend(fr.convert("RGB"), warp(take, sJ, cJ), dl).convert("RGBA")
            # 5. the arc lyric, cut into the Bean: rides the Bean plane
            fr.alpha_composite(warp(arc_lyric(t, font), sB, cB))
            # 6. her, by matte, about the bottom-centre
            fr.paste(warp(take, sJ, cJ), (0, 0), warp(matte, sJ, cJ))
            # v3's slow push over the whole shot
            g = V3_PUSH[0] + (V3_PUSH[1] - V3_PUSH[0]) * (t - S1_IN) / (S1_OUT - S1_IN)
            fr = warp(fr.convert("RGB"), g, (960, 540)).resize((960, 540), Image.LANCZOS)
            d = ImageDraw.Draw(fr)
            if e < 0.9:
                d.rectangle([8, 8, 318, 30], fill=INK); d.text((14, 11), "PREVIZ: stand-in wide plate (PIL)", font=label_font, fill=PAPER)
            for name, tt in [("start", S1_IN), ("hold_end", MOVE_T0), ("mid", (MOVE_T0 + MOVE_T1) / 2 - 0.16),
                             ("mid2", (MOVE_T0 + MOVE_T1) / 2), ("land", MOVE_T1), ("end", 15.5)]:
                if n == max(s0, round(tt * FPS)): stills[name] = (t, fr.copy(), sJ, sB)
        fr.save(os.path.join(tmp, "f%05d.jpg" % (n - n0)), quality=92)
    for name, (t, im, sJ, sB) in stills.items():
        im.save(os.path.join(OUT, "%s_%s_%.2f.jpg" % (NAME, name, t)), quality=90)
        print("still %-8s t=%.2f  her %.3f  bean %.3f (of end scale)" % (name, t, sJ, sB))
    order = [k for k in ("start", "hold_end", "mid", "mid2", "land", "end") if k in stills]
    sheet = Image.new("RGB", (960 * 3, 540 * 2), INK)
    for i, k in enumerate(order):
        sheet.paste(stills[k][1], ((i % 3) * 960, (i // 3) * 540))
    sheet.resize((1440, 540), Image.LANCZOS).save(os.path.join(OUT, NAME + "_sheet.jpg"), quality=88)
    out = os.path.join(OUT, NAME + ".mp4")
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(tmp, "f%05d.jpg"),
                    "-ss", "%.3f" % CLIP_IN, "-t", "%.3f" % (CLIP_OUT - CLIP_IN), "-i", V3, "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", out], check=True)
    for f in os.listdir(tmp): os.remove(os.path.join(tmp, f))
    os.rmdir(tmp)
    print("wrote", out, "%.1f MB" % (os.path.getsize(out) / 1e6))


if __name__ == "__main__":
    main()
