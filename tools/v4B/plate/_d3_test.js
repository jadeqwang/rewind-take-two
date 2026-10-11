// Variant sheet for the D3 plate (v4B-plate): the same take with different plate settings, 4 s apart from t = 100.
//   node render/engine/render.mjs --timeline tools/v4B/plate/_d3_test.js --preview --stills 101,102,105,106,109,110  (lit at +1.0 s, unlit at +2.0 s)
import tracks from '../../../render/timeline/_A_tracks.js';
const LIGHT = [[0, 0], [0.42, 0.05], [0.5, 0.19], [0.75, 0.83], [1.0, 0.97], [1.25, 0.4], [1.42, 0.03], [2.4, 0.04], [2.5, 0.16], [2.75, 0.71], [3.0, 1]];
// level (b): the same push as D3_CAM in render/timeline/A.js
const PUSH = lt => { const k = Math.min(1, Math.max(0, lt / 2.6)), e = 0.5 - 0.5 * Math.cos(Math.PI * k); return { s: 1 + 0.22 * e, x: -143 * e, y: 65 * e }; };
const CAM = { scale: lt => PUSH(lt).s, x: lt => PUSH(lt).x, y: lt => PUSH(lt).y };
export const VARIANTS = [
  { text: 'TVA 1729', grow: 1, aspect: null, dim: 0.12 },               // level 0: exactly the take's scribble
  { text: 'TVA 1729', grow: 1.5, aspect: 2.3, dim: 0.12 },              // level (a)
  { text: 'TVA 1729', grow: 1.5, aspect: 2.3, dim: 0.12, cam: CAM },    // level (b)
  { text: 'TVA 1729', grow: 1.5, aspect: 2.3, dim: 0.4, cam: CAM },
  // what the shipped plate looks like at 1080p pixel density: a 2x punch-in on the plate at preview size
  { text: 'TVA 1729', grow: 1.5, aspect: 2.3, dim: 0.12, cam: { scale: 2, x: -(1411 - 960) * 2, y: -(529 - 540) * 2 } },
];
export default {
  name: 'v4B_plate_test', range: [100, 100 + 4 * VARIANTS.length], background: '#0b0b0c',
  fx: [{ type: 'grain', amount: 0.035, seed: 'twos' }],
  shots: VARIANTS.map((v, k) => ({ id: `V${k}`, start: 100 + 4 * k, end: 104 + 4 * k, background: '#0b0b0c',
    layers: [
      { id: `p${k}`, type: 'video', fit: 'cover', src: 'media/shots/D3/take_2_engraved.mp4', in: 0, rate: 1, ...(v.cam || {}) },
      { type: 'canvas', module: 'tools/v4B/plate/plate.js', noRewind: true, params: { corners: tracks.D3_plate, light: LIGHT, ...v } },
    ], fx: [{ type: 'letterbox', aspect: 2.39, amount: 1 }] })),
};
