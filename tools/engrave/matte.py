"""Jade matte: BiRefNet foreground + colour cue + component filtering + flow-warped temporal smoothing.

Jade is the only coloured thing in the world, but her hair, black top and navy pants are nearly
gray, so colour alone is not a matte. BiRefNet (dichotomous segmentation, 1024^2) gives a sharp
silhouette on anime characters against busy engraved backgrounds; colour is then used to
  * rescue saturated bits BiRefNet clips (flying orange straps, residue near her body), and
  * reject salient but colourless blobs (gray agents, a water tower BiRefNet latches onto).
"""
from __future__ import annotations

import os
import cv2
import numpy as np
import torch
import torch.nn.functional as F

from engrave_core import gblur, warp, smoothstep

BIREFNET_REPO = os.environ.get("ENGRAVE_BIREFNET", "ZhengPeng7/BiRefNet")
BIREFNET_REV = os.environ.get("ENGRAVE_BIREFNET_REV", "e2bf8e4460fc8fa32bba5ea4d94b3233d367b0e4")  # pinned (remote code)


class BiRefNet:
    def __init__(self, device="cuda", size=1024):
        from transformers import AutoModelForImageSegmentation
        kw = dict(trust_remote_code=True)
        if BIREFNET_REV:
            kw["revision"] = BIREFNET_REV
        self.m = AutoModelForImageSegmentation.from_pretrained(BIREFNET_REPO, **kw).to(device).eval().half()
        self.size = size
        self.dev = device
        self.mean = torch.tensor([0.485, 0.456, 0.406], device=device).view(1, 3, 1, 1)
        self.std = torch.tensor([0.229, 0.224, 0.225], device=device).view(1, 3, 1, 1)

    @torch.no_grad()
    def __call__(self, rgb: torch.Tensor) -> torch.Tensor:
        """rgb (1,3,H,W) float 0..1 on device -> (1,1,H,W) 0..1"""
        h, w = rgb.shape[-2:]
        x = F.interpolate(rgb, size=(self.size, self.size), mode="bilinear", align_corners=False, antialias=True)
        x = ((x - self.mean) / self.std).half()
        p = self.m(x)[-1].sigmoid().float()
        return F.interpolate(p, size=(h, w), mode="bilinear", align_corners=False)


def chroma_map(rgb: torch.Tensor) -> torch.Tensor:
    mx = rgb.max(1, keepdim=True).values
    mn = rgb.min(1, keepdim=True).values
    return mx - mn


_NETS = {}


def get_birefnet(device="cuda"):
    """One BiRefNet per process (batch mode reuses it across clips)."""
    if device not in _NETS:
        _NETS[device] = BiRefNet(device)
    return _NETS[device]


