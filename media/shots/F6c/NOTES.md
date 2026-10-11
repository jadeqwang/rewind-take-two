# F6c: Super Meat Boy replay (195.86-197.60)

Side-on sprint with a stream of colour ghost Jades running in step behind her (Super Meat Boy replay). 'never stop' (196.68) in pencil on the ground strip.

## Keyframe

Model: google/nano-banana-pro (2K, 16:9), $0.134 per image. Chosen: `kf_ghosts2 (take 2); kf_2 (take 1)`.

Prompt (last round):

```
ghosts
Side-on tracking shot, Super Meat Boy replay: the anime girl sprints extremely fast from left to right along the top of the elevated train tracks of the Loop, large in frame, mid-stride, long hair streaming behind her, pencil in her hand; running right beside and behind her in perfect step, a long stream of a dozen translucent glowing ghost copies of her, each tinted a different color (orange, sky blue, gold, magenta, emerald), overlapping like a motion trail, fading toward the left edge. The colored city behind them, elevated tracks with gold-leaf rivets. The world is the same M.C. Escher wood engraving as the third reference (crisp black ink line work, dense precise parallel hatching and cross-hatching that follows form), but now hand-colored: vivid colored-pencil color laid over the engraving in visible pencil strokes on warm off-white paper tooth - cobalt and ultramarine blue, vermilion, magenta, emerald, warm orange, sky blue - with the black hatching still showing through the color everywhere. Gustav Klimt gold-leaf accents (flat burnished gold with spiral and small square mosaic ornament) on select surfaces. Kandinsky shapes float in the sky: concentric circles, triangles, arcs and checkerboards in colored pencil. Hand-drawn, not a painting, no watercolor wash, no airbrush, no digital gradients, not photographic, not 3D. Every surface is now colored in saturated colored pencil over the hatching, with burnished Klimt gold leaf on rooftops, cornices and ornaments. The girl is a full-color anime character with clean cel shading, exactly matching the reference sheets: white cropped bomber jacket with an orange band across chest and arms, pale-blue dot patch on the left chest, round '1420 MHz' patch on the left sleeve, black crop top, navy wide cargo pants with orange straps, chunky white sneakers, orange headphones around her neck. Her long black hair is DOWN and loose (no bun), and she holds a yellow pencil in her hand. Reference images: the first two are the character sheets for the girl (match her face, outfit and long loose hair exactly); the third shows the engraving line technique of the world. Full bleed, edge to edge, no border, no margin, no paper edge, 16:9. No text, no letters, no numbers, no signature.
refs=['media/style_tests/refs/jade_pencil_flare_t2.jpg', 'media/style_tests/refs/jade_canon_turnaround.jpg', 'media/style_tests/world/3_loop_L_tracks_seedream-5-pro.jpg']
```

## Takes

- take_1: bytedance/seedance-2.0 720p 5 s, est $0.75, state done, first frame `media/shots/F6c/kf_2.jpg`. 
  - prompt: Side-on tracking shot: the girl sprints extremely fast from left to right along the tracks, long powerful strides, hair streaming; the camera tracks sideways with her at the same speed, keeping her in the same place in frame while the colored buildings scroll past quickly from right to left. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.
  - verdict: clean side-on sprint, but the engine ghost layer over it (her matte carries background) read as smeared afterimages. Replaced; take 1 lives on reversed as F7_08 (the rewind that paints).
- take_2: bytedance/seedance-2.0 720p 5 s, est $0.75, state done, first frame `media/shots/F6c/kf_2.jpg`. r2 ghost stream in the keyframe
  - prompt: Side-on tracking shot: the girl sprints extremely fast from left to right along the elevated tracks, long powerful strides, hair streaming; the stream of translucent colored ghost copies of her runs right behind her in perfect step, every ghost repeating her stride a moment later like a motion trail. The camera tracks sideways with her at the same speed, keeping her in the same place in frame while the buildings scroll past from right to left. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.
  - verdict: new keyframe kf_ghosts2 with the ghost stream drawn in: crisp colour ghosts in step behind her. Used (0.3-2.04 s).
- take_3: bytedance/seedance-2.0 720p 5 s, est $0.75, state done, first frame `media/shots/F6c/kf_2.jpg`. polish: rainbows removed from keyframe (prompt of take 2)
  - prompt: Side-on tracking shot: the girl sprints extremely fast from left to right along the elevated tracks, long powerful strides, hair streaming; the stream of translucent colored ghost copies of her runs right behind her in perfect step, every ghost repeating her stride a moment later like a motion trail. The camera tracks sideways with her at the same speed, keeping her in the same place in frame while the buildings scroll past from right to left. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.

Video cost for this shot: $2.25 (list-price estimate).

## Judgement

Take 2 replaces the engine-ghost version; the ghosts are drawn by nano and animated by Seedance, crisp and on-model.

## chosen.json

```json
{
 "take": 3,
 "file": "media/shots/F6c/take_3_engraved.mp4",
 "in_sec": 0.3,
 "out_sec": null,
 "rate": 1.0,
 "reverse": false,
 "notes": "take 2: side-on sprint with the ghost stream drawn in (keyframe kf_ghosts2); take 1 is reused reversed at F7_08 (the rewind that paints)",
 "matte": "media/shots/F6c/take_3_matte/matte.mp4"
}
```
