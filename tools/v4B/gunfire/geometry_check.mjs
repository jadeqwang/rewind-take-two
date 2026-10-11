// Geometry check of the BUILT gunfire shots (render/timeline/_B_glayout.js, _B_gunfire.js), after Jade's "lead" note.
//   node tools/v4B/gunfire/geometry_check.mjs
// For every miss: the muzzle that flares and the impact (design px, 1920x1080, on the shot frame), whether the impact
// lies AHEAD of her on the line she was on before her last cut (a lead), how far the impact and the whole ruled line
// stay from her body on the shot frame, and whether the barrel points at the impact (angle between barrel and line).
// Writes media/reviews/v4/B/plans/gunfire/geometry.json (the blockout's version is in geometry_blockout.json).
import fs from 'fs';
const R = '/home/jade/Documents/rewind-take-two';
const L = await import(`${R}/render/timeline/_B_glayout.js`);
const G = await import(`${R}/render/timeline/_B_gunfire.js`);
G.g2();                                                    // fills G.G2GEO
const segDist = (p, a, b) => { const v = [b[0] - a[0], b[1] - a[1]], w = [p[0] - a[0], p[1] - a[1]];
  const n2 = v[0] ** 2 + v[1] ** 2, u = n2 ? Math.max(0, Math.min(1, (w[0] * v[0] + w[1] * v[1]) / n2)) : 0; return Math.hypot(w[0] - u * v[0], w[1] - u * v[1]); };
const bodyGap = (feet, head, half, a, b) => {           // min distance from the line a-b to her body (a capsule), px
  let m = 1e9; for (let k = 0; k <= 20; k++) { const p = [feet[0] + (head[0] - feet[0]) * k / 20, feet[1] + (head[1] - feet[1]) * k / 20]; m = Math.min(m, segDist(p, a, b)); }
  return m - half; };
const r1 = x => Math.round(x * 10) / 10;
const out = { source: 'built timeline (render/timeline/_B_glayout.js + _B_gunfire.js), v4c: chest-high leads on the line she left; rounds land beyond her', G1: [], G2: [] };
// v4c: each shot is aimed at the CHEST-HIGH point her torso would occupy at the shot on the line she left; the round
// passes through that empty point and lands far beyond (G1: grass; G2: the notice board just behind her)
const ptLine = (p, a, b) => segDist(p, a, b);
for (const [tb, who] of L.FIRES) {
  const cam = L.camAt(tb), A3 = L.torsoOf(tb), A = L.project(cam, A3), Ld3 = L.landOf(who, tb), Ld = L.project(cam, Ld3), J = L.jadeAt(tb);
  const feet = L.project(cam, J), head = L.project(cam, [J[0], 1.62, J[2]]), half = cam.f * 0.25 / feet[2];
  const turn = L.TURN_TIMES.filter(t => t < tb).pop(), Pt = L.jadeAt(turn), vOld = L.jadeVel(turn - 1e-3);
  const ahead = (A3[0] - Pt[0]) * vOld[0] + (A3[2] - Pt[2]) * vOld[2] > 0;
  const pose = L.agentPose(who, tb), M = pose.muzzle;
  const r = pose.rotate * Math.PI / 180, sgn = pose.sx < 0 ? -1 : 1;
  const bx = sgn * (L.CUT.muzzle[0] - L.CUT.slide[0]), by = L.CUT.muzzle[1] - L.CUT.slide[1];
  const bd = [Math.cos(r) * bx - Math.sin(r) * by, Math.sin(r) * bx + Math.cos(r) * by];
  const err = Math.abs(Math.atan2(Ld[1] - M[1], Ld[0] - M[0]) - Math.atan2(bd[1], bd[0])) * 180 / Math.PI;
  out.G1.push({ t: tb, who, turn, muzzle_px: M.map(r1), aim_point_px: A.slice(0, 2).map(r1), aim_point_m: A3.map(r1),
    aim_on_old_line_ahead: ahead, aim_point_to_her_m: r1(Math.hypot(A3[0] - J[0], A3[2] - J[2])),
    aim_point_off_tracer_px: r1(ptLine(A, M, Ld)), lands_px: Ld.slice(0, 2).map(r1), lands_m: Ld3.map(r1),
    lands_beyond_her_m: r1(Ld3[2] - J[2]), land_clear_of_her_px: r1(bodyGap(feet, head, half, Ld, Ld)),
    drawn_line_clear_of_her_px: r1((() => { const len = Math.hypot(A[0] - M[0], A[1] - M[1]), tl = Math.min(0.3, 40 / len); return bodyGap(feet, head, half, M, [A[0] + (A[0] - M[0]) * tl, A[1] + (A[1] - M[1]) * tl]); })()),
    far_turf_drawn: bodyGap(feet, head, half, Ld, Ld) > 80, barrel_vs_line_deg: r1(err) });
}
const g = G.G2GEO;
for (let k = 0; k < 2; k++) {
  const lt = g.tb[k] - g.st, M = g.gun(lt), A = g.A3[k], H = g.H[k];
  const feet = g.path(lt), h = g.hgt(feet[1]), head = [feet[0], feet[1] - h], half = 0.16 * h;
  const turn = g.turns.filter(t => t < g.tb[k]).pop(), pt = g.path(turn - g.st), pb = g.path(turn - g.st - 0.05);
  const ahead = (A[0] - pt[0]) * (pt[0] - pb[0]) > 0;
  const r = g.armR(lt), bd = [Math.cos(r), Math.sin(r)];       // arm.png barrel is ~2 deg off its x axis
  const err = Math.abs(Math.atan2(H[1] - M[1], H[0] - M[0]) - Math.atan2(bd[1], bd[0])) * 180 / Math.PI;
  out.G2.push({ t: g.tb[k], who: 'C', turn, muzzle_px: M.map(r1), aim_point_px: A.map(r1), aim_on_old_line_ahead: ahead,
    aim_chest_height_px_above_feet: r1(0.8 * g.hgt(feet[1])), aim_point_off_tracer_px: r1(ptLine(A, M, H)),
    lands_px: H.map(r1), lands_on: H[0] >= 977 && H[0] <= 1334 && H[1] >= 331 && H[1] <= 586 ? 'notice board (behind her)' : 'grass beyond',
    line_clear_of_her_px: r1(bodyGap(feet, head, half, M, H)), barrel_vs_line_deg: r1(err) });
}
const dir = `${R}/media/reviews/v4/B/plans/gunfire`;
if (!fs.existsSync(`${dir}/geometry_blockout.json`)) fs.copyFileSync(`${dir}/geometry.json`, `${dir}/geometry_blockout.json`);
fs.writeFileSync(`${dir}/geometry.json`, JSON.stringify(out, null, 1));
for (const k of ['G1', 'G2']) for (const m of out[k]) console.log(k, JSON.stringify(m));
