// _B_gunfire.js (v4, Jade's notes 1:39 and 1:41): the lawn from behind the agents. Replaces v3's B2_lawn, B2_lawn2 and
// B2_ear (render/timeline/_B_verse2.js switches with V4_GUN). Plan: docs/revisions/v4/plans/gunfire.md.
//   G1 98.28-100.70  behind A and B, the camera drives between their shoulders and settles over C's. Layered: the
//                    lawn/hotel plate (a still card), Jade from her take placed on the layout path, the agents as one
//                    engraved cut-out (B mirrored) turned so each barrel points at its miss. 4 misses: B B C C.
//   G2 100.70-102.46 long lens behind three agents (one take): C alone fires, twice, into the turf behind her; A and
//                    B are on their earpieces. "ACROSS THE / FIELD OF" on the notice board.
//   G3 102.46-104.22 earpiece close-up (one take): both callers speak; she is tiny, running to the hotel.
// Every miss is traceMiss() from _B_fx.js, its origin the muzzle that flares, its target the spot she left.
import { traceMiss } from './_B_fx.js';
import { DW, DH, camAt, project, proj, jadeAt, agentAt, agentPose, plateAt, onPlate, FIRES, LAG, impactOf, CUT } from './_B_glayout.js';
import { G1WORLD } from './_B_gtrack.js';
import { G2GUN } from './_B_ggun.js';

const S = 'media/shots/';
const INK = '#0b0b0c';
const beatPunch = { type: 'punch', amount: 0.018, on: 'beat' };
const WOODCUT = 'tools/sectionA/modules/woodcut.js';
const pin = (corners, text, extra = {}) => ({ type: 'canvas', module: 'pin',
  params: { style: 'plain', font: 'slab', color: INK, uppercase: true, padding: 4, corners, text, ...extra } });
const hilbert = corners => ({ id: 'hilbert', type: 'canvas', module: WOODCUT,
  params: { text: 'HILBERT', at: -1, color: INK, flecks: 0, hatch: 0.15, box: [420, 140], pad: 8, corners } });
const flat = q => q.flat();

