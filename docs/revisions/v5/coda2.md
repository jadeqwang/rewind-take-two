# v5-coda2: Jade's Round 3 notes on the Hilbert Hotel post-credits scene

Agent `v5-coda2`, 2026-10-12. Cap $15, tag `v5_coda2_`. Spend at start **$246.62** of $400. Nothing committed.
Scope: PC1_door / PC2_lobby (234–244.05) and the credits hand-off just before (last tick 233.642, bell 234.094: kept).

## Status: all five notes done and checked at 540p

| Clip | Path |
|---|---|
| Credits → Hilbert Hotel, Round 3 (540p, 226.0–244.05, v5 coda mix unchanged, 7.4 MB) | `media/reviews/v5/coda_hilbert_r3.mp4` |
| Contact sheet (credits every 1.1 s, door every 0.25 s, lobby every 0.6 s) | `media/reviews/v5/coda_hilbert_r3_sheet.jpg` |
| Queue close-up for the idle motion (540p, 238.8–244.05, camera held 2.3× on the queue, no text box) | `media/reviews/v5/coda_hilbert_r3_queue.mp4` (scratch timeline `tools/sectionF/coda/pc_queue_timeline.js`) |

Hand-over: `docs/revisions/v5/fragments/coda2.json`. Nothing committed. The film length (244.05) and the mix are
unchanged, so no `build.py --coda` rebuild was needed.

### Checks done

- **Door:** I computed the hand's leftmost on-screen x over every frame from its alpha and the module's transform:
  **1281** (centre 960). The reach ends by about 233.3, so the last tick (4,113 at 233.642) reads over the sleeve and
  pier. In the first timing, "4,112" sat on the white glove; I fixed that. Press 233.92–234.0, latch 234.034, bell
  234.094 as the door starts, release 234.10, gone by 234.72. Audio in the clip: last tick onset ≈233.60 at −41.6 dBFS,
  bell/latch peak −28 dBFS, the same as v5-build.
- **Ledger:** full-res still at 236.375. Rules, names and room numbers dip into the gutter, crest with the page and
  foreshorten near the spine. It is the same in the tilt-up frames (237–239.4).
- **Idle:** the per-figure sheets are in `media/shots/PC/idle/<name>/sheet.jpg`. Feet are stable in every take (≤2 px
  drift; no Seedance zoom). The faces, hair, glasses, pencils, chest dot and jackets hold. The queue clip shows nine
  different actions out of sync.
- **Note 4:** Jade #2 has rectangular-ish glasses, a solid hair curtain and smaller pigtails, and purple shows behind
  her. The protagonist has no glasses and her two crossed pencils show.
- **Text:** at 240.0 it reads "Of course we ha"; the whole line is up at 240.2 and holds with the ▼.
- **Red:** `dered.py --check` max 1.89%, the same as v5-build's clip second by second (the door +0.1–0.3 points from
  the brass plate / hand). It is dark brown ink lines plus the canon orange headphones; no visible red.

### Weak spots

- Purple's foot-tap is hidden behind the desk. She still glances and blinks, but she is the quietest of the nine.
- Idle rates below 1.0 (0.86–1.0) repeat a frame now and then. That is not visible at idle speed.
- The press hand is a single still, moved as a rigid cut-out (translate + 7° rotation). Its fingers don't articulate
  beyond the press nudge.

## Plan

1. **Stills (nano-banana-pro 2K, `tools/sectionF/coda/gen_coda2.py`, outputs + .json in `media/shots/PC/gen2/`):**
   `jade_v2` (the protagonist as at the film's end: O2 bun with the two crossed pencils (graphite pink eraser,
   rainbow pale-blue eraser), curtain bangs, **no glasses**, canon outfit: white cropped bomber, orange band,
   pale-blue dot on her left chest, 1420 MHz roundel, black mock-neck crop top, orange headphones, navy cargo with
   orange straps, white chunky sneakers; no pencil in hand), `glasses_v2` (edit of the glasses sprite: rectangular-ish
   glasses, fuller hair, half-up ponytails ~40% less volume), `glove_press` (white glove, index finger out, green
   livery cuff), `door_plate` (edit of door.jpg: brass push-plate with an engraved infinity-key on the right stone
   pier; only that patch is pasted into the frame). All 9:16 on flat grey #bdbdbd for the figures.
