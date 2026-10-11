// Section C on its own (preview harness; files starting with "_" are ignored by render/timeline.js).
//   node render/engine/render.mjs --timeline render/timeline/_C_solo.js --range 56.54 112.96 --preview --encode
import C from './C.js';
export default (ctx) => {
  const c = C(ctx);
  return { name: 'C_solo', audio: 'inputs/Rewind - cinematic edition (Remastered).mp3', range: [56.54, 112.96],
    background: '#000000', fx: [{ type: 'grain', amount: 0.035 }], shots: c.shots, overlays: c.overlays };
};
