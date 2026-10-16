// v9 round 3 (Jade 0:24 / 0:27): D2 + D3 as ONE three.js scene. Pure math, no three.js: the scene module
// (scene.js) and the track exporter (tracks.mjs, Node) both read the same rig, so the corner tracks the engine pins the
// lyric, the plate and the etch onto are exactly the scene's own projections.
//
// Car frame (everything is drawn in the car's frame; the world streams past): x = car's right, y = up (road at 0),
// z = BACKWARD (+z toward the trunk; the car drives toward -z). Metres. Song time s in seconds.
//
// Staging: Jade's white Acura (left-hand drive) southbound on Lake Shore Drive at night, in the second lane. Camera in
// the passenger seat (seat slid back ~40 cm), looking across her at the driver's door mirror. The mirror is aimed for
// HER eye (she sees straight back, a sliver of her own flank); from the passenger seat the same glass shows the next
// lane to the left, where the TVA sedan follows. Far behind on the left, over the lakefront, a bulb billboard.

export const S0 = 23.16, S1 = 25.34, S2 = 28.40, FPS = 24, W = 1920, H = 1080;
// round 5: the clip is rendered on the film's 24 fps grid: clip frame n = song time (556 + n) / 24 (23.16 itself is 0.16 frame off it)
export const CLIP0 = 556 / 24;
export const SPEED = 20;                       // m/s (45 mph)

// ---- tiny vector kit ([x, y, z] arrays)
export const v3 = (x, y, z) => [x, y, z];
export const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
export const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
export const mul = (a, k) => [a[0] * k, a[1] * k, a[2] * k];
export const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
export const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
export const norm = (a) => mul(a, 1 / Math.hypot(a[0], a[1], a[2]));
export const lerp3 = (a, b, k) => [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k];
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, k) => a + (b - a) * k;
export const smooth = (a, b, x) => { const t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t); };
export const smoother = (a, b, x) => { const t = clamp((x - a) / (b - a)); return t * t * t * (t * (t * 6 - 15) + 10); };

// ---- round 6: her face, by film frame (k = round(s * 24)): one blink while "A shadow" is sung, then a lip press as
// "chasing" lands, both mid-shot (no cut nearby), gaze on the mirror throughout. Variants: tools/v9/d23/r6_frames.py
export const FACE_KEYS = { 579: 'half', 580: 'blink', 581: 'blink', 582: 'half',
  591: 'press50', 592: 'press100', 593: 'press100', 594: 'press100', 595: 'press100', 596: 'press100', 597: 'press100',
  598: 'press100', 599: 'press100', 600: 'press100', 601: 'press50' };
export const faceAt = (s) => FACE_KEYS[Math.round(s * 24)] || 'open';

// ---- the car (Jade's white 2001 Acura TL, left-hand drive)
export const CAR = {
  halfW: 0.91, doorIn: -0.80, belt: 0.96, roof: 1.37, roofOut: 1.42,
  aBase: [-0.88, 0.97, -1.02], aTop: [-0.74, 1.37, -0.32],   // A-pillar (window side), base -> roof
  bZ: 0.62,                                                  // B-pillar
  shieldBase: { y: 0.98, z: -1.02 },                         // windshield foot
};
export const EYE_DRIVER = [-0.37, 1.13, 0.0];               // Jade's eyes (between them)
export const HEAD = [-0.39, 1.12, 0.07];                     // her head centre
export const WHEEL = { c: [-0.37, 0.86, -0.43], r: 0.19, n: norm([0, 0.42, 1]) };   // steering wheel (normal toward her)

