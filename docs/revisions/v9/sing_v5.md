# Singing shots v5: Jade's two photos (S1, V3S), 2026-10-16

Jade: "I've added 2 new images to /inputs. can you reshoot the 2 lip sync clips using these 2 new photos? the one with the
pencils should go in the first singing slot, and the one with long hair styled down should be the second."

- **S1** (0:12.60-0:19.64, f302-f471; on her until the cutaway at 0:16.14, f387) from
  `inputs/jade_ref_image2_music_video_pencils.png`: hair up, two pencils, pale-blue and pink erasers.
- **V3S** (2:33.98-2:39.14, f3696-f3819) from `inputs/jade_ref_image_music_video_long_hair.png`: long hair down.
- E3 untouched. Nothing committed. No v4 or earlier file overwritten or deleted.

Frame numbers are song frames (song seconds x 24).

> **Current state (after Jade's follow-ups the same day; details in "Follow-ups" at the end).**
> - **S1 wired:** `media/sing/S1/v5c_sync_1080.mp4`, shot again from the re-tinted pencils photo
>   (`media/sing/tint/local_a.png`), take `v5c_take_2`, lag +0.15 s. Preview: `deliverables/wip/sing_v5c_S1_preview.mp4`.
>   Ear test: `media/sing/review/v5c_S1_lag+{0.00,0.15,0.30}_*.mp4`.
> - **S1 fallback (the old take, re-synced):** `media/sing/S1/v5_sync_1080_l061_open.mp4` (+0.61). Ear test:
>   `media/sing/review/v5_S1_lag+{0.61,0.76,0.91}_*.mp4`. Preview: `deliverables/wip/sing_v5_S1_preview_l061.mp4`.
> - **V3S wired:** `media/sing/V3S/v5b_sync_1080_open.mp4`, the shoulder retake. Preview:
>   `deliverables/wip/sing_v5b_V3S_preview.mp4`. Its "shoulder" still includes the couch upholstery Jade pointed out.
> - **V3S next:** first frame `media/sing/first/v5d_V3S_first.jpg`, outpainted by nano-banana-pro, couch removed. It is
>   **waiting for Jade's look; no take shot yet.** Sheet: `media/sing/outpaint/contact_sheet.jpg`; v5b against v5d:
>   `media/sing/review/v5d_V3S_first_vs_v5b.jpg`.
> - **Spend for this job:** $14.21 of $20 (project $282.36 of $400, which includes other streams).

## Watch these

| What | File |
|---|---|
| S1 in the film (preview 960x540, 0:12.00-0:21.00, sfx mix v5coda) | `deliverables/wip/sing_v5_S1_preview.mp4` |
| V3S in the film (preview 960x540, 2:33.50-2:39.60) | `deliverables/wip/sing_v5_V3S_preview.mp4` |
| The synced singer alone, song under it | `media/sing/review/v5_S1_sync_review.mp4`, `media/sing/review/v5_V3S_sync_review.mp4` |
| First frames next to v4 | `media/sing/review/v5_first_vs_v4.jpg` |
| Take contact sheets | `media/sing/{S1,V3S}/v5_take_N_look.jpg` (whole take), `_win.jpg` (face strip at the lag) |

## Picks and takes

| Take | Frame | Lag (corr / events; 2 s windows) | Verdict |
|---|---|---|---|
| S1 `v5_take_1` | 16:9 1280x720, 193 fr | +0.89 / +0.89 (open +1.08, 'b' +0.89, 'm' +0.61); windows -0.15..+1.35, r .34 | spare: the mouth does not track the voice steadily |
| S1 `v5_take_2` | 16:9 1280x720, 193 fr | +0.60 / +0.50 (open +0.45, 'b' +0.55); windows over "The night before" +0.30..+0.53, r .5-.85 | **pick**: one lag, +0.46 s |
| V3S `v5_take_1` | 16:9 1280x720, 169 fr | +0.25 / +0.28 ('b' +0.00, 'm' +0.19); windows +0.03, then +0.29/+0.30 from 2:35.5 on, r .76-.96 | **pick**: piecewise sync |
| V3S `v5_take_2` | 16:9 1280x720, 169 fr | +0.46 / +0.45; windows -0.18..+1.14, r .38 | spare: unsteady, three blinks |

No take reframed (all 16:9, locked-off, face size as the first frame: S1 280-308 px, V3S 241-267 px at 720p). All four
stay photographic, keep the glasses and her face. Both S1 takes keep both pencils with their pale-blue and pink erasers, and
the patch stays readable. No retakes were needed.

Engine files (contract: file time 0 = in-point, rate 1, 1920x1080, 24 fps, no grain/push/grade; matte dirs with `fps.txt`):

- S1: `media/sing/S1/v5_sync_1080_open.mp4` + `v5_sync_1080_open_matte/` (links to `v5_sync_1080_matte/`, 179 PNG).
  Plain version: `v5_sync_1080.mp4`.
- V3S: `media/sing/V3S/v5_sync_1080.mp4` + `v5_sync_1080_matte/` (133 PNG).

Sync knots are `SYNC_V5` in `tools/sing/wc_post.py`:
- S1: one lag, +0.46 s; untouched frames.
- V3S: +0.05 through "before" (to 2:35.60, f3734). The clip then runs at 1.24x through the vocal silence 2:35.60-2:36.60
  (f3734-f3758, 24 cross-faded frames, no words sung there; checked, no ghosting). Then +0.29 for "my dissertation
  defense".

## What I did

1. **First frames, photo pixels only** (`tools/sing/v5_first.py`, new). BiRefNet matte of each photo
   (`wc_comp.py matte`). Her edge colours are decontaminated from the photo's own background (couch, wall, shoji, painting).
   She is laid over the exact v4 plates in the v4 2576x1449 crop and centred on v4's x, with no model repaint or restyle.
   - **Mattes:** both photos' backgrounds are fully gone. Both pencils and both eraser colours are inside the S1 matte, and
     the couch arm separates cleanly from her left shoulder. On V3S, the blue painting showing between the crown strands
     is keyed out.
   - **Scale (least-bad option, as asked):** at v4's face size (32.5 % of the frame) neither photo reaches the bottom edge.
     The pencils photo stops 19 % of the frame short, so matching v4 would have meant inventing a quarter of her torso.
     The long-hair photo stops short and its jacket is cut by both photo edges.
     - S1: face 40.8 % of frame height, eyes at 1080p y 463 (v4 403). Only a 32-photo-px strip at the bottom is
       extended, using the photo's own bottom-row jacket colours.
     - V3S: face 34.8 %, eyes at y 429. Kept smaller so the whole 1420 MHz patch stays in frame.
   - **V3S patch:** the photo edge cuts the patch, so its missing third comes from the same patch in the pencils photo
     (her own jacket). It was mapped ellipse-to-ellipse and refined to NCC 0.82, so the text and ring line up.
   - **V3S sleeves:** the right sleeve continues 45 photo px past the edge in plain fabric colour. The left arm edge is the
     photo border, trimmed to a rounded shoulder (trimming only, no new pixels). No anatomy, face or hair was invented.
2. **Takes**, through `wc_takes.py` with `WC_VER=v5` (extended, not forked):
   - New prompt `P5` (photographic woman, ink world, "the two never blend", "never painted, drawn or cartoonised").
   - Hair per shot: S1 "loose messy bun with two yellow pencils ... pale-blue eraser ... pink eraser ... stay exactly as
     they are"; V3S "long dark hair worn down".
   - S1's opening line asks the photo's faint smile to fade at once.
   - v4 acting kept, and the v4 slices, durations, 720p and avatar mode.
   - Logged as `v5_sing_S1` and `v5_sing_V3S` in `media/genlog.jsonl`.
3. **Pick and sync:**
   - `look.py` on all four takes, plus a 2 s windowed lag check, because the event lags disagreed with each other.
   - `wc_post.py sync`, then `matte` (BiRefNet per frame), then `review_sync`.
   - S1 blink: the pick's eyes are closing on the in-point, 0:12.60-0:12.72 (f302-f305, file frames 0-3). That falls in
     the wide Bean opening, so `v4_noblink.py` lays the open eyes of file frame 6 over frames 0-4 (`_open` file; check
     image `media/sing/S1/v5_sync_1080_open_check.jpg`).
   - S1 matte: BiRefNet dropped the pencils from the per-frame matte, which matters while only the matted layer shows
     her (0:12.60-0:13.92). `tools/sing/v5_pencils.py` (new) keys them back in by colour, which is safe because the
     plate is pure black and white. The BiRefNet originals are kept in `v5_sync_1080_matte_birefnet/`.
4. **Wiring:**
   - `render/timeline/A.js`: `S1_SRC = 'media/sing/S1/v5_sync_1080_open.mp4'`, and through it `S1_MATTE` (`S1_her`, the
     `A_S1_lyric` matte).
   - `render/timeline/E.js`: `V3S_SRC = 'media/sing/V3S/v5_sync_1080.mp4'`, and the `V3S_lyric` HER matte
     `v5_sync_1080_matte/`.
   - The v4 paths are kept in comments.
   - Dependency check:
     - Nothing in A.js keys off v4's hair shape. The arc lyric (THE NIGHT BEFORE) sits outside ±31° on radii 846-1014,
       clear of her head; checked in the preview.
     - The v5 stair overlay (`overlay_S1_clock.png`) doesn't overlap her on frame 0; her arm comes within about 13 px of
       it. `S1_her` is drawn after it anyway.
     - C2 and R4 comp the rendered film, so they update by themselves.
     - The unused v2 `HEAD`/`PUSH_KB` (S2 push) was tuned to the v2 framing, as before.
5. **Previews** (960x540 only), rendered from my shell with `node render/engine/render.mjs --preview --force --range ...
   --encode --audio media/sfx/Rewind_cinematic_sfx_mix_v5coda.mp3` (`--encode` is needed for an MP4 from a range).
   - The prepare step confirms the v5 media.
   - I checked stills at 0:12.62, 0:12.90, 0:13.25, 0:13.60, 0:13.95, 0:14.30, 0:14.80, 0:15.60 and 0:16.10, and at
     2:33.99, 2:34.40, 2:34.90, 2:35.90, 2:36.80, 2:37.15, 2:37.60 (cutaway), 2:38.30 and 2:39.00.
   - The matte edges sit cleanly on the engraving with no visible halo. The pencils show even in the wide. The mouth is
     open mid-"before" at 0:14.30 (f343) and mid-"night" at 2:34.40 (f3706).

## What is weak (honest list)

- **Lip sync is measured, not heard.** S1 rests on "The night before" only, since S1 is on her for just that. V3S is
  piecewise. Please judge both by ear.
- **V3S right shoulder** is squared off with a straight outer edge, caused by my sleeve extension in the first frame.
  Seedance kept it in every frame, so it's in the take, not just the matte. It's visible at preview size (e.g. 2:34.90,
  f3718). The fix is one retake (about $1.62) from a first frame whose right sleeve is rounded off; not done, because
  the takes themselves passed.
- **V3S blinks:**
  - 2:34.15-2:34.35 (f3700-f3704), just after the cut-in.
  - 2:37.06-2:37.23 (f3769-f3774), on "my", right before the cutaway at 2:37.39 (f3777).
  Neither is patched; `v4_noblink.py` could take out either one.
- **S1 smile:** the photo's faint closed-mouth smile holds through the wide opening, 0:12.60-0:13.20 (f302-f317), before
  she sings. It is gone once she sings.
- **S1 bottom edge:** the bottom 30 px (1080p) of jacket are the photo's bottom-row colours carried down, with faint
  vertical marks. The lower-left forearm ends in a straight vertical (the photo border).
- **Scale:** both are bigger than v4 (S1 face 41 % vs 32.5 %), so she is also bigger in the Bean wide opening. S1 and V3S
  no longer share one figure scale (41 % vs 35 %).
- **V3S crown:** a warm patch where the photo's wooden picture frame shows through her hair; it reads as an auburn
  highlight.
- **Identity:** I see no drift, repaint or cartooning in either pick, but at 720p upscaled to 1080p the skin is a little
  soft. The source photos already have a smoothed, slightly painterly skin texture.

## Spend

Seedance 2.5 720p, 4 calls: S1 2 x 8 s = $3.70, V3S 2 x 7 s = $3.24. **Total $6.94** of the $20 cap. Project total (list
estimates) went from $266.13 to **$273.06** of $400. Local passes (mattes, comps, patch fit, sync, noblink, pencil key,
previews) cost nothing.

## Files touched

- New: `tools/sing/v5_first.py`, `tools/sing/v5_pencils.py`.
- Extended: `tools/sing/wc_takes.py` (`WC_VER=v5`: `P5`, `V5`, tag `v5_sing_*`) and `tools/sing/wc_post.py` (`SYNC_V5`).
- Rewired: `render/timeline/A.js` (S1), `render/timeline/E.js` (V3S).
- Notes: `media/sing/NOTES.md` "# v5".
- New media, all `v5_`:
  - `media/sing/first/`: `v5_{S1,V3S}_first.jpg/.json`, `v5_her_mask_first_frame_{S1,V3S}.png`, `v5_{S1,V3S}_fig.jpg`,
    `v5_{S1,V3S}_alpha.png`, `v5S1_her_alpha.png`, `v5V3S_her_alpha.png`, `v5_patch_V3S.json`.
  - `media/sing/{S1,V3S}/`: `v5_*` takes and synced files.
  - `media/sing/review/v5_*`.
  - `deliverables/wip/sing_v5_*_preview.mp4`.

## Follow-ups (2026-10-16, same day)

### 1. S1 re-sync of the old take (Jade: "the video lags behind audio")

- **Re-measurement** of `v5_take_2`, using a mouth-vs-voice trace and correlation over just the on-screen phrase
  (0:13.05-0:14.95):
  - At +0.46 the 'b' closure lands at 0:13.93, against the voice's dip at 0:13.85.
  - The widest opening peaks at 0:14.35, while the "be-FORE" vowel peaks at 0:13.90-0:14.20.
  - The inner-lip gap and the jaw both correlate best at +0.55 (r .66 / .51), and the 'b' closure says +0.59.
  - So the mouth ran about 0.1-0.15 s late, as Jade heard.
- **Re-synced** to +0.61 as `media/sing/S1/v5_sync_1080_l061.mp4`, carrying over:
  - the noblink (`_l061_open`: file frame 0 from frame 3, frame 1 blended);
  - the pencil-keyed matte `v5_sync_1080_l061_matte/` (BiRefNet originals in `_birefnet/`).
  - The +0.46 files are kept.
- **Ear test:**
  - `media/sing/review/v5_S1_lag+0.61_lips_0.15s_earlier.mp4`
  - `media/sing/review/v5_S1_lag+0.76_lips_0.30s_earlier.mp4`
  - `media/sing/review/v5_S1_lag+0.91_lips_0.45s_earlier.mp4`
  - Each covers 0:12.60-0:19.64, 960x540, with the v5coda mix under it. All stay inside the take (clip end 7.35 / 7.50 /
    7.65 s of 8.04 s), so no held frames are needed at 0:19.64.
- Wired, then superseded by v5c (section 3). It is now the fallback.

### 2. V3S shoulder retake (v5b), then the couch correction (v5d)

- **v5b first frame** (`tools/sing/v5_first.py`, `V5_REV=b`): the frame-right sleeve was redrawn as a curved arm
  (rounded shoulder cap, slanting outer edge, cylinder shading) instead of v5's straight strip.
- **Takes:**
  - `v5b_take_1` came back **21:9 (1470x630)**, so it was rejected.
  - `v5b_take_2` (16:9): one lag of **-0.05 s**. Closures: 'b' -0.13, 'm' -0.23; correlation -0.04 (r .66); 2 s windows
    from 2:36.0 on -0.07..-0.02.
  - Its eyes were closed at 2:33.98-2:34.48 (f3696-f3708, file frames 0-12). They are replaced by the open eyes of
    frame 15 (`v5b_sync_1080_open.mp4`; check image `_open_check.jpg`).
  - Blink left in: 2:37.19-2:37.35 (f3773-f3776), on "my", just before the cutaway.
- **Wired** in `render/timeline/E.js`, with the v5 paths kept in comments. Preview:
  `deliverables/wip/sing_v5b_V3S_preview.mp4`; review clip `media/sing/review/v5b_V3S_sync_review.mp4`.
- **Jade's correction:** part of what v5/v5b treated as her frame-right shoulder is the **couch upholstery** (lacy white,
  source x ~930-1086, y ~850-1050). BiRefNet kept it, so v5b still has a white block above her shoulder. Her real
  shoulder line is the top edge of the epaulet with the snap (~(995, 1037)).
