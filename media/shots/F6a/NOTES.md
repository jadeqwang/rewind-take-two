# F6a: The loop gesture (190.58-194.10)

She sweeps the pencil in a circle; a gold line encircles the clock; the camera orbits with her arm.

## Keyframe

Model: google/nano-banana-pro (2K, 16:9), $0.134 per image. Chosen: `kf_2`.

Prompt (last round):

```
Low angle, medium-wide: the anime girl stands on the edge of a skyscraper roof, large in frame from the knees up, her right arm sweeping her yellow pencil in a huge circle above her head; a glowing gold line trails from the pencil tip and is drawing a perfect loop in the air around the colossal melting clock behind her in the sky. The world is the same M.C. Escher wood engraving as the third reference (crisp black ink line work, dense precise parallel hatching and cross-hatching that follows form), but now hand-colored: vivid colored-pencil color laid over the engraving in visible pencil strokes on warm off-white paper tooth - cobalt and ultramarine blue, vermilion, magenta, emerald, warm orange, sky blue - with the black hatching still showing through the color everywhere. Gustav Klimt gold-leaf accents (flat burnished gold with spiral and small square mosaic ornament) on select surfaces. Kandinsky shapes float in the sky: concentric circles, triangles, arcs and checkerboards in colored pencil. Hand-drawn, not a painting, no watercolor wash, no airbrush, no digital gradients, not photographic, not 3D. The clock is a colossal Salvador Dali melting pocket watch with a gold case, its face soft and drooping like warm cheese; the clock face is completely blank except simple short dash tick marks: no numerals, no Roman numerals, no letters. Every surface is now colored in saturated colored pencil over the hatching, with burnished Klimt gold leaf on rooftops, cornices and ornaments. The girl is a full-color anime character with clean cel shading, exactly matching the reference sheets: white cropped bomber jacket with an orange band across chest and arms, pale-blue dot patch on the left chest, round '1420 MHz' patch on the left sleeve, black crop top, navy wide cargo pants with orange straps, chunky white sneakers, orange headphones around her neck. Her long black hair is DOWN and loose (no bun), and she holds a yellow pencil in her hand. Reference images: the first two are the character sheets for the girl (match her face, outfit and long loose hair exactly); the third shows the engraving line technique of the world. Full bleed, edge to edge, no border, no margin, no paper edge, 16:9. No text, no letters, no numbers, no signature.
refs=['media/style_tests/refs/jade_pencil_flare_t2.jpg', 'media/style_tests/refs/jade_canon_turnaround.jpg', 'media/style_tests/world/3_loop_L_tracks_seedream-5-pro.jpg']
```

## Takes

- take_1: bytedance/seedance-2.0 720p 5 s, est $0.75, state done, first frame `media/shots/F6a/kf_2.jpg`. 
  - prompt: The girl sweeps her pencil in one huge circle above her head, the glowing gold line from its tip drawing a full loop around the giant clock in the sky; the camera orbits around her fast, in the same direction as her arm. Her face keeps the first frame's design, forehead smooth, brows relaxed, never a face close-up. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.
  - verdict: the gold line draws several loops rather than one, the camera swings round. Used.
- take_2: bytedance/seedance-2.0 720p 5 s, est $0.75, state done, first frame `media/shots/F6a/kf_2.jpg`. polish: rainbows removed from keyframe (prompt of take 1)
  - prompt: The girl sweeps her pencil in one huge circle above her head, the glowing gold line from its tip drawing a full loop around the giant clock in the sky; the camera orbits around her fast, in the same direction as her arm. Her face keeps the first frame's design, forehead smooth, brows relaxed, never a face close-up. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.
- take_3: bytedance/seedance-2.0 720p 5 s, est $0.75, state done, first frame `media/shots/F6a/kf_2.jpg`. r2: headphones on neck, pencil tip
  - prompt: The girl sweeps her pencil in one huge circle above her head, the glowing gold line from its tip drawing a full loop around the giant clock in the sky; the camera stays wide and slowly arcs around her, keeping her full body and the clock in frame. Her orange headphones stay around her neck the whole time. Her face keeps the first frame's design, never a face close-up. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.
  - verdict: round 2: headphones on neck, pencil tip, wide gold loop. Used 0-1.76 s.

Video cost for this shot: $2.25 (list-price estimate).

## Judgement

Good energy; 'a single loop' became several, acceptable.

## chosen.json

```json
{
 "take": 3,
 "file": "media/shots/F6a/take_3_engraved_dered.mp4",
 "in_sec": 0.0,
 "out_sec": null,
 "rate": 1.0,
 "reverse": false,
 "notes": "round 2: headphones on neck, pencil with tip; the gold loop round the clock",
 "matte": "media/shots/F6a/take_3_matte/matte.mp4"
}
```

## v3 revision pass (2026-10-11, stream F)

Audit after Jade 3:21. Keyframe `kf_v3_F6a_r2.jpg` (curtain bangs, mock neck, pale-blue eraser, thin rainbow-cored loop). **take_4** (4 s): used 0-1.15 s at 0.65x; it orbits behind her and softens after ~1.1 s. v2 take 3 kept.
