// SECTION E: glitch break + verse 3 (141.00-169.40), plus the 3D outro card O1 (211.64-218.92).
// Director notes: docs/sections/E.md. 3D modules live in render/three/scenes (Escher engraving renderer, display-ready
// colour => linear: false). Every cut sits on a tracked beat from analysis/cinematic/timing.json.
//   G1 141.00 (81:1)  G2 144.54 (83:1, low boom)  G3 146.32 (84:1)  G4 148.08 (85:1, kick returns)
//   M1 151.62 (87:1)  [V3S 153.98-159.14 belongs to the singing director]  M2 159.14 (91:2)  M3 165.18 (94:4.4)
//   O1 211.64 (121:1) - 218.92 (125:1)
const PAPER = '#ECE7DC';
const three = (module, params = {}) => ({ id: '3d', type: 'three', module, params, linear: false, samples: 1 });

// G1-G3: the matted anime clip sits over the drifting engraving lines on a blank page. Clips are filled in from
// media/shots/G*/chosen.json once approved (see E.md); until then the page shows the lines and a pending note.
const G_CLIPS = {
  // id: { src, matte, in, rate }   (set from chosen.json; keep null while pending)
  G1: null, G2: null, G3: null,
};
function gShot(id, start, end, drift, note) {
  const c = G_CLIPS[id];
  const layers = [
    { id: 'paper', type: 'solid', color: PAPER },
    { id: 'lines', type: 'canvas', module: 'render/three/canvas/drift_lines.js', params: drift },
  ];
  if (c) layers.push({ id: 'jade', type: 'video', src: c.src, in: c.in ?? 0, rate: c.rate ?? 1, fit: 'cover',
    ...(c.matte ? { matte: { src: c.matte, mode: c.matteMode || 'luma' } } : { blend: 'multiply' }), keepColor: true });
  else layers.push({ id: 'pending', type: 'canvas', module: 'slate', opacity: 0.0, params: { title: id, note } });
  return { id, start, end, background: PAPER, layers, fx: [{ type: 'paper', amount: 0.5 }] };
}

export default ({ T }) => ({
  section: 'E',
  shots: [
    gShot('G1', '81:1', '83:1', { boom: 144.54 }, 'G1 float clip pending'),
    gShot('G2', '83:1', '84:1', { boom: 144.54 }, 'G2 hero clip pending'),
    gShot('G3', '84:1', '85:1', { boom: 144.54, bloomAt: 146.62 }, 'G3 stroke clip pending'),
    // G4: kick returns - snap to orthographic, 90 degree clunk, the Loop assembles on the music box
    { id: 'G4', start: '85:1', end: '87:1', background: PAPER, layers: [three('render/three/scenes/e_loop.js', { shot: 'G4' })],
      fx: [{ type: 'shake', on: [148.08], amp: 10, decay: 0.25 }] },
    // M1: push in to Jade on the L track, agents enter
    { id: 'M1', start: '87:1', end: 153.98, background: PAPER, layers: [three('render/three/scenes/e_loop.js', { shot: 'M1' })] },
    // M2: Mobius Lake Shore Drive (lyric painted on the road inside the module)
    { id: 'M2', start: 159.14, end: 165.18, background: PAPER, layers: [three('render/three/scenes/e_mobius.js')],
      fx: [{ type: 'shake', on: [162.30], amp: 6, decay: 0.2 }] },
    // M3: routed onto the Penrose stairs; "it couldn't trace"
    { id: 'M3', start: 165.18, end: '97:1', background: PAPER, layers: [
      three('render/three/scenes/e_loop.js', { shot: 'M3' }),
      { id: 'lyric', type: 'canvas', module: 'render/three/canvas/trace_lyric.js', stage: 'post', params: { size: 62, y: 975 } },
    ], fx: [{ type: 'shake', on: [166.30 + 0.86], amp: 6, decay: 0.2 }] },
    // O1: Ascending and Descending forever, slow pull-back, the world in colour (variance report overlay: engine)
    { id: 'O1', start: '121:1', end: '125:1', background: PAPER,
      layers: [three('render/three/scenes/penrose_loop.js', { pull: [7.5, 25], pullDur: 7.28, color: 1 })] },
  ],
});