- **v5d, the outpaint** (`tools/sing/v5_outpaint.py`):
  - **Input:** the photo was padded left, right and bottom on wall-grey canvases (4:3 2133x1600 for nano-banana-pro,
    3:2 2400x1600 for gpt-image). The couch was hand-masked and painted out to the wall colour
    (`media/sing/outpaint/couch_mask.png`).
  - **Models:** nano-banana-pro and gpt-image-2.5-flare, one take each, $0.33 together. The prompt asked for both
    shoulders and arms to be completed, the shoulder sloping along the epaulet, the orange bands continuing, and the full
    1420 MHz patch.
  - **Merge:** the photo's own pixels are pasted back over everything the photo shows (never the couch), with a ~25 px
    feathered seam. The model output is first registered to her face.

| Outpaint | Landmark drift (mean / max px) | Verdict |
|---|---|---|
| `nbp_1` (nano-banana-pro) | 2.0 / 4.7 (detector noise is about 1 / 3.3) | **pick**: framing kept; right shoulder slopes from the collar along the epaulet into a hanging arm; band wraps the sleeve; patch complete with text continuous across the seam; left arm continues to the lower left (selfie pose) |
| `gpt_1` (gpt-image-2.5-flare) | 2.4 / 6.6 | reject: re-rendered the whole picture and moved her body relative to her face, so the merge doubles the patch |

