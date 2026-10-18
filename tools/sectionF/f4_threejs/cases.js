// F4 camera / fall cases for the Bean mirror check. World: metres, y up, the Bean centred on the origin, its 20 m length
// along x, its front face (z = +6.5) toward the camera. Shared by index.html (browser) and render.mjs (node).
//
// A case: a camera at `cam0` pitched down `tilt` degrees, focal `focal` (in image heights; 1.296 = 1400 px at 1920x1080,
// 69 deg horizontal). Her head sits on the camera ray through image point `px` (1920x1080 pixels) at `dh` metres. Her
// body is straight, head down, feet up (`bodyUp`), facing the camera horizontally (or away from it). She moves along
// `path` ('ray' = straight away from the camera through her head, as the footage does: her head stays put in the frame
// while the Bean swells round it; 'down' = straight down) and the camera keeps its offset from her. `dist` = metres
// left between her head and the mirror along the path.

const deg = Math.PI / 180;
const sub = (a, b) => a.map((v, i) => v - b[i]), add = (a, b) => a.map((v, i) => v + b[i]);
const mul = (a, s) => a.map(v => v * s), dot = (a, b) => a.reduce((s, v, i) => s + v * b[i], 0);
const norm = a => mul(a, 1 / Math.hypot(...a));
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];

export function beanF(p) {           // same implicit as the shader
  const q = [p[0] / 10, (p[1] - 4.4) / 5.6, p[2] / 6.5], n = 2.6;
  let d = (Math.abs(q[0]) ** n + Math.abs(q[1]) ** n + Math.abs(q[2]) ** n) ** (1 / n) - 1;
  d *= 4;
  const a = (Math.hypot(p[0] / 7, p[1] / 3.7) - 1) * 3.7;
  const h = Math.min(1, Math.max(0, 0.5 - 0.5 * (d + a) / 0.8));
  d = d * (1 - h) + (-a) * h + 0.8 * h * (1 - h);
  return Math.max(d, -p[1]);
}
export function beanN(p) {
  const e = 0.002, g = [0, 1, 2].map(i => { const a = p.slice(), b = p.slice(); a[i] += e; b[i] -= e; return beanF(a) - beanF(b); });
  return norm(g);
}
function hitBean(o, d) {             // first crossing along a ray (fine steps, then bisection)
  let t = 0, prev = beanF(o);
  for (let i = 0; i < 20000; i++) {
    const t1 = t + 0.01, v = beanF(add(o, mul(d, t1)));
    if (v < 0 && prev > 0) { let a = t, b = t1; for (let k = 0; k < 40; k++) { const m = (a + b) / 2; if (beanF(add(o, mul(d, m))) > 0) a = m; else b = m; } return b; }
    prev = v; t = t1;
  }
  return null;
}

export function camBasis(pos, tilt, yaw = 0) {
  const f = [Math.sin(yaw) * Math.cos(tilt * deg), -Math.sin(tilt * deg), -Math.cos(yaw) * Math.cos(tilt * deg)];
  const r = norm(cross(f, [0, 1, 0])), u = cross(r, f);
  return { pos, f, r, u };
}

// Her pose (v10b, Jade 2026-10-18: "her back is arched"): back to the camera, head first, the spine extended so the head
// is thrown back and her face turns down and back toward the camera (that is why the camera sees her face under her
// crown, the right way up), legs bowed slightly back, arms out in a T. Angles in degrees, each bending further toward
// her back: a1 belly, a2 chest, a3 neck, a4 head; l1 thighs, l2 shins; arm = arms swept toward her feet.
export const ARCH = { a1: 5, a2: 10, a3: 25, a4: 100, l1: 6, l2: 6, arm: 22 };
// front3 (Jade's variant): back barely arched, head in line with the spine and a touch tucked, legs nearly straight; the
// camera sees the back of her head and the mirror her face.
export const ARCH3 = { a1: 2, a2: 3, a3: 0, a4: -8, l1: 2, l2: 2, arm: 22 };

