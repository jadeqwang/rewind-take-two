# F5a: HERO: the boss (183.56-187.08)

Swell 183.72: airborne, a giant pencil drawn back like a sword, the colossal melting clock over the Loop dripping agents.

## Keyframe

Model: google/nano-banana-pro (2K, 16:9), $0.134 per image. Chosen: `kf_r2 (round 2)`.

Prompt (last round):

```
Hero shot, low angle, slow-motion moment: the anime girl is airborne in the left foreground, large in frame (head to knees), leaping upward, her yellow pencil drawn back over her shoulder in both hands like a sword about to strike, long black hair flying, determined. Behind and above her, filling the right half of the sky, the colossal melting clock hangs over the Chicago Loop skyline, drooping over the skyscrapers, tiny black-suited agents dripping off its melting edge like drops of ink. The world is the same M.C. Escher wood engraving as the third reference (crisp black ink line work, dense precise parallel hatching and cross-hatching that follows form), but now hand-colored: vivid colored-pencil color laid over the engraving in visible pencil strokes on warm off-white paper tooth - cobalt and ultramarine blue, vermilion, magenta, emerald, warm orange, sky blue - with the black hatching still showing through the color everywhere. Gustav Klimt gold-leaf accents (flat burnished gold with spiral and small square mosaic ornament) on select surfaces. Kandinsky shapes float in the sky: concentric circles, triangles, arcs and checkerboards in colored pencil. Hand-drawn, not a painting, no watercolor wash, no airbrush, no digital gradients, not photographic, not 3D. The clock is a colossal Salvador Dali melting pocket watch with a gold case, its face soft and drooping like warm cheese; the clock face is completely blank except simple short dash tick marks: no numerals, no Roman numerals, no letters. The agents are men in black suits, white shirts, black ties and black sunglasses with nearly blank faces, drawn as pure black-and-white engraving with no color at all: they are the only uncolored things in the picture. Every surface is now colored in saturated colored pencil over the hatching, with burnished Klimt gold leaf on rooftops, cornices and ornaments. The girl is a full-color anime character with clean cel shading, exactly matching the reference sheets: white cropped bomber jacket with an orange band across chest and arms, pale-blue dot patch on the left chest, round '1420 MHz' patch on the left sleeve, black crop top, navy wide cargo pants with orange straps, chunky white sneakers, orange headphones around her neck. Her long black hair is DOWN and loose (no bun), and she holds a yellow pencil in her hand. Reference images: the first is the character sheet for the girl (match her face, outfit and long loose hair exactly); the second shows the engraving line technique; the third shows the agents' design. Full bleed, edge to edge, no border, no margin, no paper edge, 16:9. No text, no letters, no numbers, no signature.
refs=['media/style_tests/refs/jade_pencil_flare_t2.jpg', 'media/style_tests/world/3_loop_L_tracks_seedream-5-pro.jpg', 'media/design/takes/agent_formation_nano_t1.jpg']
```

## Takes

- take_1: bytedance/seedance-2.0 720p 5 s, est $0.75, state done, first frame `media/shots/F5a/kf_2.jpg`. 
  - prompt: Slow motion: the girl rises through the air toward the giant melting clock, winding the pencil back over her shoulder like a sword about to strike, hair flowing; the clock drips slowly and tiny agents fall from its edge. The camera pushes in slowly and tilts up. Her face keeps the first frame's design, forehead smooth, brows relaxed, never a face close-up. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.
  - verdict: great: slow push-in, she winds the pencil back, clock drips. Used.
- take_2: bytedance/seedance-2.0 720p 5 s, est $0.75, state done, first frame `media/shots/F5a/kf_2.jpg`. polish: rainbows removed from keyframe (prompt of take 1)
  - prompt: Slow motion: the girl rises through the air toward the giant melting clock, winding the pencil back over her shoulder like a sword about to strike, hair flowing; the clock drips slowly and tiny agents fall from its edge. The camera pushes in slowly and tilts up. Her face keeps the first frame's design, forehead smooth, brows relaxed, never a face close-up. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.
- take_3: bytedance/seedance-2.0 720p 5 s, est $0.75, state done, first frame `media/shots/F5a/kf_2.jpg`. r2: pencil with tip, headphones on neck
  - prompt: Slow motion: the girl rises through the air toward the giant melting clock, winding the big yellow pencil back over her shoulder like a sword about to strike, its sharpened graphite tip catching the light, hair flowing; the clock drips slowly and tiny agents fall from its edge. The camera pushes in slowly and tilts up. Her orange headphones stay around her neck the whole time. Her face keeps the first frame's design, forehead smooth, brows relaxed, never a face close-up. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.
- take_4: bytedance/seedance-2.0 720p 5 s, est $0.75, state done, first frame `media/shots/F5a/kf_2.jpg`. r2: pencil with tip, headphones on neck
  - prompt: Slow motion: the girl rises through the air toward the giant melting clock, winding the big yellow pencil back over her shoulder like a sword about to strike, its sharpened graphite tip catching the light, hair flowing; the clock drips slowly and tiny agents fall from its edge. The camera pushes in slowly and tilts up. Her orange headphones stay around her neck the whole time. Her face keeps the first frame's design, forehead smooth, brows relaxed, never a face close-up. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.
  - verdict: round 2: pencil with eraser and graphite tip, headphones on neck; winds back and strikes. Used 1.4-4.9 s.

Video cost for this shot: $3.00 (list-price estimate).

## Judgement

The pencil is oversized (anime sword exaggeration); deliberate. Clock face has dash ticks only, no numerals.

## chosen.json

```json
{
 "take": 4,
 "file": "media/shots/F5a/take_4_engraved_dered.mp4",
 "in_sec": 1.4,
 "out_sec": null,
 "rate": 1.0,
 "reverse": false,
 "notes": "round 2 (review #10): a real pencil with eraser and sharpened graphite tip, headphones on her neck; winds back and strikes at the clock (1.4-4.9 s)",
 "matte": "media/shots/F5a/take_4_matte/matte.mp4"
}
```

## v3 revision pass (2026-10-11, stream F)

Jade 3:05. Keyframes `kf_v3_F5a_a_r2.jpg` (wind-up; rainbow pencil with pale-blue eraser and rainbow core, curtain bangs, mock neck, desk objects in the skyline) and `kf_v3_F5a_b.jpg` (the swing has become drawing), nano-banana-pro edits, prompts in `kf_prompt.txt` and `tools/sectionF/v3.py`. **take_5** (Seedance 2.0 720p 5 s, first + last frame): the take opens on the *last* keyframe, then winds back (0.9-1.2 s), slashes (1.4-2.5 s) and draws a rainbow line up across the clock (2.5-4.9 s). Used 1.4-4.92 s at 1.0; recap F7_11 uses 1.6 s. De-red with `--protect-rainbow`. v2 take 4 kept.