// ---- G1 ------------------------------------------------------------------------------------------------------------
function g1() {
  const st = 98.28, en = 100.70, T = lt => st + lt;
  // Jade's take: her turns (source 0.7 / 2.0 / 3.5, from the matte track) land on the beats 98.50 / 99.38 / 100.26
  const SRC = [[0, 0.37], [0.22, 0.7], [1.10, 2.0], [1.98, 3.5], [2.42, 4.2]];
  const srcOf = lt => { for (let i = 1; i < SRC.length; i++) if (lt <= SRC[i][0] || i === SRC.length - 1) {
    const [a, b] = [SRC[i - 1], SRC[i]]; return a[1] + (b[1] - a[1]) * (lt - a[0]) / (b[0] - a[0]); } };
  const trk = lt => { const f = Math.min(G1WORLD.length - 1.001, Math.max(0, srcOf(lt) * 24)), i = Math.floor(f), u = f - i;
    return G1WORLD[i].map((v, k) => v + (G1WORLD[i + 1][k] - v) * u); };          // [cx, bottom, height, foot_x]
  const feet = lt => proj(T(lt), jadeAt(T(lt)));
  const jade = { type: 'video', src: `${S}B_g1world/take_1_engraved.mp4`, srcTime: SRC, fit: 'cover',
    matte: { src: `${S}B_g1world/take_1_matte/matte.mp4`, mode: 'luma' }, keepColor: true,
    anchor: lt => { const r = trk(lt); return [r[3] / DW, r[1] / DH]; },
    scale: lt => { const c = camAt(T(lt)); return (c.f * 1.62 / feet(lt)[2]) / trk(lt)[2]; },
    x: lt => feet(lt)[0] - DW / 2, y: lt => feet(lt)[1] - DH / 2 };
  const plate = { type: 'image', src: `${S}B_g1clean/kf_v1.jpg`, fit: 'cover',
    x: lt => plateAt(T(lt)).x, y: lt => plateAt(T(lt)).y, scale: lt => plateAt(T(lt)).s };
  const agent = name => ({ id: `agent_${name}`, type: 'image', src: `${S}B_gcut/agent.png`, fit: 'none',
    anchor: [CUT.shoulder[0] / CUT.w, CUT.shoulder[1] / CUT.h],
    x: lt => agentPose(name, T(lt)).pivot[0] - DW / 2, y: lt => agentPose(name, T(lt)).pivot[1] - DH / 2,
    scale: lt => { const p = agentPose(name, T(lt)); return [p.sx, p.s]; }, rotate: lt => agentPose(name, T(lt)).rotate,
    // the camera drives past A and B: each fades as his shoulder comes within ~1 m of the lens (he has left the frame)
    opacity: lt => { const d = agentPose(name, T(lt)).depth, u = Math.min(1, Math.max(0, (d - 0.8) / 0.5)); return u * u * (3 - 2 * u); } });
  // "I ZIGZAG" painted on the grass between the shoulders: 'I zig' then 'zag' (the second z in the vocal, 98.78)
  const X0 = -1.15, X1 = 2.75, Z0 = 7.0, Z1 = 16.5, XS = X0 + (X1 - X0) * 0.565;
  const ground = (xa, xb) => lt => flat([[xa, 0, Z1], [xb, 0, Z1], [xb, 0, Z0], [xa, 0, Z0]].map(P => proj(T(lt), P).slice(0, 2)));
  const misses = FIRES.map(([tb, who], k) => {
    const I = impactOf(tb);
    return traceMiss({ id: `g1miss${k}`, origin: lt => agentPose(who, T(lt)).muzzle, times: [tb], shotStart: st, lag: LAG,
      targets: [proj(tb - LAG, I).slice(0, 2)], scroll: lt => proj(T(lt), I).slice(0, 2),
      size: Math.max(0.55, 1.62 * camAt(tb).f / project(camAt(tb), I)[2] / 300), width: 8 });   // marks scale with her on screen; line ~4 px
  });
  const BB = [1309, 129, 1484, 65, 1484, 136, 1309, 190];          // the plate's left billboard panel (design px at 98.28)
  const bb = lt => flat([0, 2, 4, 6].map(i => onPlate(T(lt), [BB[i], BB[i + 1]])));
  return { id: 'B2_G1', start: st, end: en, background: INK, fx: [beatPunch], layers: [
    { id: 'plate', ...plate },
    hilbert(bb),
    { id: 'zig', ...pin(ground(X0, XS), 'I zig', { style: 'ground', times: ['98.28', '98.47'], padding: 0, grain: 0.2 }), blend: 'multiply' },
    { id: 'zag', ...pin(ground(XS, X1), 'zag', { style: 'ground', times: ['98.78'], padding: 0, grain: 0.2 }), blend: 'multiply' },
    ...misses.flatMap(m => m.under),
    { id: 'ribbon', type: 'canvas', module: 'render/timeline/_B_gunribbon.js', keepColor: true, params: {} },
    { id: 'jade', ...jade },
    agent('C'), agent('A'), agent('B'),
    ...misses.flatMap(m => m.over),
  ] };
}

