#!/usr/bin/env python3
"""v9 fixes #2 (D3) and #3 (C_V2f_car): one physically real interior rear-view mirror in one car interior.

    PY=~/Documents/1-music-shipped/moongazing/.venv/bin/python
    $PY tools/v9/mirrors/gen.py LIST
    $PY tools/v9/mirrors/gen.py run v2f_roof_a v2f_roof_b [--dry-run]
    $PY tools/v9/mirrors/gen.py run d3_a d3_b [--dry-run]
    $PY tools/v9/mirrors/gen.py vid v9_d3 [--dry-run]       # Seedance 2.0 take of the chosen D3 keyframe
    $PY tools/v9/mirrors/gen.py wait v9_d3

Every paid call is tagged v9_mirrors_<job>; prompts and refs are appended to media/shots/<shot>/kf_log.jsonl.
No lettering is drawn by the model: plates, the sign and the mirror etch are pinned by the engine.
"""
import concurrent.futures as cfut
import glob
import json
import os
import shutil
import sys
import time

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
sys.path.insert(0, os.path.join(ROOT, "tools/sectionA"))
import cf  # noqa: E402
from common import ref, trim_margins  # noqa: E402
from PIL import Image  # noqa: E402

NBP = "google/nano-banana-pro"
F3, D3 = "media/shots/V2f3", "media/shots/D3"

NIGHT = ("Drawn as an M.C. Escher wood engraving at night: the dark sky, the car interior and all shadows are carved "
         "from dense black ink with fine white engraved lines, every light is a crisp white engraved starburst of "
         "radiating lines, warm off-white paper shows only in the lit areas. Crisp black ink lines, dense precise "
         "parallel hatching and cross-hatching that follows form, high contrast, no gray wash, no airbrush. Full bleed, "
         "edge to edge, no border, no margin, 16:9. ")
NOTEXT = ("There is NO text, no letters, no numbers and no writing anywhere: licence plates are blank pale rectangles, "
          "the sign panel is blank, the mirror carries no writing, no watermark, no caption. No red anywhere. ")

V2F_ROOF = (
    "Edit image 1. It is a finished picture of a girl driving at night, seen from the back seat over her right "
    "shoulder, into which crude FLAT GREY placeholder shapes and one dark placeholder rectangle have been painted. "
    "Keep EVERYTHING else exactly as it is: the girl (her face, hair, bun, the two crossed pencils, headphones, "
    "jacket, hands), the steering wheel, the dashboard, the radio, both seats, the road and the small rear-view "
    "mirror with the sedans in it must not change at all, same places, same sizes, same colours. "
    "Redraw ONLY the placeholders, in the same black-and-white wood-engraving line work as the rest of the car "
    "interior (image 2 shows how this car's roof, header and mirror mount look close up): "
    "1. The big grey area across the top is the car's ROOF LINER, seen from inside and below: a dark padded fabric "
    "ceiling engraved with fine hatching, running right across the top of the picture and over the girl's head. "
    "Its lower edge is the WINDSHIELD HEADER: the rounded top rim of the windshield with a thin rubber seal, running "
    "across the picture just above the rear-view mirror. "
    "2. The two grey slabs under the roof are the two SUN VISORS, folded up flat against the roof liner, each with a "
    "small clip; the left one is behind the girl's head. "
    "3. The small grey block above the mirror is the mirror's MOUNT and the short STEM: the mirror hangs from the "
    "windshield header on that short stem, exactly as in image 2. Keep the mirror itself unchanged. "
    "4. The grey wedge at the right edge is the right-hand A-PILLAR: the dark padded post at the right edge of the "
    "windshield, running from the header down to the dashboard behind the passenger seat. "
    "5. The dark rectangle with the pale border, left of the mirror, is a blank overhead highway sign panel far "
    "ahead, seen THROUGH the windshield below the header: draw it as a plain dark sign panel with a thin pale border "
    "on a slim steel truss gantry with two thin posts standing at the sides of the road, far away, small; the panel "
    "stays completely blank. Through the rest of the windshield: the night sky, the road and a few distant "
    "streetlights, as before. Nothing of the old overhead gantry is left above the header. "
    "The girl is the ONLY color in the picture. " + NIGHT + NOTEXT)