2. **Idle takes** (Seedance 2.0, 9:16, 5 s, first frame = last frame = the still, so each take loops; locked camera,
   grey ground): `tools/sectionF/coda/vgen_coda2.py`, shots `v5_coda2_idle_<name>`. Test `jade` first, check face /
   hair / jacket, then the other eight. Matte: BiRefNet (`tools/engrave/matte.py`) -> RGBA PNG sequences cropped
   to a fixed box -> `media/shots/PC/idle/<name>/`. Lobby module draws frame ((t + phase_k) mod N) per figure.
3. Door: drop the arm/handle grip; the glove reaches from the right edge to the push-plate on the right pier,
   presses (~234.0, the latch click), withdraws; the door swings by itself from the bell (234.094), ease-in-out.
4. Ledger: a curved-page mesh (per-page top/bottom edge curves measured from the plate + a lift profile that dives
   into the gutter and lifts at the outer edge; text re-parameterised by surface arc length, so it foreshortens
   toward the spine), drawn as affine triangles.
5. FRONT DESK line typed at ~110 cps (whole line ~0.3 s), then held.
6. Ghosts rebuilt from the new protagonist; ghosts / tail / 8-bit get engine idle (per-figure sway + breath with
   their own period and phase; the 8-bit a 2-frame idle).

## Decisions

- **Door hand: the doorman's white glove with the green livery cuff** (not Jade's own hand). Jade's original note asks
  for "a gloved hand"; Jade doesn't wear gloves (her own POV hand would be a bare hand in the white bomber cuff), the
  doorman's glove reads *hotel* at once, and it keeps the look Jade already saw. He stands just off frame right, beside
  the door, and presses the brass plate on the stone pier; his hand never gets left of x 1276 (frame centre 960).
- Push-plate: brass, engraved infinity-key (the crest's motif), on the right stone pier at handle height (design
  x 1810–1900, y 620–775), nano edit of door.jpg, only that patch pasted (feathered) into the frame.
- The protagonist is the end-of-film Jade (O2 onwards: bun back up with both pencils crossed, graphite pink eraser +
  rainbow pale-blue eraser), no glasses, empty hands (canon: exactly two pencils, both in the bun).
- Idle takes use first frame = last frame (Seedance `last_frame_image`), so each loops without a seam.

## Spend (list-price estimates, `spend.py --tags`)

| What | $ |
|---|---|
| 6 nano-banana-pro 2K stills (`jade_v2`, `jade_v3`, `glasses_v2`, `door_plate`, `door_press`; `glove_press` not needed: the press hand is cut from `door_press` at 2K) | 0.67 |
| Seedance 2.0 idle takes: jade, glasses, teal, purple at 720p (4 × 0.75) | 3.00 |
| Seedance 2.0 idle takes: braids, plain, sleepy, rainbow, mint at 480p (5 × 0.35) | 1.75 |
| **Total this pass** | **5.42** (cap 15) |

Project total after: $252.18 of $400.

## Files

- Edited: `tools/sectionF/modules/hilbert_door.js`, `tools/sectionF/modules/hilbert_lobby.js`, `tools/sectionF/edl.py`
  (PC1/PC2 rows, `LEDGER_CURVES`; F_edl.json regenerated, only PC1_door / PC2_lobby differ).
- New code: `tools/sectionF/coda/gen_coda2.py` (stills + prompts), `vgen_coda2.py` (idle takes + prompts),
  `prep_coda2.py` (door plate patch, press hand, sprites_v2), `idle_matte.py` (takes → RGBA loops),
  `pc_queue_timeline.js` (scratch, the queue clip).
- Media (gitignored): `media/shots/PC/gen2/` (stills + .json: model, prompt, refs, seed null), `gen2/ff/` (idle first
  frames), `door_frame_v2.png`, `press_hand.png`, `door_geom_v2.json`, `sprites_v2/`, `idle/<name>/` (120 PNG frames +
  info.json + sheet.jpg each, 153 MB), `media/gen/v5_coda2_idle_<name>/take_1.mp4` (+ .json with the prompt and model),
  the three review files. v5-build's assets are untouched (`sprites/`, `glove.png`, `door_frame.png`, `door_geom.json`).
