"""v3 revision pass, stream GO (G1-G3 two-pencil bun + sleeve roundel, O2 restage): keyframe edits and Seedance takes.

    PY=~/Documents/moongazing/.venv/bin/python
    $PY tools/sectionE/go_v3.py kf NAME [NAME ...]        # nano-banana-pro keyframe edits (KF table below)
    $PY tools/sectionE/go_v3.py submit SHOT [--dry-run]   # Seedance 2.0 720p take (VID table; first + optional last frame)
    $PY tools/sectionE/go_v3.py wait SHOT [SHOT ...]
Takes land in media/gen/<SHOT>/take_N.mp4 (vgen convention). Tags: revA_go_*.
"""
import concurrent.futures as cfut
import os
import sys

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
import cf  # noqa: E402
import gen  # noqa: E402
import vgen  # noqa: E402

NANO = "google/nano-banana-pro"
SD20 = "bytedance/seedance-2.0"
K = "media/shots/"
CANON = "media/style_tests/refs/jade_canon_turnaround.jpg"
BUNREF = "media/shots/O2/_ref_bun_two_pencils.jpg"   # JPEG copy of media/design/jade_bun_two_pencils.png (rev-A's two-pencil sheet)

TWO = ("TWO classic yellow hexagonal pencils with silver ferrules are pushed through the bun, crossed in an X like a pair "
       "of hair sticks: one has a pink eraser, the other has a pale sky-blue eraser. Both erasers point up and outward "
       "above the bun; both sharpened points come out below the bun on the far side. Each pencil is one perfectly "
       "straight line from eraser to point (the part hidden inside the bun lines up with the visible ends). Exactly two "
       "pencils, not one, not three.")
PATCH = ("The round white patch with a black ring on her left upper sleeve carries crisp, bold black sans-serif "
         "lettering on two centred lines: '1420' on the first line and 'MHz' on the second (capital M, capital H, "
         "lowercase z). Spell it exactly.")
KEEP = ("Keep EVERYTHING else exactly the same as the first image: identical composition, camera, framing, pose, face, "
        "outfit, colours, line art, cel shading and the blank warm off-white paper background with its few drifting "
        "black hatch fragments. Full bleed, no border. No other text.")
RAINBOW = ("The yellow pencil in her hand has a pale sky-blue eraser on a silver ferrule, and its sharpened wooden point "
           "shows a multicolour core: tiny concentric swirls of orange, yellow, green, blue, violet and magenta instead of "
           "graphite.")

HALL = ("Dawn in a university hallway, tall arched windows on the right pouring soft pink-gold light across the floor, the "
        "same hall and the same drawing technique as the first image: an M.C. Escher wood engraving (crisp black ink line "
        "work, dense parallel hatching that follows form) hand-coloured with soft coloured pencil on warm paper, a little "
        "Klimt gold-leaf ornament on the door frame, Kandinsky circles and triangles in the window glass. Hand-drawn, "
        "not a painting, not photographic, not 3D. No red.")
JADE_BACK = ("The girl is the full-colour anime character of the second image (clean cel shading), seen from BEHIND, her "
             "back to the camera: white cropped bomber jacket whose back is plain white with ONE large pale sky-blue "
             "circle in the centre and nothing else on it (no emblem, no square, no logo, no lettering), one orange band "
             "running round each sleeve at the upper arm and across the back just below the shoulder blades, orange "
             "headphones round her neck, navy wide-leg cargo pants with orange straps, chunky white sneakers.")
DOOR = ("The door is a tall, plain, panelled wooden door with NO plaque, NO sign, NO notice, NO paper and no writing of any "
        "kind on it. Its round brass knob is on the door's RIGHT edge and its three brass hinges are on its LEFT edge.")

