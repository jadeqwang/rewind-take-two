# Singing shots v7: Jade's two new selfies, a singer's expression (S1, V3S), 2026-10-18

Jade (2026-10-18): "we now have new selfies in the /inputs folder. can you reshoot the 2 singing clips ... the first clip
using hairup with pencils and the second clip using hairdown. please use a natural amount of wind for hair movement, and
the normal amount of expression that you would expect from a singer in a music video. I think some of the shortcomings of
previous versions came from a lack of expression."

- **S1:** song 0:12.60-0:19.64 (f302-f471), from `inputs/selfie_hairup_jade_jacket_retouch_v2.png` (hair up, pink and
  pale-blue pencils), over `plate_close_1`. She is on screen until the cutaway at 0:16.14 (f387).
- **V3S:** song 2:33.98-2:39.14 (f3696-f3819), from `inputs/selfie_hairdown_jade_jacket_retouch_v2.png`, over
  `plate_truth_1`. The cutaway is 2:37.39-2:37.84.

Both are wired into A.js and E.js, with 540p previews, side-by-sides and ear-test clips. Nothing is committed and no v6
or earlier file was changed. Frame numbers are song frames (song s x 24) unless they say "file frame" (0 = the shot's
in-point).

## Files for Jade

| What | File |
|---|---|
| Review page (section "Singing v7", at the top) | `deliverables/wip/sing_review.html` |
| S1 in the film (960x540, 0:12.00-0:21.00, v5coda mix) | `deliverables/wip/sing_v7_S1_preview.mp4` |
| V3S in the film (960x540, 2:33.50-2:39.60) | `deliverables/wip/sing_v7_V3S_preview.mp4` |
| Before / after (left: currently wired v6b / v6; right: v7) | `deliverables/wip/sing_v7_{S1,V3S}_vs_v6.mp4` |
| S1 ear test (0:12.60-0:19.64, song under it) | `media/sing/review/v7_S1_lag+{0.42,0.57,0.72,0.87,1.02,1.17,1.32}_measured*.mp4` |
| V3S ear test (2:33.98-2:39.14) | `media/sing/review/v7_V3S_lag{-0.35,-0.20,-0.05,+0.10}_measured*.mp4` |
| First frames against v6, plus the v7 masks | `media/sing/review/v7_first_vs_v6.jpg` |
| Shoulder fills tried (model output and merge) | `media/sing/outpaint/v7/contact_sheet.jpg` |

`_WIRED` marks the wired lag. The ear-test clips are the raw take, so the blinks painted out in the film still show in
them.

## 1. First frames (`tools/sing/v7_outpaint.py`, `tools/sing/v7_first.py`, new)

**The photos do not cover the frame.** Both selfies are 1086x1448 close-ups. At v6's placement (face, landmarks 10-152,
504.6 crop px; eyes at crop (1262, 575)):
- S1 is scaled 0.856, and the frame spans photo x -887..2124 and rows 49..1743.
- V3S is scaled 0.964, and the frame spans photo x -692..1982 and rows 72..1576.
- So the photo is only the middle third of the frame. Her shoulders, upper arms and lower chest past the photo's left,
  right and bottom edges had to be **outpainted**.

**Outpaint (the v5_outpaint approach).**
- The photo goes on a 2400x1800 grey canvas (photo at x 657, its top at the canvas top) and the model continues it "as
  if the camera had been further back". The prompt keeps the room, the jacket's bands, epaulets and snaps, and completes
  the 1420 MHz patch.
- Tried for S1: nano-banana-pro x3 and gpt-image-2.5-flare x1. For V3S: nano-banana-pro x5 and gpt x1.
- Rejected:
  - gpt redraws the whole picture, so pasting the photo back doubles the patch.
  - S1_nbp_1 and nbp_3 add extra orange stripes.
  - V3S_nbp_1 and nbp_4 leave a grey bar and cut her arm.
  - V3S_nbp_2 tiles extra copies of her.
  - V3S_nbp_3 adds a second, oversized patch.
