#!/usr/bin/env python
"""Section D (Drop 2 + "Anomaly detected", 112.96-141.00): keyframe prompts and generation.

    PY=~/Documents/moongazing/.venv/bin/python
    $PY tools/sections/D/kf.py NAME [NAME ...] [--model=nano|flare] [--take=N]
    $PY tools/sections/D/kf.py --list

Writes media/shots/<SHOT>/kf_<name>_<model>_t<N>.png (16:9) and a contact sheet in media/shots/_D/.
"""
import os
import sys

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "media/style_tests/scripts"))
from st import run_all, sheet  # noqa: E402

CANON = "media/design/jade_canon_turnaround.png"
AGENT = "media/design/takes/agent_turn_flare_t1.png"
MODELS = {"nano": "google/nano-banana-pro", "flare": "openai/gpt-image-2.5-flare", "seedream": "bytedance/seedream-5-pro"}

JADE = ("Use the attached character turnaround sheet as the exact, locked design of the girl: same face, same anime drawing "
        "style and proportions. Her outfit exactly: white cropped bomber jacket worn open with an orange band across the "
        "chest and around both sleeves, a small pale-blue dot patch on her left chest, a round black-and-white roundel patch "
        "on her LEFT upper sleeve, a plain pale-blue circle on the back, black crop top, navy-blue wide-leg cargo pants with "
        "hanging orange straps, chunky white sneakers, orange over-ear headphones around her neck, long black hair worn up "
        "in a loose bun with a yellow pencil stuck through it. ")
AGENTS = ("The agents match the attached agent sheet exactly: identical men in plain narrow black suits, white shirts, thin "
          "black ties, opaque black sunglasses, nearly blank mannequin-like engraved faces, coiled earpiece wire; drawn in "
          "the same black-and-white engraving technique as the world. ")
STYLE = ("Rendered as an M.C. Escher wood engraving / lithograph: crisp black ink lines on warm off-white paper, dense "
         "precise parallel hatching and cross-hatching that follows form, high contrast, no gray wash, no color anywhere "
         "except the girl. The girl is a full-color anime character (clean cel shading) exactly matching the reference "
         "sheet. No text, no letters, no numbers, no signs, no signature. Full bleed, edge to edge, no border, no margin, "
         "no paper edge, 16:9.")
TWINS = ("There are two identical copies of the same girl in this picture (the same character twice, same face, same "
         "outfit, both in full color). ")

