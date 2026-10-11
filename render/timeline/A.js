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
  C1: { src: S('C1', 'take_3_engraved.mp4'), in: 0.0, rate: 1 },   // v3: no bullet, a muzzle flare at the centre pistol; two pencils
  C3: { src: S('C3', 'take_1_engraved.mp4'), in: 0.0, rate: 1 },
  C4: { src: S('C4', 'take_4_engraved.mp4'), in: 0.0, rate: 1 },   // v3: two crossed pencils; near (right) sleeve has no roundel
  S2: { src: S('S2', 'take_1_lens.mp4'), in: 0.0, rate: 1 },
  D1: { src: S('D1', 'take_1_engraved.mp4'), in: 0.0, rate: 1 },
  D2: { src: S('D2', 'take_2_engraved.mp4'), in: 0.0, rate: 1 },   // v3: the bulb billboard big in the window (lyric surface)
  D3: { src: S('D3', 'take_2_engraved.mp4'), in: 0.0, rate: 1 },   // v3: two straight pencils crossed through the bun
  D4: { src: S('D4', 'take_2_engraved.mp4'), in: 0.9, rate: 1 },   // v3: both cars on the right shoulder, the black sedan behind the Acura
  D5cu: { src: S('D5', 'take_2_engraved.mp4'), in: 0.0, rate: 1 },   // v3: close-up of the shades (lyric in the lenses)
  D5: { src: S('D5', 'take_3_engraved.mp4'), in: 0.3, rate: 1 },   // v3: the three men on the same lakefront shoulder as D4
  D6: { src: S('D6', 'take_2_engraved.mp4'), in: 0.4, rate: 1 },   // v3: starts one beat later (32.36). Restaged: from the passenger seat, agents at HER window (same view direction as D8); two pencils
  D7: { src: S('D7', 'take_2_engraved.mp4') },   // v3: the agent's view through her window; played backward (D7_SRC)
  D8: { src: S('D8', 'take_3_engraved.mp4'), in: 1.18, rate: 1.25 },   // v3: reverse angle, only the BACK of her card; needle slams on "do" (36.92)
  P1: { src: S('P1', 'take_2_engraved.mp4'), in: 0.3, rate: 1 },   // take_2 = A_P1b (lakefront)
  P2: { src: S('P2', 'take_2_engraved.mp4'), in: 0.3, rate: 1 },   // v3: the v2 keyframe with the two-pencil bun
  P3: { src: S('P3', 'take_1_engraved.mp4'), in: 0.4, rate: 1 },
  P4: { src: S('P4', 'take_1_engraved.mp4'), in: 0.0, rate: 1 },
};
// S1, v3: the watercolor singer (media/sing/NOTES.md, "v3 watercolor"). The lip sync is baked into the file: file
// time 0 = song 12.60, rate 1. LIP nudges it (A = lips 0.15 s earlier, C = 0.15 s later).
// v2 (pencil trace): S1_SRC 'media/sing/S1/take_1_lips.mp4', S1_IN = 12.6 - 12.9 + 1.04, S2_her on take_1_lips_wide.mp4, push from 1.3
const LIP = 'B';
const S1_IN = 0 + { A: 0.15, B: 0, C: -0.15 }[LIP];   // clip time at song 12.60
const S1_SRC = 'media/sing/S1/v3_sync_1080.mp4';
// slow push over the three singing cuts (1.0 -> 1.08 keeps the band, dot and 1420 MHz roundel in frame)
const S1_PUSH = (a, b) => ({ from: { scale: a }, to: { scale: b }, ease: 'linear' });
// v2's S2 push from her face into the Lake Shore Drive headlights (unused since v3; kept for switching back)
const HEAD = [1600, 690], PUSH = 4.5;
const PUSH_KB = { from: { scale: 1.08, x: 0, y: 0 }, to: { scale: PUSH, x: -(HEAD[0] - 960) * PUSH, y: -(HEAD[1] - 540) * PUSH }, ease: 'inCubic' };
// keyframes: used instead of the takes while USE_STILLS is true (layout checks before the takes exist)
const USE_STILLS = false;
const KF = { C1: 'still_hero_engraved.png', C3: 'kf_sdr2.jpg', C4: 'kf_sdr1f.jpg', S2: 'kf_nbp1.jpg', D1: 'kf_sdr1.jpg', D2: 'kf_sdr1.jpg',
  D3: 'kf_sdr3.jpg', D4: 'kf_nbp1.png', D5: 'kf_sdr1.jpg', D5cu: 'kf_v3_cu.jpg', D6: 'kf_v3_2.jpg', D7: 'kf_v3_2.jpg', D8: 'kf_v3_2.jpg', P1: 'kf_sdr1.jpg',
  P2: 'kf_v3_1.jpg', P3: 'kf_sdr1.jpg', P4: 'kf_torso1.jpg' };
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
const C4_PUSH = { scale: [[0, 1], [0.55, 1, 'inOutCubic'], [1.45, 2.6]], x: [[0, 0], [0.55, 0, 'inOutCubic'], [1.45, -(1326 - 960) * 2.6]],
  y: [[0, 0], [0.55, 0, 'inOutCubic'], [1.45, -(850 - 540) * 2.6]] };
