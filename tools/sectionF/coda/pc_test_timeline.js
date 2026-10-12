// v5-build scratch timeline: the film's timeline (render/timeline.js) cut down to the coda (O4, the PC shots and the
// counter), so stills of the post-credits scene render without loading every section's media. Not part of the film.
//   node render/engine/render.mjs --timeline tools/sectionF/coda/pc_test_timeline.js --stills 240,243 --preview
import film from '../../../render/timeline.js';

export default async function pcTest(ctx) {
  const tl = await film(ctx);
  tl.shots = tl.shots.filter(s => /^(O4|PC)/.test(s.id));
  tl.overlays = tl.overlays.filter(o => /O_counter|O_credit/.test(o.id));
  tl.name = 'pc_test';
  tl.range = [Math.min(...tl.shots.map(s => s.start)), Math.max(...tl.shots.map(s => s.end))];
  return tl;
}