- **Used: `S1_nbp_2`, `V3S_nbp_5`.**
- **Merge.** Every pixel the photo shows is pasted back: face, hair, flyaways, pencils, glasses, collar, disc.
  - Below the shoulders the hand-over sits ~100 px inside the photo's side edges, so the band ends and the photo's
    half-patch come whole from the model's continuous jacket. Above the shoulders and along the bottom it is ~25 px.
  - Near the hand-over the model's fill is aligned to the photo by local optical flow, and it gets a clamped
    low-frequency colour match.
  - Face landmark drift of the model's output is 2.6 px mean (S1) and 1.4 px (V3S). The hand-over difference is 4.3 and
    5.2 (mean max-channel, /255).
  - Checked at full size: no doubled patch, no ghosted disc or collar tip, no pale band edge.

**Matte.** BiRefNet on the merged canvas (`WC_VER=v7S1` / `v7V3S` `wc_comp.py matte`), then v5's `decontaminate`.
- **S1:** both pencils survive whole (erasers, ferrules, yellow bodies), with no wall between strands.
  - Over magenta at full size the flyaways read as dark strands.
  - The faintest, longest wisps of the photo (the arcs high above the bun) are dropped.
- **V3S:** BiRefNet kept the white door trim behind her hair, left of her head (photo x ~325-345, rows ~430-700), at
  alpha 0.7-1.0.
  - It isn't the wall's colour, so decontamination couldn't clean it.
  - A local luminance key (`v7_first.py` `trim_key`, only inside that box) removes it. Checked over magenta and over the
    plate.

**Placement.**
- S1: face 0.353 of the frame height, eyes at 1080p (941.5, 429.6).
- V3S: face 0.351, eyes at (940.0, 428.5). The same as v6's (941, 429).
- A guard asserts the figure never meets the canvas border inside the frame.
- She runs off the bottom edge across crop x 697-1865 (S1) and 526-1770 (V3S); v6 was 591-1927. The selfie's
  perspective gives her narrower shoulders than the old photo.

**Outputs:**
- `media/sing/first/v7_{S1,V3S}_first.jpg`, `v7_her_mask_first_frame_{S1,V3S}.png`, `v7_{S1,V3S}_fig.jpg` / `_alpha.png`
  and `.json`.
- `review/v7_first_vs_v6.jpg` and `review/v7_first_magenta_{S1,V3S}.jpg`.

## 2. Prompts (`tools/sing/wc_takes.py`, `WC_VER=v7`; v5 / v6 / v6b prompts unchanged, lengths re-checked)

**Kept from P6/P6B:**
- the photographic woman against the ink world, never blending;
- the face lock (same face shape and width, eye size, nose, jaw, brows, skin, light makeup; never beautify, slim, smooth
  or enlarge her eyes);
- glasses on;
- jacket, collar and snaps, turtleneck, bands, disc and patch unchanged;
- no headphones; locked-off camera framed as the first frame; no new text.

**Per-shot hair and wind:**
- S1: a loose messy bun with the two pencils (pink at the picture's left, pale-blue at the right) staying exactly in
  place. A natural light breeze moves the loose strands and flyaways around the bun and temples; the bun and pencils
  stay put.
- V3S: long dark hair down, parted in the middle, swaying gently through all of the hair.

**Removed:** "never smiles", "brows relaxed, no frown", "head keeps its angle".

There were three rounds of expression prompt, because Seedance overacted.

| Round | Prompt | What it asked | Result |
|---|---|---|---|
| 1 | `P7` (S1 1998 / V3S 1867 chars) | Jade's brief nearly verbatim: a music-video singer, emotionally invested, singing with her whole face. Brows lift and knit with the phrasing, eyes alive on the camera, cheeks and jaw working, mouth wide on open vowels, nods / tilts / turns, breath in the shoulders. Urgent, longing, a little haunted; no beaming grin, no mugging | S1 take 1 good. **V3S all overacted:** tearful knitted brows throughout, a wide shout on "night", bared teeth, eyes shut 0.7-1.3 s |
| 2 | `P7B` (`WC_V7R=2`; 1991 / 1860) | the same, "but composed"; brows "draw together naturally"; names crying, pained, grinning, grimacing and bared teeth as don'ts; only quick full blinks | V3S still near-crying (the hair-down photo's resting face, inner brows a little up and lips parted, plus "longing / haunted"). S1: grins in t6 |
| 3 | `P7C` (`WC_V7R=3`, V3S only, 1876) | "a confident singer ... strong, sure and urgent, with a touch of longing, never sad, tearful or pained"; brows lift with the phrasing and relax between phrases; eyes bright on the camera | V3S t12: expressive and composed. **Picked** |

