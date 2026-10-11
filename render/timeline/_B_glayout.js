// _B_glayout.js (v4 gunfire, notes 1:39 / 1:41): the lawn in metres and the G1 camera, shared by the timeline
// (render/timeline/_B_gunfire.js) and its canvas modules. Same layout as the approved blockout
// (tools/v4B/gunfire/blockout.py, media/reviews/v4/B/plans/gunfire/): x right, y up, z away from the firing line
// (agents A and B at z = 0) toward the hotel. Song seconds. Design px are 1920x1080.
export const DW = 1920, DH = 1080;

// Jade: straight legs between turn points, every turn on a tracked beat; 4.1 m/s of depth
const TURNS = [[97.62, -2.4], [98.50, 2.3], [99.38, -2.2], [100.26, 2.8], [100.70, 0.9], [101.14, 3.0]];
const Z0 = 19.0, VZ = 4.1;
export function jadeAt(t) {
  for (let i = 0; i < TURNS.length - 1; i++) {
    const [t0, x0] = TURNS[i], [t1, x1] = TURNS[i + 1];
    if (t <= t1 || i === TURNS.length - 2) { const u = (t - t0) / (t1 - t0); return [x0 + (x1 - x0) * u, 0, Z0 + VZ * (t - 98.28)]; }
  }
}
export function agentAt(name, t) {
  if (name === 'A') return [-0.95, 0, 0];
  if (name === 'B') return [1.25, 0, 0.3];
  return [-1.3 + 0.19 * (Math.min(t, 102.46) - 98.28), 0, 3.2 + 1.2 * (Math.min(t, 102.9) - 98.28)];  // C walks forward
}
export const LAG = 0.25;
export const FIRES = [[98.94, 'B'], [99.38, 'B'], [99.82, 'C'], [100.26, 'C']];          // A only aims
export const impactOf = tb => jadeAt(tb - LAG);                                            // where she was, on the grass

// G1 camera: starts behind A and B, drives between their shoulders (ease in), settles over C's; lens 47 -> 31 deg
const G1 = { t0: 98.28, t1: 100.70, p0: [0.05, 1.78, -3.05], p1: [-0.22, 1.68, 2.85], yaw: [0, 0.6], pitch: 0.45, fov: [47, 31] };
export function camAt(t) {
  const u0 = Math.min(1, Math.max(0, (t - G1.t0) / (G1.t1 - G1.t0))), u = u0 * u0;
  const L = (a, b) => a + (b - a) * u;
  const ta = Math.tan(G1.fov[0] * Math.PI / 360), tb = Math.tan(G1.fov[1] * Math.PI / 360);
  const f = (DW / 2) / Math.exp(L(Math.log(ta), Math.log(tb)));
  return { pos: [0, 1, 2].map(k => L(G1.p0[k], G1.p1[k])), yaw: L(G1.yaw[0], G1.yaw[1]) * Math.PI / 180, pitch: G1.pitch * Math.PI / 180, f };
}
// world -> [sx, sy, depth] in design px
export function project(cam, P) {
  const d = [P[0] - cam.pos[0], P[1] - cam.pos[1], P[2] - cam.pos[2]];
  const cy = Math.cos(cam.yaw), sy = Math.sin(cam.yaw), cp = Math.cos(cam.pitch), sp = Math.sin(cam.pitch);
  const x = cy * d[0] - sy * d[2], z = sy * d[0] + cy * d[2];
  const y2 = cp * d[1] + sp * z, z2 = -sp * d[1] + cp * z;
  return [DW / 2 + cam.f * x / z2, DH / 2 - cam.f * y2 / z2, z2];
}
export const proj = (t, P) => project(camAt(t), P);

