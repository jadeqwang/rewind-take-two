#!/usr/bin/env python3
"""v5 round 2 (Jade 0:13 & 2:35: "can you just copy the one from later in the same video? the one inside the clock at
3:13?"): the F6b clock Penrose stair, lifted off its plate and set on the near rooftop of the Bean plate (free).

    PY=~/Documents/moongazing/.venv/bin/python
    $PY tools/v5/stairs2/comp.py            # close plate + the two take overlays + check stills
    $PY tools/v5/stairs2/comp.py --wide     # also the wide Bean plane and its pushed frames (bg.py)

The stair is not redrawn. Its pixels are those of media/shots/F6b/kf_v3_F6b_redraw_crop_dered.png (the 3:13 plate),
cut out with the engine's exact block faces (tools/sectionF/penrose_guide.py via lift.py), scaled uniformly (no
rotation, no shear: same viewing angle) and toned into the Bean's black-and-white engraving:
  - luminance only, mapped onto the Bean's paper and ink; per-face tone (tops paper, right faces lit, left faces shaded:
    the roof is lit from the right); the face's own hand hatching kept, plus vertical engraved lines at the roof's line
    period so the walls read as engraving at 540p (texture inside each face polygon only); outlines thickened.
  - the plate's own hatched cast shadow under and inside the loop, multiplied onto the roof (ticks of the clock face
    removed).
The old square stairwell under it is first removed by interpolating the roof's hatch lines across it along their own
direction (searched per pixel, about slope 0.46), so nothing of it shows in the loop's well or round the stair.

Writes (old files untouched):
  media/sing/plates/plate_close_1_stairs_clock.png
  media/sing/plates/stairs_v5/overlay_{S1,V3S}_clock.png, clock_check_{S1,V3S}_{1080.jpg,540.png}, clock_lift.png
  media/sing/plates/plate_wide_v4_stairs_clock_bean.png + media/shots/S1_wide/bg_1080_stairs_clock/   (--wide)
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as nd

ROOT = "/home/jade/Documents/rewind-take-two"
os.chdir(ROOT)
sys.path.insert(0, "tools/v5/stairs2")
import lift  # noqa: E402
import importlib.util  # noqa: E402
_sp = importlib.util.spec_from_file_location("stairs1_comp", "tools/v5/stairs/comp.py")
c1 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(c1)   # v5-stairs round 1: FIT, frame(), to_take(), PASTE

D = "media/sing/plates/stairs_v5"
CLOSE = "media/sing/plates/plate_close_1.jpg"
# placement on the close plate: the stair's bbox centre and width (close plate px)
CX, CY, W = float(os.environ.get("ST_CX", 302)), float(os.environ.get("ST_CY", 1218)), float(os.environ.get("ST_W", 325))
OLD = [(127, 1262), (215, 1116), (366, 1185), (288, 1344)]      # the old square stairwell with its drawn base (v5-stairs findings, widened)
PAPER, INK = np.array([250., 241., 230.]), np.array([8., 5., 2.])
CURVE = tuple(float(x) for x in os.environ.get("ST_CURVE", "0.08,0.92,1.0").split(","))   # wall levels: black, white, gamma


def _walk(H, a, xs, ys, slope, offs=(2,)):
    """for each hole pixel, the first pixel outside the hole along +-(1, slope): distance and samples at offs beyond"""
    d = np.array([1.0, slope]) / np.hypot(1, slope)
    res = {}
    for sgn in (-1, 1):
        dist = np.full(len(xs), np.nan, np.float32)
        val = np.zeros((len(offs), len(xs), 3), np.float32)
        for t in range(1, 700):
            px, py = xs + sgn * d[0] * t, ys + sgn * d[1] * t
            ix, iy = np.clip(np.round(px).astype(int), 0, H.shape[1] - 1), np.clip(np.round(py).astype(int), 0, H.shape[0] - 1)
            out = ~H[iy, ix] & np.isnan(dist)
            if out.any():
                for j, o in enumerate(offs):
                    for c in range(3):
                        val[j, out, c] = nd.map_coordinates(a[..., c], [py[out] + sgn * d[1] * o, px[out] + sgn * d[0] * o], order=1)
                dist[out] = t
            if not np.isnan(dist).any():
                break
        res[sgn] = (dist, val)
    return res


def fill_old(pl):
    """remove the old stairwell: every hole pixel = the roof's hatch line through it, interpolated between the hole's
    two edges along the line direction. The direction is searched per pixel (slopes 0.20..0.62): the one whose two
    edge profiles agree best, so both ends sample the same engraved line and nothing ghosts"""
    a = np.asarray(pl, np.float32)
    H = Image.new("L", pl.size, 0)
    ImageDraw.Draw(H).polygon(OLD, fill=255)
    H = np.asarray(H.filter(ImageFilter.MaxFilter(57)), bool)
    ys, xs = np.nonzero(H)
    y0, x0 = ys.min(), xs.min()
    slopes = np.arange(0.20, 0.625, 0.015)
    offs = (2, 4, 6, 8, 10)
    mis_all, fill_all = [], []
    for sl_ in slopes:
        r = _walk(H, a, xs, ys, sl_, offs)
        (d0, v0), (d1, v1) = r[-1], r[1]
        mis = np.abs(v0.mean(-1) - v1.mean(-1)).mean(0)
        img = np.zeros((ys.max() - y0 + 1, xs.max() - x0 + 1), np.float32); cnt = np.zeros_like(img)
        img[ys - y0, xs - x0] = mis; cnt[ys - y0, xs - x0] = 1
        mis_all.append((nd.gaussian_filter(img, 6) / np.maximum(nd.gaussian_filter(cnt, 6), 1e-3))[ys - y0, xs - x0])
        wgt = (d1 / (d0 + d1))[:, None]
        fill_all.append(v0[0] * wgt + v1[0] * (1 - wgt))
    # best slope per pixel, then smoothed into a gently varying direction field (the roof's lines fan slowly)
    k = np.argmin(np.stack(mis_all), 0)
    img = np.zeros((ys.max() - y0 + 1, xs.max() - x0 + 1), np.float32); cnt = np.zeros_like(img)
    img[ys - y0, xs - x0] = slopes[k]; cnt[ys - y0, xs - x0] = 1
    sm = (nd.gaussian_filter(img, 25) / np.maximum(nd.gaussian_filter(cnt, 25), 1e-3))[ys - y0, xs - x0]
    k = np.clip(np.round((sm - slopes[0]) / 0.015).astype(int), 0, len(slopes) - 1)
    fill = np.stack(fill_all)[k, np.arange(len(xs))]
    print("old stairwell fill: slope %.3f..%.3f" % (sm.min(), sm.max()))
    b = a.copy()
    b[ys, xs] = fill
    return Image.fromarray(np.clip(b, 0, 255).astype(np.uint8)), H


def lift_stair():
    """the stair from the 3:13 plate in grey engraving: (rgb float HxWx3 0..255, alpha blocks 0..1, shadow mult 0..1),
    at plate (2400 px) scale, cropped to a box round the stair"""
    src = np.asarray(Image.open(lift.PLATE).convert("RGB"), np.float32)
    lum = src @ np.array([0.299, 0.587, 0.114], np.float32)
    faces = lift.faces()
    lab = Image.new("L", (2400, 1350), 0)
    dl = ImageDraw.Draw(lab)
    kinds = {"T": 1, "R": 2, "L": 3}
    for pts, k in faces:                                    # painter's order as drawn, so the label is the visible face
        dl.polygon(pts, fill=kinds[k])
    lab = np.asarray(lab)
    blocks = lift.block_mask(grow=2)
    x0, y0, x1, y1 = blocks.getbbox()
    box = (x0 - 30, y0 - 30, x1 + 30, y1 + 90)
    sl = (slice(box[1], box[3]), slice(box[0], box[2]))
    L = lum[sl]; lb = lab[sl]
    # 0 = ink, 1 = paper, from the plate's own range (tops' paper ~233, darkest ink ~35)
    v = np.clip((L - 35) / (233 - 35), 0, 1)
    vb = np.clip((nd.gaussian_filter(L, 1.2) - 35) / (233 - 35), 0, 1)
    # outlines: the plate's dark edge lines thickened by one px (min filter) so they carry at the Bean's line weight
    edge = nd.minimum_filter(vb, 3)
    # the plate's own tones (its light comes from the left: left faces light, right faces dark), contrast raised
    # toward the Bean's ink-on-paper; the walls' own vertical hand hatching is what shows
    out = np.clip((v - CURVE[0]) / (CURVE[1] - CURVE[0]), 0, 1) ** CURVE[2]
    out = np.where(lb == 1, v, out)                          # tops stay paper
    edges = (edge < 0.45) & (lb > 0)
    out[edges] = np.minimum(out[edges], edge[edges] * 0.6)
    a = np.asarray(blocks, np.float32)[sl] / 255
    a = nd.gaussian_filter(a, 0.8)
    # shadow: the plate's cast hatching round and inside the loop, as a multiplier (1 = no shadow)
    bm = np.asarray(lift.block_mask(), bool)[sl]
    filled = nd.binary_fill_holes(nd.binary_dilation(bm, iterations=4))
    down = np.zeros_like(bm)
    for dy in range(0, 56, 2):
        down |= np.roll(bm, dy, axis=0)
    reg = (down | filled) & ~bm
    dark = vb < 0.35
    ticks = nd.binary_opening(dark, structure=np.ones((5, 5)))  # thick bars = clock ticks / rim, not hatching
    ticks = nd.binary_dilation(ticks, iterations=8)
    reg &= ~ticks
    regs = nd.gaussian_filter(reg.astype(np.float32), 5) * reg
    paper_loc = np.clip(nd.maximum_filter(nd.gaussian_filter(L, 1), 25), 150, 255)
    sh = np.clip(L / paper_loc, 0, 1)
    sh = 1 - (1 - sh) * 0.85 * regs
    sh = np.where(bm, 1.0, sh)
    rgb = INK + out[..., None] * (PAPER - INK)
    return rgb, a, sh, box


def place(pl_size, rgb, a, sh, box):
    """scale the lifted stair to width W and centre it at (CX, CY) on the close plate (uniform scale only)"""
    s = W / 728.0                                             # 728 = the blocks' bbox width on the 3:13 plate
    bb = lift.block_mask().getbbox()
    bcx, bcy = (bb[0] + bb[2]) / 2 - box[0], (bb[1] + bb[3]) / 2 - box[1]
    ox, oy = CX - bcx * s, CY - bcy * s
    inv = (1 / s, 0, -ox / s, 0, 1 / s, -oy / s)

    def tf(arr, fill):
        h, w = arr.shape[:2]
        im = Image.fromarray(arr.astype(np.float32), "F")
        # pre-shrink with a box filter so the fine hatching averages instead of aliasing, then the exact placement
        sw, shh = max(1, round(w * s)), max(1, round(h * s))
        small = im.resize((sw, shh), Image.BOX)
        sx, sy = sw / w, shh / h
        t = small.transform(pl_size, Image.AFFINE, (sx / s, 0, -ox * sx / s, 0, sy / s, -oy * sy / s), Image.BICUBIC, fillcolor=fill)
        return np.asarray(t, np.float32)
    rgbp = np.stack([tf(rgb[..., c], 0) for c in range(3)], -1)
    ap = np.clip(tf(a, 0), 0, 1)
    shp = np.clip(tf(sh, 1), 0, 1)
    return rgbp, ap, shp


def close_plate():
    pl = Image.open(CLOSE).convert("RGB")
    filled, H = fill_old(pl)
    rgb, a, sh, box = lift_stair()
    Image.fromarray(np.clip(rgb * a[..., None] + 255 * (1 - a[..., None]) * sh[..., None], 0, 255).astype(np.uint8)).save(f"{D}/clock_lift.png")
    rgbp, ap, shp = place(pl.size, rgb, a, sh, box)
    base = np.asarray(filled, np.float32) * shp[..., None]
    out = rgbp * ap[..., None] + base * (1 - ap[..., None])
    outi = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    outi.save("media/sing/plates/plate_close_1_stairs_clock.png")
    # changed-region mask for the overlays: old hole + stair + shadow
    m = (H | (ap > 0.004) | (shp < 0.995)).astype(np.uint8) * 255
    m = Image.fromarray(m).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(3))
    m.save(f"{D}/clock_mask_close.png")
    print("wrote media/sing/plates/plate_close_1_stairs_clock.png; stair box",
          Image.fromarray((ap > 0.01).astype(np.uint8) * 255).getbbox())
    return outi, m


def run_overlays(plate, m):
    """same fit and per-channel tone match as round 1 (tools/v5/stairs/comp.py overlay()), under the new names"""
    for key, f in c1.FIT.items():
        take = np.asarray(c1.frame(f["src"]), np.float32)
        pt = c1.to_take(plate, f); mt = c1.to_take(m, f, resample=Image.BILINEAR)
        old = c1.to_take(Image.open(CLOSE).convert("RGB"), f)
        mk = np.asarray(mt, np.float32) / 255
        ring = (np.asarray(mt.filter(ImageFilter.MaxFilter(61)), np.float32) > 0) & (mk < 0.02)
        ring[:, 380:] = False
        bo = np.asarray(old.filter(ImageFilter.GaussianBlur(3)), np.float32)
        bt = np.asarray(Image.fromarray(take.astype(np.uint8)).filter(ImageFilter.GaussianBlur(3)), np.float32)
        rgb = np.asarray(pt, np.float32).copy()
        for ch in range(3):
            x, y = bo[..., ch][ring], bt[..., ch][ring]
            ga, gb = np.polyfit(x, y, 1)
            rgb[..., ch] = rgb[..., ch] * ga + gb
            print(key, "ch", ch, "gain %.3f offset %.1f" % (ga, gb))
        img = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.5))
        rgba = img.convert("RGBA"); rgba.putalpha(mt)
        rgba.save(f"{D}/overlay_{key}_clock.png")
        chk = Image.fromarray(take.astype(np.uint8)).convert("RGBA"); chk.alpha_composite(rgba)
        chk.convert("RGB").save(f"{D}/clock_check_{key}_1080.jpg", quality=92)
        chk.convert("RGB").resize((960, 540), Image.LANCZOS).save(f"{D}/clock_check_{key}_540.png")
        print("wrote", f"{D}/overlay_{key}_clock.png")


def wide(plate, m):
    bean = Image.open("media/sing/plates/plate_wide_v4_bean.png").convert("RGBA")
    a = np.asarray(bean.split()[3]).copy()
    lay = bean.copy(); lay.paste(plate.convert("RGBA"), c1.PASTE)
    mm = Image.new("L", bean.size, 0); mm.paste(m, c1.PASTE)
    out = Image.composite(lay, bean, mm); out.putalpha(Image.fromarray(a))
    out.save("media/sing/plates/plate_wide_v4_stairs_clock_bean.png"); print("wrote media/sing/plates/plate_wide_v4_stairs_clock_bean.png")
    sys.path.insert(0, "tools/v4B/bean")
    import bg
    bg.BEAN_IMG = "media/sing/plates/plate_wide_v4_stairs_clock_bean.png"
    bg.OUT = "media/shots/S1_wide/bg_1080_stairs_clock"
    bg.main()


if __name__ == "__main__":
    plate, m = close_plate()
    if "--no-takes" not in sys.argv:
        run_overlays(plate, m)
    if "--wide" in sys.argv:
        wide(plate, m)
