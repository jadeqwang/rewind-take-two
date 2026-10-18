# Singing shots: state at checkpoint (2026-10-16, about 15:50 CDT)

A resume note for the singing-shot rework. The full history is in `docs/revisions/v9/sing_v5.md` and
`media/sing/NOTES.md` (section "v5"). Media is gitignored and lives only on this machine.

## Wired into the film now (540p previews only; no 1080p render)

| Shot | Song time | File (`render/timeline/…`) | Source photo | Sync |
|---|---|---|---|---|
| S1 (1st singing slot) | 0:12.60-0:19.64 | A.js `S1_SRC = media/sing/S1/v5c_sync_1080_l090_open.mp4` | `inputs/jade_ref_image2_music_video_pencils.png`, re-tinted (`media/sing/tint/local_a.png`) | lag +0.90, Jade's ear pick ("about right, for the first half"); eyes patched open on file frames 1-6 |
| V3S (2nd singing slot) | 2:33.98-2:39.14 | E.js `V3S_SRC = media/sing/V3S/v5d_sync_1080_open.mp4` | `inputs/jade_ref_image_music_video_long_hair.png`, couch cut out, shoulders and patch outpainted (`v5d_V3S_first.jpg`) | measured lag +0.15 (v5b's measured lag was "good" by Jade's ear); lid droop at 2:34.35-2:34.56 patched open |

Previews: `deliverables/wip/sing_v5c_l090_S1_preview.mp4`, `deliverables/wip/sing_v5d_V3S_preview.mp4`.

## Open: the photos may change again

Feedback from a friend of Jade's: neither singing photo looks like her (the reference photos were beautified). New
direction, in progress:

- `inputs/nomakeup_selfie.png`. Round 1 (light makeup + jacket) gave `media/sing/selfie/selfie_pick_{model,hybrid}.png`.
  Round 2 ("no-makeup makeup" glow-up) gave `selfie_r2_pick_{model,hybrid}.png`. Contact sheets and metrics are in
  `media/sing/selfie/` (README there).
- `inputs/light_makeup_irl.png`: Jade's own real makeup. Round 3 = the film's jacket only, face untouched (a little
  smoothing or freckle removal is OK). Running at checkpoint time, writing to `media/sing/selfie/r3/`
  (`tools/sing/selfie_r3.py`).
- Once Jade picks a photo, rebuild BOTH shots from it. Fill in the shoulders and patch if they are cut off
  (`tools/sing/v5_outpaint.py`), place her over the plates (`tools/sing/v5_first.py`), shoot Seedance takes
  (`wc_takes.py`), then `look.py`, `wc_post.py` sync and matte, `v5_pencils.py` if there are pencils, and
  `v4_noblink.py` for half-blinks.

## Jade's standing notes from this round

- **Lip sync:** judge by ear. For S1, the measured lag was 0.8 s too small (measured +0.10; she picked +0.90). For V3S
  the measurement was right. Always make ear-test clips that bracket well earlier than the measurement.
- **Blinks:** no half-blinks (lids that sink partway and hang). Keep a full natural blink, or remove it cleanly.
- **Likeness:** no slimming, no eye enlargement, no nose or jaw change, brow shape untouched. Light makeup and light
  hair tidying are fine, and so is a little skin smoothing or freckle removal.
- **No spend cap** (Jade: "we have plenty of credits"). Keep logging spend. Total at checkpoint is about $290.
- **Review pages:** keep them local, at `deliverables/wip/sing_review.html` (media paths relative to it), and open
  them for her with `xdg-open`.
- **Style tests** (gongbi and Braid-like, `media/sing/style/`) were shown to Jade; none chosen.

## Env gotchas

- `FFMPEG=/home/jade/Documents/1-music-shipped/moongazing/.venv/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2`
- `FACE_LANDMARKER=$HOME/Documents/1-music-shipped/moongazing/tools/sync/models/face_landmarker.task` (`mouth.py`'s
  default path is stale)
- MediaPipe venv: `~/Documents/1-music-shipped/orbital-sunrise-video/video/out/.venv/bin/python`. BiRefNet:
  `tools/engrave/.venv/bin/python`.
- Range preview: `node render/engine/render.mjs --preview --force --range A B --encode --audio
  media/sfx/Rewind_cinematic_sfx_mix_v5coda.mp3 --out deliverables/wip/<name>.mp4`

## Decisions after the checkpoint (2026-10-16)

- **Photo:** round 3 on `inputs/light_makeup_irl.png`. Jade: "hybrid's fuller hair looks good, model del has right
  posture", so the pick combines the model edit's posture with fuller hair, her exact face pasted back, and the patch
  outpainted (`media/sing/selfie/r3b/`, `selfie_r3b_pick.png`).
