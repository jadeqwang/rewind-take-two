# Singing shots v9w: warm watercolour, animated with v8's acting (TEST), 2026-10-18

Jade: "i like warm watercolour warm light. can you animate those and let me see the lip sync on those with v8's acting
directions".

Source stills (by the style agent, `media/sing/style/v8/README.md`):
- S1: `glow_S1__nbp_1__fixx2.png`;
- V3S: `glow_V3S__nbp_1__fixx2__ext.png`.

**Status: test only, not wired.**
- A.js and E.js still point at v7. They were swapped to v9w for the two preview renders only, and restored and checked
  with `diff`.
- Nothing is committed.
- Frame numbers are song frames (song s x 24) unless they say "take frame".

## Files for Jade

| What | File |
|---|---|
| Review page, section "Singing v9w (warm watercolour)" at the top, ear tests first | `deliverables/wip/sing_review.html` |
| S1 lip-sync clips: painted figure over the plate, song under it, eye fixes in | `media/sing/review/v9w_S1_lag+{0.40..1.30}_measured*.mp4` (7) |
| V3S lip-sync clips | `media/sing/review/v9w_V3S_lag+{0.00,0.15,0.30,0.45}_measured*.mp4` |
| Previews (960x540) | `deliverables/wip/sing_v9w_{S1,V3S}_preview.mp4` |
| Three panels: watercolour v4, v8, v9w | `deliverables/wip/sing_v9w_{S1,V3S}_vs.mp4` |
| First frames against v8 and v4 | `media/sing/review/v9w_first_vs_v8_v4.jpg` |
| Hair fix before and after | `media/sing/style/v9w/{S1,V3S}_fix_before_after.jpg` |
| Over magenta and over the plate, full size | `media/sing/review/v9w_first_check_{S1,V3S}.jpg` |

**Ear-test clips are new this round.** They play the patched take frames (the eye fixes are in, applied to the take
before syncing, `tools/sing/v9w_post.py patch`). Each frame is matted per frame over the plate crop, with the v5coda mix
under it. They have no lyric layer and no Bean move; the previews have those.

## 1. Stills (`tools/sing/v9w_stills.py`, new; no model call)

**Hair recolour, local only.** It works inside the hair zone, with the face oval (stretched up to the hairline), the
neck, ears, pencils and (V3S) the jacket bands protected. Measured change inside the face oval: **0.0** on both.
- **S1:** the orange wash bloom around the bun and down her left temple goes back to paper where it lies on paper. Where
  it tints strands, or fills gaps inside the bun, it goes to her dark hair tone. The pencils are untouched.
- **V3S:** the hair's gold chroma is cut to 25 % and its mid-tones darkened by up to 22 %, so the hair reads dark, with
  a warm highlight left on the lit edge.

**Upscale** to 3072 wide (S1 3072x2048, V3S 3072x2458), with Real-ESRGAN x4plus, tiled.
- ESRGAN alone smoothed the paint grain on her skin, a beautifying drift, so the result is blended 50/50 with Lanczos.
- **Likeness against her photo** (`style/v9w/likeness.json`; % change of each ratio, as in the style README):
  - S1, v8 still → v9w 2k: NME 1.01 → 1.21 %; eye width +1.0 → +0.4; eye height -3.3 → -2.1; face width / height
    +6.4 → +7.4. That last one is the closed singing mouth, as the README explains.
  - V3S: NME 1.08 → 1.33 %; **eye width +4.6 → +4.1** (not worse); lower face +2.5 → +3.0; face width / height
    +2.7 → +4.0.
  - By eye at 2x: the same face, with the paint texture kept.

## 2. First frames (`tools/sing/v9w_first.py`, new)

**Placement:** v8's medium shot. Face 0.306 (S1) and 0.309 (V3S) of the frame height; eyes at 1080p (941, 416) / (941, 417).
Both stills reach past the frame's bottom edge, so there is no cut.

**Matte:**
- BiRefNet, then wc_comp.refine and a hair-edge firming. Painted wisps get their alpha from how much darker than the
  paper they are, so they read dark over the engraving rather than grey and semi-transparent.
- The paper is unmixed from the edge colour.
- S1 adds:
  - an ink key on the bun: BiRefNet had kept the pale wash bloom as solid figure; where the recolour acted, the alpha
    comes from the original still's darkness;
  - the pencil key.
- Checked at full size over magenta and over the plate. Both pencils are whole: pink eraser at the picture's left,
  pale-blue at the right, with ferrules.

## 3. Prompt P9W (`wc_takes.py`, `WC_VER=v9w`; S1 1935 chars, V3S 1838; v7/v8 unchanged)

