# Singing Jade at the Bean: S1, E3, V3S (2026-10-11)

Three shots with the same framing, made by the Orbital Sunrise method (`docs/recon/pipeline.md` §2–3). Media is
gitignored; scripts are in `tools/sing/` (committed). Times are song seconds (`analysis/cinematic/timing.json`).

## Picks (play these)

| Shot | Song in–out | Take | Lip lag B | Clip in–out at B | Review composite (A/B/C) |
|---|---|---|---|---|---|
| S1 "The night before my dissertation defense," | 12.60–19.64 | `S1/take_1_lips.mp4` (raw: `take_1.mp4`) | **+1.04 s** | 0.74–7.78 | `review/S1_take_1_lips_ABC.mp4` |
| E3 held "Rewind." | 119.44–122.95 | `E3/take_3_lips.mp4` (raw: `take_3.mp4`) | **+0.75 s** | 1.05–4.56 | `review/E3_take_3_lips_ABC.mp4` |
| V3S "The night before my dissertation defense," | 153.98–159.14 | `V3S/take_2_lips.mp4` (raw: `take_2.mp4`) | **−0.12 s** | 0.18–5.34 | `review/V3S_take_2_lips_ABC.mp4` |

Rule: `clip_time = song_time − ref_t0 + lag` (ref_t0 = where the vocal slice starts: S1 12.90, E3 119.14, V3S 153.68).
A = lips 0.15 s earlier (lag + 0.15), C = lips 0.15 s later (lag − 0.15). No variant needs a held frame
(`review/*_ABC.json`). Single full-frame variants: `review/<SHOT>_<take>_{A,B,C}.mp4` (720p, song mix under it).
Jade picks by ear; the "B" lags are my measurement. The `_lips` versions are the same frames with the lip colour
pass described below; `review/*_take_N_ABC.mp4` without `_lips` are the untouched takes.

All takes are 1280×720, 24 fps, chest-up and centred, with the face the same size as the first frame (face height
228 px in the first frame vs about 234 px in the takes). The engine should add only a light style pass on top (MGP
`OS_STYLE`; a heavy one breaks her glasses into dashes).

## Polish pass (06:20–06:30 CDT, rough-cut review v1, top-10 item 5); no new generation, $0

`tools/sing/polish.py`; every frame is still the approved take's own frame, so likeness and lip sync are unchanged
(same frame count, fps and duration). The files the timelines reference were rewritten **in place**; backups sit
next to them as `*_orig.mp4` (1280×720, as before):

