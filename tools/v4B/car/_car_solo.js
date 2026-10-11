// Solo preview of the 1:30 car shot alone (no C.js needed):
//   node render/engine/render.mjs --timeline tools/v4B/car/_car_solo.js --stills 89.3,90.4,91.2,92.7 --preview
import carShot from './car_shot.js';
export default () => ({ name: 'car_solo', audio: 'inputs/Rewind - cinematic edition (Remastered).mp3', range: [89.26, 92.79],
  background: '#000000', fx: [{ type: 'grain', amount: 0.035 }], shots: [carShot(89.26)], overlays: [] });
