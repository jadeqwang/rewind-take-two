// Typography / HUD / residue kit demo: each shot sits at the moment of the song the shot list uses it for.
//   node render/engine/render.mjs --timeline render/engine/demo/kit.js --stills 16.9,88.3,...   (see README "Kit stills")
const M = 'media/engine_demo/';
// the placeholder clip has a baked red rim light; residueRim remaps saturated reds to residue orange (no red in this film)
const JADE = { type: 'video', src: M + 'circle.mp4', matte: { src: M + 'circle_matte.mp4', mode: 'luma' }, keepColor: true, fit: 'height', grade: { residueRim: 1 } };
// the night plate printed as a negative: reads as an engraving on paper once `isolate` + `engrave` run over it
// (cropped below the skyline strip, which printed as a ragged band along the top edge)
const ENGRAVED = { type: 'image', src: M + 'far.jpg', fit: 'cover', crop: [0, 0.2, 1, 1], scale: 1.05, grade: { exposure: 1.8, contrast: 1.15, invert: true } };
const PAPER_FX = [{ type: 'isolate', amount: 1, engrave: 0.6, cell: 5 }, { type: 'paper', amount: 0.6 }, { type: 'grain', amount: 0.04 }];
const kb = (a, b) => ({ from: { scale: a }, to: { scale: b } });

