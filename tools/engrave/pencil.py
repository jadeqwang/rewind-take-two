"""Colored-pencil and gold-leaf layers for the engraving (GPU, torch).

Strokes
  Tileable stroke textures (static noise filtered with long, thin oriented kernels in the Fourier
  domain, one per orientation bin and pencil layer) are sampled through *advected texture
  coordinates*: two UV fields are carried along with the background optical flow and reset in
  turn, then cross-faded (Neyret-style texture advection). The grain sticks to the world without
  the blur that repeatedly warping a texture would cause, and stroke direction follows the
  hatch flow field (theta) plus a per-layer offset.

Pigment
  Each pencil layer multiplies the paper by a hue-preserving, value-lifted version of the source
  colour (or a palette gradient map), with coverage = stroke texture thresholded by pressure, and
  masked by the paper tooth, so the paper shows through and overlapping layers build up
  (layered, not a flat wash). Neutral source areas get no pressure: the paper stays clean.

Gold leaf
  A crinkled foil height field (sampled through the same advected UVs, so it is attached to the
  surface) is shaded with a slowly orbiting light: a broad sheen plus flakes that twinkle smoothly
  over time.
"""
from __future__ import annotations

import math

import torch
import torch.nn.functional as F

from engrave_core import gblur, smoothstep, warp


