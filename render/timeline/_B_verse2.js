// Section B (rev-B, v3 restage): the on-foot chase at the end of Verse 2, 94.06–112.96. Used by C.js, which spreads
// `shots` and `overlays` into section C (rev-A owns everything in C.js before 94.06). Plan: docs/revisions/B_research.md.
// One level, always left to right: L platform → beam → chasm (the shadow falls short, she dashes) → lawn by the Hilbert
// (they shoot where she was) → hotel corner (one of them spawns) → the hit → CONTINUE?.
// Takes: media/shots/B_<take>/take_1_engraved.mp4 (+ take_1_matte, or take_1_jmatte = Jade only, made by
// tools/sections/B/jmatte.py where the engrave matte also caught agents or the notice board).
// All plate coordinates below were read off the takes with a design-px grid (1920×1080).
import { dash, traceMiss } from './_B_fx.js';

const S = 'media/shots/';
const PAPER = '#ece7dc', INK = '#0b0b0c', ORANGE = '#F08A24';
const F = 1 / 24, E = F / 4;
const plate = k => `${S}B_${k}/take_1_engraved.mp4`;
const matteSrc = (k, j = '') => `${S}B_${k}/take_1_${j}matte/matte.mp4`;
const matte = (k, j = '') => ({ src: matteSrc(k, j), mode: 'luma' });
const beatPunch = { type: 'punch', amount: 0.018, on: 'beat' };
const snapF = t => Math.ceil(t * 24 - 1e-6) / 24;      // first frame at or after t

// in-world lettering (module pin), Anton capitals in ink; word-timed with the 2-frame ink bleed
const pin = (corners, text, extra = {}) => ({ type: 'canvas', module: 'pin',
  params: { style: 'plain', font: 'slab', color: INK, uppercase: true, padding: 4, corners, text, ...extra } });
// a sub-quad of a trapezoid whose top and bottom edges are horizontal (constant depth, so linear along them)
const subQuad = ([x0, y0, x1, y1, x2, y2, x3, y3], u0, u1) => {
  const top = u => [x0 + (x1 - x0) * u, y0 + (y1 - y0) * u], bot = u => [x3 + (x2 - x3) * u, y3 + (y2 - y3) * u];
  return [...top(u0), ...top(u1), ...bot(u1), ...bot(u0)];
};

// HILBERT on the hotel's rooftop billboard: rev-A's woodcut lettering (as on their 0:24 sign, render/timeline/A.js D2),
// steady (a name, not a lyric: `at` before the shot, so it is cut solid from the first frame). `face`: paint the lit
// panel first where the plate drew it hatched dark.
const WOODCUT = 'tools/sectionA/modules/woodcut.js';
const BB = { lawn: [1621, 107, 1811, 27, 1812, 100, 1621, 167], chasm: [1626, 106, 1818, 22, 1820, 96, 1627, 161] };
const hilbert = (corners, face = false) => [
  ...(face ? [{ id: 'bb_face', type: 'canvas', module: 'render/timeline/_B_quad.js', params: { corners, color: '#efe7da' } }] : []),
  { id: 'hilbert', type: 'canvas', module: WOODCUT, params: { text: 'HILBERT', at: -1, color: INK, flecks: 0, hatch: 0.15, box: [420, 140], pad: 8, corners } }];