// ---- camera: the passenger's eye (round 4: in the passenger seat beside her, level with her head, looking LEFT across
// her at her side window, as D6 does; the camera only rotates and zooms, it never moves, so her plate stays exact)
export const CAM = [0.50, 1.10, -0.12];
// aims are given as a direction from the camera: deg forward of straight-left, deg up
const dirAim = (fwdDeg, upDeg) => { const a = fwdDeg * Math.PI / 180, e = upDeg * Math.PI / 180; return add(CAM, [-Math.cos(a) * Math.cos(e), Math.sin(e), -Math.sin(a) * Math.cos(e)]); };
// round 4: the plate (media/shots/D23/plate_r4_e2.png, 2752 x 1536) was drawn by the model in D6's composition; this is
// the camera it was fitted to (tools/v9/d23 round-4 notes: her head, the window's front corner): 6.5 deg forward of
// straight left, 9.25 deg down, vfov 58. Every framing below is a rotation + zoom of it, so the plate stays exact.
export const PLATE_IMG = { w: 2752, h: 1536 };
export const GUIDE = { fov: 58, aim: dirAim(6.5, -9.25) };
// plate pixel -> world point at distance `dist` from the camera (along that pixel's ray)
export function platePoint(px, py, dist) {
  const f0 = norm(sub(GUIDE.aim, CAM)), r0 = norm(cross(f0, [0, 1, 0])), u0 = cross(r0, f0);
  const f = (PLATE_IMG.h / 2) / Math.tan(GUIDE.fov * Math.PI / 360);
  const d = norm(add(f0, add(mul(r0, (px - PLATE_IMG.w / 2) / f), mul(u0, -(py - PLATE_IMG.h / 2) / f))));
  return add(CAM, mul(d, dist));
}
const aimPx = (px, py) => platePoint(px, py, 1);

// ---- the driver's door mirror: housing on an arm from the sail at the front of her window, flat glass
// the glass centre sits in the clear window just left of the plate's A-pillar and above the wheel rim, 1.1 m out to the
// side (round 3's mirror plane); its arm runs right, behind the pillar, to the door skin
// the point on a plate pixel's ray where world x = xw (the door skin plane etc.)
function platePointX(px, py, xw) { const d = sub(platePoint(px, py, 1), CAM); return add(CAM, mul(d, (xw - CAM[0]) / d[0])); }
const M_C = platePointX(1570, 568, -1.10);
export const ARM0 = platePointX(1800, 610, -0.93);   // on the door skin, hidden behind the plate's A-pillar
// round 4: the glass is aimed for HER: she sees straight back, a hair outward and down (as a driver sets it). From the
// passenger seat the same glass then shows the lanes further out (the far-left lane, where the TVA sedan comes up).
const DRIVER_LOOK = norm([0.10, -0.056, 1]);
const M_N = norm(add(norm(sub(EYE_DRIVER, M_C)), DRIVER_LOOK));
const M_U = norm(cross([0, 1, 0], M_N));                       // glass right, seen from the front
const M_V = cross(M_N, M_U);                                    // glass up
export const MIRROR = { c: M_C, n: M_N, u: M_U, v: M_V, w: 0.24, h: 0.155, r: 0.035 };
// round 5 (Jade: the rectangle is wrong): the 1999-2003 Acura TL door mirror outline, from photos of the real car
// (docs/revisions/v9/fix_2_r5_ref_*.jpg). Glass-local (a, b) in [-1, 1]^2, a = +1 at the INBOARD end (toward the car;
// M_U points inboard), b = +1 at the top: a tall, squarish inboard end, a near-flat top running out, then one big
// rounded sweep at the outboard end, the bottom edge rising toward it (the cap tapers outboard, a teardrop corner).
function bez(p0, p1, p2, p3, n) { const o = []; for (let i = 1; i <= n; i++) { const t = i / n, u = 1 - t; o.push([u * u * u * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t * t * t * p3[0], u * u * u * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t * t * t * p3[1]]); } return o; }
export const TL_OUTLINE = (() => {
  const P = [[0.90, -1.0]];
  P.push(...bez([0.90, -1.0], [0.97, -1.0], [1.0, -0.96], [1.0, -0.88], 6));     // inboard bottom corner (tight)
  P.push(...bez([1.0, -0.88], [1.0, -0.2], [1.0, 0.5], [1.0, 0.76], 6));          // inboard end, upright
  P.push(...bez([1.0, 0.76], [1.0, 0.93], [0.92, 1.0], [0.76, 1.0], 8));          // inboard top corner
  P.push(...bez([0.76, 1.0], [0.3, 1.0], [-0.1, 0.99], [-0.38, 0.95], 10));       // top edge, near flat, a touch falling
  P.push(...bez([-0.38, 0.95], [-0.86, 0.90], [-1.0, 0.55], [-1.0, 0.06], 16));   // outboard sweep, top half
  P.push(...bez([-1.0, 0.06], [-1.0, -0.42], [-0.82, -0.74], [-0.42, -0.80], 16)); // outboard sweep, into the rising bottom
  P.push(...bez([-0.42, -0.80], [0.0, -0.86], [0.5, -0.97], [0.90, -1.0], 10));    // bottom edge, rising outboard
  return P;   // closed (last point = first)
})();
export function inGlass(a, b) {   // point-in-polygon on TL_OUTLINE
  let c = false; const P = TL_OUTLINE;
  for (let i = 0, j = P.length - 1; i < P.length; j = i++) {
    const [xi, yi] = P[i], [xj, yj] = P[j];
    if ((yi > b) !== (yj > b) && a < (xj - xi) * (b - yi) / (yj - yi) + xi) c = !c;
  }
  return c;
}
// a point on the glass from glass-local (a, b) in [-1, 1]^2 (a: right, b: up, as seen from the front)
export const glassPt = (a, b) => add(M_C, add(mul(M_U, a * MIRROR.w / 2), mul(M_V, b * MIRROR.h / 2)));
// mirror image of a world point through the glass plane
export const reflect = (p) => sub(p, mul(M_N, 2 * dot(sub(p, M_C), M_N)));
// what HER eye sees at the glass centre (a sanity check printed by tracks.mjs: straight back, a little down)
export const driverView = () => { const d = norm(sub(EYE_DRIVER, M_C)); return sub(mul(M_N, 2 * dot(d, M_N)), d); };
// what the CAMERA sees at the glass centre
export const camView = () => { const d = norm(sub(CAM, M_C)); return sub(mul(M_N, 2 * dot(d, M_N)), d); };

