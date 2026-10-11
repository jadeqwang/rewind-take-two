// tessellate.js: the pursuing fleet as an Escher regular division of the plane (Day and Night / Sky and Water /
// Metamorphosis), drawn on the road plane of a plate through a pinhole camera.
//
// Far away the road is a flat tiling: black sedan-shaped tiles interlock with paper-white sedan-shaped tiles (one
// tile shape, translated on a square lattice and coloured like a checkerboard, so figure and ground are the same
// car). Coming toward the camera the black tiles gain volume and become solid engraved sedans with white starburst
// strobes, while the white tiles fade into the plate's own road. At the far end the tiling relaxes to plain cells
// and dissolves into wave hatching. The whole lattice advances toward the camera on the beat, so the pattern keeps
// turning into cars.
//
// The tile tiles by construction: both long sides are the straight lines x = ±w/2 and the nose curve
// y = -l/2 - a·g(x) is the tail curve y = +l/2 - a·g(x) translated by one tile length, so translated copies leave
// no gap and no overlap for any amplitude a (the convex nose of one car sits in the concave tail of the next).
//
//   params (all lengths in tile widths; the camera looks along +Y down the road, cars drive toward it):
//     cam: { f (px), pitch (deg down), h (camera height), cx, cy (principal point, design px), x0 (road centre, sideways
//            from the camera) }: a zero-roll pinhole. Fit it to a plate from the horizon (cy - f·tan pitch), the
//            vanishing point (cx) and the slope of the road edges ((u - cx)/(v - horizon) = X·cos pitch / h).
//     zoom: { z (keys), px, py }   zoom about a screen point; give the plate layer the same `scale` keys and
//            x = (px - 960)(1 - z), y = (py - 540)(1 - z) and the two stay locked
//     cols 8 (lanes), len 2.5 (tile length), front (distance of the fleet's front row at t0), t0 (absolute s),
//     advance 1 (tile lengths per beat), step 0.5 (0 = glide, 1 = jump on each beat), rows 70, near 2.5 (cull)
//     vol [y1, y2]     full volume nearer than y1, flat beyond y2
//     road [y1, y2]    white tiles thin into road hatching (plate shows through) nearer than y1, solid paper beyond y2
//     shape [y1, y2]   full car-shaped tile nearer than y1, plain cell beyond y2
//     far [y1, y2]     the tiling dissolves into wave hatching between y1 and y2
//     ink, paper, strobe 1 (roof starburst size), beams 1 (headlamp starbursts), detail 1 (line weight of the flat
//     car drawings), seed, parity 0|1 (which lanes are black in the front row), skip [[lane, row], …] (cars left out)
import { clamp, hash, lerp } from '../src/core.js';

const smooth = (a, b, x) => { const t = clamp((x - a) / (b - a || 1e-6)); return t * t * (3 - 2 * t); };
const NOSE = 0.42;                                           // nose depth of the full car tile (tile widths)
const g0 = (x) => 1 - Math.pow(Math.abs(2 * x), 2.6);        // nose profile across the tile, 0 at the corners, 1 on the axis

// the tile outline (plan), amplitude a: 0 = plain cell, 1 = car; N points per end, both ends the same curve
function tilePoly(l, a, N = 12) {
  const p = [];
  for (let k = 0; k <= N; k++) { const x = -0.5 + k / N; p.push([x, -l / 2 - a * NOSE * g0(x)]); }       // nose (toward camera)
  for (let k = 0; k <= N; k++) { const x = 0.5 - k / N; p.push([x, l / 2 - a * NOSE * g0(x)]); }         // tail
  return p;
}
// a real sedan plan with the same point count, for the solid cars (rounded both ends, a touch narrower than its tile)
function carPoly(l, N = 12) {
  const p = [], hw = 0.46, hl = l / 2 + NOSE * 0.55;
  const end = (x, s) => s * (hl - 0.42 * Math.pow(Math.abs(x / hw), 3.2)) - NOSE * 0.2;
  for (let k = 0; k <= N; k++) { const x = (-0.5 + k / N) * 2 * hw; p.push([x, end(x, -1)]); }
  for (let k = 0; k <= N; k++) { const x = (0.5 - k / N) * 2 * hw; p.push([x, end(x, 1)]); }
  return p;
}
const mix = (A, B, t) => A.map((q, i) => [lerp(q[0], B[i][0], t), lerp(q[1], B[i][1], t)]);
const rrect = (hw, y0, y1, n = 4) => {                       // rounded quad (cabin, roof), nose side first
  const r = Math.min(hw * 0.45, (y1 - y0) * 0.3), p = [];
  const corner = (cx, cy, a0) => { for (let k = 0; k <= n; k++) { const a = a0 + k / n * Math.PI / 2; p.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r]); } };
  corner(-hw + r, y0 + r, Math.PI); corner(hw - r, y0 + r, -Math.PI / 2); corner(hw - r, y1 - r, 0); corner(-hw + r, y1 - r, Math.PI / 2);
  return p;
};

