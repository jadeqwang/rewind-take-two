#!/usr/bin/env python
"""YouTube thumbnails for REWIND (v5). Composes 1280x720 sRGB PNGs from real 1080p frames of the film plus the film's
own type (Anton = the slab sign face, IM Fell = the REWIND title face, Press Start 2P = the HUD), then a check sheet.

  tools/engrave/.venv/bin/python tools/thumbnails/make_thumbnails.py [A B C] [--sheet]

Sources (staged under media/thumbnails/src/, gitignored):
  A  E7_04_chasm @ 136.833  engine still without the residue ribbons:
       node render/engine/render.mjs --timeline tools/thumbnails/tl_e7_noribbon.mjs --stills 136.833
  B  B2_leap     @ 95.458   engine still
  C  F6c keyframe media/shots/F6c/kf_clean.jpg (2731x1536; the first frame of the take-3 sprint the film plays)
Notes and ranking: docs/revisions/v5/thumbnail.md
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageCms, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "sectionF"))
import dered  # noqa: E402  (red audit / fix shared with section F)

SRC = os.path.join(ROOT, "media", "thumbnails", "src")
OUT = os.path.join(ROOT, "deliverables", "thumbnails")
FONTS = os.path.join(ROOT, "render", "fonts")
W, H = 1280, 720
SRGB = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()

INK = (11, 11, 12)
PAPER = (236, 231, 220)
ORANGE = (240, 138, 36)
HUD = (244, 241, 234)


def font(name, size):
    f = {"anton": "anton-latin-400-normal.woff2", "fell": "IMFeENrm28P.ttf", "hud": "PressStart2P-Regular.ttf",
         "mono": "IBMPlexMono-Bold.ttf"}[name]
    return ImageFont.truetype(os.path.join(FONTS, f), size)


def load(path):
    return Image.open(path).convert("RGB")


def crop_to(img, box):
    """Crop box (x0, y0, x1, y1) in source px, resized to W x H (box must be 16:9)."""
    return img.crop(box).resize((W, H), Image.LANCZOS)


def text_layer(text, fnt, tracking=0):
    """Returns an L mask of the text set with extra tracking (px), tightly cropped, plus its baseline offset."""
    widths = [fnt.getlength(c) for c in text]
    total = int(sum(widths) + tracking * (len(text) - 1)) + 4
    asc, desc = fnt.getmetrics()
    m = Image.new("L", (total + 40, asc + desc + 40), 0)
    d = ImageDraw.Draw(m)
    x = 20
    for c, w in zip(text, widths):
        d.text((x, 20), c, font=fnt, fill=255)
        x += w + tracking
    bb = m.getbbox()
    return m.crop(bb)


def stamp_text(img, text, fnt, xy, fill, tracking=0, stroke=0, stroke_fill=INK, shadow=0, shadow_off=(0, 0),
               shadow_alpha=0.75, glow=0, glow_fill=PAPER, glow_alpha=0.9, anchor="lt", skew=0.0):
    """Draw text with an outer stroke, a soft drop shadow and an optional soft glow plate. xy is the anchor point:
    'lt' left-top, 'mt' middle-top, 'rt' right-top of the ink bbox."""
    m = text_layer(text, fnt, tracking)
    pad = stroke + max(glow, shadow) * 3 + 10
    big = Image.new("L", (m.width + 2 * pad, m.height + 2 * pad), 0)
    big.paste(m, (pad, pad))
    if skew:
        big = big.transform(big.size, Image.AFFINE, (1, skew, -skew * big.height / 2, 0, 1, 0), Image.BICUBIC)
    x, y = xy
    if anchor[0] == "m":
        x -= big.width // 2
    elif anchor[0] == "r":
        x -= big.width - pad
    else:
        x -= pad
    y -= pad
    a = np.asarray(big, np.float32) / 255
    body = a
    if stroke:
        k = 2 * stroke + 1
        ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
        outer = cv2.dilate(a, ker)
    else:
        outer = a
    layers = []
    if glow:
        g = cv2.GaussianBlur(cv2.dilate(a, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (glow, glow))), (0, 0), glow)
        layers.append((np.clip(g * 1.6, 0, 1) * glow_alpha, glow_fill, (0, 0)))
    if shadow:
        s = cv2.GaussianBlur(outer, (0, 0), shadow)
        layers.append((s * shadow_alpha, INK, shadow_off))
    layers.append((outer, stroke_fill, (0, 0)))
    layers.append((body, fill, (0, 0)))
    for alpha, col, (ox, oy) in layers:
        lay = Image.new("RGB", big.size, col)
        img.paste(lay, (x + ox, y + oy), Image.fromarray((np.clip(alpha, 0, 1) * 255).astype(np.uint8)))
    return (x + pad, y + pad, x + pad + m.width, y + pad + m.height)


def rewind_glyph(img, x, y, h, fill=ORANGE, stroke=6, stroke_fill=INK, gap=0.0):
    """The ◀◀ rewind glyph (two triangles pointing left), left-top at (x, y), height h."""
    w = h * 0.86
    lay = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(lay)
    for i in range(2):
        x0 = x + i * (w * (1 - gap) * 0.98)
        d.polygon([(x0, y + h / 2), (x0 + w, y), (x0 + w, y + h)], fill=255)
    a = np.asarray(lay, np.float32) / 255
    ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * stroke + 1, 2 * stroke + 1))
    outer = cv2.dilate(a, ker)
    img.paste(Image.new("RGB", img.size, stroke_fill), (0, 0), Image.fromarray((outer * 255).astype(np.uint8)))
    img.paste(Image.new("RGB", img.size, fill), (0, 0), Image.fromarray((a * 255).astype(np.uint8)))
    return x + w * (2 - gap) * 0.98


def ring(img, cx, cy, r, sweep=(200, 470), width=14, faint=4, fill=ORANGE, dot=18):
    """The film's rewind ring: a thin full circle plus a thick orange arc with a dot at its head (counter-clockwise)."""
    s = 3
    lay = Image.new("RGBA", (img.width * s, img.height * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    box = [(cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s]
    d.ellipse(box, outline=fill + (150,), width=faint * s)
    d.arc(box, sweep[0], sweep[1], fill=fill + (255,), width=width * s)
    a = np.deg2rad(sweep[0])
    hx, hy = cx + r * np.cos(a), cy + r * np.sin(a)
    d.ellipse([(hx - dot) * s, (hy - dot) * s, (hx + dot) * s, (hy + dot) * s], fill=fill + (255,))
    lay = lay.resize(img.size, Image.LANCZOS)
    img.paste(lay, (0, 0), lay)


def grade(img, contrast=1.0, sat=1.0, gamma=1.0):
    a = np.asarray(img, np.float32) / 255
    if gamma != 1.0:
        a = a ** gamma
    if sat != 1.0:
        g = a @ np.array([0.299, 0.587, 0.114], np.float32)
        a = g[..., None] + (a - g[..., None]) * sat
    if contrast != 1.0:
        a = (a - 0.5) * contrast + 0.5
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))


def vignette(img, strength=0.35, cx=0.5, cy=0.5, rx=0.75, ry=0.75, col=INK):
    yy, xx = np.mgrid[0:img.height, 0:img.width].astype(np.float32)
    d = np.sqrt(((xx / img.width - cx) / rx) ** 2 + ((yy / img.height - cy) / ry) ** 2)
    m = np.clip(d - 0.5, 0, 1) * strength * 2
    lay = Image.new("RGB", img.size, col)
    img.paste(lay, (0, 0), Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8)))