- **Both singing slots use the hair-down photo** (Jade: "let's just use the hair down in both"). No pencils in S1 any
  more, so S1 needs no pencil key (`v5_pencils.py`).
- **Collar:** the model edit's jacket collar is correct; the r3 hybrid's face paste erased part of it (Jade). In r3b
  the collar (stand-up sides, snaps, turtleneck edge) comes from the model edit untouched, and the face mask stops at
  the jaw.
- **r3b at this checkpoint:** running (an agent was editing `selfie_r3_pick_model.png` for fuller hair, pasting her
  face back, and outpainting the patch). If it was interrupted, re-run that brief from these notes.

## v6: both shots rebuilt from the chosen photo (2026-10-16 evening, Jade away)

Jade: "go ahead and animate the singing so i can see it". Built from `media/sing/selfie/selfie_r3b_pick.png`, hair
down in both, with no outpaint needed. Full report: `docs/revisions/v9/sing_v6.md`.

| Shot | Wired file | Take | Lag |
|---|---|---|---|
| S1 0:12.60-0:19.64 | A.js `media/sing/S1/v6_sync_1080.mp4` | v6_take_1 | +1.09, measured over the whole line (v5c's phrase-1-only method read too small) |
| V3S 2:33.98-2:39.14 | E.js `media/sing/V3S/v6_sync_1080.mp4` | v6_take_3 | +0.20 measured |

- Previews: `deliverables/wip/sing_v6_{S1,V3S}_preview.mp4`. Ear tests: `media/sing/review/v6_*_lag*.mp4`.
- Open: Jade picks the sync by ear on `deliverables/wip/sing_review.html` (section "Singing v6"). Then rebuild the
  sync file at her pick (`wc_post.py` `SYNC_V6`, `--name`), re-matte, re-wire, re-render the preview, and re-check the
  eyes at the new in-point.

## v6b: S1 retake for movement and wind (2026-10-17)

Jade on v6: the second clip "feels much more natural than the first ... maybe because there's natural head movement ...
or maybe the first clip has a little bit of wind in the upper part of the hair but the wind isn't moving any other part
of the hair. can you add a bit more natural wind and movement to the first singing clip? audio sync is perfect."

- Measured: S1 v6_take_1 yaw range 0.027 and mouth-x range 4.7 px, against V3S v6_take_3's 0.067 and 16.1 px.
- `WC_VER=v6b` (`wc_takes.py` `P6B`, `WIND6B`): natural singer's nods and tilts, and a steady breeze through all of the
  hair. 8 takes ($14.80). Takes 4 and 8 were reframed; 5 and 6 slur the 'b'; take 7 is still stiff; take 1 has many
  blinks; take 3 blinks at the in-point.
- **Wired: `v6b_take_2`**, yaw 0.129, x 35 px, hair motion about 2x v6. Lag +0.95 (`SYNC_V6B`), read by the 'b' release
  and the "fore" end, the markers that give v6_take_1 +1.11 against its wired +1.09. A.js
  `S1_SRC = media/sing/S1/v6b_t2_sync_1080_open.mp4`: the blink at 15.97-16.23 (file frames 81-86) patched from frame 80.
- Review: `deliverables/wip/sing_review.html` section "v6b" (side-by-side `sing_v6b_S1_vs_v6.mp4`, preview, ear tests
  `media/sing/review/v6b_S1_lag+{0.80,0.95,1.10}_*`).
- Weak: cheeks a little full with pressed lips at 13.45-13.55, on "night".
- Spend about $318.

## v7: both shots reshot from Jade's two new selfies, with a singer's expression (2026-10-18)

Jade: "reshoot the 2 singing clips ... the first clip using hairup with pencils and the second clip using hairdown ... a
natural amount of wind ... the normal amount of expression that you would expect from a singer in a music video." Full
report: `docs/revisions/v9/sing_v7.md`.

| Shot | Wired file | Take | Lag |
|---|---|---|---|
| S1 0:12.60-0:19.64 | A.js `media/sing/S1/v7_sync_1080_open.mp4` (hair up, pencils) | v7_take_1 (prompt P7) | +0.87 measured; blinks at file frames 0-6 and 82-89 patched |
| V3S 2:33.98-2:39.14 | E.js `media/sing/V3S/v7_sync_1080_open.mp4` (hair down) | v7_take_12 (prompt P7C, round 3) | -0.20 measured; partial blink at file frames 25-29 patched |

- The selfies are close-ups, so the shoulders, arms and lower chest were outpainted (nano-banana-pro;
  `tools/sing/v7_outpaint.py`). Every pixel the photos show is their own.
- S1 matte: BiRefNet, then `v5_pencils.py --ferrule`, then `v7_matte_fix.py` (the pencil bases, a plate sliver).
- Expression against v6: inner-brow range S1 0.46 against 0.18 (v6) and 0.25 (v6b); V3S 0.50 against 0.24.
- V3S needed three prompt rounds: "longing / haunted" gave a crying face on this photo. The pick asks for "confident,
  strong, urgent, a touch of longing".
- Review: `deliverables/wip/sing_review.html` section "Singing v7" (previews `sing_v7_{S1,V3S}_preview.mp4`,
  side-by-sides `sing_v7_{S1,V3S}_vs_v6.mp4`, ear tests `media/sing/review/v7_*_lag*`).
- Open: Jade picks the sync by ear. Then rebuild at her pick (`SYNC_V7`, `--name`), redo the eye patches, matte and
  pencil key, re-wire and re-render the preview.
- Renders need `FFMPEG` exported, or the preview prepare step cannot probe the new files.
- Spend +$42.17 (24 Seedance takes and 10 image fills); the project is at $360.36. `spend.py`'s cap is still $400.

## v8: "sultry" TEST round (2026-10-18; not wired, v7 stays in the film)

Kenton found v7 lacking something the watercolor had, and Jade asked for "some kind of sultry vibe?". Report:
`docs/revisions/v9/sing_v8.md`.

| Shot | Test file (not wired) | Take | Lag |
|---|---|---|---|
| S1 | `media/sing/S1/v8_sync_1080_open.mp4` | v8_take_4 | +0.80 measured; slow closes at file frames 29-37 and 59-69 patched |
| V3S | `media/sing/V3S/v8_sync_1080_open.mp4` | v8_take_3 | +0.45 measured; opening (0-14) and 74-83 patched |

- **New:** prompt `P8` (head turned and chin down, eyes up, brows low, half-lowered gaze, soft close-mic lips, a hint of
  smile in the eyes) and `tools/sing/v8_first.py` (face 0.30 of the frame height, wider shoulders, a local warm side
  light as a gain layer over her own pixels).
- **S1 alternative:** `v8t3_sync_1080_open.mp4`, more sultry but without the pink eraser. My first v8 S1 first frame had
  lost it in the matte; that is fixed now.
- **Review:** `deliverables/wip/sing_review.html` section "Singing v8 (sultry test)", with three-panel videos
  `sing_v8_{S1,V3S}_vs_v7_v4.mp4` (watercolor v4 | v7 | v8).
- **Open:** Jade compares and decides whether v8 replaces v7. If yes, set the ear-picked lag in `SYNC_V8`, rebuild,
  redo the eye patches, matte and pencil key, and wire as in sing_v8.md.
- **Spend:** v8 $18.35; the project is at $384.34.

## v9w: the warm watercolour stills animated with v8's acting (2026-10-18; TEST, not wired, v7 stays)

Jade: "i like warm watercolour warm light. can you animate those and let me see the lip sync". Report:
`docs/revisions/v9/sing_v9w.md`.

| Shot | Test file | Take | Lag |
|---|---|---|---|
| S1 | `media/sing/S1/v9w_sync_1080.mp4` (+ `_matte/`) | v9w_take_4 | +0.85 measured; no eye patch |
| V3S | `media/sing/V3S/v9w_sync_1080.mp4` (+ `_matte/`) | v9w_take_4_open (two lid-dips patched) | +0.15 measured |

- **Stills:** the hair fixed locally (`tools/sing/v9w_stills.py`; face pixels unchanged) and upscaled to 3072 wide.
- **Prompt `P9W`:** a painting that stays painted, a jaw lock, harder on eyes open.
- **S1 t4 has the steadiest jaw measured on any take**, v4 included.
- **Review:** `deliverables/wip/sing_review.html` section "Singing v9w", lip-sync clips first (composited over the plate,
  eye fixes in).
- **Open:** Jade picks the sync by ear and decides v7, v8 or v9w.
- **Spend:** $13.87; the project is at $398.21 of the $600 cap.

### v9w wired (2026-10-18)

Jade: "hair up: 0.7 is slightly better. the one you picked for hair down looks good. yes, wire them in."

| Shot | Wired file | Lag |
|---|---|---|
| S1 0:12.60-0:19.64 | A.js `media/sing/S1/v9w_sync_1080_l070_open.mp4` (matte `_open_matte/` -> `v9w_sync_1080_l070_matte/`) | +0.70, Jade's ear; blink at file frames 8-15 patched |
| V3S 2:33.98-2:39.14 | E.js `media/sing/V3S/v9w_sync_1080.mp4`, HER `v9w_sync_1080_matte/` | +0.15 |

- Previews: `deliverables/wip/sing_v9w_{S1,V3S}_wired_preview.mp4`. The v7 paths are in comments.
- `v9w_pencils.py` now template-matches both pencils (all 193 frames matched).
