# stairs_v5: the impossible staircase on the near rooftop (v5, Jade 0:13 & 2:35), by v5-stairs

The square rooftop stairwell at lower left of the Bean's reflection is replaced by a Penrose staircase. **No model drew
the used stair**: it is a procedural drawing (`tools/v5/stairs/penrose.py`, no seed, deterministic), a real 3-D object
under an orthographic camera and z-buffer whose loop of four flights closes in the picture only because its end is
pushed along the view axis by the total climb. Parameters: `P` in penrose.py (`el 46, yaw 45, hand -1, size 0.97,
ring 0.30, steps 6/5/6/5, rise 0.05, base 0.04, ox 64, oy 52`). Rebuild (free):

    PY=~/Documents/moongazing/.venv/bin/python
    $PY tools/v5/stairs/penrose.py guide g16 && $PY tools/v5/stairs/comp.py g16_onplate.png g16 --wide

| File | What |
|---|---|
| `plate_close_1_stairs.png` | `plate_close_1.jpg` with only the stair region replaced (stair silhouette + 10 px, 4 px feather) |
| `plate_wide_v4_stairs_bean.png` | `plate_wide_v4_bean.png` with the stair pasted at the close plate's place (1350, 106), tight mask |
| `stairs_v5/overlay_S1.png`, `overlay_V3S.png` | 1920x1080 RGBA: the stair in each sing take's frame (fit on the rooftop: S1 s 0.731 (-67.5, -42.5), V3S s 0.734 (-68, -46)), tone matched per channel |
| `stairs_v5/g16_draw.png/.json` | the drawing (RGBA, plate px box) and its camera/geometry |
| `stairs_v5/check_*` | the take's frame 40 with the overlay, 1080 and 540 |
| `stairs_v5/cand_A1`, `cand_B1..B3` (+ .json: prompt, model `google/nano-banana-pro` 2K, refs, no seed) | rejected model passes: A1 (text only) drew an ordinary up-one-side-down-the-other stair; B1–B3 (restyle of the drawn guide) each "repaired" the seam, so the loop stopped being impossible. $0.67 in all (A1 was paid twice: a naming race overwrote the first) |

Timeline: `S1_wide` plays `media/shots/S1_wide/bg_1080_stairs/` (bg.py's push from the new bean plane); `S1_stairs`
and V3S `stairs` layers lay the overlay over the take.

## Round 2 (v5-stairs2): the 3:13 clock stair

Jade rejected the drawn stair ("not an actual impossible staircase") and asked for the clock stair at 3:13. The used stair
is now the F6b plate's stair (`media/shots/F6b/kf_v3_F6b_redraw_crop_dered.png`), cut out with the engine's exact block
faces and toned to grey engraving; no model, no redraw (`tools/v5/stairs2/comp.py --wide`, details in
`docs/revisions/v5/stairs.md`, Round 2).

| File | What |
|---|---|
| `plate_close_1_stairs_clock.png` | close plate: old stairwell removed (hatch lines continued), clock stair at (302, 1218), 325 px wide, with its plate shadow |
| `plate_wide_v4_stairs_clock_bean.png` | wide Bean plane with that patch; pushed frames `media/shots/S1_wide/bg_1080_stairs_clock/` |
| `stairs_v5/overlay_{S1,V3S}_clock.png` | the patch in each take's frame, tone matched |
| `stairs_v5/clock_lift.png`, `clock_mask_close.png`, `clock_geometry_check.png`, `clock_check_*` | the lifted stair, the changed-region mask, the exact tread outlines over the result, take stills |
