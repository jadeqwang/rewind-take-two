# Singing shots v8: "sultry" TEST round (S1, V3S), 2026-10-18

Kenton on v7: "much better than the previous version, but there's something about the original one (in watercolor art)
that this one is lacking". Jade: "some kind of sultry vibe?"

The coordinator compared watercolor v4 against v7 (`deliverables/wip/sing_v4_vs_v7_faces.jpg`). v7 reads as a square-on
video call:
- brows raised, eyes wide;
- wide enunciation;
- flat frontal daylight;
- a big head on narrow shoulders.

Jade approved a test round with three changes: a new acting prompt (P8), relit first frames, and a wider framing.

**Status: test only, not wired.**
- A.js and E.js still point at v7. I swapped the v8 (and, for the comparisons, v4) paths in only for the preview renders
  and restored both files afterwards, checked with `diff`.
- Nothing is committed.
- Frame numbers are song frames (song s x 24) unless they say "file frame" (0 = the shot's in-point).

## Files for Jade

| What | File |
|---|---|
| Review page (section "Singing v8 (sultry test)", at the top) | `deliverables/wip/sing_review.html` |
| S1 v8 in the film (960x540, 0:12.00-0:21.00) | `deliverables/wip/sing_v8_S1_preview.mp4` |
| V3S v8 in the film (2:33.50-2:39.60) | `deliverables/wip/sing_v8_V3S_preview.mp4` |
| Three panels: watercolor v4, v7 (wired), v8 | `deliverables/wip/sing_v8_{S1,V3S}_vs_v7_v4.mp4` |
| S1 ear test (v8_take_4) | `media/sing/review/v8_S1_lag+{0.35..1.25}_measured*.mp4` |
| V3S ear test (v8_take_3) | `media/sing/review/v8_V3S_lag+{0.30,0.45,0.60,0.75}_measured*.mp4` |
| First frames before and after the light, with face close-ups | `media/sing/review/v8_first_relight.jpg` |
| S1 alternative take (no pink eraser, see below) | `media/sing/S1/v8t3_sync_1080_open.mp4`, ear tests `media/sing/review/v8t3_S1_lag*` |

The v4 panels are the watercolor files rendered in today's timeline. The ear-test clips are the raw takes, without the
eye patches.

## 1. First frames (`tools/sing/v8_first.py`, new; `tools/sing/v7_outpaint.py` with `OP_VER=v8`)

### Framing

The face is 0.30 of the frame height (v6/v7: 0.35), and the eyes sit at 1080p (940, 418).
- **S1:** a new, wider fill (`outpaint/v8/S1_nbp_1`: a 3000x2000 canvas, nano-banana-pro at 4K, with a prompt line for
  natural full shoulder width).
  - Shoulders are about 2.7 face heights across, against v7's about 2.3.
  - The two other S1 fills were worse: one has narrow shoulders, one doubles the bands.
- **V3S:** v7's fill (`outpaint/v7/V3S_nbp_5`), which is already about 2.7 face heights wide.
  - All 7 wider V3S fills failed. Two turned the bed into a second jacket with a second patch, even after I added "only
    one person and one jacket"; the others cut or duplicated an arm.
- **Measured at 1080:** the S1 inter-ocular is 177.8 px, against v7's 204.2 and watercolor v4's 192.6. She is now framed
  a little wider than the watercolor.

### Light

A local relight, not a generative edit: one smooth per-channel gain layer multiplied over her own pixels (`gain_field`).
- The key light comes from frame-right for S1 (as in the watercolor) and from frame-left for V3S (the plate's warm side).
- On the key side, +9% light and a warm shift; on the far side, -27%.
- A shadow runs down the far side of the face, with -17% under the cheekbones.
- There is a broad, weak flush. I made the first flush stronger, but it read as blusher, so I spread and weakened it.
- Landmark shift, relit against unlit, is 0.42 px (S1) and 0.17 px (V3S) at 720p. Inter-ocular, eye width and face width
  move by under 1%. Her face, features and makeup are her pixels.

### Matte

- V3S reuses v7's trim key.
- **S1 pencils:** BiRefNet on the v8 canvas dropped the pink eraser and its ferrule, and my first magenta check was too
  small to see it. So all three first S1 takes (v8_take_1-3) came back with only a yellow stub on the left.
  - I fixed the first frame: `v5_pencils.key` on the canvas, with its search window set from the solid head rather than
    the flyaways. That frame is `first/v8_S1_first.jpg`; the round-1 frame is in `first/v8_round1/`.
  - Then I reshot S1 (v8_take_4-6). The pencils are whole in takes 4-6.

## 2. Prompt P8 (`wc_takes.py`, `WC_VER=v8`; S1 1927 chars, V3S 1812; v6b/v7 prompts unchanged)

The new acting, against v7:
- She sings soft and close to the mic, with small, controlled lip movements and no wide enunciation; lips still close on
  'b' and 'm'.
- Sultry and self-possessed.
- In the first moments she turns her head a little, lowers her chin slightly and looks up into the lens.
- A calm, half-lowered gaze: lids resting steadily a little lowered, never sinking further and never shut; only quick
  full blinks.
- Brows low and relaxed: never raised, no forehead lift, never knit.
- Slow, languid movement.
- A hint of a knowing smile in the eyes; never a grin; never pained, sad, tearful or wide-eyed.
- The warm side light stays.

Kept from P7: the identity lock, glasses, the jacket list, no headphones, the locked-off camera, and the S1 pencils and
breeze. V3S's hair line adds "a strand drifting across one side of her face".

## 3. Takes (Seedance 2.5 720p, avatar mode, same slices; tags `v8_sing_*`)

| Take | Lag | Eyes on screen | Verdict |
|---|---|---|---|
| S1 `v8_take_1` (round-1 frame) | corr +0.58, windows +0.24..+1.48 | shut 0:12.85-0:13.64 | reject: no pink eraser, lag drifts |
| S1 `v8_take_2` | corr +0.84 | shut from the start to 0:13.61 | reject: no pink eraser |
| S1 `v8_take_3` | corr +0.890 (r .66), windows +0.71..+1.07 | downcast to 0:13.35; two one-eyed half-winks | **alternative**, kept as `v8t3_*`: the best phrase-1 lips and the most sultry, but **no pink eraser** |
| S1 `v8_take_4` (fixed frame) | corr +0.712 (r .49); events +0.74/+0.64/+0.95/+0.82; phrase 1 on the trace +0.80 | blinks 0:12.93, 0:13.81 (slow), 0:15.06 (0.42 s) | **pick, +0.80**; pencils whole |
| S1 `v8_take_5` | windows -0.60..+1.47 (r .19) | many | reject: lag unusable |
| S1 `v8_take_6` | steady +1.27 on phrase 2 | shut to 0:12.81 | reject: mouth nearly shut through "The night", the on-screen phrase |
| V3S `v8_take_1` | windows +0.40..+1.80 | eyes shut 2:34.05-2:35.25 (1.2 s) | reject |
| V3S `v8_take_2` | windows +1.44 → -0.06 | low or shut to 2:34.81 | reject: drift |
| V3S `v8_take_3` | corr +0.452 (r .61); events +0.66/+0.46/+0.23/+0.58; trace +0.45 | low or shut to 2:34.45; shut 2:36.99-2:37.41; slow blink 2:38.24 | **pick, +0.45** |

What changed, measured on the synced files over the on-screen span (S1 0:12.60-0:16.14, V3S 2:33.98-2:39.14).
Blendshapes read the painted v4 face less reliably, so its numbers are only a rough guide.

| | Median browInnerUp | Median jawOpen | jawOpen p95 | Head roll range | Median pitch (chin down ↑) | Inter-ocular at 1080 |
|---|---|---|---|---|---|---|
| S1 v4 watercolor | 0.84 | 0.035 | 0.34 | 3.2° | 0.254 | 192.6 |
| S1 v7 | 0.78 | 0.172 | 0.56 | 1.6° | 0.258 | 204.2 |
| **S1 v8 t4** | **0.49** | **0.054** | 0.37 | 1.6° | 0.273 | 177.8 |
| V3S v4 watercolor | 0.88 | 0.048 | 0.32 | 5.6° | 0.239 | 195.7 |
| V3S v7 | 0.78 | 0.124 | 0.31 | 2.3° | 0.256 | 205.2 |
| **V3S v8 t3** | **0.55** | **0.039** | 0.23 | 5.3° | 0.274 | 171.3 |

- **Brows** sit lower: inner-brow median 0.78 → 0.49 / 0.55.
- **The mouth** is soft: median jaw is a third of v7's and close to the watercolor's.
- **Chin** is slightly lower: pitch 0.273-0.274, against 0.256-0.258.
- **V3S head roll** is now watercolor-like (5.3° against 5.6°). **S1** is not (1.6° against 3.2°).
- **Identity** at 720p against the start image:
  - S1 t4: inter-ocular 119.2 (121.3), eye width 35.2 (36.2). Eye width / inter-ocular 0.295 against 0.298, so no eye
    enlargement.
  - V3S t3: 114.4 (116.7) and 33.9 (34.0). The ratio is 0.296 against 0.291 (+1.7%). Small, and partly the lowered lids
    early in the take, but I'm noting it.
  - By eye at 2x: her face, glasses on, jacket, patch and disc intact. Both pencils in S1 t4.

## 4. Sync (measured; Jade's ear decides; not wired)

- **S1 t4, +0.80** (`SYNC_V8` knots (12.60, 0.50), (19.64, 7.54)).
  - On the trace the mouth opens on "The night" (13.15-13.45), closes for the 'b' (13.5-13.85) and opens on "fore" at
    13.95 (voice back at 13.88).
  - Phrase 2, under the cutaway, drifts to about +1.0.
  - Ear tests at +0.35..+1.25 in 0.15 steps.
- **V3S t3, +0.45** (knots (153.98, 0.75), (159.14, 5.91)).
  - The 'b' closure sits on 2:34.72 and the 'm' releases at 2:37.12.
  - The mouth falls about 0.1 s after the phrase end (2:39.14).
  - Ear tests at +0.30 / **+0.45** / +0.60 / +0.75.
- **S1 t3 alternative:** +0.85 (knots in the `wc_post.py` comment), ear tests `v8t3_S1_lag*`.

## 5. Eyes (`v6_eyes.py`, `v4_noblink.py`)

**S1** (`v8_sync_1080_open.mp4`, file frame = song frame - 302):
- Kept: a normal full blink at 0:12.93-0:13.18 (f310-f315, file frames 8-13), in the Bean wide.
- Patched open: a slow close at 0:13.81-0:14.14 (f331-f338, file frames 29-37; from frame 28).
- Patched open: a 0.42 s close at 0:15.06-0:15.47 (f361-f370, file frames 59-69; from frame 58).
- Checked at 2x: `S1/v8_sync_1080_open_check{,_f29}.jpg`.

**V3S** (`v8_sync_1080_open.mp4`, file frame = song frame - 3696):
- Patched open: the opening, eyes downcast and nearly shut at 2:33.98-2:34.56 (f3696-f3709, file frames 0-14; from frame
  15). That gives "chin down, eyes up".
- Patched open: a 0.42 s close at 2:37.06-2:37.48 (f3770-f3779, file frames 74-83; from frame 72). The cutaway starts at
  2:37.39.
- Kept: a slow full blink at 2:38.31-2:38.65 (f3800-f3807, file frames 104-111), lids at 0.19-0.32 for 8 frames.
- Checked at 2x: `V3S/v8_sync_1080_open_check{,_inpoint}.jpg`.

## 6. Mattes

- **S1:** BiRefNet, then `v5_pencils.py --ferrule`, then `v7_matte_fix.py` (`S1/v8_sync_1080_open_matte/`). Checked over
  magenta at file frames 0, 20, 40, 60, 84 and 140: both pencils present, pink eraser included.
- **V3S:** BiRefNet. Checked at file frames 0, 60, 100 and 120: whole figure, no plate pieces.

## What is weak (honest list)

- **Not heard.** Both lags are measured. S1 t4's lag is read from the on-screen phrase; its phrase 2 (under the cutaway)
  is about 0.2 s later.
- **S1 t4 is less sultry than t3.**
  - Its head roll range is 1.6°, the same as v7 and half the watercolor's.
  - It needed two eye patches: 0:13.81-0:14.14 (f331-f338) and 0:15.06-0:15.47 (f361-f370).
  - t3 has the better turned-head, half-lidded performance, but no pink eraser. Given that, the S1 test answers "does
    sultry help?" only partly.
- **V3S faces the camera after the opening:** median |yaw| 0.006. The turn and chin-down happen in the first ~0.6 s.
- **V3S cut-in:** the patched open eyes (2:33.98-2:34.56, f3696-f3709) look toward frame-left more than into the lens.
- **Seedance kept closing her eyes.** All 9 takes close them for 0.3-1.2 s somewhere despite "never shut". Three patches
  (one in S1, two in V3S) are painted eyes from a neighbouring frame.
- **Kept blinks:** the V3S slow blink at 2:38.31-2:38.65 (f3800-f3807), 0.33 s, and the S1 blink at 0:12.93 (f310).
- **S1 flyaways:** the matte lets faint plate hatching show between the flyaways above the bun at file frames 0 and 84
  (0:12.60, f302; 0:16.10, f386).
- **Pink eraser:** small, and partly hidden behind the bun as she turns.
- **Shoulders are invented** by nano-banana-pro outside the photo, more of them now (wider framing).
- **The V3S fill is v7's.** A natural-width V3S fill never worked.
- **The light is subtle.** It is a gain layer over flat daylight, not a real key light, and Seedance flattens it a
  little as she moves. The S1 far-side shadow and warm key read in the stills; the cheekbone shading is mild.
- **V3S eye-width ratio** is +1.7% against the start image (above).
- **720p upscaled**, as before.
- **My miss:** the first S1 first frame went out without the pink eraser. It cost 3 takes ($5.55).

## Spend

| Item | Calls | Spend |
|---|---|---|
| S1 Seedance 8 s | 6 (3 on the pencil-less frame, 3 retakes) | $11.10 |
| V3S Seedance 7 s | 3 | $4.86 |
| Outpaint fills (nano-banana-pro 4K) | 10 (S1 3, V3S 7) | $2.40 |
| **Total v8** | 19 | **$18.35** |

- `REWIND_CAP=600` was set for this round, as the coordinator asked.
- The project estimate (`spend.total()`) is **$384.34**. That is $5.63 more than v7's end ($360.36) plus v8; it comes
  from other billed work in between, not this round.
- `tools/gen/spend.py`'s default cap reads $600 in the working tree. I didn't change it.

## Files touched

- **New:** `tools/sing/v8_first.py`.
- **Extended:**
  - `tools/sing/wc_takes.py`: `WC_VER=v8`, `P8`, `V8_HAIR`, tag `v8_sing_*`.
  - `tools/sing/v7_outpaint.py`: `OP_VER=v8`, the wider canvas, the one-jacket line.
  - `tools/sing/wc_post.py`: `SYNC_V8`.
- **Timeline:** `render/timeline/A.js` and `E.js` are unchanged (v7 wired). They were swapped temporarily for renders
  and restored.
- **Pages and notes:** `deliverables/wip/sing_review.html` (section "v8"), `docs/revisions/v9/SING_STATE.md`,
  `media/sing/NOTES.md`.
- **Media:**
  - `media/sing/outpaint/v8/`
  - `media/sing/first/v8_*`, `v8S1_her_alpha.png`, `v8_round1/`
  - `media/sing/{S1,V3S}/v8_take_*`, `v8_sync_1080*`
  - `media/sing/S1/v8t3_sync_1080*`
  - `media/sing/review/v8_*`, `v8t3_*`
  - `deliverables/wip/sing_v8_*`

## Rebuild

```
export REWIND_CAP=600 FFMPEG=... FACE_LANDMARKER=...   (as in sing_v7.md)
OP_VER=v8 $PY tools/sing/v7_outpaint.py prep; OP_VER=v8 $PY tools/sing/v7_outpaint.py gen S1 nbp_1; OP_VER=v8 $MPY tools/sing/v7_outpaint.py merge S1 nbp_1
WC_VER=v8S1 $EPY tools/sing/wc_comp.py matte media/sing/outpaint/v8/S1_nbp_1_merged.png
$MPY tools/sing/v8_first.py comp; $MPY tools/sing/v8_first.py sheet
WC_VER=v8 $PY tools/sing/wc_takes.py submit S1 V3S --n=3
WC_VER=v8 $PY tools/sing/wc_post.py sync S1; WC_VER=v8 $PY tools/sing/wc_post.py sync V3S
$MPY tools/sing/v4_noblink.py media/sing/S1/v8_sync_1080.mp4 /tmp/a.mp4 28 29 37 --fade=2
$MPY tools/sing/v4_noblink.py /tmp/a.mp4 media/sing/S1/v8_sync_1080_open.mp4 58 59 69 --fade=2
$MPY tools/sing/v4_noblink.py media/sing/V3S/v8_sync_1080.mp4 /tmp/b.mp4 15 0 14 --fade=1
$MPY tools/sing/v4_noblink.py /tmp/b.mp4 media/sing/V3S/v8_sync_1080_open.mp4 72 74 83 --fade=2
WC_VER=v8 $EPY tools/sing/wc_post.py matte S1 v8_sync_1080_open; $EPY tools/sing/v5_pencils.py media/sing/S1/v8_sync_1080_open.mp4 media/sing/S1/v8_sync_1080_open_matte --ferrule
$EPY tools/sing/v7_matte_fix.py media/sing/S1/v8_sync_1080_open.mp4 media/sing/S1/v8_sync_1080_open_matte; WC_VER=v8 $EPY tools/sing/wc_post.py matte V3S v8_sync_1080_open
To wire (when Jade picks): A.js S1_SRC = 'media/sing/S1/v8_sync_1080_open.mp4'; E.js V3S_SRC = 'media/sing/V3S/v8_sync_1080_open.mp4'
and its V3S_lyric HER matte = 'media/sing/V3S/v8_sync_1080_open_matte/'.
```
