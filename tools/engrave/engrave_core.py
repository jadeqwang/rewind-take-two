"""Wood/line-engraving renderer (GPU, torch).

The world (everything outside the Jade matte) is redrawn as black ink lines on off-white paper:

* tone      : luminance -> auto-levels (temporally smoothed) + local contrast -> darkness T in [0,1]
* direction : smoothed structure tensor (lines run along edges / forms), blended with a fallback
              screen-space angle where the image is flat (sky, walls)
* lines     : a continuous stripe field f ~ cos(phase) synthesized by iterated oriented Gabor
              filtering (the fingerprint-enhancement trick); lines bend with the flow, fork and end
              like a burin cut. Stroke width follows tone: ink where f > cos(pi * coverage).
* darks     : an optional second (cross) layer at +90 deg for the deepest tones
* edges     : XDoG contour ink
* paper/ink : static paper grain + slight ink starvation, pure two-colour output (no gray wash)
* time      : the stripe field and tensor are advected with optical flow (or the global pan) from
              the previous frame and only re-aligned by a couple of Gabor iterations per frame, so
              lines stick to the world instead of boiling.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import torch
import torch.nn.functional as F


# ----------------------------------------------------------------------------------------------
# small helpers
# ----------------------------------------------------------------------------------------------
def _gauss_kernel1d(sigma: float, device) -> torch.Tensor:
    r = max(1, int(math.ceil(3.0 * sigma)))
    x = torch.arange(-r, r + 1, device=device, dtype=torch.float32)
    k = torch.exp(-0.5 * (x / sigma) ** 2)
    return k / k.sum()


def gblur(x: torch.Tensor, sigma: float) -> torch.Tensor:
    """Separable gaussian blur of (B,C,H,W); large sigmas run on a downsampled copy."""
    if sigma <= 0.3:
        return x
    if sigma > 12:
        f = int(sigma // 6)
        h, w = x.shape[-2:]
        small = F.interpolate(x, size=(max(1, h // f), max(1, w // f)), mode="area")
        small = gblur(small, sigma / f)
        return F.interpolate(small, size=(h, w), mode="bilinear", align_corners=False)
    k = _gauss_kernel1d(sigma, x.device)
    c = x.shape[1]
    r = (k.numel() - 1) // 2
    kx = k.view(1, 1, 1, -1).repeat(c, 1, 1, 1)
    ky = k.view(1, 1, -1, 1).repeat(c, 1, 1, 1)
    x = F.conv2d(F.pad(x, (r, r, 0, 0), mode="replicate"), kx, groups=c)
    x = F.conv2d(F.pad(x, (0, 0, r, r), mode="replicate"), ky, groups=c)
    return x


def smoothstep(e0, e1, x):
    t = ((x - e0) / (e1 - e0)).clamp(0, 1)
    return t * t * (3 - 2 * t)


def warp(x: torch.Tensor, flow: torch.Tensor) -> torch.Tensor:
    """Backward warp: out(p) = x(p + flow(p)). flow is (1,2,H,W) in pixels (dx,dy)."""
    _, _, h, w = x.shape
    yy, xx = torch.meshgrid(torch.arange(h, device=x.device, dtype=torch.float32),
                            torch.arange(w, device=x.device, dtype=torch.float32), indexing="ij")
    gx = (xx + flow[:, 0]) / max(w - 1, 1) * 2 - 1
    gy = (yy + flow[:, 1]) / max(h - 1, 1) * 2 - 1
    grid = torch.stack([gx, gy], dim=-1)
    return F.grid_sample(x, grid, mode="bilinear", padding_mode="border", align_corners=True)


def value_noise(h, w, cell, gen, device):
    """Smooth value noise in [0,1] (bicubic-upsampled random grid)."""
    gh, gw = max(2, int(h / cell) + 3), max(2, int(w / cell) + 3)
    g = torch.rand(1, 1, gh, gw, generator=gen, device="cpu").to(device)
    big = F.interpolate(g, size=(int(gh * cell), int(gw * cell)), mode="bicubic", align_corners=False)
    return big[..., :h, :w].clamp(0, 1)


# ----------------------------------------------------------------------------------------------
# parameters
# ----------------------------------------------------------------------------------------------
@dataclass
class EngraveParams:
    period: float | None = None        # line spacing in px (default: height / 190)
    bins: int = 16                      # orientation bins of the Gabor bank
    fallback_angle: float = 0.0         # degrees; line direction in flat areas (0 = horizontal)
    fallback_weight: float = 0.35       # how strongly flat areas snap to the fallback angle
    tensor_sigma: float | None = None   # structure-tensor smoothing in periods (default 2)
    iters_first: int = 14               # Gabor iterations on the first frame
    iters: int = 2                      # Gabor iterations per subsequent frame
    gamma: float = 1.15                 # tone curve exponent on darkness
    contrast: float = 0.55              # local contrast boost
    white_point: float = 0.10           # darkness below this -> bare paper
    max_cover: float = 0.92             # ink coverage at full darkness (leaves thin white lines)
    cross: bool = True                  # cross-hatch layer for the darks
    cross_start: float = 0.5            # darkness where cross-hatching starts
    cross_angle: float = 55.0           # degrees between main and cross lines
    edges: float = 1.0                  # XDoG contour strength (0 = off)
    carve: float = 1.0                  # white-line carving on the lit side of edges in darks (0 = off)
    edge_sigma: float | None = None     # px (default period * 0.25)
    paper: tuple = (0.953, 0.929, 0.871)
    ink: tuple = (0.075, 0.066, 0.062)
    grain: float = 1.0                  # paper/ink texture amount
    advect: str = "flow"                # flow | pan | fixed
    tensor_ema: float = 0.6             # temporal weight of the previous (warped) tensor
    tone_ema: float = 0.85              # temporal smoothing of the auto-levels
    tone_temporal: float = 0.5          # weight of the flow-warped previous tone (line-width flicker)
    field_damp: float = 0.6             # how much of each frame's Gabor re-alignment is applied
    outline: float = 1.0                # dark ink outline around the matte (0 = off)
    outline_px: float | None = None     # outline thickness (default height / 420)
    palette: str | None = None          # pencil colours: None = from the colour source, or a name/hex list
    color_lift: float = 1.0             # in coloured areas, ink tone follows value instead of luma
    pencil_reset: int = 48              # frames per texture-advection cycle of the pencil grain
    pencil_angle: float = -35.0         # pencil hatch angle (degrees) where there is no structure


class Engraver:
    """Stateful per-sequence renderer. Call .step() once per frame in order."""

    def __init__(self, h: int, w: int, params: EngraveParams | None = None, device="cuda", seed=7):
        self.p = p = params or EngraveParams()
        self.h, self.w, self.dev = h, w, device
        self.P = p.period or max(3.2, h / 190.0)
        self.tsig = (p.tensor_sigma or 1.5) * self.P
        self.esig = p.edge_sigma or max(0.7, self.P * 0.16)
        self.olw = p.outline_px or max(1.2, h / 420.0)
        gen = torch.Generator().manual_seed(seed)
        self._build_bank()
        self.pencil = None
        # static textures (paper does not move: it is the paper)
        mott = value_noise(h, w, h / 6, gen, device) * 0.6 + value_noise(h, w, h / 30, gen, device) * 0.4
        fine = torch.rand(1, 1, h, w, generator=gen).to(device)
        fine = gblur(fine, 0.6)
        fibre = gblur(torch.rand(1, 1, h, w, generator=gen).to(device), 1.2)
        g = p.grain
        self.paper_tex = 1.0 + g * (0.035 * (mott - 0.5) + 0.05 * (fine - fine.mean()) + 0.06 * (fibre - fibre.mean()))
        self.ink_starve = (g * 0.9 * (fibre - fibre.mean()) / (fibre.std() + 1e-6) * 0.06)
        self.wobble = (value_noise(h, w, self.P * 9, gen, device) - 0.5) * 0.9  # phase wobble (radians/2pi)
        yy, xx = torch.meshgrid(torch.arange(h, device=device, dtype=torch.float32),
                                torch.arange(w, device=device, dtype=torch.float32), indexing="ij")
        self.xx, self.yy = xx[None, None], yy[None, None]
        self.reset()

    # ------------------------------------------------------------------------------------------
    def reset(self):
        self.f = None
        self.f2 = None
        self.tone_prev = None
        if getattr(self, "pencil", None) is not None:
            self.pencil.reset()
        self.J = None
        self.levels = None
        self.offset = torch.zeros(2, device=self.dev)

    def _build_bank(self):
        P, K = self.P, self.p.bins
        su, sv = 1.1 * P, 0.55 * P  # along-line, across-line sigmas
        r = int(math.ceil(2.5 * su))
        y, x = torch.meshgrid(torch.arange(-r, r + 1, dtype=torch.float32),
                              torch.arange(-r, r + 1, dtype=torch.float32), indexing="ij")
        ks = []
        for k in range(K):
            a = math.pi * k / K  # tangent angle
            u = x * math.cos(a) + y * math.sin(a)
            v = -x * math.sin(a) + y * math.cos(a)
            env = torch.exp(-0.5 * (u / su) ** 2 - 0.5 * (v / sv) ** 2)
            g = env * torch.cos(2 * math.pi * v / P)
            g = g - env * (g.sum() / env.sum())  # zero DC
            g = g / g.abs().sum()
            ks.append(g)
        self.bank = torch.stack(ks)[:, None].to(self.dev)  # (K,1,k,k)
        self.bank_r = r

    # ------------------------------------------------------------------------------------------
    def _tone(self, rgb):
        p = self.p
        y = (0.2126 * rgb[:, 0:1] + 0.7152 * rgb[:, 1:2] + 0.0722 * rgb[:, 2:3])
        return y

    def _levels(self, y, valid):
        # robust percentiles of the world (outside the matte), smoothed over time
        v = y[valid > 0.5]
        if v.numel() < 1000:
            v = y.flatten()
        if v.numel() > 400_000:
            v = v[torch.randint(0, v.numel(), (400_000,), device=v.device)]
        lo, hi = torch.quantile(v, torch.tensor([0.01, 0.995], device=v.device))
        cur = torch.stack([lo, hi])
        if self.levels is None:
            self.levels = cur
        else:
            a = self.p.tone_ema
            self.levels = a * self.levels + (1 - a) * cur
        return self.levels

    def _tensor(self, y):
        ys = gblur(y, max(0.8, self.P * 0.3))
        gx = (torch.roll(ys, -1, 3) - torch.roll(ys, 1, 3)) * 0.5
        gy = (torch.roll(ys, -1, 2) - torch.roll(ys, 1, 2)) * 0.5
        J = torch.cat([gx * gx, gx * gy, gy * gy], 1)
        return gblur(J, self.tsig)

    def _orient(self, J):
        """Line direction from the tensor. Incoherent spots (crossings, vortex singularities that would
        turn into fingerprint loops) and flat areas fall back to the screen-space fallback angle."""
        p = self.p
        Jxx, Jxy, Jyy = J[:, 0:1], J[:, 1:2], J[:, 2:3]
        tr = Jxx + Jyy + 1e-10
        disc = torch.sqrt((Jxx - Jyy) ** 2 + 4 * Jxy ** 2)
        coh = disc / tr                                    # 0 isotropic .. 1 one clear direction
        strong = smoothstep(0.0, 1.0, tr / (gblur(tr, self.h / 12) + 1e-10) * 0.8)
        w = smoothstep(0.12, 0.45, coh) * strong
        w = w * (1 - 0.5 * p.fallback_weight)  # a little fallback bias everywhere
        a = math.radians(p.fallback_angle)
        n = (-math.sin(a), math.cos(a))  # normal of fallback lines = the gradient they imply
        nx, nxy, ny = (Jxx / tr), (Jxy / tr), (Jyy / tr)
        Txx = w * nx + (1 - w) * n[0] * n[0]
        Txy = w * nxy + (1 - w) * n[0] * n[1]
        Tyy = w * ny + (1 - w) * n[1] * n[1]
        theta_g = 0.5 * torch.atan2(2 * Txy, Txx - Tyy)
        theta_t = theta_g + math.pi / 2  # line (tangent) direction
        self.coh = coh
        self.orient_w = w * smoothstep(0.15, 0.6, tr / tr.mean())  # absolute: soft sky is not structure
        return torch.remainder(theta_t, math.pi)

    def _gabor(self, f, theta, n_iter):
        K = self.p.bins
        idx = theta / (math.pi / K)
        i0 = torch.floor(idx).long() % K
        wf = idx - torch.floor(idx)
        i1 = (i0 + 1) % K
        for _ in range(n_iter):
            R = F.conv2d(F.pad(f, (self.bank_r,) * 4, mode="reflect"), self.bank)  # (1,K,H,W)
            r = torch.gather(R, 1, i0) * (1 - wf) + torch.gather(R, 1, i1) * wf
            amp = torch.sqrt(gblur(r * r, self.P * 0.9) * 2.0 + 1e-10)
            f = (r / amp).clamp(-1.2, 1.2)
        return f

    def _damp(self, fp, fg):
        a = self.p.field_damp
        if a >= 1:
            return fg
        f = a * fg + (1 - a) * fp
        amp = torch.sqrt(gblur(f * f, self.P * 0.9) * 2.0 + 1e-10)
        return (f / amp).clamp(-1.2, 1.2)

    def _init_field(self, theta):
        # per-bin screen-space stripes (nearest bin) as a seed; Gabor iterations heal the seams
        K = self.p.bins
        k = torch.round(theta / (math.pi / K)) % K
        a = k * (math.pi / K)
        v = -self.xx * torch.sin(a) + self.yy * torch.cos(a)
        return torch.cos(2 * math.pi * (v / self.P + self.wobble))

    # ------------------------------------------------------------------------------------------
    @torch.no_grad()
    def step(self, rgb: torch.Tensor, matte: torch.Tensor | None = None, flow: torch.Tensor | None = None,
             strength: float = 1.0, bloom: torch.Tensor | None = None, bloom_rgb: torch.Tensor | None = None,
             jade_rgb: torch.Tensor | None = None, gold: torch.Tensor | None = None,
             return_debug: bool = False):
        """rgb (1,3,H,W) 0..1; matte (1,1,H,W) 0..1 (1 = Jade, passed through);
        flow (1,2,H,W) backward flow in px (current -> previous frame), background-only is best.
        bloom (1,1,H,W) mask where colored-pencil colour from bloom_rgb (default rgb) shows through.
        jade_rgb: what is composited inside the matte (default rgb), e.g. an anime-SR upscale.
        gold (1,1,H,W): gold-leaf mask (needs a bloom/colour mask to be visible too)."""
        p = self.p
        if matte is None:
            matte = torch.zeros_like(rgb[:, :1])
        world = 1.0 - matte
        y = self._tone(rgb)
        if bloom is not None and p.color_lift > 0:
            # in coloured areas the ink follows value, not luma: a saturated blue wall is a light,
            # coloured wall with some hatching, not a black one
            v = rgb.max(1, keepdim=True).values
            mn = rgb.min(1, keepdim=True).values
            colw = smoothstep(0.03, 0.18, gblur(v - mn, 2.0))  # how coloured the source is here
            self._colw = colw * bloom
            vl = 1 - (1 - v) * 0.7
            # only where the source is actually coloured: gray buildings keep their ink in the flood
            y = y + (vl - y) * (self._colw * p.color_lift).clamp(0, 1)

        # --- tone ------------------------------------------------------------------------------
        lo, hi = self._levels(y, world)
        yn = ((y - lo) / (hi - lo + 1e-4)).clamp(0, 1)
        # Jade is not part of the world: fill her region with a blurred world tone for analysis
        wb = gblur(world, self.P * 3) + 1e-4
        yfill = gblur(yn * world, self.P * 3) / wb
        ya = yn * world + yfill * matte
        local = gblur(ya, self.h / 40)
        yc = (ya + p.contrast * (ya - local)).clamp(0, 1)
        dark = (1.0 - yc) ** p.gamma
        tone_s = gblur(dark, self.P * 0.45)  # tone at line scale

        # --- direction -------------------------------------------------------------------------
        if flow is not None and p.advect == "pan":
            # global translation only
            med = flow.flatten(2).median(dim=2).values.view(1, 2, 1, 1)
            flow = med.expand(1, 2, self.h, self.w)
        J = self._tensor(ya)
        if self.J is not None and p.tensor_ema > 0:
            Jp = warp(self.J, flow) if (flow is not None and p.advect != "fixed") else self.J
            J = p.tensor_ema * Jp + (1 - p.tensor_ema) * J
        self.J = J
        theta = self._orient(J)

        # --- line field ------------------------------------------------------------------------
        if self.f is None:
            f = self._gabor(self._init_field(theta), theta, p.iters_first)
        else:
            fp = warp(self.f, flow) if (flow is not None and p.advect != "fixed") else self.f
            f = self._damp(fp, self._gabor(fp, theta, p.iters))
        self.f = f

        if p.tone_temporal > 0 and getattr(self, "tone_prev", None) is not None:
            tp = warp(self.tone_prev, flow) if (flow is not None and p.advect != "fixed") else self.tone_prev
            # follow real tone changes quickly, smooth only small shimmer
            d = (tone_s - tp).abs()
            a = p.tone_temporal * (1 - smoothstep(0.08, 0.25, d))
            tone_s = a * tp + (1 - a) * tone_s
        self.tone_prev = tone_s

        cover = (smoothstep(p.white_point, 1.0, tone_s) * p.max_cover)
        if bloom is not None and p.color_lift > 0:
            cw = p.color_lift * self._colw
            cover = smoothstep(p.white_point + 0.15 * cw, 1.0, tone_s) * p.max_cover * (1 - 0.5 * cw)
        thr = torch.cos(math.pi * cover)
        dfdx = math.pi * 2 / self.P * torch.sin(math.pi * cover).clamp(min=0.25)  # f-units per px
        ink = ((f - thr) / dfdx + 0.5).clamp(0, 1)
        ink = ink * (cover > 0.012).float()

        if p.cross:
            th2 = torch.remainder(theta + math.radians(p.cross_angle), math.pi)
            if self.f2 is None:
                f2 = self._gabor(self._init_field(th2), th2, p.iters_first)
            else:
                fp2 = warp(self.f2, flow) if (flow is not None and p.advect != "fixed") else self.f2
                f2 = self._damp(fp2, self._gabor(fp2, th2, p.iters))
            self.f2 = f2
            # mid-dark bump: diamond cross-hatching in the mids, fading out in the deepest darks
            c2 = smoothstep(p.cross_start, p.cross_start + 0.2, tone_s) * (1 - smoothstep(0.86, 0.98, tone_s)) * 0.3
            thr2 = torch.cos(math.pi * c2)
            ink2 = ((f2 - thr2) / (math.pi * 2 / self.P * torch.sin(math.pi * c2).clamp(min=0.25)) + 0.5).clamp(0, 1)
            ink2 = ink2 * (c2 > 0.02).float()
            ink = torch.maximum(ink, ink2)

        # --- contour ink (two-scale XDoG on the analysed tone) ---------------------------------
        hatch = ink
        e = None
        if p.edges > 0:
            k = p.edges
            sf = self.esig
            dog_f = gblur(yc, sf) - gblur(yc, sf * 1.6)           # fine: rivets, window bars, ties
            kf = kc = k
            if bloom is not None and p.color_lift > 0:
                # in pencil areas the source's own pencil texture must not turn into ink dashes;
                # only strong contours survive
                cb = bloom * (0.4 + 0.6 * self._colw / (bloom + 1e-4))
                kf = k / (1 + 3.0 * p.color_lift * cb)
                kc = k / (1 + 1.2 * p.color_lift * cb)
            sc = self.P * 0.45
            dog_c = gblur(yc, sc) - gblur(yc, sc * 1.6)           # coarse: silhouettes of forms
            e = torch.maximum(smoothstep(0.018 / kf, 0.04 / kf, -dog_f),
                              smoothstep(0.03 / kc, 0.06 / kc, -dog_c) * 0.9)
            ink = torch.maximum(ink, e)
            if p.carve > 0:
                # white-line engraving: the lit side of an edge is cut back to paper inside the darks
                wl = smoothstep(0.02 / p.carve, 0.045 / p.carve, dog_f) * smoothstep(0.35, 0.6, tone_s)
                ink = ink * (1 - wl)

        # ink starvation / paper tooth
        ink = (ink - self.ink_starve * ink * (1 - ink) * 4 - self.ink_starve.clamp(min=0) * 0.5 * ink).clamp(0, 1)

        paper = torch.tensor(p.paper, device=self.dev).view(1, 3, 1, 1) * self.paper_tex
        inkc = torch.tensor(p.ink, device=self.dev).view(1, 3, 1, 1)
        if bloom is not None:
            src = bloom_rgb if bloom_rgb is not None else rgb
            if self.pencil is None:
                from pencil import Pencil
                self.pencil = Pencil(self.h, self.w, self.P, self.dev, palette=p.palette,
                                     reset_frames=p.pencil_reset, paper=p.paper)
            pflow = flow if p.advect != "fixed" else None
            gm = gold * bloom if gold is not None else None
            # pencil follows forms where there is structure, else a hand-hatched diagonal
            wp = self.orient_w
            pa = math.radians(p.pencil_angle)
            cx = wp * torch.cos(2 * theta) + (1 - wp) * math.cos(2 * pa)
            sy = wp * torch.sin(2 * theta) + (1 - wp) * math.sin(2 * pa)
            th_p = torch.remainder(0.5 * torch.atan2(sy, cx), math.pi)
            mult, grgb, ga, _ = self.pencil.step(th_p, pflow, src, bloom * world, gm)
            paper = paper * mult
            if grgb is not None:
                ga = (ga * world).clamp(0, 1)
                paper = paper * (1 - ga) + grgb * self.paper_tex * ga
                # leaf is laid over the hatching; contour ink stays
                lines = hatch * (1 - 0.8 * ga)
                ink = torch.maximum(lines, e * (1 - 0.3 * ga)) if e is not None else lines
                # Klimt outlines his gilded forms: a crisp ink line along the leaf boundary
                gb = gblur(ga, max(0.8, self.P * 0.18))
                ring = (1 - (2 * gb - 1).abs()).clamp(0, 1)
                ink = torch.maximum(ink, smoothstep(0.55, 0.8, ring) * smoothstep(0.05, 0.3, ga.amax()))
        eng = paper * (1 - ink) + inkc * ink

        # --- strength: blend with the source re-printed in the same paper/ink palette ----------
        if strength < 1.0:
            ys = y.clamp(0, 1)
            pal = torch.tensor(p.paper, device=self.dev).view(1, 3, 1, 1) * self.paper_tex * ys + inkc * (1 - ys)
            if bloom is not None:
                pal = pal * (1 - bloom) + rgb * bloom
            eng = pal * (1 - strength) + eng * strength

        # --- composite Jade + outline -----------------------------------------------------------
        out = eng * world + (jade_rgb if jade_rgb is not None else rgb) * matte
        if p.outline > 0:
            m = matte
            r = self.olw
            dil = gblur(m, r * 0.9)
            ring = smoothstep(0.03, 0.18, dil) * (1 - smoothstep(0.35, 0.8, m))
            ring = ring * p.outline * strength
            out = out * (1 - ring) + inkc * ring
        out = out.clamp(0, 1)
        if return_debug:
            return out, dict(theta=theta, f=f, ink=ink, tone=tone_s)
        return out
