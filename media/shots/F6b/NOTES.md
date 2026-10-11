# F6b: Clock hands = Penrose stairs (194.10-195.86)

The clock face's hands have become Ascending and Descending; agents march it forever. Reused at F7_03.

## Keyframe

Model: google/nano-banana-pro (2K, 16:9), $0.134 per image. Chosen: `kf_2`.

Prompt (last round):

```
Frontal view of the colossal melting clock face hanging in the sky over the Chicago Loop: its two clock hands have become M.C. Escher's Ascending and Descending, an impossible Penrose staircase forming a closed square loop across the clock face; a single file of dozens of black-suited agents marches around the endless staircase. The world is the same M.C. Escher wood engraving as the third reference (crisp black ink line work, dense precise parallel hatching and cross-hatching that follows form), but now hand-colored: vivid colored-pencil color laid over the engraving in visible pencil strokes on warm off-white paper tooth - cobalt and ultramarine blue, vermilion, magenta, emerald, warm orange, sky blue - with the black hatching still showing through the color everywhere. Gustav Klimt gold-leaf accents (flat burnished gold with spiral and small square mosaic ornament) on select surfaces. Kandinsky shapes float in the sky: concentric circles, triangles, arcs and checkerboards in colored pencil. Hand-drawn, not a painting, no watercolor wash, no airbrush, no digital gradients, not photographic, not 3D. The clock is a colossal Salvador Dali melting pocket watch with a gold case, its face soft and drooping like warm cheese; the clock face is completely blank except simple short dash tick marks: no numerals, no Roman numerals, no letters. The agents are men in black suits, white shirts, black ties and black sunglasses with nearly blank faces, drawn as pure black-and-white engraving with no color at all: they are the only uncolored things in the picture. Every surface is now colored in saturated colored pencil over the hatching, with burnished Klimt gold leaf on rooftops, cornices and ornaments. Reference images: the first shows the engraving line technique of the world; the second shows the agents' design. Full bleed, edge to edge, no border, no margin, no paper edge, 16:9. No text, no letters, no numbers, no signature.
refs=['media/style_tests/world/3_loop_L_tracks_seedream-5-pro.jpg', 'media/design/takes/agent_formation_nano_t1.jpg']
```

## Takes

- take_1: bytedance/seedance-2.0 720p 5 s, est $0.75, state done, first frame `media/shots/F6b/kf_2.jpg`. 
  - prompt: The single file of black-suited agents marches around the endless square staircase on the clock face, round and round, climbing forever; the clock face slowly droops and drips. Slow camera push-in. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.
  - verdict: slow push-in, marching reads. Used.
- take_2: bytedance/seedance-2.0 720p 5 s, est $0.75, state done, first frame `media/shots/F6b/kf_2.jpg`. polish: rainbows removed from keyframe (prompt of take 1)
  - prompt: The single file of black-suited agents marches around the endless square staircase on the clock face, round and round, climbing forever; the clock face slowly droops and drips. Slow camera push-in. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.

Video cost for this shot: $1.50 (list-price estimate).

## Judgement

Clear one-idea image.

## chosen.json

```json
{
 "take": 2,
 "file": "media/shots/F6b/take_2_engraved_dered.mp4",
 "in_sec": 0.0,
 "out_sec": null,
 "rate": 1.0,
 "reverse": false,
 "notes": "clock hands = Penrose stairs, agents march; reused at F7_03",
 "matte": "media/shots/F6b/take_2_matte/matte.mp4"
}
```

## v3 revision pass (2026-10-11, stream F)

Jade 3:13. No video take: still plate `kf_v3_F6b_plate.jpg` (empty clock face, bigger clock, desk objects), cropped to `kf_v3_F6b_plate_crop.png` and de-reddened to `kf_v3_F6b_plate_crop_dered.png`. The Penrose staircase and the agents are drawn by `tools/sectionF/modules/penrose_march.js` (see `penrose()` in `tools/sectionF/edl.py`). v2 take 2 kept.

### v3 follow-up: restyle (rev-A review)

- **Stairs:** `tools/sectionF/penrose_guide.py` draws the engine's exact geometry at the magic angle onto the empty-clock
  plate (`kf_v3_F6b_guide.png`, step table `kf_v3_F6b_steps.json`). nano-banana-pro redrew it in the plate's hand
  (`kf_v3_F6b_redraw.png` → `_crop.png` → `_crop_dered.png`, tag `revA_f_kf_F6b_redraw`). Checked tread by tread by
  overlaying the 22 exact tread outlines on the redraw: every block in place, 7 / landing / 2 / landing / 2 / landing /
  7 / landing, each flight climbing, the loop closing at the seam (step 21 → step 0). Accepted.
- **Agents:** ink-engraved sprite sheet (`kf_v3_F6b_agents.jpg`, refs `agent_turnaround_male`, `agent_action`) cut by
  `tools/sectionF/agent_sprites.py` into `agents/front_0-3.png`, `agents/back_0-2.png` (paper halo, feet on the bottom
  edge, 280 px tall). `penrose_march.js` places them on the tread centres, front view on flights A/D, back view on B/C,
  flipped for the flights that run screen-left, two walk drawings per step, one step per beat.
- **Off-angle opening dropped:** the redraw exists only at the magic angle, so the shot holds it; the 194.10 clunk is the
  flash + shake + punch.
- **"All clockwise", measured on the rendered clip** (`media/reviews/v3/A/0313_infinite_staircase.mp4`, frames 0.32 s
  after four successive beats; `tools/sectionF/penrose_track.py`: dark-blob detection on the clock face, the tread table
  fitted to the blobs, fit error 4.6–6.1 px at 540p). Screen positions are preview px (960×540).

  | Agent | 192.66 | 193.10 | 193.54 | 193.98 | Screen direction |
  |---|---|---|---|---|---|
  | A1 (flight A, near right) | step 4 (521, 279) | 5 (498, 285) | 6 (476, 298) | 7 (450, 308) | down-left: right side → bottom |
  | B1 (flight B → C, left) | step 10 (369, 273) | 11 (335, 252) | 12 (not detected: overlaps the agent in front; seen by eye on the step) | 13 (383, 199) | up-left then up-right: bottom → left → top |
  | D1 (flight D, far right) | step 16 (469, 198) | 17 (495, 206) | 18 (520, 212) | 19 (550, 216) | down-right: top → right |

  Whole-frame check: the set of occupied treads maps onto the next beat's best with a shift of +1 tread on all three
  beat pairs (11, 11, 13 matches vs ≤ 7 for −1 and 0). Right → bottom → left → top on screen is clockwise.
- Fallbacks kept: `kf_v3_F6b_plate_crop_dered.png` with the engine-drawn stairs (set `stairs: true`, no `sprites`, plate
  back to that file in `edl.py`), and v2 `take_2_engraved_dered.mp4`.
