"""Section F style test: the colored-pencil world. 4 keyframes x 2 models (nano-banana-pro, gpt-image-2.5-flare)."""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (COLOR_WORLD, FINISH, FLARE, JADE_DOWN, NANO, SHOTS, refs, run_parallel, sheet, to169)  # noqa: E402

OUT = os.path.join(SHOTS, "F_style")
REFNOTE = ("Reference images: the first two are the character sheets for the girl (match her face, outfit and long loose "
           "hair exactly); the third shows the engraving line technique of the world.")

KF = {
    "T1_sprint": ("Low wide-angle shot on the elevated train tracks of the Chicago Loop: the anime girl sprints straight "
                  "toward the camera, extremely fast, long black hair streaming behind her, yellow pencil gripped in her "
                  "right hand, large in frame from the knees up. Behind her the Loop skyline with the Willis Tower; a "
                  "towering wave of color is breaking over the city behind her."),
    "T2_boss": ("Hero shot, low angle: the anime girl is airborne in the foreground, large in frame, leaping up, her yellow "
                "pencil drawn back over her shoulder like a sword, long hair flying. Behind and above her a colossal Salvador "
                "Dali melting pocket clock hangs over the Chicago Loop skyline, its soft face drooping over the skyscrapers, "
                "tiny black-suited agents dripping off its melting edge like drops of ink. The clock has no numerals, only "
                "plain tick marks."),
    "T3_gold": ("The anime girl flies mid-air across the frame, large, arms spread, long hair fanning out, pencil in hand, "
                "surrounded by swirling Klimt gold-leaf spirals and Kandinsky circles filling the sky above the Chicago "
                "rooftops; the sky is a mosaic of gold, ultramarine and vermilion."),
    "T4_bean": ("High angle looking straight down: the anime girl dives head-first toward Cloud Gate (the Bean) in "
                "Millennium Park, arms forward, hair streaming upward; the Bean's mirror surface below reflects her and the "
                "colored skyline in curved distortion, the reflection rendered in the same colored-pencil-over-engraving style."),
}


def main():
    rf = refs()
    jobs = []
    for k, scene in KF.items():
        prompt = f"{scene} {COLOR_WORLD} {JADE_DOWN} {REFNOTE} {FINISH}"
        for model, short in ((NANO, "nano"), (FLARE, "flare")):
            out = os.path.join(OUT, f"{k}_{short}.png")
            if glob.glob(os.path.join(OUT, f"{k}_{short}.*")) and "--force" not in sys.argv:
                continue
            jobs.append((model, prompt, list(rf), out, f"F_style_{k}"))
    res = run_parallel(jobs)
    items = []
    for k in KF:
        for short in ("nano", "flare"):
            g = [x for x in glob.glob(os.path.join(OUT, f"{k}_{short}.*")) if "_eng" not in x]
            if g:
                p = g[0]
                to169(p)
                items.append((p, f"{k} {short}"))
    sheet(items, os.path.join(OUT, "sheet_style_r1.jpg"), title="F style test r1: colored pencil over engraving")
    print(res)


if __name__ == "__main__":
    main()