KF = {
    # name: (out, prompt, [inputs])
    "G1": (K + "G1/kf_v3_a.jpg", "Edit this anime key frame. Change only her hair accessory and the sleeve patch. Her black "
           f"hair stays in the same loose messy bun. {TWO} A small glint of light sits on the pale-blue eraser. {PATCH} {KEEP}",
           [K + "G1/kf_a.jpg"]),
    "G2_first": (K + "G2/kf_v3_first.jpg", "Edit this anime key frame. Change only her hair accessory and the sleeve patch. "
                 f"Her black hair stays in the same loose messy bun, still tied. {TWO} Her raised right hand pinches the "
                 f"pencil with the pale sky-blue eraser, ready to pull it out. {PATCH} {KEEP}", [K + "G2/kf_first_b.jpg"]),
    "G2_last": (K + "G2/kf_v3_last.jpg", f"Edit this anime key frame. Change only the pencil and the sleeve patch. {RAINBOW} "
                f"She holds exactly one pencil. Her long hair stays loose and floating. {PATCH} {KEEP}", [K + "G2/kf_last_a.jpg"]),
    "G3_first": (K + "G3/kf_v3_first.jpg", f"Edit this anime key frame. Change only the pencil and the sleeve patch. {RAINBOW} "
                 f"She holds exactly one pencil. {PATCH} {KEEP}", [K + "G3/E_G3_kf_first.jpg"]),
    "O2_first": (K + "O2/kf_v3_first.jpg", f"Redraw the scene of the first image as a new key frame. {HALL} {JADE_BACK} "
                 "She stands on the hallway floor directly in front of the closed door, facing it, about one step away, "
                 "large in frame from the knees up; the camera is behind her and a little to her right, so we see her "
                 "back, the back of her head and the whole door beyond her left shoulder. " + DOOR + " Her long black hair "
                 "is gathered, twisted and coiled into a neat round bun at the crown of her head; her LEFT hand is raised "
                 "and holds the coiled bun in place. One yellow hexagonal pencil with a pink eraser already goes straight "
                 "through the bun on a diagonal, eraser up to the upper left, point out at the lower right. Her RIGHT hand "
                 "is raised and holds a second yellow pencil with a pale sky-blue eraser, its sharpened point touching the "
                 "upper right edge of the bun, about to slide through it on the opposite diagonal so the two pencils will "
                 "cross in an X. Both elbows are up. Full bleed, edge to edge, no border, no margin, no paper edge, 16:9. "
                 "No text, no letters, no numbers, no signature.", [K + "O2/kf_1.jpg", CANON]),
    "O2_last": (K + "O2/kf_v3_last.jpg", "Edit this key frame into the last frame of the same shot, a few seconds later. "
                "Same hallway, same camera, same framing, same drawing technique and colours. The door is now OPEN: it has "
                "swung INWARD, away from the camera, into the room beyond, turning on the hinges at its LEFT edge, so the "
                "door leaf now stands angled deep inside the room on the left side of the doorway and we see its edge and "
                "inner face in perspective. Through the open doorway a bright seminar room glows with warm morning light. "
                "The girl has both arms down and is walking through the doorway, mid-stride across the threshold, still seen "
                "from behind, a little smaller because she is further away; her right hand trails on the edge of the open "
                "door. Her bun now holds itself: the two yellow pencils (one pink eraser, one pale sky-blue eraser) are "
                "crossed through it in a clean X, erasers up, each pencil perfectly straight. The back of her white jacket "
                "shows one large pale sky-blue circle and the orange band, nothing else. No plaque, no sign and no writing "
                "anywhere. Full bleed, no border. No text.", [K + "O2/kf_v3_first.jpg"]),
}

RAINBOW_REF = ("The pencil in her hand is exactly the RAINBOW pencil from the prop callout at the bottom of the second image "
               "(the bun reference sheet): a plain yellow hexagonal barrel with no pattern on it, a silver ferrule and a pale "
               "sky-blue eraser at the back end, and a sharpened wooden cone whose core is a rainbow swirl instead of graphite. "
               "The second image is only a prop reference: do not copy its heads or layout.")