P8's acting, plus three changes:
- **A painting:** she is a watercolour painting in warm washes on rice paper, lit warm from one side, that stays painted
  and never photographic, while the world stays black ink.
- **A jaw lock:** "her face, jaw and chin keep exactly the shape of the first frame: only her lips, lids and brows move;
  the head turns are small, slow and rigid. A light breeze in her hair carries most of the movement."
- **Harder on the eyes:** "Her eyes stay open the whole time, looking into the lens ... only quick full blinks, never
  closed for longer."

## 4. Takes (Seedance 2.5 720p avatar; 4 per shot; all 16:9; tags `v9w_sing_*`)

Jaw, `tools/sing/v9w_jaw.py` (new): the upper-jaw contour residual after a rigid head fit, against the first frame, in
inter-ocular units (p50 / p95 / max). Baselines: watercolour v4 S1 .030 / .106 / .127, V3S .083 / .129 / .134.
v8 (photo) reads .34-.42, because its head turns change the projected contour.

| Take | Lag (corr; windows) | Eyes on screen | Jaw p50/p95/max | Brow / jaw95 / roll | Verdict |
|---|---|---|---|---|---|
| S1 t1 | +0.56; windows -0.46..+1.48 | blink 0:13.15-0:13.49 | .159/.219/.229 | .22 / .15 / 4.1° | reject: lag unsteady; jaw drifts most |
| S1 t2 | +0.77; +0.40..+1.70 | shut 0:12.88-0:13.63 | .064/.117/.136 | .51 / .17 / 0.8° | reject: eyes shut through "The night" |
| S1 t3 | +0.63; +0.20..+1.58 | open to the cutaway | .121/.201/.211 | .32 / .21 / 7.7° | spare: lag drifts, jaw .20 |
| **S1 t4** | **+0.848 (r .63)**; +0.84 at 13.9, +0.88..+0.93 on phrase 2 | one quick blink 0:12.81-0:13.10 | **.020/.041/.060** | .17 / .24 / 1.1° | **pick, +0.85**: the steadiest jaw of any take, v4 included; both pencils; stays painted |
| V3S t1 | +0.22 | shut 2:33.59-2:34.30, 2:37.01-2:38.05 | .059/.123/.138 | .45 / .12 / 5.9° | reject: eyes shut 1 s |
| V3S t2 | +0.08 | shut 2:33.59-2:35.25 | .095/.122/.142 | .52 / .15 / 1.6° | reject: eyes shut 1.7 s |
| V3S t3 | +1.22, windows +0.14..+1.80 | shut 2:33.07-2:34.07, 2:36.90-2:37.36 | .031/.060/.091 | .55 / .17 / 1.8° | reject: lag unusable, eyes shut |
| **V3S t4** | events +0.41/-0.00/+0.14/+0.17, windows mostly +0.14..+0.18 | quick blinks; two lid-dips (patched) | .062/.098/.167 | .27 / .15 / 6.2° | **pick, +0.15**: steady lag, eyes open, a hint of a smile at the end |

**Against v8, on the picks (take-wide):**
- Inner-brow range S1 0.17 (v8 0.43), V3S 0.27 (v8 0.42): calmer and lower.
- Jaw p95 S1 0.24 (v8 0.32), V3S 0.15 (v8 0.23): softer lips.
- **Head turn is small:** S1 roll 1.1°; V3S roll 6.2° with yaw ±0.03. That is the jaw lock asking for "small, slow,
  rigid". The turn and chin-down read as a pose rather than a movement.
- **Identity at 720p** against the start frame:
  - S1 t4: inter-ocular 118.1 (120.2), eye width 35.0 (36.0).
  - V3S t4: 121.1 (123.7) and 36.5 (37.4).
  - Eye width / inter-ocular 0.296 against 0.300 (S1) and 0.301 against 0.302 (V3S), so no enlargement.
- **Painted look:** checked at full size at take frames 0, 60, 120 and 190 (S1) and 0, 60, 110 and 165 (V3S). Both stay
  watercolour on paper over ink and never go photographic.

## 5. Sync (measured; not wired)

- **S1 +0.85** (`wc_post.py` `SYNC_V9W`, knots (12.60, 0.55), (19.64, 7.59)).
  - On the trace the 'b' releases into "fore" on the voice's dip at 13.88.
  - The 'm' of "my" releases at 16.30 (voice 16.29).
  - The phrase end falls with the voice.
