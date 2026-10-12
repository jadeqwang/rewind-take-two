"""v5-build: the post-credits stills (nano-banana-pro 2K, tag v5_build_*). Each output gets a .json beside it with the
model, prompt and refs. Plan: docs/revisions/v5/build.md.

    $PY tools/sectionF/coda/gen_build.py [name ...] [--dry-run]
names: lobby, committee_a, committee_b, pixel, doorway (default: all that do not exist yet)
"""
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
import cf  # noqa: E402

OUT = "media/shots/PC/gen"
COMMITTEE = "inputs/committee_v3_long_ponytails_ff.png"
NOR = ("Absolutely no red anywhere (use orange, gold, magenta, violet, pale blue, teal and green instead). No text, no "
       "captions, no watermark.")
SHEET = ("Redraw these young women as standing full-length figures, head to toe, each one facing the viewer, standing "
         "calmly and patiently as if waiting in a queue, arms relaxed at the sides, feet flat on the ground. Keep the exact "
         "anime illustration style, line weight, faces and colouring of the reference image. Each wears the same outfit as "
         "in the reference: an open white cropped bomber jacket with one orange band across the chest and sleeves and a "
         "small pale-blue dot on the left chest, a black mock-neck crop top, plus black high-waisted wide trousers and white "
         "sneakers. Draw the {n} figures side by side in one row, evenly spaced with clear empty space between them, none "
         "overlapping, none touching the image edges, all the same height, on a perfectly flat plain light grey background "
         "(#bdbdbd) with no floor, no shadow, no table, no props except as listed. From left to right: {who}. " + NOR)
JOBS = {
    "lobby": dict(refs=["media/reviews/v5/plans/coda/lobby_line_color.jpg", "media/shots/O2/kf_v3_last.jpg"], prompt=(
        "The receptionist's point of view, standing behind the front desk of the Hilbert Hotel lobby, eye level a little "
        "above a standing person's head. Strict one-point perspective: the vanishing point is exactly at the horizontal "
        "centre of the image and 36% of the way down from the top. The lobby is an endless grand hall: identical pale "
        "marble columns, arches and crystal chandeliers repeating in two rows on both sides and shrinking toward the "
        "vanishing point forever, with a long straight deep teal and gold carpet runner running exactly down the middle of "
        "the hall from the desk to the vanishing point. The hall is completely EMPTY: no people at all. Foreground, across "
        "the bottom fifth of the frame: the top of a polished honey-oak reception desk seen from behind; on it, left of "
        "centre, a brass service bell, and in the centre an open guest ledger lying flat facing the viewer, its two cream "
        "pages completely BLANK (no writing, no lines, no numbers). Same hand-drawn style and soft warm palette as the first "
        "reference: fine black engraved cross-hatching with coloured pencil laid into the hatching on warm cream paper, "
        "lilac and cream marble, gold leaf, Kandinsky circles and triangles in the wall panels, soft warm light. Wood is "
        "honey oak or walnut, never mahogany. " + NOR)),
    "committee_a": dict(refs=[COMMITTEE], prompt=SHEET.format(n=4, who=(
        "(1) the one with round glasses and long black twin-tails (in the reference she reads a notebook); "
        "(2) the one with long black hair whose ends are dyed teal (teal tips); "
        "(3) the one with a short purple bob; "
        "(4) the one with two long black braids")), aspect="16:9"),
    "committee_b": dict(refs=[COMMITTEE], prompt=SHEET.format(n=4, who=(
        "(1) the one with plain long straight black hair, holding a pen; "
        "(2) the sleepy one with her black hair in a bun, eyes closed, standing but dozing with her head tilted; "
        "(3) the one with long curly rainbow hair in teal, blue and violet, holding a small bag of chips; "
        "(4) the one with long black twin-tails who wears a mint-green jacket instead of the white one and blows a pink "
        "bubblegum bubble")), aspect="16:9"),
    "pixel": dict(refs=["media/reviews/v5/plans/coda/sprites/jade.png", "media/design/jade_canon_turnaround.png"], prompt=(
        "An 8-bit pixel-art video game sprite of this young woman, standing, facing the viewer, full body head to toe, like "
        "an NES-era platformer hero about 48 pixels tall, shown hugely enlarged with perfectly crisp square pixels and a "
        "limited palette of about 12 flat colours, no anti-aliasing, no gradients. Black hair in a bun with two yellow "
        "pencils crossed through it, glasses, white cropped jacket with an orange band and a pale-blue dot, black top, "
        "orange headphones round her neck, navy trousers with orange straps, white sneakers, a yellow pencil in her right "
        "hand. One single sprite in the centre of the image on a perfectly flat plain light grey background (#bdbdbd), no "
        "floor, no shadow. " + NOR), aspect="1:1"),
    "doorway": dict(refs=["media/reviews/v5/plans/coda/door_color.jpg"], prompt=(
        "Edit this image: remove the glass door leaf completely (the whole door between the two dark wooden jambs, with "
        "its glass, its gold HILBERT HOTEL emblem, its brass handle and the little brass bell on its spring) so that the "
        "doorway stands wide open. Through the open doorway we now look straight into the warm, softly lit hotel lobby: "
        "a grand hall with pale marble columns, arches and crystal chandeliers receding in one-point perspective, a deep "
        "teal and gold carpet runner down the middle, warm golden light, completely empty of people. Keep everything "
        "outside the doorway exactly as it is: the arch, the stained-glass side panels with their circles and triangles, "
        "the stone and wood, the framing and the drawing style (fine engraved hatching with coloured pencil on warm "
        "paper). The lobby inside is drawn in the same style, in focus. " + NOR)),
}


def run(name, dry):
    j = JOBS[name]
    out = f"{OUT}/{name}.jpg"
    inp = {"prompt": j["prompt"], "aspect_ratio": j.get("aspect", "16:9"), "image_size": "2K",
           "image_input": [f"file:{r}" for r in j["refs"]]}
    paths = cf.generate("google/nano-banana-pro", inp, os.path.join(ROOT, out), tag=f"v5_build_{name}", dry_run=dry)
    if not dry:
        json.dump({"model": "google/nano-banana-pro", "prompt": j["prompt"], "refs": j["refs"], "aspect_ratio": inp["aspect_ratio"],
                   "image_size": "2K", "seed": None, "out": paths}, open(os.path.join(ROOT, f"{OUT}/{name}.json"), "w"), indent=1)
    return name, paths


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or [n for n in JOBS if not os.path.exists(os.path.join(ROOT, OUT, n + ".jpg"))]
    os.makedirs(os.path.join(ROOT, OUT), exist_ok=True)
    with ThreadPoolExecutor(5) as ex:
        for name, p in ex.map(lambda n: run(n, dry), names):
            print(name, p)