| File (in place, now 1920×1080) | Push-in 1.3× | Headphones → #F08A24 | Grain + paper baked |
|---|---|---|---|
| `S1/take_1_lips.mp4` | yes | yes | yes (E3's: grain .045 at 1.2 px on twos, paper .18) |
| `E3/take_3_lips.mp4` | yes | yes | no: Section D's fx already adds it (it would double) |
| `V3S/take_2_lips.mp4` | yes | yes | yes |
| `S1/take_1_lips_wide.mp4` (new) | **no** (old framing) | yes | yes |

- **Push-in:** a fixed window x 113–1098, y 20–574 of the 720p take (985×554 = 1.3×), Lanczos to 1080p, the same
  for all three shots, so they still rhyme. The sleeve running to the lower-left corner and the lower orange band
  are cropped off; her shoulder still shows at the lower left. She stays centred; the mouth sits at about 70 % of
  the frame height, with the jaw well inside the frame.
- **Headphones:** keyed once on frame 0 inside a box under the lips and outside the face oval (the cups, cheek
  blush, lips, hair and warm paper all share one hue, so the key needs the box). The mask is carried on a jaw/chin
  landmark fit, and the colour comes from the jacket band (same hue, colored-pencil saturation, pixel's own value).
  Checked at four points in each clip: no leaks, and the mask tracks the head movement.
- **Lip offsets unchanged** (the in-points are clip times; the files have the same timing): S1 +1.04, E3 +0.75,
  V3S −0.12. The `review/*_lips_ABC.mp4` composites were rebuilt from the new files.
- **Section A, S2:** `S2_her` pushes 4.5× into `HEAD = [1600, 690]`, which is in the old framing. In the
  pushed-in file the headlights sit at about x 1860, against the frame edge. Point `S2_her` at
  `media/sing/S1/take_1_lips_wide.mp4` (same timing, old framing, orange headphones, grain), or move HEAD.
- **Section D, E3:** its cached occluder `media/shots/E3/occluder_mask.{png,mp4}` was remapped to the new framing
  (backups `occluder_mask_orig.*`); checked over a take frame. If D ever rebuilds it from
  `first/her_mask_first_frame.png` (old framing, unchanged), run
  `polish.py remap-mask` on it, or its hard-coded blob cut will land on her hair. The ribbon orbit (CX 900) was
  tuned to her old head size: with the bigger head the left side of the orbit now passes behind her hair.
- Note for Jade: her real headphones are pale dusty pink (handbook); this follows the film's canon orange on the
  review's request. The pink versions are the `_orig` files.

## What was made

1. **Base:** `first/base16.jpg`, her approved trace `jade_trace_jacket_hp_2.jpg` (orbital-sunrise-video), whole,
   centred, frame height = trace height (`tools/sing/base.py`, the same geometry as MGP's base16).
2. **Plates** (nano-banana-pro, `tools/sing/paint.py`): `plates/plate_close_1.jpg` is the close-up Bean mirror at night
   as an Escher wood engraving. It shows the sensible city, a rooftop at lower left with a square stairwell (the
   closed-loop staircase, small), and Lake Shore Drive with tiny headlights at right. `plates/plate_truth_1.jpg` is an
   edit of the same plate with only the reflection changed: Penrose stairs looping round elevated train tracks, a
   self-feeding waterfall, towers joined impossibly, and orange/pale-blue colored-pencil blooms in the sky. `*_crop.jpg`
   are the same plates in the first frames' crop geometry, for the engine (S2 push-in, E3 ribbons).
   Rejected: `plate_sane_*` (whole Bean small in frame: she read as a giant cutout), `plate_close_2` (margin),
   `plate_truth_2` (a bubble inside the Bean).
3. **Her, painted in:** `paint2_plate_close_1_1.jpg`. The model painted the place round the kept trace with plate
   image 2 as reference, tinted her in light colored pencil, and continued the shoulder that the trace cuts off at
   lower left. Face landmarks are within mean 1.1 / max 3.3 px of the trace. Rejected: the first paints (a second
   bean behind her head) and paint2 #2 (a pale halo round her).
4. **Her lines back:** `restore.py` (MGP's, 40 % face, 85 % lips) gives `S1_r.jpg`. Then `deshadow.py still
   --tint=1.8` (MGP's tool, her pick) gives `S1_full.jpg`. Then `comp.py unborder`, a plain centred 16:9 crop
   (2576×1449, box in `first/crop.json`) that removes the model's cream margin and black rule line without
   rescaling her, gives **`first/S1_first.jpg`**.
5. **E3 first frame = S1 first frame** (`E3_first.jpg`, byte-identical), so the rhyme is exact and the frame stays
   clean for the engine's ribbons. Her matte for the engine is `first/her_mask_first_frame.png`; it matches the
   first frame only, since takes move.
6. **V3S first frame:** her figure from `S1_full.jpg` (pixel-identical, same place and scale; the silhouette comes
   from the trace plus the painted shoulder, `her_mask_ext.png`) laid over `plate_truth_1` (`comp.py comp
   --grow=0 --feather=3`), then the same crop, giving **`first/V3S_first.jpg`**. No face from anywhere else.
7. **Vocal slices** (`audio/`, from `vocals_bs_roformer_48k.wav`): S1 12.90 + 8 s; V3S 153.68 + 7 s (silent
   gap); E3 119.14 + 5 s with **119.14–119.38 muted**, because the last "stop" chop sits in the only 0.3 s before
   "Rewind." (119.44).
8. **Takes:** Seedance 2.5, 720p, 16:9, `reference_audios` = slice, `generate_audio:false`, `use_virtual_avatar:true`,
   prompt from MGP round 2 (smooth forehead, head keeps the angle, locked-off camera) (`tools/sing/takes.py`).
9. **Lag:** `look.py` combines the correlation of mouth opening vs vocal level with event lags (lip closures on
   'b' of before and 'm' of my, the phrase opening, the phrase end). It writes `take_N.look.json`, `_look.jpg` and
   `_win.jpg` (face strip at the measured lag).

## All takes

| Take | Result | Lag (corr / events) | Verdict |
|---|---|---|---|
| S1 take_1 | 16:9 | +1.10 / +1.04 (0.91–1.23), r .58 | **pick** |
| S1 take_2 | 16:9 | +0.94 / +0.97, r .50 | alternate, nearly identical |
| S1 take_3 | 16:9 | −0.19 / −0.03 (−0.45…+0.07), r .25 | reject: weak, inconsistent mouth |
| E3 take_1 | 16:9 | +1.08 / +0.83 | alternate: vowel narrows about 0.4 s before the note ends |
| E3 take_2 | 16:9 | +0.66 / +0.58 | reject: barely opens; a hair strand sprouts in the last second |
| E3 take_3 (prompt: vowel held to the end) | 16:9 | +1.08 / +0.83; B set to 0.75 from mouth open 1.0 s / reopen 4.7 s | **pick**: widest, longest held vowel |
| V3S take_1 | **21:9 1470×630** | +0.05 / −0.05 | reject: reframed |
| V3S take_2 | 16:9 | −0.09 / −0.12, r .64 | **pick** |
| V3S take_3 | **21:9** | +0.12 / +0.14 | reject: reframed |
| V3S take_4 | **4:3 1112×834** | +0.34 / +0.36, r .66 | reject: reframed, framing no longer rhymes |

Contact sheets per shot: `review/S1_contact.jpg`, `review/E3_contact.jpg`, `review/V3S_contact.jpg` (picks
marked); plates and first frames: `review/plates_and_first_frames.jpg`.

## Cost (list-price estimates, tags `sing_*` in `media/genlog.jsonl`)

| Item | Calls | USD |
|---|---|---|
| nano-banana-pro 2K (plates, paints, edits) | 12 (+1 HTTP 500, not billed) | 1.61 |
| Seedance 2.5 720p (S1 3×8 s, E3 3×5 s, V3S 4×7 s) | 10 | 15.49 |
| **Total** | | **17.10** (budget 35) |

Local passes (restore, deshadow, composite, lip colour, variants) cost nothing.

## Quality concerns (for Jade)

- **Lips:** the trace's lips are graphite grey. Next to the 1.8-tinted skin they read cold blue-grey, a little in
  the first frame and clearly in the takes. `tools/sing/liptint.py` (no paid call) warms them to a muted rose at the
  same lightness, tracked per frame, with teeth and mouth interior left alone. The `_lips` takes have it, and the
  raw takes are kept. Her call; she has not seen it.
- **V3S reframing:** Seedance reframed 3 of 4 V3S takes (21:9, 21:9, 4:3), but none of the 6 S1/E3 takes. Probably
  the brighter, busier truth reflection. Only take_2 rhymes with S1. It has brief forehead creases (a brow raise)
  around 157.4–157.8 s; at that moment she is mid "my dissertation".
- **E3 opening:** at the in-point (119.44) her mouth is already open, because the take opens on the vowel at clip
  1.0 s. The cut lands on the word, so this should read fine; it closes about 0.4 s before 122.95 at lag B
  (lag A keeps it open longer).
- **Hidden details:** the Penrose rooftop staircase in S1 is a small square stairwell on the lower-left roof. It
  reads as a loop only if you look for it. The engine could sharpen it if wanted. The headlights on Lake Shore Drive
  are in the reflection at right and move a little in the takes.
- **Composite seam (V3S):** a few of S1's sky hatch lines sit just above her hair, inside the matte. They are hard
  to see at 720p.
- **Selfie shoulder:** the trace is a selfie pose, so her shoulder runs out at lower left (painted on). OS asked for
  "no selfie arm"; MGP used the same pose and it was approved.
- Takes are 720p, to be upscaled to 1080p in the film.

## Rebuild

```
PY=~/Documents/moongazing/.venv/bin/python; MPY=~/Documents/orbital-sunrise-video/video/out/.venv/bin/python
$PY tools/sing/base.py
$PY tools/sing/paint.py plate plate_close --n=2
$PY tools/sing/paint.py paint paint2 media/sing/plates/plate_close_1.jpg --n=2
$PY tools/sing/paint.py plate plate_truth --src=media/sing/plates/plate_close_1.jpg --n=2
$MPY tools/sing/restore.py media/sing/first/paint2_plate_close_1_1.jpg media/sing/first/S1_r.jpg --face=0.4 --lips=0.85
$MPY tools/sing/comp.py mask; $MPY tools/sing/comp.py extend media/sing/first/paint2_plate_close_1_1.jpg media/sing/plates/plate_close_1.jpg
$MPY tools/sing/deshadow.py still media/sing/first/S1_r.jpg media/sing/first/S1_full.jpg --tint=1.8
$MPY tools/sing/comp.py unborder media/sing/first/S1_full.jpg media/sing/first/S1_first.jpg
$MPY tools/sing/comp.py comp media/sing/first/S1_full.jpg media/sing/plates/plate_truth_1.jpg media/sing/first/V3S_full.jpg --grow=0 --feather=3
$MPY tools/sing/comp.py unborder media/sing/first/V3S_full.jpg media/sing/first/V3S_first.jpg
$PY tools/sing/takes.py audio; $PY tools/sing/takes.py submit S1 --n=2; $PY tools/sing/takes.py wait
$MPY tools/sing/look.py S1 take_1; $MPY tools/sing/liptint.py take S1 take_1
$PY tools/sing/variants.py S1 take_1_lips 1.04
```
