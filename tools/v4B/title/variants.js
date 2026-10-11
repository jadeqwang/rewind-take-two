// v4-B check timeline: the C3 title card with three settings of the name, one per second, to compare at 540p.
//   node render/engine/render.mjs --timeline tools/v4B/title/variants.js --preview --stills 2.5,5.5,8.5
const INK = '#0b0b0c', PAPER = '#ece7dc';
const base = { color: PAPER, size: 210, y: 470, arrive: { at: 0, every: 0 }, flip: { at: 0.55, dur: 0.45, stagger: 0.09 }, subtitle: 'jade wang' };
const V = [
  { subtitleSize: 92, subtitleDy: 126, subtitleTracking: 10, subtitleHalo: 0.85 },
  { subtitle: 'JADE WANG', subtitleSize: 62, subtitleDy: 118, subtitleTracking: 30, subtitleItalic: false, subtitleHalo: 0.85 },
  { subtitleSize: 92, subtitleDy: 126, subtitleTracking: 10, subtitleHalo: 0 },
];
export default {
  name: 'v4B_title', range: [0, 9], background: INK,
  shots: V.map((v, i) => ({ id: 'T' + i, start: i * 3, end: i * 3 + 3, background: INK,
    layers: [{ type: 'video', src: 'media/shots/C3/take_1_engraved.mp4', in: 0, rate: 1, fit: 'cover' },
      { type: 'canvas', module: 'title', stage: 'post', params: { ...base, ...v } }],
    fx: [{ type: 'letterbox', aspect: 2.39, amount: 1 }] })),
};