export function draw(lt, env) {
  const g = env.ctx, p = env.params, T = env.T;
  const C = { f: 1500, pitch: 24, h: 9, cx: 960, cy: 540, x0: 0, ...(p.cam || {}) };
  const zm = p.zoom ? env.val(p.zoom.z, 1) : 1;
  if (zm !== 1) { const px = p.zoom.px ?? 960, py = p.zoom.py ?? 540; C.f *= zm; C.cx = px + (C.cx - px) * zm; C.cy = py + (C.cy - py) * zm; }
  const ph = C.pitch * Math.PI / 180, cp = Math.cos(ph), sp = Math.sin(ph);
  const P = (X, Y, Z = 0) => { const zc = Y * cp + (C.h - Z) * sp, yc = (C.h - Z) * cp - Y * sp; return [C.cx + C.f * X / zc, C.cy + C.f * yc / zc, C.f / zc]; };
  const cols = p.cols ?? 8, l = p.len ?? 2.5, rows = p.rows ?? 70, ink = p.ink || '#0b0b0c', paper = p.paper || '#ece7dc';
  const vol = p.vol || [22, 40], road = p.road || [16, 30], shape = p.shape || [70, 120], far = p.far || [120, 170];
  const detail = p.detail ?? 1, seed = p.seed ?? 7, parity = p.parity ?? 0;
  const skip = new Set((p.skip || []).map(q => q.join(',')));

  // lattice advance: whole tile lengths per beat, eased so part of each step lands on the beat
  const t0 = p.t0 != null ? T.time(p.t0) : env.origin, beats = T.beats;
  let s = 0;
  if (beats && beats.length) {
    let n = 0; while (n < beats.length - 1 && beats[n + 1] <= env.t) n++;
    let n0 = 0; while (n0 < beats.length - 1 && beats[n0 + 1] <= t0) n0++;
    const fr = (t, k) => clamp((t - beats[k]) / ((beats[k + 1] ?? beats[k] + 0.44) - beats[k]));
    const st = p.step ?? 0.5, e = (u) => lerp(u, 1 - Math.pow(1 - u, 4), st);
    s = ((n + e(fr(env.t, n))) - (n0 + e(fr(t0, n0)))) * (p.advance ?? 1);
  } else s = (env.t - t0) / 0.44 * (p.advance ?? 1);
  const front = p.front ?? 30, yMin = p.near ?? 2.5;

  const path = (pts, Y0, X0, Z) => {
    g.beginPath();
    for (let k = 0; k < pts.length; k++) { const q = P(X0 + pts[k][0], Y0 + pts[k][1], Z); k ? g.lineTo(q[0], q[1]) : g.moveTo(q[0], q[1]); }
    g.closePath();
  };
  const seg = (a, b) => { g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b[0], b[1]); g.stroke(); };

  g.save(); g.lineJoin = 'round'; g.lineCap = 'round';
  const full = tilePoly(l, 1), sedan = carPoly(l);
  const X = (i) => C.x0 + (i - (cols - 1) / 2);

  // ---------- 1. the flat tiling, far → near
  for (let j = rows; j >= 0; j--) {
    const Y = front + (j - s) * l; if (Y < yMin || Y > far[1]) continue;
    const a = 1 - smooth(shape[0], shape[1], Y), fade = 1 - smooth(far[0], far[1], Y);
    const wRoad = smooth(road[0], road[1], Y), poly = a > 0.999 ? full : tilePoly(l, a);
    const sc = P(C.x0, Y)[2];                                 // px per tile width at this row
    for (let i = 0; i < cols; i++) {
      const black = ((i + j + parity) & 1) === 0, gone = skip.has(i + ',' + j);
      if (black) {
        if (gone) continue;
        g.globalAlpha = fade; g.fillStyle = ink; path(poly, Y, X(i), 0); g.fill();
      } else {
        if (wRoad <= 0.01) continue;
        g.globalAlpha = fade; g.fillStyle = paper; path(poly, Y, X(i), 0);
        if (wRoad > 0.97) g.fill();
        else {                                                // the tile thins into engraved road hatching
          g.save(); g.clip(); g.strokeStyle = paper; const n = 9;
          for (let k = 0; k < n; k++) {
            const xx = X(i) - 0.5 + (k + 0.5) / n, q0 = P(xx, Y - l / 2 - NOSE), q1 = P(xx, Y + l / 2);
            g.lineWidth = Math.max(0.6, (q0[2] + q1[2]) / 2 / n * wRoad * 1.05); g.beginPath(); g.moveTo(q0[0], q0[1]); g.lineTo(q1[0], q1[1]); g.stroke();
          }
          g.restore();
        }
      }
      // car drawing inside the flat tile (roof, windscreen, rear window): paper lines on ink, ink lines on paper
      const flat = black ? smooth(vol[0], vol[1], Y) > 0.35 : wRoad > 0.97;
      if (detail > 0 && sc > 14 && a > 0.3 && flat) {
        g.globalAlpha = fade * clamp((sc - 14) / 8) * clamp((a - 0.3) / 0.3); g.strokeStyle = black ? paper : ink; g.lineWidth = Math.max(1.3, sc * 0.03) * detail;
        const x = X(i), yN = Y - l / 2 - NOSE * a, col = black ? paper : ink;
        g.fillStyle = col;
        const quad = (pts) => { g.beginPath(); pts.forEach((q, k) => { const r = P(x + q[0], Y + q[1]); k ? g.lineTo(r[0], r[1]) : g.moveTo(r[0], r[1]); }); g.closePath(); };
        quad([[-0.37, -0.2 * l], [0.37, -0.2 * l], [0.3, -0.06 * l], [-0.3, -0.06 * l]]); g.fill();                    // windscreen
        quad([[-0.29, 0.25 * l], [0.29, 0.25 * l], [0.35, 0.35 * l], [-0.35, 0.35 * l]]); g.fill();                    // rear window
        quad([[-0.3, -0.03 * l], [0.3, -0.03 * l], [0.29, 0.22 * l], [-0.29, 0.22 * l]]); g.stroke();                  // roof
        quad([[-0.4, -0.5 * l - 0.02], [-0.22, -0.5 * l - 0.14 * a], [-0.22, -0.5 * l + 0.1 - 0.14 * a], [-0.4, -0.5 * l + 0.1]]); g.fill();   // headlamps
        quad([[0.4, -0.5 * l - 0.02], [0.22, -0.5 * l - 0.14 * a], [0.22, -0.5 * l + 0.1 - 0.14 * a], [0.4, -0.5 * l + 0.1]]); g.fill();
      }
    }
    // far end: wave hatching takes over from the tiles (Metamorphosis)
    const wave = smooth(far[0] - (far[1] - far[0]) * 0.6, far[0] + (far[1] - far[0]) * 0.3, Y) * (1 - smooth(far[1] - l * 3, far[1], Y));
    if (wave > 0.02) {
      g.globalAlpha = wave * 0.85; g.strokeStyle = paper; g.lineWidth = Math.max(1, sc * 0.05);
      for (let r = 0; r < 2; r++) {
        g.beginPath();
        for (let k = 0; k <= cols * 16; k++) {
          const xx = -cols / 2 + k / 16, q = P(C.x0 + xx, Y + (r - 0.5) * l * 0.5 + 0.1 * l * Math.sin(xx * 2.6 + j * 1.7 + r * 2.4) + 0.05 * l * Math.sin(xx * 6.1 + j));
          k ? g.lineTo(q[0], q[1]) : g.moveTo(q[0], q[1]);
        }
        g.stroke();
      }
    }
  }

  // ---------- 2. the solid sedans, far → near (black tiles only)
  for (let j = rows; j >= 0; j--) {
    const Y = front + (j - s) * l; if (Y < yMin || Y > vol[1]) continue;
    const v = 1 - smooth(vol[0], vol[1], Y); if (v < 0.02) continue;
    const a = 1 - smooth(shape[0], shape[1], Y), sc = P(C.x0, Y)[2], lw = Math.max(1.4, sc * 0.022);
    const plan = mix(tilePoly(l, a), sedan, smooth(0.05, 0.75, v));
    const zb = 0.5 * v, zr = 0.84 * v;                         // belt line and roof heights
    for (let i = 0; i < cols; i++) {
      if (((i + j + parity) & 1) !== 0 || skip.has(i + ',' + j)) continue;
      const x = X(i), id = i * 131 + j * 17 + seed, yN = Y - l / 2 - NOSE * 0.75;
      g.globalAlpha = 1; g.fillStyle = ink; g.strokeStyle = ink; g.lineWidth = 1;
      // body: the plan swept from the road to the belt line (side quads + lid), solid ink
      for (let k = 0; k < plan.length; k++) {
        const A = plan[k], B = plan[(k + 1) % plan.length], q = [P(x + A[0], Y + A[1], 0), P(x + B[0], Y + B[1], 0), P(x + B[0], Y + B[1], zb), P(x + A[0], Y + A[1], zb)];
        g.beginPath(); g.moveTo(q[0][0], q[0][1]); for (let m = 1; m < 4; m++) g.lineTo(q[m][0], q[m][1]); g.closePath(); g.fill(); g.stroke();
      }
      path(plan, Y, x, zb); g.fill();
      // cabin: belt quad → roof quad
      const cb = rrect(0.4, -0.1 * l, 0.37 * l), cr = rrect(0.32, 0.03 * l, 0.27 * l);
      for (let k = 0; k < cb.length; k++) {
        const A = cb[k], B = cb[(k + 1) % cb.length], A2 = cr[k], B2 = cr[(k + 1) % cr.length];
        const q = [P(x + A[0], Y + A[1], zb), P(x + B[0], Y + B[1], zb), P(x + B2[0], Y + B2[1], zr), P(x + A2[0], Y + A2[1], zr)];
        g.beginPath(); g.moveTo(q[0][0], q[0][1]); for (let m = 1; m < 4; m++) g.lineTo(q[m][0], q[m][1]); g.closePath(); g.fill(); g.stroke();
      }
      path(cr, Y, x, zr); g.fill();
      if (v < 0.06) continue;
      const da = clamp((v - 0.06) / 0.2);
      // white-line engraving: lid outline, bonnet creases, windscreen (paper glass with ink reflections), roof, lamps, grille
      g.globalAlpha = da; g.strokeStyle = paper; g.fillStyle = paper; g.lineWidth = lw;
      path(plan, Y, x, zb); g.stroke();
      seg(P(x - 0.2, yN + 0.3, zb), P(x - 0.24, Y - 0.12 * l, zb)); seg(P(x + 0.2, yN + 0.3, zb), P(x + 0.24, Y - 0.12 * l, zb));
      const w0 = [P(x - 0.36, Y - 0.09 * l, zb), P(x + 0.36, Y - 0.09 * l, zb), P(x + 0.29, Y + 0.04 * l, zr), P(x - 0.29, Y + 0.04 * l, zr)];
      g.beginPath(); g.moveTo(w0[0][0], w0[0][1]); for (let m = 1; m < 4; m++) g.lineTo(w0[m][0], w0[m][1]); g.closePath(); g.stroke();
      g.lineWidth = lw * 1.6;
      for (let k = 0; k < 2; k++) { const u = 0.5 + 0.2 * k; { const A = [lerp(w0[0][0], w0[1][0], u), lerp(w0[0][1], w0[1][1], u)], B = [lerp(w0[3][0], w0[2][0], u + 0.14), lerp(w0[3][1], w0[2][1], u + 0.14)]; seg([lerp(A[0], B[0], 0.2), lerp(A[1], B[1], 0.2)], [lerp(A[0], B[0], 0.8), lerp(A[1], B[1], 0.8)]); } }
      g.strokeStyle = paper; g.lineWidth = lw;
      path(cr, Y, x, zr); g.stroke();
      for (const sx of [-1, 1]) {                                // headlamps on the nose
        const h0 = P(x + sx * 0.36, yN + 0.13, 0.36 * v), h1 = P(x + sx * 0.2, yN + 0.03, 0.36 * v), h2 = P(x + sx * 0.2, yN + 0.03, 0.24 * v), h3 = P(x + sx * 0.36, yN + 0.13, 0.24 * v);
        g.beginPath(); g.moveTo(h0[0], h0[1]); g.lineTo(h1[0], h1[1]); g.lineTo(h2[0], h2[1]); g.lineTo(h3[0], h3[1]); g.closePath(); g.fill();
      }
      for (let k = 0; k < 3; k++) seg(P(x - 0.13, yN, (0.2 + 0.07 * k) * v), P(x + 0.13, yN, (0.2 + 0.07 * k) * v));   // grille
      seg(P(x - 0.42, yN + 0.16, 0.12 * v), P(x + 0.42, yN + 0.16, 0.12 * v));                                        // bumper
      // bonnet and roof hatching (white-line engraving), then a small starburst on each headlamp
      g.globalAlpha = da * 0.9; g.lineWidth = lw * 0.6;
      for (let k = 1; k < 5; k++) { const xx = -0.3 + 0.12 * k; seg(P(x + xx * 0.6, Y + 0.06 * l, zr), P(x + xx * 0.6, Y + 0.24 * l, zr)); }
      for (let k = 0; k < 2; k++) seg(P(x - 0.3 + 0.6 * k, Y + 0.39 * l, zb), P(x - 0.3 + 0.6 * k, Y + 0.48 * l, zb));
      const bm = (p.beams ?? 1) * da;
      if (bm > 0.01) {
        g.globalAlpha = bm; g.lineWidth = lw * 0.8;
        for (const sx of [-1, 1]) {
          const c1 = P(x + sx * 0.28, yN + 0.08, 0.3 * v), R1 = sc * 0.2 * bm;
          for (let k = 0; k < 8; k++) { const an = k / 8 * Math.PI * 2 + 0.2, rr = R1 * (k % 2 ? 0.55 : 1); seg([c1[0] + Math.cos(an) * R1 * 0.2, c1[1] + Math.sin(an) * R1 * 0.2], [c1[0] + Math.cos(an) * rr, c1[1] + Math.sin(an) * rr]); }
          for (let k = 0; k < 3; k++) {                       // light raking the road ahead
            const ang = (k - 1) * 0.12 + sx * 0.04, len = l * (0.3 + 0.15 * hash(id, k, sx + 2));
            seg(P(x + sx * 0.28, yN - 0.2, 0), P(x + sx * 0.28 + Math.sin(ang) * len, yN - 0.2 - Math.cos(ang) * len, 0));
          }
        }
      }
      // roof strobe: an engraved white starburst, flickering in a ripple across the fleet
      const st = (p.strobe ?? 1) * da;
      if (st > 0.01) {
        const c0 = P(x, Y + 0.13 * l, zr + 0.06 * v), ph2 = Math.floor(env.t * 12 + hash(id, 3) * 12) , on = 0.55 + 0.45 * hash(id, ph2 >> 1);
        const R = sc * 0.42 * st * on, rays = 14;
        g.globalAlpha = da; g.lineWidth = lw * 0.85; g.strokeStyle = paper;
        for (let k = 0; k < rays; k++) {
          const an = k / rays * Math.PI * 2 + hash(id, 9) * 0.4, rr = R * (k % 2 ? 0.55 : 1) * (0.8 + 0.4 * hash(id, k, ph2 >> 1));
          seg([c0[0] + Math.cos(an) * R * 0.16, c0[1] + Math.sin(an) * R * 0.16], [c0[0] + Math.cos(an) * rr, c0[1] + Math.sin(an) * rr * 0.8]);
        }
        g.beginPath(); g.arc(c0[0], c0[1], R * 0.13, 0, 7); g.fill();
      }
    }
  }
  g.restore();
}