- **v5d first frame:** `media/sing/first/v5d_V3S_first.jpg`, with `v5d_her_mask_first_frame_V3S.png` (`V5_REV=d`;
  BiRefNet on the merge).
  - Same scale and place as v5: face 34.8 %, eyes at 1080p (941, 429). The landmarks are taken from the original photo,
    because the detector reads the face 2 % bigger on the wide canvas.
  - Her face, hair and every jacket pixel the photo shows are the photo's own. Only the arms past the photo's edges and
    the patch's missing third are the model's.
  - Checked at full size: the shoulder slope, the arm outline, the band across the seam and the patch text all look
    right. The crown is clean.
  - Faint seam: at most a hairline is left on the frame-left sleeve, where the photo's edge was.
- **Not shot yet**, as asked. When Jade approves, one Seedance take (`WC_VER=v5d`, about $1.62) still fits the $20 cap.

### 3. S1 again, from the re-tinted pencils photo (v5c; Jade: "local_a is good")

- **First frame:** `media/sing/first/v5c_S1_first.jpg` (`V5_REV=c`). It is a straight swap of `local_a`'s pixels into
  the v5 geometry: same matte (max difference 0), same landmarks and scale. Pixels changed only in her face.
- **Takes** (same prompt and settings; tag `v5_sing_S1_tint`):

