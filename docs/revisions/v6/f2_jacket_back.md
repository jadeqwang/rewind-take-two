# v6: jacket back (F2/F2b wall-run, plus the D lawn takes)

Jade's note 2:54: "jacket design should have no orange stripe visible on the back, but a large blue dot". Her follow-up on the real jacket: the orange band stops at the side seam under the arm and never continues onto the back. Frames where a raised arm or her hair hides the back don't need repainting.

Canon (O2, the turnaround sheets): the back is plain white, with one large pale-blue dot between the shoulder blades and orange only on the sleeves.

## Tool

`tools/jacket_back.py SPEC` reads one JSON spec per clip in `tools/jacket_back_specs/`. For each frame in `ranges` it does this:

1. **Back panel.** A polygon is built from keyframed points, with linear interpolation between keys:
   - `L`/`R` are the side seams at band height.
   - `TL`/`TR` are the tops of the seams, under the hair.
   - `BL`/`BR` are the hem-rib corners, joined by a curved bottom edge that follows the rib.
   - Keys can be absolute, or relative to the tracked centroid of the existing blue dot (`"anchor"`, used for B_lawn).
   - The polygon's sides are the seam lines, so the band ends sharply at the seam. The sleeve orange outside the polygon is not touched.
2. **Orange to white.** Pixels in the solid band are found, the area is grown by about 4 px to catch the pencil-texture specks, and every warm pixel inside it is recoloured:
   - The target colour is the median white of the jacket in that same frame.
   - Brightness comes from the band's own broad lightness, using a normalised blur of its red channel. Faint pencil streaks don't come through, but anything clearly darker (ink lines, folds, hair strands, the shadow side) keeps its own value. The shading and the ink survive and the band leaves no flat patch.
3. **Dot.** An ellipse sized from the seam-to-seam width (`dot_w` 0.23, `dot_aspect` 0.72), rotated with the shoulders and kept clear of the rib. It gets a thin dark ink ring (about 1.4% of the width).
   - Its fill is multiplied by the pixel's own shading.
   - It is painted only on bright jacket pixels inside the polygon, so hair and arms that cross in front stay in front.
   - A key can set `"hide": true` when the back is covered.

Encoding matches each source: same resolution, 24 fps, frame count, yuv420p, High profile.
- F2 uses crf 14, like `tools/sectionF/dered.py`.
- The lawn takes use crf 16 with `-tune grain +faststart`, like `tools/engrave/engrave.py`.

Review helpers: `--check FRAMES` draws the polygon and dot overlay, and `--compare FRAMES [--after-only] [--perframe WxH | --box ...]` makes before/after tiles.

## F2 / F2b (172.96–176.48)

- **Source:** `media/shots/F2/take_3_engraved_dered.mp4`, 121 frames.
- **On screen:** F2 uses frames 0–42 (clip_in 0, rate 1). F2b uses frames 78–120 (clip_in 3.24, rate 1, scale 1.12). No reverse, no matte on the plate.
- **Output:** `media/shots/F2/take_3_engraved_dered_back.mp4`, 121 frames, 1920x1080, h264 High.
- **Repainted:** frames 29–42 and 77–120.
  - Frames 0–28 are untouched. She is side-on or 3/4 from the front there, and the back isn't visible.
  - Frames 29–30: band removed, no dot. Her hair covers the middle of her back.
  - Dot visible on frames 31–42 and 77–120, except 87–88, where her hair swings across the back.
  - The dot always sits behind hair and arms. When her hair covers the panel, only the parts of the dot outside the hair show.
- **What the back looked like:** the source band is a flat cel orange of about (245,125,45), shaded down to about (150,50,10) on the far side. The back has soft grey cel shading and a few fold strokes, under a heavy black outline. In F2b the back is small (about 90–110 px across) and gets smaller as she recedes.
- **Ghosts left alone.** The pink ghost (left) and the green ghost (right) show the band only as a faint tinted stripe. Their translucency and glow aren't something I can hand-key convincingly in their tints, and at preview size they read as tinted silhouettes. If Jade wants them done, it needs the same spec approach with a tinted dot.
- **Wiring:** `tools/sectionF/edl.py` now sets `CHOSEN["F2"].file` to the `_back` file. Re-running edl.py rewrote `media/shots/F_edl.json`. Only the F2 and F2b `file` lines changed; today's edits (TVA REPORT, CASE 4,098, base 4098, O2 `_blue`) are kept. Of the `chosen.json` files, only `media/shots/F2/chosen.json` changed.

## D lawn takes (coordinator follow-up, same rule)

The live uses are all built by bclip() in `tools/sections/D/build_timeline.py`. `bclip()` now returns `*_engraved_back.mp4` for `BACK_FIXED = ("lawn", "lawn2")` (the mattes are unchanged). `sprite_of()` adds `_back` to the sprite cache name, so the ghost sprites rebake. D.js was regenerated: before my change it reproduced byte-for-byte; afterwards the only differences are these `src` paths and the two new sprite names.

- **B_lawn** (`media/shots/B_lawn/take_1_engraved_back.mp4`, 121 frames). Used at E2_06_lawn 115.67–116.03 and E7_06_lawn 138.38–139.00 (the plate, the jade layer and the ghost fan), and by the lawn ghost sprite at 0.75 s.
  - The big dot was already there. Only the band across the back (below the dot) was removed, cut at the side seams.
  - Repainted frames 10–58, which covers every frame those shots use. Frames 0–9 are a side view and untouched.
  - Keys are relative to the tracked dot.
- **B_lawn2** (`media/shots/B_lawn2/take_1_engraved_back.mp4`, 97 frames). Used at E2_07_lawn2 116.03–116.52 (source frames about 19–31), and by the lawn2 ghost sprite at 1.30 s.
  - Seen 3/4 from behind. The back panel reads on frames 17–33, and those are the frames repainted.
  - Band removed. A flattened dot (aspect 0.5) was added in B_lawn's own dot style, (118,171,219) with no ink outline, so it matches the take it's cut against.
- **Live g1/g2 (98.28–102.46, `_B_gunfire.js`):** these use the B_g* plates, not B_lawn. In the engine stills, g2 already shows the big dot and no band on her back. In g1 she is tiny, with white on the back and orange only on the sleeves. Nothing was changed there; the `_B_verse2.js` lawn blocks are dead code.

## Other section F shots (169.4–226) with her back and the band

None found. From 0.5 s contact sheets of the preview plus full-size checks:
- F1, F4 and F6a show the front.
- F3 shows her inverted, front and side.
- F6c, F7a and F7_08 are side-on.
- F5b (187.08) and O2 (218.92) show the back with the dot and no band, which is correct.

## Images (scratch: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/5c16a6f7-8726-4ff9-89a4-a5a70f33aa2b/scratchpad/f2back/)

- `tile_F2_every3rd_30-42.jpg`, `tile_F2b_every3rd_78-99.jpg`, `tile_F2b_every3rd_102-120.jpg`: before/after, zoomed on her back.
- `stills/` and `stills_sheet.jpg`: engine preview stills at 173.2, 174.0, 174.9, 175.8 and 176.3.
- `tile_B_lawn_every3rd_10-58.jpg`, `tile_B_lawn2_every2nd_17-33.jpg`: before/after tiles for the lawn takes.
- `stillsD/` and `stillsD_sheet.jpg`: engine stills at 115.75–116.7 and 138.5/138.85. `stillsG/` and `stillsG_zoom.jpg`: g1/g2.
- `chk/ghosts.jpg`: the ghosts' backs, for reference.