The V3S pick's emotion is one step away from Jade's words: less "haunted", more "urgent and strong". That was the only
way I found to stop the take from crying.

## 3. Takes (Seedance 2.5, 720p, avatar mode, the v4-v6 vocal slices and durations; tags `v7_sing_*`)

Expression is measured with `tools/sing/v7_expr.py` (new; MediaPipe blendshapes plus geometry over the whole take,
p95-p5 ranges):
- brInUp = browInnerUp range;
- lift = geometric brow-to-eye distance / inter-ocular, range;
- jaw95 = jawOpen p95;
- roll = head roll range in degrees.

Lags: look.py corr (r) / events (open, 'b', 'm', end) / v6_lagwin 2 s windows.

**S1** (the baselines are v6_take_1: brInUp .18, lift .017, jaw95 .18, roll 1.1°, yaw .013; and v6b_take_2: .25 / .048
/ .31 / 2.9° / .065)

| Take | Frame | Lag | Expression | Verdict |
|---|---|---|---|---|
| `v7_take_1` (r1) | 16:9 | corr +0.869 (r .57); events +0.83/+0.80/+0.74/+1.03; windows from 13.9 on +0.88..+0.97 (r .50-.89) | brInUp .46, lift .066, jaw95 .38, roll 5.6°, yaw .127 | **pick, +0.87** |
| `v7_take_2` (r1) | 16:9 | +0.52, windows drift +0.37..+1.15 | .50 / .076 / .30 / 3.3° | reject: beaming open-mouthed grin on "night" (clip 1.0 s) |
| `v7_take_3` (r1) | **21:9 1470x630** | - | - | reject: reframed |
| `v7_take_4` (r1) | 16:9 | +0.55, windows +1.13 → +0.22 → +1.00 | .53 / .076 / .29 / 1.2° | reject: lag unsteady |
| `v7_take_5` (r2) | 16:9 | +1.01, windows +0.18..+1.35 | .50 / .062 / .36 / 4.5° | reject: lag drifts; blinks at the in-point and at 14.27 |
| `v7_take_6` (r2) | 16:9 | +0.67, windows +0.24..+1.38 | .51 / .050 / .43 / 2.2° | reject: grins at 16.73-17.23 |
| `v7_take_7` (r2) | 16:9 | +0.31, windows drift | .55 / .054 / .31 / 6.5° | reject: eyes shut 16.88-17.84 |
| `v7_take_8` (r2) | 16:9 | corr +1.03 (r .56); events +0.74/+1.26/+0.74/+0.86; phrase-1 windows +0.41..+0.98, phrase-2 +0.79..+0.98 | .53 / .058 / .35 / 2.0° | **spare**: lag inconsistent in phrase 1; less head movement |

**V3S** (the baseline is v6_take_3: brInUp .24, brOutUp .28, lift .039, jaw95 .20, roll 2.5°, yaw .048)

| Take | Frame | Lag | Verdict |
|---|---|---|---|
| `v7_take_1`-`4` (r1) | 16:9 | t4 the steadiest (+0.57..+0.66); the others unsteady | reject: overacted (shout at ~2:34.3 in t1 and t4, bared teeth 2:37.40-2:38.15 in t4), eyes shut 0.7-1.3 s (t2, t3), 4+ blinks |
| `v7_take_5`-`9` (r2) | 16:9 | mostly drifting | reject: near-crying face; eyes shut or hanging at 0.6-0.7 for 0.6-1.6 s (t5 2:36.95, t6 2:37.15-2:38.73, t7 2:37.33-2:38.21, t9 2:37.56-2:38.48); t8 io +2.8 %, lag +1.39 |
| `v7_take_10` (r2) | **21:9** | - | reject: reframed |
| `v7_take_11` (r3) | 16:9 | windows -0.51..+1.48 | reject: unsteady, 5 blinks |
| `v7_take_12` (r3) | 16:9 | corr -0.152 (r .60); events -0.30/-0.21/-0.27/-0.13 (median -0.24); windows from 155.2 on -0.13..-0.20 (r .47-.89) | **pick, -0.20**. brInUp .50, brOutUp .58, lift .061, jaw95 .28, roll 2.1°, yaw .038 |
| `v7_take_13`, `15`, `16` (r3) | 16:9 | drifting | reject: 5-8 blinks each; t15 inter-ocular 128.8 against 135.2 (-4.7 %) |
| `v7_take_14` (r3) | 16:9 | corr +0.34 (r .48); windows +0.26..+0.68 | **spare**: composed and expressive, but the lag drifts; blinks 2:34.06, 2:34.77 |

