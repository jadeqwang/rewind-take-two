# Singing shots v6: Jade's approved photo in both slots (S1, V3S), 2026-10-16

Jade approved `media/sing/selfie/selfie_r3b_pick.png`: her real face and light makeup, fuller hair worn down, the film's
jacket. Her direction: "let's just use the hair down in both". Both singing shots are rebuilt from it with one figure,
and only the plate behind her differs.

- **S1:** song 0:12.60-0:19.64 (f302-f471). She is on screen until the cutaway at 0:16.14 (f387), over `plate_close_1`.
- **V3S:** song 2:33.98-2:39.14 (f3696-f3819), over `plate_truth_1`.

Wired into A.js and E.js, with 540p previews and ear-test clips. Nothing is committed and no v5 or earlier file was
changed. Frame numbers are song frames (song s x 24) unless they say "file frame" (0 = the shot's in-point).

## Files for Jade

| What | File |
|---|---|
| S1 in the film (960x540, 0:12.00-0:21.00, v5coda mix) | `deliverables/wip/sing_v6_S1_preview.mp4` |
| V3S in the film (960x540, 2:33.50-2:39.60) | `deliverables/wip/sing_v6_V3S_preview.mp4` |
| S1 ear test (0:12.60-0:19.64, song under it) | `media/sing/review/v6_S1_lag+{0.79,0.94,1.09,1.24,1.39,1.54,1.69,1.99}_measured*.mp4` |
| V3S ear test (2:33.98-2:39.14) | `media/sing/review/v6_V3S_lag+{0.05,0.20,0.35,0.50}_measured*.mp4` |
| First frames against v5c / v5d, plus the mask and the bare plate | `media/sing/review/v6_first_vs_v5.jpg` |

The ear-test file names give the lag and its offset from the measurement. `_WIRED` marks the wired one. S1 has one extra
clip, `measured-0.30_extra`, for the reason given under "Sync".

## 1. First frames (`tools/sing/v6_first.py`, new; no paid call)

- **Matte:** BiRefNet (`WC_VER=v6 wc_comp.py matte`, giving `first/v6_her_alpha.png`). I checked it by eye over magenta,
  at full size, in four zooms: both shoulders, the lower left and the lower right.
  - The headboard behind her frame-left shoulder is gone, and so are both wall sconces, the ceiling fan and the bed.
  - The gaps between her arms and her body (bed, wood, floor) are keyed out on both sides.
  - Loose hairs at her frame-right shoulder are kept soft, and their edge colours are cleaned of the wall (v5's
    `decontaminate`).
  - Nothing of the room rides along.
- **Placement:** v5d's geometry. The figure is laid into the 2576x1449 crop at scale 1.130, face (landmarks 10-152)
  504.6 crop px, eyes at crop (1262, 575.5) = 1080p (941, 429), centred.
  - Measured on the composites, the face is 0.336-0.338 of the frame height. Against the photo's own landmarks it is
    0.348. The detector reads faces a little smaller over the plate; v5d had the same effect.
  - She runs off the bottom edge, where her span is crop x 591-1927.
- **Arms / outpaint:** none needed, so none done.
  - At this scale the frame's bottom edge is photo row 1281, and her arms only reach the photo's side borders at rows
    1359 (left) and 1372 (right), 80-90 rows below the frame.
  - So the frame needs no pixel the photo lacks. Every pixel of her is the photo's own, with no invented arm and no seam.
    The script asserts this.
  - Her arms are her real pose: upper arms hang slightly out from the body and go off the bottom edge at about 23 % and
    75 % of the frame width, nowhere near the lower corners. There is no straight cut line anywhere.
- **Outputs:**
  - `media/sing/first/v6_S1_first.jpg` and `v6_V3S_first.jpg`. The same figure, from one `v6_fig.jpg` and `v6_alpha.png`,
    so it is pixel-identical; only the plate differs.
  - `v6_her_mask_first_frame_{S1,V3S}.png` (identical), and `v6_{S1,V3S}_first.json`.
  - Contact sheet `media/sing/review/v6_first_vs_v5.jpg`.
  - Checked at full size on both plates: clean hair edges, no halo, collar and snaps intact, whole patch. The white shape
    beside her on the truth plate is the plate's own waterfall.

## 2. Takes (Seedance 2.5, 720p, avatar mode, the v4/v5 vocal slices and durations; tag `v6_sing_*`)

`tools/sing/wc_takes.py` now takes `WC_VER=v6`, with a new prompt `P6` and per-shot `V6` acting. The prompt says:

- she is a real, photographed person, the world stays black-ink engraving, and the two never blend;
- never painted, drawn or cartoonised;
- never smiles; tense and determined; eyes open; head keeps its angle; locked-off camera;
- her face exactly as in the first frame: same face shape and width, same eyes and eye size, nose, jaw, brows and skin,
  same light makeup; no beautifying, slimming, smoothing, ageing, restyling or eye enlargement;
- gunmetal-and-teal glasses stay on;
- long dark hair worn down, parted in the middle;
- collar with snaps, turtleneck, orange bands, blue disc and the 1420 MHz patch unchanged;
- no headphones.

Both prompts fit the 2000-character limit (S1 1948, V3S 1999).

| Take | Frame | Lag (look.py corr / events) | Verdict |
|---|---|---|---|
| S1 `v6_take_1` | 16:9 1280x720, 193 fr | corr +1.087 (r .54); open +1.075, 'b' +1.01, 'm' +1.11, end +1.23 (median +1.095); "my dissertation defense" 2 s windows +1.13..+1.30 (r .82-.99) | **pick**, wired at **+1.09** |
| S1 `v6_take_2` | 16:9, 193 fr | corr +0.90 (r .38); events drift +0.74 .. +1.15 | spare: lag drifts; blinks on "The" (~0:13.0), at ~0:16.25 and ~0:17.6 |
| V3S `v6_take_1` | **21:9 1470x630** | (+0.12) | **reject**: reframed |
| V3S `v6_take_2` | 16:9, 169 fr | corr -0.44 (r .47); events -0.26 / -0.42 / -0.73 / -0.21; windows -0.58 .. +1.48 | reject: unsteady; blinks ~2:35.6, ~2:37.1 |
| V3S `v6_take_3` (retake) | 16:9, 169 fr | corr +0.202 (r .58); open +0.33, 'b' -0.08, 'm' +0.14, end +0.25 (median +0.196) | **pick**, wired at **+0.20** |
| V3S `v6_take_4` (retake) | 16:9, 169 fr | corr +0.12 (r .49); events median +0.17 | spare: blinks right at the in-point (~2:33.9) and on "my" (~2:37.0-2:37.2) |

- **Identity:** no drift in any take. On the picks, measured at 720p against the first frame:
  - inter-ocular 131-133 px (first frame 133.4);
  - eye width 37.1-38.1 (37.9), so no eye enlargement;
  - face width 202-210 (205; it grows with an open mouth);
  - face height 239-256 (245).
  - By eye at 2x: her face, her light makeup, glasses on, hair down, collar and patch intact, never smiling.
  - Seedance placed her about 11 px left of the first frame at 720p (1.5 % of the width). The matte is per frame, so
    nothing depends on it.

## 3. Sync

**Finding (it explains last round's S1).** Correlating the mouth with the voice over "The night before" alone (0:13.05-0:14.95),
which is how v5c's +0.10 was measured, locks on the take's pre-roll mouthing:

- Re-measured now, `v5c_take_2` gives +0.11 over that window. Its "my dissertation defense" windows say **+1.21..+1.29**,
  and the whole take says +0.81.
- Jade's ear picked +0.90 for it.
- `v6_take_1` behaves the same: +0.03 over phrase 1 alone, +1.09 over the whole take, +1.13..+1.30 over phrase 2.

On a trace plot of `v6_take_1` at +1.09 (mouth gap against the vocal stem):

- The mouth opens on "The" at 0:13.10 (voice 0:13.15) and opens on "fore" 0:13.9-0:14.6.
- Phrase 2 lands almost exactly: the mouth opens at 0:16.30 against the voice at 0:16.25, and stops at 0:18.40 against
  0:18.40.
- At +0.03, the widest opening falls on the decaying end of "fore" (0:14.3), and there is no closure near the 'b'
  (voice dip 0:13.88).

So the S1 lag is the whole-take and event measurement, **+1.09**. That is consistent with Jade's +0.90 pick on the last
take.

- **S1 wired at +1.09** (`SYNC_V6`: knots (12.60, 0.79), (19.64, 7.83)).
  - Ear-test clips at measured -0.15 / +0.00 / +0.15 / +0.30 / +0.45 / +0.60 / +0.90 = lags +0.94 / +1.09 / +1.24 /
    +1.39 / +1.54 / +1.69 / +1.99, as asked.
  - Because the measurement now already includes the ~0.8 s that used to be missing, I added **+0.79 (measured -0.30)**
    as an extra. If the lips now sound early, that is the one to try.
  - The clips at +1.39 and beyond run past the take's end (8.04 s). Their last 0.09-0.69 s (from about 0:18.95 on) is
    the take's last frame held. In the film that time is on the cutaway.
- **V3S wired at +0.20** (knots (153.98, 0.50), (159.14, 5.66)).
  - On the trace, the 'm' of "my" closes at 2:37.0-2:37.2, and the mouth falls with the voice at about 2:39.3.
  - Ear-test clips at measured -0.15 / +0.00 / +0.15 / +0.30 = +0.05 / +0.20 / +0.35 / +0.50.
- Both synced files are untouched frames at rate 1 (no cross-fades): `media/sing/S1/v6_sync_1080.mp4` (174 frames) and
  `media/sing/V3S/v6_sync_1080.mp4` (133 frames).

## 4. Eyes (stepped frame by frame, `tools/sing/v6_eyes.py`, new; openness relative to the clip's open level)

**S1** (`v6_sync_1080.mp4`, file frame = song frame - 302):
- **0:12.60-0:16.14 (f302-f386, file frames 0-84), everything on screen:** no blink, no droop.
  - Openness is 0.88-1.00 on every frame, and 0.97 at the in-point.
  - The whole Bean wide opening, 0:12.60-0:13.92, is open-eyed.
  - The lowest is 0.88 at 0:13.72 (f329), checked by eye: open.
- **Full blink at 0:19.31-0:19.48 (f463-f466, file frames 161-164):** lids at 0.11 / 0.15 / 0.22 / 0.62. This is after
  the cutaway (0:16.14). The film never shows S1 after that, so it is left alone.
- **No noblink patch, so no `_open` file.**

**V3S** (`v6_sync_1080.mp4`, file frame = song frame - 3696):
- **2:33.98 (f3696, file frame 0):** 0.83, rising to 0.89 / 0.90 / 0.91 over f3697-f3699.
  - This is the last lift of a blink the take makes at about 2:33.75-2:33.90, before the in-point, so it is not shown.
  - By eye at 2x it reads as open; the lids are a hair lower on the cut-in frame only. It isn't a half-blink, since it
    doesn't sink and hang.
  - Left untouched.
- **2:34.02-2:39.14 (f3697-f3819):** no blink and no droop; 0.88-1.04 throughout.
  - On "my", 2:37.19-2:37.40 (f3773-f3778), 0.89-0.91, open. This is where v5b's half-blink was.

## 5. Matte and wiring

- **Per-frame BiRefNet mattes:**
  - `media/sing/S1/v6_sync_1080_matte/` (174 PNG + `fps.txt`)
  - `media/sing/V3S/v6_sync_1080_matte/` (133 PNG + `fps.txt`)
  - Checked over magenta at S1 file frames 0, 40, 84 and V3S 0, 60, 120: whole figure, hair edges clean, no plate
    pieces.
  - No pencil key any more. No `_open` variant, so no symlink is needed.
  - A.js derives `S1_MATTE` = `media/sing/S1/v6_sync_1080_matte/` from `S1_SRC`.
- **`render/timeline/A.js`:** `S1_SRC = 'media/sing/S1/v6_sync_1080.mp4'`. The v5c +0.90 path is in the comment above
  it and in the `A_S1_lyric` HER comment.
- **`render/timeline/E.js`:** `V3S_SRC = 'media/sing/V3S/v6_sync_1080.mp4'`, and the `V3S_lyric` HER matte is
  `media/sing/V3S/v6_sync_1080_matte/`. The v5d paths are in comments.
- Both modules import cleanly. The preview prepare step picked up all four v6 media.

## 6. Previews (960x540, my shell)

`deliverables/wip/sing_v6_S1_preview.mp4` (12.0-21.0) and `deliverables/wip/sing_v6_V3S_preview.mp4` (153.5-159.6),
both with the v5coda mix.

**S1 stills:** 0:12.62, 0:12.90, 0:13.25, 0:13.60, 0:13.95, 0:14.30, 0:14.80, 0:15.60, 0:16.10.
- **In the Bean wide (0:12.62-0:13.25)** she sits small at bottom centre, about the size she was in v5d. Eyes open, no
  furniture, matte edge clean. Both arms run off the bottom edge with no cut line (zoomed at 0:12.62).
- **The mouth** is open on "The" at 0:13.25 (f318) and rounded on "fore" at 0:13.95 / 0:14.30 (f335 / f343).
- **Arc lyric** "THE NIGHT BEFORE" sits clear of her head.
- **Collar, snaps, blue disc and the 1420 MHz patch** are readable in every still.

**V3S stills:** 2:33.99, 2:34.40, 2:34.90, 2:35.90, 2:36.80, 2:37.15, 2:37.60 (cutaway), 2:38.30, 2:39.00.
- **The mouth** is open on "night" at 2:34.40 (f3706), rounded on "fore" at 2:34.90, and closed for the 'm' of "my" at
  2:37.15 (f3772).
- **"DEFENSE"** fades in beside her hair at 2:38.30, as it did in v5d, and doesn't touch her.
- **Patch and collar** are intact, and no straight edges show.

## What is weak (honest list)

- **Lip sync is measured, not heard.** For S1 the method changed (see "Sync"), so +1.09 is a new kind of number. It
  agrees with Jade's ear on the last take, but please judge the S1 brackets, including the extra +0.79.
- **The S1 lag rests on the whole take.** S1 is on screen only for "The night before", and over that phrase alone
  correlation is weak at any lag near 1 s (r .28). The S1 lag rests on the whole take, the lip events (+1.01..+1.08 on
  phrase 1) and phrase 2, which plays under the cutaway.
- **S1 pre-roll.** At the in-point, 0:12.60 (f302), her lips are slightly parted (gap 0.048 against a sung peak of
  0.10). They close to 0.02 by 0:12.85 (f308), then open for "The" at 0:13.14. This happens while she is small in the
  wide.
- **S1 silence (0:15.27-0:15.93, f366-f382).** Her lips hold slightly parted (0.035-0.039) while the voice is silent.
  She isn't mouthing words, but her mouth isn't shut either.
- **V3S cut-in.** The lids on frame 0 (2:33.98) are slightly lower (0.83) than from frame 2 on.
- **Resolution.** The takes are 720p upscaled to 1080p, so the skin is softer than the photo.
- **Measured face size.** 33.6 % of the frame height on the composites, against v5d's 34.8 % by the same measure on the
  photo. It is the same placement, read differently by the detector.
- **Approved-photo flaws, both outside the frame.** The photo has a faint horizontal tone step at photo row ~1355 and a
  teal fleck at about (980, 1360). Both are below the frame's bottom edge (photo row 1281), so neither is visible.
- **Step 1 deviation.** No outpaint was needed or done, because the photo covers everything the frame shows.

## Spend

Seedance 2.5 720p, 6 calls:

| Shot | Calls | Spend |
|---|---|---|
| S1 | 2 x 8 s | $3.70 |
| V3S | 4 x 7 s (2 retakes after the 21:9 take) | $6.47 |
| **Total** | 6 | **$10.17** |

- Project estimate went from $293.23 to **$303.40** (`spend.total()`).
- Mattes, first frames, sync, eye checks and previews are local and free.
- `media/genlog.jsonl` has two lines per job (submit and collect), so a plain sum of its `v6_sing_*` lines reads $20.35.
  The real figure is $10.17.

## Files touched

- **New:** `tools/sing/v6_first.py`, `tools/sing/v6_eyes.py`, `tools/sing/v6_lagwin.py`.
- **Extended:**
  - `tools/sing/wc_takes.py` (`WC_VER=v6`: `P6`, `V6`, tag `v6_sing_*`)
  - `tools/sing/wc_post.py` (`SYNC_V6`)
- **Rewired:** `render/timeline/A.js` (S1), `render/timeline/E.js` (V3S).
- **Notes:** `media/sing/NOTES.md` "# v6".
- **New media (all `v6_`):**
  - `media/sing/first/v6_*`
  - `media/sing/{S1,V3S}/v6_take_*`, `v6_first_2048.jpg`, `v6_sync_1080.mp4` and `_matte/`
  - `media/sing/review/v6_*`
  - `deliverables/wip/sing_v6_*_preview.mp4`

## Rebuild

```
EPY=tools/engrave/.venv/bin/python; MPY=~/Documents/1-music-shipped/orbital-sunrise-video/video/out/.venv/bin/python
PY=~/Documents/1-music-shipped/moongazing/.venv/bin/python
export FFMPEG=~/Documents/1-music-shipped/moongazing/.venv/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2
export FACE_LANDMARKER=~/Documents/1-music-shipped/moongazing/tools/sync/models/face_landmarker.task
WC_VER=v6 $EPY tools/sing/wc_comp.py matte media/sing/selfie/selfie_r3b_pick.png
$MPY tools/sing/v6_first.py comp; $MPY tools/sing/v6_first.py sheet
WC_VER=v6 $PY tools/sing/wc_takes.py submit S1 V3S --n=2; WC_VER=v6 $PY tools/sing/wc_takes.py wait S1 V3S
$MPY tools/sing/look.py S1 v6_take_1; $MPY tools/sing/v6_lagwin.py S1 v6_take_1 13.05 18.40     (same for V3S v6_take_3)
WC_VER=v6 $PY tools/sing/wc_post.py sync S1; WC_VER=v6 $PY tools/sing/wc_post.py sync V3S
$MPY tools/sing/v6_eyes.py media/sing/S1/v6_sync_1080.mp4 12.60; $MPY tools/sing/v6_eyes.py media/sing/V3S/v6_sync_1080.mp4 153.98
WC_VER=v6 $EPY tools/sing/wc_post.py matte S1 v6_sync_1080; WC_VER=v6 $EPY tools/sing/wc_post.py matte V3S v6_sync_1080
WC_VER=v6 $PY tools/sing/wc_post.py review S1 v6_take_1 1.09 media/sing/review/v6_S1_lag+1.09_measured+0.00_WIRED.mp4 --audio=media/sfx/Rewind_cinematic_sfx_mix_v5coda.mp3
node render/engine/render.mjs --preview --force --range 12.0 21.0 --encode --audio media/sfx/Rewind_cinematic_sfx_mix_v5coda.mp3 --out deliverables/wip/sing_v6_S1_preview.mp4
```
