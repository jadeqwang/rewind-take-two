// Section C: Verse 2, "the precision platformer" (V2a–V2n, 56.54–112.96). Director's doc: docs/sections/C.md
// Cut list locked to the timing.json beat grid. Each row = one cut: [start, end, clip, take, clipIn, rate, extra].
// Plates are engraved takes (tools/engrave); clips with Jade carry the engrave matte so she stays in colour.
const S = 'media/shots/';
const GIRL = new Set(['V2a3', 'V2b3', 'V2c4', 'V2c5', 'V2d2', 'V2e2', 'V2f2', 'V2h1', 'V2i1', 'V2i2', 'V2i3', 'V2i4',
  'V2j1', 'V2j2', 'V2k1', 'V2k2', 'V2k3', 'V2l1', 'V2l2', 'V2m1', 'V2n1']);
const PAPER = '#ece7dc', INK = '#0b0b0c', ORANGE = '#F08A24';

const CUTS = [
  // V2a car chase (bar 33): HUD pops in on the first frame
  [56.54, 58.30, 'V2a1', 1, 0.5, 1],
  [58.30, 59.20, 'V2a2', 1, 0.5, 1],
  [59.20, 60.08, 'V2a3', 2, 0.3, 1],
  [60.08, 61.40, 'V2a4', 2, 0.5, 1],
  [61.40, 62.30, 'V2a5', 1, 0.3, 1],
  [62.30, 63.62, 'V2a3', 2, 3.4, 1],
  // V2b kaizo road (bar 37): a cut every 2 beats, each trap = setup + payoff
  [63.62, 64.50, 'V2b1', 1, 1.0, 1],
  [64.50, 65.40, 'V2b1', 1, 2.4, 1.6],
  [65.40, 66.28, 'V2b2', 1, 0.3, 1.3],
  [66.28, 67.16, 'V2b3', 1, 0.0, 1],
  [67.16, 68.06, 'V2b4', 2, 0.2, 1],
  [68.06, 68.94, 'V2b4', 2, 1.2, 1.2],
  [68.94, 69.82, 'V2a2', 1, 2.5, 1],
  [69.82, 70.70, 'V2b5', 1, 0.8, 1.2],
  [70.70, 71.58, 'V2b6', 1, 1.6, 1.2],
  [71.58, 72.48, 'V2b6', 1, 3.5, 1.6],
  // V2c the bridge (bar 42): three held heroes on the "oh" swells (73.34, 76.93, 80.46)
  [72.48, 73.34, 'V2c1', 1, 1.0, 1.5],
  [73.34, 75.12, 'V2c2', 1, 1.5, 1, { hero: true }],
  [75.12, 76.02, 'V2c3', 1, 1.4, 1, { scale: 1.3, y: 150 }],
  [76.02, 76.90, 'V2c4', 1, 1.0, 1],
  [76.90, 78.66, 'V2c5', 1, 0.5, 1.2, { hero: true }],
  [78.66, 79.56, 'V2c3', 1, 3.0, 1.2, { scale: 1.3, y: 150 }],
  [79.56, 80.44, 'V2c6', 1, 1.5, 1.2],
  [80.44, 82.22, 'V2c7', 1, 1.0, 1, { hero: true }],
  [82.22, 83.10, 'V2c8', 1, 0.0, 1],
  // V2d the jump (bar 48): lift-off on 83.54, hang through the band hole 84.04–84.74
  [83.10, 83.98, 'V2d1', 1, 2.0, 1],
  [83.98, 84.86, 'V2d2', 2, 1.0, 0.6, { frameBlend: true, hero: true, scale: [[0, 1.3], [0.88, 1.5, 'out']], x: [[0, -130], [0.88, -230, 'out']], y: [[0, 110], [0.88, 190, 'out']] }],
  // V2e "back" slams on the bar-49 downbeat
  [84.86, 86.18, 'V2e1', 1, 0.0, 1, { slam: true }],
  [86.18, 87.06, 'V2e2', 1, 1.0, 1],
  [87.06, 88.38, 'V2e3', 1, 0.0, 1.2],
  // V2f sirens in my mirror (bar 51)
  [88.38, 90.14, 'V2f1', 1, 0.0, 1],
  [90.14, 92.79, 'V2f2', 1, 0.5, 1],
  // V2g kaizo trap: 5 frames of L train, 2 frames black
  [92.79, 93.00, 'V2g1', 1, 0.72, 1, { scale: 1.3, y: 40, flash: true }],
  // V2h respawn (bar 54), V2i race, V2j field (top-down), V2k too fast, V2l ring, V2m shot
  [93.66, 94.06, 'V2h1', 1, 0.4, 1.2],
  [94.06, 95.86, 'V2i1', 1, 0.5, 1, { ghost: [[0, 230], [0.9, 60, 'inOut'], [1.8, -170, 'inOut']] }],
  [95.86, 96.74, 'V2i1', 1, 2.6, 1, { ghost: [[0, -190], [0.88, -420, 'inOut']] }],
  [96.74, 97.62, 'V2i3', 1, 0.5, 1, { ghost: [[0, -160], [0.88, -380, 'inOut']] }],
  [97.62, 98.28, 'V2i4', 1, 0.3, 1.5],
  [98.28, 100.70, 'V2j1', 1, 0.0, 1, { ribbon: 2.4 }],
  [100.70, 102.46, 'V2j2', 1, 0.3, 1.3],
  [102.46, 104.22, 'V2j1', 1, 3.5, 1, { ribbon: 1.7 }],
  [104.22, 105.98, 'V2k2', 2, 1.2, 1, { stutter: 1.35, scale: 1.06 }],
  [105.98, 107.72, 'V2k2', 2, 3.6, 1, { stutter: 1.35, scale: 1.06 }],
  [107.72, 108.67, 'V2k3', 2, 0.5, 1.2],
  [108.67, 109.92, 'V2l1', 1, 0.3, 1.5, { stutter: 1.0 }],
  [109.92, 110.78, 'V2l2', 1, 1.4, 1],
  [110.78, 111.22, 'V2m1', 2, 0.35, 1, { flash: true, flashAt: 0.1, flashAmt: 0.45 }],
  [112.66, 112.96, 'V2n1', 1, 1.78, 1],
];