**Identity** (720p, against the start image at the same size):
- **S1 `v7_take_1`:** inter-ocular 136.4 (first frame 133.0), eye width 40.5 (39.7), face width 203.8 (200.2).
  - Everything is ~2 % larger together because she leans toward the camera (face height 241-281 px).
  - Eye width / inter-ocular is 0.297 against the first frame's 0.298, so there is no eye enlargement.
- **V3S `v7_take_12`:** inter-ocular 136.7 (135.2), eye width 40.0 (40.0), face width 214.0 (207.3; it grows with an open
  mouth).
- By eye at 2x: her face, glasses on, collar, snaps, disc and patch intact in both; no beautifying.

**What changed against v6 (the numbers):**
- **S1:** inner-brow range 2.5x v6_take_1 and 1.9x v6b; brow lift 3.9x and 1.4x; jaw p95 2.1x and 1.2x; head roll 5.6°
  against 1.1° / 2.9°.
- **V3S:** inner-brow range 2.1x v6_take_3, outer brow 2.1x, brow lift 1.6x, jaw p95 1.4x.
  - V3S head movement is about the same as v6_take_3 (roll 2.1° against 2.5°, yaw .038 against .048). The extra life is
    in the face, not the head.

**Pencils (S1).** Checked at 2x on file frames 0-180 of the take: both stay in the bun with their colours. At file frames
40 and 120 the pink pencil's yellow body is hidden in her hair as her head tilts.

## 4. Sync

**S1, wired at +0.87** (`SYNC_V7`: knots (12.60, 0.57), (19.64, 7.61); `media/sing/S1/v7_sync_1080.mp4`, 179 frames,
untouched).
- Trace (`tools/sing/v7_trace.py`, new): at +0.87 the mouth opens on "The" at 0:13.20 (voice 13.15-13.20).
- The release of the 'b' closure into "fore" lands at 0:13.88-0:13.90, exactly where the voice comes back after its dip
  at 0:13.88. At +0.80 it is late (13.95); at +0.95 it comes before the dip (13.80).
- Phrase 2 (under the cutaway) says +0.92..+0.97.
- Ear tests at +0.42 / +0.57 / +0.72 / **+0.87** / +1.02 / +1.17 / +1.32 (measured -0.45..+0.45), as asked. S1
  measurements have run short of Jade's ear before, so the later-lips side (+1.02..+1.32) is there to try.

**V3S, wired at -0.20** (knots (153.98, 0.10), (159.14, 5.26); `media/sing/V3S/v7_sync_1080.mp4`, 133 frames,
untouched).
- The take's mouth runs slightly **early**, which is new (v6 was +0.20).
- At -0.20 the 'b' closure sits on 2:34.72, the 'm' of "my" releases at ~2:37.17 (voice ~2:37.15), and the mouth falls
  with the phrase end at 2:39.14. -0.30 is late on the 'b'; -0.10 is early.
- Ear tests at -0.35 / **-0.20** / -0.05 / +0.10 (measured -0.15..+0.30).

## 5. Eyes (`tools/sing/v6_eyes.py` over the on-screen span, then `v4_noblink.py`)

**S1** (`v7_sync_1080.mp4`, file frame = song frame - 302):
- **Full blink at the in-point:** 0:12.60-0:12.81 (f302-f306, file frames 0-4), lids 0.26-0.39. Patched open on file
  frames 0-6 from frame 8 (openness 0.93), fading back over frames 5-6. She is small in the Bean wide here.
- **Full blink at the cutaway:** 0:16.02-0:16.23 (f384-f388, file frames 82-86), lids 0.19-0.32. The cut is at file
  frame 85. Patched on frames 82-89 from frame 81 (0.91), as v6b was.
- After patching: open on every on-screen frame (0.89-1.00).
- Checked at 2x (`media/sing/S1/v7_sync_1080_open_check{,_inpoint}.jpg`): eyes open, no ghosting, brows untouched.
- The take's full blink at 0:19.68 (f472) comes after the cutaway and is never shown.
- File: `media/sing/S1/v7_sync_1080_open.mp4`. Two passes; the first pass is in the scratchpad only.

