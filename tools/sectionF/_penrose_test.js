// stills test for tools/sectionF/modules/penrose_march.js (not part of the film)
//   node render/engine/render.mjs --timeline tools/sectionF/_penrose_test.js --preview --stills 193.0,194.0,194.3
const BEATS = [192.34, 192.78, 193.22, 193.66, 194.10, 194.54, 194.98];
export default { name: 'F_penrose_test', range: [192.34, 195.42], background: '#f4ecd8', fx: [],
  shots: [{ id: 'F6b', start: 192.34, end: 195.42, background: '#f1e7cf',
    layers: [{ type: 'image', src: 'media/shots/F6b/kf_v3_F6b_plate_crop_dered.png', fit: 'cover' }, { type: 'canvas', module: 'tools/sectionF/modules/penrose_march.js', stage: 'pre',
      params: { cx: 960, cy: 468, width: 520, n: [7, 2, 2, 7], beats: BEATS, clunk: { at: 194.10, from: 27, dur: 0.2 } } }] }] };
