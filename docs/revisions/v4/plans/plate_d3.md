# v4 / B — D3 licence plate `TVA 1729` (note 0:26)

Status: done (v4B-plate, 2026-10-11). Not committed (`v4-B` commits). Spend: $0.

> 0:26 - maybe the plate on the car can say TVA (and some numbers – what would be some good 4 digit numbers here?)

Decided: the plate reads `TVA 1729` (1729, the Hardy–Ramanujan taxicab number). Shot D3, 25.34–28.40 s.

## Result

The sedan's front plate in the wing mirror now reads `TVA 1729`, right-reading, for the whole shot.

- **Reads at 540p: yes, but small.** The plate is 49×21 px at 960×540, capitals 13 px tall. It reads in every frame
  I checked from the encoded clip, in the unlit and the lit phases. A first-time viewer who looks at the car gets it
  in under a second. The lyric being etched in the same mirror competes for the first two seconds, so I expect most
  viewers to catch `TVA` and fewer to catch the number. On a phone it is a pause-to-read detail.
- **Legibility level: (a).** At the take's own plate size (33×8 px at 540p) the text is 4 px tall and cannot be read.
  At 1.5× the take's width with a US-plate shape (2.3:1) it reads, so that is what is in the film.
- **Level (b) was built and not shipped.** A slow push toward the mirror (1.0 → 1.22) makes the plate 60 px wide.
  Her face and the etched lyric survive, but her bun with the two crossed pencils leaves the frame and the
  headphones are half cut, and the pencils in this shot were Jade's own v3 note. Clip for comparison:
  `media/reviews/v4/B/0026_plate_alt_push.mp4` (+ `.jpg`), timeline `tools/v4B/plate/_d3_push.js`. To ship it, copy
  `PUSH` and `D3_CAM` from that file into `render/timeline/A.js`, spread `D3_CAM()` into `vid('D3', …)`, spread
  `D3_CAM(3, 27)` and `D3_CAM(0, 24)` into the two etch layers in place of their `x`/`y`, and pass `cam: D3_CAM()`
  in the plate's params.
- **Level (c)** (a new keyframe with the sedan closer) was not needed.

## Hand-over files

| | |
|---|---|
| After clip (960×540 H.264 + AAC, 24.5–29.2 s, 3.7 MB) | `media/reviews/v4/B/0026_plate.mp4` |
| 540p still at 27.0 s | `media/reviews/v4/B/0026_plate.jpg` |
| 3× crop of the mirror, same frame | `media/reviews/v4/B/0026_plate_mirror_3x.jpg` |
| Alternative with the push (not in the film) | `media/reviews/v4/B/0026_plate_alt_push.mp4`, `.jpg` |
| Track | `media/shots/D3/track_plate_v4.json`, check sheet `media/shots/D3/track_plate_v4.jpg` |

## What was done

1. **Track.** `tools/v4B/plate/track_plate.py` (run with `tools/engrave/.venv/bin/python`; it needs OpenCV). It tracks
   the raw take `media/shots/D3/take_2.mp4`, because the engraved take's line texture is fixed to the screen and does
   not move with the car. Matching is normalised cross-correlation on gradient magnitude against one lit and one unlit
   reference frame, for the whole front of the car and for the plate alone. The car hardly moves: ±0.4 px sideways and
   ±0.9 px up and down at 720p, so the track is a translation of the plate rectangle, smoothed over 5 frames. Output is
   in the engine's 1920×1080 design space (fit `cover`, the same mapping as `tools/sectionA/track_quad.py`), 121 keys,
   TL TR BR BL of the take's own plate (66×16.5 design px). The file also holds `light`, the brightness of the take's
   plate per frame: streetlights swing the car from unlit to lit twice during the shot.
2. **Plate module.** `tools/v4B/plate/plate.js`, a canvas module, reusable for other cars: `text` is a parameter
   (`'\n'` stacks two lines). Pale field, dark border with a slightly uneven hand-cut edge, squeezed Anton capitals,
   a few nicks in the letters, burin strokes along the foot. When `light` drops, the field is crossed by horizontal
   ink lines at the engraving's pitch instead of going grey. `grow` and `aspect` resize the tracked quad about its
   centre; `cam` takes the same numbers as a layer transform, so the plate can ride a push and still be drawn sharp.
   All parameters are listed in the file header. No engine module was changed.
3. **Timeline.** One layer added to the D3 entry of `render/timeline/A.js`, right after `vid('D3')` and before the two
   etch layers, which are untouched (4 lines with its comment):
   `{ type: 'canvas', module: 'tools/v4B/plate/plate.js', noRewind: true, params: { text: 'TVA 1729', corners: tracks.D3_plate, grow: 1.5, aspect: 2.3, dim: 0.12, light: [...] } }`.
   `dim: 0.12` keeps the plate bright when the car is unlit: with the default 0.4 the unlit plate was a grey slab that
   could not be read at 540p, and the car is unlit for about 60 % of the shot.
4. **Track constant.** One line added to `render/timeline/_A_tracks.js`: `D3_plate`, after `D3_etch` (line 9).
   That file is generated, so the same entry was added to `TRACKS` in `tools/sectionA/make_tracks.py` (one line);
   without it the next regeneration would drop `D3_plate` and break the D3 entry. I did not run the generator. I
   checked that it would write every existing entry exactly as it stands now.

## Checks

- Tracked quad drawn on the engraved take, 13 frames across the shot: on the plate in all of them.
- Frames pulled from the encoded after clip at 25.4, 25.8, 26.2, 26.6, 27.0, 27.4, 27.8 and 28.35 s, looked at 1:1:
  `TVA 1729` reads in each.
- The plate at 1080p pixel density (a 2× punch-in at preview size, the last variant of
  `tools/v4B/plate/_d3_test.js`): border, nicks and the unlit hatching hold up.

## Not right / to know

- The plate is about 1.6× the width a real plate would be on that car (28 % of the car's width against 17 %). It
  does not look wrong in the mirror, but it is a cheat.
- No 1080p render was made (pass rule). The 1080p look was judged from the punch-in only.
- `noRewind: true`, like the shot's etch layers: if D3 is replayed inside a rewind comp, the plate there is the
  take's blank one.
- Variant sheet for anyone tuning it: `tools/v4B/plate/_d3_test.js` (levels 0, a and b side by side, 4 s apart from
  t = 100; lit at +1.0 s, unlit at +2.0 s). `tools/v4B/plate/sheet.py` makes the crop sheets.
- `docs/revisions/v4/review_B.json` has no entry for this note: that file is `v4-B`'s.