**V3S** (`v7_sync_1080.mp4`, file frame = song frame - 3696):
- **2:35.10-2:35.19 (f3723-f3724, file frames 27-28):** a quick partial blink, lids to 0.55 for two frames. It doesn't
  hang, but it is a partial lid, so it is patched on file frames 25-29 from frame 24 (0.90). Checked at 2x:
  `media/sing/V3S/v7_sync_1080_open_check.jpg`.
- **2:38.31-2:38.44 (f3800-f3802, file frames 104-106):** a natural full blink (lids shut on two frames). Kept.
- The cut-in frame 2:33.98 is 0.96. The rest is open (0.82-1.00).
- File: `media/sing/V3S/v7_sync_1080_open.mp4`.

## 6. Matte and wiring

**S1:** `media/sing/S1/v7_sync_1080_open_matte/` (179 PNG + `fps.txt`), built in three steps.
1. BiRefNet per frame (originals in `_matte_birefnet/`).
2. `v5_pencils.py --ferrule` (new opt-in flag; v5 behaviour unchanged without it; the keyed set is in `_matte_pencils/`).
   With the flag, an eraser whose yellow body is hidden in her hair is joined to the nearest hair. Without it the pink
   eraser floated free of her head at file frame 30.
3. `tools/sing/v7_matte_fix.py` (new), which:
   - extends the pale-blue pencil along its own axis into the see-through bun hair BiRefNet drops. Without it the pencil
     hovered 3-9 px above her hair in ~100 frames (file frames 0-14, 53-89, 115-123, 147-165, 174);
   - removes a white sliver of the plate's tower that rode along at her right temple (file frames 30-34).

Checked over magenta at file frames 0, 8, 28-40, 60, 84, 120, 140 and 147 at full size:
- both pencils whole and attached;
- flyaways as dark strands;
- no plate pieces, except a faint pale fringe along the hair at frame 32.

**V3S:** `media/sing/V3S/v7_sync_1080_open_matte/` (133 PNG + `fps.txt`, BiRefNet). Checked over magenta at file frames
0, 40, 80 and 120: the whole figure, clean hair edges, no plate.

**Wiring:**
- `render/timeline/A.js`: `S1_SRC = 'media/sing/S1/v7_sync_1080_open.mp4'`. S1_MATTE is derived as
  `..._open_matte/`. The v6b path is in the comment above it and in the `A_S1_lyric` HER comment.
- `render/timeline/E.js`: `V3S_SRC = 'media/sing/V3S/v7_sync_1080_open.mp4'`, and the `V3S_lyric` HER matte is
  `media/sing/V3S/v7_sync_1080_open_matte/`. The v6 paths are in comments.
- Both modules import cleanly. The preview's prepare step picked up the v7 media.

## 7. Previews (960x540, my shell; `FFMPEG` must be exported or the renderer cannot probe the new files)

**S1 stills:** 0:12.62, 0:12.90, 0:13.25, 0:13.60, 0:13.95, 0:14.30, 0:14.80, 0:15.60, 0:16.10.
- In the Bean wide she sits small at bottom centre, eyes open, both pencil tips visible.
- Mouth open on "The" at 0:13.25 (f318), rounded on "fore" at 0:13.95 / 0:14.30 (f335 / f343).
- Brows lifted on "night".
- "THE NIGHT BEFORE" sits clear of her head.
- Collar, snaps, disc and the 1420 MHz patch are readable in every still.

**V3S stills:** 2:33.99, 2:34.40, 2:34.90, 2:35.90, 2:36.80, 2:37.15, 2:37.60 (cutaway), 2:38.30, 2:39.00.
- Mouth open on "night" at 2:34.40 (f3706), lips closed for the 'm' of "my" at 2:37.15 (f3772).
- "DISSERTATION DEFENSE" clear of her hair.
- 2:38.30 catches the start of the kept natural blink.

## What is weak (honest list)

- **Lip sync is measured, not heard.**
  - S1 +0.87 rests on the 'b' release and the phrase-2 windows. The open, 'b' and 'm' events alone say +0.81, the
    windows say +0.93.
  - V3S's -0.20 is the first negative lag on this shot.
  - Please judge the brackets.
- **The emotion moved off Jade's words for V3S.** Two rounds with "longing / a little haunted" gave a near-crying face on
  this photo every time. The pick (round 3) asks for "confident, strong, urgent, a touch of longing". It is expressive,
  but less haunted than the brief.
