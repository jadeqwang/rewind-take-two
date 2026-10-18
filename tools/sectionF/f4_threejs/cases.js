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

export const CASES = {
  A: { label: 'as drawn (fit to frame 0): camera 5.8 m up, 22 m from the Bean, level; she moves along its line of sight onto the front face',
       cam0: [0, 5.8, 22], tilt: -4, focal: 1.15, px: [958, 575], dh: 4.2, path: 'ray', facing: 'camera' },
  B: { label: 'higher camera: 13 m up, 10 deg down; she moves along its line of sight onto the upper shoulder',
       cam0: [0, 13, 21], tilt: 10, focal: 1.15, px: [958, 575], dh: 4.2, path: 'ray', facing: 'camera' },
  C: { label: 'floor-like (the keyframe prompt): camera 18 m up, 50 deg down; she drops straight down onto the top',
       cam0: [0, 18, 4], tilt: 50, focal: 1.15, px: [958, 575], dh: 4.2, path: 'down', facing: 'camera' },
  D: { label: 'case A, but she faces the Bean (the camera would see her back)',
       cam0: [0, 5.8, 22], tilt: -4, focal: 1.15, px: [958, 575], dh: 4.2, path: 'ray', facing: 'away' },
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
    base = { cam, head0, dir, contact, t0: t, bU, bF, bL, nC: beanN(contact) };
    cache.set(C, base);
  }
  if (dist < 0) dist = base.t0 - 0.12;                // < 0: the start of the shot (her head dh from the camera)
  const head = sub(base.contact, mul(base.dir, dist + 0.12));
  const off = sub(C.cam0, base.head0);
  const cam = { ...base.cam, pos: add(head, off), focal: C.focal };
  return { cam, head, bU: base.bU, bF: base.bF, bL: base.bL, contact: base.contact, startDist: base.t0 - 0.12, nContact: base.nC };
}