export default function verse2B({ T }) {
  const shots = [];

  // ---- 94.06–95.42 platform. She sprints left to right, agents flood in behind; her graphite shadow (her own clip,
  // a quarter second ahead in time) runs half a body ahead. "A SHADOW" / "CHASING ME" on the two blank sign boards.
  {
    const v = { src: plate('plat'), in: 0.0, rate: 1, fit: 'cover' };
    shots.push({ id: 'B2_plat', start: 94.06, end: 95.42, background: INK, fx: [beatPunch], layers: [
      { id: 'plate', type: 'video', ...v },
      { id: 'ghost', type: 'ghosts', ...v, matte: matteSrc('plat'), loop: false, graphite: true, instances: [{ offset: 0.3, opacity: 0.62 }] },
      { id: 'jade', type: 'video', ...v, matte: matte('plat'), keepColor: true },
      // sign interiors: (600..1033, 298..383) and (1103..1538, 298..383); caps fill ~312..370
      { id: 'sign_l', ...pin([640, 287, 994, 287, 994, 391, 640, 391], 'A shadow', { times: ['94.06', '94.58'] }) },
      // "me" is sung at 96.05, after this shot: it lands two frames after "chasing" so the sign is whole before the cut
      { id: 'sign_r', ...pin([1106, 287, 1535, 287, 1535, 391, 1106, 391], 'chasing me', { times: ['95.30', '95.38'] }) },
    ] });
  }

  // ---- 95.42–96.30 platform to beam: cut on the airborne pose (source 0.30), land, run on. Shadow still ahead.
  {
    const v = { src: plate('leap'), in: 0.30, rate: 1.3, fit: 'cover' };
    shots.push({ id: 'B2_leap', start: 95.42, end: 96.30, background: INK, fx: [beatPunch], layers: [
      { id: 'plate', type: 'video', ...v },
      { id: 'ghost', type: 'ghosts', ...v, matte: matteSrc('leap'), loop: false, graphite: true, instances: [{ offset: 0.22, opacity: 0.62 }] },
      { id: 'jade', type: 'video', ...v, matte: matte('leap'), keepColor: true },
    ] });
  }

  // ---- 96.30–98.28 the chasm, one shot on one plate (chasm_dash take 1 and its retake chasm_dash_b share the keyframe,
  // so the world is the same). Her graphite shadow (chasm_short) runs ahead: it jumps (src 1.8), arcs, hits the far
  // wall, slides down its face (src ~4.1) and bursts into graphite motes on the 97.18 downbeat. She (chasm_dash_b)
  // jumps right after (src 1.3 at 97.16), peaks and drops, arms up, feet below the lip (src 2.0): she is not going to
  // make it. The dash fires on "race" (97.83): 2-frame freeze, dark frame, white ring, three pale-blue afterimages
  // laid flat across the gap, and she is on the wall top in take 1's dive pose (src 2.75), skids in at 1.4x: landing
  // disc and dust at 98.16, skid into the cut. (Retake b alone falls out of frame and returns as a rainbow streak.)
  {
    const st = 96.30, atL = snapF(97.83) - st, jumpL = 0.86;
    const A = { src: plate('chasm_dash_b'), matte: matte('chasm_dash_b'), in: 0.3, fit: 'cover',
      rate: [[0, (1.3 - 0.3) / jumpL, 'hold'], [jumpL, (2.0 - 1.3) / (atL - jumpL), 'hold'], [atL, 9.6, 'hold'], [atL + F, 4.8, 'hold'], [atL + 2 * F, 0]] };   // after the freeze: src 2.4–2.6, she has fallen out of frame (later the take brings her back as a streak)
    const bOn = atL + 3 * F - E, landL = bOn + (2.92 - 2.75) / 1.4;      // content clock
    const bTime = [[0, 2.75, 'hold'], [bOn, 2.75], [landL, 2.92], [2.0, 3.0]];
    const B = { src: plate('chasm_dash'), srcTime: bTime, fit: 'cover' };
    const d = dash({ clip: A, at: st + atL, land: st + landL, shotStart: st, afterimages: 0, line: false,
      feet: { layer: 'jadeB', point: 'bottom', smooth: 1, offset: [0, 15] } });
    const burst = 97.18 - st, from = [971, 451], to = [1362, 598];
    const after = [0, 1, 2].map(k => ({ id: `after${k}`, type: 'ghosts', src: A.src, matte: A.matte, fit: 'cover', loop: false,
      x: (to[0] - from[0]) * k / 3, y: (to[1] - from[1]) * k / 3,
      opacity: [[0, 0, 'hold'], [atL + (k < 2 ? 1 : 2) * F - E, 1], [atL + (k < 2 ? 1 : 2) * F - E + 14 * F, 0]],
      instances: [{ freeze: 2.0, opacity: 0.6, color: '#8DB8E8', tint: 1, grade: { contrast: 0.55 } }] }));
    shots.push({ id: 'B2_chasm', start: st, end: 98.28, background: INK, fx: [beatPunch, ...d.fx], layers: [
      { id: 'plate', type: 'video', ...A, matte: undefined },
      { id: 'plateB', type: 'video', ...B, opacity: [[0, 0, 'hold'], [bOn, 1]] },
      ...hilbert(BB.chasm, true),
      { id: 'shadow', type: 'ghosts', src: plate('chasm_short'), matte: matteSrc('chasm_short'), fit: 'cover', loop: false, graphite: true,
        srcTime: [[0, 1.5], [0.3, 2.15], [0.7, 3.7], [burst, 4.12], [1.5, 4.4]],
        opacity: [[0, 1, 'hold'], [burst + F - E, 0.45, 'hold'], [burst + 2 * F - E, 0]], instances: [{ opacity: 0.62 }] },
      { id: 'shadow_motes', type: 'canvas', module: 'render/timeline/_B_motes_hold.js', params: { at: burst, x: 1140, y: 700, count: 96, shape: 'square',
        colors: ['#8f8a82', '#d8d3ca', '#5e5b57'], speed: 650, drag: 3.0, gravity: 520, size: 17, life: 1.3, glow: 0.3 } },
      ...after,
      ...d.under,
      { id: 'jade', type: 'video', ...A, keepColor: true, opacity: [[0, 1, 'hold'], [atL + F / 2, 0]] },
      { id: 'jadeB', type: 'video', ...B, matte: matte('chasm_dash'), keepColor: true, opacity: [[0, 0, 'hold'], [bOn, 1]] },
      ...d.over,
    ] });
  }

  // ---- 98.28–100.70 the lawn, wide. She cuts on every beat (source 1.8x: turns at src 0.55/1.33/2.25/3.1/3.85 land on
  // 98.42/98.85/99.36/99.84/100.25). Each beat one agent fires: trace line, starburst, turf where she was, a scar that
  // stays. Orange residue ribbon behind her. "I ZIGZAG" painted flat on the lawn ("zag" = the second z in the vocal
  // stem, 98.78). Muzzle tips read off the plate (agents 2/3/4 from the front): (495,235) (660,292) (920,352).
  {
    const st = 98.28, v = { src: plate('lawn'), in: 0.30, rate: 1.8, fit: 'cover' };
    // ground plane: vanishing point on the horizon under the lettering's centre (1300, 470), so both ends lean the
    // same small amount; a shallow band y 700 (far) .. 830 (near), right of the agents' feet: letters painted flat on
    // grass seen from ~20° up are foreshortened to about a third of their height, so the band is ~8:1 on screen
    const G = [993, 700, 1671, 700, 1880, 830, 820, 830], split = 0.565;
    const shotsAt = [[98.94, [920, 352], 1.25], [99.38, [660, 292], 1.1], [99.82, [925, 355], 1.0], [100.26, [500, 238], 0.9]];
    const misses = shotsAt.map(([t, o, z], k) => traceMiss({ id: `miss${k}`, origin: o, times: [t], shotStart: st, size: z }));
    shots.push({ id: 'B2_lawn', start: st, end: 100.70, background: INK, fx: [beatPunch], layers: [
      { id: 'plate', type: 'video', ...v },
      ...hilbert(BB.lawn),
      { id: 'zig', ...pin(subQuad(G, 0, split), 'I zig', { style: 'ground', times: ['98.28', '98.47'], padding: 0, grain: 0.2 }), blend: 'multiply' },
      { id: 'zag', ...pin(subQuad(G, split, 1), 'zag', { style: 'ground', times: ['98.78'], padding: 0, grain: 0.2 }), blend: 'multiply' },
      ...misses.flatMap(m => m.under),
      { type: 'canvas', module: 'ribbon', keepColor: true,
        params: { follow: { layer: 'jade', point: 'centroid', smooth: 3 }, trail: 2.4, width: 40, drift: [0, 0], seed: 3 } },
      { id: 'jade', type: 'video', ...v, matte: matte('lawn', 'j'), keepColor: true },
      ...misses.flatMap(m => m.over),
    ] });
  }

  // ---- 100.70–102.46 the lawn, closer: past the notice board ("ACROSS THE / FIELD OF GRASS", word-timed) and out
  // right. Source 0.35 → 1.5 at 1.3x (to the board, the hard cut in front of it); then a jump cut on the 101.58 beat
  // past the take's cut-back (src 1.5–2.6 runs back left, toward the agents) to src 2.72, legs under the board, and on
  // at 1.05x: she comes out right of the board and is gone by ~102.25, leaving the board, the hole and the lyric.
  // Miss 1 (101.14) punches a hole in the board where she just was; miss 2 (102.00) hits the turf behind her.
  {
    const st = 100.70, jc = 101.58 - st;
    const v = { src: plate('lawn2'), srcTime: [[0, 0.35], [jc - E, 0.35 + (jc - E) * 1.3, 'hold'], [jc, 2.72], [1.76, 3.64]], fit: 'cover' };
    const board = [1290, 398, 1774, 398, 1774, 660, 1290, 660], hole = [1287, 598];
    const m1 = traceMiss({ id: 'missB', origin: [414, 512], times: [101.14], shotStart: st, targets: [hole], scar: 0, size: 0.8 });
    const m2 = traceMiss({ id: 'missT', origin: [414, 512], times: [102.00], shotStart: st, targets: [[1185, 960]], size: 0.85 });
    shots.push({ id: 'B2_lawn2', start: st, end: 102.46, background: INK, fx: [beatPunch], layers: [
      { id: 'plate', type: 'video', ...v },
      ...hilbert(BB.lawn),
      { id: 'board', ...pin(board, 'across the\nfield of grass', { sync: 'lyric', padding: 14, panel: '#f6e8d8', border: '#f6e8d8' }) },
      { id: 'hole', type: 'canvas', module: 'render/timeline/_B_hole.js', params: { at: 101.14 - st, x: hole[0], y: hole[1], r: 13 } },
      ...m1.under, ...m2.under,
      { id: 'jade', type: 'video', ...v, matte: matte('lawn2', 'j'), keepColor: true },
      ...m1.over, ...m2.over,
    ] });
  }

  // ---- 102.46–104.22 the firing line: the lead agent, two fingers to his earpiece, speaks; she is tiny, far right.
  // ("grass", sung 102.39–103.74, lands on the board two frames before the cut: it is held here as a lower third)
  shots.push({ id: 'B2_ear', start: 102.46, end: 104.22, background: INK, fx: [beatPunch], layers: [
    { id: 'plate', type: 'video', src: plate('ear'), in: 0.2, rate: 1, fit: 'cover' }, ...hilbert(BB.lawn)] });

  // ---- 104.22–105.98 side-scroll to the hotel (take skip_b: the agents start far back and gain on her). The plate
  // (world, agents) runs on a smooth ease-in clock, src 0.6 → 4.6 (about 1x at the cut-in, 4.5x by the cut), so the
  // pack closes continuously from far back to a few strides behind her; Jade, through her matte, runs at 1x. Under
  // the plate, copies a little earlier and later (their own Jade cut out) fill the hole where the plate's own Jade was.
  {
    const st = 104.22, en = 105.98, in0 = 0.6, rate = 1;
    const D = en - st, world = off => lt => in0 + (4.6 - in0) * Math.min(1, Math.max(0, lt / D)) ** 2 + off;
    const v = { src: plate('skip_b'), fit: 'cover' };
    const cut = { ...matte('skip_b', 'd'), mode: 'lumaInv' };   // her matte grown ~8 px (take_1_dmatte): no edge ghosts
    shots.push({ id: 'B2_skip', start: st, end: en, background: '#d6d0c5', fx: [beatPunch], layers: [
      // hole fill: the same plate a little earlier / later, each with its own Jade cut out
      // (offsets chosen off her stride period, so the fills do not all cut out the same leg)
      ...[0.61, -0.53, 0.37, -0.29, 0.17, -0.11].map((o, k) => ({ id: `fill${k}`, type: 'video', ...v, srcTime: world(o), matte: cut })),
      { id: 'world', type: 'video', ...v, srcTime: world(0), matte: cut },   // no frameBlend: the cut matte is per frame
      { id: 'jade', type: 'video', ...v, in: in0, rate, matte: matte('skip_b'), keepColor: true },
    ] });
  }

  // ---- 105.98–107.28 along the hotel front: she runs with her head turned back (source 0.35–1.8); nobody behind.
  shots.push({ id: 'B2_glance', start: 105.98, end: 107.28, background: INK, fx: [beatPunch], layers: [
    { id: 'plate', type: 'video', src: plate('glance'), in: 0.35, rate: 1.1, fit: 'cover' }] });

  // ---- 107.28–108.67 round the corner (take round_corner_b, high three-quarter view, camera locked; same keyframe as
  // round_corner, so the B_roundcornerclean patch still fits). She runs along the front wall; the agent waits around
  // the corner, where we can see him and she can't. He is not there at first (feathered patch of the engraved clean
  // still); on the 107.72 downbeat he flickers in over three frames (on, off, on) and stays, while she is still
  // approaching. She swings round the corner and runs smack into his chest on the 108.16 beat (src 1.25). His pistol
  // stays low at his hip for the whole take.
  {
    const st = 107.28, a = snapF(107.72) - st, bump = 108.16 - st;
    const v = { src: plate('round_corner_b'), fit: 'cover' };
    const k1 = [[0, 0.2], [bump, 1.25], [1.39, 1.25 + (1.39 - bump) * 1.3]];
    shots.push({ id: 'B2_corner', start: st, end: 108.67, background: INK, fx: [beatPunch, { type: 'shake', amp: 14, freq: 16, decay: 0.25, on: [108.16] }], layers: [
      { id: 'plate', type: 'video', ...v, srcTime: k1 },
      { id: 'clean', type: 'image', src: `${S}B_roundcornerclean/patch_agent.png`, fit: 'cover',
        opacity: [[0, 1, 'hold'], [a - E, 0, 'hold'], [a + F - E, 1, 'hold'], [a + 2 * F - E, 0, 'hold']] },
    ] });
    // ---- 108.67–109.92 "With no warning": punch in on the same take (1.35x toward the two of them): she bounces off
    // him, arms flying (src 2.4, ~108.98), staggers back (src 3.4, ~109.56) and catches herself on the wall (src 4.0,
    // ~109.87) while he stands his ground. No trace line.
    const s0 = k1[2][1];
    shots.push({ id: 'B2_corner_in', start: 108.67, end: 109.92, background: INK, fx: [{ type: 'punch', amount: 0.025, on: 'downbeat' }], layers: [
      { id: 'plate', type: 'video', ...v, srcTime: [[0, s0], [0.6, 2.85], [1.25, 4.1]], scale: 1.35, x: -30, y: -140 }] });
  }

  // ---- 109.92–110.78 low angle: the pistol rises, barrel at or below her waist (source 1.1–2.09).
  shots.push({ id: 'B2_pistol', start: 109.92, end: 110.78, background: INK, fx: [beatPunch], layers: [
    { id: 'plate', type: 'video', src: plate('pistol'), in: 1.1, rate: 1.15, fit: 'cover' }] });

  // ---- 110.78–111.22 the hit (side view, motes from her jacket) with the flash.
  shots.push({ id: 'B2_shot', start: 110.78, end: 111.22, background: INK,
    fx: [beatPunch, { type: 'flash', at: [0.04], dur: 0.05, amount: 0.45 }], layers: [
      { id: 'plate', type: 'video', src: plate('shot'), in: 0.0, rate: 1, fit: 'cover' }] });

  // ---- 111.22–112.66 CONTINUE?: freeze on the last frame of the hit, invert (P5 grammar), arcade countdown
  // (was C_V2n_continue on V2m1; re-pointed to B_shot so the frozen picture matches)
  shots.push({ id: 'C_V2n_continue', start: 111.22, end: 112.66, background: PAPER, layers: [
    { type: 'video', src: plate('shot'), in: 0.44, rate: 1, freeze: 0, fit: 'cover', x: [[0, 0], [0.3, 330, 'outCubic']] },
    { type: 'video', src: plate('shot'), in: 0.44, rate: 1, freeze: 0, fit: 'cover', x: [[0, 0], [0.3, 330, 'outCubic']], matte: matte('shot'), keepColor: true },
    { type: 'solid', color: PAPER, rect: [0, 0, 780, 1080], opacity: [[0, 0], [0.3, 0.92]] },  // inverts to ink under `negative`
  ], fx: [{ type: 'negative', amount: [[0, 0], [0.3, 1, 'outCubic']] }, { type: 'wobble', amount: [[0, 0.6], [0.4, 0]] }] });

  // ---- 112.66–112.96 the ◀◀ button slam (unchanged v2 V2n1 row)
  shots.push({ id: 'B2_V2n1', start: 112.66, end: 112.96, background: INK, fx: [beatPunch], layers: [
    { id: 'V2n1_t1', type: 'video', src: `${S}V2n1/take_1_engraved.mp4`, in: 1.78, rate: 1, fit: 'cover' }] });

  const ov = (id, start, end, layer) => ({ id, start, end, layers: [layer] });
  const overlays = [
    // HUD (v2's), moved to the top LEFT from the chasm cut (96.30) on, where the hotel billboard (HILBERT) is top right:
    // the race readout slides over with its chip; the platformer readout gets the same ink chip so it reads over the plates
    { id: 'C_race_chip', start: 94.06, end: 98.28, layers: [{ type: 'solid', color: INK, rect: [1300, 36, 600, 112], opacity: 0.95, x: [[0, 0, 'hold'], [2.24, -1280]] }] },
    ov('C_hud_race', 94.06, 98.28, { type: 'canvas', module: 'hud', x: [[0, 0, 'hold'], [2.24, -1280]], params: { mode: 'race', side: 'right', iteration: 4096,
      split: [[0, 0.42], [1.8, 0.12], [2.6, -0.04], [4.2, -0.31]], color: PAPER, splitColor: [[0, PAPER, 'hold'], [2.55, '#5fd16a']] } }),
    { id: 'C_field_chip', start: 98.28, end: 110.78, layers: [{ type: 'solid', color: INK, rect: [20, 36, 470, 170], opacity: 0.95 }] },
    ov('C_hud_field', 98.28, 110.78, { type: 'canvas', module: 'hud', params: { mode: 'platformer', side: 'left', color: PAPER, iteration: 4097, deaths: 4097, timer: { from: '56.54' } } }),
    ov('C_hud_continue', 111.30, 112.66, { type: 'canvas', module: 'hud', x: -560, params: { mode: 'continue', from: 9, every: 0.8, start: '111.40', press: 'PRESS ◀◀' } }),
    // lyrics not on a surface ("A shadow chasing me" is on the station signs, "I zigzag across the field of grass" on the lawn and the board)
    ov('C_lyr_race', 96.30, 98.28, { type: 'canvas', module: 'lowerthird', params: { text: 'like it’s a race', sync: 'lyric', color: INK, halo: 0.9, size: 74 } }),
    ov('C_lyr_grass', 102.46, 104.17, { type: 'canvas', module: 'lowerthird', params: { text: 'grass', times: ['102.39'], color: INK, halo: 0.9, size: 74, hold: 1.35 } }),
    ov('C_lyr_toofast', 104.17, 108.67, { type: 'canvas', module: 'lowerthird', params: { color: INK, halo: 0.9, size: 74 } }),
    ov('C_lyr_nowarning', 108.67, 110.78, { type: 'canvas', module: 'lowerthird', params: { color: INK, halo: 0.9, size: 74 } }),
    ov('C_lyr_shot', 110.78, 111.62, { type: 'canvas', module: 'whisper', params: { text: 'shot', sync: 'lyric', x: 420, y: 330, size: 44 } }),
    ov('C_lyr_timestops', 111.62, 112.66, { type: 'canvas', module: 'whisper', params: { text: '… and time stops', sync: 'lyric', x: 400, y: 990, size: 34, color: '#a9a49b' } }),
    // the hit: Celeste mote burst at the impact point on the B_shot plate (her side, where the drawn motes come from)
    ov('C_motes', 110.78, 112.66, { type: 'canvas', module: 'motes', keepColor: true, params: { at: '110.82', x: 950, y: 410, count: 64 } }),
    // the ◀◀ on the arcade button (no model-drawn glyphs)
    ov('C_rw_glyph', 112.66, 112.96, { type: 'canvas', module: 'pin', params: { style: 'plain', text: '◀◀', font: '"Press Start 2P"', size: 120, color: INK, x: 700, y: 470, rotate: -8 } }),
  ];
  return { shots, overlays };
}
