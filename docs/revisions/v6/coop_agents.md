# v6: the large agent's head in the co-op level (2:13)

Jade: "2:13 - there are a few frames where a larger agent's head is visible. Maybe the agents lag a little bit further behind?"

## What is visible

The head is in shot `C2a_swap` (132.26-133.56). Engine preview frames, film time:

| Film time | What shows |
|---|---|
| 132.708, 132.750, 132.792, 132.833 | a third agent's head, shoulder and outstretched arm grabbing at ORANGE's trailing sneaker |
| 132.917, 132.958, 133.042 | a floating head with sunglasses and one arm reaching down to the pencil beside her feet |
| 133.333 | a forearm and hand beside her rear foot |

The 0.5-scale agents layer (`agents/take_1.mp4`) never shows the head, so delaying the agents would not have fixed this. The head belongs to the leading agent in Seedance take `c2/take_1`, which is drawn at the take's full scale (twice the size of the agents layer). It shows up through ORANGE's own matte, `media/shots/C_coop/c2t1_L.mp4`. When `tools/v4B/coop/level.py` splits the girls from the agents, it keeps any matte pixel that touches a girl and lies within 281 px of her saturated colour. On take frames 17-28 and 37-38 the agent is lunging at her heel, so his head and arm fall inside that radius and are drawn as part of her. Her `srcTime` (take 0.15-1.9 over 1.30 s) maps those take frames to the film times above.

## Fix

- New `tools/v4B/coop/unleak.py`. It erases the agent from ORANGE's matte using hand-keyed polygons in source pixels, one per affected take frame (17-22, 24-26, 28, 37, 38). Frames 23 and 27 were already clean. Her rear sneaker, which his hands close around, is kept. The script writes `media/shots/C_coop/c2t1_Lc.mp4` (300 KB, gitignored like the rest of `media/`). Every other frame is `c2t1_L` unchanged. Run it with `tools/engrave/.venv/bin/python tools/v4B/coop/unleak.py`.
- `tools/sections/D/build_timeline.py`, C2a only: `girl("orange", "c2t1", "L", ...)` becomes `girl("orange", "c2t1", "Lc", ...)`, with a v6 comment. `render/timeline/D.js` was regenerated, and the only co-op change is that matte `src`. (C2b was switched to `Lc` too by the pencil-tip fix below.)
- The agents layer is unchanged (`AG_T`, `AG_X`, `AG_Y`), so the chase, the lunge at 132.70 and the see-saw throw at 134.00 play exactly as before. No agent delay was needed.

## Verification (preview 960x540, every frame 129.125-134.875)

A pixel diff of before against after shows that only the 8 frames listed above changed. C1, the rest of C2a and C2b are identical. Images are in the scratch folder (not in the repo):

- `/tmp/claude-1000/-home-jade-Documents-rewind-take-two/5c16a6f7-8726-4ff9-89a4-a5a70f33aa2b/scratchpad/coop/before_c2a.jpg` / `after_c2a.jpg`: every frame 132.625-133.250
- `.../coop/zoom_ba.jpg`: before/after pairs cropped on ORANGE at each affected frame
- `.../coop/before_full.jpg` / `after_full.jpg`: every third frame across 129.1-134.9
- `.../coop/leak_L.jpg`, `matte_check.jpg`: the take with ORANGE's matte overlaid (green = kept, magenta = erased)
- `.../coop/wip_tile_a.jpg`: frames from `deliverables/wip/rewind_v6_preview_540p_sfx.mp4`, where the issue was first located

# v6: the detached pencil tip (2:13-14)

Jade: "2:13-14 there's a frame or two where part of the tip of the pencil is detached and visible"

## What is visible

The tip shows in shot `C2b_letgo`, after the bridge swings up (the `pencil` layer reaches `UP` at 134.20). A loose pencil point lies on the far desk, left of the girl's heel at the far button:

| Film time | What shows |
|---|---|
| 134.417, 134.458 | the sharpened point, wood and lead, pointing at her sneaker |
| 134.500 | the lead tip alone |

The patch strips, `tail`, the hinge and the `pencil` sprite are not the cause. In Seedance take `c2/take_1` the pencil never rises, and its point touches the left girl's heel on take frames 106-108. `level.py` merged it into her matte, `c2t1_L`. While the bridge was down (C2a) it sat exactly over the sprite and could not be seen. Once the sprite is raised it shows up as a detached tip. I rendered every frame of 132.26-134.88 at preview size, and these 3 are the only frames where it is visible.

## Fix

- `tools/v4B/coop/unleak.py`: three more erase polygons, for take frames 106, 107 and 108 (around source x 1300-1440, y 595-665, stopping at her sneaker). This rebuilt `c2t1_Lc.mp4`.
- `tools/sections/D/build_timeline.py`: in C2b, `girl("orange", "c2t1", "L", C2BT, 0)` becomes `"Lc"`, with a v6 comment. `D.js` was regenerated.

## Verification (preview 960x540, every frame 132.292-134.875)

A pixel diff of before against after shows that only 134.417, 134.458 and 134.500 changed. The tip is gone and her sneaker is intact. The C2a agent fix above is unaffected.

- `/tmp/claude-1000/-home-jade-Documents-rewind-take-two/5c16a6f7-8726-4ff9-89a4-a5a70f33aa2b/scratchpad/coop/tip_ba.jpg`: before/after crops at 134.375-134.542
- `.../coop/tip_grid.jpg`: take frames 105-108 with the old matte overlaid (green)
- `.../coop/pb_a.jpg`, `pb_b.jpg`: every frame 132.292-134.875 before the fix
