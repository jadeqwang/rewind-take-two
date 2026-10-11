"""Frame pipeline shared by engrave.py (video) and engrave_still.py (images)."""
from __future__ import annotations

import time

import numpy as np
import torch

torch.backends.cudnn.benchmark = True
import torch.nn.functional as F

from engrave_core import EngraveParams, Engraver
from matte import Flow, Matter, background_flow, flow_to_torch
from upscale import Upscaler


def to_t(rgb_u8: np.ndarray, dev) -> torch.Tensor:
    return torch.from_numpy(rgb_u8).to(dev).permute(2, 0, 1)[None].float() / 255.0


def to_u8(t: torch.Tensor) -> np.ndarray:
    return (t.clamp(0, 1)[0].permute(1, 2, 0) * 255 + 0.5).byte().cpu().numpy()


def crispness(rgb_u8: np.ndarray, matte_u8: np.ndarray | None = None) -> float:
    """Mean absolute high-pass of the world luminance at 480 lines. Gray-wash video frames score
    ~0.02-0.045, crisp engraved plates ~0.10+."""
    import cv2
    g = cv2.cvtColor(rgb_u8, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0
    s = 480.0 / g.shape[0]
    g = cv2.resize(g, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    hp = np.abs(g - cv2.GaussianBlur(g, (0, 0), 1.0))
    if matte_u8 is not None:
        m = cv2.resize(matte_u8, (g.shape[1], g.shape[0])) < 64
        if m.mean() > 0.2:
            return float(hp[m].mean())
    return float(hp.mean())


def auto_strength(c: float, lo=0.35, crisp_hi=0.10, crisp_lo=0.05) -> float:
    """crisp (>= crisp_hi) -> lo strength; soft (<= crisp_lo) -> 1.0"""
    t = min(1.0, max(0.0, (crisp_hi - c) / (crisp_hi - crisp_lo)))
    return lo + (1.0 - lo) * t


def out_size(src_w, src_h, upscale: float, out_height: int | None):
    if out_height:
        s = out_height / src_h
    else:
        s = upscale
    w, h = int(round(src_w * s / 2)) * 2, int(round(src_h * s / 2)) * 2
    return w, h


class Pipeline:
    def __init__(self, src_w, src_h, params: EngraveParams, upscale=1.0, out_height=None,
                 upscaler="animevideov3", world_upscaler="lanczos", matte=True, keep_color=False, device="cuda", seed=7):
        self.dev = device
        self.sw, self.sh = src_w, src_h
        self.ow, self.oh = out_size(src_w, src_h, upscale, out_height)
        self.up = self.up_world = None
        if (self.ow, self.oh) != (src_w, src_h):
            # Jade gets the anime SR model; the world (which is redrawn anyway) engraves more cleanly
            # from a faithful Lanczos upscale than from SR's painterly smoothing.
            self.up = Upscaler(upscaler if self.ow > src_w else "lanczos", self.ow, self.oh, device)
            wu = world_upscaler if self.ow > src_w else "lanczos"
            self.up_world = self.up if wu == self.up.mode else Upscaler(wu, self.ow, self.oh, device)
        self.eng = Engraver(self.oh, self.ow, params, device=device, seed=seed)
        self.matter = Matter(device, keep_color=keep_color, feather=max(1.0, 0.8 * self.oh / src_h)) if matte else None
        self.flow = Flow(width=min(640, src_w))
        self.timing = dict(up=0.0, matte=0.0, flow=0.0, engrave=0.0, n=0)

    def reset(self):
        self._auto = None
        self.eng.reset()
        self.flow.reset()
        if self.matter:
            self.matter.reset()

    @torch.no_grad()
    def __call__(self, rgb_u8: np.ndarray, strength: float | str = 1.0, bloom: np.ndarray | None = None,
                 bloom_rgb: np.ndarray | None = None, ext_matte: np.ndarray | None = None,
                 gold: np.ndarray | str | None = None):
        """rgb_u8 source frame (H,W,3). Returns (out_u8 at output size, matte_u8 at output size)."""
        T = self.timing
        t0 = time.time()
        fl = self.flow(rgb_u8)
        flow_full = flow_to_torch(fl, self.oh, self.ow, self.sw, self.dev) if fl is not None else None
        t1 = time.time()
        big = self.up(rgb_u8) if self.up is not None else rgb_u8
        jade = to_t(big, self.dev)
        if self.up_world is not None and self.up_world is not self.up:
            rgb = to_t(self.up_world(rgb_u8), self.dev)
        else:
            rgb = jade
        torch.cuda.synchronize()
        t2 = time.time()
        # matte at output resolution, segmented on the (sharper) Jade upscale
        if ext_matte is not None:
            mo = torch.from_numpy(ext_matte).to(self.dev).float()[None, None] / 255.0
            mo = F.interpolate(mo, size=(self.oh, self.ow), mode="bilinear", align_corners=False)
        elif self.matter is not None:
            self.matter.world_color = bloom is not None
            mo = self.matter(jade, flow_full)
        else:
            mo = torch.zeros_like(rgb[:, :1])
        torch.cuda.synchronize()
        t3 = time.time()
        flow = background_flow(flow_full, mo, dil_px=max(3, self.oh // 60)) if flow_full is not None else None
        bl = brgb = gm = None
        if isinstance(bloom, (int, float)):
            bl = torch.full_like(rgb[:, :1], float(bloom))
        elif bloom is not None:
            bl = torch.from_numpy(bloom).to(self.dev).float()[None, None] / 255.0
            bl = F.interpolate(bl, size=(self.oh, self.ow), mode="bilinear", align_corners=False)
        if bloom_rgb is not None:
            brgb = F.interpolate(to_t(bloom_rgb, self.dev), size=(self.oh, self.ow), mode="bilinear",
                                 align_corners=False)
        if isinstance(gold, str) and gold == "auto":
            from pencil import auto_gold_mask
            gm = auto_gold_mask(brgb if brgb is not None else rgb)
        elif gold is not None:
            gm = torch.from_numpy(gold).to(self.dev).float()[None, None] / 255.0
            gm = F.interpolate(gm, size=(self.oh, self.ow), mode="bilinear", align_corners=False)
        if strength == "auto":
            st = auto_strength(crispness(rgb_u8))
            self._auto = st if getattr(self, "_auto", None) is None else 0.8 * self._auto + 0.2 * st
            strength = self._auto
        self.last_strength = float(strength)
        out = self.eng.step(rgb, mo, flow, strength=strength, bloom=bl, bloom_rgb=brgb, jade_rgb=jade,
                            gold=gm)
        torch.cuda.synchronize()
        t4 = time.time()
        T["flow"] += t1 - t0
        T["up"] += t2 - t1
        T["matte"] += t3 - t2
        T["engrave"] += t4 - t3
        T["n"] += 1
        return to_u8(out), (mo[0, 0].clamp(0, 1) * 255 + 0.5).byte().cpu().numpy()
