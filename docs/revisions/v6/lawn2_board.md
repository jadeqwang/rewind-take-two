# v6: the notice board at 1:41 (Jade: she clips through the sign)

> "1:41 - across the field of grass - she appears to somewhat clip through the sign as she runs past it. one solution
> may be for the sign to be further away visually (in 3d space) so that she doesn't clip"

## Which shot

On screen at 100.70-102.46 is **`B2_G2`** (`g2()` in `render/timeline/_B_gunfire.js`), the long lens from behind the
three agents. `B2_lawn2` in `_B_verse2.js` is dead code: `V4_GUN = true` replaces it (and `B2_lawn`, `B2_ear`) with
`gunfireShots()`. `_B_verse2.js` is not touched by this fix.

## Diagnosis

- The plate (`media/shots/B_g2clean/take_1_engraved.mp4`, an agents-only take) has the notice board drawn in. The camera
  is locked and the board is static: the panel box is x 962-1350, y 330-594. The posts are at x 1000-1022 and 1288-1310,
  and their feet stand on the turf at **y ~709**, with a cast-shadow band at y 686-718. The rest of the plate boils.
  Grass and wall change about 16-23 grey levels per frame. The board changes 0.3.
- Jade is not in the plate. She is a cut-out from `B_g1world`, placed on a laid-out feet path. Her scale comes from the
  plate's ground (`hgt(y) = 1.33 (y - 523)`, so the horizon is at y 523), and she is drawn over the board.
- Her feet run y 762 → 732 on the first leg and **y 727 → 683 on the second** (after ~101.4). While she is over the
  board on the first leg, her feet sit only 23-53 px below the posts' foot line, so she is barely nearer than the
  board. On the second leg they go from 18 px below the line to 26 px *above* it (y 694-683 from ~101.9). There she is
  level with or behind the board on the turf, yet drawn in front of it. Her head and torso also cover the lower half
  of the panel. With nothing on screen to say which is nearer, she reads as clipping through it. This shows most from
  ~101.4 to the end of the shot (frames 2434-2458).
- Her matte is not at fault: it is the whole cut-out, and none of the board is in it.

## Fix (Jade's direction: the board further back)

1. **Clean plate and new board, per source frame** (`tools/v4B/gunfire/g2_board_v6.py`, output
   `media/shots/B_g2clean/v6_board/f0000-f0074.png`, RGBA with an alpha PNG sequence, 17 MB, plus `v6_board.json`):
   - **Sky and far turf** left of the hotel wall come from the same rows 200 px to the left, from plate+noC. That region
     is static under the noC patch anyway.
   - **The hotel's side wall** behind the board is a piecewise remap: each hidden window bay is mapped onto bay 4's
     window, and each pier onto the 4/5 pier, with the rows scaled about the wall foot so the bays match the arches
     visible above the old board. The source is that same frame only when B's arm is clear of the source bays (x
     1338-1432, y 285-612). Otherwise it comes from a cycling pool of clean frames (source 0-6 and 14-17), so the fill
     still boils (v6b).
   - **Posts and their shadow band** are filled with the turf beside or below them, from the same frame. In frames
     where B's hand is near, they come from the nearest frame without it (v6b).
   - **The board** is the plate's own engraved board (panel and posts), scaled to **0.70** with its feet on the turf at
     **y 635** (it was 709). The new panel is [990, 370]-[1262, 555]. On this ground that puts it about 1.7x further
     away. The old cast-shadow band is scaled and multiplied in at the new feet as the contact shadow.
   - **B's hand** reaches over the board, the posts and the shadow band in source frames 18-26 (about 100.95-101.25).
     There the overlay keeps the plate, using a foreground mask over the whole board area down to the shadow band
     (v6b). The hand stays in front and whole.