- **V3S +0.15** (take `v9w_take_4_open`; knots (153.98, 0.45), (159.14, 5.61)).
  - The 'b' closure sits on 154.6-154.7 and the 'm' on 157.1.
  - The mouth falls just after the phrase end.
- **Synced files:**
  - `media/sing/S1/v9w_sync_1080.mp4` (179 frames)
  - `media/sing/V3S/v9w_sync_1080.mp4` (133 frames)
  - their mattes `.../v9w_sync_1080_matte/`, the take's per-frame mattes mapped through the same sync, so the engine
    contract holds.

## 6. Eyes and matte

**Eyes:**
- **S1:** no patch. One quick full blink at 0:12.81-0:13.10 (f307-f313), while she is small in the Bean wide. Open
  everywhere else on screen.
- **V3S, patched in the take** (`v9w_take_4_open.mp4`):
  - a lid-dip at the in-point, 2:33.99-2:34.24 (take frames 11-17, from frame 9);
  - a half-lid at 2:37.49-2:37.65 (take frames 95-99, from frame 94).
  - Checks: `V3S/v9w_take_4_open_check_{11,95}.jpg`.
- **V3S kept:** quick full blinks at 2:34.85-2:35.06 (f3717-f3721) and 2:37.06-2:37.27 (f3770-f3774), the second just
  before the cutaway at 2:37.39.

**Matte:**
- **S1:** BiRefNet, plus `tools/sing/v9w_pencils.py` (new). BiRefNet drops both pale erasers in the painted takes, and
  the pale-blue eraser is too grey to key by colour. So each whole pencil is taken from the first frame and moved
  rigidly with its yellow body every frame. Both bodies were found on 178 of 193 frames, one on 15.
- **V3S:** BiRefNet.
- Checked over the plate at S1 take frames 0, 40, 80, 120, 160 and 190, and V3S previews 2:33.99-2:39.00.

## What is weak (honest list)

- **Not heard.** Both lags are measured.
- **S1 pencils in the matte are a moved copy** of the first frame's pencils. Where the take tilts a pencil differently
  from its body's axis, the eraser can sit a few px off the take's own (not visible at 540p).
- **15 S1 frames have only one body found.** There the second pencil is BiRefNet's own (yellow only, no eraser). I didn't
  list which frames.
- **The head turn is small.** The jaw lock and the turn pull against each other: S1 roll is 1.1°, against v4's 3.2°.
- **V3S jaw** varies more (p95 .098, max .167 at take 4.04 s ≈ 2:37.6, under the cutaway) than S1's, though less than
  v4's (.129 p95).
- **V3S eye patches** (painted from a neighbouring frame): 2:33.99-2:34.24 (f3696-f3702) and 2:37.49-2:37.65
  (f3780-f3784).
- **V3S patch:** "1420 MHz" is small and soft, as in the painting.
- **S1 bun:** the take keeps a slightly lighter area in the bun at frame-right where the wash bloom was (no orange).
  Its flyaways are thinner than the still's.
- **Likeness:** the stills keep the style agent's drift (V3S eye width +4.1 % and lower face +3.0 % against her photo;
  S1 face width / height +7.4 %, mostly the closed mouth).
- **Upscaling** is an ESRGAN/Lanczos blend, then Seedance at 720p, so the skin is soft at 1080p.
- **Ear tests have no lyrics and no Bean move.** In S1 the film holds her small in the Bean wide until 0:13.92; the ear
  test shows her at full size throughout.

## Spend

| Item | Calls | Spend |
|---|---|---|
| S1 Seedance 8 s | 4 | $7.40 |
| V3S Seedance 7 s | 4 | $6.47 |
| **Total v9w** | 8 | **$13.87** |

No image-model calls were made; the stills were fixed locally. The project is at **$398.21** of the $600 cap.

## Files touched

- **New:** `tools/sing/v9w_stills.py`, `v9w_first.py`, `v9w_jaw.py`, `v9w_post.py`, `v9w_pencils.py`.
- **Extended:**
  - `wc_takes.py`: `P9W`, `V9W_HAIR`, `WC_VER=v9w`.
  - `wc_post.py`: `SYNC_V9W`.
  - `v5_pencils.py` and `v7_matte_fix.py`: they scale 720p take frames to the 1080 matte; 1080 inputs are unchanged.
- **Timeline:** `render/timeline/A.js` and `E.js` are unchanged (v7).
- **Pages and notes:** `deliverables/wip/sing_review.html`, `SING_STATE.md`, `media/sing/NOTES.md`.
- **Media:**
  - `media/sing/style/v9w/`
  - `media/sing/first/v9w*`
  - `media/sing/{S1,V3S}/v9w_*`
  - `media/sing/review/v9w_*`
  - `deliverables/wip/sing_v9w_*`

