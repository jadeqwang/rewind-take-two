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

import { TL_OUTLINE_R7 } from './tl_outline_r7.js';   // round 7: the drawn housing's glass outline (housing_r7.py)
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
// round 7: the wheel at a real TL height (its top rim at the dash top, ~0.97, below the belt line; round 4 had it 8 cm
// higher, which put the drawn rim over the window's front lower corner, where the mirror really is)
export const WHEEL = { c: [-0.37, 0.795, -0.45], r: 0.19, n: norm([0, 0.42, 1]) };   // steering wheel (normal toward her)

// ---- camera: the passenger's eye (round 4: in the passenger seat beside her, level with her head, looking LEFT across
// her at her side window, as D6 does; the camera only rotates and zooms, it never moves, so her plate stays exact)
// round 7: 23 cm further forward in the passenger seat (and a touch inboard and up), so the steering wheel sits LEFT of
// and below the window's front lower corner, where the door mirror really is: a clean sightline for the push into the glass
export const CAM = [0.45, 1.12, -0.35];
// aims are given as a direction from the camera: deg forward of straight-left, deg up
const dirAim = (fwdDeg, upDeg) => { const a = fwdDeg * Math.PI / 180, e = upDeg * Math.PI / 180; return add(CAM, [-Math.cos(a) * Math.cos(e), Math.sin(e), -Math.sin(a) * Math.cos(e)]); };
// round 4: the plate (media/shots/D23/plate_r4_e2.png, 2752 x 1536) was drawn by the model in D6's composition; this is
// the camera it was fitted to (tools/v9/d23 round-4 notes: her head, the window's front corner): 6.5 deg forward of
// straight left, 9.25 deg down, vfov 58. Every framing below is a rotation + zoom of it, so the plate stays exact.
export const PLATE_IMG = { w: 2752, h: 1536 };
export const GUIDE = { fov: 58, aim: dirAim(-2.0, -9.0) };
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
// round 7 (Jade: "the placement feels unnaturally high"): the real TL spot, on the sail at the window's FRONT LOWER
// corner, the glass bottom on the belt line (provisional world position; refined onto the r7 plate's drawn corner below)
// registered to the r7 plate (plate_r7_n -> r7_plate_rgba.png): its drawn window corner (A-pillar foot on the sill) is at
// plate px (1815, 695); the glass's inboard bottom sits just rearward of it, ~40 px above the sill (from the passenger's
// eye the glass bottom clears the door's inner edge by ~1.5 deg), its neck hidden behind the painted sail
// (measured on plate_r7_n: sill y 693, the window's vertical front frame x ~1810 from y 590 down, the A-pillar's lower
// edge through (1687, 500), (1745, 540), (1800, 580)): the glass's inboard edge ~1745 so its rounded top corner clears the
// pillar, the cap's bottom on the sill; the sail (make_plate_r7.py) bridges from it to the frame
const M_C = platePointX(1679, 610, -1.10);
export const ARM0 = platePointX(1790, 680, -0.93);   // on the door skin, hidden behind the plate's A-pillar
// round 4: the glass is aimed for HER: she sees straight back, a hair outward and down (as a driver sets it). From the
// passenger seat the same glass then shows the lanes further out (the far-left lane, where the TVA sedan comes up).
// round 7: the aim, fixed. Rounds 4-6 wrote [0.10, ...] meaning "a hair outward", but +x is the car's RIGHT, so her glass
// looked 5.7 deg INWARD and her own flank filled two thirds of it. Now as a driver sets it: the glass centre looks straight
// back (her flank a sliver along the inboard quarter), a little down. tracks_r7.mjs prints the check.
const DRIVER_LOOK = norm([0.0, -0.040, 1]);
const M_N = norm(add(norm(sub(EYE_DRIVER, M_C)), DRIVER_LOOK));
const M_U = norm(cross([0, 1, 0], M_N));                       // glass right, seen from the front
const M_V = cross(M_N, M_U);                                    // glass up
export const MIRROR_FR = 1.12;   // round 7: the reflection frustum covers 1.12 x the glass rectangle (the glass mesh runs under the drawn rim)
export const MIRROR = { c: M_C, n: M_N, u: M_U, v: M_V, w: 0.22, h: 0.142, r: 0.035 };   // round 7: 22 x 14.2 cm (the TL's glass; rounds 3-6: 24 x 15.5)
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
// round 7: the visible glass is the DRAWN housing's hole (TL_OUTLINE above is the CG guide's outline it was drawn over)
export const GLASS_OUTLINE = TL_OUTLINE_R7;
export function inGlass(a, b) {   // point-in-polygon on GLASS_OUTLINE (round 7; was TL_OUTLINE)
  let c = false; const P = GLASS_OUTLINE;
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
// round 7: re-framed for the r7 plate (camera 23 cm further forward): her eye at plate px (910, 545), the glass centre
// at (1730, 579), the window corner (1815, 695). The two-shot is wider than round 6's (face and glass are 37 deg apart)
const FOV_OPEN = 44, FOV_TWO = 27.5, FOV_TWO_END = 22.5, FOV_GLASS = 7.4;
const AIM_OPEN = aimPx(1250, 760);
const AIM_TWO = aimPx(1290, 600);
const AIM_TWO_END = aimPx(1400, 612);
export function camAt(s) {
  let fov, aim;
  if (s < S1) {
    const k = easeIO3(clamp((s - S0) / (24.0 - S0)));
    // round 7: the two-shot holds while "A shadow" lights, then creeps toward the glass as "chasing" lands (eased, so the
    // move hands on to D3's zoom at rest), her profile sliding toward the left edge
    const creep = smooth(24.45, S1, s);   // eases to rest at S1; D3 starts from rest (ease of ease), so no velocity jump at the cut
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
// round 7: the DRAWN housing's camera: a fixed 10 deg frustum on the mirror from the same eye point (the camera only
// rotates and zooms, so a card on this frustum stays registered at every framing). D3 ends at ~7.2 deg vfov, and the card
// is drawn at 1536 px over 10 deg, a touch sharper than the final frame needs.
export const HOUSING = { fov: 10.0, aim: add(M_C, add(mul(M_U, 0.02), mul(M_V, -0.004))) };
export function housingCam() { return camFrom(HOUSING.aim, HOUSING.fov, S0, 0); }
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
// round 7: with the aim fixed the camera's view in the glass is ~31 deg outward, so the sedan comes up in the FAR-left
// lane (scene_r7 adds Lake Shore Drive's fourth southbound lane), angled toward us (yaw), and holds ~16 m back
export const SEDAN = { x: -11.05, len: 5.15, w: 1.84, yaw: -28 * Math.PI / 180, dEnd: 18.0 };
export function sedanAt(s) {
  const k = smoother(S0, 26.9, s);   // round 7: arrives a touch earlier (it enters the glass ~26.1, as in rounds 4-6)
  const d = lerp(70, SEDAN.dEnd, k) + 0.2 * Math.sin(s * 0.9);
  const x = SEDAN.x - 0.06 * Math.sin(s * 0.7 + 1);
  return { front: [x, 0, M_C[2] + d], d };
}
// the sedan is an engraved impostor card (media/shots/D23/sedan_a_rgba.png, nano-banana) standing at its front bumper,
// facing -z (seen ~10 deg off its axis in the mirror). Scale from its blank plate: a US plate, 12 x 6.5 in.
export const SEDAN_IMG = { size: [2752, 1536], cx: 1390, ground: 1376, plate: [1551, 964, 1803, 1103],   // round 5: the drawn plate measured (pale field + its thin frame)
  lamps: [[1185, 810], [2070, 810]] };
export const PLATE = { w: 0.305, h: 0.305 * (1102 - 966) / (1802 - 1550) };
export const SEDAN_PPM = (1802 - 1550) / 0.305;             // image px per metre on the card
export function plateCorners(s) {   // world corners TL, TR, BR, BL as seen from behind it (i.e. facing the sedan)
  const f = sedanAt(s).front, I = SEDAN_IMG, k = SEDAN_PPM, c = Math.cos(SEDAN.yaw), sn = Math.sin(SEDAN.yaw);
  // card-local: image x grows toward the viewer's right = local -x (the card faces -z); then the sedan's yaw about y
  // (three.js rotation.y: x' = x cos + z sin, z' = -x sin + z cos)
  const P = (px, py) => { const x = -(px - I.cx) / k, y = (I.ground - py) / k; return [f[0] + x * c, y, f[2] - x * sn]; };
  const [x0, y0, x1, y1] = I.plate;
  return [P(x0, y0), P(x1, y0), P(x1, y1), P(x0, y1)];
}
// the billboard: two bulb panels on a lattice tower on the lakefront, far behind on the left
// round 7: the camera's view in the glass is ~31 deg outward, so the billboard stands far back on the lakefront (out on the
// breakwater), big, high on its tower: it sits above the sedan's roof in the glass and drifts slowly
// round 7: the northbound traffic's phase (metres added to every car's start): at 400 no car crosses the far billboard
// in the glass (checked on the mask per frame; at 0 one crossed at 25.92-26.00 and hid CHASING for two frames)
export const TRAFFIC_SHIFT = 400;
export const BILL = { x: -905, z0: 1500, y0: 0.6, w: 88, ph: 16.8, gap: 3.6 };   // y0: bottom of the lower panel
export function billPanels(s) {
  const z = worldZ(BILL.z0, s), hw = BILL.w / 2;
  // seen from the front (it faces -z, toward the road ahead / us), the viewer's right is -x... the face looks toward -z,
  // a viewer at -z looking +z has right = -x, so TL is at +x
  const q = (yb, yt) => [[BILL.x + hw, yt, z], [BILL.x - hw, yt, z], [BILL.x - hw, yb, z], [BILL.x + hw, yb, z]];
  const yb1 = BILL.y0, yt1 = yb1 + BILL.ph, yb2 = yt1 + BILL.gap, yt2 = yb2 + BILL.ph;
  return { top: q(yb2, yt2), bot: q(yb1, yt1) };
}
// lyric etch on the glass itself (glass-local box): the bottom band, under the sedan (round 4: its plate sits mid-glass)
// round 7: the etch moves to the BOTTOM band of the glass, under the TVA plate and over the bumper (the billboard keeps the top
// band through D3, behind the sedan's roof): two lines, the quad following the drawn glass's rising bottom edge outboard
export const ETCH = { a0: -0.45, a1: 0.85, out: [-0.68, -0.40], in: [-0.84, -0.54] };
