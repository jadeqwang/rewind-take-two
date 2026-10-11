"""Section F keyframes (nano-banana-pro, colored-pencil-over-engraving look locked in the style test).

    $PY tools/sectionF/kf.py [SHOT ...] [--n=2] [--force]
Writes media/shots/<SHOT>/kf_<k>.(jpg|png) and a contact sheet media/shots/F_kf_sheet.jpg.
"""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (COLOR_WORLD, FINISH, JADE_DOWN, NANO, SHOTS, refs, run_parallel, sheet, to169, st, ROOT)  # noqa: E402

REF_AGENTS = "media/design/takes/agent_formation_nano_t1.jpg"
AGENTS = ("The agents are men in black suits, white shirts, black ties and black sunglasses with nearly blank faces, drawn as "
          "pure black-and-white engraving with no color at all: they are the only uncolored things in the picture.")
REFNOTE = ("Reference images: the first two are the character sheets for the girl (match her face, outfit and long loose "
           "hair exactly); the third shows the engraving line technique of the world.")
REFNOTE_AG = ("Reference images: the first is the character sheet for the girl (match her face, outfit and long loose hair "
              "exactly); the second shows the engraving line technique; the third shows the agents' design.")
REFNOTE_NOJADE = "Reference images: the first shows the engraving line technique of the world; the second shows the agents' design."
FULL = ("Every surface is now colored in saturated colored pencil over the hatching, with burnished Klimt gold leaf on "
        "rooftops, cornices and ornaments.")
MAXI = ("Maximal color crescendo: the sky has become a Gustav Klimt gold-leaf mosaic of spirals, eyes and small squares, "
        "with big Kandinsky circles, triangles and arcs in ultramarine, vermilion and magenta; still drawn by hand in colored "
        "pencil with the black engraved hatching visible under the color.")
CLOCK = ("The clock is a colossal Salvador Dali melting pocket watch with a gold case, its face soft and drooping like warm "
         "cheese; the clock face is completely blank except simple short dash tick marks: no numerals, no Roman numerals, "
         "no letters.")

# shot: (scene, extra, refkind)
KF = {
    "F2": ("Dramatic low angle looking straight up the black steel facade of the Willis Tower (Sears Tower) against the sky: "
           "the anime girl runs vertically UP the face of the tower, her body perpendicular to the wall, feet planted on the "
           "facade, large in frame, long black hair streaming down behind her, her right hand dragging her yellow pencil "
           "along the wall so it leaves a bright orange-to-blue colored-pencil line in her wake. Flanking her on both sides "
           "two translucent glowing ghost copies of her, one tinted magenta, one tinted emerald green, run up the wall in step.",
           "", "jade"),
    "F3": ("A scene from M.C. Escher's Relativity: an impossible hall of staircases and archways where gravity points in "
           "three directions. The anime girl, large in the center of frame, sprints along the UNDERSIDE of a staircase as if "
           "it were the floor (upside down relative to the rest of the hall), hair streaming, pencil in hand. Several "
           "black-suited agents lose their footing and tumble off other staircases, falling in different directions.",
           AGENTS, "jade_ag"),
    "F4": ("Looking down from high above and just behind the diving girl: the anime girl dives head-first straight down, "
           "arms stretched forward, long hair streaming up toward the camera, large in the top half of frame; far below "
           "her, the mirror-polished Cloud Gate sculpture (the Bean) in Millennium Park, and in its curved mirror surface "
           "her own full-color reflection dives up toward her. The colored skyline curves around the edges of the mirror.",
           "", "jade"),
    "F5a": ("Hero shot, low angle, slow-motion moment: the anime girl is airborne in the left foreground, large in frame "
            "(head to knees), leaping upward, her yellow pencil drawn back over her shoulder in both hands like a sword "
            "about to strike, long black hair flying, determined. Behind and above her, filling the right half of the sky, "
            "the colossal melting clock hangs over the Chicago Loop skyline, drooping over the skyscrapers, tiny "
            "black-suited agents dripping off its melting edge like drops of ink.",
            CLOCK + " " + AGENTS + " " + FULL, "jade_ag"),
    "F5b": ("Deliberate wide shot at golden hour: the colossal melting clock hangs over the whole Chicago Loop skyline like a "
            "second sun, its soft face draped over the skyscrapers; long drips of black ink run off its lower edge and each "
            "drip turns into a black-suited agent falling toward the rooftops. In the right foreground on a rooftop water "
            "tower, the anime girl stands seen from behind, small but clear, hair blowing, pencil in her hand, facing the clock.",
            CLOCK + " " + AGENTS + " " + FULL, "jade_ag"),
    "F6a": ("Low angle, medium-wide: the anime girl stands on the edge of a skyscraper roof, large in frame from the knees "
            "up, her right arm sweeping her yellow pencil in a huge circle above her head; a glowing gold line trails from "
            "the pencil tip and is drawing a perfect loop in the air around the colossal melting clock behind her in the sky.",
            CLOCK + " " + FULL, "jade"),
    "F6b": ("Frontal view of the colossal melting clock face hanging in the sky over the Chicago Loop: its two clock hands have "
            "become M.C. Escher's Ascending and Descending, an impossible Penrose staircase forming a closed square loop "
            "across the clock face; a single file of dozens of black-suited agents marches around the endless staircase.",
            CLOCK + " " + AGENTS + " " + FULL, "noj"),
    "F6c": ("Side-on tracking shot: the anime girl sprints extremely fast from left to right along the top of the elevated "
            "train tracks of the Loop, large in frame, mid-stride, long hair streaming behind her, pencil in her hand; the "
            "colored city behind her, elevated tracks with gold-leaf rivets.",
            FULL, "jade"),
    "F7a": ("Wide low shot along the elevated train tracks of the Loop: a flood of dozens of translucent glowing ghost copies of "
            "the anime girl, each tinted a different color (orange, sky blue, gold, magenta, emerald), sprint toward the camera "
            "together like a stampede, the real full-color girl leading in front, large in frame.",
            FULL, "jade"),
    "F7b": ("Medium shot from the front-left, waist up: the anime girl runs toward the camera with a huge confident grin, "
            "long black hair whipping in the wind, yellow pencil in her raised hand, the colored city streaking past behind her.",
            FULL, "jade"),
    "F7c": ("Biggest image of the film: the anime girl soars upward through the sky, large in frame, arms spread wide, long "
            "hair fanning out, pencil in her hand, the whole sky around her a swirling Klimt gold-leaf mosaic; far below, the "
            "Chicago Loop in full color.",
            MAXI, "jade"),
    "F7d": ("Close on the colossal melting clock in the sky folding in on itself like soft paper: its drooping face curls and "
            "folds over into a twisted loop, the gold case bending into a Moebius band, ink drips flying off it.",
            CLOCK + " " + MAXI, "noj"),
    "F7e": ("Two identical copies of the anime girl leap toward each other mid-air from the left and right of frame, large, "
            "hands reaching out, about to touch and merge into one, a burst of colored motes and gold leaf flakes between "
            "their hands, above the colored rooftops of the Loop.",
            MAXI, "jade"),
    "F8": ("Calm, center frame, full body: the anime girl stands still on the elevated train tracks facing the camera, "
           "breathing, catching her breath, long hair moving in the wind, pencil held loosely in her hand, a quiet small smile. "
           "Behind her, in a single straight row across the tracks, stand a line of translucent glowing ghost copies of "
           "her, each tinted a different color (orange, sky blue, gold, magenta, emerald), like a committee.",
           FULL, "jade"),
    "O2": ("Dawn. A university hallway with tall arched windows pouring soft pink-gold dawn light across the floor: the anime "
           "girl, seen from behind at three-quarters, stands in front of a tall heavy wooden door with a small BLANK brass "
           "plaque on it (no writing on the plaque), her long black hair down, her yellow pencil in her right hand raised "
           "toward her hair. Large in frame, from the knees up.",
           "The colors are soft dawn colored pencil over engraved hatching, quiet and warm.", "jade"),
}


