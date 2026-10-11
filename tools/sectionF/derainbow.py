"""Polish pass (coordinator note): remove the literal rainbow arcs and checkerboard confetti from F keyframes while
keeping the Kandinsky circles/triangles/colour fields and the Klimt gold. nano-banana-pro edit with the keyframe as the
only input.   $PY tools/sectionF/derainbow.py SHOT=media/shots/F5a/kf_2.jpg ...   -> media/shots/<SHOT>/kf_clean.png
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import NANO, SHOTS, run_parallel, sheet, to169  # noqa: E402

EDIT = ("Edit this drawing. Remove every rainbow: all striped multicolour rainbow arcs and half-rainbows in the sky must be "
        "gone. Also remove all checkerboard squares and checkered confetti. Where they were, continue the warm paper sky "
        "with light colored-pencil strokes, or put a Kandinsky concentric circle, a plain triangle or a soft colour field "
        "instead. Keep EVERYTHING else exactly the same: identical composition, camera, framing, the girl (face, outfit, "
        "long hair, pencil, pose) unchanged, buildings, clock, agents and ghosts unchanged, Klimt gold spirals and mosaic "
        "kept, same hand-drawn colored-pencil-over-engraving style. Full bleed, no border, no text.")


def main():
    jobs, outs = [], []
    for a in sys.argv[1:]:
        shot, src = a.split("=")
        out = os.path.join(SHOTS, shot, "kf_clean.png")
        jobs.append((NANO, EDIT, [src], out, f"F_derainbow_{shot}"))
        outs.append((shot, src))
    res = run_parallel(jobs, workers=8)
    items = []
    for shot, src in outs:
        p = res.get(os.path.join(SHOTS, shot, "kf_clean.png"))
        if isinstance(p, str):
            to169(p)
            items += [(os.path.join("/home/jade/Documents/rewind-take-two", src), f"{shot} before"), (p, f"{shot} after")]
    sheet(items, os.path.join(SHOTS, "F_derainbow_sheet.jpg"), cols=4, cell_w=600, title="F polish: rainbows out")


if __name__ == "__main__":
    main()
