"""Optional upscaling before engraving: Real-ESRGAN anime (via spandrel) or Lanczos.

Weights are looked up in $ENGRAVE_MODELS (default ~/.cache/engrave) and downloaded on first use.
"""
from __future__ import annotations

import os
import urllib.request

import cv2
import numpy as np
import torch
import torch.nn.functional as F

MODELS = {
    # fast compact video model (SRVGGNetCompact, x4)
    "animevideov3": ("realesr-animevideov3.pth",
                     "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth"),
    # heavier RRDB anime model (x4), sharper but ~6x slower
    "anime6b": ("RealESRGAN_x4plus_anime_6B.pth",
                "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth"),
}
_NETS = {}
MODEL_DIR = os.path.expanduser(os.environ.get("ENGRAVE_MODELS", "~/.cache/engrave"))


class Upscaler:
    """mode: 'lanczos' | 'animevideov3' | 'anime6b'. Output size (w, h) is fixed per sequence."""

    def __init__(self, mode: str, out_w: int, out_h: int, device="cuda"):
        self.mode, self.ow, self.oh, self.dev = mode, out_w, out_h, device
        self.net = None
        if mode in MODELS:
            fn, url = MODELS[mode]
            path = os.path.join(MODEL_DIR, fn)
            if not os.path.exists(path):
                os.makedirs(MODEL_DIR, exist_ok=True)
                print(f"[upscale] downloading {url}")
                urllib.request.urlretrieve(url, path)
            key = (mode, device)
            if key not in _NETS:
                from spandrel import ModelLoader
                _NETS[key] = ModelLoader().load_from_file(path).to(device).eval().half()
            self.net = _NETS[key]
        elif mode != "lanczos":
            raise ValueError(f"unknown upscaler {mode}")

    @torch.no_grad()
    def __call__(self, rgb_u8: np.ndarray) -> np.ndarray:
        if self.net is None:
            return cv2.resize(rgb_u8, (self.ow, self.oh), interpolation=cv2.INTER_LANCZOS4)
        x = torch.from_numpy(rgb_u8).to(self.dev).permute(2, 0, 1)[None].half() / 255.0
        y = self.net(x).float()
        y = F.interpolate(y, size=(self.oh, self.ow), mode="bicubic", align_corners=False, antialias=True)
        return (y.clamp(0, 1)[0].permute(1, 2, 0) * 255 + 0.5).byte().cpu().numpy()