KF.update({
    # round 2: the same edits with rev-A's two-pencil reference sheet as image 2
    "G2_last2": (K + "G2/kf_v3_last2.jpg", f"Edit the first image (an anime key frame). Change only the pencil. {RAINBOW_REF} She "
                 f"holds exactly one pencil. Her long hair stays loose and floating. {KEEP}", [K + "G2/kf_v3_last.jpg", BUNREF]),
    "G3_first2": (K + "G3/kf_v3_first2.jpg", f"Edit the first image (an anime key frame). Change only the pencil. {RAINBOW_REF} She "
                  f"holds exactly one pencil. {KEEP}", [K + "G3/kf_v3_first.jpg", BUNREF]),
    "O2_first2": (K + "O2/kf_v3_first2.jpg", "Edit the first image (a key frame). Keep the hallway, the door, the camera, the "
                  "framing, her pose and the drawing technique exactly. Change only the two pencils so they match the prop callout "
                  "at the bottom of the second image (the bun reference sheet): (1) the pencil already through her bun is the "
                  "graphite pencil, a plain yellow barrel lying on a diagonal straight through the bun, its PINK ERASER and silver "
                  "ferrule at the UPPER LEFT end above the bun and its dark sharpened point coming out at the LOWER RIGHT below the "
                  "bun, one perfectly straight line; (2) the pencil in her raised right hand is the rainbow pencil, a plain yellow "
                  "barrel with a PALE SKY-BLUE ERASER at the upper right end (the end furthest from the bun) and its sharpened "
                  "rainbow-cored point touching the upper right edge of the bun, aimed down-left so it will cross the first pencil "
                  "in an X. Erasers up, points down. The door stays plain: no plaque, no sign, no writing. The second image is "
                  "only a prop reference: do not copy its heads or layout. Full bleed, no border, no text.",
                  [K + "O2/kf_v3_first_crop.jpg", BUNREF]),
})
KF["O2_last"] = (K + "O2/kf_v3_last.jpg", KF["O2_last"][1] + " The two crossed pencils sit in the bun exactly as in the bun "
                 "reference sheet (second image; a prop reference only, do not copy its heads or layout).",
                 [K + "O2/kf_v3_first2.jpg", BUNREF])

# (nano-banana returns PNG here; the kf_v3_first3.jpg on disk is that image with a stray eraser stub painted out by hand.
#  G2/kf_v3_first3.jpg is G2/kf_v3_first2.jpg with its third pencil removed by cv2.inpaint.)
KF["O2_first3"] = (K + "O2/kf_v3_first3.jpg", "Edit the first image (a key frame). Keep the hallway, the door, the camera, the "
                    "framing, her body, her jacket and the drawing technique exactly. There must be EXACTLY TWO pencils in the "
                    "picture, both already in her bun, crossed in an X as in the bun reference sheet (second image; prop reference "
                    "only, do not copy its heads or layout). REMOVE the third pencil, the one her right hand holds out to the right "
                    "of the bun: erase it completely. Instead her raised right hand grips the upper-right end (the pale sky-blue "
                    "eraser end) of the pencil that is already in the bun, as if she has just pushed it through. Both pencils have "
                    "plain yellow barrels with no stripes and no pattern: recolour the rainbow-striped barrel to plain yellow. The "
                    "upper-left pencil keeps its pink eraser, the upper-right pencil keeps its pale sky-blue eraser; both points "
                    "come out below the bun. Her left hand still holds the bun. No plaque, no sign, no writing on the door. Full "
                    "bleed, no border, no text.", [K + "O2/kf_v3_first2.jpg", BUNREF])
KF["O2_last"] = (KF["O2_last"][0], KF["O2_last"][1], [K + "O2/kf_v3_first3.jpg", BUNREF])

KF["G2_first2"] = (K + "G2/kf_v3_first2.jpg", "Edit the first image (an anime key frame). Keep her pose, face, outfit, framing and "
                    "the blank paper background exactly. Fix only the pencils in her bun: there must be EXACTLY TWO pencils in the "
                    "whole picture, crossed in an X through the bun exactly as in the three-quarter view of the bun reference sheet "
                    "(second image; prop reference only, do not copy its heads or layout): one plain yellow pencil with a PINK "
                    "eraser, one plain yellow pencil with a PALE SKY-BLUE eraser, erasers up, both points coming out below the bun, "
                    "each pencil perfectly straight. Erase every other pencil, eraser or pencil point. Her raised right hand pinches "
                    f"the pale sky-blue eraser end, ready to pull that pencil out. {PATCH} Full bleed, no border. No other text.",
                    [K + "G2/kf_v3_first.jpg", BUNREF])