JADE = ("The driver is EXACTLY the anime girl of image 3 (and of image 1), seen from behind and to her right: same "
        "anime drawing style with clean cel shading, in FULL COLOR. Black hair worn up in a loose bun high on the back "
        "of her head, with exactly TWO classic yellow wooden pencils pushed through the bun and crossed in an X, "
        "erasers up (one pink eraser, one pale-blue eraser), each pencil one perfectly straight stick; long curtain "
        "bangs and a few loose strands fall beside her cheek. Orange over-ear headphones rest around her neck. She "
        "wears her white cropped bomber jacket with an orange band around the sleeve, over a black mock-neck top. ")

D3_KF = (
    "Image 1 is a finished frame from the same film: the inside of the girl's car, a white left-hand-drive 2001 Acura TL "
    "sedan, at night, seen over her right shoulder. Image 2 is a close-up of the same car's interior rear-view mirror "
    "on its stem under the roof liner. Image 3 is the girl's character sheet. Draw a NEW, CLOSER frame inside the same "
    "car, with the same interior (same dark roof liner, windshield header, sun visors, mirror and mirror stem, same "
    "steering wheel and dashboard) and the same drawing style. "
    "Camera: in the back seat, just behind and to the right of the driver's head, at the height of her eyes, looking "
    "forward and a little up toward the rear-view mirror; an over-the-shoulder shot. "
    "On the LEFT of the picture, large and close: the girl in the driver's (left) seat, seen from behind and to her "
    "right: the back of her head and her bun with the two crossed pencils at the upper left, her right ear, her "
    "cheek, the line of her jaw and her right eye. She does not turn her head: only her eye glances up and to the "
    "right, into the rear-view mirror, wary. Her right shoulder at the lower left. " + JADE +
    "In the UPPER MIDDLE of the picture, slightly right of centre: the car's interior REAR-VIEW MIRROR, the same mirror "
    "as image 2, about a third of the picture wide, a wide shallow rounded rectangle in a black plastic housing, "
    "hanging on a short black stem from its mount on the windshield header at the top centre of the windshield. Above "
    "it, across the whole top of the picture, the dark padded roof liner and the folded-up sun visors. The mirror is "
    "angled toward the driver. Around and below the mirror, through the windshield: Lake Shore Drive at night ahead, "
    "dark road with white lane dashes, a row of tall streetlights as white starbursts, a dark city skyline far away. "
    "At the bottom, the top of the steering wheel rim and her right hand on it. "
    "IN THE MIRROR GLASS, reflected back through the car's own REAR WINDOW (the dark frame of the rear window and the "
    "tops of the two rear-seat headrests show along the bottom and sides of the glass): ONE plain boxy black 1990s "
    "sedan follows close behind, head-on, centred in the glass, its HEADLIGHTS OFF, a dark shape with no lights, "
    "only its windshield catching a glint of a streetlight; a large BLANK pale front licence plate on its bumper; "
    "behind it the dark road and a few streetlights. Above the car in the glass, dark night sky. "
    "The mirror is physically real: it hangs from the header inside the car, in front of the windshield. "
    "The car interior, the road and the night are black-and-white engraving; the ONLY color in the picture is the girl "
    "(skin, hair, the yellow pencils with one pink and one pale-blue eraser, the orange headphones, the orange sleeve "
    "band). " + NIGHT + NOTEXT)


D3_EDIT = (
    "Image 1 is a rough paste-up LAYOUT of a frame from an animated film: the inside of the girl's car (a white "
    "left-hand-drive 2001 Acura TL) at night, seen from the back seat close behind the driver's right ear. Follow its "
    "layout exactly: the girl's head, bun and shoulders on the left at that size and place; the interior rear-view "
    "mirror at the top, right of centre, at exactly that size and place, hanging on its short stem from the "
    "windshield header; the roof liner and the two folded sun visors across the top; the right A-pillar and the "
    "passenger seat back at the right. Redraw the whole frame cleanly as one coherent picture in the drawing style "
    "of images 1 and 2, fixing the paste-up seams. Image 2 is the same car's mirror close up (its housing, stem and "
    "roof liner). Image 3 is the girl's character sheet. Change ONLY these things: "
    "1. The flat grey area at the far left becomes the dark driver's side window and the left A-pillar, at night. "
    "2. Her hands are both on the STEERING WHEEL, which is in front of her: draw the top of the wheel rim across the "
    "lower middle of the picture with her hands on it; no badge visible. "
    "3. Her eye glances UP and to the RIGHT, into the rear-view mirror: only her eye moves, her head keeps exactly its "
    "angle. Wary, mouth closed. "
    "4. IN THE MIRROR GLASS, replace the cars with what is behind her car, seen through her car's own REAR WINDOW: "
    "the dark edges of the rear window and the tops of the two rear-seat headrests along the bottom of the glass; "
    "ONE plain boxy black 1990s sedan close behind, head-on, centred in the glass, its HEADLIGHTS OFF, a dark shape "
    "with no lights on, no light bar, no strobes, a plain grille with no badge, and a large BLANK pale front licence "
    "plate; behind it the dark road and two or three streetlights; dark night sky above. "
    "5. Through the windshield, replace the overhead sign and its gantry with Lake Shore Drive at night: the dark "
    "road curving gently ahead with white lane dashes, a row of tall streetlights as white starbursts along the road, "
    "a low wall and beyond it the dark water of the lake, a few distant city lights. No sign, no gantry. "
    + JADE + "The car interior, the road and the night are black-and-white wood engraving; the ONLY color in the "
    "picture is the girl (skin, hair, the yellow pencils with one pink and one pale-blue eraser, the orange "
    "headphones round her neck). " + NIGHT + NOTEXT)

