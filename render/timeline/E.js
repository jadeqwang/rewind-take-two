// SECTION E: glitch break + verse 3 (141.00-169.40), plus the 3D outro card O1 (211.64-218.92).
// Director notes: docs/sections/E.md. 3D modules live in render/three/scenes (Escher engraving renderer, display-ready
// colour => linear: false). Every cut sits on a tracked beat from analysis/cinematic/timing.json.
//   G1 141.00 (81:1)  G2 144.54 (83:1, low boom)  G3 146.32 (84:1)  G4 148.08 (85:1, kick returns)
//   M1 151.62 (87:1)  V3S 153.98-159.14 (singing take, cutaway 90:2-90:3)  M2 159.14 (91:2)  M3 165.18 (94:4.4)
//   O1 211.64 (121:1) - 218.92 (125:1)
const PAPER = '#ECE7DC';
// sun: false everywhere - the ringed sun read as an unexplained target in rough cut v1
const three = (module, params = {}) => ({ id: '3d', type: 'three', module, params: { sun: false, ...params }, linear: false, samples: 1 });

// G1-G3: the matted anime clip sits over the drifting engraving lines on a blank page. Clips are filled in from
// media/shots/G*/chosen.json once approved (see E.md); until then the page shows the lines and a pending note.
const G_CLIPS = {
  // id: { src, matte, in, rate }  from media/shots/G*/chosen.json (G2 at 1.15x: pencil clears the bun at ~144.64,
  // the shot ends inside the hair fan; G3 at 1.4x fits the whole stroke into the shot)
  // v3 (2026-10-11, Jade 2:21 + the two-pencil canon): new takes with the two crossed pencils in the bun (G1), the
  // pale-blue-eraser rainbow pencil pulled while the pink-eraser one drifts away (G2), and a rainbow-cored stroke (G3).
  // *_patch = the same take with the sleeve roundel re-lettered `1420 / MHz` in every frame (tools/sectionE/patchfix.py).
  // v2 picks, kept beside them: G1 take_1_engraved (in 0), G2 take_4_engraved (in 0.46, rate 1.15, y 54, scale 0.95),
  // G3 take_4_engraved_soft + take_4_matte/matte_dilated6 (in 1.2, rate 1.4).
  G1: { src: 'media/shots/G1/take_3_engraved_patch.mp4', matte: 'media/shots/G1/take_3_matte/matte.mp4', in: 0.0, rate: 1.0 },
  G2: { src: 'media/shots/G2/take_5_engraved_patch.mp4', matte: 'media/shots/G2/take_5_matte/matte.mp4', in: 0.68, rate: 1.15 },  // boom 144.54 lands as the pencil comes free
  G3: { src: 'media/shots/G3/take_5_engraved_soft_patch.mp4', matte: 'media/shots/G3/take_5_matte/matte_dilated9.mp4', in: 1.3, rate: 1.6 },  // stroke starts ~1.3 s, ~85% drawn at the cut
};
function gShot(id, start, end, drift, note) {
  const c = G_CLIPS[id];
  const layers = [
    { id: 'paper', type: 'solid', color: PAPER },
    { id: 'lines', type: 'canvas', module: 'render/three/canvas/drift_lines.js', params: drift },
  ];
  if (c) layers.push({ id: 'jade', type: 'video', src: c.src, in: c.in ?? 0, rate: c.rate ?? 1, fit: 'cover', y: c.y ?? 0, scale: c.scale ?? 1,
    ...(c.matte ? { matte: { src: c.matte, mode: c.matteMode || 'luma' } } : { blend: 'multiply' }), keepColor: true });
  else layers.push({ id: 'pending', type: 'canvas', module: 'slate', opacity: 0.0, params: { title: id, note } });
  return { id, start, end, background: PAPER, layers, fx: [{ type: 'paper', amount: 0.5 }] };
}

// V3S (singing #3, made by the singing director: media/sing/NOTES.md). Lip lag B = -0.12 s; A/B/C = lips 0.15 s
// earlier / measured / 0.15 s later. clip_time = song_time - 153.68 + lag. Upscaled by the engine, NOT engraved.
// v3: the watercolor singer (media/sing/NOTES.md, "v3 watercolor"); sync is baked in: file time 0 = song 153.98.
// v2 (pencil trace): V3S_SRC 'media/sing/V3S/take_2_lips.mp4', V3S_T0 = 153.68, measured lag -0.12.
const V3S_VARIANT = 'B';
const V3S_T0 = 153.98;
const V3S_LAG = { A: 0.15, B: 0, C: -0.15 }[V3S_VARIANT];
// v4 (Jade: glossier hair, no smile; media/sing/NOTES.md, "v4"): same framing, scale and timing as v3. v3: 'media/sing/V3S/v3_sync_1080.mp4'
const V3S_SRC = 'media/sing/V3S/v4_sync_1080.mp4';
// v5 (Jade 2:35: "make that rooftop staircase an actual impossible staircase"): a Penrose stair on the near rooftop
// (lower left) in place of the square stairwell; the plate is baked into the take, so it is a still overlay over the take
// (she never comes near it; take, in-point and her matte unchanged). docs/revisions/v5/stairs.md. v4: no 'stairs' layer.
// v5 round 2 (Jade: copy the 3:13 clock stair): the F6b stair lifted off its plate (tools/v5/stairs2/comp.py).
// Round 1: 'media/sing/plates/stairs_v5/overlay_V3S.png'.
const V3S_STAIRS = 'media/sing/plates/stairs_v5/overlay_V3S_clock.png';
const v3s = (id, start, end) => ({ id, start, end, background: '#000000',
  layers: [{ id: 'sing', type: 'video', src: V3S_SRC, in: start - V3S_T0 + V3S_LAG, rate: 1, fit: 'cover', keepColor: true },
    { id: 'stairs', type: 'image', src: V3S_STAIRS, fit: 'cover', keepColor: true }] });