// the lawn/hotel plate is a card ZP m out, filling the frame at the first frame (a pure zoom plus a little dolly)
const ZP = 60;
const cam0 = camAt(G1.t0);
const PC = [cam0.pos[0], cam0.pos[1] - (ZP - cam0.pos[2]) * Math.tan(cam0.pitch), ZP];
const k0 = cam0.f / project(cam0, PC)[2];
export function plateAt(t) {               // {x, y (offset of the plate centre from the frame centre), s (scale)}
  const c = camAt(t), p = project(c, PC);
  return { x: p[0] - DW / 2, y: p[1] - DH / 2, s: (c.f / p[2]) / k0 };
}
export const onPlate = (t, [x, y]) => { const q = plateAt(t); return [DW / 2 + q.x + (x - DW / 2) * q.s, DH / 2 + q.y + (y - DH / 2) * q.s]; };

// the agent cut-out (media/shots/B_gcut/agent.json): image px of shoulder (pivot), muzzle, rear of slide; 909 px = 1.82 m
export const CUT = { w: 620, h: 960, shoulder: [215, 178], muzzle: [566, 184], slide: [452, 180], mPerPx: 1.82 / 909, shoulderY: 1.52 };
const rot = (r, [x, y]) => [Math.cos(r) * x - Math.sin(r) * y, Math.sin(r) * x + Math.cos(r) * y];
const sub = (a, b) => [a[0] - b[0], a[1] - b[1]];
// screen pose of an agent's cut-out at time t: pivot, scale, mirror, rotation (deg), muzzle
const MIRROR = { A: 1, B: -1, C: 1 };
const smooth = u => { u = Math.min(1, Math.max(0, u)); return u * u * (3 - 2 * u); };
export function agentPose(name, t) {
  const cam = camAt(t), a = agentAt(name, t), P = project(cam, [a[0], CUT.shoulderY, a[2]]);
  const s = cam.f / P[2] * CUT.mPerPx, sx = s * MIRROR[name];
  const off = q => [sx * (q[0] - CUT.shoulder[0]), s * (q[1] - CUT.shoulder[1])];
  // aim: track the spot she was at LAG ago (low, on the grass); lock on the impact for each of his shots
  const trackP = project(cam, jadeAt(t - LAG)), mine = FIRES.filter(f => f[1] === name).map(f => f[0]);
  let T = trackP;
  for (const tb of mine) {
    const w = smooth((t - (tb - 0.45)) / 0.12) * (1 - smooth((t - (tb + 0.18)) / 0.12));
    if (w > 0) { const I = project(cam, impactOf(tb)); T = [T[0] + (I[0] - T[0]) * w, T[1] + (I[1] - T[1]) * w]; }
  }
  const pv = [P[0], P[1]];
  let r = Math.atan2(T[1] - pv[1], T[0] - pv[0]) - Math.atan2(off(CUT.muzzle)[1], off(CUT.muzzle)[0]);
  for (let i = 0; i < 4; i++) {                     // put T on the barrel line (slide -> muzzle), not just the pivot line
    const M = sub(rot(r, off(CUT.muzzle)), [0, 0]), Sd = rot(r, off(CUT.slide)), D = sub(M, Sd), n = Math.hypot(D[0], D[1]);
    const TM = sub(T, [pv[0] + M[0], pv[1] + M[1]]), e = (D[0] * TM[1] - D[1] * TM[0]) / (n * Math.hypot(TM[0], TM[1]));
    r += Math.asin(Math.max(-1, Math.min(1, e))) * Math.hypot(TM[0], TM[1]) / Math.hypot(T[0] - pv[0], T[1] - pv[1]);
  }
  // recoil from the frame after each shot: the muzzle kicks up and settles
  let kick = 0;
  for (const tb of mine) { const dt = t - tb - 1 / 24; if (dt >= 0) kick += 6 * Math.exp(-dt / 0.08) * Math.min(1, dt * 48 + 0.5); }
  r += -kick * Math.PI / 180 * MIRROR[name];
  const M = rot(r, off(CUT.muzzle));
  return { pivot: pv, s, sx, rotate: r * 180 / Math.PI, muzzle: [pv[0] + M[0], pv[1] + M[1]], depth: P[2] };
}