2. **`g2()`**:
   - The `board_v6` video layer (`alpha: true`, the plate's `srcTime`) sits over noC.
   - The lyric pin moves to the new text quad [1006, 381]-[1244, 489]. The word times are unchanged.
   - The holes (r 8) are re-aimed. Each round still passes through the empty chest-high spot. It then carries on to
     the board's depth: along the 3D line, screen position is affine in inverse depth, and inverse depth on this ground
     is proportional to (feet y - 523), with C's feet at ~945. The holes land at (1157, 528) and (1155, 522), on the
     blank lower part of the panel below the lyric. The misses aim at these points (`targets: [H[k]]`), so the trace
     lines still end in the board.
3. **noC patch (v6b):** `B_g2noC/patch_v6.png` is `patch.png` made fully opaque from x 538, with an 8 px feather from
   x 530 (made by `noc_v6()` in the same script). `g2()` now uses it.
4. **Unchanged:** timing, her path and take, C's arm spring and kickback, both shot times, the HILBERT billboard, and
   G1 and G3.

## v6b: Jade's "disembodied elbow" and "floating partial ghost arm on another agent"

Checked every frame of the shot (2417-2458). Each agent's arm was zoomed, before and after.

- **B, a second, detached arm** (my v6 bug), film frames **2431-2458** (101.29 to the end of the shot). The wall fill
  is remapped from bays 4/5. From source frame ~26, B's raised arm is in those bays, so each frame copied a piece of
  his sleeve and elbow onto the hidden bays left of him. Fix: a frame is a wall source only if nothing moves in the
  source bays; otherwise it comes from the clean pool.
- **B, the hand cut to bare finger outlines** (my v6 bug), film frames **2427-2428** (101.12-101.17). His hand dips to
  y ~700 by the right post. The foreground mask stopped at y 624, so the post and shadow fill painted turf over most of
  the hand. Fix: the mask now runs down to the shadow band (y 724) and from x 1180, and the post and shadow turf comes
  from a frame without the hand.
- **C, a see-through ghost arm** (from v4c, not from v6), film frames **2417-2458** (the whole shot). noC's left edge
  feathers in over x 525-570, which is exactly where the take's own C hangs his left arm (x ≥ ~540). His arm showed
  through at 10-80% beside the cut-out C. Above the horizon, the gap between A's elbow (x ≤ ~529) and that arm is
  x 530-539. `patch_v6.png` is opaque from x 538 and feathers 530-538, so the ghost is gone and A is untouched.
- **A** and **C's cut-out arm** were fine in every frame.

Result: her feet are now always 48-127 px below the board's foot line (683-762 against 635). She is drawn fully in
front of the board, and she now stands taller than the whole board, so depth and occlusion agree in every frame.

## Notes and trade-offs

- **The two holes now almost coincide** (about 6 px apart), which is the honest geometry: both lines converge at the
  board's depth. It reads as one hole hit twice; the old version showed two separate holes. If two holes are wanted,
  the board could stand a little nearer or the second chest spot could move, but either breaks the "through the spot
  she left" line.
- The lyric is smaller (the text quad is 238×108, down from 340×154). It is still legible at preview size.
- The sky and far turf fill is static, like the noC region next to it. The wall, posts and shadow fill boil with the
  plate.
- This is not new: the faint light seam at x ~960-990 near C's pistol is the v4c noC patch edge, and it is the same
  in the before frames.

## Files

- `render/timeline/_B_gunfire.js`: `g2()` only (the `H` computation, the `board_v6` layer, the pin quad, the hole radius,
  and in v6b the noC source `patch_v6.png`).
  The 1:42 agent's g3() edits are kept.
- `tools/v4B/gunfire/g2_board_v6.py`: new. Run it with `tools/engrave/.venv/bin/python tools/v4B/gunfire/g2_board_v6.py
  [--frames 75] [--check DIR]`.
- `media/shots/B_g2clean/v6_board/` and `media/shots/B_g2clean/v6_board.json`: new and gitignored. These are in the
  plate's own folder, not `B_lawn2`, because `B_lawn2` is not used. `media/shots/B_g2noC/patch_v6.png` is new in v6b
  (4.9 MB).

## Review images (preview 960x540, scratch)

`/tmp/claude-1000/-home-jade-Documents-rewind-take-two/5c16a6f7-8726-4ff9-89a4-a5a70f33aa2b/scratchpad/lawn2/`
- `before_after_every2.jpg`: every 2nd frame, 2417-2457, before | after, full frame.
- `before_after_every2_zoom.jpg`: the same frames cropped to the board.
- `after_zoom.jpg` and `hand_zoom.jpg`: closer looks at the shots and at B's hand over the new board.
- `before_after_every2_Barm.jpg`: the same frames cropped to B's arm (v6b).
- `ghostC.jpg`: before (top) and after (bottom) of the area left of C, every 3rd frame (v6b).
- `elbow_after_sheet.jpg`: every frame 2422-2442, B's arm, after v6b. `armsC.jpg` and `armsAC.jpg`: C and A, every 2nd
  frame.
- `before/` and `after/`: all 42 frames (`after/` is v6b).
