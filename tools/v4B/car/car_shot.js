// car_shot.js (v4, B): the 1:30 car shot, option C (Jade's pick). One take: over her right shoulder in the
// left-hand-drive Acura (wheel, dash, both pencils, her cheek), then a push between the front seats into the rear-view
// mirror, which is full of the fleet. Built from two engraved stills (plan: docs/revisions/v4/plans/car.md):
//   wide  media/shots/V2f3/kf_wide_b_fix_engraved.png   (its mirror is the close keyframe's mirror, laid in at R)
//   close media/shots/V2f4/kf_close_b2_engraved.png
// The push is a zoom about the fixed point F of the wide, so the wide's mirror lands exactly on the close still.
// v4b (Jade: "would be better if it were animated (even if you could just feel the cars moving)"), all free, all from
// the two stills (cut-outs: tools/v4B/car/cutouts.py):
//   - the car's ride: a slow bob and roll plus a faint road judder, as shot fx, so the pinned text rides with it;
//   - the road ahead streams toward us: the window region is an endless zoom about the vanishing point, seen through
//     the cabin cut-out (wide_cabin.png); the gantry with the sign approaches and climbs out of frame (wide_gantry.png);
//   - a streetlight sweeps through the cabin every two beats (fx_car.js 'sweep');
//   - in the mirror the three nearest sedans are their own cut-outs: each sways, bobs, drifts a little across its lane
//     and closes in; their roof bars flash (fx_car.js 'strobe', white only). Their plates ride with them.
// Lettering and plates are pinned by the engine, never drawn: SIRENS (woodcut, cut into the sign, sung 90.19),
// IN MY MIRROR (woodcut in Fell, cut into the mirror's lower edge, sung 91.09), TVA 1729 / 4104 / 4096.
// All times are absolute song seconds, so the shot start (CAR_START in render/timeline/C.js) can move freely.
const S = 'media/shots/';
const WIDE = `${S}V2f3/kf_wide_b_fix_engraved.png`, CABIN = `${S}V2f3/wide_cabin.png`, GANTRY = `${S}V2f3/wide_gantry.png`;
const BODY = `${S}V2f4/kf_close_b2_engraved_body.png`, PADDED = `${S}V2f4/close_pad.png`, PAD = 2.2;   // close on a black margin
const WOODCUT = 'tools/sectionA/modules/woodcut.js', FX = 'tools/v4B/car/fx_car.js';
// v4c (Jade: "the main weakness is actually that she's completely still ..."): the wide is now a Seedance 2.0 take of
// the wide still (tools/v4B/car/vid.py, engraved), so she breathes, blinks and glances, and the road streams for real.
// Set TAKE = null to go back to the still with the engine's endless road zoom under the cabin cut-out.
const TAKE = `${S}V2f3/take_1_engraved.mp4`;
const C0 = [960, 540];
const MW = [1335.8, 436.5];          // mirror centre in the wide, design px (tools/v4B/car/fix_wide.py -> kf_wide_b_fix.json)
const MC = [961.0, 585.3];           // mirror centre in the close, design px (kf.py MIRROR_SRC)
const R = 394.4 / 1866.8;            // close design px -> wide design px (mirror body widths)
const E_END = 1.08;                  // the close still's scale on the last frame
const VP = [905, 488];               // vanishing point of the road ahead in the wide (design px)
// camera: Z = zoom of the wide. Slow creep on the hold, the push 90.50 -> 92.00 (eased in log space), then a creep.
const PUSH = [90.50, 92.00], Z0 = 1.0, Z1 = 1.045, Z2 = 1.0 / R, Z3 = E_END / R;
const sm = (u) => { u = Math.max(0, Math.min(1, u)); return u * u * (3 - 2 * u); };
const ease = (u) => { u = Math.max(0, Math.min(1, u)); return u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2; };
export function zoom(t) {
  if (t < PUSH[0]) return Z0 + (Z1 - Z0) * sm((t - 89.26) / (PUSH[0] - 89.26));
  if (t < PUSH[1]) return Math.exp(Math.log(Z1) + (Math.log(Z2) - Math.log(Z1)) * ease((t - PUSH[0]) / (PUSH[1] - PUSH[0])));
  return Z2 + (Z3 - Z2) * sm((t - PUSH[1]) / (92.79 - PUSH[1]));
}
// fixed point F: zooming the wide about F by Z2 frames the close still exactly (centred, scale 1)
const PEND = [MW[0] + R * (C0[0] - MC[0]), MW[1] + R * (C0[1] - MC[1])];
const F = [0, 1].map((i) => (Z2 * PEND[i] - C0[i]) / (Z2 - 1));
// a "cam" is the engine's layer transform {scale, x, y}: screen = C0 + (x, y) + scale * (p - C0)
const wideCam = (t) => { const z = zoom(t); return { scale: z, x: (F[0] - C0[0]) * (1 - z), y: (F[1] - C0[1]) * (1 - z) }; };
const closeCam = (t) => { const z = zoom(t); return { scale: z * R,
  x: F[0] - C0[0] + z * (MW[0] - R * MC[0] - F[0] + R * C0[0]), y: F[1] - C0[1] + z * (MW[1] - R * MC[1] - F[1] + R * C0[1]) }; };
