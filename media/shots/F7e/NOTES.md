# F7e: BIG 2: Banach-Tarski reunion (203.76-205.52)

Swell 203.78: two Jades leap together and merge into one in a burst of motes and gold flakes.

## Keyframe

Model: google/nano-banana-pro (2K, 16:9), $0.134 per image. Chosen: `kf_2`.

Prompt (last round):

```
Two identical copies of the anime girl leap toward each other mid-air from the left and right of frame, large, hands reaching out, about to touch and merge into one, a burst of colored motes and gold leaf flakes between their hands, above the colored rooftops of the Loop. The world is the same M.C. Escher wood engraving as the third reference (crisp black ink line work, dense precise parallel hatching and cross-hatching that follows form), but now hand-colored: vivid colored-pencil color laid over the engraving in visible pencil strokes on warm off-white paper tooth - cobalt and ultramarine blue, vermilion, magenta, emerald, warm orange, sky blue - with the black hatching still showing through the color everywhere. Gustav Klimt gold-leaf accents (flat burnished gold with spiral and small square mosaic ornament) on select surfaces. Kandinsky shapes float in the sky: concentric circles, triangles, arcs and checkerboards in colored pencil. Hand-drawn, not a painting, no watercolor wash, no airbrush, no digital gradients, not photographic, not 3D. Maximal color crescendo: the sky has become a Gustav Klimt gold-leaf mosaic of spirals, eyes and small squares, with big Kandinsky circles, triangles and arcs in ultramarine, vermilion and magenta; still drawn by hand in colored pencil with the black engraved hatching visible under the color. The girl is a full-color anime character with clean cel shading, exactly matching the reference sheets: white cropped bomber jacket with an orange band across chest and arms, pale-blue dot patch on the left chest, round '1420 MHz' patch on the left sleeve, black crop top, navy wide cargo pants with orange straps, chunky white sneakers, orange headphones around her neck. Her long black hair is DOWN and loose (no bun), and she holds a yellow pencil in her hand. Reference images: the first two are the character sheets for the girl (match her face, outfit and long loose hair exactly); the third shows the engraving line technique of the world. Full bleed, edge to edge, no border, no margin, no paper edge, 16:9. No text, no letters, no numbers, no signature.
refs=['media/style_tests/refs/jade_pencil_flare_t2.jpg', 'media/style_tests/refs/jade_canon_turnaround.jpg', 'media/style_tests/world/3_loop_L_tracks_seedream-5-pro.jpg']
```

## Takes

- take_1: bytedance/seedance-2.0 720p 5 s, est $0.75, state done, first frame `media/shots/F7e/kf_2.jpg`. 
  - prompt: Extremely fast: the two identical girls fly toward each other and collide in mid-air, merging into one single girl in a burst of colored motes and gold flakes; one girl remains and lands. Static camera. Keep the exact hand-drawn look of the first frame: colored pencil over black engraved hatching on warm paper, the girl in clean anime cel shading. No text, no letters, no logos, no watermark.
  - verdict: merge at ~0.8 s, one Jade lands. Used.

Video cost for this shot: $0.75 (list-price estimate).

## Judgement

Works first time.

## chosen.json

```json
{
 "take": 1,
 "file": "media/shots/F7e/take_1_engraved_dered.mp4",
 "in_sec": 0.15,
 "out_sec": null,
 "rate": 1.0,
 "reverse": false,
 "notes": "BIG 2: Banach-Tarski reunion, two Jades merge at ~0.8 s",
 "matte": "media/shots/F7e/take_1_matte/matte.mp4"
}
```

## v3 revision pass (2026-10-11, stream F)

Audit: take 1 left the merged Jade with a pencil in each hand. **take_2** (same keyframe `kf_2.jpg`, prompt asks for exactly one pencil after the merge) used from 0.15 s; one pencil from ~1.4 s. Its paper margin is cropped in `tools/sectionF/crops.json`. v2 take 1 kept.

## v5 (2026-10-12, v5-build)

F7_07 is gone from the cut: F7_06 + F7_07 became **F7_07m** (202.88–205.52), the BLUE + ORANGE reassembly built from take 2 by `tools/v5/merge/bake.py` (assets in `media/shots/F7m/`; the merged girl is take 2 from 1.6667 s). See `docs/revisions/v5/merge.md`.