export function body(P = ARCH) {
  const r = d => d * deg;
  const up = f => [0, -Math.cos(f), -Math.sin(f)];        // headward direction, bent back by f
  const fn = f => [0, -Math.sin(f), Math.cos(f)];         // its front normal
  const dn = f => [0, Math.cos(f), -Math.sin(f)];         // footward direction, bent back by f
  const dnN = f => [0, Math.sin(f), Math.cos(f)];
  const f1 = r(P.a1), f2 = f1 + r(P.a2), f3 = f2 + r(P.a3), f4 = f3 + r(P.a4);
  const J = [];
  J[4] = [0, 0, 0];                                      // pelvis
  J[3] = add(J[4], mul(up(f1), 0.24));                    // waist
  J[2] = add(J[3], mul(up(f2), 0.27));                    // shoulders
  J[1] = add(J[2], mul(up(f3), 0.16));                    // skull base (a long drawn neck)
  J[0] = add(add(J[1], mul(up(f4), 0.1)), mul(fn(f4), 0.03));   // head centre
  const g1 = r(P.l1), g2 = g1 + r(P.l2);
  for (const [h, k, a, t, sx] of [[5, 6, 7, 13, 1], [8, 9, 10, 14, -1]]) {
    J[h] = add(J[4], [0.09 * sx, 0.06, 0]);
    J[k] = add(J[h], mul(dn(g1), 0.44));
    J[a] = add(J[k], mul(dn(g2), 0.42));
    J[t] = add(J[a], mul(dnN(g2), 0.14));
  }
  const aa = r(P.arm);
  J[11] = add(J[2], [0.82 * Math.cos(aa), 0.82 * Math.sin(aa), 0]);     // LEFT hand
  J[12] = add(J[2], [-0.82 * Math.cos(aa), 0.82 * Math.sin(aa), 0]);    // RIGHT hand
  const o = J[0];
  return { J: J.map(j => sub(j, o)), hf: fn(f4), hu: up(f4), tn: [fn(f3), fn(f2), fn(f1)], ln: dnN(g2),
           R: [0.115, 0.055, 0.12, 0.11, 0.11, 0.085, 0.085, 0.07, 0.085, 0.085, 0.07, 0.075, 0.075, 0.06, 0.06] };
}

export const CASES = {
  A: { label: 'as drawn (fit to frame 0): camera 5.8 m up, 22 m from the Bean, level; she moves along its line of sight onto the front face',
       cam0: [0, 5.8, 22], tilt: -4, focal: 1.15, px: [958, 575], dh: 4.2, path: 'ray', facing: 'away' },
  B: { label: 'higher camera: 13 m up, 10 deg down; she moves along its line of sight onto the upper shoulder',
       cam0: [0, 13, 21], tilt: 10, focal: 1.15, px: [958, 575], dh: 4.2, path: 'ray', facing: 'away' },
  A3: { label: 'front3: as A, her back barely arched and her head in line with her spine (Jade 2026-10-18)',
       cam0: [0, 5.8, 22], tilt: -4, focal: 1.15, px: [958, 575], dh: 4.2, path: 'ray', facing: 'away', arch: ARCH3 },
  C: { label: 'floor-like (the keyframe prompt): camera 18 m up, 50 deg down; she drops straight down onto the top',
       cam0: [0, 18, 4], tilt: 50, focal: 1.15, px: [958, 575], dh: 4.2, path: 'down', facing: 'away' },
};
// F4 source frames for the fractions of the start distance left (from the Bean's widths in the F4 matte: the camera's
// distance to the Bean goes as 1/width; extrapolated past frame 60, where the Bean leaves the frame; contact ~frame 77)
export const FRAMES = [[0, 1.0], [20, 0.78], [40, 0.51], [52, 0.33], [60, 0.21], [70, 0.07], [76, 0.013]];


