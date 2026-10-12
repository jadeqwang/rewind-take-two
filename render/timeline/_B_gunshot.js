// _B_gunshot.js (v4c gunfire, G1): one chest-high lead shot. Jade: "they should be aiming for where the torso would have
// been if she hadn't zagged". A ruled dashed ink line draws from the muzzle THROUGH the empty chest-high point she
// left (params.aim) and on a little past it, fading (params.tail); on the shot frame a 2-frame starburst at the muzzle;
// if given, a small turf burst far beyond, where the round lands (params.land). Same ink language as b_tracemiss
// (render/engine/modules/b_tracemiss.js). Canvas2D, a pure function of the layer clock.
//   params.at (layer-local shot time), origin / aim / land: lt => [x, y] design px (land may be null), lead .33,
//   tail .3 (share of the muzzle->aim length drawn past the aim point), size 1, width 8, ink, paper
const F = 24, TAU = Math.PI * 2;
const hash = (a, b = 0) => { const x = Math.sin(a * 127.1 + b * 311.7) * 43758.5453; return x - Math.floor(x); };

function starburst(g, x, y, R, dir, seed, ink, paper) {
  const n = 9, pts = [];
  for (let i = 0; i < n * 2; i++) {
    const a = dir + (i / (n * 2)) * TAU, tip = i % 2 === 0, along = Math.cos(a - dir);
    const r = tip ? R * (0.62 + 0.5 * hash(seed, i)) * (1 + 0.55 * Math.max(0, along)) : R * (0.22 + 0.1 * hash(seed, i + 40));
    pts.push([x + Math.cos(a) * r, y + Math.sin(a) * r]);
  }
  g.lineJoin = 'miter'; g.beginPath(); pts.forEach((q, i) => (i ? g.lineTo(q[0], q[1]) : g.moveTo(q[0], q[1]))); g.closePath();
  g.fillStyle = paper; g.fill(); g.strokeStyle = ink; g.lineWidth = 3.2; g.stroke();
  for (let i = 0; i < n * 2; i += 2) {
    const a = dir + (i / (n * 2)) * TAU, tr = Math.hypot(pts[i][0] - x, pts[i][1] - y);
    g.lineWidth = 1.6; g.beginPath(); g.moveTo(x + Math.cos(a) * R * 0.2, y + Math.sin(a) * R * 0.2); g.lineTo(x + Math.cos(a) * tr * 0.62, y + Math.sin(a) * tr * 0.62); g.stroke();
  }
  g.fillStyle = ink; g.beginPath(); g.arc(x, y, R * 0.07, 0, TAU); g.fill();
}

export function draw(lt, env) {
  const g = env.ctx, p = env.params, ink = p.ink || '#0b0b0c', paper = p.paper || '#fbf8f1';
  const at = p.at, lead = p.lead ?? 0.33, Z = p.size ?? 1, w = (p.width ?? 8) * Z, dt = lt - at, fr = dt * F;
  if (dt < -lead) return;
  const O = env.val(p.origin), A = env.val(p.aim), tail = p.tail ?? 0.3;
  const E = [A[0] + (A[0] - O[0]) * tail, A[1] + (A[1] - O[1]) * tail], dir = Math.atan2(A[1] - O[1], A[0] - O[0]);
  if (fr < 2) {
    const u = Math.min(1, (lt - (at - lead)) / lead), e = 1 - (1 - Math.min(1, u * 1.6)) ** 2;    // draws out, then holds
    const al = dt < 0 ? 1 : fr < 1 ? 0.7 : 0.3;
    const seg = (a, b, alpha) => {
      g.globalAlpha = al * alpha * 0.9; g.strokeStyle = paper; g.lineWidth = w + 7 * Z; g.setLineDash([]);
      g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b[0], b[1]); g.stroke();
      g.globalAlpha = al * alpha; g.strokeStyle = ink; g.lineWidth = w; g.setLineDash([22 * Z, 13 * Z]);
      g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b[0], b[1]); g.stroke(); g.setLineDash([]);
    };
    g.save(); g.lineCap = 'butt';
    const total = 1 + tail, reach = e * total;                         // in units of |O -> A|
    const P = k => [O[0] + (A[0] - O[0]) * k, O[1] + (A[1] - O[1]) * k];
    seg(O, P(Math.min(1, reach)), 1);
    if (reach > 1) seg(A, P(reach), 0.45);                              // past the empty spot: the round goes on
    // where it is aimed: a small surveyor's ring on the chest-high spot
    const c = 16 * Z; g.globalAlpha = al; g.lineWidth = w * 0.7; g.strokeStyle = ink; g.lineCap = 'round';
    g.beginPath(); g.arc(A[0], A[1], c, 0, TAU); g.moveTo(A[0] - c * 1.5, A[1]); g.lineTo(A[0] + c * 1.5, A[1]); g.moveTo(A[0], A[1] - c * 1.5); g.lineTo(A[0], A[1] + c * 1.5); g.stroke();
    g.restore();
  }
  if (dt < 0) return;
  if (fr < 2) { g.save(); starburst(g, O[0], O[1], 110 * Z * (fr < 1 ? 1 : 0.62), dir + (fr < 1 ? 0 : 0.35), 31 + at * 7, ink, paper); g.restore(); }
  const L = p.land ? env.val(p.land) : null;
  if (L && dt > 0.04 && dt < 0.5) {                                     // far beyond: a small kick of turf
    const t2 = dt - 0.04; g.save(); g.fillStyle = ink; g.globalAlpha = Math.max(0, 1 - (t2 / 0.46) ** 2);
    for (let i = 0; i < 9; i++) {
      const a = -Math.PI / 2 + (hash(at, i) - 0.5) * 1.6, v = (160 + 220 * hash(at, i + 9)) * Z;
      const x = L[0] + Math.cos(a) * v * t2, y = L[1] + Math.sin(a) * v * t2 + 900 * Z * t2 * t2, s = (4 + 6 * hash(at, i + 18)) * Z;
      g.beginPath(); g.moveTo(x - s, y); g.lineTo(x + s, y - s * 0.3); g.lineTo(x - s * 0.5, y + s * 0.5); g.closePath(); g.fill();
    }
    g.restore();
  }
}
