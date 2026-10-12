// v5 merge previz (Jade's 3:23 note; plan docs/revisions/v5/merge.md). Section F's EDL with F7_06 + F7_07 replaced by
// one shot, F7_07m 202.88-205.52 (tools/v5/merge/F7_07m.json, the same entry tools/sectionF/edl.py will load): BLUE and ORANGE reassemble into the one original Jade. Assets: tools/v5/merge/bake.py.
//   node render/engine/render.mjs --timeline tools/v5/merge/previz_timeline.js --range 200.24 207.28 --preview --encode --force
// Does not touch media/shots/F_edl.json or any render/timeline file.
import { edlToSection, mergeSections } from '../../../render/engine/src/sections.js';

export default async function timeline(ctx) {
  const { T } = ctx;
  const edl = await ctx.readJSON('media/shots/F_edl.json');
  edl.shots = edl.shots.filter(s => s.shot !== 'F7_06' && s.shot !== 'F7_07');
  const m = await ctx.readJSON('tools/v5/merge/F7_07m.json');
  delete m._doc;
  edl.shots.push(m);
  edl.shots.sort((a, b) => a.in - b.in);
  const sec = await edlToSection(edl, T, ctx, 'v5_merge_previz');
  sec._src = 'v5_merge_previz';
  const { shots, overlays } = mergeSections([sec], T, { fill: false });
  return { name: 'v5_merge_previz', audio: 'media/sfx/Rewind_cinematic_sfx_mix.mp3', range: [169.4, 211.64],
    background: '#000000', fx: [], shots, overlays };
}
