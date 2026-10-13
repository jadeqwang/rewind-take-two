// Section C: Verse 2, "the precision platformer" (V2a–V2n, 56.54–112.96). Director's doc: docs/sections/C.md
// Cut list locked to the timing.json beat grid. Each row = one cut: [start, end, clip, take, clipIn, rate, extra].
// Plates are engraved takes (tools/engrave); clips with Jade carry the engrave matte so she stays in colour.
import verse2B, { RELOAD_SKIP } from './_B_verse2.js';   // rev-B: 94.06–112.96 (the restaged chase) lives in _B_verse2.js
import carShot from '../../tools/v4B/car/car_shot.js';   // v4: the 1:30 car shot (V2f)
const CAR_START = 89.26;   // v4: the car shot starts on this tracked beat (89.26 = bar 51 beat 3); 90.14 = v3's cut
const S = 'media/shots/';
const GIRL = new Set(['V2a3', 'V2b3', 'V2c4', 'V2c5', 'V2d2', 'V2e2', 'V2f2', 'V2h1', 'V2i1', 'V2i2', 'V2i3', 'V2i4',
  'V2j1', 'V2j2', 'V2k1', 'V2k2', 'V2k3', 'V2l1', 'V2l2', 'V2m1', 'V2n1']);
const PAPER = '#ece7dc', INK = '#0b0b0c', ORANGE = '#F08A24';

// V2c7 (v3): the fleet as an Escher tessellation (module `tessellate`) on the road of V2c7 take 2. The camera is
// fitted to that plate; the shot opens zoomed into the flat tiling and pulls out to the wide (plate and module
// share TESS_Z about TESS_PV). She drives south and the camera looks back north: lake on screen-right, park on
// screen-left, so the HUD gets an ink corner chip over the bright lake for this shot only (TESS_CHIP).
// v2 row, to switch back: [80.44, 82.22, 'V2c7', 1, 1.0, 1, { hero: true }]
const TESS_PV = [960, 330], TESS_Z = [[0, 2.8, 'linear'], [0.44, 2.5, 'inOutCubic'], [1.2, 1.27, 'linear'], [1.78, 1.2]];
const tessK = (f) => TESS_Z.map(([t, z, e]) => [t, f(z), e]);
const TESS = { type: 'canvas', module: 'tessellate', params: { cam: { f: 1100, pitch: 21, h: 4.6, cx: 960, cy: 540, x0: -0.5 },
  cols: 8, len: 1.95, front: 13.9, t0: 80.44, advance: 0.42, parity: 1, vol: [12.5, 17], road: [11.5, 16], shape: [30, 46], far: [34, 56],
  zoom: { z: TESS_Z, px: TESS_PV[0], py: TESS_PV[1] } } };
const TESS_CHIP = { type: 'solid', stage: 'post', color: INK, rect: [1436, 0, 484, 192], opacity: 0.95 };

const CUTS = [
  // V2a car chase (bar 33): HUD pops in on the first frame
  [56.54, 58.30, 'V2a1', 1, 0.5, 1],
  [58.30, 59.20, 'V2a2', 1, 0.5, 1],
  [59.20, 60.08, 'V2a3', 3, 0.3, 1],
  [60.08, 61.40, 'V2a4', 2, 0.5, 1],
  [61.40, 62.30, 'V2a5', 1, 0.3, 1],
  [62.30, 63.62, 'V2a3', 3, 3.4, 1],
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
  [76.90, 78.66, 'V2c5', 2, 0.3, 1.2, { hero: true }],
  [78.66, 79.56, 'V2c3', 1, 3.0, 1.2, { scale: 1.3, y: 150 }],
  [79.56, 80.44, 'V2c6', 1, 1.5, 1.2],
  [80.44, 82.22, 'V2c7', 2, 1.0, 1, { hero: true, scale: TESS_Z, y: tessK(z => (TESS_PV[1] - 540) * (1 - z)), over: [TESS, TESS_CHIP] }],
  [82.22, 83.10, 'V2c8', 1, 0.0, 1],
  // V2d the jump (bar 48): lift-off on 83.54, hang through the band hole 84.04–84.74
  [83.10, 83.98, 'V2d1', 1, 2.0, 1],
  [83.98, 84.86, 'V2d2', 4, 2.0, 0.6, { frameBlend: true, hero: true, scale: [[0, 1.3], [0.88, 1.5, 'out']], x: [[0, -130], [0.88, -230, 'out']], y: [[0, 110], [0.88, 190, 'out']] }],
  // V2e "back" slams on the bar-49 downbeat
  [84.86, 86.18, 'V2e1', 1, 0.0, 1, { slam: true }],
  [86.18, 87.06, 'V2e2', 2, 0.3, 1, { scale: 1.4, x: -330, y: 200 }],
  [87.06, 88.38, 'V2e3', 1, 0.0, 1.2],
  // V2f sirens in my mirror (bar 51). v4 (Jade's 1:30 note, option C): V2f2 is replaced by the over-the-shoulder push
  // into the rear-view mirror, built in tools/v4B/car/car_shot.js and added in sectionC() below; it starts at CAR_START.
  // v3 rows, to switch back: [88.38, 90.14, 'V2f1', 1, 0.0, 1], [90.14, 92.79, 'V2f2', 2, 0.5, 1] (+ C_lyr_sirens etch)
  [88.38, CAR_START, 'V2f1', 1, 0.0, 1],
  // V2g kaizo trap: 5 frames of L train, 2 frames black
  [92.79, 93.00, 'V2g1', 1, 0.72, 1, { scale: 1.3, y: 40, flash: true }],
  // V2h respawn (bar 54), V2i race, V2j field (top-down), V2k too fast, V2l ring, V2m shot
  [93.66, 94.06, 'V2h1', 2, 0.25, 1.2, { scale: 1.5, x: 480, y: -240 }],
];