# ---- O2 round 2 (rev-A: the insertion itself must be on screen): the second pencil is still in her hand ----------------
KF["O2_b_first"] = (K + "O2/kf_v3b_first.jpg", "Edit the first image (a key frame). Keep the hallway, the door, the camera, the "
                    "framing, her body, her jacket, her bun and the drawing technique exactly. In the first image two yellow pencils "
                    "are crossed through her bun. Change ONE of them: the pencil with the PALE SKY-BLUE eraser (the one whose eraser "
                    "points to the upper right) has NOT been pushed in yet. Draw it pulled back out along its own diagonal line, up "
                    "and to the right: its sharpened point just touches the upper-right edge of the bun, and its whole yellow barrel, "
                    "silver ferrule and pale sky-blue eraser stick out above and to the right of her head in one straight line. Her "
                    "raised RIGHT hand grips the middle of that pencil's barrel, ready to push it down and to the left through the "
                    "bun. Nothing of that pencil shows at the lower left of the bun any more: remove its point there. The other "
                    "pencil (PINK eraser at the upper left, dark point at the lower right) stays exactly where it is, straight "
                    "through the bun. Her LEFT hand still holds the bun against her head. EXACTLY TWO pencils in the whole picture, "
                    "both with plain yellow barrels, the same two as in the prop callout of the second image (a prop reference only: "
                    "do not copy its heads or layout). No plaque, no sign, no writing on the door. Full bleed, no border, no text.",
                    [K + "O2/kf_v3_first3.jpg", BUNREF])

_PAGE = ("The background stays an almost empty page of warm off-white paper; only a few short black engraved hatch-line "
         "fragments drift very slowly around her like iron filings. No other colour appears in the background.")
_FACE = "Her face and outfit keep the first frame's design exactly; forehead smooth, brows relaxed, never a face close-up."
_PATCHV = "The round sleeve patch keeps its lettering exactly as in the first frame."
NO_TEXT = "No new text, no subtitles, no logos, no watermark."
LOOK_O2 = ("Keep the exact hand-drawn look of the first frame: coloured pencil over black engraved hatching on warm paper, "
           "the girl in clean anime cel shading. No text, no letters, no logos, no watermark.")

