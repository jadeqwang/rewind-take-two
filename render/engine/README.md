# REWIND render engine

A timeline-driven compositor for the *Rewind* music video. Frames are drawn in JavaScript inside headless Chrome (three.js r186 on the RTX 3090 via ANGLE/Vulkan) and encoded with ffmpeg. Every frame depends only on its index, so ranges render in parallel workers and can be re-rendered in any order.

**Directors:** put your shots in `render/timeline/<SECTION>.js` (copy `render/timeline/_TEMPLATE.js`) or, as a fallback, `media/shots/<SECTION>_edl.json`. Use the [typography/HUD kit](#typography-and-hud-kit) for all text and the [residue and post](#residue-ghosts-and-post) tools for ribbons, ghosts, motes and inversions. Check your work with `--list`, `--stills` and `--range … --preview --encode`.

```bash
cd ~/Documents/rewind-take-two
(cd render/engine && npm install)                                     # once: playwright-core + three (node_modules is gitignored)

node render/engine/render.mjs --list                                  # resolved shot table (bar:beat, source file of every shot)
node render/engine/render.mjs --preview                               # the film, 960x540 draft + audio
node render/engine/render.mjs                                          # full 1920x1080, x264 High CRF 16 + AAC 320k
node render/engine/render.mjs --range 42.38 56.54 --encode            # a frame range (+ a clip with its audio slice)
node render/engine/render.mjs --range 25:1 33:1 --preview --encode    # ranges accept bar:beat / word / section times
node render/engine/render.mjs --still 84.5                            # one full-res PNG still at t
node render/engine/render.mjs --stills 83,85.2,"word:reload"          # several stills
node render/engine/render.mjs --sheet 82:95:0.5 --cols 6              # contact sheet
node render/engine/render.mjs --verify 8   |   --verify 40.4,119.2    # determinism check (two browsers, opposite orders)
node render/engine/render.mjs --track media/shots/X/take_1_matte/ --out track.json   # subject track of a matte
node render/engine/render.mjs --serve                                 # studio scrubber URL (arrow keys step frames)

node render/engine/render.mjs --timeline render/engine/demo/timeline.js --preview   # 13 s engine demo
node render/engine/render.mjs --timeline render/engine/demo/kit.js --stills 119.2   # kit demo (every module in context)
```

Options: `--timeline <file>` (default `render/timeline.js`), `--preview` or `--w/--h`, `--workers N` (default 4 full, 3 preview, capped at 6), `--gpu nvidia|egl|cpu`, `--audio <mp3>` (default: the timeline's `audio`, else `inputs/Rewind - cinematic edition (Remastered).mp3`), `--timing <json>`, `--out <mp4>`, `--crf`, `--preset`, `--q <jpeg quality>`, `--png` (lossless intermediate frames), `--force` (re-render cached frames), `--noaudio`.

Outputs (gitignored): `render/engine/out/<timeline name>/{full,preview}/frames/f000000.jpg`, `…/<name>_<mode>[_a-b].mp4`, `…/stills/`. Extracted video frames and matte tracks: `media/engine_cache/{full,preview}/`.

## Architecture

```
render.mjs (Node)
  ├─ imports the timeline + timing JSON (resolves ranges; render/timeline.js merges the section files here too)
  ├─ lib/prepare.mjs  ffmpeg → CFR JPEG sequences per video / matte (mp4 or PNG-sequence dir), plus a per-frame
  │                   subject track for every matte (media/engine_cache/<mode>/, keyed by size+mtime+res)
  ├─ lib/server.mjs   static server over the repo root, /__ls/<dir> listings, PUT /__out/… (frames straight to disk)
  ├─ N workers = N headless Chrome processes taking 1-second chunks off a shared queue (resumable, atomic writes;
  │   a lost WebGL context restarts the worker; repeated losses fall back nvidia → egl → cpu with a warning)
  └─ ffmpeg: frames + audio slice (-ss = first frame / 24) → H.264 High, BT.709 tagged, AAC 48 kHz

page/index.html → src/engine.js (one frame, i → t = i / 24)
  shotAt(t) → content clock (shot.time remap, tapeStop, hold) → fx.js → post parameters
  layers (bottom → top) → draw ops → compositor.js (one three.js WebGLRenderer owns the GL context):
      'pre' layers ─► comp RT (premultiplied) ──► post pass ──► 'post' layers (HUD, lyrics) ──► final pass ─► canvas
                      └─ colour mask RT (keepColor layers)       (distort, tape, VHS, isolate, negative,  (flash, fade,
                                                                  grade, paper, grain, letterbox)          dither)
  modules are instantiated lazily and share one canvas / render target; assets load miss-driven (draw → await
  whatever was missing → draw again), so pixels never depend on cache timing
```

Lineage: the CLI/worker harness, TimeMap and miss-driven loader come from `rewind-music-video/render` (Rewind take one); the single-three.js-context compositor with Canvas2D type layers from `rare-earth-techno-remix/render`; chunked resumable workers and the studio scrubber from `orbital-sunrise-video/video`.

## The film timeline: sections and EDLs

`render/timeline.js` only merges the section directors' work:

1. every `render/timeline/<SECTION>.js` (files starting with `_` are skipped), exporting `{section, shots, overlays?, fx?}` or a function `({T, core}) => {...}`; relative module paths inside it resolve against `render/timeline/`;
2. every `media/shots/<SECTION>_edl.json` whose section has no `.js` file (the fallback format below);
3. **overlaps are an error**: the message names both shots, their times and their files. Duplicate shot ids are errors too;
4. any time range nobody covers yet gets a placeholder **slate** (song section + game genre) with the default word-timed lower-third lyric.

Section-level `fx` are prepended to every shot of that section. Shot `end` defaults to the next shot's start within the same file (the last shot needs an `end` or `dur`).

### EDL JSON (fallback format)

```json
{ "section": "C", "fx": [], "overlays": [],
  "shots": [
    { "shot": "V2e", "file": "media/shots/V2e1/take_1_engraved.mp4",
      "in": "49:1", "out": 88.38,                     // timeline in/out (seconds or any time expression), or "dur"
      "clip_in": 0.4, "rate": 1.0, "reverse": false,  // reverse = play [clip_in, clip_in + dur·rate] backwards
      "chosen": "media/shots/V2e1/chosen.json",       // optional: file / in_sec / rate / reverse come from it
      "matte": "media/shots/V2e1/take_1_matte/",      // optional: Jade keeps colour; enables ghosts/follow/negative
      "freeze": 1.2, "fit": "cover", "scale": 1, "x": 0, "y": 0, "crop": [0,0,1,1], "kenBurns": {}, "grade": {},
      "background": "#ece7dc",
      "text": [
        { "style": "slam", "text": "back on the road", "sync": "lyric", "in": 84.86, "out": 88.38, "color": "#0b0b0c" },
        { "style": "sign", "text": "LAKE SHORE DR\nI'm speeding down Lake Shore", "sync": "lyric", "corners": [560,170,1380,230,1372,500,566,470] },
        { "style": "platformer", "side": "right", "iteration": 4097, "deaths": 4096 }
      ],
      "layers": [ /* any extra engine layers */ ], "fx": [ /* shot fx */ ] } ] }
```

`file` may be a video or a still (`.png/.jpg` → image layer). `text[].style` picks the module: `lowerthird`, `slam`, `dialogue`, `sign` / `etch` / `ground` / `plain` (pin), `title`, `terminal`, `whisper`, `trace`, `pencil`, `motes`, or a HUD mode (`platformer`, `iteration`, `pause`, `continue`, `loading`, `rewind`, `race`). Text `in`/`out` are timeline times; every other key is passed as a module param (see the kit below). Text layers go in the `post` stage (above grain), pinned in-world text in `pre`.

## Timeline format

```js
export default {
  name: 'rewind', audio: 'inputs/Rewind - cinematic edition (Remastered).mp3', range: [0, 227.96],
  background: '#000000',
  fx: [{ type: 'grain', amount: 0.04 }],                    // global effects, applied to every shot first
  shots: [                                                   // base track: one shot at a time; carries post fx
    { id: 'drop1_rewind', start: '25:1', end: '33:1',        // or dur: '8bar' | '16b' | 3.5
      time: [[0, 0], [2, 1, 'inOut'], [4, 4]],               // optional content-clock remap for every layer
      background: '#0b0b0c',
      layers: [ /* bottom → top */ ],
      fx: [{ type: 'rewind', amount: 1 }, { type: 'punch', on: 'downbeat' }] },
  ],
  overlays: [ { id: 'hud', start: '33:1', end: '62:3', layers: [/* … */] } ],   // concurrent; default stage 'post'
};
```

**Times.** Shot `start`/`end`, ranges, layer `start`/`end` and keyframe times accept seconds (`86.5`; inside a shot, numbers are shot-local), `"bar:beat"` (1-based, fractional beats ok, on the tracked grid: `"25:1"` = 42.38 s), `"beat:64"`, `"word:reload"`, `"word:rewind#2"`, `"word:stop@40"` (first after 40 s), `"wordEnd:…"`, `"line:12"`, `"section:drop1"`, `"sectionEnd:drop1"`, `"event:impact#2"`, plus offsets: `"17:1+0.5b"`, `"word:rewind-2f"`, `"section:drop2+1bar"`, `"33+0.25"`. A missing word or section throws.

**Timing source.** `analysis/cinematic/timing.json` (beats, bars, sections, `lyrics.lines[].words`, typed events). `data/timing.stub.json` stood in before it existed.

**Keyframes.** Any animatable value may be a constant, `[[t, value, ease?], …]` (t local seconds or an absolute time string; ease on the left key: `linear` `hold` `in` `out` `inOut` `inCubic` `outCubic` `inOutCubic` `inExpo` `outExpo` `inOutSine` `outBack` `smooth`), `{keys, ease}`, or a function `(lt, env) => value`. Numbers, arrays and `#rrggbb` colours interpolate.

### Layers

Common: `id`, `type`, `start`/`end`, `opacity`, `fadeIn`/`fadeOut` (s), `blend` (`normal` `add` `screen` `multiply` `erase`), `stage` (`pre` | `post`), `keepColor` (stays in colour under `isolate` / `negative`), `realtime` (ignore the shot's time remap), `time` (layer clock remap), `noRewind` (skipped inside a comp), transform: `fit` (`cover` `contain` `height` `width` `stretch` `none`), `x`, `y` (design px from centre), `scale` (or `[sx, sy]`; negative = flip), `rotate` (deg), `anchor`, `crop` (`[x0, y0, x1, y1]` normalised), `rect` (`[x, y, w, h]`), `kenBurns: {from: {scale, x, y, rotate}, to: {…}, ease}`, `grade: {saturation, exposure, contrast, gamma, tint, lift, invert, hue (deg), colorize '#hex', colorizeAmount}`, `key: {type: 'luma', low, high, invert} | {type: 'chroma', color, tolerance, softness, spill}`.

| type | specific params |
|---|---|
| `solid` | `color` (with `rect`/`rotate` for paper slips, panels) |
| `image` | `src`, `repeat: [x, y]` |
| `parallax` | `speed` (px/s) or `scroll` (keyed px); `layers: [{src, depth (scroll factor), y, scale, repeat, grade, opacity, blend}]` |
| `video` | `src` (video file, or a PNG/JPG sequence directory ending in `/`, e.g. `tools/engrave --matte-out` dirs; `fps.txt` sets its rate, default 24), `in`, `rate` (number or keys; negative = reverse; ramps are integrated), or `srcTime` (keys: layer time → source time), `freeze` (layer time to hold from), `loop` (`true` / `'pingpong'`), `frameBlend`, `echo: {n, dt, alpha, blend}`, `matte: {src, mode: 'luma'/'alpha'/'lumaInv'/'alphaInv', offset}`, `alpha: true` |
| `ghosts` | many instances of one matted clip: see [ghosts](#residue-ghosts-and-post) |
| `canvas` / `three` | `module`, `params`; three: `samples` (MSAA, default 4), `linear` (`false` for display-ready output, e.g. `render/three` scenes) |
| `comp` | `source: 'film'` or a shot id; `srcTime` keys (layer time → absolute song time, e.g. `[[0, 86.5, 'inCubic'], [3, 82]]` = rewind); `echo`. Renders that shot's `pre` layers, max depth 2 |

### Effects (`fx`, shot-level; numbers keyframable on the shot clock)

`grain {amount, size, seed: 'frame'|'twos'|'shot'}` · `paper {amount}` · `vignette` · `scanlines` · `chroma {amount px}` · `vhs` · `warble` · `wobble` · `tracking` · `ripple {amount, speed}` · `zoom` · `spin` · `grade {saturation, contrast, exposure, tint, lift}` · `letterbox {aspect 2.39, amount}` · `isolate {amount, ink, paper, engrave, cell, angle}` (world → ink on paper / engraving; `keepColor` layers stay) · **`negative {amount, ink, paper}`** (woodblock negative: white lines on ink; `keepColor` layers stay in colour; key 0→1 over .3 s for P5) · `fade {in, out}` · `flash {at, on, dur, amount, color}` · `punch {amount, on, decay}` · `shake {amp, freq, steady, on, decay}` · `tapeStop {at, dur, toBlack}` · `hold {at, until}` (freeze frame) · `rewind {amount}` (VHS search) · `bg {color}`.

Events for `on`: `'beat'`, `'downbeat'`, `'every:2'`, any event type in timing.json (`'impact'`, `'trailer_impact'`, `'vocal_chops'`, `'words'`, `'lines'`, …), an array of times, or `{list, every, offset}`. Events before the shot's start are ignored.

## Typography and HUD kit

Fonts (OFL, vendored in `render/fonts/`, loaded automatically): **IM Fell English** (+ italic) `'fell'`, **Overpass** (variable 100–900) `'sign'`, **Press Start 2P** `'hud'`, **IBM Plex Mono** (400/700) `'mono'`, **Reenie Beanie** (pencil hand) `'hand'`, plus Anton, JetBrains Mono and CMU Serif italic. Any module `font` param takes these short names or a CSS family.

**Word sources** (shared by every text module; times are what the module reveals on):

| params | words |
|---|---|
| none | the lyric line being sung now (from timing.json), with `lead` / `hold` |
| `source: 'window'` | every sung word whose onset falls inside the layer's time range (dialogue default) |
| `text` + `sync: 'lyric'` | your text, each word matched to the next sung word with the same spelling inside the layer's window |
| `text` + `times: [...]` | one time per word (layer-local numbers or absolute expressions) |
| `text` + `cps` | typewriter pace from `at` (or the layer start) |
| `text` | all at once at `at` (or the layer start); `\n` breaks lines |

| module | use (shot list) | key params | still |
|---|---|---|---|
| `lowerthird` | default sung lyric, IM Fell, lower third; each word appears on its onset with a **2-frame ink bleed** | `color` (ink; `'#F08A24'` when the lyric is residue; `'#ece7dc'` on dark), `size` 62, `x`, `y` 960, `align`, `maxWidth`, `halo` (paper glow for legibility), `italic`, `uppercase`, `tracking`, `hold` | `kit_lowerthird_inkbleed.jpg`, `kit_lowerthird_bleed_frames_0_1_2.jpg` |
| `slam` | kinetic lyric ("back on the road" slamming with the landing) | `mode: 'stack'` (line builds word by word) / `'word'` (current word huge), `size` 150, `color`, `accent` (just-landed word), `impact`, `tilt`, `y` | `kit_slam_kinetic.jpg` |
| `dialogue` | RPG box, typewriter (D7–D8, the only one in the film) | `rect`, `speaker`, `font` (`'fell'` or `'hud'`), `size`, `typeTime` .22 s/word, `open`/`close` frames, `caret` | `kit_dialogue_typewriter.jpg` |
| `pin` | in-world text, **corner-pinned** (projective mesh warp) | `corners` [TL, TR, BR, BL] 8 numbers, keyframable (track the plate by keying them); `style: 'sign'` (Overpass on a bordered panel; `panel: '#1f5a3a'` for green) / `'etch'` / `'ground'` (use `blend: 'multiply'`) / `'plain'`; `text`, `size`, `res` | `kit_pin_sign.jpg`, `kit_pin_ground.jpg` |
| `etch` | mirror etching (D3, V2f) = `pin` with style etch; frosted glyphs with a groove shadow and scratches | as pin; `blend: 'screen'` over dark glass | `kit_etch_mirror.jpg` |
| `title` | **REWIND**: letters arrive in reverse order (D first), mirrored, then card-flip to right-reading | `arrive: {at, every}` (`every: 0` = whole mirrored word bleeds in at once, C3), `flip: {at, dur, stagger}`, `mirrored: false` (second REWIND), `subtitle: 'jade wang'`, `size` | `kit_title_rewind_flip.jpg` |
| `terminal` | agency terminal; `█` runs are real solid redaction blocks; typed on pace or word timings; inverted alarm | `lines: ['TIME VARIANCE █████████', {text: 'ANOMALY DETECTED.', sync: 'lyric'}]`, `cps`, `alarm` (0/1 keys), `blink` (Hz), `mode: 'full'` / `'panel'` + `rect`, `size` | `kit_terminal_alarm.jpg` |
| `whisper` | whispered "shot", "never stop": IM Fell italic, lowercase, graphite, tracked out, breathes in | `text`, `sync`, `size` 34, `color`, `tracking` (em), `x`, `y` | in `kit_motes_burst_whisper.jpg` |
| `trace` | "it couldn't **trace**": a dotted line traces the letters, loses the path, wanders off | `text`, `at` (e.g. `'word:trace'`), `dur`, `lose` (fraction traced), `wander`, `wanderLen`, `spacing`, `dot`, `ghost`, `color` | `kit_trace_lost.jpg` |
| `pencil` | handwriting that writes itself (sticky note, anagram slip, "never stop" on walls) | `text`, `at` + `cps` or `sync`/`times`, `size`, `color` (graphite; orange for coloured pencil), `x`, `y`, `rotate`, `corners`, `grain`, `point` | `kit_pencil_handwriting.jpg` |
| `hud` | game UI, Press Start 2P, small, top corners; one mode per layer (below) | `color`, `accent`, `side`, `size`, `margin` | |
| `motes` | Celeste-style death burst at a point, orange/blue | `at`, `x`, `y`, `count`, `colors`, `speed`, `drag`, `gravity`, `size`, `life`, `ring`, `shape`, `spread`, `angle` | `kit_motes_burst_whisper.jpg` |
| `ribbon` | causal residue trail | see below | `kit_ribbon_follow_bloom.jpg` |
| `lyric`, `slate`, `iso_test` | take-one-style lyric line (Anton), animatic placeholder, reference three.js module | | |

HUD modes (`hud`, `params.mode`):

| mode | params | still |
|---|---|---|
| `platformer` | `iteration` (number/keys), `deaths` (number or `{base, on: 'beat'/'downbeat'/event list, from, step}`; pops on each death), `timer` (`{from, offset, rate}` or `false`), `side` | `kit_ghosts_13_hud_platformer.jpg` |
| `iteration` | rolling odometer for the ending: `base` + `rate`·(t − `from`) keeps rolling forever (or keyed `value`), `snap` (mechanical ticks), `label`, `flicker` | `kit_hud_iteration_roll.jpg` |
| `pause` | `cursor` (item index keys; fractional = moving), `blinkAt` (selection blinks .4 s), `items`, `dim` | `kit_hud_pause.jpg` |
| `continue` | CONTINUE? countdown: `from` 9, `every` (s) or `on` (events), `start` | `kit_hud_continue.jpg` |
| `loading` | `title` ('Reload.'), `tip`, `deaths`, `spinner` (spinning pencil), `progress` keys, `bg` (`null` = transparent) | `kit_hud_loading.jpg` |
| `rewind` | ◀◀ ×N: `multiplier` keys, `ring` (clock ring sweeping counter-clockwise; `sweep` keys or `rate`), `counter`, `scrub` | `02_rewind_comp_x4_t88.208.jpg` |
| `race` | `GHOST: ITERATION n` + `split` (s; keys), `splitColor` keys | |

## Residue, ghosts and post

- **Ribbon** (`module: 'ribbon'`): `path` keys `[[t, x, y], …]` or **`follow: {layer: 'jade', point: 'centroid' | 'top' | 'bottom', smooth: 3, offset: [dx, dy]}`**, which rides a video layer's matte in the same shot (the tracker: render.mjs extracts a per-frame centroid/top/bottom track from every matte, smoothed over ±n frames, mapped through that layer's framing and speed). `trail` (s), `drift` [vx, vy] (world motion so residue streams behind her), `width`, `colors` (default residue gradient `#F08A24 → #8DB8E8`; give each ghost iteration its own from `core.KANDINSKY`), `twist`, **`bloom`** (additive glow, default .8), **`grain`** (coloured-pencil tooth, default .5), `pencil` (hatched strokes), `motes` (density). Give it `keepColor: true` under `isolate`/`negative`. `--track <matte>` dumps the same track as JSON for other tools.
- **Ghosts** (`type: 'ghosts'`): one matted clip drawn many times: `src`, `matte`, base `fit/x/y/scale`, `in`/`rate`/`loop`, `tint` (colorize amount, .65), and either `instances: [{x, y, scale, flip, color, hue, tint, opacity, offset (s), freeze (source s), blend}]` or `generate: {count, seed, area: [x0, y0, x1, y1] (offsets), scale: [min, max], opacity, offset: [min, max], quantize (s), colors (default Kandinsky), flip, sort}`. Reveal with `show` (count keys; fractional fades in the next) or `on: 'vocal_chops'` (one more ghost per event, with a pop). Instances on the same source frame share one texture, so `quantize` the offsets: 13 ghosts ≈ 130 ms, 100 ghosts ≈ 110 ms per 1080p frame here. V2i graphite ghost runner: one instance with `color: '#5e5b57'`, `tint: 1`, `offset: -0.4`.
- **Woodblock negative** (`fx: negative`): world luminance flips to white lines on ink through the paper/ink duotone; `keepColor` layers (Jade's matte, motes, ribbons) stay in colour. Combine with `tapeStop` for P5, with `hold` for the frozen pause frame.
- **Mote burst** (`module: 'motes'`): see the kit table; freeze it with the shot's `hold`/`tapeStop`, implode it by replaying through a `comp` backwards.

## Modules (writing your own)

```js
// Canvas2D: drawn into a cleared W×H canvas already scaled to 1920×1080 design units
export async function init(ctx, params, env) { return { /* state, e.g. loaded images */ }; }   // optional, once
export function draw(lt, env) { const g = env.ctx; /* draw from lt / env.t only */ }

// three.js: draw into the render target the engine has bound (transparent, MSAA)
import * as THREE from 'three';                       // always the bare specifier (import map → node_modules three r186)
export async function init(renderer, params, env) { const scene = …, camera = …; return { scene, camera }; }
export function draw(lt, env) { env.renderer.render(env.state.scene, env.state.camera); }
// Factory form (render/three uses it): export function createScene() { return { init(renderer, params), draw(t), dispose() }; }
```

A module is named `'hud'` (→ `render/engine/modules/hud.js`), by repo path, or relative to its timeline file. Helpers for text modules live in `modules/lib/text.js` (word sources, ink bleed, layout, corner-pin warp, pencil grain).

`env`: `lt` (layer clock), `t` (absolute song time being drawn; inside a comp, the source time), `origin`/`layerEnd` (absolute layer start/end), `frame`, `frameT`, `dur`, `shot`, `layer`, `params`, `state`, `val(x, default)`, `T` (TimeMap), `lyric(opts)`, `pulse(on, decay)`, `events(on)`, `follow(spec)` (tracked point → `fn(layerTime) → [x, y]`), `rng(...seed)`, `core` (hash, noise, easing, `PAL`, `KANDINSKY`, `FONT`, clock), `assets`, `rewinding`, `W`/`H` (1920/1080), `S` (px per design px); three modules also get `renderer`, `target`, `THREE`. Rules: no `Math.random`, no `Date`, no state carried between `draw` calls, never call `renderer.setRenderTarget`, restore renderer state you change. Instances are created on first use and released after 4 s unused if the module exports `dispose()`.

`env.lyric({lead, hold})` returns `{line, lineIndex, text, words: [{text, start, end, state: 'past' | 'current' | 'future', progress}], word, wordIndex, lineProgress, appear, vanish, next}`. Also `T.wordAt(t)`, `T.lineAt(t)`, `T.word('rewind', 2)`, `T.section('drop1')`, `T.sectionAt(t)`, `T.barBeat(bar, beat)`, `T.barBeatAt(t)`, `T.beatTime(x)`, `T.countIn(a, b, 'beats')`, `T.pulse(t, 'downbeat', 0.12)`, `T.time(expr)`.

## Determinism and hygiene

- Frame i depends only on i: randomness is hashed from (seed, frame/time), counters count timing events, assets load miss-driven, `Math.random` is reseeded per frame. `--verify` renders frames in two browsers in opposite orders and compares pixel hashes (engine demo 8/8 and kit 10/10 module-heavy frames identical on nvidia).
- Cached frames carry a fingerprint of every `.js/.json/.html` under `render/` plus the timing JSON and size/quality; any change discards stale frames. Media replaced under the same path is re-extracted (size+mtime key) but rendered frames are not invalidated: pass `--force`.
- Chrome's TMPDIR is forced onto disk (`render/engine/out/t`); workers are capped at 6.
- Pixels are reproducible per GPU backend. If the GPU is busy (other agents' CUDA jobs), Chrome sometimes loses the WebGL context: workers retry, then fall back to egl/cpu and say so. Don't mix backends in a final encode; re-run with `--force` if a fallback happened.

## Throughput (engine demo, 13 s = 312 frames)

| mode | workers | wall | fps | × realtime | in-page per frame |
|---|---|---|---|---|---|
| preview 960×540 (JPEG q.85) | 3 | 3.4 s | 91 | 3.8× | ~25 ms |
| full 1920×1080 (JPEG q.95) | 4 | 8.2 s | 38 | 1.6× | ~90 ms |
| full 1920×1080 | 6 | 8.3 s | 38 | 1.6× | (no gain: GPU readback/JPEG bound) |

Encode: x264 `slow` CRF 16 High + AAC 320k: 8 s for the 13 s demo (≈45 Mb/s with per-frame grain; use `--crf 18`–`20` or grain `seed: 'twos'` for uploads). Kit text/HUD modules cost 5–30 ms per 1080p frame; 13 ghosts ~130 ms, 100 ghosts ~110 ms (the first frames of a shot also pay for loading its video frames); the `render/three` Engraver diorama ~600 ms.

## Demos

- `demo/timeline.js` (song 82.0–95.0): video forward → tape stop → the same shot rewound through a `comp` (◀◀ ×2 ×4 ×8), parallax level under `isolate` with a matted Jade, three.js loading screen. Stills `demo_stills/01_…`–`04_…`.
- `demo/kit.js`: every kit module at the moment of the song the shot list uses it for (lower third at 13 s, sign at 21 s, etch, dialogue, motes + whisper on "shot", negative + pause, REWIND title, slam, Reload., ground text, CONTINUE?, 13 ghosts on the vocal chops, 100-ghost swarm, pencil slip, terminal alarm, follow ribbon, trace, iteration roll). Stills `demo_stills/kit_*.jpg`.
- Demo media: `tools/make_demo_media.py` stages clips into `media/engine_demo/` (gitignored).

## Known limitations

- Video is decoded ahead of time to JPEG sequences at native fps (exact random access; ~50 MB of cache per 10 s of 1080p). VFR sources are forced to CFR. Alpha sources need `alpha: true`.
- Frame blending is a linear cross-fade. Keys are basic (luma; chroma with simple spill pull; no matte choke).
- `comp` layers render the source shot's `pre` layers only and re-render once per echo; nesting depth 2. Absolute-time keyframes inside a remapped clock are approximate.
- The tracker is matte-statistics only (centroid / top / bottom of the matte); it cannot follow a hand or a point inside the silhouette. Key ribbon paths by hand for that.
- Ink bleed is a blur/spread approximation, not a fluid simulation. The trace outline is an edge walk, so it follows letter outlines rather than pen strokes.
- No compositor-wide bloom or motion blur (ribbons have their own bloom); no audio mixing.
- Three modules must import bare `'three'`. Modules that output display-ready colour need `linear: false`.
- This dual-GPU box needs `--disable-vulkan-surface` for Chrome's Vulkan path (built in); contexts can still be lost under heavy GPU load (handled by retry/fallback above).
