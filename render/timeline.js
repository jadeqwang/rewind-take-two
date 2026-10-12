// REWIND (cinematic edition): the film timeline. Rendered by render/engine (see render/engine/README.md).
//   node render/engine/render.mjs --preview              whole film, 960x540 draft + audio
//   node render/engine/render.mjs --range 42.38 56.54    one section's frames (+ --encode for a clip)
//
// This file only MERGES the section directors' work:
//   render/timeline/<section>.js      (preferred)   export default {section, shots, overlays?, fx?} or ({T, core}) => {...}
//   media/shots/<section>_edl.json    (fallback, used when the .js does not exist; format in render/engine/README.md)
// Overlapping shots across all files are an error (the message names both shots and files). Any time range nobody
// covers yet gets a placeholder slate naming the song section and its game genre (docs/treatment.md genre ladder).
// A default word-timed lower-third lyric is laid over placeholder slates only; directors own their shots' typography.
import { loadSections, mergeSections } from './engine/src/sections.js';

const GENRE = {
  intro: ['Cold open', 'letterboxed woodcut night drive'], verse1: ['Cutscene', 'lyrics live in the world'],
  pre_drop: ['Game over', 'body shot, freeze, colored motes'], tape_stop: ['Tape stop', 'the world winds down'],
  silence: ['Pause menu', '▶ RESUME / ◀◀ REWIND / QUIT'], drop1: ['Braid rewind', 'the film so far runs backward at half speed'],
  verse2: ['Precision platformer', 'side-scroll LSD → Grant Park, death counter'], build: ['Bullet-hell gauntlet', 'cuts every beat, death #2'],
  tape_stop_2: ['Tape stop', ''], silence_2: ['Continue?', ''], drop2: ['Braid shadow / co-op', 'each rewind spawns a ghost Jade'],
  spoken_anomaly: ['System alert', 'Anomaly detected'], glitch_break: ['Puzzle reveal', 'the pencil comes out'],
  verse3: ['Monument Valley', 'isometric Chicago, color blooms where she draws'], final_drop: ['Boss fight', 'every genre at once'],
  outro: ['Trailer cards', 'one frozen tableau per impact'], ring_out: ['Ring-out', ''], final_whisper: ['New Game+', 'Never stop.'], tail: ['Black', ''],
};

export default async function timeline(ctx) {
  const { T } = ctx;
  const sections = await loadSections(ctx, T);
  const { shots, overlays } = mergeSections(sections, T, {
    fillShot: (a, b, sec) => ({
      id: `slate_${(sec?.id || 'x')}_${a.toFixed(2)}`, start: a, end: b, _placeholder: true,
      layers: [{ type: 'canvas', module: 'slate', params: { title: sec?.label || 'uncovered', subtitle: (GENRE[sec?.id] || [])[0] || '', note: `${(GENRE[sec?.id] || [])[1] || ''}   (no shots yet)` } }],
    }),
  });
  // default lyric overlay over placeholder slates only (directors own the typography of their shots)
  const lyricOverlays = shots.filter(s => s._placeholder).map(s => ({
    id: `lyrics_${s.id}`, start: s.start, end: s.end,
    layers: [{ type: 'canvas', module: 'lowerthird', params: { color: '#0b0b0c', size: 60 } }],
  }));
  return {
    name: 'rewind',
    audio: 'inputs/Rewind - cinematic edition (Remastered).mp3',
    // v5 coda (docs/revisions/v5/coda.md): the film may run past the song (T.duration = 227.96, timing.json) for the
    // credits' fade and the post-credits scene, so it ends where its last shot ends
    range: [0, Math.max(T.duration, ...shots.map(s => s.end))],
    background: '#000000',
    fx: [{ type: 'grain', amount: 0.035 }],
    shots,
    overlays: [...overlays, ...lyricOverlays],
  };
}