// ---- G2: long lens behind A, B, C (agents-only take of B_g2clean). C alone fires; A is on his earpiece, B's hand goes
// up to his (source 0.6-1.4 -> 100.88-101.40). The take is retimed so C's two recoils (source 0.80 / 2.15, read off
// the pistol track) follow the shots on 101.14 and 102.00. Jade is her G1 take, placed on a screen path that is
// on C's barrel line exactly where each miss lands: she was there a beat (101.14) / two beats (102.00) before.
function g2() {
  const st = 100.70, en = 102.46;
  const SRC = [[0, 0.09], [0.44, 0.78], [1.30, 2.13], [1.76, 2.85]];
  const lin = K => lt => { for (let i = 1; i < K.length; i++) if (lt <= K[i][0] || i === K.length - 1) {
    const [a, b] = [K[i - 1], K[i]], u = (lt - a[0]) / (b[0] - a[0]); return Array.isArray(a[1]) ? a[1].map((v, k) => v + (b[1][k] - v) * u) : a[1] + (b[1] - a[1]) * u; } };
  const srcOf = lin(SRC);
  const gun = lt => { const f = Math.min(G2GUN.length - 1.001, Math.max(0, srcOf(lt) * 24)), i = Math.floor(f), u = f - i;
    return G2GUN[i].map((v, k) => v + (G2GUN[i + 1][k] - v) * u); };                  // [mx, my, dx, dy]
  const onBarrel = (lt, x) => { const g = gun(lt); return [x, g[1] + (x - g[0]) / g[2] * g[3]]; };
  // C's barrel hardly moves in the take, so she crosses its line once: up the line (away from him) from Pb to Pa,
  // then cuts right, off it. 101.14 lands on Pa (she was there at 100.70, a beat before); 102.00 lands on Pb, further
  // back (she was there at 100.55, before the cut): he is falling behind. Neither line ever crosses her on screen.
  const tb = [101.14, 102.00], lag = [0.44, 1.45];
  const I1 = onBarrel(tb[0] - st, 1040), I2 = onBarrel(tb[1] - st, 1068);
  // her feet on screen (local time); height from the plate's ground: 1.33 px per px below the horizon (y 523)
  const path = lin([[-0.15, I2], [0, I1], [0.44, [1060, 724]], [0.88, [1160, 688]], [1.30, [1255, 655]], [1.76, [1330, 630]]]);
  const JSRC = [[0, 2.0], [1.76, 3.45]], jsrc = lin(JSRC);   // her source turn at 2.0 (left -> right) lands on the 100.70 cut
  const trk = lt => { const f = Math.min(G1WORLD.length - 1.001, Math.max(0, jsrc(lt) * 24)), i = Math.floor(f), u = f - i;
    return G1WORLD[i].map((v, k) => v + (G1WORLD[i + 1][k] - v) * u); };
  const jade = { id: 'jade', type: 'video', src: `${S}B_g1world/take_1_engraved.mp4`, srcTime: JSRC, fit: 'cover',
    matte: { src: `${S}B_g1world/take_1_matte/matte.mp4`, mode: 'luma' }, keepColor: true,
    anchor: lt => { const r = trk(lt); return [r[3] / DW, r[1] / DH]; },
    scale: lt => 1.33 * (path(lt)[1] - 523) / trk(lt)[2],
    x: lt => path(lt)[0] - DW / 2, y: lt => path(lt)[1] - DH / 2 };
  const misses = [I1, I2].map((I, k) => traceMiss({ id: `g2miss${k}`, origin: lt => gun(lt).slice(0, 2), times: [tb[k]], shotStart: st,
    lag: lag[k], targets: [I], size: 0.62, width: 8 }));
  return { id: 'B2_G2', start: st, end: en, background: INK, fx: [beatPunch], layers: [
    { id: 'plate', type: 'video', src: `${S}B_g2clean/take_1_engraved.mp4`, srcTime: SRC, fit: 'cover' },
    { id: 'board', ...pin([985, 346, 1325, 346, 1325, 500, 985, 500], 'across the\nfield of',
      { times: ['100.63', '101.28', '101.42', '101.74'], padding: 6 }) },
    ...misses.flatMap(m => m.under),
    jade,
    ...misses.flatMap(m => m.over),
  ] };
}

// ---- G3: the earpiece close-up (take of the B_g3ear edit; camera locked) --------------------------------------------
function g3() {
  const st = 102.46;
  return { id: 'B2_G3', start: st, end: 104.22, background: INK, fx: [beatPunch], layers: [
    { id: 'plate', type: 'video', src: `${S}B_g3ear/take_1_engraved.mp4`, in: 0.2, rate: 1, fit: 'cover' },
    hilbert([1625, 105, 1819, 20, 1820, 97, 1626, 162]),
  ] };
}

export function gunfireShots() {
  return [g1(), g2(), g3()];
}
export { g1, g2, g3 };
