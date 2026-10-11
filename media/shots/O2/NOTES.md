# O2: Dawn: the defense (218.92-222.78)

Dawn hallway; she twists her hair up and pushes the pencil back in (New Game+), opens the door and walks in. A paper notice 'DISSERTATION DEFENSE / 9:00 AM' is corner-pinned on the door under the blank brass plaque (hand-keyed track in tools/sectionF/o2_plaque.json). Played at 1.3x so the door opens before the hard cut at 222.78.

## Keyframe

Model: google/nano-banana-pro (2K, 16:9), $0.134 per image. Chosen: `kf_1`.

Prompt (last round):

```
Dawn. A university hallway with tall arched windows pouring soft pink-gold dawn light across the floor: the anime girl, seen from behind at three-quarters, stands in front of a tall heavy wooden door with a small BLANK brass plaque on it (no writing on the plaque), her long black hair down, her yellow pencil in her right hand raised toward her hair. Large in frame, from the knees up. The world is the same M.C. Escher wood engraving as the third reference (crisp black ink line work, dense precise parallel hatching and cross-hatching that follows form), but now hand-colored: vivid colored-pencil color laid over the engraving in visible pencil strokes on warm off-white paper tooth - cobalt and ultramarine blue, vermilion, magenta, emerald, warm orange, sky blue - with the black hatching still showing through the color everywhere. Gustav Klimt gold-leaf accents (flat burnished gold with spiral and small square mosaic ornament) on select surfaces. Kandinsky shapes float in the sky: concentric circles, triangles, arcs and checkerboards in colored pencil. Hand-drawn, not a painting, no watercolor wash, no airbrush, no digital gradients, not photographic, not 3D. The colors are soft dawn colored pencil over engraved hatching, quiet and warm. The girl is a full-color anime character with clean cel shading, exactly matching the reference sheets: white cropped bomber jacket with an orange band across chest and arms, pale-blue dot patch on the left chest, round '1420 MHz' patch on the left sleeve, black crop top, navy wide cargo pants with orange straps, chunky white sneakers, orange headphones around her neck. Her long black hair is DOWN and loose (no bun), and she holds a yellow pencil in her hand. Reference images: the first two are the character sheets for the girl (match her face, outfit and long loose hair exactly); the third shows the engraving line technique of the world. Full bleed, edge to edge, no border, no margin, no paper edge, 16:9. No text, no letters, no numbers, no signature.
refs=['media/style_tests/refs/jade_pencil_flare_t2.jpg', 'media/style_tests/refs/jade_canon_turnaround.jpg', 'media/style_tests/world/3_loop_L_tracks_seedream-5-pro.jpg']
```

## Takes

- take_1: bytedance/seedance-2.0 720p 6 s, est $0.9, state done, first frame `media/shots/O2/kf_1.jpg`. 
  - prompt: The girl twists her long hair up into a loose bun with one hand and pushes the yellow pencil through it to hold it, then reaches out, pushes the heavy wooden door open and walks in. Static camera, soft dawn light slowly brightening. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.
  - verdict: hair-up + pencil at 2.4-3.6 s, door opens ~4.6 s. Used.

Video cost for this shot: $0.90 (list-price estimate).

## Judgement

Paper margin cropped.

## chosen.json

```json
{
 "take": 1,
 "file": "media/shots/O2/take_1_engraved_dered.mp4",
 "in_sec": 0.0,
 "out_sec": null,
 "rate": 1.3,
 "reverse": false,
 "notes": "dawn door: hair up + pencil at ~2.4-3.6 s source, door opens ~4.6 s",
 "matte": "media/shots/O2/take_1_matte/matte.mp4"
}
```