## Rebuild

```
$MPY tools/sing/v9w_stills.py fix; $EPY tools/sing/v9w_stills.py upscale; $MPY tools/sing/v9w_stills.py metrics
WC_VER=v9wS1 $EPY tools/sing/wc_comp.py matte media/sing/style/v9w/S1_2k.png; WC_VER=v9wV3S $EPY tools/sing/wc_comp.py matte media/sing/style/v9w/V3S_2k.png
$MPY tools/sing/v9w_first.py comp; $MPY tools/sing/v9w_first.py check
WC_VER=v9w $PY tools/sing/wc_takes.py submit S1 V3S --n=4
$MPY tools/sing/v9w_post.py patch V3S v9w_take_4 9:11-17:2 94:95-99:2
WC_VER=v9w $EPY tools/sing/wc_post.py matte S1 v9w_take_4; $EPY tools/sing/v9w_pencils.py media/sing/S1/v9w_take_4.mp4 media/sing/S1/v9w_take_4_matte
WC_VER=v9w $EPY tools/sing/wc_post.py matte V3S v9w_take_4_open
WC_VER=v9w $PY tools/sing/wc_post.py sync S1; WC_VER=v9w $PY tools/sing/wc_post.py sync V3S   (+ map the take mattes into v9w_sync_1080_matte/)
$PY tools/sing/v9w_post.py ear S1 v9w_take_4 0.85 media/sing/review/v9w_S1_lag+0.85_measured+0.00_MEASURED.mp4
To wire: A.js S1_SRC = 'media/sing/S1/v9w_sync_1080.mp4'; E.js V3S_SRC = 'media/sing/V3S/v9w_sync_1080.mp4', HER matte 'media/sing/V3S/v9w_sync_1080_matte/'.
```

## Wired (2026-10-18, Jade: "hair up: 0.7 is slightly better. the one you picked for hair down looks good. yes, wire them in.")

| Shot | Wired file | Lag | Matte |
|---|---|---|---|
| S1 | A.js `S1_SRC = 'media/sing/S1/v9w_sync_1080_l070_open.mp4'` | **+0.70** (Jade's ear; measured +0.85) | `v9w_sync_1080_l070_open_matte/` (symlink to `v9w_sync_1080_l070_matte/`) |
| V3S | E.js `V3S_SRC = 'media/sing/V3S/v9w_sync_1080.mp4'` | +0.15 (measured; Jade: "looks good") | E.js `V3S_lyric` HER `media/sing/V3S/v9w_sync_1080_matte/` |

- **S1 at +0.70:** `SYNC_V9W` S1 knots are now (12.60, 0.40), (19.64, 7.44) (`--name=v9w_sync_1080_l070`).
  - The new in-point brings the take's blink on screen at 0:12.93-0:13.22 (f310-f316, file frames 8-14). Its reopen hangs
    at half for two frames, so it is patched open on file frames 8-15 from frame 7.
  - After that, eyes are open over the whole on-screen span (0.97-1.03 at the in-point).
  - Check: `media/sing/S1/v9w_sync_1080_l070_open_check.jpg`.
- **S1 pencils, round 3 of `v9w_pencils.py`:** each first-frame pencil is found by masked template matching (position
  ±60 px, rotation ±20°).
  - Round 2's yellow-body centroid shifted when hair hid part of the body, which dropped the pale-blue eraser on several
    frames.
  - Both pencils matched (≥ 0.90) on all 193 take frames.
  - Checked over the plate at file frames 0, 10, 20, 30, 45, 60, 72 and 84: both whole, with erasers.
- **Edits:**
  - A.js: only the `S1_SRC` line (with its comment; v7 path kept) and the `A_S1_lyric` HER comment.
  - E.js: `V3S_SRC` (v7 path in the comment) and the HER matte.
  - Both import cleanly. A_R2.js, B.js and counters.md were not touched.
- **Previews:** `deliverables/wip/sing_v9w_S1_wired_preview.mp4` and `deliverables/wip/sing_v9w_V3S_wired_preview.mp4`.
  - Stills checked: Bean wide 0:12.62 / 0:12.95 (eyes open, no matte edge, pencils in the bun), and 0:13.40, 0:13.95,
    2:33.99, 2:38.30.
- **Weak:** in the Bean wide (0:12.60-0:13.92) she is about 70 px tall at 540p, so the pink eraser is only a couple of
  pixels; it reads clearly from 0:13.95.
