// Section B: engine-only shots that reuse earlier footage.
//   C2  1.90–7.24   cold-open rewind teaser: flashes of LATER shots played backward, cut on the sound designer's
//                   accelerating clock ticks (media/sfx/stems/03_rewind_ticks.wav, cue `rewind_ticks` in cues.json)
//   P5  40.65–41.40 freeze + woodblock-negative inversion with a tape-slowdown wobble (Jade + motes stay in colour)
//   P6  41.40–42.38 pause menu over the frozen negative (overlay); cursor RESUME → REWIND, selection blinks on "st-"
//   R1  42.38–42.65 impact: white flash, the negative shatters back to positive
//   R3  48.42–52.48 "Rewind." #1: Verse 1 (D8 → D1) backward under a caustic ripple, half-time judder
//   R4  52.48–56.54 "Rewind." #2: back past S2, S1 and C4, decelerating onto Lake Shore Drive (C3) for V2a at 56.54
// R2 (the 13 death tableaux, 42.65–48.42) lives in A_R2.js.
const INK = '#0b0b0c', PAPER = '#ece7dc', ORANGE = '#F08A24', BLUE = '#8DB8E8';

// ------------------------------------------------------------------------------------------------ C2 flash list
// Tick onsets of the rewind_ticks stem (8ths → 16ths 3.68 → 32nds 5.48 → 64ths 6.36). Cuts land on every tick while a
// tick is ≥ 2 frames (8ths, 16ths), on every 2nd 32nd and every 3rd 64th, so the last flashes are 2 frames each.
const TICKS = [1.9, 2.12, 2.34, 2.57, 2.8, 3.02, 3.24, 3.46, 3.68, 3.795, 3.91, 4.025, 4.14, 4.25, 4.36, 4.47, 4.58,
  4.69, 4.8, 4.91, 5.02, 5.135, 5.25, 5.365, 5.48, 5.535, 5.59, 5.645, 5.7, 5.755, 5.81, 5.865, 5.92, 5.975, 6.03,
  6.085, 6.14, 6.195, 6.25, 6.305, 6.36, 6.388, 6.415, 6.443, 6.47, 6.498, 6.525, 6.553, 6.58, 6.608, 6.635, 6.662,
  6.69, 6.718, 6.745, 6.773, 6.8, 6.828, 6.855, 6.883, 6.91, 6.938, 6.965, 6.993, 7.02, 7.047, 7.075, 7.102, 7.13,
  7.158, 7.185, 7.213];
const CUT_IDX = [0, ...[2, 3, 4, 5, 6, 7], ...Array.from({ length: 16 }, (_, k) => 8 + k),
  ...Array.from({ length: 8 }, (_, k) => 24 + 2 * k), ...Array.from({ length: 10 }, (_, k) => 40 + 3 * k)];
// SOURCE TIMES (song seconds), one per cut, in cut order. Swap any entry when a better shot lands; each flash plays
// backward from its source time at the current ◀◀ speed. Pass 1 (8ths): the six hero images; pass 2 (16ths): sections
// F → E; pass 3 (32nds): Verse 2 + the deaths; pass 4 (64ths): Section A backward, landing on C3 at 7.24.
export const C2_SOURCES = [
  1.88,                                                        // C1 itself starts going backward
  160.5, 140.4, 132.6, 118.6, 108.8, 84.2,                     // Möbius diorama, ANOMALY terminal, Banach–Tarski twins, ghost ring, ring of agents, bridge jump
  164.0, 152.5, 150.5, 144.0, 141.6, 138.5, 136.0, 133.5,      // M2, M1 diorama, G4, white page, filings, meter, ribbons, split
  130.0, 126.0, 124.0, 117.5, 116.0, 114.0, 106.5, 103.0,      // slip, replay, replay, ring, field, tracks, too fast, field
  101.5, 95.0, 88.0, 80.5, 72.8, 67.0, 60.0, 47.0,             // field, ghost race, back on the road, sedans, bridge, kaizo road, hands, a death
  40.5, 39.9, 37.0, 35.0, 31.5, 27.0, 24.0, 22.2, 16.0, 11.5,  // P4 burst, gun, D8, ID, shades, mirror, HILBERT, gantry, S1, C4
];
// Rule (rough cut v1): nothing after 146.32 except the engraved M diorama (150–166) may appear here: the world turning
// to colour at 169.40 is the film's reveal. 
const C2_SPEED = [[1.9, 1.5], [2.34, 2], [3.68, 4], [5.48, 8], [6.36, 16]];   // ◀◀ ×N by song time
const CUTS = CUT_IDX.map((i, k) => [TICKS[i], C2_SOURCES[k]]);
const speedAt = t => C2_SPEED.filter(s => s[0] <= t + 1e-6).pop()[1];
const c2Src = (lt) => {
  const t = 1.9 + lt; let c = CUTS[0];
  for (const x of CUTS) if (x[0] <= t + 1e-6) c = x;
  return c[1] - (t - c[0]) * speedAt(t);
};
// residue ribbons whipping backward (right → left) across the frame, one per speed step
const whip = (t0, dur, y0, y1, seed) => ({ type: 'canvas', module: 'ribbon', keepColor: true, start: t0 - 1.9, end: t0 - 1.9 + dur + 0.25,
  params: { path: [[0, 2150, y0], [dur * 0.5, 960, (y0 + y1) / 2 - 90], [dur, -250, y1]], trail: 0.35, width: 34, twist: 0.7, motes: 0.5, seed } });

