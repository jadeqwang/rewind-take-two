// Level (b) of the D3 plate note, NOT in the film: the D3 shot of render/timeline/A.js with a slow push toward the
// mirror (1.0 -> 1.22 over 2.6 s), for comparison with the shipped level (a). Her bun and the two pencils leave the
// frame by the end, which is why it was not shipped.
//   node render/engine/render.mjs --timeline tools/v4B/plate/_d3_push.js --range 25.34 28.4 --preview --encode
import tracks from '../../../render/timeline/_A_tracks.js';
const INK = '#0b0b0c';
const inset = (keys, fx, fy) => keys.map(([t, q]) => {
  const cx = (q[0] + q[2] + q[4] + q[6]) / 4, cy = (q[1] + q[3] + q[5] + q[7]) / 4;
  return [t, q.map((v, i) => (i % 2 ? cy + (v - cy) * fy : cx + (v - cx) * fx))];
});
const D3_QUAD = inset(tracks.D3_etch, 0.62, 2.3).map(([t, q]) => [t, q.map((v, i) => v + (i % 2 ? 40 : -185))]);
// the push: design window x 290..1864, y 158..816 at the end (her face and the etched lyric stay; bun and headphones go)
const PUSH = lt => { const k = Math.min(1, Math.max(0, lt / 2.6)), e = 0.5 - 0.5 * Math.cos(Math.PI * k); return { s: 1 + 0.22 * e, x: -143 * e, y: 65 * e }; };
// a layer's own offset (ox, oy) rides the camera: x = camX + s * ox
const D3_CAM = (ox = 0, oy = 0) => ({ scale: lt => PUSH(lt).s, x: lt => PUSH(lt).x + ox * PUSH(lt).s, y: lt => PUSH(lt).y + oy * PUSH(lt).s });
export default {
  name: 'v4B_plate_push', audio: 'inputs/Rewind - cinematic edition (Remastered).mp3', range: [25.34, 28.4], background: '#000000',
  fx: [{ type: 'grain', amount: 0.035, seed: 'twos' }],
  shots: [
    { id: 'D3', start: 25.34, end: 28.4, background: INK,
      layers: [
        { id: 'D3_plate', type: 'video', fit: 'cover', src: 'media/shots/D3/take_2_engraved.mp4', in: 0.0, rate: 1, ...D3_CAM() },
        { type: 'canvas', module: 'tools/v4B/plate/plate.js', noRewind: true, params: { text: 'TVA 1729', corners: tracks.D3_plate, grow: 1.5, aspect: 2.3, dim: 0.12, cam: D3_CAM(),
          light: [[0, 0], [0.42, 0.05], [0.5, 0.19], [0.75, 0.83], [1.0, 0.97], [1.25, 0.4], [1.42, 0.03], [2.4, 0.04], [2.5, 0.16], [2.75, 0.71], [3.0, 1]] } },
        { type: 'canvas', module: 'etch', noRewind: true, ...D3_CAM(3, 27), opacity: 0.85, params: { text: "me I couldn't\nplace", sync: 'lyric', size: 60, corners: D3_QUAD, color: INK } },
        { type: 'canvas', module: 'etch', noRewind: true, ...D3_CAM(0, 24), params: { text: "me I couldn't\nplace", sync: 'lyric', size: 60, corners: D3_QUAD, color: '#fbf8f1' } },
      ], fx: [{ type: 'letterbox', aspect: 2.39, amount: 1 }] },
  ],
};
