# F7b: Her grin (198.48-199.38)

Waist-up, running at camera, grinning.

## Keyframe

Model: google/nano-banana-pro (2K, 16:9), $0.134 per image. Chosen: `kf_1`.

Prompt (last round):

```
Medium shot from the front-left, waist up: the anime girl runs toward the camera with a huge confident grin, long black hair whipping in the wind, yellow pencil in her raised hand, the colored city streaking past behind her. The world is the same M.C. Escher wood engraving as the third reference (crisp black ink line work, dense precise parallel hatching and cross-hatching that follows form), but now hand-colored: vivid colored-pencil color laid over the engraving in visible pencil strokes on warm off-white paper tooth - cobalt and ultramarine blue, vermilion, magenta, emerald, warm orange, sky blue - with the black hatching still showing through the color everywhere. Gustav Klimt gold-leaf accents (flat burnished gold with spiral and small square mosaic ornament) on select surfaces. Kandinsky shapes float in the sky: concentric circles, triangles, arcs and checkerboards in colored pencil. Hand-drawn, not a painting, no watercolor wash, no airbrush, no digital gradients, not photographic, not 3D. Every surface is now colored in saturated colored pencil over the hatching, with burnished Klimt gold leaf on rooftops, cornices and ornaments. The girl is a full-color anime character with clean cel shading, exactly matching the reference sheets: white cropped bomber jacket with an orange band across chest and arms, pale-blue dot patch on the left chest, round '1420 MHz' patch on the left sleeve, black crop top, navy wide cargo pants with orange straps, chunky white sneakers, orange headphones around her neck. Her long black hair is DOWN and loose (no bun), and she holds a yellow pencil in her hand. Reference images: the first two are the character sheets for the girl (match her face, outfit and long loose hair exactly); the third shows the engraving line technique of the world. Full bleed, edge to edge, no border, no margin, no paper edge, 16:9. No text, no letters, no numbers, no signature.
refs=['media/style_tests/refs/jade_pencil_flare_t2.jpg', 'media/style_tests/refs/jade_canon_turnaround.jpg', 'media/style_tests/world/3_loop_L_tracks_seedream-5-pro.jpg']
```

## Takes

- take_1: bytedance/seedance-2.0 720p 4 s, est $0.6, state done, first frame `media/shots/F7b/kf_1.jpg`. 
  - prompt: The girl runs toward the camera, grinning, hair whipping in the wind; the camera tracks backward in front of her, fast and handheld. Her face keeps the first frame's design, forehead smooth, brows relaxed, never a face close-up. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.
  - verdict: good; the pencil leaves her hand after frame 0 (not visible in 0.9 s). Used.
- take_2: bytedance/seedance-2.0 720p 4 s, est $0.6, state done, first frame `media/shots/F7b/kf_1.jpg`. polish: rainbows removed from keyframe (prompt of take 1)
  - prompt: The girl runs toward the camera, grinning, hair whipping in the wind; the camera tracks backward in front of her, fast and handheld. Her face keeps the first frame's design, forehead smooth, brows relaxed, never a face close-up. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.

Video cost for this shot: $1.20 (list-price estimate).

## Judgement



## chosen.json

```json
{
 "take": 2,
 "file": "media/shots/F7b/take_2_engraved_dered.mp4",
 "in_sec": 0.0,
 "out_sec": null,
 "rate": 1.0,
 "reverse": false,
 "notes": "her grin",
 "matte": "media/shots/F7b/take_2_matte/matte.mp4"
}
```

## v3 revision pass (2026-10-11, stream F)

Audit after Jade 3:21 (v2 had no bangs and a garbled roundel). Keyframe `kf_v3_F7b.jpg` (nano edit of `kf_clean.jpg`:
centre part and curtain bangs, mock neck, `1420 / MHz` roundel on her left sleeve, pale-blue dot on her left chest).
**take_3** (4 s) used from 0.05 s (Seedance repeats its first frame). Existing crop still covers the paper margin.
v2 take 2 kept.
