// Section D on its own (preview harness; files starting with "_" are ignored by render/timeline.js).
//   node render/engine/render.mjs --timeline render/timeline/_D_solo.js --range 112.96 141 --preview --encode
import D from './D.js';
export default {
  name: 'D_solo', audio: 'inputs/Rewind - cinematic edition (Remastered).mp3', range: [112.96, 141.0],
  background: '#000000', fx: [{ type: 'grain', amount: 0.035 }],
  shots: D.shots, overlays: D.overlays,
};