def red_fraction(img):
    """The section F audit (dered.py --check): hue within 15 deg of 0, saturation > 0.45, value > 0.2."""
    hsv = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0].astype(np.float32) * 2, hsv[..., 1] / 255.0, hsv[..., 2] / 255.0
    d = np.minimum(h, 360 - h)
    return float(((d < 15) & (s > 0.45) & (v > 0.2)).mean())


def dered_img(img):
    return Image.fromarray(dered.fix(np.asarray(img).copy(), "orange"))


def clean_spot(img, box, drop=5):
    """Inpaint a stray debris smudge on flat paper: pixels inside box darker than the box's border median by > drop."""
    a = np.asarray(img).copy()
    x0, y0, x1, y1 = box
    L = cv2.cvtColor(a, cv2.COLOR_RGB2GRAY).astype(np.float32)
    sub = L[y0:y1, x0:x1]
    ref = np.median(np.concatenate([sub[0], sub[-1], sub[:, 0], sub[:, -1]]))
    m = np.zeros(L.shape, np.uint8)
    m[y0:y1, x0:x1] = (sub < ref - drop).astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((7, 7), np.uint8))
    return Image.fromarray(cv2.inpaint(a, m, 6, cv2.INPAINT_TELEA))


def sharpen(img, amt=60, radius=1.2):
    return img.filter(ImageFilter.UnsharpMask(radius=radius, percent=amt, threshold=2))