// ---- camera move: one take across D2 and D3. vfov (deg, full 16:9 frame) and the look-at point, keyed on song time.
// D2: a medium two-shot (her profile, both hands on the wheel in front of her, her side window with the mirror beyond
// her face) easing in to a tighter two-shot of her profile and the mirror, landing as "A" is sung (23.97). D3: a zoom
// into the glass, the sedan and its plate filling it by 27.3.
const ease = (k) => k * k * (3 - 2 * k);
const easeIO3 = (k) => (k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2);
const FOV_OPEN = 44, FOV_TWO = 23, FOV_TWO_END = 19.5, FOV_GLASS = 8.0;
const AIM_OPEN = aimPx(1260, 740);
const AIM_TWO = aimPx(1240, 545);
const AIM_TWO_END = aimPx(1290, 555);
export function camAt(s) {
  let fov, aim;
  if (s < S1) {
    const k = easeIO3(clamp((s - S0) / (24.0 - S0)));
    const creep = clamp((s - 24.0) / (S1 - 24.0));
    fov = Math.exp(lerp(Math.log(FOV_OPEN), Math.log(FOV_TWO), k));
    fov = Math.exp(lerp(Math.log(fov), Math.log(FOV_TWO_END), creep));
    aim = lerp3(lerp3(AIM_OPEN, AIM_TWO, k), AIM_TWO_END, creep);
  } else {
    const k = ease(ease(clamp((s - S1) / (27.30 - S1))));
    const creep = clamp((s - 27.30) / (S2 - 27.30));
    // zoom on a log scale so the push feels even; the aim slides onto the glass centre
    fov = Math.exp(lerp(Math.log(FOV_TWO_END), Math.log(FOV_GLASS), k)) - 0.3 * creep;
    aim = lerp3(AIM_TWO_END, add(M_C, mul(M_V, -0.004)), Math.min(1, k * 1.2));
  }
  return camFrom(aim, fov, s, Math.tan(fov * Math.PI / 360) / Math.tan(15 * Math.PI / 360));
}
function camFrom(aim, fov, s, sc) {
  // a breath of hand-held drift (the passenger's head), deterministic, tiny next to the zoom
  const j = sc * (0.0025 * Math.sin(s * 1.7 + 0.4) + 0.0012 * Math.sin(s * 4.1 + 1.3));
  const jy = sc * (0.0018 * Math.sin(s * 2.3 + 2.0) + 0.0008 * Math.sin(s * 5.3));
  const pos = CAM, f0v = norm(sub(aim, pos));
  const r0 = norm(cross(f0v, [0, 1, 0])), u0 = cross(r0, f0v);
  const fwd = norm(add(f0v, add(mul(r0, j), mul(u0, jy))));
  const right = norm(cross(fwd, [0, 1, 0])), up = cross(right, fwd);
  return { pos, fwd, right, up, fov };
}
// the plate's camera (GUIDE): the card is registered to THIS frustum: the card is registered to THIS frustum (no drift), whatever the move does later
export function guideCam() { return camFrom(GUIDE.aim, GUIDE.fov, S0, 0); }
// world point -> design px {x, y (from top), z (view depth)}
export function project(p, cam) {
  const d = sub(p, cam.pos), z = dot(d, cam.fwd);
  const f = (H / 2) / Math.tan(cam.fov * Math.PI / 360);
  return { x: W / 2 + f * dot(d, cam.right) / z, y: H / 2 - f * dot(d, cam.up) / z, z };
}