const plate = (clip, take) => `${S}${clip}/take_${take}_engraved.mp4`;
const matte = (clip, take) => ({ src: `${S}${clip}/take_${take}_matte/matte.mp4`, mode: 'luma' });

function videoLayer(clip, take, clipIn, rate, x = {}) {
  const v = { id: `${clip}_t${take}`, type: 'video', src: plate(clip, take), in: clipIn, rate, fit: 'cover' };
  if (x.scale) v.scale = x.scale;
  if (x.y) v.y = x.y;
  if (x.x) v.x = x.x;
  if (x.frameBlend) v.frameBlend = true;
  return v;
}

// beat-stepped clock: the plate jumps forward on every beat (frame-skipping agents); Jade (matte) stays continuous
function stutterLayers(clip, take, clipIn, rate, k, start, end, T, scale = 1) {
  const beats = T.beats.filter(t => t > start + 0.02 && t < end - 0.02);
  const keys = [[0, clipIn, 'hold']];
  for (const b of beats) keys.push([b - start, clipIn + (b - start) * rate * k, 'hold']);
  keys.push([end - start, clipIn + (end - start) * rate * k]);
  const layers = [
    { id: `${clip}_live`, type: 'video', src: plate(clip, take), in: clipIn, rate, fit: 'cover', scale },
    { id: `${clip}_held`, type: 'video', src: plate(clip, take), srcTime: keys, fit: 'cover', scale,
      matte: { ...matte(clip, take), mode: 'lumaInv' } },
  ];
  if (GIRL.has(clip)) layers.push({ id: `${clip}_jade`, type: 'video', src: plate(clip, take), in: clipIn, rate, fit: 'cover', scale,
    matte: matte(clip, take), keepColor: true });
  return layers;
}

