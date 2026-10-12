// Thumbnail scratch timeline (docs/revisions/v5/thumbnail.md): section D's E7_04_chasm alone, with the residue
// ribbon layer of the D_E7_ribbons overlay dropped (its colour wash kept). Not part of the film.
import D from '../../render/timeline/D.js';
const shot = D.shots.find(s => s.id === 'E7_04_chasm');
const ov = D.overlays.filter(o => o.id === 'D_E7_ribbons').map(o => ({ ...o, layers: o.layers.filter(l => l.module !== 'ribbon') }));
export default {
  name: 'thumb_e7_noribbon', audio: 'inputs/Rewind - cinematic edition (Remastered).mp3',
  range: [136.62, 137.5], background: '#000000', fx: [{ type: 'grain', amount: 0.035 }],
  shots: [shot], overlays: ov,
};
