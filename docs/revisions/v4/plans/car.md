# 1:30, the car: plan

**Status: plan and blockout ready for Jade.** Nothing spent, no shared file edited, nothing committed.
(v4-B sub-agent `v4B-car`, 2026-10-11.)

## Execution (kept current; a fresh session can resume from here)

**Status: option C built and in the cut (540p check done); waiting for Jade's review.** Jade chose C on 2026-10-11 ("animatic_C.mp4 is the best of the 3, split lyric is
good, start over the shoulder is good, front readable is good"). Spend cap $8, tag `v4B_car_`.

Decisions (v4-B, from Jade): one take, hold wide over her right shoulder then push between the seats to the
mirror, mirror turned to the lens; SIRENS on the road sign (as large as the windshield allows) and IN MY MIRROR on
the mirror's lower edge, each on its sung onset; plates right-reading at 1.5x via `tools/v4B/plate/plate.js`,
hero `TVA 1729`, `TVA 4104` if a second can read; shot runs 89.26-92.79 (V2f1 trimmed to 88.38-89.26; going back to
90.14 must be a one-number change); her bun, both pencils and some cheek visible in the wide.

| Step | State | Files |
|---|---|---|
| 1. Layout references for the keyframes (`car_scene.html?kf=wide|close`) | done | `media/shots/V2f3/blockout_wide.png`, `media/shots/V2f4/blockout_close.png` |
| 2. Keyframes: `tools/v4B/car/kf.py` | done. Close: `media/shots/V2f4/kf_close_b2.png` (close_b with badges removed; close_a too busy). Wide: `media/shots/V2f3/kf_wide_b.jpg` (wide_a had no sign and hid her face), fixed free by `tools/v4B/car/fix_wide.py` -> `kf_wide_b_fix.png` (left eraser recoloured pale blue; the close mirror laid back in) | `media/shots/V2f3/`, `media/shots/V2f4/`, `kf_log.jsonl` in each |
| 3. Move | done: method (b), two stills + engine push (no Seedance). `tools/v4B/car/car_shot.js`: zoom about a fixed point so the wide's mirror lands on the close still; hand-over in two steps (mirror body, then the rest) in the fast part; sign, bezel words and plates pinned by the engine | `tools/v4B/car/car_shot.js`, solo check `tools/v4B/car/_car_solo.js` |
| 4. Engrave | done: `engrave_still.py` on both stills (under `media/.engrave.lock`) | `*_engraved.png`, close also `_feather.png` / `_body.png` (alpha) |
| 5. Timeline | done: `render/timeline/C.js` (import + `CAR_START = 89.26`, V2f1 row ends at CAR_START, V2f2 row removed, one `shots.push(carShot(...))`, `C_lyr_sirens` commented out; v3 values in comments). Back to 90.14: change `CAR_START` | |
| 6. Hand-over | done: clip 87.5-93.8 s (4.8 MB), stills at the widest (90.42) and the end (92.75), fragment | `media/reviews/v4/B/0130_car.mp4`, `0130_car_wide.png`, `0130_car_end.png`, `docs/revisions/v4/fragments/car.json` |
| 9. Sky fix (v4-B: the take's own gantry popped in the sky 89.50-89.80) | done, free: the sky left of the gantry and right of the mirror is held to the still (`media/shots/V2f3/wide_sky_left.png`, `cutouts.py`), she is drawn back over it from the take through its matte; frames 89.4-90.0 checked one by one; the left seam is gone. Clip re-rendered with the SFX mix |  |
| 8. Seedance take of the wide (Jade: "yes, do the $1.20 road motion take ... she's completely still"). `tools/v4B/car/vid.py submit v4B_car_wide` | done: take_1 ($0.60) kept (face and both pencils hold; road streams), engraved under flock -> `take_1_engraved.mp4` (+ `take_1_matte/`); it is the wide base in `car_shot.js` (`TAKE`; null = the still fallback); sky band keeps the still's gantry, mirror keeps the still + engine fleet. Clip re-rendered with the SFX mix | `media/gen/v4B_car_wide/`, `media/shots/V2f3/take_N.mp4` |
| 7. Animation (Jade: "would be better if it were animated (even if you could just feel the cars moving)") | done, free: `tools/v4B/car/cutouts.py` (cabin, gantry, three sedans, close on a reflected margin), `tools/v4B/car/fx_car.js` (strobes, light sweep), `car_shot.js` rewritten (ride as shot fx, endless road zoom under the cabin, gantry growing about the header line, cars sway/bob/drift/close in). SIRENS and IN MY MIRROR re-lettered with `tools/sectionA/modules/woodcut.js` (Jade: "SIRENS text should feel more woodblock textured"). Clip re-rendered with `--force` (frames cache does not see `tools/` changes) and the SFX mix muxed in | `media/reviews/v4/B/0130_car.mp4` (SFX), `0130_car_wide.png`, `0130_car_end.png` |

Spend so far: $1.27 (5 keyframes at $0.134, one Seedance take $0.60).
Checked at 540p: wheel and dash in frame, left-hand drive; mirror real-shaped and pushed into. SIRENS about 40 px tall
on the sign; `TVA 1729` about 70 px wide at the end, `TVA 4104` / `4096` about 45 px (they read, small). Weak: the picture
is still under the move (no road motion, strobes do not flash); for about 0.2 s around 91.8 a blurred border of the wide
shows round the mirror; the gantry is seen above the windshield header; the HUD (`C_hud_car`, to 90.14) and the
"back on the road" slam (to 89.40) still overlap the start of the shot (outside the rows this note may edit).
 Session stopped once at 17:44 on an API login error; resumed.

---

## The plan as shown to Jade

> 1:30 - are we in an impossible view here? because she's doesn't have a steering wheel. maybe we can use threejs
> and do an over the shoulder shot and look at her mirror in perspective? and maybe there can be some TVA markings
> on the license plates?

![contact sheet](../../../../media/reviews/v4/B/plans/car/contact_sheet.jpg)

Stills, numbers and three animatics with the song: `media/reviews/v4/B/plans/car/`. Blockout: `tools/v4B/car/`.

## What the blockout found

Yes, v3 is an impossible view. With the cabin built to scale and a 25 × 7 cm mirror that really reflects:

1. **A real mirror is small:** about 160 px wide at 540p from over her shoulder. A plate reads only when the
   mirror nearly fills the frame.
2. **A mirror set for her shows her face to a lens behind her shoulder,** not the road. Only from her own eye
   line does it show what is behind the car (top views on the sheet).
3. **A real mirror reverses the plate** (`9271 AVT`). The stills paint the agents' front plates in mirror-writing,
   like AMBULANCE, so they read `TVA 1729`, as the 0:26 shot already does.
4. **Her own boot lid hides the lead car's plate** inside about 7 m, which caps it at 87 px wide at 540p.

## Options

All three keep V2f1 (the river of sedans, 88.38–90.14) and replace only V2f2.

| | Shot | Mirror | Lead plate, 540p |
|---|---|---|---|
| **A** | Over her right shoulder: wheel, dash, both pencils, **her eyes in the mirror**. Cut to her eye line: the mirror at real size, pushing in until the fleet fills it. | As she would set it. Nothing faked. | 87 px |
| B | Same wide shot, the fleet in the mirror. Cut in between the front seats. | Turned 18.6° to the lens, as a film crew would. | 73 px |
| C | B as one take: hold wide, then push to the mirror. | As B. | 74 px |

**I recommend A:** nothing is faked, her eyes (colour) are in the first shot and what they see is in the second,
and the plate is biggest.

## Beats and words

- 90.14–91.02: over the shoulder. **SIRENS** (sung 90.19) on an overhead road sign, lettered like the Verse 1 signs.
- 91.02–92.79: the mirror. **IN MY MIRROR** (sung 91.09) on the mirror's lower edge. Then the L train lands as now.
- 91.02 is a tracked beat; no word is in two shots.

## Finishing

Recommended: **the blockout is the layout, the picture is generated**, as for the 0:35 ID shots. Blockout still +
canon sheets → keyframe → Seedance (720p, fixed camera) → `tools/engrave`. The push is an engine zoom (exact from a
fixed eye point). The plate is pinned with the 0:26 plate tool and the lyrics with the engine, so no lettering
depends on Seedance.

Alternative, held in reserve: the engraving shader straight on the 3D scene. Exact and free, but the car needs real
modelling, she would be a cutout, and it would not match the shots either side.

**Cost:** A or B about **$1.80, $3 with one retake of each shot**; C about $3 and the likeliest to fail. Cap: $6 of
the $15.

## Not working yet

- **SIRENS is small:** about 20–30 px tall at 540p. The windshield header limits a real sign.
- **Only the lead plate reads at 540p.** `TVA 4104`, `4096` and `0900` are too small, cut off or hidden.
- A's last frame is inside the mirror, and that shot has no Jade (no colour) for 1.8 s.
- In the wide shot her headrest hides most of her head.
- The blockout is boxes: it shows layout and timing, not the look. The image model may still draw right-hand
  drive or lose her eyes in so small a mirror.

## Questions for Jade

1. A, B or C?
2. SIRENS on a road sign, IN MY MIRROR on the mirror: is the split right, and is the sign big enough?
3. Plates at true size (only the lead car readable), or 1.5× as at 0:26? Mirror plates reading normally, as at 0:26?
4. Leave V2f1 alone, or start the interior at 88.38?

---

## For whoever builds it (not for the two-minute read)

- Re-render: `node tools/v4B/car/capture.mjs` (all stills, software GL, under a minute),
  `~/Documents/moongazing/.venv/bin/python tools/v4B/car/sheet.py`, `FRAMES_TMP=<dir> tools/v4B/car/animatic.sh A B C`.
  Scene: `tools/v4B/car/car_scene.html?opt=A|B|C&t=<song s>[&plates=true][&aim=driver|camera][&view=plan]`;
  cameras and timing are in `option()`. Do not set `TMPDIR` to a long path: Chrome aborts.
- Scale: +x front, +y up, +z passenger side, metres. Lens over her shoulder (-0.86, 1.17, 0.08), her eye
  (-0.17, 1.13, -0.36), mirror (0.38, 1.25, 0). The road bends left ahead so the sign clears the mirror.
- `render/timeline/C.js` after approval: split the `V2f2` row at 91.02 into two new clips (new folders beside
  `media/shots/V2f2/`, which stays), and replace `C_lyr_sirens` with a `pin` `sign` (90.14–91.02) and a `pin`
  `etch` (91.02–92.79), both `sync: 'lyric'`.
- Seedance 2.0 720p is $0.15/s (`media/gen/spend.jsonl`); keyframes ran $0.05–0.21 each in `media/shots/D7/NOTES.md`.