def _hex(c: str):
    c = c.strip().lstrip("#")
    return tuple(int(c[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


PALETTES = {
    # Jade's residue ribbon: orange -> sky blue
    "residue": ["#2b3a67", "#3f7cc4", "#e8572a", "#f08a24", "#f2c14e", "#8fbfe8"],
    # Klimt: deep teal / oxblood / ochre / gold
    "klimt": ["#1d3b3a", "#6b2d2a", "#a3542b", "#c9962f", "#e7c35a", "#f3e2a0"],
    # Kandinsky primaries
    "kandinsky": ["#1b2a6b", "#c0262d", "#2f7d4f", "#e9b62c", "#e46a9b", "#6fb7e0"],
}


def parse_palette(spec: str | None):
    if not spec:
        return None
    cols = PALETTES.get(spec, None) or spec.split(",")
    return torch.tensor([_hex(c) for c in cols], dtype=torch.float32)


class Pencil:
    def __init__(self, h, w, period, device="cuda", seed=11, bins=12, layers=3, reset_frames=48,
                 stroke_len=None, palette=None, paper=(0.953, 0.929, 0.871)):
        self.h, self.w, self.dev = h, w, device
        self.P = period
        self.K = bins
        self.L = layers
        self.T = reset_frames
        self.offsets = [0.0, math.radians(22), math.radians(-34)][:layers]
        self.palette = parse_palette(palette).to(device) if palette else None
        pn = torch.tensor(paper, device=device)
        self.paper_norm = (pn / pn.max()).view(1, 3, 1, 1)
        gen = torch.Generator().manual_seed(seed)
        sl = stroke_len or 4.5 * period         # stroke length (sigma along), px
        sw = max(0.6, 0.2 * period)             # stroke width (sigma across), px
        # tileable textures: (L, K, H, W) in [0,1], roughly uniform
        tex = []
        fy = torch.fft.fftfreq(h).view(-1, 1)
        fx = torch.fft.rfftfreq(w).view(1, -1)
        for l in range(layers):
            noise = torch.randn(h, w, generator=gen)
            N = torch.fft.rfft2(noise)
            ks = []
            for k in range(bins):
                a = math.pi * k / bins
                # frequency along the stroke is suppressed by the long sigma
                fu = fx * math.cos(a) + fy * math.sin(a)
                fv = -fx * math.sin(a) + fy * math.cos(a)
                G = torch.exp(-2 * math.pi ** 2 * ((fu * sl) ** 2 + (fv * sw) ** 2))
                t = torch.fft.irfft2(N * G, s=(h, w))
                t = (t - t.mean()) / (t.std() + 1e-8)
                ks.append(0.5 * (1 + torch.erf(t / math.sqrt(2))))  # gaussian -> uniform
            tex.append(torch.stack(ks))
        self.tex = torch.stack(tex).to(device).half()  # (L,K,H,W)
        # paper tooth (static: it is the paper) and foil height (advected with the surface)
        tooth = torch.randn(1, 1, h, w, generator=gen).to(device)
        tooth = gblur(tooth, 0.7) * 0.7 + gblur(torch.randn(1, 1, h, w, generator=gen).to(device), 2.0) * 1.6
        self.tooth = 0.5 * (1 + torch.erf((tooth - tooth.mean()) / (tooth.std() * math.sqrt(2))))
        foil = torch.zeros(1, 1, h, w)
        for s, amp in ((period * 4, 1.0), (period * 1.6, 0.55), (period * 0.6, 0.3)):
            n = torch.fft.irfft2(torch.fft.rfft2(torch.randn(h, w, generator=gen)) *
                                 torch.exp(-2 * math.pi ** 2 * ((fx * s) ** 2 + (fy * s) ** 2)), s=(h, w))
            foil[0, 0] += amp * n / (n.std() + 1e-8)
        self.foil = foil.to(device)
        self.flake = torch.rand(1, 2, h, w, generator=gen).to(device)  # (threshold, phase)
        yy, xx = torch.meshgrid(torch.arange(h, device=device, dtype=torch.float32),
                                torch.arange(w, device=device, dtype=torch.float32), indexing="ij")
        self.ident = torch.stack([xx, yy])[None]
        self.reset()

    def reset(self):
        self.wb = None
        self.uv = [self.ident.clone(), self.ident.clone()]
        self.t = 0
        self.pig_prev = None

    # ------------------------------------------------------------------------------------------
    def _sample(self, tex, uv):
        """Sample a tileable (1,C,H,W) texture at pixel coords uv (1,2,H,W) with wrap-around."""
        pad = 2
        tp = F.pad(tex, (pad, pad, pad, pad), mode="circular")
        x = torch.remainder(uv[:, 0], self.w) + pad
        y = torch.remainder(uv[:, 1], self.h) + pad
        gx = x / (self.w + 2 * pad - 1) * 2 - 1
        gy = y / (self.h + 2 * pad - 1) * 2 - 1
        return F.grid_sample(tp, torch.stack([gx, gy], -1).to(tp.dtype), mode="bilinear",
                             padding_mode="border", align_corners=True)

    def _advance(self, flow):
        # carry both UV layers with the flow; reset each in turn at zero weight
        if flow is not None:
            # grain needs coherent motion, not per-pixel detail: noisy flow in flat areas (sky)
            # would marble the strokes
            fs = gblur(flow, self.h / 36)
            self.uv = [warp(u, fs) for u in self.uv]
        self.t += 1
        ph = (self.t % self.T) / self.T
        if self.t % self.T == 0:
            self.uv[0] = self.ident.clone()
        if (self.t + self.T // 2) % self.T == 0:
            self.uv[1] = self.ident.clone()
        wa = math.sin(math.pi * ph) ** 2
        return [wa, 1.0 - wa]

    def _strokes(self, layer, theta, uvw):
        """Stroke texture value for one pencil layer along theta (+offset), uv cross-faded."""
        K = self.K
        th = torch.remainder(theta + self.offsets[layer], math.pi)
        idx = th / (math.pi / K)
        i0 = torch.floor(idx).long() % K
        i1 = (i0 + 1) % K
        f = (idx - torch.floor(idx))
        out = 0
        for uv, wgt in zip(self.uv, uvw):
            if wgt < 1e-3:
                continue
            s = self._sample(self.tex[layer][None], uv).float()  # (1,K,H,W)
            v = torch.gather(s, 1, i0) * (1 - f) + torch.gather(s, 1, i1) * f
            out = out + wgt * v
        # the cross-fade of two uniform variables is not uniform: re-spread around 0.5
        tot = uvw[0] ** 2 + uvw[1] ** 2
        return (0.5 + (out - 0.5) / math.sqrt(max(tot, 0.5))).clamp(0, 1)

    # ------------------------------------------------------------------------------------------
    def pigment(self, src, flow):
        """Pencil colour + pressure from a colour source (or a palette gradient map)."""
        # de-ink: the source's own dark linework must not muddy the pigment (the engraving redraws it)
        v = src.max(1, keepdim=True).values
        wgt = v ** 4 + 1e-3
        src = gblur(src * wgt, self.P * 0.6) / gblur(wgt, self.P * 0.6)
        # white balance against the source's own paper (image models draw on warm paper): the
        # paper tone must read as neutral, or every blank area would get beige strokes
        lum = (0.2126 * src[:, 0:1] + 0.7152 * src[:, 1:2] + 0.0722 * src[:, 2:3])
        bright = lum > torch.quantile(lum.flatten()[::7], 0.9)
        if bright.sum() > 100:
            ref = torch.stack([src[:, c:c + 1][bright].median() for c in range(3)])
            ref = ref / ref.max()
            self.wb = ref if getattr(self, "wb", None) is None else 0.9 * self.wb + 0.1 * ref
            src = (src / self.wb.view(1, 3, 1, 1).clamp(min=0.5)).clamp(0, 1)
        mx = src.max(1, keepdim=True).values
        mn = src.min(1, keepdim=True).values
        chroma = mx - mn
        if self.palette is not None:
            lum = (0.2126 * src[:, 0:1] + 0.7152 * src[:, 1:2] + 0.0722 * src[:, 2:3]).clamp(0, 1)
            pal = self.palette  # (n,3)
            n = pal.shape[0]
            # gray source: gradient map by luminance; coloured source: snap to the nearest palette hue
            x = smoothstep(0.08, 0.88, lum) * (n - 1)
            i0 = torch.floor(x).long().clamp(0, n - 2)
            fr = x - i0
            grad = pal[i0[:, 0]].permute(0, 3, 1, 2) * (1 - fr) + pal[i0[:, 0] + 1].permute(0, 3, 1, 2) * fr
            sn = src / (src.max(1, keepdim=True).values + 1e-3)
            pn = pal / pal.max(1, keepdim=True).values
            d = ((sn[:, :, None] - pn.t()[None, :, :, None, None]) ** 2).sum(1)  # (1,n,H,W)
            near = pal[d.argmin(1)].permute(0, 3, 1, 2)
            cw = smoothstep(0.06, 0.16, chroma)
            pig = grad * (1 - cw) + near * cw
            pig = 0.8 * pig + 0.2  # pencil over a gray world: keep it airy, the ink carries value
            press = (0.3 + 0.3 * (1 - lum)) * (1 - cw) + smoothstep(0.03, 0.2, chroma) * cw
        else:
            # raw source colour; step() inverts the multiply so the strokes average out to it
            pig = src.clamp(0, 1)
            press = smoothstep(0.03, 0.2, chroma) * (0.8 + 0.4 * (1 - mx))
        press = gblur(press, self.P * 0.4)
        pig = gblur(pig, self.P * 0.25)
        st = torch.cat([pig, press], 1)
        if self.pig_prev is not None:
            pp = warp(self.pig_prev, flow) if flow is not None else self.pig_prev
            d = (st - pp).abs().amax(1, keepdim=True)
            a = 0.5 * (1 - smoothstep(0.1, 0.3, d))
            st = a * pp + (1 - a) * st
        self.pig_prev = st
        return st[:, :3], st[:, 3:4].clamp(0, 1)

    @torch.no_grad()
    def step(self, theta, flow, src, mask, gold=None):
        """Returns (paper multiplier (1,3,H,W), gold rgb, gold alpha, pencil coverage)."""
        uvw = self._advance(flow)
        pig, press = self.pigment(src, flow)
        press = press * mask
        # expected stroke coverage for this pressure -> pigment that reproduces the source colour
        # on average (pencil is more saturated than the area it tints; paper shows between strokes)
        a_exp = 1.0
        for l in range(self.L):
            c = (press * 1.5 - 0.33 * l).clamp(0, 1)
            a_exp = a_exp * (1 - c * 0.7 * (0.62 + 0.18 * l))
        a_exp = (1 - a_exp).clamp(min=0.25)
        if self.palette is None:
            # undo the warm paper tint (it multiplies under the pigment), then solve for the pencil
            # colour whose stroke coverage averages to the source colour
            pig = (pig / self.paper_norm).clamp(0, 1)
            pig = (1 - 0.75 * (1 - pig) / a_exp).clamp(0, 1)
        mult = torch.ones_like(src)
        cov_all = torch.zeros_like(press)
        for l in range(self.L):
            # pressure decides how many layers build up and how dense each is
            c = (press * 1.5 - 0.33 * l).clamp(0, 1)
            if c.max() < 0.01:
                continue
            s = self._strokes(l, theta, uvw)
            cov = smoothstep(1 - c - 0.1, 1 - c + 0.1, s) * (c > 0.01).float()
            # paper tooth: light pressure skips the valleys, heavy pressure fills them
            cov = cov * smoothstep(0.42 - 0.5 * c, 0.62 - 0.5 * c, self.tooth)
            dens = 0.62 + 0.18 * l
            mult = mult * (1 - cov * dens * (1 - pig))
            cov_all = torch.maximum(cov_all, cov)
        gold_rgb = galpha = None
        if gold is not None and gold.max() > 0.01:
            gold_rgb = self._foil(uvw)
            galpha = gold
        return mult, gold_rgb, galpha, cov_all

    def _foil(self, uvw):
        h = 0
        for uv, wgt in zip(self.uv, uvw):
            if wgt > 1e-3:
                h = h + wgt * self._sample(self.foil, uv)
        gx = (torch.roll(h, -1, 3) - torch.roll(h, 1, 3)) * 0.5
        gy = (torch.roll(h, -1, 2) - torch.roll(h, 1, 2)) * 0.5
        k = 2.2
        n = torch.cat([-k * gx, -k * gy, torch.ones_like(gx)], 1)
        n = n / n.norm(dim=1, keepdim=True)
        t = self.t / 24.0
        a = 2 * math.pi * t / 5.0  # light orbits every 5 s
        L = torch.tensor([math.cos(a) * 0.6, math.sin(a) * 0.6 - 0.3, 1.0], device=self.dev)
        L = (L / L.norm()).view(1, 3, 1, 1)
        V = torch.tensor([0.0, 0.0, 1.0], device=self.dev).view(1, 3, 1, 1)
        H = (L + V)
        H = H / H.norm(dim=1, keepdim=True)
        diff = (n * L).sum(1, keepdim=True).clamp(0, 1)
        spec = (n * H).sum(1, keepdim=True).clamp(0, 1) ** 28
        dark = torch.tensor([0.50, 0.33, 0.10], device=self.dev).view(1, 3, 1, 1)
        mid = torch.tensor([0.83, 0.62, 0.22], device=self.dev).view(1, 3, 1, 1)
        hi = torch.tensor([1.00, 0.93, 0.68], device=self.dev).view(1, 3, 1, 1)
        base = dark + (mid - dark) * smoothstep(0.2, 0.9, diff)
        # flakes: static per-flake phase, smooth twinkle as time goes on (stable, never random)
        fl = self.flake
        tw = 0.5 + 0.5 * torch.sin(2 * math.pi * (t * 0.7 + fl[:, 1:2]))
        flakes = (fl[:, 0:1] > 0.985).float() * smoothstep(0.6, 1.0, tw)
        flakes = gblur(flakes, 0.7) * 2.5
        sheen = (spec * 0.9 + flakes).clamp(0, 1)
        return (base + (hi - base) * sheen).clamp(0, 1)


def auto_gold_mask(src: torch.Tensor) -> torch.Tensor:
    """Gold/yellow-ochre areas of a colour source: hue ~35-62 deg, saturated, bright."""
    r, g, b = src[:, 0:1], src[:, 1:2], src[:, 2:3]
    mx = src.max(1, keepdim=True).values
    mn = src.min(1, keepdim=True).values
    c = mx - mn + 1e-6
    # hue in degrees for the r-max sector (gold lives there: r >= g > b)
    hue = 60.0 * ((g - b) / c)
    rmax = (r >= g).float() * (g > b).float()
    sat = c / (mx + 1e-6)
    m = rmax * smoothstep(28, 38, hue) * (1 - smoothstep(58, 66, hue)) * smoothstep(0.35, 0.55, sat) \
        * smoothstep(0.42, 0.6, mx)
    # the source's leaf has dark texture/specks: close the holes, then soften the boundary
    r = max(2, int(src.shape[-2] / 360))
    m = gblur(m, 1.0)
    m = F.max_pool2d(m, 2 * r + 1, stride=1, padding=r)            # dilate
    m = -F.max_pool2d(-m, 2 * r + 1, stride=1, padding=r)          # erode (closing)
    m = -F.max_pool2d(-m, 3, stride=1, padding=1)                  # drop speckle
    m = F.max_pool2d(m, 3, stride=1, padding=1)
    return smoothstep(0.25, 0.65, gblur(m, 1.2))