D3_MIRROR_FIX = (
    "Edit the attached image. Keep the whole picture exactly as it is: same composition, same girl (face, eye, hair, "
    "bun, the two crossed pencils, headphones, jacket, hands), same steering wheel, roof liner, visors, windshield, "
    "lake and streetlights, same mirror housing and stem at the same size and place, same drawing style. Change ONLY "
    "what is reflected in the rear-view mirror glass, so that it is optically correct: in the glass we see the inside "
    "of the girl's own car from the front, looking back: the tops of the two rear headrests and the rear seat backs "
    "at the bottom of the glass, the rear parcel shelf, and above them the car's REAR WINDOW framed by the dark rear "
    "pillars and the roof edge. The black sedan is OUTSIDE the car: seen THROUGH the rear window, on the road behind, "
    "a little smaller, its lower half hidden behind the rear parcel shelf and the boot lid, so that nothing of it "
    "is inside the cabin or between the seats. The sedan's headlights are OFF: dark unlit lamps, a dark grille with "
    "no badge or emblem, a blank pale front licence plate just visible above the parcel shelf. Behind it the dark "
    "road and two streetlights. No text, no letters, no numbers. The world stays black-and-white wood engraving; "
    "only the girl is in colour. Full bleed, 16:9, no border.")

D3_CLOSER = (
    "Edit the attached image. Keep the whole picture exactly as it is: same composition, same girl (face, eye, hair, "
    "bun, the two crossed pencils, headphones, jacket, hands), same steering wheel, roof liner, visors, windshield, "
    "lake and streetlights, same mirror housing and stem at the same size and place, same reflected rear seats, "
    "headrests and rear window in the mirror glass, same drawing style. Change ONLY the black sedan seen through the "
    "rear window in the mirror: it is now much CLOSER behind, tailgating, so it looks about twice as big and fills "
    "most of the width of the rear window, still OUTSIDE the car, seen through the rear window above the rear seat "
    "backs, its bonnet cut off by the bottom edge of the rear window. Its headlights are OFF (dark unlit lamps), a "
    "plain dark grille with NO badge or emblem, and a LARGE BLANK pale front licence plate, clearly visible, centred "
    "just above the bottom edge of the rear window. No text, no letters, no numbers anywhere. The world stays "
    "black-and-white wood engraving; only the girl is in colour. Full bleed, 16:9, no border.")

JOBS = {
    "v2f_roof_a": (F3, "v9_roof_a", V2F_ROOF, [F3 + "/v9_roof_guide.png", "media/shots/V2f4/kf_close_b2.png"]),
    "v2f_roof_b": (F3, "v9_roof_b", V2F_ROOF, [F3 + "/v9_roof_guide.png", "media/shots/V2f4/kf_close_b2.png"]),
    "d3_a": (D3, "kf_v9_a", D3_KF, [F3 + "/v9_roof_a.png", "media/shots/V2f4/kf_close_b2.png", "media/design/jade_canon_turnaround.png"]),
    "d3_b": (D3, "kf_v9_b", D3_KF, [F3 + "/v9_roof_a.png", "media/shots/V2f4/kf_close_b2.png", "media/design/jade_bun_two_pencils.png"]),
    "d3_c": (D3, "kf_v9_c", D3_EDIT, [D3 + "/v9_guide.png", "media/shots/V2f4/kf_close_b2.png", "media/design/jade_bun_two_pencils.png"]),
    "d3_d": (D3, "kf_v9_d", D3_EDIT, [D3 + "/v9_guide.png", "media/shots/V2f4/kf_close_b2.png", "media/design/jade_canon_turnaround.png"]),
    "d3_e": (D3, "kf_v9_e", D3_MIRROR_FIX, [D3 + "/kf_v9_d.png"]),
    "d3_f": (D3, "kf_v9_f", D3_MIRROR_FIX, [D3 + "/kf_v9_d.png"]),
    "d3_g": (D3, "kf_v9_g", D3_CLOSER, [D3 + "/kf_v9_f.jpg"]),
    "d3_h": (D3, "kf_v9_h", D3_CLOSER, [D3 + "/kf_v9_f.jpg"]),
}


