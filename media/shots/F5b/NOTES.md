# F5b: The clock drips agents (187.08-190.58)

Deliberate wide at golden hour: ink drips turn into black-suited agents falling onto the rooftops; Jade small on a water-tower roof. Swell 189.54 gets a warm flash.

## Keyframe

Model: google/nano-banana-pro (2K, 16:9), $0.134 per image. Chosen: `kf_2`.

Prompt (last round):

```
Deliberate wide shot at golden hour: the colossal melting clock hangs over the whole Chicago Loop skyline like a second sun, its soft face draped over the skyscrapers; long drips of black ink run off its lower edge and each drip turns into a black-suited agent falling toward the rooftops. In the right foreground on a rooftop water tower, the anime girl stands seen from behind, small but clear, hair blowing, pencil in her hand, facing the clock. The world is the same M.C. Escher wood engraving as the third reference (crisp black ink line work, dense precise parallel hatching and cross-hatching that follows form), but now hand-colored: vivid colored-pencil color laid over the engraving in visible pencil strokes on warm off-white paper tooth - cobalt and ultramarine blue, vermilion, magenta, emerald, warm orange, sky blue - with the black hatching still showing through the color everywhere. Gustav Klimt gold-leaf accents (flat burnished gold with spiral and small square mosaic ornament) on select surfaces. Kandinsky shapes float in the sky: concentric circles, triangles, arcs and checkerboards in colored pencil. Hand-drawn, not a painting, no watercolor wash, no airbrush, no digital gradients, not photographic, not 3D. The clock is a colossal Salvador Dali melting pocket watch with a gold case, its face soft and drooping like warm cheese; the clock face is completely blank except simple short dash tick marks: no numerals, no Roman numerals, no letters. The agents are men in black suits, white shirts, black ties and black sunglasses with nearly blank faces, drawn as pure black-and-white engraving with no color at all: they are the only uncolored things in the picture. Every surface is now colored in saturated colored pencil over the hatching, with burnished Klimt gold leaf on rooftops, cornices and ornaments. The girl is a full-color anime character with clean cel shading, exactly matching the reference sheets: white cropped bomber jacket with an orange band across chest and arms, pale-blue dot patch on the left chest, round '1420 MHz' patch on the left sleeve, black crop top, navy wide cargo pants with orange straps, chunky white sneakers, orange headphones around her neck. Her long black hair is DOWN and loose (no bun), and she holds a yellow pencil in her hand. Reference images: the first is the character sheet for the girl (match her face, outfit and long loose hair exactly); the second shows the engraving line technique; the third shows the agents' design. Full bleed, edge to edge, no border, no margin, no paper edge, 16:9. No text, no letters, no numbers, no signature.
refs=['media/style_tests/refs/jade_pencil_flare_t2.jpg', 'media/style_tests/world/3_loop_L_tracks_seedream-5-pro.jpg', 'media/design/takes/agent_formation_nano_t1.jpg']
```

## Takes

- take_1: bytedance/seedance-2.0 720p 5 s, est $0.75, state done, first frame `media/shots/F5b/kf_2.jpg`. 
  - prompt: The colossal melting clock sags further over the skyline; thick drips of black ink stretch and fall from its lower edge and turn into black-suited agents tumbling down onto the rooftops; the girl's hair and jacket blow in the wind. Slow camera push-in toward the clock. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.
  - verdict: good drips and falling agents; the camera drifts right and crops Jade after ~3 s. Used 0-3.5 s.
- take_2: bytedance/seedance-2.0 720p 5 s, est $0.75, state done, first frame `media/shots/F5b/kf_2.jpg`. polish: rainbows removed from keyframe (prompt of take 1)
  - prompt: The colossal melting clock sags further over the skyline; thick drips of black ink stretch and fall from its lower edge and turn into black-suited agents tumbling down onto the rooftops; the girl's hair and jacket blow in the wind. Slow camera push-in toward the clock. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.

Video cost for this shot: $1.50 (list-price estimate).

## Judgement

Reads. Jade is small by design (the one deliberate wide).

## chosen.json

```json
{
 "take": 2,
 "file": "media/shots/F5b/take_2_engraved_dered.mp4",
 "in_sec": 0.0,
 "out_sec": null,
 "rate": 1.0,
 "reverse": false,
 "notes": "wide; ink drips become agents",
 "matte": "media/shots/F5b/take_2_matte/matte.mp4"
}
```

## v3 revision pass (2026-10-11, stream F)

Desk objects (Jade's idea, the establishing wide of the boss section). Keyframe `kf_v3_F5b.jpg` (nano edit of
`kf_clean.jpg`: a stack of giant books, leaning books, a mug of pencils, ink bottles and a ruler among the towers).
**take_3** (5 s) used from 0.05 s. v2 take 2 kept.