export default ({ T }) => ({
  section: 'E',
  overlays: [
    // V3-1 lyric over the whole singing slot (incl. the cutaway), Section A's lower-third style; paper ink with a soft
    // ink halo because the plate's lower third is her white jacket
    // v3: the line is in the world, as in S1 (render/timeline/A.js, A_S1_lyric): the same legend on the same arcs inside
    // the Bean's rim, but here the mirror shows the truth, so it is written in residue-orange coloured pencil instead of
    // cut in white line. One word per sung onset; behind her (her matte is laid back over it); not over the cutaway.
    { id: 'V3S_lyric', start: 153.98, end: 159.14, layers: (() => {
      const ARC = 'render/timeline/_arc_lyric.js', HER = { src: 'media/sing/V3S/v4_sync_1080_matte/', mode: 'luma' };
      const arc = (text, times, r, at) => ({ text, times, cx: 965, cy: 981, r, ...at, size: 88, style: 'pencil', color: '#F08A24' });
      const LEGEND = [arc('THE NIGHT', ['word:the@153', 'word:night@153'], 1014, { to: -31 }), arc('BEFORE', ['word:before@154'], 930, { to: -31 }),
        arc('MY', ['word:my@157'], 1014, { from: 31 }), arc('DISSERTATION', ['word:dissertation@157'], 930, { from: 31 }),
        arc('DEFENSE', ['word:defense@158'], 846, { from: 31 })];
      const cut = (start, end, legend) => [
        ...legend.map(params => ({ type: 'canvas', module: ARC, stage: 'pre', keepColor: true, start, end, params })),
        { type: 'video', stage: 'pre', keepColor: true, start, end, src: V3S_SRC, in: start + V3S_LAG, rate: 1, fit: 'cover', matte: HER },
      ];
      // no word in more than one shot (Jade, as in S1): V3S carries THE NIGHT BEFORE MY, V3S_b after the cutaway the rest
      return [...cut(0, 157.39 - 153.98, LEGEND.slice(0, 3)), ...cut(157.84 - 153.98, 159.14 - 153.98, LEGEND.slice(3))];
    })() },
  ],
  shots: [
    gShot('G1', '81:1', '83:1', { boom: 144.54, cx: 990, cy: 600 }, 'G1 float clip pending'),
    gShot('G2', '83:1', '84:1', { boom: 144.54, cx: 1000, cy: 540 }, 'G2 hero clip pending'),
    gShot('G3', '84:1', '85:1', { boom: 144.54, cx: 1480, cy: 520, bloomAt: 146.85, bloomX: 640, bloomY: 400 }, 'G3 stroke clip pending'),
    // G4: kick returns - snap to orthographic, 90 degree clunk, the Loop assembles on the music box
    { id: 'G4', start: '85:1', end: '87:1', background: PAPER, layers: [three('render/three/scenes/e_loop.js', { shot: 'G4' })],
      fx: [{ type: 'shake', on: [148.08], amp: 10, decay: 0.25 }] },
    // M1: push in to Jade on the L track, agents enter
    { id: 'M1', start: '87:1', end: 153.98, background: PAPER, layers: [three('render/three/scenes/e_loop.js', { shot: 'M1' })] },
    // V3S: the singing shot. A one-beat cutaway (90:2-90:3) to the diorama's truth covers a brief brow crease in the take
    v3s('V3S', 153.98, 157.39),                           // 157.39 = 90:2
    { id: 'V3S_cut', start: 157.39, end: 157.84, background: PAPER,
      layers: [three('render/three/scenes/penrose_loop.js', { pull: [8.2, 7.6], pullDur: 0.45, pullFrom: [12.9, 4.9, -3.4], color: 0 })] },
    v3s('V3S_b', 157.84, 159.14),                         // 157.84 = 90:3
    // M2: Mobius Lake Shore Drive (lyric painted on the road inside the module)
    { id: 'M2', start: 159.14, end: 165.18, background: PAPER, layers: [three('render/three/scenes/e_mobius.js')],
      fx: [{ type: 'shake', on: [162.30], amp: 10, decay: 0.22 }, { type: 'flash', at: [162.30], dur: 0.12, amount: 0.45, color: '#ffffff' },
        { type: 'punch', on: [162.30], amount: 0.04, decay: 0.25 }] },
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
