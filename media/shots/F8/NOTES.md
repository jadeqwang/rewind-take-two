# F8: The committee (209.90-211.64)

She stops center frame, breathing; ghost Jades in a line behind her. 'never stop' (210.77) in pencil in the sky. Band out 210.90.

## Keyframe

Model: google/nano-banana-pro (2K, 16:9), $0.134 per image. Chosen: `kf_1`.

Prompt (last round):

```
Calm, center frame, full body: the anime girl stands still on the elevated train tracks facing the camera, breathing, catching her breath, long hair moving in the wind, pencil held loosely in her hand, a quiet small smile. Behind her, in a single straight row across the tracks, stand a line of translucent glowing ghost copies of her, each tinted a different color (orange, sky blue, gold, magenta, emerald), like a committee. The world is the same M.C. Escher wood engraving as the third reference (crisp black ink line work, dense precise parallel hatching and cross-hatching that follows form), but now hand-colored: vivid colored-pencil color laid over the engraving in visible pencil strokes on warm off-white paper tooth - cobalt and ultramarine blue, vermilion, magenta, emerald, warm orange, sky blue - with the black hatching still showing through the color everywhere. Gustav Klimt gold-leaf accents (flat burnished gold with spiral and small square mosaic ornament) on select surfaces. Kandinsky shapes float in the sky: concentric circles, triangles, arcs and checkerboards in colored pencil. Hand-drawn, not a painting, no watercolor wash, no airbrush, no digital gradients, not photographic, not 3D. Every surface is now colored in saturated colored pencil over the hatching, with burnished Klimt gold leaf on rooftops, cornices and ornaments. The girl is a full-color anime character with clean cel shading, exactly matching the reference sheets: white cropped bomber jacket with an orange band across chest and arms, pale-blue dot patch on the left chest, round '1420 MHz' patch on the left sleeve, black crop top, navy wide cargo pants with orange straps, chunky white sneakers, orange headphones around her neck. Her long black hair is DOWN and loose (no bun), and she holds a yellow pencil in her hand. Reference images: the first two are the character sheets for the girl (match her face, outfit and long loose hair exactly); the third shows the engraving line technique of the world. Full bleed, edge to edge, no border, no margin, no paper edge, 16:9. No text, no letters, no numbers, no signature.
refs=['media/style_tests/refs/jade_pencil_flare_t2.jpg', 'media/style_tests/refs/jade_canon_turnaround.jpg', 'media/style_tests/world/3_loop_L_tracks_seedream-5-pro.jpg']
```

## Takes

- take_1: bytedance/seedance-2.0 720p 5 s, est $0.75, state done, first frame `media/shots/F8/kf_1.jpg`. 
  - prompt: The girl stands still, breathing hard, shoulders rising and falling, her hair and jacket moving gently in the wind; the translucent ghost copies behind her settle and stand still in a row. Locked-off static camera. Her face keeps the first frame's design, forehead smooth, brows relaxed, never a face close-up. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.
  - verdict: near-static breathing, hair moving. Used.
- take_2: bytedance/seedance-2.0 720p 5 s, est $0.75, state done, first frame `media/shots/F8/kf_1.jpg`. polish: rainbows removed from keyframe (prompt of take 1)
  - prompt: The girl stands still, breathing hard, shoulders rising and falling, her hair and jacket moving gently in the wind; the translucent ghost copies behind her settle and stand still in a row. Locked-off static camera. Her face keeps the first frame's design, forehead smooth, brows relaxed, never a face close-up. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.
- take_3: bytedance/seedance-2.0 720p 5 s, est $0.75, state done, first frame `media/shots/F8/kf_1.jpg`. r2: canon patches, pencil in hand
  - prompt: The girl stands still, breathing hard, shoulders rising and falling, her hair and jacket moving gently in the wind, the yellow pencil held loosely in her hand; the translucent ghost copies behind her settle and stand still in a row. Locked-off static camera. Her orange headphones stay around her neck the whole time. Her face keeps the first frame's design, forehead smooth, brows relaxed, never a face close-up. Keep the exact hand-drawn look of the first frame. No text, no letters, no logos, no watermark.
  - verdict: round 2: canon patches (pale-blue dot, 1420), no red, pencil in hand. Used.

Video cost for this shot: $2.25 (list-price estimate).

## Judgement

Paper margin cropped.

## chosen.json

```json
{
 "take": 3,
 "file": "media/shots/F8/take_3_engraved_dered.mp4",
 "in_sec": 0.2,
 "out_sec": null,
 "rate": 1.0,
 "reverse": false,
 "notes": "round 2 (review #7): canon pale-blue dot + 1420 patch, no red, pencil in hand; the committee",
 "matte": "media/shots/F8/take_3_matte/matte.mp4"
}
```