// cam o (scale k about point a, then shift d), all in the layer's own design px
const about = (cam, k, a, d = [0, 0]) => ({ scale: cam.scale * k, x: cam.x + cam.scale * ((1 - k) * (a[0] - C0[0]) + d[0]),
  y: cam.y + cam.scale * ((1 - k) * (a[1] - C0[1]) + d[1]) });
const apply = (cam, q) => q.map((v, i) => C0[i % 2] + (i % 2 ? cam.y : cam.x) + cam.scale * (v - C0[i % 2]));
const layerT = (camFn) => ({ scale: (lt, env) => camFn(env.t).scale, x: (lt, env) => camFn(env.t).x, y: (lt, env) => camFn(env.t).y });
const camP = (camFn) => ({ scale: (lt, env) => camFn(env.t).scale, x: (lt, env) => camFn(env.t).x, y: (lt, env) => camFn(env.t).y });
// hand-over in two steps, both inside the fast part of the push: first the mirror body alone (it IS the wide's mirror,
// relaid), then the whole close still on its black margin, so no blurred edge of the wide is ever left round it
const bodyOpacity = (t) => sm((zoom(t) - 1.6) / (2.6 - 1.6));
const closeOpacity = (t) => sm((zoom(t) - 3.0) / (3.9 - 3.0));
const padCam = (t) => { const c = closeCam(t); return { ...c, scale: c.scale * PAD }; };

// the road ahead: two copies of the wide zooming about VP, half a cycle apart, cross-faded (an endless dolly)
const ROAD_PERIOD = 0.30, ROAD_K = 1.22;
const roadPhase = (t, half) => (((t - 89.0) / ROAD_PERIOD + (half ? 0.5 : 0)) % 1 + 1) % 1;
const roadCam = (t, half) => about(wideCam(t), Math.pow(ROAD_K, roadPhase(t, half)), VP);
const roadOpacity = (t, half) => 1 - Math.abs(2 * roadPhase(t, half) - 1);
// the gantry: approaches (grows about VP) from the first frame, faster and faster
const gantryK = (t) => 1 + 0.10 * Math.max(0, t - 89.26) + 0.05 * Math.pow(Math.max(0, t - 89.26), 2);
const GANTRY_A = [905, 276];         // on the header line: the gantry grows up and out from behind the header
const gantryCam = (t) => about(wideCam(t), gantryK(t), GANTRY_A);

// the three sedans in the mirror, in the close's design px: anchor = bottom centre (where the car meets the road)
const CARS = [
  { id: 'left', src: `${S}V2f4/car_left.png`, a: [480, 662], sway: [5, 1.3, 0.4], bob: [2.2, 3.1, 1.1], drift: 14, close: 0.05,
    plate: ['TVA 4104', [370.8, 606.1, 422.8, 606.1, 422.8, 632.1, 370.8, 632.1]], bars: [[456, 416, 30], [568, 416, 30]], ph: 0.31 },
  { id: 'right', src: `${S}V2f4/car_right.png`, a: [1452, 664], sway: [5, 1.1, 2.0], bob: [2.2, 2.7, 0.3], drift: -12, close: 0.06,
    plate: ['TVA 4096', [1509.8, 605.4, 1561.8, 605.4, 1561.8, 631.4, 1509.8, 631.4]], bars: [[1366, 420, 30], [1478, 420, 30]], ph: 0.62 },
  { id: 'hero', src: `${S}V2f4/car_hero.png`, a: [965, 746], sway: [6, 0.9, 1.0], bob: [2.6, 3.4, 2.2], drift: 6, close: 0.10,
    plate: ['TVA 1729', [919.2, 674.3, 1012.7, 674.3, 1012.7, 718.6, 919.2, 718.6]], bars: [[862, 386, 52], [1058, 386, 52]], ph: 0 },
];
const carCam = (c) => (t) => {
  const u = sm((t - 89.26) / (92.79 - 89.26));
  const k = 1.02 + c.close * u;                                              // closing in (and always covering itself)
  const d = [c.sway[0] * Math.sin(t * c.sway[1] * 2 * Math.PI + c.sway[2]) + c.drift * u,
    c.bob[0] * Math.sin(t * c.bob[1] * 2 * Math.PI + c.bob[2]) + 1.2 * Math.sin(t * 17 + c.bob[2])];
  return about(closeCam(t), k, c.a, d);
};

