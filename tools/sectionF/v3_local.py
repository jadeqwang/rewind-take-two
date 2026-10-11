"""Section F v3: local (free) keyframe touch-ups the image model would not make.
  patch(im, cx, cy, r, rot)   canon sleeve roundel: white disc, black ring, '1420' / 'MHz'
  recolor(im, box, hue_from, hue_to)   e.g. a pink eraser -> pale blue
  paste(im, other, box, feather)       take a region from another aligned keyframe
Run: $PY tools/sectionF/v3_local.py   (writes kf_v3_<SHOT>_final.png next to the inputs)
"""
import colorsys
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = "/home/jade/Documents/rewind-take-two"
S = os.path.join(ROOT, "media/shots")
FONT = os.path.join(ROOT, "render/fonts/Overpass[wght].ttf")
if not os.path.exists(FONT):
    FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def patch(im, cx, cy, r, rot=0, squash=1.0):
    k = 4
    R = int(r * k)
    p = Image.new("RGBA", (2 * R + 8, 2 * R + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(p)
    c = R + 4
    d.ellipse([c - R, c - R, c + R, c + R], fill=(246, 244, 238, 255), outline=(20, 20, 22, 255), width=max(3, R // 9))
    f = ImageFont.truetype(FONT, int(R * 0.62))
    try:
        f.set_variation_by_axes([800])
    except Exception:  # noqa: BLE001
        pass
    for txt, dy in (("1420", -0.30), ("MHz", 0.34)):
        w = d.textlength(txt, font=f)
        d.text((c - w / 2, c + dy * R - R * 0.36), txt, font=f, fill=(20, 20, 22, 255))
    p = p.resize((int(p.width * squash), p.height), Image.LANCZOS).rotate(rot, resample=Image.BICUBIC, expand=True)
    p = p.resize((p.width // k, p.height // k), Image.LANCZOS)
    im.paste(p, (int(cx - p.width / 2), int(cy - p.height / 2)), p)
    return im


def recolor(im, box, pick, to_rgb, tol=28, sat_min=0.18):
    """Inside box, pixels whose hue is within tol degrees of pick (and saturated) take to_rgb's hue/saturation."""
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255
    x0, y0, x1, y1 = box
    reg = a[y0:y1, x0:x1]
    mx, mn = reg.max(-1), reg.min(-1)
    v, sat = mx, (mx - mn) / np.maximum(mx, 1e-5)
    r, g, b = reg[..., 0], reg[..., 1], reg[..., 2]
    d = np.maximum(mx - mn, 1e-5)
    h = np.where(mx == r, (g - b) / d % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    dist = np.minimum(abs(h - pick), 360 - abs(h - pick))
    m = ((dist < tol) & (sat > sat_min) & (v > 0.45)).astype(np.float32)
    m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 255
    th, tl, ts = colorsys.rgb_to_hls(*[c / 255 for c in to_rgb])
    out = reg.copy()
    lum = reg.mean(-1)
    tgt = np.stack([np.full_like(lum, c / 255) for c in to_rgb], -1) * (lum / max(1e-5, lum[m > 0.5].mean() if (m > 0.5).any() else 1))[..., None]
    out = reg * (1 - m[..., None]) + np.clip(tgt, 0, 1) * m[..., None]
    a[y0:y1, x0:x1] = out
    return Image.fromarray((a * 255).round().astype(np.uint8))


def paste(im, other, box, feather=14):
    x0, y0, x1, y1 = box
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rectangle([x0 + feather, y0 + feather, x1 - feather, y1 - feather], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(feather / 2))
    return Image.composite(other.convert("RGB").resize(im.size), im.convert("RGB"), m)


if __name__ == "__main__":
    import sys
    which = sys.argv[1:] or ["F7c", "F8"]
    if "F7c" in which:
        im = Image.open(f"{S}/F7c/kf_v3_F7c_r3.jpg").convert("RGB")
        im = recolor(im, (880, 280, 985, 375), 350, (150, 196, 232))          # pink eraser -> pale blue
        im = patch(im, 1541, 300, 26, rot=8, squash=0.9)
        im.save(f"{S}/F7c/kf_v3_F7c_final.png")
    if "F8" in which:
        r3 = Image.open(f"{S}/F8/kf_v3_F8_r3.png").convert("RGB")
        r2 = Image.open(f"{S}/F8/kf_v3_F8_r2.jpg").convert("RGB")
        im = paste(r3, r2, (1230, 110, 1560, 350))                              # r3 put a second pair of headphones on her ears
        im = recolor(im, (1280, 320, 1480, 440), 8, (238, 112, 26), tol=13, sat_min=0.55)   # red headphones -> canon orange
        im = recolor(im, (1150, 700, 1620, 1420), 8, (238, 112, 26), tol=13, sat_min=0.6)   # red straps -> orange
        im = patch(im, 1535, 518, 34, rot=-4, squash=0.88)
        im.save(f"{S}/F8/kf_v3_F8_final.png")