| Take | Frame | Lag over "The night before" | Verdict |
|---|---|---|---|
| `v5c_take_1` | 16:9 1280x720 | mouth runs against the voice (best -0.45, r .33) | reject |
| `v5c_take_2` | 16:9 1280x720 | **+0.10 (r .82)**: mouth opens 0:13.17 (voice 0:13.15), 'b' closes 0:13.88 (voice dip 0:13.85), widest on "fore" 0:14.15-0:14.40 | **pick**, wired at **+0.15** |

- **Lag choice:** +0.15 puts the lips 0.05 s ahead of the measurement, leaning early as Jade's note on the old take
  suggests (r .78). With a lag that small, the in-point comes 0.15 s before the take starts. So the take's first frame
  (the start image itself) is held for 4 frames, 0:12.60-0:12.75 (f302-f306). `wc_post.synced_frames` now holds instead
  of stopping.
- **Ear test:**
  - `media/sing/review/v5c_S1_lag+0.00_0.15s_later.mp4`
  - `media/sing/review/v5c_S1_lag+0.15_WIRED.mp4`
  - `media/sing/review/v5c_S1_lag+0.30_0.15s_earlier.mp4`
- **Eyes:** open at the in-point, so no noblink was needed. There's a 2-frame half-lid at 0:13.39-0:13.43 (f321-f322)
  on "night".
