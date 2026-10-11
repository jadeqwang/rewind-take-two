// Engine demo (13 s, song time 82.0–95.0: "Now I'm back on the road / Sirens in my mirror … reload").
// Exercises: video forward → tape stop → the same shot rewound (comp layer, ×2 ×4 ×8 HUD, residue un-spooling),
// parallax side-scroller + matted/keyed Jade in colour over an engraved world, death counter on beats, word-synced lyric,
// speed ramp + frame blending + freeze frame, a Three.js isometric module, bar:beat and word-referenced cuts.
//   node render/engine/render.mjs --timeline render/engine/demo/timeline.js --preview
const M = 'media/engine_demo/';

// Jade's hip in run.mp4 (in-point 1.0 s), read off a 2 fps contact sheet: [shot-local s, x, y] in design px
const RUN_PATH = [[0, 707, 490], [0.5, 743, 520], [1, 803, 508], [1.5, 845, 532], [2, 923, 550], [2.5, 947, 532], [3, 935, 490], [3.5, 953, 502], [4, 947, 520], [4.5, 965, 502]];
// her fingertip circles (circle.mp4 at scale .62, x 400, y 205 below; fingertip loop ≈ (.49, .46) of the clip): CCW, one turn per 1.1 s
const CIRCLE_PATH = Array.from({ length: 41 }, (_, k) => { const t = k * 0.1, a = -2 * Math.PI * t / 1.1 + 0.6; return [t, 1348 + 72 * Math.cos(a), 712 + 56 * Math.sin(a)]; });

