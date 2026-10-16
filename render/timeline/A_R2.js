// R2 (Drop 1, 42.65–48.42): thirteen "stop" chops = thirteen frozen past deaths (Section A world-building).
// Kept in its own file so the Drop 1 director can take it over (or delete it) without touching A.js.
// One engraved still per chop (media/shots/R2/engraved/), cut exactly on the chop onsets from timing.json, each with a
// small push so nothing is dead-still, a VHS scrub between hits and the iteration counter jumping backward.
const DIR = 'media/shots/R2/engraved/';
// v9: *_patch = the same still with the sleeve roundel re-lettered 1420 / MHz (tools/sectionE/patchfix.py)
const STILLS = ['01train', '02marinab', '03picasso_patch', '04bridge_patch', '05fountain', '06watertower', '07riverwalk_patch',
  '08skydeck', '09lightning', '10gearsb_patch', '11ferris', '12iceb_patch', '13sedanb'];
const ITER = [4093, 4091, 4092, 4089, 4090, 4088, 4086, 4087, 4085, 4084, 4082, 4083, 4081];   // randomized but decreasing; all below 4094 (4094-4098 have their own fates, docs/revisions/v5/counters.md)

export default ({ T }) => {
  const chops = T.lists.vocal_chops.map(c => (typeof c === 'number' ? c : c.start)).filter(t => t >= 42.6 && t < 48.5);
  const ends = [...chops.slice(1), 48.42];
  const shots = STILLS.map((s, k) => {
    const dir = k % 2 ? 1 : -1;
    return {
      id: `R2_${String(k + 1).padStart(2, '0')}`, start: chops[k], end: ends[k], background: '#0b0b0c',
      layers: [
        { type: 'image', src: `${DIR}kf_${s}_engraved.png`, fit: 'cover', keepColor: true,
          kenBurns: { from: { scale: 1.04, x: -8 * dir }, to: { scale: 1.08, x: 8 * dir }, ease: 'linear' } },
        { type: 'solid', stage: 'post', color: '#ece7dc', rect: [36, 40, 380, 54], opacity: 0.92 },
        { type: 'canvas', module: 'hud', stage: 'post', params: { mode: 'iteration', value: ITER[k], side: 'left', color: '#0b0b0c', size: 24 } },
      ],
      fx: [{ type: 'vhs', amount: [[0, 0.9], [0.09, 0, 'out']] }, { type: 'tracking', amount: [[0, 1], [0.12, 0, 'out']] },
        { type: 'punch', amount: 0.03, on: [chops[k]], decay: 0.15 }],
    };
  });
  return { section: 'A_R2', shots };
};