// v6 (Jade 0:59, 1:24, 1:26; docs/revisions/v6/o2_erasers.md): canon is one pale-blue and one pink eraser in her bun.
// These takes drew both pink: *_blue = the same plate with one eraser recoloured in every frame (tools/blue_eraser.py).
// The mattes are unchanged.
const BLUE_ERASER = { V2a3_3: 'take_3_engraved_blue.mp4', V2d2_4: 'take_4_engraved_blue.mp4', V2e2_2: 'take_2_engraved_blue.mp4' };
const plate = (clip, take) => `${S}${clip}/${BLUE_ERASER[`${clip}_${take}`] ?? `take_${take}_engraved.mp4`}`;
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
  if (x.ghost) {  // V2i: an earlier attempt (iteration 4,094, the one that missed the chasm jump), her own clip as a graphite ghost 5 frames behind in time,
    // drawn under her: half a body ahead at first, then falling behind as she pulls ahead (x keys, design px)
    layers.splice(1, 0, { id: 'ghost', type: 'ghosts', src: plate(clip, take), matte: matte(clip, take).src, fit: 'cover',
      in: clipIn, rate, graphite: true, x: x.ghost, instances: [{ offset: -0.21, opacity: 0.62 }] });
  }
  if (x.ribbon) layers.push({ type: 'canvas', module: 'ribbon', keepColor: true,
    params: { follow: { layer: 'jade', point: 'centroid', smooth: 3 }, trail: x.ribbon, width: x.ribbonWidth || 46, drift: x.drift || [0, 0], seed: i } });
  if (x.over) layers.push(...x.over);   // extra layers above the plate (V2c7 tessellation)
  const fx = [];
  if (x.hero) fx.push({ type: 'punch', amount: 0.025, on: 'downbeat' });
  else fx.push({ type: 'punch', amount: 0.018, on: 'beat' });
  if (x.flash) fx.push({ type: 'flash', at: [x.flashAt ?? 0.12], dur: 0.05, amount: x.flashAmt ?? 0.9 });
  if (x.slam) fx.push({ type: 'flash', at: [0], dur: 0.084, amount: 0.4 }, { type: 'shake', amp: 26, freq: 18, decay: 0.35, on: [start] });
  return { id: `C${String(i + 1).padStart(2, '0')}_${clip}`, start, end, background: INK, layers, fx };
}

export default function sectionC({ T }) {
  const shots = [...CUTS.map((c, i) => shotFor(c, i, T)), ...verse2B({ T }).shots];

  shots.push(carShot(CAR_START, 92.79));   // v4: V2f car shot (SIRENS on the sign, IN MY MIRROR on the mirror, TVA plates)
  // 92.79 kaizo trap → 2 frames of black → "Reload." LOADING screen (V2h)
  shots.push({ id: 'C_V2g_black', start: 93.00, end: 93.07, layers: [{ type: 'solid', color: '#000000' }] });
  shots.push({ id: 'C_V2h_loading', start: 93.07, end: 93.66, background: INK, layers: [
    { type: 'canvas', module: 'hud', params: { mode: 'loading', title: 'Reload.', titleSize: 64, deaths: 4096, spinner: true,
      tip: 'TVA agents can only follow what they can trace.', progress: [[0, 0], [0.55, 1, 'outCubic']], bg: INK } }] });
  shots.sort((a, b) => a.start - b.start);

  const ov = (id, start, end, layer) => ({ id, start, end, layers: [layer] });
  const overlays = [
    // HUD cluster (top-right, this section only); 4-frame pop on bar 33
    ov('C_hud_car', 56.54, CAR_START,   /* v4: ends with the car shot's cut (v3: 90.14) */ { type: 'canvas', module: 'hud', opacity: [[0, 0, 'hold'], [0.042, 1, 'hold'], [0.083, 0.25, 'hold'], [0.125, 1]],
      params: { mode: 'platformer', side: 'right', iteration: 4097, deaths: 4096, timer: { from: '56.54' } } }),
    ov('C_hud_respawn', 93.66, 94.06, { type: 'canvas', module: 'hud', params: { mode: 'platformer', side: 'right', color: INK, margin: 104, iteration: 4097, deaths: 4096, timer: { from: '56.54', offset: RELOAD_SKIP } } }),

    // lyrics
    ov('C_lyr_nowim', 83.40, 84.86, { type: 'canvas', module: 'lowerthird', params: { color: PAPER, text: 'And now I’m', sync: 'lyric', size: 76 } }),
    ov('C_lyr_back', 84.86, Math.min(89.40, CAR_START),   /* v4: never over the car interior (v3: 89.40) */ { type: 'canvas', module: 'slam', params: { text: 'back on the road', sync: 'lyric', font: 'fell', size: 120, x: 1340, y: 200, maxWidth: 1000,
      color: PAPER, accent: ORANGE, impact: 1.4, tilt: 3 } }),
    // v4: "sirens in my mirror" now sits on two surfaces of the car shot (tools/v4B/car/car_shot.js). v3 overlay:
    // ov('C_lyr_sirens', 90.14, 92.79, { type: 'canvas', module: 'pin', params: { style: 'etch', text: 'sirens in my mirror …', sync: 'lyric', size: 74, color: '#fbf8f1', panel: 'rgba(11,11,12,0.6)',
    //   corners: [800, 682, 1780, 746, 1776, 812, 800, 752] } }),
    ...verse2B({ T }).overlays,
  ];
  return { section: 'C', shots, overlays };
}
