// v9 fix #2 round 2: D3 alone, with the round-2 values, for checking before the lead edits A.js (the D3 block here
// is exactly the proposed A.js block; see docs/revisions/v9/fix_2_3_mirrors.md, Round 2).
//   FFMPEG=... node render/engine/render.mjs --timeline tools/v9/mirrors/_d3_solo.js --preview --range 25 28.4 --encode --out <file>
import { D3_PLATE_R2, D3_ETCH_L_R2, D3_ETCH_R_R2 } from './d3_tracks_r2.js';

const INK = '#0b0b0c';
const LETTERBOX = { type: 'letterbox', aspect: 2.39, amount: 1 };
const ETCH = (text, corners) => [
  { type: 'canvas', module: 'etch', noRewind: true, x: 2, y: 2, opacity: 0.85, params: { text, sync: 'lyric', size: 60, padding: 4, corners, color: INK } },
  { type: 'canvas', module: 'etch', noRewind: true, params: { text, sync: 'lyric', size: 60, padding: 4, corners, color: '#fbf8f1' } },
];
export const D3_R2 = {
  id: 'D3', start: 25.34, end: 28.4, background: INK,
  layers: [
    { id: 'D3_plate', type: 'video', fit: 'cover', src: 'media/shots/D3/v9_take_2_push_r2.mp4', in: 0.0, rate: 1 },
    { type: 'canvas', module: 'tools/v4B/plate/plate.js', noRewind: true, params: { text: 'TVA 1729', corners: D3_PLATE_R2, grow: 2.4, aspect: 2.3, dim: 0.12, light: 0.8, mirror: true } },
    ...ETCH('me I', D3_ETCH_L_R2),
    ...ETCH("couldn't\nplace", D3_ETCH_R_R2),
  ], fx: [LETTERBOX] };

export default () => ({ name: 'd3_solo', audio: 'inputs/Rewind - cinematic edition (Remastered).mp3', range: [25.34, 28.4],
  background: '#000000', fx: [{ type: 'grain', amount: 0.035 }], shots: [D3_R2], overlays: [] });
