# F1: IMPACT: color flood (169.40-172.96)

At the impact a wave of colour bursts from her and sweeps the engraved skyline; she sprints out of it at camera. Built as a radial matte wipe (tools/sectionF/wipe.py) between the engraved twin of the clip (tools/engrave, strength 1, no bloom) and the colour clip, with a hatched pencil-stroke front and a gold leading edge. The wipe matte is kept as take_N_wipe_matte.mp4.

## Keyframe

Model: google/nano-banana-pro (2K, 16:9), $0.134 per image. Chosen: `kf_full1 (r3); kf_1 = style-test T1 (r1, r2)`.

Prompt (last round):

```
full
Low wide-angle shot on the elevated train tracks of the Chicago Loop: the anime girl sprints straight toward the camera, extremely fast, large in frame from the knees up, long black hair streaming behind her, yellow pencil gripped in her right hand. Behind her the Loop skyline with the Willis Tower; a towering wave of color made of colored-pencil strokes is breaking over the city behind her. The world is the same M.C. Escher wood engraving as the third reference (crisp black ink line work, dense precise parallel hatching and cross-hatching that follows form), but now hand-colored: vivid colored-pencil color laid over the engraving in visible pencil strokes on warm off-white paper tooth - cobalt and ultramarine blue, vermilion, magenta, emerald, warm orange, sky blue - with the black hatching still showing through the color everywhere. Gustav Klimt gold-leaf accents (flat burnished gold with spiral and small square mosaic ornament) on select surfaces. Kandinsky shapes float in the sky: concentric circles, triangles, arcs and checkerboards in colored pencil. Hand-drawn, not a painting, no watercolor wash, no airbrush, no digital gradients, not photographic, not 3D. Every surface is now colored in saturated colored pencil over the hatching, with burnished Klimt gold leaf on rooftops, cornices and ornaments. The girl is a full-color anime character with clean cel shading, exactly matching the reference sheets: white cropped bomber jacket with an orange band across chest and arms, pale-blue dot patch on the left chest, round '1420 MHz' patch on the left sleeve, black crop top, navy wide cargo pants with orange straps, chunky white sneakers, orange headphones around her neck. Her long black hair is DOWN and loose (no bun), and she holds a yellow pencil in her hand. Reference images: the first two are the character sheets for the girl (match her face, outfit and long loose hair exactly); the third shows the engraving line technique of the world. Full bleed, edge to edge, no border, no margin, no paper edge, 16:9. No text, no letters, no numbers, no signature.
refs=['media/style_tests/refs/jade_pencil_flare_t2.jpg', 'media/style_tests/refs/jade_canon_turnaround.jpg', 'media/style_tests/world/3_loop_L_tracks_seedream-5-pro.jpg']
```

## Takes

- take_1: bytedance/seedance-2.0 720p 5 s, est $0.75, state done, first frame `media/shots/F1/kf_1.jpg`. 
  - prompt: Extremely fast: the girl sprints straight toward the camera along the elevated tracks, closing the distance until she fills the frame from the knees up, long hair streaming behind her, pencil in her hand. Behind her the giant wave of color curls and crashes forward over the skyline, rolling after her. The camera pulls back quickly ahead of her, low to the tracks. Her face keeps the first frame's design, forehead smooth, brows relaxed, never a face close-up. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.
  - verdict: half-bloom keyframe: she jogs rather than sprints and the 'after' is still mostly gray buildings, so the flood reads weakly. Fallback.
- take_2: bytedance/seedance-2.0 720p 5 s, est $0.75, state done, first frame `media/shots/F1/kf_1.jpg`. r2 faster sprint
  - prompt: Extremely fast, explosive sprint: the girl runs flat out straight at the camera along the elevated tracks with huge powerful strides, arms pumping, long hair whipping straight back, pencil in her fist; she closes the distance in three seconds until she fills the frame from the waist up. The camera is low and pulls back fast but she gains on it. Behind her the giant wave of color crashes forward over the skyline and rolls after her. Her face keeps the first frame's design, forehead smooth, brows relaxed. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.
  - verdict: same keyframe, faster sprint prompt.
- take_3: bytedance/seedance-2.0 720p 5 s, est $0.75, state done, first frame `media/shots/F1/kf_1.jpg`. r3 full-color keyframe, fast sprint
  - prompt: Extremely fast, explosive sprint: the girl runs flat out straight at the camera along the elevated tracks with huge powerful strides, arms pumping, long hair whipping straight back, pencil in her fist; she closes the distance in three seconds until she fills the frame from the waist up. The camera is low and pulls back fast but she gains on it. Behind her the giant wave of color crashes forward over the skyline and rolls after her. Her face keeps the first frame's design, forehead smooth, brows relaxed. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.
  - verdict: full-colour keyframe (colored girders and facades) so the before/after is unmistakable.

Video cost for this shot: $2.25 (list-price estimate).

## Judgement

The wipe itself works: the engraved twin is a convincing Escher plate of the same frame and the colour arrives from her. The engrave matte leaks some wave colour around her in the engraved twin; it reads as the colour starting at her, so it stays. Take 3 (full-colour keyframe) is in the cut: wipe origin on her, outq ease, the front reaches the corners on the bar-98 downbeat.

## chosen.json

```json
{
 "take": 3,
 "file": "media/shots/F1/take_3_wipe.mp4",
 "in_sec": 0.0,
 "out_sec": null,
 "rate": 1.1,
 "reverse": false,
 "notes": "colour-flood wipe (tools/sectionF/wipe.py): engraved twin -> colour clip, radial from her, gold leading edge",
 "matte": "media/shots/F1/take_3_matte/matte.mp4"
}
```
