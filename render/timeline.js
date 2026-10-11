// REWIND (cinematic edition): the film timeline. Rendered by render/engine (see render/engine/README.md).
//   node render/engine/render.mjs --preview              whole film, 960x540 draft + audio
//   node render/engine/render.mjs --range 42.38 56.54    one section's frames (+ --encode for a clip)
//
// STARTER: one placeholder slate per section of analysis/cinematic/timing.json (genre ladder from docs/treatment.md)
// plus the word-synced lyric overlay. Replace a section's `layers` with real shots as they arrive; split it into as
// many shots as the shot list needs (start/end may be seconds, "bar:beat", "word:…", "section:…").
// Keep this file importable in Node (no DOM at top level): render.mjs reads it to find videos and the range.
const GENRE = {
  intro: ['Cold open', 'letterboxed woodcut night drive'], verse1: ['Cutscene', 'lyrics live in the world'],
  pre_drop: ['Game over', 'body shot, freeze, colored motes'], tape_stop: ['Tape stop', 'the world winds down'],
  silence: ['Pause menu', '▶ RESUME / ◀◀ REWIND / QUIT'], drop1: ['Braid rewind', 'the film so far runs backward at half speed'],
  verse2: ['Precision platformer', 'side-scroll LSD → Grant Park, death counter'], build: ['Bullet-hell gauntlet', 'cuts every beat, death #2'],
  tape_stop_2: ['Tape stop', ''], silence_2: ['Pause menu', ''], drop2: ['Braid shadow / co-op', 'each rewind spawns a ghost Jade'],
  spoken_anomaly: ['System alert', 'Anomaly detected'], glitch_break: ['Puzzle reveal', 'the pencil comes out'],
  verse3: ['Monument Valley', 'isometric Chicago, color blooms where she draws'], final_drop: ['Boss fight', 'every genre at once'],
  outro: ['Trailer cards', 'one frozen tableau per impact'], ring_out: ['Ring-out', ''], final_whisper: ['New Game+', 'Never stop.'], tail: ['Black', ''],
};

export default function timeline({ T }) {
  const shots = T.sections.map(s => ({
    id: s.id || s.name,
    start: s.start, end: s.end,
    layers: [{ type: 'canvas', module: 'slate', params: { title: s.label || s.name, subtitle: (GENRE[s.id] || [])[0] || '', note: (GENRE[s.id] || [])[1] || '' } }],
    fx: [{ type: 'flash', at: [0], dur: 0.08, amount: 0.4 }],
  }));
  return {
    name: 'rewind',
    audio: 'inputs/Rewind - cinematic edition (Remastered).mp3',
    range: [0, T.duration],
    background: '#000000',
    fx: [{ type: 'grain', amount: 0.035 }],
    shots,
    overlays: [
      { id: 'lyrics', start: 0, end: T.duration, layers: [{ type: 'canvas', module: 'lyric', params: { style: 'line', y: 960, size: 64, uppercase: true, color: '#0b0b0c', dim: 0.3 } }] },
    ],
  };
}