def refs_for(kind):
    hd, canon, world = refs()
    if kind == "jade":
        return [hd, canon, world], REFNOTE
    if kind == "jade_ag":
        return [hd, world, REF_AGENTS], REFNOTE_AG
    return [world, REF_AGENTS], REFNOTE_NOJADE


def prompt_for(shot):
    scene, extra, kind = KF[shot]
    rf, note = refs_for(kind)
    jade = JADE_DOWN if kind != "noj" else ""
    return f"{scene} {COLOR_WORLD} {extra} {jade} {note} {FINISH}".replace("  ", " "), rf


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opts = {a[2:].partition("=")[0]: a[2:].partition("=")[2] or True for a in sys.argv[1:] if a.startswith("--")}
    n = int(opts.get("n", 2))
    tag = opts.get("tag", "")
    shots = args or list(KF)
    jobs = []
    for s in shots:
        p, rf = prompt_for(s)
        if opts.get("extra"):
            p = opts["extra"] + " " + p
        d = os.path.join(SHOTS, s)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "kf_prompt.txt"), "a").write(f"--- {tag}\n{p}\nrefs={rf}\n")
        have = len([x for x in glob.glob(os.path.join(d, "kf_*.*")) if not x.endswith(".txt")])
        if have and "force" not in opts and not tag:
            continue
        for k in range(n):
            jobs.append((NANO, p, rf, os.path.join(d, f"kf_{tag}{k + 1}.png" if tag else f"kf_{k + 1}.png"), f"F_kf_{s}"))
    run_parallel(jobs, workers=8)
    items = []
    for s in shots:
        for p in sorted(glob.glob(os.path.join(SHOTS, s, "kf_*.*"))):
            if p.endswith(".txt") or "_raw" in p:
                continue
            to169(p)
            items.append((p, os.path.relpath(p, SHOTS)))
    sheet(items, os.path.join(SHOTS, "F_kf_sheet_" + ("_".join(args) if args and len(args) < 4 else "all") + ".jpg"),
          cols=4, cell_w=640, title="Section F keyframes")


if __name__ == "__main__":
    main()
