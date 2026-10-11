// Section A only (for checking A.js without the other sections): node render/engine/render.mjs --timeline render/timeline/_A_test.js ...
import A from './A.js';
export default (ctx) => {
  const s = A(ctx);
  const shots = s.shots.map(sh => ({ ...sh, fx: [...(s.fx || []), ...(sh.fx || [])] }));
  return { name: 'A_test', audio: 'inputs/Rewind - cinematic edition (Remastered).mp3', range: [0, 40.65], background: '#000000', shots, overlays: s.overlays || [] };
};
