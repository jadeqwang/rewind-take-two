# F3: Relativity flip (176.48-180.02)

Escher's Relativity hall in colour; she runs upside down on the underside of a staircase, agents (still pure black ink) tumble off. The engine snaps a 90-degree roll + zoom on the downbeat; Seedance adds a continuous roll.

## Keyframe

Model: google/nano-banana-pro (2K, 16:9), $0.134 per image. Chosen: `kf_2`.

Prompt (last round):

```
b
A scene from M.C. Escher's Relativity: an impossible hall of staircases and archways where gravity points in three directions. The anime girl, large in the center of frame, sprints along the UNDERSIDE of a staircase as if it were the floor (upside down relative to the rest of the hall), hair streaming, pencil in hand. Several black-suited agents lose their footing and tumble off other staircases, falling in different directions. The world is the same M.C. Escher wood engraving as the third reference (crisp black ink line work, dense precise parallel hatching and cross-hatching that follows form), but now hand-colored: vivid colored-pencil color laid over the engraving in visible pencil strokes on warm off-white paper tooth - cobalt and ultramarine blue, vermilion, magenta, emerald, warm orange, sky blue - with the black hatching still showing through the color everywhere. Gustav Klimt gold-leaf accents (flat burnished gold with spiral and small square mosaic ornament) on select surfaces. Kandinsky shapes float in the sky: concentric circles, triangles, arcs and checkerboards in colored pencil. Hand-drawn, not a painting, no watercolor wash, no airbrush, no digital gradients, not photographic, not 3D. The agents are men in black suits, white shirts, black ties and black sunglasses with nearly blank faces, drawn as pure black-and-white engraving with no color at all: they are the only uncolored things in the picture. The girl is a full-color anime character with clean cel shading, exactly matching the reference sheets: white cropped bomber jacket with an orange band across chest and arms, pale-blue dot patch on the left chest, round '1420 MHz' patch on the left sleeve, black crop top, navy wide cargo pants with orange straps, chunky white sneakers, orange headphones around her neck. Her long black hair is DOWN and loose (no bun), and she holds a yellow pencil in her hand. Reference images: the first is the character sheet for the girl (match her face, outfit and long loose hair exactly); the second shows the engraving line technique; the third shows the agents' design. Full bleed, edge to edge, no border, no margin, no paper edge, 16:9. No text, no letters, no numbers, no signature.
refs=['media/style_tests/refs/jade_pencil_flare_t2.jpg', 'media/style_tests/world/3_loop_L_tracks_seedream-5-pro.jpg', 'media/design/takes/agent_formation_nano_t1.jpg']
```

## Takes

- take_1: bytedance/seedance-2.0 720p 5 s, est $0.75, state done, first frame `media/shots/F3/kf_2.jpg`. 
  - prompt: Extremely fast: the girl sprints along the underside of the staircase, upside down, hair streaming; the black-suited agents lose their footing and tumble away, falling in different directions. The camera slowly rolls, rotating the whole impossible hall. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.
  - verdict: good: continuous camera roll, agents falling, Jade on-model. Used.

Video cost for this shot: $0.75 (list-price estimate).

## Judgement

One of the strongest shots. Paper margin cropped (5.6%).

## chosen.json

```json
{
 "take": 1,
 "file": "media/shots/F3/take_1_engraved.mp4",
 "in_sec": 0.0,
 "out_sec": null,
 "rate": 1.0,
 "reverse": false,
 "notes": "Relativity hall; the engine snaps a 90-degree roll on the downbeat",
 "matte": "media/shots/F3/take_1_matte/matte.mp4"
}
```
