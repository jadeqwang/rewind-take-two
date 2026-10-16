# v9 fix #4: twin colours by identity (C2a_swap end + C2b_letgo, 2:13.2-2:14.9)

Jade (verbatim): "4, 2:13.6-2:14.5, C2b_letgo (+C2a f3203-3205): Orange/blue twin colouring swaps between the girls
mid-stride when they cross (screen-side mattes); jackets mix both colours; a hard vertical seam cuts the leaping twin
half orange/half blue."

**Status: fixed in new source files; needs the timeline change below and the lead's integrated render.** Spend: $0
(no paid calls; tracking ran locally on the GPU). `tools/gen/spend.py` read $252.72 before and $260.78 after; the
difference comes from other agents running at the same time, and none of it is tagged `v9_4`.

## What was wrong

- Both girl layers in C2a_swap and C2b_letgo draw `c2t1_bo.mp4`. That file is the engraved take with the twin
  **right of a vertical seam** recoloured BLUE (`tools/v4B/coop/recolor.py` via `level.py`). Their mattes,
  `c2t1_R` / `c2t1_Lc`, are split at the same seam. This came from the v4 decision that "ORANGE is always screen-left
  of BLUE".
- In the take, ORANGE (the springer) **leaps over** BLUE (crouched on the far button) at take frames 40-50. So:
  - **f3203-3205:** the seam cut through the leaping girl. She came out half orange and half blue, with a straight cut
    across her arm and torso, blue headphones and blue lips.
  - **C2b:** after the jump cut ORANGE is on the right, so screen-side colouring painted the girl on the button (BLUE)
    orange and the runner (ORANGE) blue. The story has these the other way round: BLUE holds the far button and lets
    go.
  - **f3209-3217:** BLUE rises into ORANGE's silhouette, and the seam ran through both bodies, giving mixed jackets.
  - **f3225-3226:** as ORANGE ran out, the seam jumped and the left runner flipped from orange to blue mid-stride.

## What I made

New tool: `tools/v4B/coop/twins.py`.

1. **`track`** follows both girls through all 121 take frames with SAM 2.1 video (`facebook/sam2.1-hiera-large` via
   `transformers`, free download).
   - It is prompted with boxes on take frame 30 (ORANGE running in, BLUE crouched) and take frame 104 (BLUE on the
     left, ORANGE running out), and propagated both ways from each.
   - Each frame uses the nearer prompt.
   - Output: `media/shots/C_coop/c2t1_v9/track_{O,B}.npz`.
2. **`build`** gives every pixel of the existing girl matte (`c2t1_Lc | c2t1_R`, which already has the agent and
   pencil-tip clean-ups) to the girl whose track holds it:
   - The stronger track wins where both claim a pixel.
   - Pixels neither track claims go to the nearer track. That keeps ORANGE's head on take 100-103, which SAM misses.
   - It then recolours by owner: ORANGE's pale-blue bits turn orange and BLUE's orange bits turn blue, with the same
     colours and masks as `recolor.py`. Three refinements on top of that:
     - **Bun and pencils stay as drawn:** the top 16% of each girl's own *tracked* silhouette is left alone, so BLUE's
       bun pencils are wood again. In v8 they were tinted blue.
     - **Skin line art stays as drawn:** reddish-brown lips, eyelids and finger outlines sit in the orange hue range.
       Any orange blob whose surrounding ring (ink excluded) is mostly skin is left alone. Without this, BLUE had
       blue lips and fingers. This affected v8's BLUE too.
     - **C2a gap fill:** C2a draws BLUE 18 px lower than ORANGE (the held button), so an 18 px strip of paper opened
       where BLUE's head hid ORANGE at the leap. That strip (missing pixels with ORANGE directly above them) is added to
       ORANGE's matte and inpainted from ORANGE's own pixels. The fill lives in a separate file for her layer only, so
       BLUE's pixels are untouched.
   - From take 104 on, blobs larger than 8,000 px outside both tracks are dropped. This is the take's own untitled
     book slab, which `c2t1_R` had swallowed (take 107-108). It covered the v8 book title at f3226-3227, so the title
     now shows there.

New files (all gitignored media):

| File | Use |
|---|---|
| `media/shots/C_coop/c2t1_v9_bo.mp4` | the BLUE layer's `src` (16 MB, crf 12, 1920x1080, 121 frames) |
| `media/shots/C_coop/c2t1_v9_bo_O.mp4` | the ORANGE layer's `src` (as above, plus the C2a gap fill) |
| `media/shots/C_coop/c2t1_v9_B.mp4` | the BLUE layer's matte (luma) |
| `media/shots/C_coop/c2t1_v9_O.mp4` | the ORANGE layer's matte (luma) |
| `media/shots/C_coop/c2t1_v9/` | tracks (`track_{O,B}.npz`) and the PNG mattes (`O/`, `B/`) |

Rebuild: `tools/engrave/.venv/bin/python tools/v4B/coop/twins.py track && tools/engrave/.venv/bin/python
tools/v4B/coop/twins.py build`. Takes about 1 minute; it uses `gpulock`.