// ------------------------------------------------------------------------------------------------ P5 / R1 frozen frame
// P4's last state (A.js): P4 take from clip 0.285 at 40.65, motes burst at 40.37. tapeStop(at 0, dur .35) halts the
// content clock at 0.175 s; R1 maps its clock to the same instant so both shots show the identical frozen frame.
const P4_SRC = 'media/shots/P4/take_1_engraved.mp4', P4_MATTE = { src: 'media/shots/P4/take_1_matte/', mode: 'luma' };
const frozen = (lift) => [
  // the world is lifted toward paper before the negative flips it, so the negative reads as white lines on ink
  { id: 'p4', type: 'video', src: P4_SRC, in: 0.285, fit: 'cover', grade: { lift } },
  { id: 'p4_jade', type: 'video', src: P4_SRC, in: 0.285, fit: 'cover', matte: P4_MATTE, keepColor: true },
  { id: 'p4_motes', type: 'canvas', module: './_B_motes_hold.js', keepColor: false, params: { at: -0.28, x: 640, y: 620, count: 140, life: 9 } },
];

export default ({ T }) => ({
  section: 'B',
  fx: [{ type: 'grain', amount: 0.035, seed: 'twos' }],
  shots: [
    // ---------------------------------------------------------------------------------------------- C2 teaser
    { id: 'C2', start: 1.9, end: 7.24, background: INK,
      layers: [
        { id: 'C2_comp', type: 'comp', source: 'film', srcTime: (lt) => c2Src(lt) },
        whip(2.34, 0.6, 300, 760, 1), whip(3.68, 0.4, 820, 240, 2), whip(4.6, 0.3, 520, 600, 3), whip(5.48, 0.25, 200, 900, 4), whip(6.36, 0.2, 700, 380, 5),
        { type: 'solid', stage: 'post', color: PAPER, rect: [36, 40, 380, 54], opacity: 0.92 },
        { type: 'canvas', module: 'hud', stage: 'post',
          params: { mode: 'iteration', value: [[0, 4096], [4.85, 4096, 'inOutCubic'], [5.2, 4097]], snap: false, side: 'left', color: INK, size: 24 } },
        { type: 'solid', stage: 'post', color: PAPER, rect: [36, 104, 300, 92], opacity: 0.92 },
        { type: 'canvas', module: 'hud', stage: 'post',
          params: { mode: 'rewind', x: 40, y: 172, color: INK, accent: ORANGE, multiplier: [[0, 2, 'hold'], [1.78, 4, 'hold'], [3.58, 8, 'hold'], [4.46, 16, 'hold']] } },
      ],
      fx: [{ type: 'rewind', amount: [[0, 0.35], [5.0, 0.9]] }, { type: 'chroma', amount: [[0, 1], [5, 4]] },
        { type: 'punch', amount: 0.025, on: CUTS.map(c => c[0]), decay: 0.08 }] },

    // ---------------------------------------------------------------------------------------------- P5 freeze → negative
    { id: 'P5', start: 40.65, end: 41.4, background: INK,
      layers: frozen([[0, '#000000'], [0.17, '#6a6a6a']]),
      time: (lt) => { const u = Math.min(lt / 0.35, 1); return 0.35 * (u - u * u / 2); },
      fx: [{ type: 'negative', amount: [[0, 0], [0.3, 1, 'inOut']] },
        { type: 'warble', amount: [[0, 1], [0.45, 0.15]] }] },
    // P6 menu lives in the overlay below; the shot holds the negative frame
    { id: 'P6', start: 41.4, end: 42.38, background: INK, time: [[0, 0.175], [1, 0.175]],
      layers: frozen('#6a6a6a'), fx: [{ type: 'negative', amount: 1 }, { type: 'warble', amount: 0.12 }] },
    // ---------------------------------------------------------------------------------------------- R1 impact
    { id: 'R1', start: 42.38, end: 42.65, background: INK, time: [[0, 0.175], [1, 0.175]],
      layers: [...frozen('#000000'),
        { type: 'canvas', module: 'motes', params: { at: 0, x: 960, y: 540, count: 70, colors: [PAPER, INK], shape: 'diamond', size: 18, speed: 2600, ring: true, life: 0.5 } }],
      fx: [{ type: 'flash', at: [0], dur: 0.1, amount: 1, color: PAPER }, { type: 'negative', amount: [[0, 1], [0.18, 0, 'outCubic']] },
        { type: 'shake', amp: 26, freq: 18, decay: 0.25 }, { type: 'punch', amount: 0.08, on: [42.38], decay: 0.2 }] },

    // ---------------------------------------------------------------------------------------------- R3 Braid rewind
    { id: 'R3', start: 48.42, end: 52.48, background: INK,
      layers: [
        // D8 → D1 backward (37.94 → 21.40 in 4.06 s ≈ ×4), held on twos-of-twos for the half-time judder (12 fps)
        { id: 'R3_comp', type: 'comp', source: 'film', echo: { n: 2, dt: 0.1, alpha: 0.28 },
          srcTime: (lt) => 37.94 - (Math.floor(lt * 12) / 12) * (16.54 / 4.06) },
        // her residue ribbon un-spools: the layer clock runs backward, so the trail retracts toward where it started
        { type: 'canvas', module: 'ribbon', keepColor: true, time: [[0, 4.06], [4.06, 0]],
          params: { path: [[0, -200, 760], [1.2, 520, 640], [2.4, 1100, 820], [3.4, 1560, 560], [4.06, 2150, 620]], width: 40, twist: 0.5, motes: 0.6, pencil: true, seed: 7 } },
        { type: 'canvas', module: 'hud', stage: 'post',
          params: { mode: 'rewind', x: 40, y: 120, ring: true, rate: 0.6, ringRadius: 420, color: PAPER, accent: ORANGE, multiplier: [[0, 2, 'hold'], [1.0, 4, 'hold'], [2.2, 8, 'hold']] } },
        { type: 'canvas', module: 'title', stage: 'post',
          params: { color: PAPER, size: 300, y: 640, arrive: { at: 0.16, every: 0.13 }, flip: { at: 1.6, dur: 0.5, stagger: 0.1 } } },
      ],
      fx: [{ type: 'ripple', amount: 0.7, speed: 5 }, { type: 'rewind', amount: 0.55 }, { type: 'grade', tint: '#dcebff', saturation: 0.9, contrast: 1.05 },
        { type: 'flash', at: [0], dur: 0.08, amount: 0.7, color: BLUE }, { type: 'vignette', amount: 0.35 }] },
    // ---------------------------------------------------------------------------------------------- R4 rewind lands
    { id: 'R4', start: 52.48, end: 56.54, background: INK,
      layers: [
        // S2 → S1 → C4 → C3, decelerating; stops on C3 (7.30) at 55.3, then a slow push onto the tiny white car on LSD
        { id: 'R4_comp', type: 'comp', source: 'film', echo: { n: 1, dt: 0.12, alpha: [[0, 0.3], [2.6, 0]] },
          srcTime: [[0, 21.36, 'outCubic'], [3.3, 7.3, 'hold'], [4.06, 7.3]],
          kenBurns: { from: { scale: 1, x: 0, y: 0 }, to: { scale: 2.6, x: -(560 - 960) * 2.6, y: -(860 - 540) * 2.6 }, ease: 'inCubic' } },
        { type: 'canvas', module: 'hud', stage: 'post', end: 2.8,
          params: { mode: 'rewind', x: 40, y: 120, ring: true, rate: 0.4, ringRadius: 420, color: PAPER, accent: ORANGE, multiplier: [[0, 8, 'hold'], [1.2, 4, 'hold'], [2.0, 2, 'hold']] } },
        { type: 'canvas', module: 'title', stage: 'post', end: 3.2, fadeOut: 0.5,
          params: { color: PAPER, size: 150, y: 600, mirrored: false, arrive: { at: 0.02, every: 0.08 } } },
      ],
      fx: [{ type: 'ripple', amount: [[0, 0.6], [3.0, 0, 'outCubic']], speed: 4 }, { type: 'rewind', amount: [[0, 0.5], [2.8, 0]] },
        { type: 'grade', tint: '#dcebff', saturation: 0.9 }, { type: 'letterbox', aspect: 2.39, amount: [[0, 1], [3.3, 1, 'inOutCubic'], [4.0, 0]] }] },
  ],
  overlays: [
    { id: 'P6_menu', start: 41.4, end: 42.38, layers: [
      { type: 'solid', stage: 'post', color: INK, rect: [640, 290, 640, 500], opacity: 0.9 },
      { type: 'canvas', module: 'hud', stage: 'post',
        params: { mode: 'pause', color: '#8a857c', accent: PAPER, dim: 0.2, cursor: [[0, 0, 'hold'], [0.22, 0, 'outCubic'], [0.32, 1, 'hold']], blinkAt: 0.66 } }] },
    { id: 'P5_whisper', start: 40.95, end: 42.38, layers: [
      { type: 'canvas', module: 'whisper', stage: 'post', params: { text: '…and time stops', times: [0.09, 0.37, 1.11], x: 1380, y: 1050, size: 40, color: PAPER } }] },
  ],
});