KF = {
    # ---- E2: thirteen ghosts ------------------------------------------------------------------------------------
    "E2_trk": dict(shot="E2", refs=[CANON], prompt=JADE + (
        "Side-on view, camera level with the elevated train track deck of Chicago's Loop 'L': a riveted steel trestle deck "
        "with rails and wooden sleepers runs straight across the lower quarter of the frame from edge to edge. At the "
        "center-right a tall riveted steel column with cross-braced lattice rises from the deck up past the top edge of "
        "the frame. Behind: brick tenements with fire escapes and rooftop water towers, open sky of horizontal engraved "
        "lines. The girl crouches at the LEFT third of the frame on the deck in a sprinter's start, facing right, about to "
        "burst forward; she is large in frame, her crouched body about 40% of the frame height. The rest of the deck is "
        "empty. Flat side-on platformer staging, camera locked off. ") + STYLE),
    "E2_fld": dict(shot="E2", refs=[CANON, AGENT], prompt=JADE + AGENTS + (
        "Ground-level view across the wide lawn of Grant Park, camera at hip height: the grass carved as flowing engraved "
        "strokes, the Chicago skyline low on the horizon, and an elevated steel L-train trestle crossing the far edge of "
        "the park in the middle distance. Three agents stand on the lawn at the center and right of the frame, a few "
        "steps away, arms reaching toward her, closing in. The girl runs in from the LEFT, mid-stride, facing right toward "
        "them; she is large in frame (full body, head to sneakers about 60% of the frame height). ") + STYLE),
    "E2_ring": dict(shot="E2", refs=[CANON, AGENT], prompt=JADE + AGENTS + (
        "A deliberate wide, high-angle shot looking down at about 35 degrees onto the lawn of Grant Park. In the middle "
        "of the frame, eight agents stand in a tight ring, back to back, facing outward, stunned, heads turned in "
        "different directions. Around them a wide open circle of engraved grass. Along the top edge of the frame an "
        "elevated steel L-train trestle runs horizontally across the park, the skyline beyond it. The girl sprints across "
        "the open grass at the lower left, running around the ring, small but clearly readable (about one sixth of the "
        "frame height). ") + STYLE),
    # ---- E4: Super Meat Boy replay --------------------------------------------------------------------------------
    "E4_gap": dict(shot="E4", refs=[CANON, AGENT], prompt=JADE + AGENTS + (
        "Side-on view of the Loop's elevated L tracks high above the street, camera slightly below deck level looking a "
        "little up. Two sections of riveted steel trestle deck with rails, separated by a wide gap in the middle of the "
        "frame where the span is missing (the street far below). On the right-hand section a small elevated station "
        "platform with four agents standing, looking about, bewildered. The girl sprints in from the left on the left "
        "section, facing right, leaning forward at full speed, her full body about 40% of the frame height. Open sky of "
        "engraved horizontal lines above. ") + STYLE),
    # ---- E5: co-op boost, slip of paper -----------------------------------------------------------------------------
    "E5_boost": dict(shot="E5", refs=[CANON], prompt=JADE + TWINS + (
        "Side-on view on an elevated L station platform beside the blank brick side wall of a building; the building's "
        "flat rooftop edge with a stone cornice is near the top of the frame (the wall is about two and a half times her "
        "height). At the foot of the wall on the LEFT, the first copy of the girl kneels on one knee with her back to the "
        "wall, facing right, both hands cupped together low in front of her knee as a step, ready to boost. The second "
        "copy of the girl sprints in from the RIGHT toward her, mid-stride, facing left. Both full figures, large in "
        "frame, a few steps apart. ") + STYLE),
    "E5_hand": dict(shot="E5", refs=[CANON], prompt=JADE + TWINS + (
        "On a flat tar-paper rooftop in the Loop, rooftop water towers and chimneys behind, a skyline beyond. Medium "
        "two-shot, framed from the knees up: on the left the first copy of the girl holds out a small folded slip of plain "
        "white paper toward the second copy on the right, who reaches for it with her hand. Both in profile toward each "
        "other, friendly, conspiratorial smiles. ") + STYLE),
    "E5_slip": dict(shot="E5", refs=[CANON], prompt=JADE + (
        "Close-up insert: the girl's two hands (white bomber jacket cuffs with the orange band visible at the wrists) hold "
        "a small unfolded slip of plain white paper flat toward the camera, filling the middle of the frame. The paper is "
        "completely BLANK: no writing, no marks, no lines, clean off-white. Her face is out of frame. Behind, an "
        "engraved rooftop with water towers. ") + STYLE),
    # ---- E6: Banach-Tarski ------------------------------------------------------------------------------------------
    "E6_single": dict(shot="E6", refs=[CANON, AGENT], prompt=JADE + AGENTS + (
        "On a wide flat tar-paper rooftop in the Loop with water towers and chimneys, the skyline behind. The girl stands "
        "alone in the exact center of the frame, facing the camera, feet planted, a confident smirk, her full body about "
        "60% of the frame height. Three agents close in from the left and three from the right, mid distance, arms "
        "reaching. Symmetrical composition, camera at chest height, locked off. ") + STYLE),
    "E6_split": dict(shot="E6", refs=[CANON, AGENT], prompt=JADE + TWINS + AGENTS + (
        "On a wide flat tar-paper rooftop in the Loop with water towers and chimneys, the skyline behind. In the exact "
        "center of the frame the two copies of the girl stand back to back, one facing left and one facing right, each in "
        "a crouched sprint start, about to run apart in opposite directions; their full bodies about 55% of the frame "
        "height. Three agents on the left and three on the right, mid distance, caught off guard. Symmetrical composition, "
        "camera at chest height, locked off. ") + STYLE),
    # ---- E7: colour everywhere --------------------------------------------------------------------------------------
    "E7_hero": dict(shot="E7", refs=[CANON], prompt=JADE + (
        "Low-angle shot: the girl sprints straight toward the camera along the top of the elevated L tracks, the rails and "
        "the riveted trestle receding in strong one-point perspective behind her, brick buildings and water towers on "
        "both sides. Euphoric open-mouthed grin, arms pumping, her full body large in frame (about 75% of the frame "
        "height). ") + STYLE),
    "E7_meter": dict(shot="E7", refs=[AGENT], prompt=AGENTS + (
        "Close-up of the chest and hands of one agent (his head is cut off by the top edge of the frame): in front of his "
        "black suit jacket and tie he holds out a round, palm-sized tracking meter like a pocket watch, connected to his "
        "cuff by a coiled cord. The meter's dial has only tick marks around the rim, no numbers, and a single long "
        "needle. Everything is black-and-white engraving. ") + STYLE.replace(" except the girl. The girl is a full-color "
        "anime character (clean cel shading) exactly matching the reference sheet.", ".")),
    "E7_city": dict(shot="E7", refs=[], prompt=(
        "High aerial view over Chicago's Loop: the elevated L tracks form a rectangle through dense city blocks of brick "
        "and stone buildings, rooftops with water towers, tall skyscrapers including Willis Tower, the Chicago River "
        "curving along one side, Lake Michigan at the far horizon. No people. ") + STYLE.replace(
        " except the girl. The girl is a full-color anime character (clean cel shading) exactly matching the reference "
        "sheet.", ".")),
    # ---- E8: anomaly detected ---------------------------------------------------------------------------------------
    "E8_ring": dict(shot="E8", refs=[AGENT], prompt=AGENTS + (
        "Camera slightly above eye level, medium-wide: eight agents stand in a tight ring on the engraved lawn of Grant "
        "Park, back to back, each facing outward, heads turned in different directions, searching. They fill most of the "
        "frame (the nearest are seen from the knees up). The skyline behind. ") + STYLE.replace(
        " except the girl. The girl is a full-color anime character (clean cel shading) exactly matching the reference "
        "sheet.", ".")),
    "E8_line": dict(shot="E8", refs=[AGENT], prompt=AGENTS + (
        "Eye-level medium shot: a row of six agents standing shoulder to shoulder on an elevated L station platform, "
        "framed from the waist up, all six heads turned sharply in profile toward the left of frame, identical. Riveted "
        "steel canopy and brick buildings behind. ") + STYLE.replace(
        " except the girl. The girl is a full-color anime character (clean cel shading) exactly matching the reference "
        "sheet.", ".")),
}


def out_path(name, model, take):
    k = KF[name]
    d = os.path.join(ROOT, "media/shots", k["shot"])
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"kf_{name}_{model}_t{take}.png")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opts = {a[2:].partition("=")[0]: a[2:].partition("=")[2] for a in sys.argv[1:] if a.startswith("--")}
    if "list" in opts:
        print("\n".join(KF))
        sys.exit()
    models = (opts.get("model") or "nano").split(",")
    take = int(opts.get("take") or 1)
    jobs = []
    for n in args:
        for m in models:
            jobs.append(dict(model=MODELS[m], prompt=KF[n]["prompt"], refs=KF[n]["refs"], out=out_path(n, m, take),
                             tag=f"D_kf_{n}", crop=True))
    res = run_all(jobs, workers=8)
    os.makedirs(os.path.join(ROOT, "media/shots/_D"), exist_ok=True)
    tiles = [(p, os.path.basename(o)) for o, p in res.items()]
    sheet(tiles, os.path.join(ROOT, f"media/shots/_D/kf_sheet_{opts.get('sheet', 't%d' % take)}.jpg"),
          "Section D keyframes", cols=2)
