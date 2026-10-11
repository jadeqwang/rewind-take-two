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
import { DW, DH, camAt, project, proj, jadeAt, agentAt, agentPose, plateAt, onPlate, FIRES, LAG, impactOf, landOf, torsoOf, CUT, aimAngle } from './_B_glayout.js';
const sm = u => { u = Math.min(1, Math.max(0, u)); return u * u * (3 - 2 * u); };
import { G1WORLD } from './_B_gtrack.js';
import { G2GUN } from './_B_ggun.js';

const S = 'media/shots/';
export const G2GEO = {};          // filled by g2(): impacts, path, gun track (for tools/v4B/gunfire/geometry_check.mjs)
const INK = '#0b0b0c';
const beatPunch = { type: 'punch', amount: 0.018, on: 'beat' };
const WOODCUT = 'tools/sectionA/modules/woodcut.js';
const pin = (corners, text, extra = {}) => ({ type: 'canvas', module: 'pin',
  params: { style: 'plain', font: 'slab', color: INK, uppercase: true, padding: 4, corners, text, ...extra } });
const hilbert = (corners, text = 'HILBERT', id = 'hilbert', box = [420, 140]) => ({ id, type: 'canvas', module: WOODCUT,
  params: { text, at: -1, color: INK, flecks: 0, hatch: 0.15, box, pad: 8, corners } });
const flat = q => q.flat();

// ---- G1 ------------------------------------------------------------------------------------------------------------
function g1() {
  const st = 98.28, en = 100.70, T = lt => st + lt;
  // Jade's take: its four turns (source 0.7 / 2.0 / 3.5 / 4.4, from the matte track) land on her layout cuts 98.77 /
  // 99.21 / 99.65 / 100.09 (4 frames before each shot beat). Legs are 0.44 s, shorter than the take's, so the middle of
  // each long source leg is skipped (a sub-frame jump mid-stride, J = 1/96 s) rather than running her at 3x.
  const J = 1 / 96;
  const SRC = [[0, 0.06], [0.49, 0.70],
    [0.71 - J, 1.00], [0.71, 1.70], [0.93, 2.00],
    [1.15 - J, 2.30], [1.15, 3.20], [1.37, 3.50],
    [1.59 - J, 3.80], [1.59, 4.10], [1.81, 4.40], [2.42, 4.98]];
  const srcOf = lt => { for (let i = 1; i < SRC.length; i++) if (lt <= SRC[i][0] || i === SRC.length - 1) {
    const [a, b] = [SRC[i - 1], SRC[i]]; return a[1] + (b[1] - a[1]) * Math.min(1, Math.max(0, (lt - a[0]) / (b[0] - a[0]))); } };
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
  // v4c: every shot is aimed at the chest-high spot she left (torsoOf); the line runs through it and a little past;
  // the round lands far beyond (landOf), shown as a kick of turf only where that spot is clear of her on screen
  const clear = (tb, P) => { const c = camAt(tb), J = jadeAt(tb), f = project(c, J), hd = project(c, [J[0], 1.62, J[2]]), half = c.f * 0.25 / f[2];
    let m = 1e9; for (let k = 0; k <= 10; k++) { const y = f[1] + (hd[1] - f[1]) * k / 10; m = Math.min(m, Math.hypot(P[0] - f[0], P[1] - y)); } return m - half; };
  const misses = FIRES.map(([tb, who], k) => {
    const A3 = torsoOf(tb), Ld = landOf(who, tb), landOK = clear(tb, project(camAt(tb), Ld)) > 80;
    const z = Math.max(0.45, 1.62 * camAt(tb).f / project(camAt(tb), A3)[2] / 330);
    const O0 = agentPose(who, tb).muzzle, A0s = project(camAt(tb), A3), len = Math.hypot(A0s[0] - O0[0], A0s[1] - O0[1]);
    return { id: `g1shot${k}`, type: 'canvas', module: 'render/timeline/_B_gunshot.js', params: { at: tb - st, size: z, tail: Math.min(0.3, 40 / len),
      origin: lt => agentPose(who, T(lt)).muzzle, aim: lt => proj(T(lt), A3).slice(0, 2),
      land: landOK ? (lt => proj(T(lt), Ld).slice(0, 2)) : null } };
  });
  const BB = [1309, 129, 1484, 65, 1484, 136, 1309, 190];          // the plate's left billboard panel (design px at 98.28)
  const bb = lt => flat([0, 2, 4, 6].map(i => onPlate(T(lt), [BB[i], BB[i + 1]])));
  // Jade: "HILBERT HOTEL (missing HOTEL on a blank sign above)": the plate's second, right-hand panel gets HOTEL
  const HB = [1495, 65, 1670, 102, 1666, 172, 1495, 136];
  const hb = lt => flat([0, 2, 4, 6].map(i => onPlate(T(lt), [HB[i], HB[i + 1]])));
  return { id: 'B2_G1', start: st, end: en, background: INK, fx: [beatPunch], layers: [
    { id: 'plate', ...plate },
    hilbert(bb),
    hilbert(hb, 'HOTEL', 'hotel', [360, 140]),
    { id: 'zig', ...pin(ground(X0, XS), 'I zig', { style: 'ground', times: ['98.28', '98.47'], padding: 0, grain: 0.2 }), blend: 'multiply' },
    { id: 'zag', ...pin(ground(XS, X1), 'zag', { style: 'ground', times: ['98.78'], padding: 0, grain: 0.2 }), blend: 'multiply' },
    { id: 'ribbon', type: 'canvas', module: 'render/timeline/_B_gunribbon.js', keepColor: true, params: {} },
    { id: 'jade', ...jade },
    agent('C'), agent('A'), agent('B'),
    ...misses,
  ] };
}

