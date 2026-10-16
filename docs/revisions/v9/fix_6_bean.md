# v9 fix 6: F4 Bean reflection (3:00.0-3:02.8)

Status: done. Waiting for the lead's integrated render.

## What was wrong (checked frame by frame on the source clip)
F4 is `media/shots/F4/take_2_engraved_dered.mp4` (`F_edl.json`, 180.02-183.56, rate 1.3, so source frames 0-110).
- **The reflection didn't match her.** It had no headphones, no pale-blue chest dot, legs apart in a V (hers are
  together), and it was about 0.4 of her size. From source frame ~64 (f4370) it rose under her. Its grey arms then
  spread just under her white arms (the "four-armed" read), and by ~86-96 its face had slid up and merged into hers.
- **The sleeve roundel was garbled** in every frame up to ~105 ("1420"-ish scribble, e.g. "88 / 5b").
- Jade was right about the reviewer's note: the shot shows her front (face, chest dot) from above. A reflection that
  shows the same costume details is what she asked for, so I kept the front and did not swap it for her back.

## What I made
Paint/composite, no regeneration. The new reflection is built from the falling Jade's own pixels, so the headphones,
chest dot, legs-together pose, pencil hand and re-lettered roundel all match her by construction.
1. **Roundel:** `tools/sectionE/patchfix.py take_2_engraved_dered.mp4 take_2_engraved_dered_patch.mp4 --init 1080,465,1 --from 0 --to 120 --guess -10 --thr 75`.
   It tracked frames 0-105 (106-110 have no ring: she's sinking and the model's own lettering there already reads "1420 MHz").
2. **Reflection:** new script `tools/sectionF/f4_reflection.py` (docstring has the details). Per frame it:
   - builds her matte (BiRefNet plus a flow-carried silhouette from frame 54) and clips it to her head outline;
   - removes the old reflection. Frames 0-79 use clean plates: Bria `fibo-edit-1.5` masked erases on 21 keyframes,
     carried between keyframes by a homography of the Bean. Frames 80+ use a fill along the ripple rings;
   - draws the new reflection: her cutout flipped about the mirror surface (heads meet, text mirror-reversed). It is
     shrunk by a convex-mirror magnification that grows to 1 at contact (~frame 78), compressed toward the feet, a
     touch cooler and darker, and clipped to the Bean. It starts to ripple from frame 70 and fades out over 72-80 as
     the mirror turns to liquid.
   Plates are in `media/shots/F4/v9_plates*/` (`v9_plates2/chosen.json` lists the 21 used). Mask caches are in
   `media/shots/F4/v9_work/`.
   - **Output:** `media/shots/F4/take_2_engraved_dered_v9refl.mp4` (1920x1080, 24 fps, 121 frames, CRF 12, same timing as the original).

Evidence (source frames, labelled with their master frame):
- `fix_6_bean_before_after.jpg`: v8 on top, v9 below, across the shot.
- `fix_6_bean_detail.jpg`: source frames 40 and 60, before and after. The reflection now has the headphones, chest
  dot and legs together.
- `fix_6_bean_roundel.jpg`: the roundel, before and after.

## Spend
$1.62: 54 Bria `fibo-edit-1.5` calls at $0.03, tag `v9_6`, including retries for plates that added trees, coins or
legs. The project total is now $261.56 of $400 (that figure includes other agents' spend).

## Exact EDL change (the lead applies it; I didn't edit `F_edl.json` or `edl.py`)
In `media/shots/F_edl.json`, F4 shot:
```diff
-  "file": "media/shots/F4/take_2_engraved_dered.mp4",
+  "file": "media/shots/F4/take_2_engraved_dered_v9refl.mp4",
```
No other changes: in, out, clip_in, rate, fx and text stay the same. To make it survive an `edl.py` rebuild, set
`"F4": dict(take=2, file=S + "F4/take_2_engraved_dered_v9refl.mp4", ...)` in `tools/sectionF/edl.py` CHOSEN. Its
`_dered` lookup only adds a suffix when that file exists, and `..._v9refl_dered.mp4` doesn't. `matte_file` is
informational only, so it needs no change.

## What still looks wrong
- **Frames 74-80 (f4378-4382):** the fading reflection reads briefly as a translucent, rippled ghost of her standing
  in the rings. It's intended (the mirror goes liquid), but it is a dissolve, not a physical splash.
- **Frames 80-92 (f4382-4391):** right under her chin there's a soft dark "dent" where the old reflection's face was
  painted out. A faint brownish trace of that face remains at about 86-92. These frames are mostly under the ripple
  swirl and the 0.9 white flash comes right after.
- **Faint seams:** where she meets the Bean (her hair tips, the chin line around frames 40-60) there are slight seams
  and grey smudges. Plate fills drift by a pixel or two between keyframes. These are only visible when frame-stepping.
- **Scale at contact:** the reflection is life-size at contact, so its legs reach the bottom of the frame in 72-76.
  That's what a flat-ish mirror gives, but it is bigger than the old model reflection.
- **Roundel at 106-110:** the ring is gone (the model's own drawing) and the text "1420 MHz" floats on the sleeve,
  under the end flash.
- **Not checked yet:** the 1.0-1.1 zoom fx and the "never stop" text that the engine adds. Check them in the lead's preview.
