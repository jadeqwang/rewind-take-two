// Section A: cold open, intro, Verse 1, pre-drop (0.00–40.65), shots C1, C3, C4, S1 (placement), S2, D1–D8, P1–P4.
// Not here: C2 (rewind teaser 1.90–7.24, REUSE assembled from final shots), P5/P6 onward.
// S1 media is the singing director's (media/sing/, see media/sing/NOTES.md); LIP picks the A/B/C lip-sync variant.
// The 13 R2 death tableaux are stills in media/shots/R2/ (see R2_STILLS below); Drop 1's director places them.
// Media: media/shots/<ID>/ (chosen.json per shot); track keys: media/shots/<ID>/track_*.json (tools/sectionA/track_quad.py).
import tracks from './_A_tracks.js';

const S = (id, f) => `media/shots/${id}/${f}`;
const INK = '#0b0b0c', PAPER = '#ece7dc', ORANGE = '#F08A24';

// chosen takes (mirrors media/shots/<ID>/chosen.json)
const PLATE = {
  C1: { src: S('C1', 'take_1_engraved.mp4'), in: 0.0, rate: 1 },
  C3: { src: S('C3', 'take_1_engraved.mp4'), in: 0.0, rate: 1 },
  C4: { src: S('C4', 'take_2_engraved.mp4'), in: 0.0, rate: 1 },
  S2: { src: S('S2', 'take_1_lens.mp4'), in: 0.0, rate: 1 },
  D1: { src: S('D1', 'take_1_engraved.mp4'), in: 0.0, rate: 1 },
  D2: { src: S('D2', 'take_1_engraved.mp4'), in: 0.0, rate: 1 },
  D3: { src: S('D3', 'take_1_engraved.mp4'), in: 0.0, rate: 1 },
  D4: { src: S('D4', 'take_1_engraved.mp4'), in: 2.0, rate: 1 },
  D5: { src: S('D5', 'take_1_engraved.mp4'), in: 0.0, rate: 1 },
  D6: { src: S('D6', 'take_1_engraved.mp4'), in: 0.3, rate: 1 },
  D7: { src: S('D7', 'take_1_engraved.mp4'), in: 0.0, rate: 1 },
  D8: { src: S('D8', 'take_2_engraved.mp4'), in: 0.2, rate: 1 },
  P1: { src: S('P1', 'take_1_engraved.mp4'), in: 0.0, rate: 1 },
  P2: { src: S('P2', 'take_1_engraved.mp4'), in: 0.6, rate: 1 },
  P3: { src: S('P3', 'take_1_engraved.mp4'), in: 0.4, rate: 1 },
  P4: { src: S('P4', 'take_1_engraved.mp4'), in: 0.0, rate: 1 },
};
// S1 lip sync: clip_time = song_time - 12.90 + lag; B = measured lag 1.04 (A = lips 0.15 s earlier, C = 0.15 s later)
const LIP = 'B';
const S1_IN = 12.6 - 12.9 + 1.04 + { A: 0.15, B: 0, C: -0.15 }[LIP];   // clip time at song 12.60
const S1_SRC = 'media/sing/S1/take_1_lips.mp4';
// S2 push: into the Lake Shore Drive headlights at lower right of the Bean reflection (design px of the S1 frame)
const HEAD = [1600, 690], PUSH = 4.5;
const PUSH_KB = { from: { scale: 1, x: 0, y: 0 }, to: { scale: PUSH, x: -(HEAD[0] - 960) * PUSH, y: -(HEAD[1] - 540) * PUSH }, ease: 'inCubic' };
// keyframes: used instead of the takes while USE_STILLS is true (layout checks before the takes exist)
const USE_STILLS = false;
const KF = { C1: 'still_hero_engraved.png', C3: 'kf_sdr2.jpg', C4: 'kf_sdr1f.jpg', S2: 'kf_nbp1.jpg', D1: 'kf_sdr1.jpg', D2: 'kf_sdr1.jpg',
  D3: 'kf_sdr3.jpg', D4: 'kf_nbp1.png', D5: 'kf_sdr1.jpg', D6: 'kf_sdr1.jpg', D7: 'kf_nbp1.jpg', D8: 'kf_nbp1.jpg', P1: 'kf_sdr1.jpg',
  P2: 'kf_sdr1.jpg', P3: 'kf_sdr1.jpg', P4: 'kf_torso1.jpg' };