- **V3S head movement is not bigger than v6's.** Roll range 2.1° against v6_take_3's 2.5°, yaw .038 against .048. The
  added life is in the brows, eyes and jaw. Its hair sways but moves less than S1's flyaways.
- **The shoulders, arms and lower chest are invented** by nano-banana-pro (outside photo x 0..1086 and below photo row
  1448). That is roughly the outer third of the jacket on each side, and the bottom of the frame in S1. The 1420 MHz
  patch is the model's completion of the photo's cut-off patch. Her shoulders are narrower than in v6 (the selfie's
  perspective).
- **S1 bun and flyaways.**
  - Seedance turns the photo's spiky bun into a smaller tuft.
  - The matte drops the faintest flyaways above it.
  - The pale-blue pencil's base is a synthetic matte stroke (`v7_matte_fix.py`) in ~100 frames, not BiRefNet's. It is
    invisible at 540p.
  - A faint pale fringe at her right temple on file frame 32 (0:13.93, f334).
- **S1 eye patches.**
  - File frames 0-6: 0:12.60-0:12.85, f302-f308, in the Bean wide.
  - File frames 82-89: 0:16.02-0:16.35, f384-f391, across the cutaway at f387.
  - Both are painted eyes from a neighbouring frame, clean at 2x.
- **S1 leans in.** Her face height runs 241-281 px at 720p, so she drifts toward the camera by up to ~10 % during the take.
- **S1 phrase 2 (under the cutaway, never on screen):** she knits her brows hard and pleads at 0:16.84-0:17.84.
- **V3S hair sheen.** A lighter grey strand area in her hair beside her frame-left temple, from 2:33.98 on (file frame 0
  on). It comes from the door trim seen through her hair in the photo: I keyed it out of the first frame, but Seedance
  still paints a lighter streak there. It reads as sheen, but it is there.
- **V3S eye patch** at 2:35.10-2:35.19 (f3723-f3724, file frames 25-29), painted from file frame 24.
- **Brows knit briefly** on "before" in V3S at 2:35.25-2:35.50 (f3726-f3732). That's natural phrasing, not a frown hold.
- **Resolution:** 720p takes upscaled to 1080p, so the skin is softer than the photos.
- **Takes:** 24 Seedance takes (8 S1, 16 V3S), two of them reframed 21:9. The V3S hit rate was 1 in 16.

## Spend

| Item | Calls | Spend |
|---|---|---|
| S1 Seedance 2.5 720p, 8 s | 8 | $14.80 |
| V3S Seedance 2.5 720p, 7 s | 16 | $25.89 |
| Shoulder fills (nano-banana-pro x 8, gpt-image-2.5-flare x 2) | 10 | $1.48 |
| **Total** | 34 | **$42.17** |

- Project estimate: $318.20 → **$360.36** (`spend.total()`).
- `media/genlog.jsonl` has two lines per Seedance job (submit and collect), so a plain sum of its `v7_sing_*` lines reads
  $82.86. The real figure is $42.17.
- `spend.py` still defaults to a $400 cap ($39.64 of headroom left). Jade lifted the budget, so set `REWIND_CAP` before
  further rounds.

## Files touched

- **New:**
  - `tools/sing/v7_outpaint.py`, `v7_first.py`, `v7_expr.py`, `v7_trace.py`, `v7_matte_fix.py`
- **Extended:**
  - `tools/sing/wc_takes.py`: `WC_VER=v7`, `P7` / `V7` / `LINE7`, `P7B` (`WC_V7R=2`), `P7C` (`WC_V7R=3`), tags
    `v7_sing_*[_r2|_r3]`, the v7 key in the `LOOK` lookup.
  - `tools/sing/wc_post.py`: `SYNC_V7`.
  - `tools/sing/v5_pencils.py`: `--ferrule`, opt-in.
- **Rewired:** `render/timeline/A.js` (S1), `render/timeline/E.js` (V3S).
- **Pages and notes:** `deliverables/wip/sing_review.html` (section "v7" at the top), `docs/revisions/v9/SING_STATE.md`
  ("v7"), `media/sing/NOTES.md` ("# v7").
