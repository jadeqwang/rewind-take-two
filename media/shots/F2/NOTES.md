# F2: Wall-run up the Willis Tower (172.96-176.48)

She runs up the tower face with two ghosts flanking (magenta, emerald), dragging a pencil line. Bar 100 is a 1.18x punch-in on the same take. 'never stop' (175.59) written in pale pencil on the glass.

## Keyframe

Model: google/nano-banana-pro (2K, 16:9), $0.134 per image. Chosen: `kf_2`.

Prompt (last round):

```
b
Dramatic low angle looking straight up the black steel facade of the Willis Tower (Sears Tower) against the sky: the anime girl runs vertically UP the face of the tower, her body perpendicular to the wall, feet planted on the facade, large in frame, long black hair streaming down behind her, her right hand dragging her yellow pencil along the wall so it leaves a bright orange-to-blue colored-pencil line in her wake. Flanking her on both sides two translucent glowing ghost copies of her, one tinted magenta, one tinted emerald green, run up the wall in step. The world is the same M.C. Escher wood engraving as the third reference (crisp black ink line work, dense precise parallel hatching and cross-hatching that follows form), but now hand-colored: vivid colored-pencil color laid over the engraving in visible pencil strokes on warm off-white paper tooth - cobalt and ultramarine blue, vermilion, magenta, emerald, warm orange, sky blue - with the black hatching still showing through the color everywhere. Gustav Klimt gold-leaf accents (flat burnished gold with spiral and small square mosaic ornament) on select surfaces. Kandinsky shapes float in the sky: concentric circles, triangles, arcs and checkerboards in colored pencil. Hand-drawn, not a painting, no watercolor wash, no airbrush, no digital gradients, not photographic, not 3D. The girl is a full-color anime character with clean cel shading, exactly matching the reference sheets: white cropped bomber jacket with an orange band across chest and arms, pale-blue dot patch on the left chest, round '1420 MHz' patch on the left sleeve, black crop top, navy wide cargo pants with orange straps, chunky white sneakers, orange headphones around her neck. Her long black hair is DOWN and loose (no bun), and she holds a yellow pencil in her hand. Reference images: the first two are the character sheets for the girl (match her face, outfit and long loose hair exactly); the third shows the engraving line technique of the world. Full bleed, edge to edge, no border, no margin, no paper edge, 16:9. No text, no letters, no numbers, no signature.
refs=['media/style_tests/refs/jade_pencil_flare_t2.jpg', 'media/style_tests/refs/jade_canon_turnaround.jpg', 'media/style_tests/world/3_loop_L_tracks_seedream-5-pro.jpg']
```

## Takes

- take_1: bytedance/seedance-2.0 720p 5 s, est $0.75, state done, first frame `media/shots/F2/kf_2.jpg`. 
  - prompt: Extremely fast: the girl runs straight up the vertical face of the skyscraper toward its top, her pencil dragging a glowing colored line along the wall behind her, the two translucent ghost copies running alongside in step. The camera rushes upward with them, looking up the tower. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.
  - verdict: Seedance turned the vertical facade into a tilted floor after ~1.5 s. Rejected for take 2.
- take_2: bytedance/seedance-2.0 720p 5 s, est $0.75, state done, first frame `media/shots/F2/kf_2.jpg`. r2 true wall-run
  - prompt: Extremely fast: the girl and her two translucent ghost copies sprint straight UP the vertical glass facade of the skyscraper, away from the camera, toward the top of the tower and the sky; gravity is sideways, their feet slam onto the wall with every stride, hair hanging down toward the camera. The camera is fixed to the wall below them, looking straight up the tower, and rushes upward after them. The colored line from her pencil streaks along the wall behind her. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.
  - verdict: true wall-run: they sprint up the facade away from camera, reach the top and launch off it. Used (0-1.76 for bar 99, 3.24-5.0 for bar 100).

Video cost for this shot: $1.50 (list-price estimate).

## Judgement

Take 2 is a clean wall-run with the ghosts in step and the pencil line on the glass; bar 100 jumps to the top-of-tower launch.

## chosen.json

```json
{
 "take": 2,
 "file": "media/shots/F2/take_2_engraved.mp4",
 "in_sec": 0.0,
 "out_sec": null,
 "rate": 1.0,
 "reverse": false,
 "notes": "true wall-run up the tower (take 2); bar 100 jumps to 3.24 s (reaching the top and launching off it) with a 1.12x punch-in",
 "matte": "media/shots/F2/take_2_matte/matte.mp4"
}
```