function shotFor([start, end, clip, take, clipIn, rate, x = {}], i, T) {
  const layers = x.stutter ? stutterLayers(clip, take, clipIn, rate, x.stutter, start, end, T, x.scale)
    : [videoLayer(clip, take, clipIn, rate, x)];
  const needJade = x.ghost || x.ribbon;
  if (!x.stutter && needJade) {  // Jade again through her matte (keeps colour, drives the ribbon tracker)
    layers.push({ id: 'jade', type: 'video', src: plate(clip, take), in: clipIn, rate, fit: 'cover',
      matte: matte(clip, take), keepColor: true });
  }
  if (x.ghost) {  // V2i: her previous attempt (iteration 4,096), her own clip as a graphite ghost 5 frames behind in time,
    // drawn under her: half a body ahead at first, then falling behind as she pulls ahead (x keys, design px)
    layers.splice(1, 0, { id: 'ghost', type: 'ghosts', src: plate(clip, take), matte: matte(clip, take).src, fit: 'cover',
      in: clipIn, rate, graphite: true, x: x.ghost, instances: [{ offset: -0.21, opacity: 0.62 }] });
  }
  if (x.ribbon) layers.push({ type: 'canvas', module: 'ribbon', keepColor: true,
    params: { follow: { layer: 'jade', point: 'centroid', smooth: 3 }, trail: x.ribbon, width: x.ribbonWidth || 46, drift: x.drift || [0, 0], seed: i } });
  const fx = [];
  if (x.hero) fx.push({ type: 'punch', amount: 0.025, on: 'downbeat' });
  else fx.push({ type: 'punch', amount: 0.018, on: 'beat' });
  if (x.flash) fx.push({ type: 'flash', at: [x.flashAt ?? 0.12], dur: 0.05, amount: x.flashAmt ?? 0.9 });
  if (x.slam) fx.push({ type: 'flash', at: [0], dur: 0.084, amount: 0.4 }, { type: 'shake', amp: 26, freq: 18, decay: 0.35, on: [start] });
  return { id: `C${String(i + 1).padStart(2, '0')}_${clip}`, start, end, background: INK, layers, fx };
}