export default {
  name: 'engine_kit',
  range: [13, 228],
  background: '#ece7dc',
  shots: [
    { id: 'lowerthird', start: 13.0, end: 18.6, background: '#ece7dc', layers: [{ ...ENGRAVED, kenBurns: kb(1.1, 1.2) },
      { type: 'canvas', module: 'lowerthird', stage: 'post', params: { color: '#0b0b0c', halo: 0.85 } }], fx: PAPER_FX },
    { id: 'sign', start: 21.2, end: 23.3, layers: [{ ...ENGRAVED, y: 120, kenBurns: kb(1.15, 1.35) },
      { type: 'canvas', module: 'pin', params: { style: 'sign', text: "LAKE SHORE DR\nI'm speeding down Lake Shore", sync: 'lyric', at: -1.2,
        corners: [[0, [560, 170, 1380, 230, 1372, 500, 566, 470]], [2.1, [470, 120, 1470, 200, 1460, 540, 476, 500]]] } }], fx: PAPER_FX },
    { id: 'etch', start: 23.9, end: 28.0, background: '#0b0b0c', layers: [{ ...ENGRAVED, grade: { exposure: 0.8 } },
      { type: 'canvas', module: 'etch', blend: 'screen', params: { text: "a shadow chasing me I couldn't place", sync: 'lyric', size: 46, corners: [380, 820, 1560, 790, 1562, 862, 382, 900] } }],
      fx: [{ type: 'isolate', amount: 1, engrave: 0.5 }, { type: 'vignette', amount: 0.5 }] },
    { id: 'dialogue', start: 33.5, end: 37.9, layers: [{ ...ENGRAVED }, { type: 'canvas', module: 'dialogue', stage: 'post', params: { speaker: 'JADE' } }], fx: PAPER_FX },
    { id: 'motes', start: 39.9, end: 41.04, layers: [{ ...ENGRAVED }, { ...JADE, scale: 1.0, x: 120, freeze: 0.34, in: 2 },
      { type: 'canvas', module: 'motes', keepColor: true, params: { at: 'word:shot', x: 1060, y: 760 } },
      { type: 'canvas', module: 'whisper', stage: 'post', params: { text: 'shot', sync: 'lyric', x: 1500, y: 960 } }], fx: PAPER_FX },
    { id: 'negative', start: 41.04, end: 41.4, layers: [{ ...ENGRAVED }, { ...JADE, scale: 1.0, x: 120, freeze: 0, in: 2.34 },
      { type: 'canvas', module: 'motes', keepColor: true, params: { at: 40.24, x: 1060, y: 760 } }],
      fx: [...PAPER_FX, { type: 'negative', amount: [[0, 0], [0.3, 1]] }, { type: 'tapeStop', at: 0, dur: 0.3, toBlack: false }] },
    { id: 'pause', start: 41.4, end: 42.38, layers: [{ ...ENGRAVED }, { ...JADE, scale: 1.0, x: 120, freeze: 0, in: 2.34 },
      { type: 'canvas', module: 'motes', keepColor: true, params: { at: 40.24, x: 1060, y: 760 } },
      { type: 'canvas', module: 'hud', stage: 'post', params: { mode: 'pause', cursor: [['word:time', 0, 'outBack'], ['word:time+0.25', 1]], blinkAt: 'word:stops' } }],
      fx: [...PAPER_FX, { type: 'negative', amount: 1 }, { type: 'hold', at: 0 }] },
    { id: 'title', start: 48.42, end: 50.4, background: '#ece7dc', layers: [{ type: 'canvas', module: 'title', params: { arrive: { at: 0.05, every: 0.09 }, flip: { stagger: 0.07 } } }],
      fx: [{ type: 'paper', amount: 0.7 }, { type: 'grain', amount: 0.04 }] },
    { id: 'slam', start: 84.86, end: 88.6, layers: [{ type: 'video', src: M + 'run.mp4', in: 2 }, { type: 'canvas', module: 'slam', stage: 'post', params: { mode: 'stack', text: 'back on the road', sync: 'lyric', color: '#ece7dc', accent: '#F08A24', size: 170, y: 560 } }],
      fx: [{ type: 'isolate', amount: 1, engrave: 0.45 }, { type: 'punch', on: 'words', amount: 0.03 }] },
    { id: 'loading', start: 93.07, end: 94.06, layers: [{ type: 'canvas', module: 'hud', params: { mode: 'loading', title: 'Reload.', tip: 'The Time Variance █████████ can only follow what it can trace.', deaths: 4097 } }] },
    { id: 'ground', start: 98.2, end: 103.7, background: '#ece7dc', layers: [{ ...ENGRAVED, kenBurns: kb(1.2, 1.3) },
      { type: 'canvas', module: 'pin', blend: 'multiply', params: { style: 'ground', text: 'I zigzag across the field of grass', sync: 'lyric', size: 110, corners: [560, 640, 1360, 640, 1780, 900, 140, 900] } }], fx: PAPER_FX },
    { id: 'continue', start: 111.22, end: 112.96, background: '#0b0b0c', layers: [{ type: 'canvas', module: 'hud', params: { mode: 'continue', from: 9, every: 0.8 } }] },
    { id: 'ghosts', start: 113.89, end: 119.4, layers: [{ ...ENGRAVED },
      { type: 'ghosts', src: M + 'circle.mp4', matte: { src: M + 'circle_matte.mp4' }, fit: 'height', scale: 0.42, y: 120, on: 'vocal_chops',
        generate: { count: 13, seed: 4, area: [-820, -260, 820, 300], scale: [0.8, 1.15], offset: [0, 5], opacity: [0.55, 0.8] } },
      { ...JADE, scale: 0.62, y: 205 },
      { type: 'canvas', module: 'hud', stage: 'post', params: { mode: 'platformer', side: 'right', color: '#0b0b0c', iteration: 4097, deaths: { base: 4084, on: 'vocal_chops', from: 113.8 }, timer: { from: 56.54 } } }],
      fx: [{ type: 'isolate', amount: 1, engrave: 0.55 }, { type: 'paper', amount: 0.5 }] },
    { id: 'swarm', start: 123.0, end: 126.25, layers: [{ ...ENGRAVED },
      { type: 'ghosts', src: M + 'circle.mp4', matte: { src: M + 'circle_matte.mp4' }, fit: 'height', scale: 0.25, y: 60,
        generate: { count: 100, seed: 9, area: [-900, -330, 900, 380], scale: [0.6, 1.3], offset: [0, 6], quantize: 0.5, opacity: [0.5, 0.85] } },
      { type: 'ghosts', src: M + 'circle.mp4', matte: { src: M + 'circle_matte.mp4' }, fit: 'height', scale: 0.5, x: 520, y: 200, graphite: true,
        instances: [{ x: 0, y: 0, offset: -0.4, opacity: 0.6 }] }],   // the V2i speedrun ghost: graphite
      fx: [{ type: 'isolate', amount: 1, engrave: 0.55 }, { type: 'paper', amount: 0.5 }] },
    { id: 'pencil', start: 126.25, end: 130.5, background: '#ece7dc', layers: [{ ...ENGRAVED },
      { type: 'solid', color: '#f3eee2', rect: [560, 330, 820, 380], rotate: -3, keepColor: true },
      { type: 'canvas', module: 'pencil', keepColor: true, params: { text: "What's an anagram of\nBanach–Tarski?", at: 0.4, cps: 14, size: 76, x: 620, y: 450, rotate: -3 } }], fx: PAPER_FX },
    { id: 'terminal', start: 138.8, end: 141.0, layers: [{ type: 'canvas', module: 'terminal', params: {
      lines: ['TIME VARIANCE █████████', '> SCAN ITERATION 4,097', { text: 'ANOMALY DETECTED.', sync: 'lyric' }], cps: 40, alarm: [[0, 0, 'hold'], ['word:detected', 1]], blink: 3 } }] },
    { id: 'follow', start: 152.0, end: 155.0, layers: [{ ...ENGRAVED }, { ...JADE, id: 'jade', scale: 0.8, x: [[0, -500], [3, 500]], y: 100 },
      { type: 'canvas', module: 'ribbon', keepColor: true, params: { follow: { layer: 'jade', point: 'top', offset: [0, 120] }, trail: 2.5, width: 34, drift: [-120, 0] } }],
      fx: PAPER_FX },
    { id: 'trace', start: 167.4, end: 171.0, background: '#ece7dc', layers: [{ ...ENGRAVED, opacity: 0.35 },
      { type: 'canvas', module: 'trace', params: { text: 'trace', at: 'word:trace', size: 240, ghost: 0.08 } }], fx: PAPER_FX },
    { id: 'iteration', start: 226.0, end: 227.9, background: '#000000', layers: [
      { type: 'canvas', module: 'hud', params: { mode: 'iteration', base: 4097, rate: 2.5, from: 0.3, flicker: 0.3, side: 'left', size: 34 } },
      { type: 'canvas', module: 'pencil', params: { text: 'never stop.', sync: 'lyric', at: -0.2, color: '#b5b0a6', size: 96, x: 760, y: 580 } }] },
  ],
};