- **Matte:** `media/sing/S1/v5c_sync_1080_matte/`, with the pencils keyed in on every frame (`v5_pencils.py`; originals
  in `_birefnet/`).
- **Wired:** `render/timeline/A.js` `S1_SRC = 'media/sing/S1/v5c_sync_1080.mp4'`, with the earlier paths in comments.
  Preview: `deliverables/wip/sing_v5c_S1_preview.mp4`.

### Weak spots (follow-ups)

- **Lips are measured, not heard,** for every variant. For S1 v5c I leaned 0.05 s early on purpose.
- **S1 (both takes):** the mouth still moves a little in the vocal silence, 0:14.9-0:16.14 (e.g. 0:15.30, f367), before
  the cutaway.
- **V3S v5b (wired now):**
  - It still carries the couch block on the frame-right shoulder. v5d fixes that once it's shot.
  - Blink at 2:37.19-2:37.35, on "my".
  - The opening eye patch spans 13 frames (2:33.98-2:34.48). Her eyes hold still there while she sings "The".
- **V3S v5d:**
  - The frame-left arm reaches toward the lower left (the model read the photo as a selfie).
  - The model's sleeve fabric is a little smoother than the photo's.
  - A faint hairline seam is left on that sleeve.

### 4. V3S shot from the outpainted frame (v5d), and Jade's half-blink note

Jade on v5b: "the timing on the original v5b is good, but the blink is a weird half-blink that looks a little uncanny".

