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

---

# v3 watercolor (2026-10-11, revision pass, stream SING)

Jade's note: "let's use the watercolor version of me for singing, because part of the point … is that the art style
I'm rendered in mismatches the surroundings". All three shots are rebuilt from `inputs/jade_watercolor_jacket_v6.png`
by the method of `../moongazing-public-version/work/singer5/` (base sheet, the place put round her, her own face
pixels put back, Seedance 2.5 avatar takes). Everything is written beside the v2 files with a `v3_` prefix; no v2
file changed. The Bean plates are the v2 plates, untouched. She is not engraved, traced or tinted, and has **no
headphones** (the portrait has none; Jade can ask for them).

## Files for the engine

Each `v3_sync_1080.mp4` is already lip-synced: **file time 0 = the shot's in-point, rate 1, no lag to add.**
1920×1080, 24 fps, no push-in, no baked grain or paper (the engine adds grain).

| Shot | Song in–out | File | Take | Sync baked in | Length |
|---|---|---|---|---|---|
| S1 (+S1b, S2_her) | 12.60–19.64 | `media/sing/S1/v3_sync_1080.mp4` | `v3_take_1` | lag +0.58 s to 14.70, +1.00 s from 16.10; the clip runs 1.3× through the silence between (34 cross-faded frames, 14.70–16.10) | 7.33 s |
| E3 | 119.44–122.95 | `media/sing/E3/v3_sync_1080.mp4` | `v3_take_1` | the open vowel (clip 0.86–3.30) stretched over the whole note (rate 0.74, cross-faded), mouth closes 122.75–122.95 | 3.92 s |
| V3S | 153.98–159.14 | `media/sing/V3S/v3_sync_1080.mp4` | `v3_take_2` | one lag, +0.16 s; untouched frames | 5.54 s |

- **A.js (S1):** `S1_SRC = 'media/sing/S1/v3_sync_1080.mp4'`, `S1_IN = 0` (S1 in 0, S1b in 5.28). `S2_her` uses the
  same file (it is the wide framing; there is no pushed-in variant any more): `in: 7.04, freeze: 0.24`, and its push
  should start at 1.0×, not 1.3×. **Lake Shore headlights for the S2 push: (1615, 702)** in the 1920×1080 frame at the
  end of the shot (1610, 700 at the start; a second pair sits at about 1605, 950). v2's `HEAD = [1600, 690]` still works.