Note for anyone reusing `Sam2VideoProcessor.add_inputs_to_inference_session`: it empties the `obj_ids` list you pass
it, so pass a copy.

## How it was checked

I did not run render.mjs. I composited the girl layers myself, the way the engine does:
- plate_titled plus the button, strip, tail and hinge sprites;
- the per-frame `srcTime` mapping, taking source frame = floor(srcTime × 24);
- C2a's y offsets: BLUE +18, ORANGE +18 until 0.2 s and then 0.

Agents and the pencil sprite are left out. I stepped through every frame from f3175 to f3237, old against new, at
reduced size, with native-scale crops of 3200-3205, 3209-3220 and 3222-3231.

- `fix_4_f3205_before_after.jpg`: f3205. Before: the vertical seam through the leaper's arm, a blue jacket and
  headphones on ORANGE, blue lips and knuckles, and blue pencils on BLUE. After: ORANGE is all orange, BLUE all blue,
  no seam.
- `fix_4_c2b_before_after.jpg`: f3206-3229, v8 above and v9 below. In v9 BLUE (the girl who was on the button) stays
  blue from rising through the overlap to running out, and ORANGE stays orange. There are no mixed jackets and no flip
  at 3225-3226.
- `fix_4_stepthrough_before.jpg` / `fix_4_stepthrough_after.jpg`: every frame f3193-3237 (labels are film frame and
  take frame).

Colour continuity across the jump cut is now correct by identity. C2a ends with ORANGE (the springer) over BLUE, and
C2b opens with BLUE on the button on the left and ORANGE standing on the right. The C2b colours are therefore
**swapped compared with v8** (v8 had the button girl orange), which matches the beats in `docs/sections/D.md`: BLUE
holds the far button, ORANGE crosses, BLUE lets go.

## Exact timeline change

**`render/timeline/D.js`**, shots `C2a_swap` and `C2b_letgo` (four `src` lines in each shot, nothing else; in today's
file they are lines 4210/4230/4237/4261 and 4454/4468/4475/4489):

| Layer | Field | Old | New |
|---|---|---|---|
| `blue` | `src` | `media/shots/C_coop/c2t1_bo.mp4` | `media/shots/C_coop/c2t1_v9_bo.mp4` |
| `blue` | `matte.src` | `media/shots/C_coop/c2t1_R.mp4` | `media/shots/C_coop/c2t1_v9_B.mp4` |
| `orange` | `src` | `media/shots/C_coop/c2t1_bo.mp4` | `media/shots/C_coop/c2t1_v9_bo_O.mp4` |
| `orange` | `matte.src` | `media/shots/C_coop/c2t1_Lc.mp4` | `media/shots/C_coop/c2t1_v9_O.mp4` |

`srcTime`, `y`, `keepColor`, layer order and every other layer stay unchanged. C1_hold (`c1t2_*`) is not touched.

**`tools/sections/D/build_timeline.py`**, the source of D.js: `girl()` always builds `src` as `{take}_bo.mp4`. Give it
an optional source, then use it on lines 787 and 798:

```python
def girl(id_, take, side, sT, yk, start=None, src=None):
    L = dict(id=id_, type="video", src=src or f"{CO}/{take}_bo.mp4", keepColor=True, srcTime=sT, y=yk,
             matte=dict(src=f"{CO}/{take}_{side}.mp4", mode="luma"))
...
# v9 #4: twins coloured by identity (tools/v4B/coop/twins.py), not by screen side
girl("blue", "c2t1_v9", "B", C2T, held(None)), girl("orange", "c2t1_v9", "O", C2T, held(None, 0.20), src=f"{CO}/c2t1_v9_bo_O.mp4")   # C2a, line 787
girl("blue", "c2t1_v9", "B", C2BT, 0), girl("orange", "c2t1_v9", "O", C2BT, 0, src=f"{CO}/c2t1_v9_bo_O.mp4")                        # C2b, line 798
```

## What still looks wrong

- **The source take itself, f3205 (take 45):** ORANGE's torso mid-leap is an AI smear. Her chest and neck melt into a
  dark mass, and BLUE's bun pencils poke up into the inpainted strip under her jacket. The colour is right, but the
  drawing is mushy for that one frame, as it was in v8. Trimming C2a by one frame (end at 133.52) would hide it, but
  that also moves the jump cut, so I left it.
- **Faint skin tints:** a thin blue eyelid line on BLUE at f3209 (take 89), and a small blue fleck on her cheek by
  the hair at f3218. You only see them frame-stepping.
- **Pre-existing, not changed:**
  - The take's button disc is still inside the girl mattes on take 85-87 and 108, drawn over the button sprite as in
    v8.
  - ORANGE's head clips at the book edge as she exits (f3224-3226), as in v8.
- **Not in this check:** the agents and the pencil sprite were left out of my composite. My files do not touch either
  layer, but the lead's integrated preview is the first full view of 2:12-2:15 with everything.
