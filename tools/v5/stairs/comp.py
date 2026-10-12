#!/usr/bin/env python3
"""v5 note 0:13 & 2:35: lay the drawn impossible staircase into the plate, the two sing takes and the S1 wide (free).

    PY=~/Documents/moongazing/.venv/bin/python
    $PY tools/v5/stairs/comp.py CAND GUIDE        # e.g. cand_B1.jpg penrose_g3 (names inside media/sing/plates/stairs_v5/)
    $PY tools/v5/stairs/comp.py CAND GUIDE --wide # also the wide Bean plane + its pre-rendered push (bg.py) -> S1_wide/bg_1080_stairs/

Writes (old files untouched):
  media/sing/plates/plate_close_1_stairs.png       the close plate with only the stair region replaced (feathered mask)
  media/sing/plates/stairs_v5/overlay_S1.png       1920x1080 RGBA: the stair region in the S1 take's frame (v4_sync_1080_open)
  media/sing/plates/stairs_v5/overlay_V3S.png      same for the V3S take (v4_sync_1080)
  media/sing/plates/plate_wide_v4_stairs_bean.png  the wide Bean plane with the stair (only with --wide)
The sing takes have the plate baked in, so the timeline lays the overlay over the take (the take, its in-point, framing and
her matte are unchanged; she never comes within 100 px of the stair). The take's background is static (no drift: best
shift 0,0 over the whole take), so a still overlay registers; each take's fit to the close plate was measured on the
rooftop (blurred correlation 0.98): FIT below. Tone is matched per take and channel on the roof round the stair.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.chdir(ROOT)
D = "media/sing/plates/stairs_v5"
CLOSE = "media/sing/plates/plate_close_1.jpg"
CROP = (0, 768, 1024, 1536)                                   # the candidates' crop of the close plate (gen.py)
FIT = {  # take px = plate px * s + (tx, ty), fitted on the rooftop (x 20..360, y 700..1060 take px)
    "S1": dict(s=0.731, tx=-67.5, ty=-42.5, src="media/sing/S1/v4_sync_1080_open.mp4"),
    "V3S": dict(s=0.734, tx=-68.0, ty=-46.0, src="media/sing/V3S/v4_sync_1080.mp4"),
}
PASTE = (1350, 106)                                            # close plate in the wide plate (tools/v4B/bean/plate.py)


def frame(path, i=40):
    import av
    c = av.open(path)
    for k, f in enumerate(c.decode(video=0)):
        if k == i: return f.to_image().convert("RGB")


def mask_from_guide(guide, grow=10, feather=4):
    g = Image.open(f"{D}/{guide}_draw.png")
    import json
    box = json.load(open(f"{D}/{guide}_draw.json"))["box"]
    a = g.split()[3].point(lambda v: 255 if v > 8 else 0)
    full = Image.new("L", Image.open(CLOSE).size, 0)
    full.paste(a, (box[0], box[1]))
    full = full.filter(ImageFilter.MaxFilter(2 * grow + 1)).filter(ImageFilter.GaussianBlur(feather))
    return full


def close_plate(cand, guide):
    pl = Image.open(CLOSE).convert("RGB")
    c = Image.open(f"{D}/{cand}").convert("RGB").resize((CROP[2] - CROP[0], CROP[3] - CROP[1]), Image.LANCZOS)
    layer = pl.copy(); layer.paste(c, CROP[:2])
    m = mask_from_guide(guide)
    out = Image.composite(layer, pl, m)
    out.save("media/sing/plates/plate_close_1_stairs.png")
    m.save(f"{D}/mask_close.png")
    print("wrote media/sing/plates/plate_close_1_stairs.png")
    return out, m


def to_take(img, f, size=(1920, 1080), resample=Image.BICUBIC):
    """antialiased: Lanczos to the take's scale, then the sub-pixel shift"""
    s, tx, ty = f["s"], f["tx"], f["ty"]
    W, H = round(img.width * s), round(img.height * s)
    sx, sy = W / img.width, H / img.height
    small = img.resize((W, H), Image.LANCZOS)
    return small.transform(size, Image.AFFINE, (sx / s, 0, -tx * sx / s, 0, sy / s, -ty * sy / s), resample)


def overlay(key, plate, m):
    f = FIT[key]
    take = np.asarray(frame(f["src"]), np.float32)
    pt = to_take(plate, f); mt = to_take(m, f, resample=Image.BILINEAR)
    old = to_take(Image.open(CLOSE).convert("RGB"), f)
    # tone: per channel, take = a * plate + b, fitted on blurred pixels round the stair (ring 8..60 px outside the mask)
    mk = np.asarray(mt, np.float32) / 255
    ring = (np.asarray(mt.filter(ImageFilter.MaxFilter(61)), np.float32) > 0) & (mk < 0.02)
    ring[:, 380:] = False
    bo = np.asarray(old.filter(ImageFilter.GaussianBlur(3)), np.float32); bt = np.asarray(Image.fromarray(take.astype(np.uint8)).filter(ImageFilter.GaussianBlur(3)), np.float32)
    rgb = np.asarray(pt, np.float32).copy()
    for ch in range(3):
        x, y = bo[..., ch][ring], bt[..., ch][ring]
        a, b = np.polyfit(x, y, 1)
        rgb[..., ch] = rgb[..., ch] * a + b
        print(key, "ch", ch, "gain %.3f offset %.1f" % (a, b))
    img = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.5))   # the take's softness
    rgba = img.convert("RGBA"); rgba.putalpha(mt)
    rgba.save(f"{D}/overlay_{key}.png")
    # check stills: the take's frame with the overlay, full and 540p
    chk = Image.fromarray(take.astype(np.uint8)).convert("RGBA"); chk.alpha_composite(rgba)
    chk.convert("RGB").save(f"{D}/check_{key}_1080.jpg", quality=92)
    chk.convert("RGB").resize((960, 540), Image.LANCZOS).save(f"{D}/check_{key}_540.png")
    print("wrote", f"{D}/overlay_{key}.png")


def wide(plate, guide):
    m = mask_from_guide(guide, grow=3, feather=2)               # tight: round it the wide plate is the B2/close blend
    bean = Image.open("media/sing/plates/plate_wide_v4_bean.png").convert("RGBA")
    patch = plate.convert("RGBA")
    a = np.asarray(bean.split()[3]).copy()
    lay = bean.copy(); lay.paste(patch, PASTE)
    mm = Image.new("L", bean.size, 0); mm.paste(m, PASTE)
    out = Image.composite(lay, bean, mm); out.putalpha(Image.fromarray(a))
    out.save("media/sing/plates/plate_wide_v4_stairs_bean.png"); print("wrote media/sing/plates/plate_wide_v4_stairs_bean.png")
    sys.path.insert(0, "tools/v4B/bean")
    import bg
    bg.BEAN_IMG = "media/sing/plates/plate_wide_v4_stairs_bean.png"
    bg.OUT = "media/shots/S1_wide/bg_1080_stairs"
    bg.main()


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if len(a) < 2: sys.exit(__doc__)
    plate, m = close_plate(a[0], a[1])
    for k in FIT: overlay(k, plate, m)
    if "--wide" in sys.argv: wide(plate, a[1])