const MATTE = id => ({ src: PLATE[id].src.replace('_engraved.mp4', '_matte/'), mode: 'luma' });
const vid = (id, extra = {}) => {
  if (USE_STILLS) { const { matte, ...rest } = extra; return { id: `${id}_plate`, type: 'image', src: S(id, KF[id]), fit: 'cover', ...rest }; }
  return { id: `${id}_plate`, type: 'video', fit: 'cover', ...PLATE[id], ...extra };
};

export const R2_STILLS = ['01train', '02marinab', '03picasso', '04bridge', '05fountain', '06watertower', '07riverwalk',
  '08skydeck', '09lightning', '10gearsb', '11ferris', '12ice', '13sedanb'];

// D5: push in on the centre agent's sunglasses so the reflected lyric reads (face at ~(992, 215) → (960, 420))
const D5_KB = { from: { scale: 1, x: 0, y: 0 }, to: { scale: 2.2, x: -(992 - 960) * 2.2, y: 440 - 540 - (215 - 540) * 2.2 }, ease: 'inOutSine' };
// shrink a corner-pin track toward its centre (fx, fy = fraction of width/height kept)
const inset = (keys, fx, fy) => keys.map(([t, q]) => {
  const cx = (q[0] + q[2] + q[4] + q[6]) / 4, cy = (q[1] + q[3] + q[5] + q[7]) / 4;
  return [t, q.map((v, i) => (i % 2 ? cy + (v - cy) * fy : cx + (v - cx) * fx))];
});
const LETTERBOX = { type: 'letterbox', aspect: 2.39, amount: 1 };
const lower = (extra = {}) => ({ type: 'canvas', module: 'lowerthird', stage: 'post',
  params: { color: PAPER, size: 50, y: 1022, halo: 0, ...extra } });

