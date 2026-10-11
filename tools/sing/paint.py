#!/usr/bin/env python3
"""Singing Jade, step 2: the engraved Bean plates, and the place painted round her kept trace (nano-banana-pro).

    PY=~/Documents/moongazing/.venv/bin/python
    $PY tools/sing/paint.py plate KEY [--n=2] [--src=IMG]    # world plate (no person); --src = edit an existing plate
    $PY tools/sing/paint.py paint KEY PLATE [--n=2]          # base16 (her trace) + PLATE -> the place round her
    $PY tools/sing/paint.py edit KEY SRC [--n=2]             # change only the reflection of an existing frame
    $PY tools/sing/paint.py list                             # prompt keys

Outputs: media/sing/plates/<KEY>_<i>.png (plates) and media/sing/first/<KEY>_<i>.png (frames). Every call is logged
and capped by tools/gen/cf.py (tag sing_<KEY>). The rules (docs/recon/pipeline.md section 3): her drawing is never
redrawn; the model paints only the place round her; her own lines are put back afterwards (restore.py)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
import cf  # noqa: E402

MODEL = "google/nano-banana-pro"
BASE = "media/sing/first/base16.jpg"

ENGRAVING = ("Black-and-white wood engraving in the style of M.C. Escher's woodcuts and lithographs: dense, precise "
             "cross-hatching and engraved parallel lines, crisp solid black ink on off-white paper; every tone is built "
             "only from lines and hatching; no gray wash, no gradients, no airbrush, no photographic shading. Night is "
             "drawn the engraver's way: dark tones from dense parallel lines and cross-hatching, every light left as white "
             "paper with a small halo of radiating lines. Very high detail, architectural precision. No text, no letters, "
             "no signs, no signature, no border, no frame.")

BEAN_VIEW = ("Night in Millennium Park, Chicago. We stand close in front of Cloud Gate ('the Bean'), the camera at chest "
             "height about three metres from it and looking straight at it, so its seamless polished-steel mirror surface "
             "fills the whole background, bulging gently toward us and curving away out of the top of the picture, with "
             "only a sliver of night sky in the two top corners. The mirror reflects the city behind the camera exactly "
             "like M.C. Escher's 'Hand with Reflecting Sphere': an optically correct, smoothly curved fisheye image. ")

SANE_CITY = ("The Chicago skyline at night bends along the curvature in a curved band running from left to right at about "
             "two thirds of the picture height, tall buildings leaning outward toward the edges, their windows tiny white "
             "engraved cells; the plaza curves away underneath with a few tiny engraved people and lamp posts; above the "
             "skyline the reflected night sky in dense engraved lines. Two small details in the reflection, never "
             "featured: in the right third, far away, the curving ribbon of Lake Shore Drive along the dark lake, with one "
             "tiny pair of white headlights on it; in the left third, on a distant flat rooftop, a tiny staircase whose "
             "four short flights join up into a closed square loop, like Escher's 'Ascending and Descending'. The "
             "reflected city is otherwise sensible and real. ")

CALM_CENTRE = ("The centre of the picture is calm open mirror with soft reflected sky (a person will stand there later), "
               "so the richest reflected detail sits in the left and right thirds of the picture. Nobody stands in the "
               "foreground. ")

TRUTH_CITY = ("Keep everything else exactly as it is: the same Bean, its outline, curvature, seams, highlights, the sky "
              "corners, the plaza, the camera position and framing, and the same engraving and paper. Change only what the "
              "mirror reflects: the reflected city is now the truth, an impossible city by M.C. Escher. Penrose staircases "
              "like 'Ascending and Descending' loop around and around the elevated train tracks of the Loop; the train "
              "tracks themselves run in a closed loop that climbs forever; buildings connect impossibly, a tower's roof "
              "becoming the street of another tower, stairs at right angles to each other as in 'Relativity', a "
              "waterfall-like aqueduct feeding itself. It still sits in the same curved fisheye band and reads at first "
              "glance as a city at night. In a few places the engraving blooms into colored pencil: soft, small patches "
              "of warm orange and pale sky-blue colored-pencil strokes seeping into the reflection, as if someone had "
              "started to color it in, about five patches, mostly in the left and right thirds. Everything outside the "
              "reflection stays black ink on off-white paper. ")

KEEP_HER = ("Make image 1 into a frame for that film, and keep the woman exactly as she is drawn: the same pencil lines, "
            "the same face, head size and shape, the same high forehead and hairline, glasses, the two slightly different "
            "eyebrows, eyes, nose, lips, hair, jacket, pink headphones round her neck, pose, size and position in the "
            "picture. Do not redraw, move, resize, turn, beautify, slim or restyle her in any way: no makeup, no "
            "eyeliner, no outlined lips, no added lines, no smoothing. Her drawing stays the drawing: soft colored pencil "
            "is laid lightly over her graphite lines, the way an illustrator tints a finished pencil portrait, and the "
            "soft pencil shading of her face, neck and hair stays visible under the colour. She is the only thing in "
            "colour in the picture, a soft pencil drawing, a little gentler than the crisp engraved world around her. ")

HER_COLOURS = ("Her colours: pale warm skin; ink-black hair with the drawn strands still showing; thin dark glasses frames "
               "with clear lenses; the cropped jacket white with its warm orange band across the chest and sleeve; the "
               "top black; the headphones pale dusty pink. ")

PLACE = ("The place around her is image 2, kept as it is drawn: she stands close in front of the Bean at night and its "
         "mirror fills the whole background behind her, with the reflected city to the left and right of her and above "
         "her shoulders, exactly as in image 2. Everything around her is the black-and-white wood engraving of image 2: "
         "crisp black ink lines and cross-hatching on off-white paper, no colour in it anywhere. The mirror does not "
         "show her own reflection. ")

LIGHT = ("One light: soft, cool, even light from the front, from the park's lamps behind the camera, on her face, hair "
         "and jacket; no hard shadows on her face. She must look like she is standing in that place, not pasted onto "
         "it: the same off-white paper runs under her and the engraving, with no cutout edge, no glow, no halo and no "
         "pale outline round her. ")

STRICT = ("Strict: 16:9, drawn to all four edges, no border, no cream paper left in the background. No text, letters, "
          "numbers or anything like writing; no signature or logo. Nobody else in the foreground.")

CLOSE_VIEW = ("16:9, full bleed: the picture runs to all four edges with no margin and no border. Night in Millennium "
              "Park, Chicago, right up against Cloud Gate ('the Bean'), the camera at chest height one or two metres from "
              "it: the polished-steel mirror is so close and so big that it fills the entire picture edge to edge; only "
              "along the top does its upper curve turn away, leaving a thin strip of engraved night sky in the two top "
              "corners. Its outline and its arch are NOT visible: we see only mirror. The mirror reflects the city behind "
              "the camera exactly like M.C. Escher's 'Hand with Reflecting Sphere': an optically correct, smoothly curved "
              "fisheye image with every line crisp. ")

PLATES = {
    # S1 (and E3): close-up mirror, the sensible city
    "plate_close": dict(prompt=CLOSE_VIEW + SANE_CITY + CALM_CENTRE + ENGRAVING),
    # S1 (and E3): the sensible city
    "plate_sane": dict(prompt="16:9, full bleed. " + BEAN_VIEW + SANE_CITY + CALM_CENTRE + ENGRAVING),
    # V3S: the same plate, edited: the reflection shows the impossible city
    "plate_truth": dict(prompt=("Image 1 is a black-and-white wood engraving of the mirror surface of Cloud Gate in "
                                "Chicago at night, seen close up. " + TRUTH_CITY + "16:9, full bleed, no border. No text, "
                                "no letters, no signature.")),
}

SHOULDER = ("The drawing cuts her shoulder off with a straight vertical edge at the lower left: continue that shoulder and "
            "upper arm naturally in the same soft pencil and the same jacket (white, with the orange band round the "
            "sleeve), running out of the bottom-left corner of the picture. Behind her there is only the mirror's "
            "reflection of the city and the plaza, exactly as in image 2: do not add another sculpture, bean shape, "
            "dome or frame behind her. ")

PAINTS = {
    "paint2": ("Image 1 is a pencil drawing of a woman on cream paper. Image 2 is a plate from the film this picture "
               "belongs to: the place where she stands, right in front of the mirror of Cloud Gate ('the Bean') in "
               "Millennium Park, Chicago, at night, drawn as a black-and-white wood engraving in the manner of M.C. "
               "Escher. " + KEEP_HER + HER_COLOURS + PLACE + SHOULDER + LIGHT + STRICT),
    "paint": ("Image 1 is a pencil drawing of a woman on cream paper. Image 2 is a plate from the film this picture belongs "
              "to: the place where she stands, Cloud Gate ('the Bean') in Millennium Park, Chicago, at night, drawn as a "
              "black-and-white wood engraving in the manner of M.C. Escher. " + KEEP_HER + HER_COLOURS + PLACE + LIGHT
              + STRICT),
}

EDITS = {
    "truth": ("Image 1 is a frame from a film: a woman drawn in soft colored pencil stands in front of the mirror surface "
              "of Cloud Gate in Chicago at night, and the world around her is a black-and-white wood engraving. Keep the "
              "woman exactly as she is, every line and colour of her, untouched. " + TRUTH_CITY + "16:9, full bleed, no "
              "border. No text, no letters, no signature."),
}


def run(key, prompt, refs, outdir, n):
    out = []
    for i in range(1, n + 1):
        p = os.path.join(ROOT, outdir, f"{key}_{i}.png")
        k = i
        while any(os.path.exists(os.path.splitext(p)[0] + e) for e in (".png", ".jpg", ".webp")):
            k += 1
            p = os.path.join(ROOT, outdir, f"{key}_{k}.png")
        inp = {"prompt": prompt, "aspect_ratio": "16:9", "image_size": "2K"}
        if refs:
            inp["image_input"] = ["file:" + r for r in refs]
        out += cf.generate(MODEL, inp, p, tag=f"sing_{key}")
    return out


def main(argv):
    a = [x for x in argv if not x.startswith("--")]
    o = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    n = int(o.get("n", 2))
    if not a or a[0] == "list":
        print("plates:", list(PLATES), "paints:", list(PAINTS), "edits:", list(EDITS))
        return
    if a[0] == "plate":
        key = a[1]
        refs = [o["src"]] if o.get("src") else []
        print(run(key, PLATES[key]["prompt"], refs, "media/sing/plates", n))
    elif a[0] == "paint":
        key, plate = a[1], a[2]
        print(run(f"{key}_{os.path.splitext(os.path.basename(plate))[0]}", PAINTS[key], [BASE, plate], "media/sing/first", n))
    elif a[0] == "edit":
        key, src = a[1], a[2]
        print(run(f"{key}_{os.path.splitext(os.path.basename(src))[0]}", EDITS[key], [src], "media/sing/first", n))


if __name__ == "__main__":
    main(sys.argv[1:])