VID = {
    "revA_go_G1": dict(model=SD20, image=K + "G1/kf_v3_a.jpg", duration=5, camera_fixed=False, prompt=(
        "Slow motion, weightless, she floats in mid-air and drifts very slowly upward, her body turning gently. She slowly "
        "turns her raised hand and looks at it with quiet wonder. The two crossed yellow pencils stay in her bun, perfectly "
        "still and straight; a soft glint of light runs along the one with the pale-blue eraser. Camera: slow steady "
        f"push-in. {_PAGE} {_FACE} {_PATCHV} {NO_TEXT}")),
    "revA_go_G2": dict(model=SD20, image=K + "G2/kf_v3_first3.jpg", last=K + "G2/kf_v3_last2.jpg", duration=5, camera_fixed=False,
                       prompt=(
        "Slow motion, weightless, she floats in mid-air. Early in the shot, within the first second, she pulls the yellow "
        "pencil with the pale-blue eraser out of her bun in one smooth motion; the bun comes undone, the other pencil slips "
        "free and drifts away out of frame, and her long black hair falls loose and unfurls slowly, spreading out "
        "weightlessly to waist length, floating and rippling as if underwater for the rest of the shot. She brings the "
        "pale-blue-eraser pencil down in front of her chest and looks at it. Camera: slow low-angle orbit, circling slightly "
        f"around her. {_PAGE} {_FACE} {_PATCHV} {NO_TEXT}")),
    "revA_go_G3": dict(model=SD20, image=K + "G3/kf_v3_first2.jpg", duration=5, camera_fixed=False, prompt=(
        "Slow motion, weightless, she floats in mid-air, her long loose hair drifting. She draws ONE single slow curved "
        "stroke in the empty air with the yellow pencil, her arm moving in one smooth graceful arc. The pencil tip leaves "
        "ONE single thin flat matte coloured-pencil line like a crayon mark on paper, grainy waxy texture, no wider than "
        "the pencil itself. The colour of the line changes gradually ALONG its length, like the mark of a rainbow-core "
        "pencil: orange where it starts, then yellow, green, sky blue and violet nearest the pencil. It is one line, not "
        "parallel stripes and not a rainbow arch. At the start of the shot the air in front of her is completely empty; "
        "she begins the stroke after a short moment. The line is flat and "
        "does not glow: no light, no neon, no sparkles, no glow, no particles. The line stays still in the air after it is "
        f"drawn. Camera: very slow push-in. {_PAGE} {_FACE} {_PATCHV} {NO_TEXT}")),
    "revA_go_O2": dict(model=SD20, image=K + "O2/kf_v3_first3.jpg", last=K + "O2/kf_v3_last.jpg", duration=6, camera_fixed=True,
                       prompt=(
        "Seen from behind. Her left hand holds the coiled bun steady while her right hand pushes the pencil with the "
        "pale-blue eraser the last little way through the bun, so the two yellow pencils sit crossed in a firm X; she gives "
        "the bun a small test tug, lets go with both hands, and the bun holds by itself. There are only ever two pencils. "
        "She lowers both arms. Then she reaches out with her right "
        "hand, turns the brass knob and pushes the heavy wooden door: the door swings INWARD, away from her, into the "
        "room, turning on the hinges at its left edge; warm bright morning light spills out through the doorway. She walks "
        "forward through the doorway into the light. Static locked-off camera, soft dawn light slowly brightening. "
        "Nothing is written on the door. " + LOOK_O2)),
}
VID["revA_go_O2b"] = dict(model=SD20, image=K + "O2/kf_v3b_first.jpg", last=K + "O2/kf_v3_last.jpg", duration=6, camera_fixed=True,
                          prompt=(
    "Seen from behind. Her left hand holds the coiled bun flat against her head. In the first two seconds her right hand "
    "pushes the second yellow pencil, point first, steadily into the edge of the bun and all the way through it, so that "
    "it slides across the first pencil and its point comes out on the far side of the bun; the two pencils now sit "
    "crossed in a firm X, each one a straight line, erasers up. She lets go with both hands and the bun holds by itself. "
    "There are only ever two pencils. She lowers both arms. Then she reaches out with her right hand, turns the brass "
    "knob and pushes the heavy wooden door: the door swings INWARD, away from her, into the room, turning on the hinges "
    "at its left edge; warm bright morning light spills out through the doorway. She walks forward through the doorway "
    "into the light. Static locked-off camera, soft dawn light slowly brightening. Nothing is written on the door. "
    + LOOK_O2))
for name, s in VID.items():
    vgen.SHOTS[name] = s

_orig = vgen.build_spec


def build_spec(shot, res, note="", over=None):
    spec = _orig(shot, res, note, over)
    s = {**vgen.SHOTS[shot], **(over or {})}
    if s.get("last"):
        spec["input"]["last_frame_image"] = "file:" + os.path.relpath(gen.ref_image(os.path.join(ROOT, s["last"])), ROOT)
    return spec


vgen.build_spec = build_spec


def kf(name):
    out, prompt, inputs = KF[name]
    paths = cf.generate(NANO, {"prompt": prompt, "aspect_ratio": "16:9", "image_size": "2K",
                               "image_input": ["file:" + p for p in inputs]}, os.path.join(ROOT, out), tag=f"revA_go_kf_{name}")
    return name, paths


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    opts = {a[2:].partition("=")[0]: a[2:].partition("=")[2] or True for a in sys.argv[2:] if a.startswith("--")}
    os.chdir(ROOT)
    if cmd == "kf":
        with cfut.ThreadPoolExecutor(6) as ex:
            for r in ex.map(lambda n: kf(n), args):
                print(r)
    elif cmd == "submit":
        for s in args:
            over = {k: (int(v) if k == "duration" else v) for k, v in opts.items() if k in ("duration", "prompt", "last", "image")}
            for j in vgen.submit(s, opts.get("res", "720p"), int(opts.get("takes", 1)), "dry-run" in opts, opts.get("note", ""), over):
                print(s, j)
        print(f"spend so far (est): ${vgen.spend_total()}")
    elif cmd in ("collect", "wait"):
        import time
        t0 = time.time()
        while True:
            p = vgen.collect(args)
            if cmd == "collect" or not p or time.time() - t0 > float(opts.get("timeout", 1500)):
                print("pending:", p)
                break
            time.sleep(30)
    else:
        print(__doc__)