export default ({ T }) => ({
  section: 'A',
  fx: [{ type: 'grain', amount: 0.035, seed: 'twos' }],
  shots: [
    // ---------------------------------------------------------------- cold open: the hook
    { id: 'C1', start: 0.0, end: 1.9, background: PAPER,
      layers: [
        vid('C1', { kenBurns: { from: { scale: 1.0 }, to: { scale: 1.05 }, ease: 'linear' } }),
        { type: 'solid', stage: 'post', color: PAPER, rect: [36, 40, 352, 54], opacity: 0.92, fadeIn: 0.25, start: 0.4 },
        { type: 'canvas', module: 'hud', stage: 'post', fadeIn: 0.25, start: 0.4,
          params: { mode: 'iteration', value: 4096, side: 'left', color: INK, size: 24 } },
      ] },
    // ---------------------------------------------------------------- intro: title over the lake
    { id: 'C3', start: 7.24, end: 10.82, background: INK,
      layers: [
        vid('C3'),
        { type: 'canvas', module: 'title', stage: 'post',
          params: { color: PAPER, size: 210, y: 470, arrive: { at: 0, every: 0 }, flip: { at: 0.55, dur: 0.45, stagger: 0.09 }, subtitle: 'jade wang', subtitleSize: 38 } },
      ], fx: [LETTERBOX] },
    { id: 'C4', start: 10.82, end: 12.6, background: INK,
      layers: [
        vid('C4'),
        { type: 'canvas', module: 'pencil', params: { text: 'DEFENSE\n9AM', at: 0.15, cps: 16, size: 46, corners: tracks.C4_note, color: '#26241f', point: false, grain: 0.25 } },
      ], fx: [LETTERBOX] },
    // ---------------------------------------------------------------- verse 1: the cutscene
    { id: 'S1', start: 12.6, end: 19.64, background: INK,
      layers: [
        { id: 'S1_take', type: 'video', src: S1_SRC, in: S1_IN, rate: 1, fit: 'cover' },
        { type: 'canvas', module: 'lowerthird', stage: 'post', params: { color: INK, size: 54, y: 1010, halo: 1 } },
      ] },
    { id: 'S2', start: 19.64, end: 21.38, background: INK,
      layers: [
        { id: 'S2_her', type: 'video', src: S1_SRC, in: S1_IN + 7.04, rate: 1, freeze: 0.24, fit: 'cover', kenBurns: PUSH_KB },
        // through the mirror: the engraved road from above, bent by the convex lens and relaxing flat
        { ...vid('S2'), start: 1.0, fadeIn: 0.45 },
      ] },
    { id: 'D1', start: 21.38, end: 23.16, background: INK,
      layers: [
        vid('D1'),
        { type: 'canvas', module: 'pin', params: { style: 'sign', text: "LAKE SHORE DR\nI'm speeding down Lake Shore", corners: tracks.D1_signL } },
        { type: 'canvas', module: 'pin', params: { style: 'sign', text: 'SOUTH', corners: tracks.D1_signR } },
        lower({ text: 'I dreamt', sync: 'lyric', italic: true, y: 860, color: PAPER }),
      ], fx: [LETTERBOX] },
    { id: 'D2', start: 23.16, end: 24.9, background: INK,
      layers: [
        vid('D2'),
        { type: 'canvas', module: 'pin', params: { style: 'plain', text: 'HILBERT', font: 'sign', color: INK, corners: tracks.D2_top } },
        { type: 'canvas', module: 'pin', params: { style: 'plain', text: 'VACANCY', font: 'sign', color: INK, corners: tracks.D2_bot } },
        { ...vid('D2', { matte: { src: S('D2', 'take_1_matte_left/'), mode: 'luma' }, keepColor: true }), id: 'D2_jade' },   // Jade over the sign text (it passes behind her head)
        lower({ text: 'a shadow', sync: 'lyric' }),
      ], fx: [LETTERBOX] },
    { id: 'D3', start: 24.9, end: 28.4, background: INK,
      layers: [
        vid('D3'),
        { type: 'canvas', module: 'etch', blend: 'screen', params: { text: "chasing me I couldn't place", sync: 'lyric', size: 40, corners: tracks.D3_etch } },
      ], fx: [LETTERBOX] },
    { id: 'D4', start: 28.4, end: 30.16, background: INK,
      layers: [vid('D4'), lower({ text: 'I pulled over, and', sync: 'lyric' })], fx: [LETTERBOX] },
    { id: 'D5', start: 30.16, end: 31.92, background: INK,
      layers: [
        vid('D5', { kenBurns: D5_KB }),
        { type: 'canvas', module: 'pin', blend: 'screen', kenBurns: D5_KB, params: { style: 'plain', font: 'sign', text: 'men in shades', sync: 'lyric', color: '#ffffff', corners: inset(tracks.D5_lensL, 0.8, 0.75) } },
        { type: 'canvas', module: 'pin', blend: 'screen', kenBurns: D5_KB, params: { style: 'plain', font: 'sign', text: 'and suits', sync: 'lyric', color: '#ffffff', corners: inset(tracks.D5_lensR, 0.8, 0.75) } },
      ], fx: [LETTERBOX] },
    { id: 'D6', start: 31.92, end: 33.66, background: INK,
      layers: [vid('D6')], fx: [LETTERBOX] },
    { id: 'D7', start: 33.66, end: 36.3, background: INK,
      layers: [
        vid('D7'),
        { type: 'canvas', module: 'pin', keepColor: true, params: { style: 'plain', text: 'DOCTORAL CANDIDATE\nJADE WANG', font: 'mono', color: '#1d2b3a', corners: tracks.D7_card } },
      ], fx: [LETTERBOX] },
    { id: 'D8', start: 36.3, end: 37.96, background: INK,
      layers: [vid('D8')], fx: [LETTERBOX] },
    // ---------------------------------------------------------------- pre-drop: game over
    { id: 'P1', start: 37.96, end: 38.9, background: INK, layers: [vid('P1')], fx: [LETTERBOX] },
    { id: 'P2', start: 38.9, end: 39.68, background: INK,
      layers: [vid('P2', { kenBurns: { from: { scale: 1.08 }, to: { scale: 1.16 } } })], fx: [LETTERBOX] },
    { id: 'P3', start: 39.68, end: 40.24, background: INK,
      layers: [vid('P3')], fx: [LETTERBOX, { type: 'shake', amp: 3, freq: 9 }] },
    { id: 'P4', start: 40.24, end: 40.65, background: INK,
      layers: [
        { id: 'P4_flash', type: 'image', src: S('P4', 'kf_flash1.png'), fit: 'cover', end: 0.125 },
        { ...vid('P4'), start: 0.125 },
        { type: 'canvas', module: 'motes', keepColor: true, params: { at: 40.37, x: 640, y: 620, count: 140 } },
        { type: 'canvas', module: 'whisper', stage: 'post', params: { text: 'shot', sync: 'lyric', x: 1560, y: 980 } },
      ], fx: [{ type: 'flash', at: 0, dur: 0.12, amount: 0.6, color: PAPER }, { type: 'shake', amp: 8, freq: 14, decay: 0.3 }] },
  ],
  overlays: [
    { id: 'A_dialogue', start: 33.6, end: 37.96, layers: [
      { type: 'canvas', module: 'dialogue', stage: 'post', params: { rect: [150, 800, 1620, 200], size: 46, speaker: 'JADE' } }] },
    { id: 'A_predrop_lyric', start: 37.96, end: 40.24, layers: [lower({ text: 'With no warning I get', sync: 'lyric' })] },
  ],
});