export default {
  name: 'engine_demo',
  audio: 'inputs/Rewind - cinematic edition (Remastered).mp3',
  range: [82.0, 95.0],
  background: '#000000',
  fx: [{ type: 'grain', amount: 0.045 }, { type: 'vignette', amount: 0.22 }],

  shots: [
    { // 1. she runs; the tape stops under her
      id: 'run', start: 82.0, end: '50:1',
      layers: [
        { type: 'video', src: M + 'run.mp4', in: 1.0, rate: 1, scale: [[0, 1.0], [4.6, 1.06]] },
        { type: 'canvas', module: 'ribbon', keepColor: true, params: { path: RUN_PATH, trail: 3.2, drift: [-230, 6], width: 42, twist: 0.6, glow: 0.7, motes: 0.3 } },
      ],
      fx: [{ type: 'flash', at: [0], dur: 0.1, amount: 0.6 }, { type: 'punch', on: 'downbeat', amount: 0.03 }, { type: 'tapeStop', at: 3.9, dur: 0.7, toBlack: false }],
    },
    { // 2. ◀◀ the shot above, played backward and accelerating (the residue un-spools)
      id: 'rewind', start: '50:1', end: '51:4',
      layers: [
        { type: 'comp', source: 'film', srcTime: [[0, 86.5, 'inCubic'], [3.08, 82.15]], echo: { n: 2, dt: 0.14, alpha: 0.35 } },
      ],
      fx: [{ type: 'rewind', amount: [[0, 1.0], [2.6, 0.7]] }, { type: 'ripple', amount: 0.35 }, { type: 'grade', tint: '#d6e8ff', saturation: 0.8 },
        { type: 'flash', at: [0], dur: 0.08, amount: 0.8, color: '#7ec8ff' }],
    },
    { // 3. side-scroller level: the world is an engraving, Jade (and her residue) the only colour
      id: 'level', start: '51:4', end: 'word:reload',
      layers: [
        { type: 'parallax', speed: 240, layers: [
          { src: M + 'far.jpg', depth: 0.12, scale: 1.25, y: 330, grade: { exposure: 2.4, contrast: 1.15 } },
          { src: M + 'mid.png', depth: 0.45 },
          { src: M + 'near.png', depth: 1.0 },
        ] },
        { type: 'video', src: M + 'circle.mp4', matte: { src: M + 'circle_matte.mp4', mode: 'luma' }, keepColor: true, fit: 'height', scale: 0.62, x: 400, y: 205,
          rate: [[0, 1], [2.2, 1, 'inOut'], [2.9, 0.35]], frameBlend: true, freeze: 3.3, fadeIn: 0.12 },
        { type: 'canvas', module: 'ribbon', keepColor: true, params: { path: CIRCLE_PATH, trail: 1.3, width: 16, pencil: true, glow: 0.8, twist: 0.3, motes: 0.4, seed: 3 } },
      ],
      fx: [{ type: 'isolate', amount: 1, engrave: 0.55, cell: 5 }, { type: 'paper', amount: 0.6 }, { type: 'grain', amount: 0.06 },
        { type: 'letterbox', aspect: 2.39, amount: [[0, 0, 'outCubic'], [0.6, 1]] },
        { type: 'punch', on: 'beat', amount: 0.022 }, { type: 'shake', on: 'downbeat', amp: 12, decay: 0.18 }, { type: 'flash', at: [0], dur: 0.1, amount: 0.7 }],
    },
    { // 4. "reload" = a LOADING screen: the isometric diorama turns a quarter on the downbeat, Jade frozen on the walkway
      id: 'loading', start: 'word:reload', end: 95.0,
      layers: [
        { type: 'three', module: 'iso_test', params: { rotate: [[0, 0, 'hold'], ['54:1', 0, 'inOutCubic'], ['54:1+2b', 90]], zoom: 6.5 } },
        { type: 'video', src: M + 'circle.mp4', in: 3.0, freeze: 0, key: { type: 'luma', low: 0.025, high: 0.09 }, keepColor: true, fit: 'height', scale: 0.22, x: 40, y: -365 },
        { type: 'canvas', module: 'hud', stage: 'post', params: { mode: 'loading', bg: null, title: null, color: '#0b0b0c', tip: 'REWINDING LEAVES RESIDUE.', progress: [[0, 0], [1.5, 1, 'outCubic']] } },
      ],
      fx: [{ type: 'isolate', amount: 1, engrave: 0.35, cell: 5, paper: '#ece7dc' }, { type: 'paper', amount: 0.5 }, { type: 'flash', at: [0], dur: 0.1, amount: 0.6 }],
      background: '#ece7dc',
    },
  ],

  overlays: [
    { id: 'hud_run', start: 82.0, end: '50:1', layers: [{ type: 'canvas', module: 'hud', params: { mode: 'platformer', deaths: { base: 41, on: 'beat', from: 82.0 }, timer: { from: 70.0 }, level: 'LSD · 1-2', iteration: 7 } }] },
    { id: 'hud_rewind', start: '50:1', end: '51:4', layers: [{ type: 'canvas', module: 'hud', params: { mode: 'rewind', multiplier: [[0, 2, 'hold'], ['50:3', 4, 'hold'], ['51:1', 8]], counter: [[0, 16.5, 'inCubic'], [3.08, 12.15]], scrub: [[0, 0.95, 'inCubic'], [3.08, 0.1]] } }] },
    { id: 'hud_level', start: '51:4', end: 'word:reload', layers: [{ type: 'canvas', module: 'hud', params: { mode: 'platformer', deaths: { base: 41, on: 'beat', from: 82.0 }, timer: { from: 70.0 }, level: 'LSD · 1-3', iteration: 8 } }] },
    { id: 'lyrics', start: 82.0, end: 95.0, layers: [{ type: 'canvas', module: 'lyric', params: { style: 'line', y: 935, size: 68, uppercase: true,
      // ink on the paper-white loading screen (keyframes may use absolute times: the cut is on the word "reload")
      color: [[0, '#ece7dc', 'hold'], ['word:reload', '#0b0b0c']], clearing: [[0, 0.55, 'hold'], ['word:reload', 0]] } }] },
  ],
};