// ---- the world streaming past (car frame)
export const worldZ = (z0, s) => z0 + SPEED * (s - S0);
// the TVA sedan: the lane to the left, closing from ~60 m to ~21 m behind the mirror, then holding station
export const SEDAN = { x: -7.3, len: 5.15, w: 1.84 };
export function sedanAt(s) {
  const k = smoother(S0, 27.55, s);
  const d = lerp(70, 15.2, k) + 0.2 * Math.sin(s * 0.9);
  // round 4: it comes up in the left lane, then edges right toward the lane line to sit on her tail (and into her mirror)
  const x = lerp(SEDAN.x, -5.25, smooth(25.9, 27.3, s)) - 0.06 * Math.sin(s * 0.7 + 1);
  return { front: [x, 0, M_C[2] + d], d };
}
// the sedan is an engraved impostor card (media/shots/D23/sedan_a_rgba.png, nano-banana) standing at its front bumper,
// facing -z (seen ~10 deg off its axis in the mirror). Scale from its blank plate: a US plate, 12 x 6.5 in.
export const SEDAN_IMG = { size: [2752, 1536], cx: 1390, ground: 1376, plate: [1551, 964, 1803, 1103],   // round 5: the drawn plate measured (pale field + its thin frame)
  lamps: [[1185, 810], [2070, 810]] };
export const PLATE = { w: 0.305, h: 0.305 * (1102 - 966) / (1802 - 1550) };
export const SEDAN_PPM = (1802 - 1550) / 0.305;             // image px per metre on the card
export function plateCorners(s) {   // world corners TL, TR, BR, BL as seen from behind it (i.e. facing the sedan)
  const f = sedanAt(s).front, z = f[2], I = SEDAN_IMG, k = SEDAN_PPM;
  // image x grows toward the viewer's right = world -x (the card faces -z)
  const X = (px) => f[0] - (px - I.cx) / k, Y = (py) => (I.ground - py) / k;
  // seen from the front of the sedan (looking +z), its left is -x... its plate's own left/right: the viewer facing the
  // car sees TL at +x? No: a viewer at -z looking toward +z has right = -x. So the plate's TL (viewer's top-left) is +x.
  const [x0, y0, x1, y1] = I.plate;
  return [[X(x0), Y(y0), z], [X(x1), Y(y0), z], [X(x1), Y(y1), z], [X(x0), Y(y1), z]];
}
// the billboard: two bulb panels on a lattice tower on the lakefront, far behind on the left
export const BILL = { x: -85, z0: 262, y0: 0.8, w: 20, ph: 4.7, gap: 0.6 };   // y0: bottom of the lower panel
export function billPanels(s) {
  const z = worldZ(BILL.z0, s), hw = BILL.w / 2;
  // seen from the front (it faces -z, toward the road ahead / us), the viewer's right is -x... the face looks toward -z,
  // a viewer at -z looking +z has right = -x, so TL is at +x
  const q = (yb, yt) => [[BILL.x + hw, yt, z], [BILL.x - hw, yt, z], [BILL.x - hw, yb, z], [BILL.x + hw, yb, z]];
  const yb1 = BILL.y0, yt1 = yb1 + BILL.ph, yb2 = yt1 + BILL.gap, yt2 = yb2 + BILL.ph;
  return { top: q(yb2, yt2), bot: q(yb1, yt1) };
}
// lyric etch on the glass itself (glass-local box): the bottom band, under the sedan (round 4: its plate sits mid-glass)
export const ETCH = { a0: -0.80, a1: 0.0, out: [0.44, 0.74], in: [0.52, 0.88] };   // round 5: two lines ("me I couldn't / place", left-aligned) in the top-left sky of the TL glass, outboard of the billboard and above the sedan roof: [bottom, top] at the outboard (a0) and inboard (a1) ends