- **The half-blink in v5b** (`deliverables/wip/sing_v5b_V3S_preview.mp4`), stepped frame by frame: it is the take's own
  blink on "my", **2:37.08-2:37.38 (f3770-f3777)**.
  - The lids sink to half (openness 0.42-0.58 of open) and stay there for about 8 frames without ever closing.
  - The cutaway at 2:37.39 then cuts in mid-droop.
  - The cut-in eyes-open patch (2:33.98-2:34.58, f3696-f3710) stays open on every frame (0.77-0.85), so it isn't the
    problem.
- **Takes** (tag `v5_sing_V3S_r3`):

| Take | Frame | Lag | Verdict |
|---|---|---|---|
| `v5d_take_1` | 16:9 | closures +0.42 / +0.52, opening +0.74; 2 s windows jump -0.49..+1.37; phrase r .34 | reject: unsteady; eyes shut about 12 frames near the in-point and 0.3 s on "my" |
| `v5d_take_2` | 16:9 | closures 'b' +0.17, 'm' +0.14, end -0.00; phrase gap best +0.15 (r .48); sung windows 2:36.0-2:37.5 +0.21..+0.39 (r .73-.92) | **pick**, wired at the measured **+0.15** |

- **Lag:** as asked, v5d is wired at the measured lag. For comparison, v5b's measured and wired lag was -0.05, which
  Jade heard as right. Both are set by the same method (lip closures plus correlation), so v5d is wired the same way.
- **Ear test** (2:33.98-2:39.14, 960x540, v5coda mix; built from the raw take, so the eye patch isn't in them):
  - `media/sing/review/v5d_V3S_lag+0.00_measured-0.15_lips_later.mp4`
  - `media/sing/review/v5d_V3S_lag+0.15_measured_WIRED.mp4`
  - `media/sing/review/v5d_V3S_lag+0.30_measured+0.15_lips_earlier.mp4`
  - `media/sing/review/v5d_V3S_lag+0.45_measured+0.30_lips_earlier.mp4`
- **Eyes in v5d,** frame by frame:
  - **Lid droop: 2:34.35-2:34.56 (f3705-f3710, file frames 9-14).** Lids at 0.55-0.83, never closed, on "night". It
    would read as a half-blink, so it is removed: frames 9-14 take the open eyes of file frame 8 (2:34.31, fully open)
    at full strength, with no fade, handing back to the take's own eyes at frame 15 (2:34.60, open, 0.85).
    - After the patch, frames 9-15 hold a steady 0.75-0.85, with no dip at either seam.
    - Files: `v5d_sync_1080_open.mp4`; check image `_open_check.jpg`.
  - **Full blink, kept untouched: 2:36.10-2:36.35 (f3747-f3752).** Lids fully closed for 3 frames (2:36.15-2:36.23,
    openness 0.10-0.13), then open again. It falls in the vocal silence, before the cutaway.
  - The take is open on "my" (2:37.12-2:37.39).
- **Files:**
  - `media/sing/V3S/v5d_sync_1080_open.mp4` and `v5d_sync_1080_open_matte/` (-> `v5d_sync_1080_matte/`, 133 PNG,
    BiRefNet).
  - Wired in `render/timeline/E.js` (`V3S_SRC` and the `V3S_lyric` HER matte), with the v5b paths in comments.
  - `render/timeline/A.js` and S1 are untouched.
- **Preview:** `deliverables/wip/sing_v5d_V3S_preview.mp4` (2:33.50-2:39.60).
  - Stills checked at 2:33.99, 2:34.40, 2:34.75, 2:36.20, 2:37.20 and 2:38.40.
  - The shoulder slopes along the epaulet into a hanging arm, with no couch block and no straight cut. The patch is
    whole and the matte edge is clean.
- **Weak spots:**
  - The lips are measured, not heard.
  - The frame-left arm reaches toward the lower left (the outpaint's selfie read).
  - Her eyes at 2:34.35-2:34.56 are frame 8's eyes carried over 6 frames, slightly heavy-lidded (0.75-0.8), so they
    hold still while she sings "night".
  - The take's mouth on "dissertation defense" is smaller than v5b's.
- **Spend for this job:** $17.45 of $20.

| Tag | Spend |
|---|---|
| S1 | $3.70 |
| V3S | $3.24 |
| V3S_r2 | $3.24 |
| S1_tint | $3.70 |
| V3S_outpaint | $0.33 |
| V3S_r3 | $3.24 |