def run(name, dry=False):
    shot, stem, prompt, refs = JOBS[name]
    out = os.path.join(ROOT, shot, f"{stem}.png")
    inp = {"prompt": prompt, "aspect_ratio": "16:9", "image_size": "2K", "output_format": "png",
           "image_input": ["file:" + ref(r, 2048) for r in refs]}
    paths = cf.generate(NBP, inp, out, tag=f"v9_mirrors_{name}", dry_run=dry)
    if dry:
        return name, None
    p = paths[0]
    trim_margins(p)
    jpg = os.path.splitext(p)[0] + ".jpg"
    Image.open(p).convert("RGB").save(jpg, quality=93)
    with open(os.path.join(ROOT, shot, "kf_log.jsonl"), "a") as f:
        f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "job": name, "model": NBP, "image_size": "2K",
                            "refs": refs, "prompt": prompt, "out": os.path.relpath(jpg, ROOT)}) + "\n")
    return name, jpg


# ---- video (Seedance 2.0, first frame locked) ----
FACE = ("Her face stays exactly as in the first frame: same face, same profile, head keeps the first frame's angle, "
        "never a face close-up.")
LOOK = ("Keep the exact drawing style of the first frame throughout: black-and-white wood engraving world, only the "
        "anime girl in color. No text, no letters, no subtitles, no logos, no watermark. No red anywhere.")
VIDS = {
    "v9_d3": dict(model="bytedance/seedance-2.0", image=D3 + "/kf_v9.png", duration=4, camera_fixed=True, prompt=(
        "Night, inside the moving car. Locked-off camera on the back seat behind the driver's shoulder; it does not "
        "move. The rear-view mirror stays exactly where it is, hanging on its stem from the roof, and keeps its shape. "
        "In the mirror the unlit black sedan follows steadily, staying the same distance behind, swaying very slightly "
        "in its lane; passing streetlights flicker across the mirror glass and across the roof liner. Through the "
        "windshield the road streams toward us and the streetlights glide past. The girl drives: her eye flicks up to "
        "the mirror and holds there, wary; she blinks once; she breathes; loose strands of her hair stir slightly; she "
        "does not turn her head. The two yellow pencils stay crossed in her bun exactly as in the first frame. " + FACE +
        " " + LOOK)),
}
DEST = {"v9_d3": "D3"}


def vid(cmd, names, opts):
    import vgen
    vgen.SHOTS.update(VIDS)
    if cmd == "vid":
        for s in names:
            for j in vgen.submit(s, opts.get("res", "720p"), int(opts.get("takes", 1)), "dry-run" in opts, opts.get("note", "")):
                print(s, j)
        return
    t0 = time.time()
    while True:
        p = vgen.collect(names)
        if not p or time.time() - t0 > float(opts.get("timeout", 1500)):
            print("pending:", p)
            break
        time.sleep(30)
    for s in names:
        dst = os.path.join(ROOT, "media/shots", DEST[s])
        for f in sorted(glob.glob(os.path.join(ROOT, "media/gen", s, "take_*.mp4"))):
            for src in (f, f.replace(".mp4", "_sheet.jpg")):
                t = os.path.join(dst, "v9_" + os.path.basename(src))
                if os.path.exists(src) and not os.path.exists(t):
                    shutil.copy2(src, t)
                    print("->", os.path.relpath(t, ROOT))


if __name__ == "__main__":
    a = sys.argv[1:]
    opts = {x[2:].partition("=")[0]: x[2:].partition("=")[2] or True for x in a if x.startswith("--")}
    names = [x for x in a[1:] if not x.startswith("--")]
    if not a or a[0] == "LIST":
        for k, (shot, stem, _, refs) in JOBS.items():
            print(k, shot, stem, refs)
    elif a[0] == "run":
        with cfut.ThreadPoolExecutor(4) as ex:
            for name, p in ex.map(lambda n: run(n, "dry-run" in opts), names):
                print(name, "->", p)
    elif a[0] in ("vid", "wait"):
        vid(a[0], names, opts)
