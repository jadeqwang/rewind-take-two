#!/usr/bin/env python
"""v10b F4: paint Jade's FRONT as the Bean's mirror sees it (one nano-banana-pro call per variant, ~$0.134 each).
She dives head-first with her back to the camera and her back arched (head thrown back, face toward the camera), so the
mirror in front of and below her sees her jacket front, mock-neck crop top and throat, with her face turned away
(docs/revisions/v10/f4_reflection.md). The pose comes from the three.js check: an orthographic view of the arched
mannequin along the mirror's view direction (tools/sectionF/f4_threejs/refmap.mjs --ref), turned upright here
because image models draw upright figures more reliably; the result is turned back head-down for the comp.
Refs: that pose (upright), the outfit sheet, her F4 frame 40 (style, headphones, hair).

    ~/Documents/1-music-shipped/moongazing/.venv/bin/python tools/sectionF/f4_front_gen.py [--pose front2|front3] [--n 3] [--k0 1] [--dry-run]
front2: arched, head thrown back (media/shots/F4/v10_front/front_<k>, tag v10b_f4front).
front3 (Jade's variant): back barely arched, head in line with the spine, so the mirror sees her FACE
(media/shots/F4/v10_front3/front3_<k>, tag v10c_f4front3). Written upright as generated.
"""
import argparse
import concurrent.futures as cfut
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
import cf  # noqa: E402

OUT = os.path.join(ROOT, "media/shots/F4/v10_front")
POSE = "media/shots/F4/v10_front/pose_ref_upright.png"
STYLE = "media/shots/F4/v10_back/ref_pose_f40.png"

POSE3 = ("standing straight and calm, seen from the front and a little from below; her head is level with her body and "
         "tipped very slightly forward, her face toward us, eyes gently closed, a calm expression; both arms stretched "
         "straight out to the sides and angled slightly down, hands open; legs straight and pressed together, feet together.")
POSE2 = ("standing straight, seen from the front and a little from below; her head is tipped far back, so her face is "
         "turned up and away from us and we see the underside of her chin, her throat and the top edge of her hair, not "
         "her eyes; both arms stretched straight out to the sides and angled slightly down, hands open; legs straight and "
         "pressed together, feet together.")
PROMPT = (
    "Draw the girl from the second image (the outfit sheet, FRONT view) in EXACTLY the pose, proportions and framing of "
    "the simple colored mannequin in the first image (ignore the mannequin's colors; it only gives the pose). Pose: "
    "{pose} Outfit, seen from the FRONT: white cropped bomber jacket worn open, with a stand-up collar "
    "with snaps, orange bands across the chest and round both sleeves, a small pale-blue dot patch on her left chest, "
    "and the round black-and-white '1420 MHz' patch on her LEFT sleeve (on the right side of the picture, as in the "
    "outfit sheet's FRONT view); a black mock-neck crop top under the open jacket, bare midriff; navy wide cargo pants "
    "with orange straps hanging at the sides; chunky white sneakers seen from the front; orange headphones around her "
    "neck. Her long loose black hair falls down behind her shoulders and back, visible beside her neck and shoulders. "
    "She holds a small yellow pencil in her right hand (on the left side of the picture). Same hand-drawn look as the "
    "third image: clean anime cel shading with black ink outlines and light colored-pencil hatching. Plain flat white "
    "background, nothing else: no city, no sculpture, no reflection, no shadow, no text. One girl, exactly two arms and "
    "two legs, the whole figure inside the picture with a white margin all round.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pose", choices=["front2", "front3"], default="front2")
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--k0", type=int, default=1)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    f3 = a.pose == "front3"
    pose = POSE.replace("v10_front/", "v10_front3/") if f3 else POSE
    out = OUT.replace("v10_front", "v10_front3") if f3 else OUT
    inp = {"prompt": PROMPT.replace("{pose}", POSE3 if f3 else POSE2), "aspect_ratio": "1:1", "image_size": "2K",
           "output_format": "png", "image_input": ["file:" + pose, "file:inputs/jade_in_outfit.png", "file:" + STYLE]}

    def one(k):
        return cf.generate("google/nano-banana-pro", inp, os.path.join(out, f"{'front3' if f3 else 'front'}_{k}.png"),
                           tag="v10c_f4front3" if f3 else "v10b_f4front", dry_run=a.dry_run)
    with cfut.ThreadPoolExecutor(a.n) as ex:
        for r in ex.map(one, range(a.k0, a.k0 + a.n)):
            print(r)


if __name__ == "__main__":
    main()
