# Section director brief (read this first)

You direct one section of the REWIND music video. Your sources:

- `docs/treatment.md`: the idea.
- `docs/shotlist.md`: your shots, their times and their text treatment. The shot list is binding on timing and intent. You may improve a shot's content if your version is clearly better and still serves the lyric; write down why.
- `docs/TOOLS.md`: how to call image and video models and how to check spend.
- `docs/recon/pipeline.md` §2: model lessons.
- `analysis/cinematic/timing.json`: beats, bars and word times.

## Assets

- **Canon Jade** (anime, the only full-color thing): `media/design/jade_canon_turnaround.png`. Expression and action sheets are in `media/design/`. The outfit must be exact:
  - white cropped bomber with an orange chest/arm band
  - pale-blue dot patch on the left chest, "1420 MHz" roundel on the left sleeve, plain pale-blue circle on the back
  - black crop top
  - navy wide cargo pants with orange straps
  - chunky white sneakers
  - orange headphones around her neck
  - hair in a loose bun with a yellow pencil, until shot G2; after that her hair is down and the pencil is in her hand
- **Agents of the TIME VARIANCE █████████:** see `media/design/` (NOTES.md). Black suits, sunglasses, nearly blank faces, drawn in the engraving style.
- **World style refs:** `media/style_tests/sheet_A*.jpg`, `sheet_B2_*.jpg`.

## Look

The world is an M.C. Escher-style wood engraving: black ink on warm off-white paper, dense parallel hatching, no gray wash, no color. Jade is in full anime color.

- Use **nano-banana-pro** for keyframes, and seedream-5-pro for night and dusk.
- Use **gpt-image-2.5-flare** for complex staging and reflections. It outputs 3:2, so leave headroom and pad or outpaint rather than cropping heads.
- Prompt for "full bleed, edge to edge, no border, no margin, no paper edge". Trim any margins that still appear.
- No model-drawn text, ever. All text is added by the engine.
- Image models return the old picture when it's among the inputs, so give them a reference, not the image you want changed.

Style suffix to start from (tune it as needed):
> "Rendered as an M.C. Escher wood engraving / lithograph: crisp black ink lines on warm off-white paper, dense precise parallel hatching and cross-hatching that follows form, high contrast, no gray wash, no color anywhere except the girl. The girl is a full-color anime character (clean cel shading) exactly matching the reference sheet. Full bleed, edge to edge, no border, no margin, 16:9."

## Video

- Use **Seedance 2.0 at 720p**, with the keyframe as the first frame (add `last_frame_image` when you need to land a pose). minimax/h3 is the alternative.
- Lengths are 4–12 s; generate at least the shot length plus 1 s of handle.
- Write "extremely fast" for action, and state the camera move explicitly.
- Prompts describe motion only; the first frame carries the look.
- Make 1–2 takes per shot, more only for hero shots.

## Engraving

Run every generated clip through `tools/engrave` (see its README) so the world stays engraved and only Jade stays in color. Keep the matte output; the engine uses it for ghosts, ribbons and color isolation.

## Folders

`media/shots/<SHOT_ID>/` holds:

- `kf_*.png`: keyframes
- `take_N.mp4`: raw takes
- `take_N_engraved.mp4`: engraved takes
- `take_N_matte/`: matte frames, when needed
- `chosen.json`, with this shape:
  ```
  {take, file, in_sec, out_sec, rate, reverse, notes}
  ```
  - `in_sec`: where to start reading the clip
  - `rate`: 1.0 = normal speed
- `NOTES.md`: prompts, the model used, cost, and your judgement

## Quality bar

Look at your own output. Make contact sheets and actually view them. Reject:

- anything off-model (wrong outfit, missing pencil before G2, extra limbs, morphing)
- a world that turned gray-wash or photographic
- color leaking into the world
- a muddy, unreadable composition

Every shot needs one clear idea that reads in under a second. Jade is large in frame unless the shot is a deliberate wide. No head shots or headshot violence: the hit is to the body, as colored motes.

## Spend

Log every paid call; the tools do it. Stay within your section budget. Check `tools/gen/spend.py` before big batches. The project cap is $400 total and other directors share it.

## Video queue etiquette

The relay runs about 2 jobs per minute, shared with other directors. Submit in batches as soon as keyframes are approved; don't wait. Do keyframes for later shots while takes render.

## Engine handoff

The compositing engine lives in `render/engine/` (README there). Add your shots to the timeline as the engine README describes, in a section file of your own (e.g. `render/timeline/<section>.js`) so you don't collide with other directors. Do HUD and typography with the engine's modules, matching the shot list's typography spec. If the engine isn't ready when your media is done, write your timeline entries as JSON in `media/shots/<section>_edl.json`: shot, file, timeline in/out, clip in, rate, reverse, and text layers with timings.

## Git

Commit only code, docs and small stills (no mp4 or large png files). Use `git pull --rebase` before you push, and touch only your own files. Commit messages end with:
`Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`

## Report

Write `docs/sections/<section>.md`: what's done, chosen takes, what's weak, and the cost. Reply with a concise summary.
