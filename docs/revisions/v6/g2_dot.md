# v6: G2's missing chest dot (Jade 2:24)

> "blue dot missing from front of jacket for just a little bit"

G2 (section E, 144.54-146.32; take 5, played from 0.68 s at 1.15x, so clip frames 16-65 are on screen) is the shot where
she pulls the pencil from her bun. Canon puts a pale-blue dot patch on her left chest, which is the viewer's right
jacket panel, just above the orange chest band. The dot is there in G1 (before) and G3 (after), but G2 take 5 never drew it.

## Fix

- **Output:** `media/shots/G2/take_5_engraved_patch_dot.mp4`. It is built on `take_5_engraved_patch.mp4`, so the
  `1420 / MHz` roundel fix is kept. The encode matches tools/sectionE/patchfix.py: libx264 preset slow, CRF 12,
  yuv420p, bt709, 24 fps, 121 frames.
- **Script:** `tools/sectionE/g2_dot.py`.
- **E.js:** `G_CLIPS.G2.src` points at the new file, with a v6 comment. The matte is unchanged.

**Placement.** I measured where the dot sits, frame by frame, in G1 take_3 and G3 take_5. Seven samples from each clip
all agree. The reference point is the band's inner end, where it meets the zip edge, on the band's top line:

| Measure | Value | Measured range |
|---|---|---|
| Diameter, as a multiple of the band's thickness | 1.00 | 0.97-1.02 |
| Centre, along the band from the reference point (in dot diameters) | 1.40 | 1.27-1.47 |
| Centre, above the band's top line (in dot diameters) | 0.77 | 0.75-0.81 |

So the dot sits about a quarter of its own width above the band.

In each G2 frame the script finds the band on that panel, fits its top line, inner end and thickness, and smooths those
over 9 frames. It then draws the dot with the rules above. The band was found in all 121 frames, so nothing was
interpolated. The dot follows the jacket's drift, the zoom-in and the band's tilt.

**Look.**
- **Colour:** flat pale blue. It starts at G1's dot colour, RGB (125, 166, 220), on G2's first on-screen frame and eases
  to G3's, (104, 147, 205), by the last, so neither cut changes the colour.
- **Edge:** the G1 and G3 dots have no black ink line. They have a thin rim, about 1-2 px, of slightly darker blue,
  so this dot has the same rim instead of a black outline. The edge is antialiased at 4x, with faint grain like the
  G1 and G3 dots.

**Occlusion.** The dot is only laid on jacket pixels: white or grey fold shading. Anything dark or saturated in front of
the jacket (hair, headphones, the top, ink, skin, the band) stays in front. In this take nothing passes in front of that
part of the chest: the pencil arm is on the other side and the hair falls behind her shoulders. So the dot is fully
visible in every frame, and that panel faces the camera throughout.

## Verification

The images are in the scratch folder, not the repo:
`/tmp/claude-1000/-home-jade-Documents-rewind-take-two/5c16a6f7-8726-4ff9-89a4-a5a70f33aa2b/scratchpad/g2/`

- **`g2_every3_before_after.jpg`:** every 3rd frame (0-120), chest crop, before and after, decoded from the encoded file.
- **`dots_ref.png`:** the G1 and G3 reference dots, zoomed.
- **`stills/`:** engine stills at preview size, at 144.458 (G1), 144.583, 144.708, 145.208, 145.708, 146.208, 146.292
  (G2) and 146.417 (G3).
  - **`stills/g2_stills_grid.jpg`:** all eight stills tiled.
  - **`stills/g2_cuts_zoom.jpg`:** the dot zoomed across both cuts.
    - G1 to G2: the dot is 22.3 px and then 22.7 px across in the 960 px preview, about 14 px apart, and the same colour.
    - G2 to G3: G3 is framed wider, and the dot keeps the same size relative to the band.