const cache = new Map();
export function pose(C, dist) {
  let base = cache.get(C);
  if (!base) {
    const cam = camBasis(C.cam0, C.tilt);
    const uv = [(C.px[0] - 960) / 1080, -(C.px[1] - 540) / 1080];
    const ray = norm(add(add(mul(cam.f, C.focal), mul(cam.r, uv[0])), mul(cam.u, uv[1])));
    const head0 = add(C.cam0, mul(ray, C.dh));
    const dir = C.path === 'down' ? [0, -1, 0] : ray;
    const t = hitBean(head0, dir);
    const contact = add(head0, mul(dir, t));
    const bU = [0, 1, 0];
    let bF = norm([C.cam0[0] - head0[0], 0, C.cam0[2] - head0[2]]);
    if (C.facing === 'away') bF = mul(bF, -1);
    const bL = cross(mul(bU, -1), bF);
    const bd = body(C.arch || ARCH);
    // how far her body reaches ahead of her head centre along the path (the arched belly leads): dist is from there
    const ext = Math.max(...bd.J.map((j, i) => dot(add(add(mul(bL, j[0]), mul(bU, j[1])), mul(bF, j[2])), dir) + bd.R[i]));
    base = { cam, head0, dir, contact, t0: t, bU, bF, bL, nC: beanN(contact), body: bd, ext };
    cache.set(C, base);
  }
  if (dist < 0) dist = base.t0 - base.ext;            // < 0: the start of the shot (her head dh from the camera)
  const head = sub(base.contact, mul(base.dir, dist + base.ext));
  const off = sub(C.cam0, base.head0);
  const cam = { ...base.cam, pos: add(head, off), focal: C.focal };
  return { cam, head, bU: base.bU, bF: base.bF, bL: base.bL, contact: base.contact, startDist: base.t0 - base.ext, nContact: base.nC,
           body: base.body };
}

// What the mirror sees of her: the camera ray (down her centre column) whose reflection passes closest to the middle of
// her torso. Returns, in her local frame (x her left, y toward her feet, z her front): the torso anchor, the view
// direction fL (from the mirror toward her), the plane normal nL, and the picture axes e1L (right) and e2L (up) of a
// viewer looking along fL with world-up up. The comp lays a picture of her on that plane (mode 3), and the pose
// reference for that picture is an orthographic view along fL (mode 4).
export function mirrorView(C, frac) {
  const P = pose(C, frac * pose(C, -1).startDist);
  const { cam } = P;
  const toW = v => [0, 1, 2].map(i => P.bL[i] * v[0] + P.bU[i] * v[1] + P.bF[i] * v[2]);
  const toL = v => [dot(v, P.bL), dot(v, P.bU), dot(v, P.bF)];
  const J = P.body.J;
  const anchorL = mul(add(J[2], J[4]), 0.5);
  const A = add(P.head, toW(anchorL));
  let best = null;
  for (let py = 540; py < 1080; py += 1) {
    const uv = [0, -(py - 540) / 1080];
    const d = norm(add(mul(cam.f, cam.focal), mul(cam.u, uv[1])));
    const t = hitBean(cam.pos, d);
    if (t == null) continue;
    const Pb = add(cam.pos, mul(d, t)), n = beanN(Pb);
    const r = sub(d, mul(n, 2 * dot(d, n)));
    const w = sub(A, Pb), along = dot(w, r);
    if (along <= 0) continue;
    const miss = Math.hypot(...sub(w, mul(r, along)));
    if (!best || miss < best.miss) best = { miss, py, r, Pb };
  }
  const f = best.r;
  const e1 = norm(cross(f, [0, 1, 0])), e2 = cross(e1, f);
  return { anchorL, fL: toL(f), nL: toL(mul(f, -1)), e1L: toL(e1), e2L: toL(e2), py: best.py, miss: best.miss, mirror: best.Pb };
}
