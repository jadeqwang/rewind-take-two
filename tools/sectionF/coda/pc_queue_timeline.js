// v5-coda2 scratch timeline (not part of the film): PC2_lobby with the camera held close on the queue and no text box,
// so the per-figure idle motion can be judged at 540p (docs/revisions/v5/coda2.md).
//   node render/engine/render.mjs --timeline tools/sectionF/coda/pc_queue_timeline.js --range 238.8 244.05 --preview --encode
import film from '../../../render/timeline.js';

export default async function pcQueue(ctx) {
  const tl = await film(ctx);
  tl.shots = tl.shots.filter(s => s.id === 'PC2_lobby').map(s => ({
    ...s, layers: s.layers.filter(l => l.module !== 'dialogue').map(l => ({
      ...l, params: { ...l.params, camScale: 2.3, camX: 985, camY: 730 } })) }));
  tl.overlays = [];
  tl.name = 'pc_queue';
  tl.range = [tl.shots[0].start, tl.shots[0].end];
  return tl;
}
