# 1:30, the car: plan

**Status: plan and blockout ready for Jade.** Nothing spent, no shared file edited, nothing committed.
(v4-B sub-agent `v4B-car`, 2026-10-11.)

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
