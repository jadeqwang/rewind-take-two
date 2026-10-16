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