class Matter:
    """Stateful per-sequence matte. Works at any resolution (run it on the source frames)."""

    def __init__(self, device="cuda", color_lo=0.10, color_hi=0.20, reach=0.04, min_color_frac=0.015,
                 keep_color=False, temporal=0.45, feather=1.0, motion_reach=0.06, max_growth=1.6):
        self.net = get_birefnet(device)
        self.dev = device
        self.color_lo, self.color_hi = color_lo, color_hi
        self.reach = reach               # how far (fraction of height) colour may extend the matte
        self.min_color_frac = min_color_frac
        self.keep_color = keep_color     # True: any coloured pixel anywhere is kept (residue ribbons)
        self.temporal = temporal         # weight of the flow-warped previous matte
        self.feather = feather
        self.motion_reach = motion_reach  # max silhouette motion per frame (fraction of height)
        self.max_growth = max_growth      # area jump that counts as a segmentation flip
        self.prev = None
        self.a_ref = None
        self.world_color = False          # set when the world itself is coloured (pencil/bloom)

    def reset(self):
        self.prev = None
        self.a_ref = None

    @staticmethod
    def _dilate(x, r):
        r = max(1, int(r))
        x = F.max_pool2d(x, (1, 2 * r + 1), stride=1, padding=(0, r))  # separable: O(k) not O(k^2)
        return F.max_pool2d(x, (2 * r + 1, 1), stride=1, padding=(r, 0))

    @torch.no_grad()
    def __call__(self, rgb: torch.Tensor, flow_full: torch.Tensor | None = None) -> torch.Tensor:
        h, w = rgb.shape[-2:]
        m = self.net(rgb)
        col = smoothstep(self.color_lo, self.color_hi, gblur(chroma_map(rgb), 0.8))
        colb = (col > 0.5).float()

        # temporal prior: BiRefNet sometimes flips to a salient prop (a steel column, the whole
        # structure) when Jade is occluded or ghosted by the video model. Only accept foreground
        # within a motion-sized reach of the previous (flow-warped) matte, or near coloured pixels.
        pw = None
        if self.prev is not None:
            pw = warp(self.prev, flow_full) if flow_full is not None else self.prev
            a_prev = (pw > 0.5).float().sum().item()
            if a_prev > 0.002 * h * w:
                a_ref = self.a_ref or a_prev
                # while the matte is below its usual size (Jade re-emerging from an occluder), let
                # it regrow from further away
                short = max(0.0, 1.0 - a_prev / a_ref)
                reach = (self.motion_reach + 0.2 * short) * h
                gate = self._dilate((pw > 0.3).float(), reach)
                if not self.world_color:
                    gate = torch.maximum(gate, self._dilate(colb, 0.02 * h))
                m = m * gate
                a_cur = (m > 0.5).float().sum().item()
                if a_cur > self.max_growth * max(a_prev, a_ref):  # flipped to a big prop: hug previous
                    m = m * self._dilate((pw > 0.3).float(), 0.012 * h)

        # reject colourless components (gray people / props); a rejected blob keeps only the part
        # that overlaps Jade's previous silhouette (Jade merged with a column into one blob)
        if self.min_color_frac > 0:
            mb = (m > 0.5).squeeze().cpu().numpy().astype(np.uint8)
            n, lab, stats, _ = cv2.connectedComponentsWithStats(mb, connectivity=8)
            if n > 1:
                cb = colb.squeeze().cpu().numpy() > 0.5
                ncol = np.bincount(lab.ravel(), weights=cb.ravel().astype(np.float64), minlength=n)
                area = stats[:, cv2.CC_STAT_AREA].astype(np.float64)
                keep = (ncol / np.maximum(area, 1) >= self.min_color_frac) & (area >= 0.0005 * h * w)
                keep[0] = False
                if not keep[1:].all():
                    km = torch.from_numpy(keep[lab].astype(np.float32)).to(self.dev)[None, None]
                    km = (gblur(km, 3.0) > 0.02).float()  # keep the soft edge of kept components
                    if pw is not None:
                        km = torch.maximum(km, self._dilate((pw > 0.3).float(), 0.012 * h))
                    m = m * km

        # colour near the silhouette joins the matte
        if not self.world_color:  # in a coloured world, colour says nothing about Jade
            near = self._dilate((m > 0.3).float(), max(2, self.reach * h))
            if self.keep_color:
                near = torch.ones_like(near)
            m = torch.maximum(m, col * near)

        # temporal smoothing with the warped previous matte where they roughly agree
        if pw is not None and self.temporal > 0:
            agree = 1 - smoothstep(0.35, 0.7, (pw - m).abs())
            a = self.temporal * agree
            m = a * pw + (1 - a) * m
        self.prev = m
        a_now = (m > 0.5).float().sum().item()
        if a_now > 0.002 * h * w:
            # slow running reference of Jade's size; only grows quickly, shrinks slowly
            self.a_ref = a_now if self.a_ref is None else (0.9 * self.a_ref + 0.1 * a_now)
        if self.feather > 0:
            m = gblur(m, self.feather)
        return smoothstep(0.08, 0.92, m)


# ----------------------------------------------------------------------------------------------
class Flow:
    """DIS optical flow (CPU, OpenCV) at a working width; returns backward flow (cur -> prev)."""

    def __init__(self, width=640, preset=cv2.DISOPTICAL_FLOW_PRESET_MEDIUM):
        self.dis = cv2.DISOpticalFlow_create(preset)
        self.width = width
        self.prev = None

    def reset(self):
        self.prev = None
        self.a_ref = None

    def __call__(self, rgb_u8: np.ndarray):
        h, w = rgb_u8.shape[:2]
        s = self.width / w
        g = cv2.cvtColor(cv2.resize(rgb_u8, (self.width, int(round(h * s))), interpolation=cv2.INTER_AREA),
                         cv2.COLOR_RGB2GRAY)
        if self.prev is None:
            self.prev = g
            return None
        fl = self.dis.calc(g, self.prev, None)  # cur(x) ~ prev(x + fl)
        self.prev = g
        return fl / s  # in source px, at working res


def flow_to_torch(fl: np.ndarray, h: int, w: int, src_w: int, device) -> torch.Tensor:
    """(h',w',2) flow measured in source px -> (1,2,h,w) in target px."""
    t = torch.from_numpy(np.ascontiguousarray(fl)).to(device).permute(2, 0, 1)[None]
    t = F.interpolate(t, size=(h, w), mode="bilinear", align_corners=False)
    return t * (w / float(src_w))


def background_flow(flow: torch.Tensor, matte: torch.Tensor, dil_px: int = 9) -> torch.Tensor:
    """Replace flow inside (dilated) matte with the median background flow so the engraved
    field behind Jade moves with the world, not with her."""
    md = Matter._dilate((matte > 0.2).float(), dil_px)
    bg = flow[:, :, md[0, 0] < 0.5]
    if bg.shape[-1] < 100:
        med = flow.flatten(2).median(dim=2).values
    else:
        med = bg.median(dim=2).values
    med = med.view(1, 2, 1, 1)
    md = gblur(md, dil_px)
    return flow * (1 - md) + med * md
