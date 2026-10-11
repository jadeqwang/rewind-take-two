"""Shared look/scale CLI flags."""
from __future__ import annotations

from engrave_core import EngraveParams


def strength_arg(v):
    return "auto" if v == "auto" else float(v)


def add_look_args(ap):
    g = ap.add_argument_group("scale")
    g.add_argument("--upscale", type=float, default=1.0, help="output scale vs source (e.g. 2 for 480p)")
    g.add_argument("--out-height", type=int, help="output height (overrides --upscale), e.g. 1080")
    g.add_argument("--upscaler", default="animevideov3", choices=["animevideov3", "anime6b", "lanczos"],
                   help="upscaler for Jade (the passthrough)")
    g.add_argument("--world-upscaler", default="lanczos", choices=["animevideov3", "anime6b", "lanczos"],
                   help="upscaler feeding the engraving (lanczos keeps texture; SR smears it)")
    g = ap.add_argument_group("matte")
    g.add_argument("--no-matte", action="store_true", help="engrave the whole frame (no Jade passthrough)")
    g.add_argument("--keep-color", action="store_true",
                   help="any saturated pixel anywhere stays in colour (residue ribbons, ghosts)")
    g = ap.add_argument_group("look")
    g.add_argument("--strength", type=strength_arg, default=1.0,
                   help="0 = source (re-inked palette) .. 1 = full engraving, or 'auto' (from frame crispness)")
    g.add_argument("--period", type=float, help="line spacing in output px (default height/190)")
    g.add_argument("--fallback-angle", type=float, default=0.0, help="line angle in flat areas, degrees")
    g.add_argument("--fallback-weight", type=float, default=0.35)
    g.add_argument("--contrast", type=float, default=0.55)
    g.add_argument("--gamma", type=float, default=1.15, help=">1 lighter mids, <1 darker")
    g.add_argument("--edges", type=float, default=1.0, help="contour ink strength, 0 = off")
    g.add_argument("--carve", type=float, default=1.0, help="white-line carving in the darks, 0 = off")
    g.add_argument("--tensor-sigma", type=float, default=1.5, help="line-direction smoothing, in line periods")
    g.add_argument("--no-cross", action="store_true", help="no cross-hatching in the darks")
    g.add_argument("--outline", type=float, default=1.0, help="ink outline around Jade, 0 = off")
    g.add_argument("--grain", type=float, default=1.0, help="paper/ink texture")
    g = ap.add_argument_group("colour (final drop / bloom)")
    g.add_argument("--color", default="none", choices=["none", "pencil"],
                   help="pencil: the whole world gets directional colored-pencil strokes over the engraving")
    g.add_argument("--palette", help="pencil colours from a palette gradient map instead of the source colour: "
                                     "residue | klimt | kandinsky | '#hex,#hex,...'")
    g.add_argument("--gold", help="gold leaf: 'auto' (gold/yellow areas of the colour source) or a mask "
                                  "video/image/PNG dir (white = leaf)")
    g.add_argument("--color-lift", type=float, default=1.0,
                   help="in coloured areas ink follows value, not luma (lighter hatching on saturated colour)")
    g = ap.add_argument_group("motion")
    g.add_argument("--advect", default="flow", choices=["flow", "pan", "fixed"],
                   help="how the line field follows motion")
    g.add_argument("--iters", type=int, default=2, help="Gabor re-alignment iterations per frame")
    g.add_argument("--seed", type=int, default=7)


def params_from_args(a) -> EngraveParams:
    return EngraveParams(period=a.period, fallback_angle=a.fallback_angle, fallback_weight=a.fallback_weight,
                         contrast=a.contrast, gamma=a.gamma, edges=a.edges, carve=a.carve,
                         tensor_sigma=a.tensor_sigma, cross=not a.no_cross,
                         outline=a.outline, grain=a.grain, advect=a.advect, iters=a.iters,
                         palette=a.palette, color_lift=a.color_lift)