const SIGN_Q = [846, 100, 1260, 100, 1260, 218, 846, 218];          // the blank panel of the gantry in the wide (design px)
const BEZEL_Q = [610, 826, 1310, 826, 1310, 910, 610, 910];        // the mirror's lower edge in the close (design px)

export default function carShot(start, end = 92.79) {
  const layers = [
    // the wide: base, the streaming road, the approaching gantry, then the cabin over them
    ...(TAKE ? [{ id: 'car_take', type: 'video', src: TAKE, in: 0, rate: 1, fit: 'cover', ...layerT(wideCam) }] : [
      { id: 'car_wide', type: 'image', src: WIDE, fit: 'cover', ...layerT(wideCam) },
      ...[0, 1].map((h) => ({ id: `car_road${h}`, type: 'image', src: WIDE, fit: 'cover', opacity: (lt, env) => roadOpacity(env.t, h), ...layerT((t) => roadCam(t, h)) }))]),
    // the sky band keeps the still's gantry (the take sends gantries past at its own pace; SIRENS stays pinned to this one)
    { id: 'car_gantry', type: 'image', src: GANTRY, fit: 'cover', ...layerT(gantryCam) },
    { id: 'car_sign', type: 'canvas', module: WOODCUT, noRewind: true, params: { text: 'SIRENS', sync: 'lyric', color: '#ece7dc', box: [600, 170], pad: 10,
      hatch: 0.38, flecks: 16, corners: (lt, env) => apply(gantryCam(env.t), SIGN_Q) } },
    ...(TAKE ? [] : [{ id: 'car_cabin', type: 'image', src: CABIN, fit: 'cover', ...layerT(wideCam) }]),
    { id: 'car_sweep', type: 'canvas', module: FX, blend: 'screen', params: { kind: 'sweep', every: 2, amount: (lt, env) => 0.2 * (1 - closeOpacity(env.t)) } },
    // the mirror: body, then the whole close still on its margin, then the sedans, their bars and plates, the words
    // over the take the still's mirror is laid in from the first frame, so the engine's fleet stays in register
    { id: 'car_body', type: 'image', src: BODY, fit: 'cover', opacity: (lt, env) => (TAKE ? 1 : bodyOpacity(env.t)), ...layerT(closeCam) },
    { id: 'car_close', type: 'image', src: PADDED, fit: 'cover', opacity: (lt, env) => closeOpacity(env.t), ...layerT(padCam) },
    ...CARS.flatMap((c, i) => [
      { id: `car_${c.id}`, type: 'image', src: c.src, fit: 'cover', ...layerT(carCam(c)) },
      { id: `car_${c.id}_bars`, type: 'canvas', module: FX, blend: 'screen', params: { kind: 'strobe', points: c.bars, phase: c.ph, cam: camP(carCam(c)) } },
      { id: `car_${c.id}_plate`, type: 'canvas', module: 'tools/v4B/plate/plate.js', noRewind: true,
        params: { text: c.plate[0], corners: c.plate[1], grow: c.id === 'hero' ? 1.5 : 1.75, aspect: 2.3, dim: 0.12, light: 1, seed: 11 + i, cam: camP(carCam(c)) } },
    ]),
    { id: 'car_etch', type: 'canvas', module: WOODCUT, noRewind: true, params: { text: 'IN MY MIRROR', sync: 'lyric', font: 'fell', color: 'rgba(236,231,220,0.92)',
      box: [700, 84], pad: 4, hatch: 0.3, flecks: 8, corners: (lt, env) => apply(closeCam(env.t), BEZEL_Q) } },
  ];
  return { id: 'C_V2f_car', start, end, background: '#0b0b0c', layers,
    fx: [
      { type: 'shake', amp: 4.5, freq: 1.4, steady: 1 },          // the body of the car on its springs
      { type: 'shake', amp: 1.3, freq: 13, steady: 1 },           // road judder
      { type: 'spin', amount: (lt) => 0.35 * Math.sin(lt * 2.1 + 0.8) + 0.12 * Math.sin(lt * 5.3 + 1) },   // roll
      { type: 'punch', amount: 0.01, on: 'beat' },
    ] };
}
export const _debug = { F, PEND, R, zoom, wideCam, closeCam };