- **D.js / `tools/sections/D/build_timeline.py` (E3, B's):** `E3_TAKE = 'media/sing/E3/v3_sync_1080.mp4'`, clip in 0 at
  119.44 (set `E3_REF_T0 = 119.44` and lag 0). Her matte per frame: `media/sing/E3/v3_sync_1080_matte/`
  (94 PNGs, 1920×1080, L, `fps.txt` 24; BiRefNet on the synced file, so it follows her). First-frame mask in the
  first-frame geometry: `media/sing/first/v3_her_mask_first_frame.png` (2576×1449, same as `v3_S1_first.jpg`).
  The v2 occluder (`media/shots/E3/occluder_mask.*`) and ribbon orbit do not fit: her head is larger and centred at
  about (960, 380), hair down to the bottom of the frame.
- **E.js (V3S):** point the V3S layer at `media/sing/V3S/v3_sync_1080.mp4`, in 0 at 153.98, no variant lag. She
  blinks twice at 157.2–157.5 and 157.7–157.9; the existing cutaway (157.39–157.84) covers most of it.
- Framing (all three, identical figure and scale): portrait rows −30…1030 fill the frame height, face centred;
  face about 32 % of the frame height (v2 raw takes: 32 %; v2 after its 1.3× push: 41 %). Not pushed in, because a
  push cuts off the orange band, the blue dot and the `1420 MHz` patch. A slow engine push of up to 1.08× keeps them.

## How it was made (`tools/sing/wc_*.py`)

1. `wc_base.py` → `first/v3_base16.jpg`: the portrait on a sheet of its own paper in the v2 first-frame geometry.
2. `wc_paint.py` (nano-banana-pro, 2 calls) → `first/v3_paint_wc_{1,2}.jpg`: the plate put round her. Face
   landmarks against the portrait: mean 1.1 / 0.7 px. Picked 2 (arms at her sides); 1 spread her arms to the corners
   like a selfie.
3. `wc_restore.py` → `first/v3_wc_2_r.jpg`: her own face pixels back inside the face oval, with no light taken from
   the plate.
4. `wc_comp.py` → BiRefNet matte of her (`first/v3_her_alpha.png`), refined with a luminance key where the painting
   left white paper behind her hair, then her figure laid over the **exact v2 plates**: `first/v3_S1_first.jpg`
   (= E3's first frame) over `plate_close_1`, `first/v3_V3S_first.jpg` over `plate_truth_1`. One figure, one scale.
5. `wc_takes.py`: Seedance 2.5, 720p, avatar mode, the v2 vocal slices and durations. Takes are
   `media/sing/<SHOT>/v3_take_N.*`.
6. `look.py SHOT v3_take_N` for lag, then `wc_post.py sync|review_sync|matte` (the knots are in `SYNC` there).

| Take | Lag (corr / events) | Verdict |
|---|---|---|
| S1 `v3_take_1` | +0.54 / +0.67, r .51; closures: 'b' +0.58, 'm' about +0.95 | **pick**. The lag drifts, so the sync is piecewise |
| E3 `v3_take_1` | +0.58 / +0.62 | **pick**. Vowel open 2.4 s of the 3.5 s note, so it is stretched to the note |
| E3 `v3_take_2` (prompt: hold, then "Rewind" again) | +0.50 / +0.53 | spare: vowel open only 2.1 s, wider mouth |
| V3S `v3_take_1` | −0.28 / −0.17, r .24 | reject: barely shapes the words, eyes shut about 1.3 s, jacket shading turned cyan |
| V3S `v3_take_2` (prompt: lips shape every word, jacket never cyan) | +0.21 / +0.29; closures +0.16 | **pick** |

## What is weak

- She smiles all the way through (the portrait's smile is where every take starts). It reads warm rather than
  haunted in S1; that is the portrait, not a fault of the take.
- S1 blinks slowly on the first word (13.10–13.35). E3 has a 0.35 s eye-close mid-note (121.2–121.5). V3S opens on a
  blink (153.98–154.1).
- E3's hold is a retime: hair and blink move at 0.74× and those frames are cross-fades. Checked at full size, no
  ghosting; watch it at speed.
- Nobody has watched these with sound: lags are measured from lip closures, not judged by ear.
- The takes soften the engraving a little compared with the first frame (720p model output upscaled to 1080p).

## Cost (tags `revA_sing_*`)

nano-banana-pro 2 × $0.134 = $0.27; Seedance 2.5 720p: S1 8 s $1.85, E3 2 × 5 s $2.31, V3S 2 × 7 s $3.24.
**Total $7.67** of the $30 cap.

---

# v4 glossy hair, no smile (2026-10-11 evening, revision pass v4, instance A)

Jade's notes on the v3 preview: hair "more glossy and natural looking", "try a couple image models", "reduce smiling
magnitude in order to fit the mood of the song", stills first and then animate. S1 and V3S are remade; E3 is not
(B's 2:00 note replaces that shot). Everything is beside the v3 files with a `v4_` prefix; no v3 file changed.

## Files for the engine

Same contract as v3: **file time 0 = the shot's in-point, rate 1, no lag to add**, 1920×1080, 24 fps, clean plate, no
push, grain or grade. Same figure scale, position and bottom cut line as v3 (face height 343.7 vs 341.5 px, eye
midpoint within 2 px on frame 0).

| Shot | Song in–out | File | Take | Sync baked in | Matte (per frame, BiRefNet on the synced file, no grow) |
|---|---|---|---|---|---|
| S1 (+S1b, S2_her) | 12.60–19.64 | `media/sing/S1/v4_sync_1080.mp4` (7.46 s) | `v4_take_1` | one lag, +0.45 s; untouched frames | `media/sing/S1/v4_sync_1080_matte/` (179 PNG) |
| V3S | 153.98–159.14 | `media/sing/V3S/v4_sync_1080.mp4` (5.54 s) | `v4_take_2` | one lag, +0.09 s; untouched frames | `media/sing/V3S/v4_sync_1080_matte/` (133 PNG) |

`render/timeline/A.js` (`S1_SRC`, `A_S1_lyric` matte) and `render/timeline/E.js` (`V3S_SRC`, `V3S_lyric` matte) point at
these. The S1 take's figure reaches the bottom edge on every frame (bottom-row span 478–483 / 1422–1429 px).

## How it was made

1. **Still candidates** (`tools/sing/v4_stills.py`, $2.44): hair and expression edited separately on the top of
   `inputs/jade_watercolor_jacket_v6.png`. Hair: nano-banana-pro, gpt-image-2.5-flare, seedream-5-pro,
   grok-imagine-image-2.0, flux-1-kontext-max. Expression (small closed-lip smile, a trace, neutral, tense):
   nano-banana-pro, gpt-image-2.5-flare, seedream-5-pro. In `media/sing/v4/stills/` with a JSON beside each; sheet
   `contact_sheet_v4A.jpg`. flux-kontext repainted her face without glasses; grok barely changed the hair; the
   "natural" prompt turned the hair brown on all three models; the "tense" faces read tired.
2. **Jade's pick: H2 + F6** = `hair_gloss__gpt_1` + `face_e3_neutral__nbp_1`. `tools/sing/v4_pick.py` (no paid call)
   maps both onto the portrait at 2× by eye/nose landmarks, registers the face layer on the glasses and lays the
   face oval into the hair candidate → `media/sing/v4/stills/pick_H2+F6.png`.
3. **First frames without a repaint** (`tools/sing/v4_first.py`). `wc_paint.py` with the new portrait shrank her to
   0.77× twice (`first/v4_paint_wc_{1,2}.*`, rejected). BiRefNet mattes her cleanly straight off the portrait's own
   paper, so the plate goes behind her by compositing in v3 geometry; only the sleeve ends past the portrait's edges
   come from the v3 figure. → `first/v4_S1_first.jpg`, `first/v4_V3S_first.jpg`, `first/v4_her_mask_first_frame.png`.
4. **Takes** (`WC_VER=v4 tools/sing/wc_takes.py`, Seedance 2.5 720p avatar, same slices as v3; the prompt now says she
   never smiles and sings tense and determined):

| Take | Lag (corr / closures) | Verdict |
|---|---|---|
| S1 `v4_take_1` | +0.49 / +0.47, +0.41 | **pick**; blink at about 16.2 (on the cutaway) |
| S1 `v4_take_2` | +0.39 / +0.39, +0.66 | spare: lag drifts, eyes closed at 12.9 |
| V3S `v4_take_1` | −0.20 / −0.08, −0.32 | spare: no blinks, but the mouth runs at about 0.9× |
| V3S `v4_take_2` | +0.13 / +0.04, +0.06 (r .68) | **pick**; eyes closed for the first 6 frames, blink on "my" |

5. `WC_VER=v4 wc_post.py sync|matte|review_sync` (`SYNC_V4`).

## What is weak

- V3S opens with her eyes closed for 0.25 s, then she opens them and sings.
- Lags are measured from lip closures; nobody has judged them by ear.
- The gpt-image hair is about 1.05 px per portrait px, upscaled 1.3× in the first frame. The takes are 720p, so it
  does not show there.

## Cost (tags `v4A_*`)

Stills $2.44 (18 images), rejected repaint $0.27, Seedance 2.5 720p 2 × 8 s + 2 × 7 s = $6.94. **Total $9.64** of the
$50 soft limit.

### v4 follow-up: S1 blink removed (B's wide Bean opening)

With S1 now opening wide (B, `docs/revisions/v4/plans/bean.md`), the take's blink at file frames 8-13 (song 12.93-13.14)
read as her looking down. `tools/sing/v4_noblink.py` lays the open eyes of frame 7 over frames 8-15 (similarity fit on
nose, brow and face-side landmarks, feathered eye mask, last two frames blend back) → `media/sing/S1/v4_sync_1080_open.mp4`,
same frames otherwise, so the sync and matte are unchanged (`v4_sync_1080_open_matte` links to `v4_sync_1080_matte`).
`render/timeline/A.js` `S1_SRC` uses it; `v4_sync_1080.mp4` is kept.

---

# v5 Jade's photos (2026-10-16, v9 pass)

Jade: "I've added 2 new images to /inputs. can you reshoot the 2 lip sync clips using these 2 new photos? the one with the
pencils should go in the first singing slot, and the one with long hair styled down should be the second." S1 =
`inputs/jade_ref_image2_music_video_pencils.png` (hair up, two pencils, pale-blue + pink erasers: film canon); V3S =
`inputs/jade_ref_image_music_video_long_hair.png`. She is her own photo now: photographic, not watercolor, no repaint.
E3 not touched. Everything is beside the v4 files with a `v5_` prefix; no v4 or earlier file changed. Full report:
`docs/revisions/v9/sing_v5.md`.

## Files for the engine

Same contract as v3/v4: **file time 0 = the shot's in-point, rate 1, no lag to add**, 1920x1080, 24 fps, no grain, push or
grade; per-frame matte dir with `fps.txt` (24).

| Shot | Song in-out | File | Take | Sync baked in | Matte |
|---|---|---|---|---|---|
| S1 | 12.60-19.64 | `media/sing/S1/v5_sync_1080_open.mp4` (7.46 s; plain: `v5_sync_1080.mp4`) | `v5_take_2` | one lag, +0.46 s; file frames 0-4 (12.60-12.72) eyes from frame 6 (`v4_noblink.py`) | `v5_sync_1080_open_matte/` -> `v5_sync_1080_matte/` (179 PNG; BiRefNet + pencils keyed back by `v5_pencils.py`; BiRefNet originals in `v5_sync_1080_matte_birefnet/`) |
| V3S | 153.98-159.14 | `media/sing/V3S/v5_sync_1080.mp4` (5.54 s) | `v5_take_1` | +0.05 to 155.60, 1.24x through the silence 155.60-156.60 (24 cross-faded frames), +0.29 from 156.60 | `v5_sync_1080_matte/` (133 PNG, BiRefNet) |

`render/timeline/A.js` (`S1_SRC`, so `S1_MATTE`) and `render/timeline/E.js` (`V3S_SRC`, `V3S_lyric` HER) point at these;
the v4 paths are in comments.

## First frames (`tools/sing/v5_first.py`, no paid call)

BiRefNet on each photo (`WC_VER=v5S1|v5V3S wc_comp.py matte`), edge colours decontaminated from the photo's own background
(F = (I - (1-a)B)/a), laid over the exact plates in the v4 crop (2576x1449). Out: `first/v5_S1_first.jpg`,
`first/v5_V3S_first.jpg`, `first/v5_her_mask_first_frame_{S1,V3S}.png`; sheet `review/v5_first_vs_v4.jpg`.

| | v4 | v5 S1 | v5 V3S |
|---|---|---|---|
| face height / frame height | 0.325 | **0.408** | **0.348** |
| eye midpoint (1080p) | (941, 403) | (941, 463) | (941, 429) |

Why not v4's size: at v4's face size the pencils photo ends 273 crop px (19 % of the frame) above the bottom edge and the
long-hair photo 100 px above it with its jacket cut by both photo edges. Least-bad choices, taken:
- **S1:** scale 1.24x v4's face, eyes 60 px (1080p) lower; the photo then ends 32 photo px short of the bottom: that strip
  is the photo's own jacket colours carried down (orange left out), the only invented pixels. The lower-left forearm edge
  is the photo border (straight). Pencils keep 75-110 px of headroom.
- **V3S:** scale 1.10x, eyes 26 px lower, so the whole 1420 MHz patch stays in frame. Left arm edge = photo border, trimmed
  to a rounded shoulder and a slight taper (trim only). Right: the patch is cut by the photo edge, so its missing third is
  taken from the same patch in the pencils photo (affine fit ellipse-to-ellipse + NCC refine, NCC 0.82), and the sleeve
  runs 45 photo px past the edge in plain fabric colour. Crown: the blue painting seen between hair strands keyed out.

## Takes (`WC_VER=v5 wc_takes.py`, Seedance 2.5 720p avatar, v4 slices and durations; tag `v5_sing_*`)

New prompt (`P5`): "the woman stays photographic and real; the world stays black ink engraving; the two never blend",
per-shot hair (S1 bun + two pencils, pale-blue + pink erasers, unchanged; V3S long dark hair down), v4 acting (no smile,
tense, determined, eyes open, head keeps its angle, locked-off, patch sharp, no headphones).

| Take | Frame | Lag (corr / events; 2 s windows) | Verdict |
|---|---|---|---|
| S1 `v5_take_1` | 16:9 1280x720 | +0.89 / +0.89 (open 1.08, b 0.89, m 0.61); windows -0.15..+1.35, r .34 | spare: mouth does not follow the voice steadily; no blink in shot |
| S1 `v5_take_2` | 16:9 1280x720 | +0.60 / +0.50 (open 0.45, b 0.55); windows 13.0-15.0 +0.30..+0.53, r .5-.85 | **pick**; eyes closing at 12.60-12.67 (patched); squint at 19.9 (after the cut) |
| V3S `v5_take_1` | 16:9 1280x720 | +0.25 / +0.28 (b 0.00, m 0.19); windows +0.03 then +0.29/+0.30 from 155.5, r .68 (.76-.96) | **pick**, piecewise; blinks 154.15-154.35, 157.06-157.23 |
| V3S `v5_take_2` | 16:9 1280x720 | +0.46 / +0.45; windows -0.18..+1.14, r .38 | spare: unsteady; blinks 154.32, 155.11, 157.07 |

All four: framing locked, face size as the first frame (S1 280-308 px, V3S 241-267 px at 720p), photographic, glasses on,
pencils and erasers intact in both S1 takes, patch readable.

## What is weak

- Lags are measured (mouth vs vocal level, lip closures, windows), not judged by ear.
- V3S: right shoulder is squared with a straight outer edge (the sleeve extension; Seedance kept it). Visible at preview size.
- V3S blinks at 154.15-154.35 (just after the cut-in) and 157.06-157.23 (on "my", before the cutaway at 157.39).
- S1: faint closed-mouth smile (the photo's) in the wide, 12.60-13.20, before she sings; the bottom 30 px (1080p) of
  jacket are carried-down colour with faint vertical marks; lower-left jacket edge is a straight vertical.
- Both are bigger than v4 (S1 face 41 % vs 32.5 %), so she is bigger in the Bean wide opening too.
- V3S crown: a warm patch where the photo's wooden picture frame shows through her hair (reads as a highlight).

## Cost

Seedance 2.5 720p: S1 2 x 8 s $3.70, V3S 2 x 7 s $3.24. **Total $6.94** of the $20 cap (project $273.06 of $400).

## Rebuild

```
EPY=tools/engrave/.venv/bin/python; MPY=~/Documents/1-music-shipped/orbital-sunrise-video/video/out/.venv/bin/python
PY=~/Documents/1-music-shipped/moongazing/.venv/bin/python
export FFMPEG=~/Documents/1-music-shipped/moongazing/.venv/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2
export FACE_LANDMARKER=~/Documents/1-music-shipped/moongazing/tools/sync/models/face_landmarker.task
WC_VER=v5S1 $EPY tools/sing/wc_comp.py matte inputs/jade_ref_image2_music_video_pencils.png
WC_VER=v5V3S $EPY tools/sing/wc_comp.py matte inputs/jade_ref_image_music_video_long_hair.png
$MPY tools/sing/v5_first.py comp; $MPY tools/sing/v5_first.py sheet
WC_VER=v5 $PY tools/sing/wc_takes.py submit S1 V3S --n=2; WC_VER=v5 $PY tools/sing/wc_takes.py wait S1 V3S
$MPY tools/sing/look.py S1 v5_take_2; $MPY tools/sing/look.py V3S v5_take_1        (knots: SYNC_V5 in wc_post.py)
WC_VER=v5 $PY tools/sing/wc_post.py sync S1; WC_VER=v5 $PY tools/sing/wc_post.py sync V3S
WC_VER=v5 $EPY tools/sing/wc_post.py matte S1 v5_sync_1080; WC_VER=v5 $EPY tools/sing/wc_post.py matte V3S v5_sync_1080
$MPY tools/sing/v4_noblink.py media/sing/S1/v5_sync_1080.mp4 media/sing/S1/v5_sync_1080_open.mp4 6 0 4 --fade=2
$EPY tools/sing/v5_pencils.py media/sing/S1/v5_sync_1080_open.mp4 media/sing/S1/v5_sync_1080_matte
WC_VER=v5 $PY tools/sing/wc_post.py review_sync S1 media/sing/review/v5_S1_sync_review.mp4 --audio=media/sfx/Rewind_cinematic_sfx_mix_v5coda.mp3
```

## v5 follow-ups (same day; details in `docs/revisions/v9/sing_v5.md` "Follow-ups")

**Engine now:**
- S1 = `media/sing/S1/v5c_sync_1080.mp4`: re-tinted photo `media/sing/tint/local_a.png` (`v5_first.py V5_REV=c`), take
  `v5c_take_2`, lag +0.15 (measured +0.10), first frame held 12.60-12.75, matte `v5c_sync_1080_matte/` with the pencils
  keyed in.
- V3S = `media/sing/V3S/v5b_sync_1080_open.mp4`: shoulder retake, take `v5b_take_2` (take 1 was 21:9, rejected), lag
  -0.05, eyes at 153.98-154.48 opened, matte `v5b_sync_1080_open_matte/`.

**Fallbacks:**
- S1, the old take re-synced to +0.61: `v5_sync_1080_l061_open.mp4`.
- Ear tests, old take: `review/v5_S1_lag+0.61/0.76/0.91_*`.
- Ear tests, new take: `review/v5c_S1_lag+0.00/0.15/0.30_*`.

**Pending Jade's look:**
- V3S first frame `media/sing/first/v5d_V3S_first.jpg`, outpainted by nano-banana-pro (`tools/sing/v5_outpaint.py`).
- It removes the couch upholstery that v5/v5b mistook for her shoulder (source x ~930-1086, y ~850-1050, above the
  epaulet), and completes both arms and the patch. Only pixels beyond the photo's edges come from the model.
- No take yet. The next step would be `WC_VER=v5d`.

**Spend:** `v5_sing_*` total $14.21 of the $20 cap.

| Tag | Spend |
|---|---|
| S1 | $3.70 |
| V3S | $3.24 |
| V3S_r2 | $3.24 |
| S1_tint | $3.70 |
| V3S_outpaint | $0.33 |

**V3S v5d (wired, supersedes v5b):**
- File: `media/sing/V3S/v5d_sync_1080_open.mp4` and its matte `v5d_sync_1080_open_matte/`.
- Take `v5d_take_2` (take 1 rejected: unsteady), measured lag +0.15, wired as measured.
- The lid droop at 154.35-154.56 is replaced by the open eyes of file frame 8; the full blink at 156.10-156.35 is kept.
- Ear test: `review/v5d_V3S_lag+0.00/0.15/0.30/0.45_*`.
- Jade's v5b half-blink was the take's own, on "my", 157.08-157.38 (f3770-f3777).
- Spend now $17.45 of the $20 cap (tag `v5_sing_V3S_r3`, $3.24).
