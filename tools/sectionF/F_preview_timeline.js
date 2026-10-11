// Section F preview timeline: only media/shots/F_edl.json (so a broken section elsewhere cannot block a review render).
//   node render/engine/render.mjs --timeline tools/sectionF/F_preview_timeline.js --range 169.4 227.96 --preview --encode
import { edlToSection, mergeSections } from '../../render/engine/src/sections.js';

export default async function timeline(ctx) {
  const { T } = ctx;
  const edl = await ctx.readJSON('media/shots/F_edl.json');
  const sec = await edlToSection(edl, T, ctx, 'media/shots/F_edl.json');
  sec._src = 'F_edl';
  // borrow O1 (211.64-218.92, 3D, owned by section E) so the preview plays straight through
  try {
    const E = (await import('../../render/timeline/E.js')).default;
    const e = typeof E === 'function' ? await E({ T, core: ctx.core }) : E;
    const o1 = e.shots.find(s => s.id === 'O1');
    if (o1) sec.shots.push(o1);
  } catch (err) { /* E not available: the gap stays black */ }
  const { shots, overlays } = mergeSections([sec], T, { fill: false });
  return { name: 'F_preview', audio: 'inputs/Rewind - cinematic edition (Remastered).mp3', range: [169.4, 227.96],
    background: '#000000', fx: [], shots, overlays };
}