// D7 (v3): source time of take_2 over the shot's 2.64 s, backward: hand in the jacket (3.1) → card held up (0.0)
const D7_SRC = [[0, 3.1, 'inOutSine'], [2.1, 0.3, 'out'], [2.64, 0.0]];
// v3 in-world lyrics: lettering cut into the woodblock (lenses) / bulb-sign letters (rooftop billboard)
const WOODCUT = 'tools/sectionA/modules/woodcut.js';
// D2: the plate sits 90 px lower so the billboard's top panel clears the letterbox bar
const D2_DOWN = { y: 90 };
// D5cu: he is still walking: a small bob on every step (one step per beat, 0.44 s) on top of the take's own motion
const D5_BOB = { scale: 1.04, y: (lt) => -11 * Math.abs(Math.sin(Math.PI * lt / 0.44)) + 6, x: (lt) => 5 * Math.sin(Math.PI * lt / 0.88) };
// D3: two etched lines in the mirror's dark sky, left of the streetlight (the tracked strip, narrowed, deepened, moved left)
const D3_QUAD = inset(tracks.D3_etch, 0.62, 2.3).map(([t, q]) => [t, q.map((v, i) => v + (i % 2 ? 40 : -185))]);
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
        { type: 'solid', stage: 'post', color: PAPER, rect: [36, 40, 380, 54], opacity: 0.92, fadeIn: 0.25, start: 0.4 },
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
        // hold on her, then push 2.6x onto the sticky note (centre ~(1326, 850)) so DEFENSE 9AM reads: the stakes of the hook
        vid('C4', C4_PUSH),
        { type: 'canvas', module: 'pencil', noRewind: true, ...C4_PUSH, params: { text: 'DEFENSE\n9AM', at: 0.75, cps: 14, size: 46, corners: tracks.C4_note, color: '#1a1815', point: false, grain: 0.2 } },
      ], fx: [LETTERBOX] },
    // ---------------------------------------------------------------- verse 1: the cutscene
    { id: 'S1', start: 12.6, end: 16.14, background: INK,
      layers: [{ id: 'S1_take', type: 'video', src: S1_SRC, in: S1_IN, rate: 1, fit: 'cover', kenBurns: S1_PUSH(1.0, 1.04) }] },
    // cutaway (bar 10): the Bean's reflection of Lake Shore Drive, headlights streaming (engraved Seedance take)
    // v3 (Jade): every word of V1-1 is sung by 17.43 and she only holds the note after, so no return to her: the
    // reflection holds two bars and the road follows on "I'm speeding down" (v2: S1x to 17.88, S1b 17.88-19.64 on her,
    // S2 pushing from her face into the headlights)
    { id: 'S1x', start: 16.14, end: 19.64, background: INK,
      layers: [{ id: 'S1x_plate', type: 'video', src: S('S1x', 'take_1_engraved.mp4'), in: 0.2, rate: 1, fit: 'cover', scale: 1.04 }] },
    { id: 'S2', start: 19.64, end: 21.38, background: INK,
      // the reflection becomes the world: the engraved road from above, bent by the convex lens and relaxing flat
      layers: [vid('S2')] },
    { id: 'D1', start: 21.38, end: 23.16, background: INK,
      layers: [
        vid('D1'),
        { type: 'canvas', module: 'pin', noRewind: true, params: { style: 'sign', text: "LAKE SHORE DR\nI'm speeding down Lake Shore", corners: tracks.D1_signL } },
        { type: 'canvas', module: 'pin', noRewind: true, params: { style: 'sign', text: 'SOUTH', corners: tracks.D1_signR } },
        lower({ text: 'I dreamt', sync: 'lyric' }),
      ], fx: [LETTERBOX] },
    // v3: the rooftop bulb billboard IS the lyric (it read HILBERT / VACANCY in v2). Each panel is dark until its word
    // is sung, then flickers on like a lamp. One beat longer (to 25.34) so "chasing" (24.78) can be read.
    { id: 'D2', start: 23.16, end: 25.34, background: INK,
      layers: [
        vid('D2', D2_DOWN),
        { type: 'canvas', module: WOODCUT, noRewind: true, ...D2_DOWN, params: { text: 'A SHADOW', sync: 'lyric', reveal: 'bulb', unlit: 0.82, color: INK, flecks: 0, hatch: 0.3, box: [380, 152], pad: 16, corners: tracks.D2_top } },
        { type: 'canvas', module: WOODCUT, noRewind: true, ...D2_DOWN, params: { text: 'CHASING', sync: 'lyric', reveal: 'bulb', unlit: 0.82, color: INK, flecks: 0, hatch: 0.3, box: [388, 186], pad: 18, corners: tracks.D2_bot } },
      ], fx: [LETTERBOX] },
    { id: 'D3', start: 25.34, end: 28.4, background: INK,
      layers: [
        vid('D3'),
        // etch across the top of the mirror glass (dark sky): an ink shadow under paper-white glyphs. The billboard
        // carried "a shadow chasing", the mirror finishes the line.
        { type: 'canvas', module: 'etch', noRewind: true, x: 3, y: 27, opacity: 0.85, params: { text: "me I couldn't\nplace", sync: 'lyric', size: 60, corners: D3_QUAD, color: INK } },
        { type: 'canvas', module: 'etch', noRewind: true, y: 24, params: { text: "me I couldn't\nplace", sync: 'lyric', size: 60, corners: D3_QUAD, color: '#fbf8f1' } },
      ], fx: [LETTERBOX] },
    // v3 restage: three beats on the shoulder, two on the men, four on the shades (cuts on beats 29.74, 30.60, 32.36)
    { id: 'D4', start: 28.4, end: 29.74, background: INK,
      layers: [vid('D4'),
        // v3 (Jade): she stays in colour in the driver's seat. The engrave matte missed her (small, behind the windshield),
        // so the raw take is laid back inside a static soft window round her (she doesn't move: centroid within 3 px)
        { id: 'D4_jade', type: 'video', src: S('D4', 'take_2.mp4'), in: 0.9, rate: 1, fit: 'cover', keepColor: true, grade: { saturation: 1.35 },
          matte: { src: S('D4', 'v3_colour_mask.mp4'), mode: 'luma' } },
        lower({ text: 'I pulled over,', sync: 'lyric' })], fx: [LETTERBOX] },
    { id: 'D5', start: 29.74, end: 30.6, background: INK,
      layers: [vid('D5', { kenBurns: { from: { scale: 1.0, y: 40 }, to: { scale: 1.12, y: 110 }, ease: 'linear' } })], fx: [LETTERBOX] },
    // the shades fill the frame; "men in shades" / "and suits" are cut into the lenses, white line on black, word-timed
    { id: 'D5cu', start: 30.6, end: 32.36, background: INK,
      layers: [
        vid('D5cu', D5_BOB),
        { type: 'canvas', module: WOODCUT, noRewind: true, blend: 'screen', ...D5_BOB, params: { text: 'MEN IN\nSHADES', times: [0, 0.21, 0.28], box: [560, 400], corners: tracks.D5_cuL } },
        { type: 'canvas', module: WOODCUT, noRewind: true, blend: 'screen', ...D5_BOB, params: { text: 'AND\nSUITS', times: [0.96, 1.15], box: [560, 400], corners: tracks.D5_cuR } },
      ], fx: [LETTERBOX] },
    { id: 'D6', start: 32.36, end: 33.66, background: INK,
      layers: [vid('D6')], fx: [LETTERBOX] },
    { id: 'D7', start: 33.66, end: 36.3, background: INK,
      layers: [
        // The take is "she puts the card away", played backward: she reaches into her jacket ("I reach for my ID"),
        // draws the card out and holds it up to the window ("to show them"), landing on the keyframe. The card's
        // photo and redaction bars are drawn into the plate: no engine text on it.
        vid('D7', { srcTime: D7_SRC }),
      ], fx: [LETTERBOX] },
    { id: 'D8', start: 36.3, end: 37.96, background: INK,
      layers: [
        vid('D8'),
        // residue shimmering off the card as the needle slams (card centre ~(680, 500) in this plate); `at` is shot-local
        { type: 'canvas', module: 'motes', keepColor: true, params: { at: 0.48, x: 680, y: 440, count: 60, speed: 700, drag: 2.0, gravity: -110, size: 10, life: 1.3, ring: false, shape: 'square', spread: 0.3, angle: -90 } },
      ], fx: [LETTERBOX] },
    // ---------------------------------------------------------------- pre-drop: game over
    { id: 'P1', start: 37.96, end: 38.9, background: INK, layers: [vid('P1')], fx: [LETTERBOX] },
    { id: 'P2', start: 38.9, end: 39.68, background: INK,
      // v3: framed lower with a gentler push, so the two crossed pencils (erasers at the plate's top edge) stay inside
      // the letterbox; the plate's own top edge stays behind the bar
      layers: [vid('P2', { kenBurns: { from: { scale: 1.02, y: 130 }, to: { scale: 1.07, y: 148 } } })], fx: [LETTERBOX] },
    // v3 (Jade, 0:39): the gun pointed into the car put her head above the roof line, so no gun shot: back to the
    // agent, his hand at the holster inside his jacket, pushing in on it, then the hit (P4). v2: P3 take_1, in 0.4.
    { id: 'P1b', start: 39.68, end: 40.24, background: INK,
      layers: [vid('P1', { in: 0.3 + (39.68 - 37.96), kenBurns: { from: { scale: 1.3, x: -280, y: -40 }, to: { scale: 1.6, x: -560, y: -60 }, ease: 'in' } })],
      fx: [LETTERBOX] },
    { id: 'P4', start: 40.24, end: 40.65, background: INK,
      layers: [
        // v3 (Jade, 0:39: "just cut to the colorful pixel burst"): no gun-flash still (v2: kf_flash1.png for 3 frames);
        // the torso's first frame held under the shot's white hit flash instead, so P4's clip timing and P5 don't move
        { ...vid('P4'), id: 'P4_hold', end: 0.125, freeze: 0 },
        { ...vid('P4'), start: 0.125 },
        { type: 'canvas', module: 'motes', keepColor: true, params: { at: 0.13, x: 640, y: 620, count: 140 } },   // shot-local: the hit at 40.37 (B.js P5 continues this burst)
        { type: 'canvas', module: 'whisper', stage: 'post', params: { text: 'shot', sync: 'lyric', x: 1640, y: 990, color: PAPER } },
      ], fx: [{ type: 'flash', at: 0, dur: 0.12, amount: 0.6, color: PAPER }, { type: 'shake', amp: 8, freq: 14, decay: 0.3 }] },
  ],
  overlays: [
    // v3: V1-1 lives in the world, not in a lower third, and no word is shown in more than one shot (Jade). S1: "THE
    // NIGHT BEFORE" cut into the Bean's mirror on arcs just inside its rim (white-line woodcut capitals,
    // render/timeline/_arc_lyric.js), one word per sung onset, behind her (her matte is laid back over it). S1x: "MY
    // DISSERTATION DEFENSE," on the plaza paving of the reflection. Layer times are local to 12.60: S1 0-3.54, S1x 3.54-7.04.
    { id: 'A_S1_lyric', start: 12.6, end: 19.64, layers: (() => {
      const ARC = 'render/timeline/_arc_lyric.js', HER = { src: 'media/sing/S1/v3_sync_1080_matte/', mode: 'luma' };
      const arc = (text, times, r, at) => ({ text, times, cx: 965, cy: 981, r, ...at, size: 88, style: 'woodcut' });
      const LEFT = [arc('THE NIGHT', ['word:the@13', 'word:night@13'], 1014, { to: -31 }), arc('BEFORE', ['word:before@13'], 930, { to: -31 })];
      // S1x: the plate drifts left about 38 px/s; the quad rides it (plate px before the layer's 1.04 scale)
      const PLAZA = (dx, dy) => [172 + dx, 640 + dy, 690 + dx, 626 + dy, 662 + dx, 960 + dy, 140 + dx, 986 + dy];
      return [
        ...LEFT.map(params => ({ type: 'canvas', module: ARC, stage: 'pre', noRewind: true, start: 0, end: 3.54, kenBurns: S1_PUSH(1.0, 1.04), params })),
        { type: 'video', stage: 'pre', noRewind: true, start: 0, end: 3.54, src: S1_SRC, in: S1_IN, rate: 1, fit: 'cover', kenBurns: S1_PUSH(1.0, 1.04), matte: HER },
        { type: 'canvas', module: 'pin', stage: 'pre', noRewind: true, start: 3.54, end: 7.04, scale: 1.04, blend: 'multiply',
          params: { style: 'ground', font: 'slab', uppercase: true, text: 'MY\nDISSERTATION\nDEFENSE,', times: ['word:my@16', 'word:dissertation@16', 'word:defense@17'],
            size: 92, color: INK, grain: 0.3, corners: [[0, PLAZA(8, -2)], [3.5, PLAZA(-125, 22)]] } },
      ];
    })() },
    { id: 'A_dialogue', start: 33.6, end: 37.96, layers: [
      // v3: a compact box at lower left, mostly in the letterbox bar, so it never covers the card or a hand in D7/D8
      { type: 'canvas', module: 'dialogue', stage: 'post', params: { rect: [80, 856, 960, 132], size: 46, speaker: 'JADE' } }] },
    { id: 'A_predrop_lyric', start: 37.96, end: 40.24, layers: [lower({ text: 'With no warning I get', sync: 'lyric' })] },
  ],
});