// ---- G2: long lens behind A, B, C (agents-only take of B_g2clean; A is on his earpiece, B's hand goes up to his,
// source 0.6-1.4 -> 100.88-101.40). v4c: the take's C (pistol pointed at the grass) is painted out with the engraved
// no-C plate (B_g2noC/patch.png) and replaced by the G1 cut-out, his arm a separate piece (B_gcut/arm.png) the engine
// aims chest high. Jade: "aiming for where the torso would have been if she hadn't zagged": she cuts 4 frames before
// each shot (100.97, 101.83), and each round passes through the empty chest-high spot on the line she left and goes on
// into the notice board behind it (a hole). Between shots his arm tracks her predicted chest point on a spring.
function g2() {
  const st = 100.70, en = 102.46;
  const SRC = [[0, 0.09], [0.44, 0.78], [1.30, 2.13], [1.76, 2.85]];
  const lin = K => lt => { for (let i = 1; i < K.length; i++) if (lt <= K[i][0] || i === K.length - 1) {
    const [a, b] = [K[i - 1], K[i]], u = Math.min(1, Math.max(0, (lt - a[0]) / (b[0] - a[0])));
    return Array.isArray(a[1]) ? a[1].map((v, k) => v + (b[1][k] - v) * u) : a[1] + (b[1] - a[1]) * u; } };
  const tb = [101.14, 102.00], LD = 0.167;
  const add = (p, v, k) => [p[0] + v[0] * k, p[1] + v[1] * k];
  const hgt = y => 1.33 * (y - 523), chest = P => [P[0], P[1] - 0.8 * hgt(P[1])];       // her height: plate ground
  // her feet path (local time): left toward her lead point, cut right; right; left toward the second; cut right
  const v1 = [-330, -40], vN = [380, -50], I1f = [1080, 745], I2f = [1110, 700];
  const P1 = add(I1f, v1, -LD), A0 = add(P1, v1, -0.27), P2 = add(P1, vN, 0.43);
  const v2 = [(I2f[0] - P2[0]) / 0.60, (I2f[1] - P2[1]) / 0.60], P3 = add(P2, v2, 0.43), P4 = add(P3, vN, 0.63);
  const path = lin([[0, A0], [0.27, P1], [0.70, P2], [1.13, P3], [1.76, P4]]);
  const velAt = lt => { const a = path(lt), b = path(lt + 0.02); return [(b[0] - a[0]) / 0.02, (b[1] - a[1]) / 0.02]; };
  // C: the cut-out at its own spot in the keyframe it came from (B_g2/kf_v3.png, cover-fit 0.703)
  const K = 1920 / 2731, PV = [(CUT.shoulder[0] + 780) * K, (CUT.shoulder[1] + 420) * K];
  const off = q => [K * (q[0] - CUT.shoulder[0]), K * (q[1] - CUT.shoulder[1])];
  const rot = (r, [x, y]) => [Math.cos(r) * x - Math.sin(r) * y, Math.sin(r) * x + Math.cos(r) * y];
  const muzzleAt = r => { const m = rot(r, off(CUT.muzzle)); return [PV[0] + m[0], PV[1] + m[1]]; };
  const A3 = [chest(I1f), chest(I2f)];                                   // the empty chest-high spots
  const H = A3.map(a => { const M = muzzleAt(aimAngle(a, PV, off)); return [a[0] + (a[0] - M[0]) * 0.05, a[1] + (a[1] - M[1]) * 0.05]; });  // the board, just behind
  const want = lt => { const P = path(lt), v = velAt(lt); let T = chest(add(P, v, 0.3));
    for (let k = 0; k < 2; k++) { const l = tb[k] - st, w = sm((lt - (l - 0.30)) / 0.12) * (1 - sm((lt - (l + 0.10)) / 0.10));
      if (w > 0) T = [T[0] + (H[k][0] - T[0]) * w, T[1] + (H[k][1] - T[1]) * w]; }
    return aimAngle(T, PV, off); };
  const memo = new Map();
  const spring = lt => { const key = Math.round(lt * 960); if (memo.has(key)) return memo.get(key);
    let th = want(0), om = 0; for (let tt = 0; tt < lt; tt += 1 / 240) { const h = Math.min(1 / 240, lt - tt);
      om += (400 * (want(tt + h) - th) - 2 * 0.42 * 20 * om) * h; th += om * h; }
    if (memo.size > 3000) memo.clear(); memo.set(key, th); return th; };
  const armR = lt => { let r = spring(lt);
    for (let k = 0; k < 2; k++) { const l = tb[k] - st, w = sm((lt - (l - 0.12)) / 0.08) * (1 - sm((lt - (l + 0.04)) / 0.08)); if (w > 0) r += (want(lt) - r) * w;
      const dt = lt - l - 1 / 24; if (dt >= 0) r -= 9 * Math.exp(-dt / 0.07) * Math.PI / 180; }
    return r; };
  const shove = lt => { let b = 0; for (const t of tb) { const dt = lt - (t - st) - 1 / 24; if (dt >= 0) b += 14 * Math.exp(-dt / 0.07); } return b; };
  const armPV = lt => { const r = armR(lt), d = rot(r, [1, 0]); return [PV[0] - d[0] * shove(lt), PV[1] - d[1] * shove(lt)]; };
  const gunAt = lt => { const r = armR(lt), p = armPV(lt), m = rot(r, off(CUT.muzzle)); return [p[0] + m[0], p[1] + m[1]]; };
  const J = 1 / 96;   // her take's turns (source 2.0 / 3.5 / 4.4) on the cuts 100.97 / 101.40 / 101.83; long legs skip mid-stride
  const JSRC = [[0, 1.73], [0.27, 2.00], [0.485 - J, 2.30], [0.485, 3.20], [0.70, 3.50], [0.915 - J, 3.80], [0.915, 4.10],
    [1.13, 4.40], [1.76, 4.98]], jsrc = lin(JSRC);
  Object.assign(G2GEO, { tb, st, path, chest, hgt, A3, H, gun: gunAt, armR, turns: [100.97, 101.40, 101.83] });
  const trk = lt => { const f = Math.min(G1WORLD.length - 1.001, Math.max(0, jsrc(lt) * 24)), i = Math.floor(f), u = f - i;
    return G1WORLD[i].map((v, k) => v + (G1WORLD[i + 1][k] - v) * u); };
  const jade = { id: 'jade', type: 'video', src: `${S}B_g1world/take_1_engraved.mp4`, srcTime: JSRC, fit: 'cover',
    matte: { src: `${S}B_g1world/take_1_matte/matte.mp4`, mode: 'luma' }, keepColor: true,
    anchor: lt => { const r = trk(lt); return [r[3] / DW, r[1] / DH]; },
    scale: lt => hgt(path(lt)[1]) / trk(lt)[2],
    x: lt => path(lt)[0] - DW / 2, y: lt => path(lt)[1] - DH / 2 };
  const cut = (id, file, x, y, rotate) => ({ id, type: 'image', src: `${S}B_gcut/${file}`, fit: 'none',
    anchor: [CUT.shoulder[0] / CUT.w, CUT.shoulder[1] / CUT.h], scale: K, x, y, rotate });
  const misses = H.map((P, k) => traceMiss({ id: `g2miss${k}`, origin: lt => gunAt(lt), times: [tb[k]], shotStart: st,
    targets: [P], size: 0.6, width: 8, scar: 0, flecks: 10 }));
  return { id: 'B2_G2', start: st, end: en, background: INK, fx: [beatPunch], layers: [
    { id: 'plate', type: 'video', src: `${S}B_g2clean/take_1_engraved.mp4`, srcTime: SRC, fit: 'cover' },
    { id: 'noC', type: 'image', src: `${S}B_g2noC/patch.png`, fit: 'cover' },
    { id: 'board', ...pin([985, 346, 1325, 346, 1325, 500, 985, 500], 'across the\nfield of',
      { times: ['100.63', '101.28', '101.42', '101.74'], padding: 6 }) },
    ...H.map((P, k) => ({ id: `hole${k}`, type: 'canvas', module: 'render/timeline/_B_hole.js', params: { at: tb[k] - st, x: P[0], y: P[1], r: 11 } })),
    ...misses.flatMap(m => m.under),
    jade,
    cut('C_body', 'body.png', PV[0] - DW / 2, PV[1] - DH / 2, 0),
    cut('C_arm', 'arm.png', lt => armPV(lt)[0] - DW / 2, lt => armPV(lt)[1] - DH / 2, lt => armR(lt) * 180 / Math.PI),
    ...misses.flatMap(m => m.over),
  ] };
}

// ---- G3: the earpiece close-up (take of the B_g3ear edit; camera locked) --------------------------------------------
function g3() {
  const st = 102.46;
  return { id: 'B2_G3', start: st, end: 104.22, background: INK, fx: [beatPunch], layers: [
    { id: 'plate', type: 'video', src: `${S}B_g3ear/take_1_engraved.mp4`, in: 0.2, rate: 1, fit: 'cover' },
    hilbert([1625, 105, 1819, 20, 1820, 97, 1626, 162], 'HILBERT\nHOTEL', 'hilbert', [420, 230]),   // one panel here
  ] };
}

export function gunfireShots() {
  return [g1(), g2(), g3()];
}
export { g1, g2, g3 };
