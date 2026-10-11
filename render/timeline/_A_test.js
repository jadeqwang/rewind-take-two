// Sections A + B + R2 only (checks without the other directors' media):
//   node render/engine/render.mjs --timeline render/timeline/_A_test.js --stills 41.9 (C2 flashes of other sections show slates/black here)
import A from './A.js';
import R2 from './A_R2.js';
import B from './B.js';
export default (ctx) => {
  const shots = [], overlays = [];
  for (const f of [A, R2, B]) {
    const s = f(ctx);
    for (const sh of s.shots) shots.push({ ...sh, fx: [...(s.fx || []), ...(sh.fx || [])] });
    overlays.push(...(s.overlays || []));
  }
  shots.sort((a, b) => a.start - b.start);
  return { name: 'A_test', audio: 'inputs/Rewind - cinematic edition (Remastered).mp3', range: [0, 56.54], background: '#000000', shots, overlays };
};