- **New media (all `v7`):**
  - `media/sing/outpaint/v7/`
  - `media/sing/first/v7*`
  - `media/sing/{S1,V3S}/v7_take_*`, `v7_first_2048.jpg`, `v7_sync_1080{,_open}.mp4`, `v7_sync_1080_open_matte*/`
  - `media/sing/review/v7_*`
  - `deliverables/wip/sing_v7_*`

## Rebuild

```
EPY=tools/engrave/.venv/bin/python; MPY=~/Documents/1-music-shipped/orbital-sunrise-video/video/out/.venv/bin/python
PY=~/Documents/1-music-shipped/moongazing/.venv/bin/python
export FFMPEG=~/Documents/1-music-shipped/moongazing/.venv/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2
export FACE_LANDMARKER=~/Documents/1-music-shipped/moongazing/tools/sync/models/face_landmarker.task
$PY tools/sing/v7_outpaint.py prep; $PY tools/sing/v7_outpaint.py gen S1 nbp_2; $PY tools/sing/v7_outpaint.py gen V3S nbp_5
$MPY tools/sing/v7_outpaint.py merge S1 nbp_2; $MPY tools/sing/v7_outpaint.py merge V3S nbp_5
WC_VER=v7S1 $EPY tools/sing/wc_comp.py matte media/sing/outpaint/v7/S1_nbp_2_merged.png
WC_VER=v7V3S $EPY tools/sing/wc_comp.py matte media/sing/outpaint/v7/V3S_nbp_5_merged.png
$MPY tools/sing/v7_first.py comp; $MPY tools/sing/v7_first.py sheet; $MPY tools/sing/v7_first.py magenta
WC_VER=v7 $PY tools/sing/wc_takes.py submit S1 --n=4                     # round 1 (P7): S1 take 1
WC_V7R=3 WC_VER=v7 $PY tools/sing/wc_takes.py submit V3S --n=6           # round 3 (P7C): V3S take 12
$MPY tools/sing/look.py S1 v7_take_1; $MPY tools/sing/v6_lagwin.py S1 v7_take_1 13.05 18.40; $MPY tools/sing/v7_trace.py S1 v7_take_1 0.80 0.87 0.95
$MPY tools/sing/v7_expr.py media/sing/S1/v7_take_1.mp4 --first=media/sing/first/v7_S1_first.jpg
WC_VER=v7 $PY tools/sing/wc_post.py sync S1; WC_VER=v7 $PY tools/sing/wc_post.py sync V3S
$MPY tools/sing/v4_noblink.py media/sing/S1/v7_sync_1080.mp4 /tmp/s1_pass1.mp4 8 0 6 --fade=2
$MPY tools/sing/v4_noblink.py /tmp/s1_pass1.mp4 media/sing/S1/v7_sync_1080_open.mp4 81 82 89 --fade=2
$MPY tools/sing/v4_noblink.py media/sing/V3S/v7_sync_1080.mp4 media/sing/V3S/v7_sync_1080_open.mp4 24 25 29 --fade=2
WC_VER=v7 $EPY tools/sing/wc_post.py matte S1 v7_sync_1080_open; WC_VER=v7 $EPY tools/sing/wc_post.py matte V3S v7_sync_1080_open
$EPY tools/sing/v5_pencils.py media/sing/S1/v7_sync_1080_open.mp4 media/sing/S1/v7_sync_1080_open_matte --ferrule
$EPY tools/sing/v7_matte_fix.py media/sing/S1/v7_sync_1080_open.mp4 media/sing/S1/v7_sync_1080_open_matte
WC_VER=v7 $PY tools/sing/wc_post.py review S1 v7_take_1 0.87 media/sing/review/v7_S1_lag+0.87_measured+0.00_WIRED.mp4 --audio=media/sfx/Rewind_cinematic_sfx_mix_v5coda.mp3
node render/engine/render.mjs --preview --force --range 12.0 21.0 --encode --audio media/sfx/Rewind_cinematic_sfx_mix_v5coda.mp3 --out deliverables/wip/sing_v7_S1_preview.mp4
node render/engine/render.mjs --preview --force --range 153.5 159.6 --encode --audio media/sfx/Rewind_cinematic_sfx_mix_v5coda.mp3 --out deliverables/wip/sing_v7_V3S_preview.mp4
```

The nano-banana and Seedance outputs are not deterministic: rerunning `gen` / `submit` gives new pictures and takes. The
picks above are on disk.
