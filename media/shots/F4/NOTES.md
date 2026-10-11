# F4: Bean dive (180.02-183.56)

She dives head-first at Cloud Gate; her colour reflection rushes up; she hits the mirror on 183.56 (white flash into the boss).

## Keyframe

Model: google/nano-banana-pro (2K, 16:9), $0.134 per image. Chosen: `kf_1`.

Prompt (last round):

```
Looking down from high above and just behind the diving girl: the anime girl dives head-first straight down, arms stretched forward, long hair streaming up toward the camera, large in the top half of frame; far below her, the mirror-polished Cloud Gate sculpture (the Bean) in Millennium Park, and in its curved mirror surface her own full-color reflection dives up toward her. The colored skyline curves around the edges of the mirror. The world is the same M.C. Escher wood engraving as the third reference (crisp black ink line work, dense precise parallel hatching and cross-hatching that follows form), but now hand-colored: vivid colored-pencil color laid over the engraving in visible pencil strokes on warm off-white paper tooth - cobalt and ultramarine blue, vermilion, magenta, emerald, warm orange, sky blue - with the black hatching still showing through the color everywhere. Gustav Klimt gold-leaf accents (flat burnished gold with spiral and small square mosaic ornament) on select surfaces. Kandinsky shapes float in the sky: concentric circles, triangles, arcs and checkerboards in colored pencil. Hand-drawn, not a painting, no watercolor wash, no airbrush, no digital gradients, not photographic, not 3D. The girl is a full-color anime character with clean cel shading, exactly matching the reference sheets: white cropped bomber jacket with an orange band across chest and arms, pale-blue dot patch on the left chest, round '1420 MHz' patch on the left sleeve, black crop top, navy wide cargo pants with orange straps, chunky white sneakers, orange headphones around her neck. Her long black hair is DOWN and loose (no bun), and she holds a yellow pencil in her hand. Reference images: the first two are the character sheets for the girl (match her face, outfit and long loose hair exactly); the third shows the engraving line technique of the world. Full bleed, edge to edge, no border, no margin, no paper edge, 16:9. No text, no letters, no numbers, no signature.
refs=['media/style_tests/refs/jade_pencil_flare_t2.jpg', 'media/style_tests/refs/jade_canon_turnaround.jpg', 'media/style_tests/world/3_loop_L_tracks_seedream-5-pro.jpg']
```

## Takes

- take_1: bytedance/seedance-2.0 720p 5 s, est $0.75, state done, first frame `media/shots/F4/kf_1.jpg`. 
  - prompt: Extremely fast: the girl dives straight down toward the mirror-polished Bean; the camera plunges down right behind her; the Bean and her own reflection rush up to fill the frame until her outstretched hands touch her reflection. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.
  - verdict: first 2 s good, then Seedance cut to a photographic street and a face close-up with a hand over the face: rejected after 2.0 s.
- take_2: bytedance/seedance-2.0 720p 5 s, est $0.75, state done, first frame `media/shots/F4/kf_1.jpg`. r2 plunge into mirror
  - prompt: Extremely fast: the girl falls head-first straight down toward the mirror-polished Bean, growing larger as the Bean rushes up toward her; her own reflection in the curved mirror rises to meet her, and her hands touch the mirror surface, which ripples like liquid silver as she plunges into it. The camera follows straight down behind her, same high angle all the way. The drawing never turns photographic: keep the exact hand-drawn look of the first frame, colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. Never a face close-up. No text, no letters, no logos, no watermark.
  - verdict: dive, hands touch her reflection at ~3 s, she plunges into concentric ripples and vanishes by 5 s. Used at 1.3x.

Video cost for this shot: $1.50 (list-price estimate).

## Judgement

Take 2 is exactly the inverse-of-S2 beat: the mirror becomes liquid and takes her into the boss fight on 183.56.

## chosen.json

```json
{
 "take": 2,
 "file": "media/shots/F4/take_2_engraved.mp4",
 "in_sec": 0.0,
 "out_sec": null,
 "rate": 1.3,
 "reverse": false,
 "notes": "take 2: dive, touches her reflection at ~3 s, plunges into concentric ripples",
 "matte": "media/shots/F4/take_2_matte/matte.mp4"
}
```
