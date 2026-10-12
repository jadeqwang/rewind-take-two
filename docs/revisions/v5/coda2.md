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

## Round 4: the push-plate door (Jade, verbatim in README Round 4)

> the brass button looks like a doorbell rather than a square plate you'd expect as a mechanism. I'd naively expect
> the brass button to be a little bit lower, placed facing into the entrance the way you'd see an ADA compliant
> button to be, just, made of brass instead of the usual stainless steel square plate button
>
> probably makes sense for the doorman to be physically offscreen to the right so as to not be in the way of the guest

**Status: done, 540p checked.** Clip `media/reviews/v5/coda_door_r4.mp4` (226–238, v5 coda mix, 2.2 MB) + sheet
`media/reviews/v5/coda_door_r4_sheet.jpg`. The full-scene clip `coda_hilbert_r3.mp4` still shows the Round 3 door; the
lobby in it is unchanged.

### Decisions

- **The engraved accessibility symbol (wheelchair pictogram) on the plate is the setup session's call**, so it reads as
  an automatic-door opener at a glance.
- **Plate:** a square brass push-plate (thin rim, four screws, brighter where hands press it), mounted **on the right
  return of the entry**. That is the hatched inner face of the right pier, between the stained-glass sidelight and the
  stone front. It faces into the entrance, perpendicular to the door, so it reads as a foreshortened square angled
  toward the doorway. It is about 6 in (≈100 px tall at that wall's depth), centred at y ≈915 in design px. That is
  below the stone ledge and below the handle's middle (≈830), about 35 in up by the door's scale.
  - Nano drew it well but too big and too high (`door_plate_r4.jpg` was ~20 in; `_b` was ~9 in at handle height).
  - So I cut `_b`'s plate and re-seated it (`prep_coda2.plate_r4`): scaled to ~6 in, lowered below the ledge, and
    sheared so its edges slope like that wall's ledge lines. It went onto the original plate-free door, giving
    `gen2/door_plate_r4c.jpg`, and only that quad went into `door_frame_r4.png`.
  - The Round 3 doorbell plate is gone.
- **Doorman offscreen right:** his white glove and green cuff come in **level from the right frame edge** at the plate's
  height (233.2–233.5). The flat fingertips hover by the plate, press it (233.9–234.0; the latch click 234.034), and the
  hand slides back out to the right (234.14–234.72).
  - Nano would not give that reach in place: `door_press_r4.png` put the hand on the door handle, and
    `door_press_r4_b.jpg` brought the arm in from the lower left.
  - So the hand is cut from `door_press_r4.png` (BiRefNet; its pose is right: a flat glove, fingers to the left, back of
    the hand to camera, the forearm from the right). The module places it: scale 0.65 (wrist to fingertip ≈140 px,
    hand-sized next to the plate), rotated 25° so the forearm rises gently to the right edge, its fingertip on the plate.
  - `hilbert_door.js` gained press `dir`, `pushDir`, `scale`, `baseRot`, `target`, `shade` (the defaults reproduce
    Round 3).
- **Kept:**
  - the last tick 4,113 at 233.642, then the latch (234.034) and the bell (234.094) as the door starts to swing on its
    own (the soft-start `auto` swing);
  - the glide;
  - the mix (unchanged, no rebuild).

### Checks

- I computed the hand's leftmost point over every frame: x **1726** (the right 10% of the frame; centre 960).
- Its lowest point next to the counter's glyphs (x < 1860) is y ≤ 989. The fingertip target was raised 9 px for this;
  the counter text starts at ≈998.
- Frame strip every 0.1 s (233.0–235.3): the plate alone, the glove in from the right edge, the hover, the press, the
  hand out to the right. 4,112 → 4,113 reads under the glove.
- The door starts on the bell and swings into the lobby. The plate rides out of frame in the glide.
- Weak spot: at 540p the plate is about 30×50 px and the glove about 70 px. The symbol reads at 1080p and as a brass
  square with a pictogram at 540p.

### Spend (Round 4)

| What | $ |
|---|---|
| `door_plate_r4` (too big/high) + `door_plate_r4_b` (used, re-seated) | 0.27 |
| `door_press_r4` (hand cut from it) + `door_press_r4_b` (rejected: arm from the lower left) | 0.27 |
| **Round 4 total** | **0.54** (coda2 total 5.96 of 15; project $252.72) |

Files: `tools/sectionF/coda/gen_coda2.py` (r4 jobs), `prep_coda2.py` (`plate_r4`, `door_r4`),
`tools/sectionF/modules/hilbert_door.js` (hand placement params), `tools/sectionF/edl.py` (PC1 press/frame/geom/hand;
F_edl.json regenerated). New media: `gen2/door_plate_r4*.jpg`, `gen2/door_press_r4*.{png,jpg}` (+ .json),
`door_frame_r4.png`, `press_hand_r4.png`, `door_geom_r4.json`.

## Round 5: the plate sits flat on the wall; the full coda (Jade, verbatim in README / coordinator)

> brass button styling is correct, but is sitting jankily on the door. you can tell because the top of the button is
> not parallel to the groove in the wall it's on.
>
> can you show me the full coda with this correction up to the end of the video?

**Status: done, $0.** Full coda at 540p, 226.0–244.05 (credits fade → door → lobby → queue → FRONT DESK → end of
film, v5 coda mix): `media/reviews/v5/coda_full_r5.mp4` (7.3 MB) + `media/reviews/v5/coda_full_r5_sheet.jpg`.
This replaces `coda_hilbert_r3.mp4` and `coda_door_r4.mp4` as the current whole-scene review.

### What changed

- **The plate is pinned into the plane of the pier's inner face** (`prep_coda2.plate_r5`).
  - Why Round 4 looked off: I had warped the plate with rough corners, so its rim's top edge came out at slope 0.035
    while the groove above it runs ≈0.12.
  - The wall was measured on the plate-free door:
    - The groove right above the plate and the hatch rows on that face (structure-tensor slopes per 20 px band:
      0.133 at the groove, 0.12 → 0.24 from y 860 to 980) were fitted by least squares to the face's horizontal
      vanishing point, **VP_H (760, 735)**.
    - The face's two vertical edges (the stile boundary and the pier corner) meet at **VP_V (1508, −3312)**.
  - The source plate (`gen2/door_plate_r4_b.jpg`) is rectified first:
    - its brass face is found with an HSV key (nano re-drew the hatching, so a difference key fails);
    - the four sides are line-fitted on the convex hull;
    - it is unwarped to a flat 240×400 texture with a 9 px rim, `gen2/plate_r5_flat.png`.
  - Then that texture is corner-pinned to the plane:
    - TL (1716, 866) as before; TR on the line TL→VP_H; the sides on lines to VP_V; the bottom on a line to VP_H.
    - Result: (1716, 866) (1775, 874.1) (1781.8, 980.6) (1721, 966).
    - Same style, size (~6 in) and height (top 14 px under the groove, below the handle's middle).
  - Written to `gen2/door_plate_r5.jpg` → `door_frame_r5.png`, with geometry in `door_geom_r5.json`.
- **Check overlays:** the groove extended (cyan), the plate's top edge (magenta) and bottom edge (orange) aimed at
  VP_H, and the sides aimed at VP_V (green).
  - 1080p ×4: `gen2/plate_r5_check.png`. 540p, from the clip at 233.1: `gen2/plate_r5_check_540.png`.
  - The top edge runs parallel to the groove (both through VP_H; local slopes 0.118 and 0.137 a few px apart, as
    perspective gives). The bottom edge follows the hatch rows, and the sides follow the face's edges.
- **The glove's fingertip is re-aimed** at the new centre (1748.5, 921.7) + (−14, −17) = **(1735, 905)**. The fingertips
  sit on the upper half with the palm over the middle, as before. Its lowest point next to the counter stays at
  y ≤ 989, and its leftmost point is still x ≈1726. The hand is not moved toward the centre.
- **Counter contrast:** a faint, soft dark backing sits under the ITERATION line while it is over the door. It is a new
  module, `tools/sectionF/modules/hud_backing.js`, a blurred rounded shade (alpha 0.4, blur 10 px), rect
  [1414, 975, 464, 54]. It fades in with the door (232.8, 0.5 s) and out with the counter (to 234.19). It is the first
  layer of `O_counter` in `edl.py`, and the counter itself is untouched. 4,112 → 4,113 now reads clearly over the
  hatching at 1080p and 540p. Over the black credits it is invisible.

### Checks (frame by frame on the 540p clip; 1080p stills at 233.2 / 233.7 / 233.95 / 234.5)

- **Credits fade:** 226–232.8 as signed off; the counter reads 4,097 … 4,111.
- **Door:**
  - The door fades up at 232.8 with the plate alone.
  - The glove comes in level from the right edge at 233.2–233.5 and hovers.
  - 4,112 → 4,113 ticks at 233.642 and reads over the backing.
  - The press is at 233.9–234.0. The latch (234.034) and bell (234.094) land as the door starts to swing by itself.
  - The hand goes out to the right by 234.7. The glide runs to 236.36.
- **Lobby:** the ledger close-up (curved ink), the look up, nine idle Jades out of sync, and the FRONT DESK line full
  by 240.2, held to the cut at 244.05.
- **Audio, unchanged mix:** last tick onset 233.597 (−41.6 dBFS), latch/bell peak −28.0 dBFS. The clip is 18.04 s.
- **Red:** `dered.py --check` max 1.87%, the same as before (brown ink lines and the orange headphones).

### Spend (Round 5): $0 (no generation). coda2 total $5.96 of 15; project $252.72.

Files: `tools/sectionF/coda/prep_coda2.py` (`wall_vps`, `r5_quad`, `plate_rim`, `plate_r5`), new
`tools/sectionF/modules/hud_backing.js`, `tools/sectionF/edl.py` (PC1 frame/geom/target, O_counter backing;
F_edl.json regenerated). New media: `gen2/plate_r5_flat.png`, `gen2/door_plate_r5.jpg`, `gen2/plate_r5_check*.png`,
`door_frame_r5.png`, `door_geom_r5.json`, the two review files.