# ---------------------------------------------------------------- the three thumbnails

TITLE = dict(tracking=6, stroke=9, shadow=10, shadow_off=(6, 8))


def thumb_A():
    """E7 ghost leap (2:16): Jade launches across the chasm, the stacked colour ghosts of every attempt behind her.
    Crop stops at x=1300 so the hotel sign (post-credits spoiler) stays out of frame."""
    # engine still without the residue ribbons, crop (520, 0, 1320, 450) -> A_crop_1600.png, then a faithful
    # nano-banana-pro clean-up upscale (thumbnail.md has the prompt) -> media/thumbnails/gen/v5_thumb_A_upscale.jpg
    up = os.path.join(ROOT, "media", "thumbnails", "gen", "v5_thumb_A_upscale.jpg")
    if os.path.exists(up):
        src = load(up)
        cw = round(src.height * 16 / 9)
        img = crop_to(src, ((src.width - cw) // 2, 0, (src.width - cw) // 2 + cw, src.height))
        img = sharpen(grade(img, contrast=1.1, sat=1.45), 30)
    else:
        src = load(os.path.join(SRC, "thumb_e7_noribbon_full_t136_833.png"))
        img = sharpen(grade(crop_to(src, (520, 0, 1320, 450)), contrast=1.1, sat=1.45), 80)
    img = dered_img(img)                                        # the saturation lift must not push skin into red
    img = clean_spot(img, (726, 540, 774, 620))                 # a grey debris smudge beside her legs in the source
    stamp_text(img, "REWIND", font("anton", 200), (30, 24), ORANGE, **TITLE)
    return img


def thumb_B():
    """B2 leap (1:35): Jade mid-air over the gap in the precision-platformer section, racing her graphite ghost."""
    src = load(os.path.join(SRC, "b2_leap_t95_458.png"))
    hud = src.crop((1300, 36, 1900, 148))                       # the film's own ghost-race HUD plate
    # the crop would clip the plate at the frame edge: fill its place with the same band of horizontal hatching from
    # just left of it (x 1000-1300), then paste the whole plate back inside the frame
    band = src.crop((1000, 30, 1300, 154))
    src = src.copy()
    for x in (1300, 1600):
        src.paste(band, (x, 30))
    img = crop_to(src, (430, 20, 1590, 672))
    img = dered_img(sharpen(grade(img, contrast=1.05)))
    hud = hud.resize((int(hud.width * 0.8), int(hud.height * 0.8)), Image.LANCZOS)
    img.paste(hud, (W - hud.width - 22, 20))
    stamp_text(img, "REWIND", font("anton", 210), (1250, 400), ORANGE, anchor="rt", **TITLE)
    return img


def thumb_C():
    """F6c sprint (3:15): full colour, the ghost stream of every past run in step behind her."""
    src = dered_img(load(os.path.join(ROOT, "media", "shots", "F6c", "kf_clean.jpg")))
    img = crop_to(src, (208, 82, 2684, 1475))                   # inside the keyframe's paper margin, exact 16:9
    img = dered_img(img)
    stamp_text(img, "REWIND", font("anton", 200), (30, 24), ORANGE, **TITLE)
    return img


def thumb_D():
    """E1_E2a dash (1:54): Jade flat out in a superman dash along the el tracks, the orange ghost of her last attempt
    behind her (the start of the 1:53 leap into the dodge roll)."""
    src = load(os.path.join(SRC, "e1_e2a_tracks_t114_333.png"))
    img = crop_to(src, (220, 30, 1900, 975))
    img = dered_img(sharpen(grade(img, contrast=1.06, sat=1.15), 40))
    stamp_text(img, "REWIND", font("anton", 200), (30, 470), ORANGE, **TITLE)
    return img


THUMBS = {"A": ("ghost_leap", thumb_A), "B": ("platform_leap", thumb_B), "C": ("ghost_sprint", thumb_C),
          "D": ("ghost_dash", thumb_D)}


def save(img, key):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f"rewind_thumb_{key}_{THUMBS[key][0]}.png")
    img.save(p, optimize=True, icc_profile=SRGB)
    kb = os.path.getsize(p) / 1024
    print(f"{p}  {kb:.0f} KB  red={red_fraction(img) * 100:.3f}%")
    return p


# ---------------------------------------------------------------- check sheet (mock YouTube dark mode)

YT_BG, YT_TXT, YT_SUB = (15, 15, 15), (241, 241, 241), (170, 170, 170)


def dummy(kind):
    """Plain stand-in thumbnails of the kind a music video competes with in a feed."""
    img = Image.new("RGB", (W, H))
    if kind == 0:     # moody lo-fi: dark blue-purple gradient, white serif title
        a = np.linspace(0, 1, W)[None, :, None]
        g = (np.array([30, 24, 60]) * (1 - a) + np.array([90, 60, 120]) * a) * np.ones((H, 1, 1))
        img = Image.fromarray(g.astype(np.uint8))
        stamp_text(img, "late night drive", font("fell", 130), (W // 2, 280), (240, 240, 240), anchor="mt")
    elif kind == 1:   # bright vlog: yellow field, black slab
        img = Image.new("RGB", (W, H), (250, 210, 40))
        d = ImageDraw.Draw(img)
        d.ellipse((760, 120, 1180, 540), fill=(230, 180, 140))
        stamp_text(img, "I TRIED IT", font("anton", 190), (60, 220), INK, stroke=0)
    else:             # grey photo-ish: soft noise and a white sans title
        rng = np.random.default_rng(3)
        n = cv2.GaussianBlur(rng.random((H // 8, W // 8)).astype(np.float32), (0, 0), 3)
        n = cv2.resize(n, (W, H)) * 120 + 60
        img = Image.fromarray(np.dstack([n, n * 1.05, n * 1.1]).clip(0, 255).astype(np.uint8))
        stamp_text(img, "OFFICIAL VIDEO", font("anton", 150), (W // 2, 260), (255, 255, 255), stroke=0, anchor="mt")
    return img


def rounded(img, r):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, img.width - 1, img.height - 1), r, fill=255)
    out = Image.new("RGB", img.size, YT_BG)
    out.paste(img, (0, 0), m)
    return out


def card(img, w, ts="4:04"):
    """A thumbnail at width w as YouTube shows it: rounded corners and the duration box at bottom right."""
    h = round(w * 9 / 16)
    t = rounded(img.resize((w, h), Image.LANCZOS), max(4, w // 28))
    fs = max(9, round(w * 0.045))
    f = font("mono", fs)
    tw = int(f.getlength(ts))
    d = ImageDraw.Draw(t, "RGBA")
    pad = max(2, fs // 4)
    m = max(3, w // 45)
    x1, y1 = w - m, h - m
    d.rounded_rectangle((x1 - tw - 2 * pad, y1 - fs - 2 * pad, x1, y1), max(2, fs // 4), fill=(0, 0, 0, 205))
    d.text((x1 - tw - pad, y1 - fs - pad - fs * 0.12), ts, font=f, fill=(255, 255, 255))
    return t


def build_sheet(thumbs):
    keys = sorted(thumbs)
    dummies = [(dummy(0), "late night drive (lofi mix)"), (dummy(1), "I tried it for 30 days"),
               (dummy(2), "Some Band - Song (Official Video)")]
    items = []
    for i, k in enumerate(keys):
        if i < len(dummies):
            items.append(("dummy", *dummies[i]))
        items.append((k, thumbs[k], "Jade Wang - Rewind (Official Music Video)"))
    gap, M = 40, 60
    SW = len(keys) * W + (len(keys) - 1) * gap + 2 * M
    sheet = Image.new("RGB", (SW, 3000), YT_BG)
    d = ImageDraw.Draw(sheet)
    hf, sf = font("mono", 34), font("mono", 22)
    y = 40
    d.text((M, y), "REWIND thumbnails: full size 1280x720", font=hf, fill=YT_TXT)
    y += 60
    for i, k in enumerate(keys):
        x = M + i * (W + gap)
        sheet.paste(thumbs[k], (x, y))
        d.text((x, y + H + 8), f"{k}: rewind_thumb_{k}_{THUMBS[k][0]}.png", font=sf, fill=YT_SUB)
    y += H + 70
    # desktop home grid: 320x180 cards, 3 per row x 2 rows, with title + channel lines
    d.text((M, y), "desktop home feed, 320x180 (dark mode)", font=hf, fill=YT_TXT)
    y += 60
    cw, ch, cg = 320, 180, 24
    tf, cf = font("mono", 15), font("mono", 13)
    for i, (k, im, title) in enumerate(items):
        x = M + (i % len(items)) * (cw + cg)
        sheet.paste(card(im, cw), (x, y))
        ImageDraw.Draw(sheet).ellipse((x, y + ch + 12, x + 30, y + ch + 42), fill=(70, 70, 70))
        d.text((x + 40, y + ch + 12), title[:30], font=tf, fill=YT_TXT)
        d.text((x + 40, y + ch + 34), "channel · 1.2K views", font=cf, fill=YT_SUB)
    y += ch + 90
    # mobile suggested list: 168x94 thumbnails beside two text lines, two columns
    d.text((M, y), "mobile up-next, 168x94 (actual pixels)", font=hf, fill=YT_TXT)
    y += 60
    y0 = y
    for i, (k, im, title) in enumerate(items):
        col, row = i // 4, i % 4
        x = M + col * 620
        yy = y0 + row * 112
        sheet.paste(card(im, 168), (x, yy))
        d.text((x + 182, yy + 4), title[:34], font=tf, fill=YT_TXT)
        d.text((x + 182, yy + 26), "channel · 1.2K views", font=cf, fill=YT_SUB)
    # 4x nearest-neighbour blow-up of the 168x94 cards, to judge them pixel by pixel
    bx = M + 1300
    d.text((bx, y - 60), "the same 168x94 pixels, 3x nearest", font=hf, fill=YT_TXT)
    for i, k in enumerate(keys):
        c = card(thumbs[k], 168).resize((504, 282), Image.NEAREST)
        sheet.paste(c, (bx + (i % 4) * 530, y + (i // 4) * 300))
    y = max(y0 + 4 * 112, y + 282) + 40
    sheet = sheet.crop((0, 0, SW, y))
    p = os.path.join(OUT, "check_sheet.png")
    sheet.save(p, optimize=True)
    print(p, sheet.size, f"{os.path.getsize(p) / 1024:.0f} KB")
    return sheet


def main():
    keys = [a for a in sys.argv[1:] if a in THUMBS] or list(THUMBS)
    made = {}
    for k in keys:
        made[k] = THUMBS[k][1]()
        save(made[k], k)
    if "--sheet" in sys.argv or len(keys) == len(THUMBS):
        for k in THUMBS:
            made.setdefault(k, load(os.path.join(OUT, f"rewind_thumb_{k}_{THUMBS[k][0]}.png")))
        build_sheet(made)


if __name__ == "__main__":
    main()