export default function sectionC({ T }) {
  const shots = CUTS.map((c, i) => shotFor(c, i, T));

  // 92.79 kaizo trap → 2 frames of black → "Reload." LOADING screen (V2h)
  shots.push({ id: 'C_V2g_black', start: 93.00, end: 93.07, layers: [{ type: 'solid', color: '#000000' }] });
  shots.push({ id: 'C_V2h_loading', start: 93.07, end: 93.66, background: INK, layers: [
    { type: 'canvas', module: 'hud', params: { mode: 'loading', title: 'Reload.', titleSize: 64, deaths: 4097, spinner: true,
      tip: 'The Time Variance █████████ can only follow what it can trace.', progress: [[0, 0], [0.55, 1, 'outCubic']], bg: INK } }] });
  // V2n: freeze on the hit, invert (P5 grammar), arcade CONTINUE? 9 … 8; the ◀◀ slam is the V2n1 cut at 112.66
  shots.push({ id: 'C_V2n_continue', start: 111.22, end: 112.66, background: PAPER, layers: [
    { type: 'video', src: plate('V2m1', 2), in: 0.79, rate: 1, freeze: 0, fit: 'cover', x: [[0, 0], [0.3, 330, 'outCubic']] },
    { type: 'video', src: plate('V2m1', 2), in: 0.79, rate: 1, freeze: 0, fit: 'cover', x: [[0, 0], [0.3, 330, 'outCubic']], matte: matte('V2m1', 2), keepColor: true },
    { type: 'solid', color: PAPER, rect: [0, 0, 780, 1080], opacity: [[0, 0], [0.3, 0.92]] },  // inverts to ink under `negative`
  ], fx: [{ type: 'negative', amount: [[0, 0], [0.3, 1, 'outCubic']] }, { type: 'wobble', amount: [[0, 0.6], [0.4, 0]] }] });
  shots.sort((a, b) => a.start - b.start);

  const ov = (id, start, end, layer) => ({ id, start, end, layers: [layer] });
  const overlays = [
    // HUD cluster (top-right, this section only); 4-frame pop on bar 33
    ov('C_hud_car', 56.54, 90.14, { type: 'canvas', module: 'hud', opacity: [[0, 0, 'hold'], [0.042, 1, 'hold'], [0.083, 0.25, 'hold'], [0.125, 1]],
      params: { mode: 'platformer', side: 'right', iteration: 4097, deaths: 4096, timer: { from: '56.54' } } }),
    ov('C_hud_respawn', 93.66, 94.06, { type: 'canvas', module: 'hud', params: { mode: 'platformer', side: 'right', color: INK, iteration: 4097, deaths: 4097, timer: { from: '56.54' } } }),
    // dark chip behind the race readout (it sat over busy brick); no red anywhere
    { id: 'C_race_chip', start: 94.06, end: 98.28, layers: [{ type: 'solid', color: INK, rect: [1300, 36, 600, 112], opacity: 0.95 }] },
    ov('C_hud_race', 94.06, 98.28, { type: 'canvas', module: 'hud', params: { mode: 'race', side: 'right', iteration: 4096,
      split: [[0, 0.42], [1.8, 0.12], [2.6, -0.04], [4.2, -0.31]], color: PAPER, splitColor: [[0, PAPER, 'hold'], [2.55, '#5fd16a']] } }),
    ov('C_hud_field', 98.28, 110.78, { type: 'canvas', module: 'hud', params: { mode: 'platformer', side: 'right', color: INK, iteration: 4097, deaths: 4097, timer: { from: '56.54' } } }),
    ov('C_hud_continue', 111.30, 112.66, { type: 'canvas', module: 'hud', x: -560, params: { mode: 'continue', from: 9, every: 0.8, start: '111.40', press: 'PRESS ◀◀' } }),

    // lyrics
    ov('C_lyr_nowim', 83.40, 84.86, { type: 'canvas', module: 'lowerthird', params: { color: PAPER, text: 'And now I’m', sync: 'lyric', size: 76 } }),
    ov('C_lyr_back', 84.86, 89.40, { type: 'canvas', module: 'slam', params: { text: 'back on the road', sync: 'lyric', font: 'fell', size: 120, x: 1340, y: 200, maxWidth: 1000,
      color: PAPER, accent: ORANGE, impact: 1.4, tilt: 3 } }),
    ov('C_lyr_sirens', 90.14, 92.79, { type: 'canvas', module: 'pin', params: { style: 'etch', text: 'sirens in my mirror …', sync: 'lyric', size: 74, color: '#fbf8f1', panel: 'rgba(11,11,12,0.6)',
      corners: [800, 682, 1780, 746, 1776, 812, 800, 752] } }),
    ov('C_lyr_race', 94.06, 98.28, { type: 'canvas', module: 'lowerthird', params: { color: INK, halo: 0.9, size: 74 } }),
    ov('C_lyr_zigzag', 98.28, 104.17, { type: 'canvas', module: 'lowerthird', params: { color: '#c8661a', halo: 1, haloColor: PAPER, size: 84, y: 980 } }),
    ov('C_lyr_toofast', 104.17, 108.67, { type: 'canvas', module: 'lowerthird', params: { color: INK, halo: 0.9, size: 74 } }),
    ov('C_lyr_nowarning', 108.67, 110.78, { type: 'canvas', module: 'lowerthird', params: { color: INK, halo: 0.9, size: 74 } }),
    ov('C_lyr_shot', 110.78, 111.62, { type: 'canvas', module: 'whisper', params: { text: 'shot', sync: 'lyric', x: 420, y: 330, size: 44 } }),
    ov('C_lyr_timestops', 111.62, 112.66, { type: 'canvas', module: 'whisper', params: { text: '… and time stops', sync: 'lyric', x: 400, y: 990, size: 34, color: '#a9a49b' } }),
    // the hit: Celeste mote burst at her torso (V2m1 impact point, read off the plate)
    ov('C_motes', 110.78, 112.66, { type: 'canvas', module: 'motes', keepColor: true, params: { at: '110.93', x: 1000, y: 470, count: 64 } }),
    // the ◀◀ on the arcade button (no model-drawn glyphs)
    ov('C_rw_glyph', 112.66, 112.96, { type: 'canvas', module: 'pin', params: { style: 'plain', text: '◀◀', font: '"Press Start 2P"', size: 120, color: INK, x: 700, y: 470, rotate: -8 } }),
  ];
  return { section: 'C', shots, overlays };
}
