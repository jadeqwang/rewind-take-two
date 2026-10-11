// car_shot.js (v4, B): the 1:30 car shot, option C (Jade's pick). One take: over her right shoulder in the
// left-hand-drive Acura (wheel, dash, both pencils, her cheek), then a push between the front seats into the rear-view
// mirror, which is full of the fleet. Built from two engraved stills (plan: docs/revisions/v4/plans/car.md):
//   wide  media/shots/V2f3/kf_wide_b_fix_engraved.png   (its mirror is the close keyframe's mirror, laid in at r)
//   close media/shots/V2f4/kf_close_b2_engraved_feather.png
// The push is a zoom about the fixed point F of the wide, so the wide's mirror lands exactly on the close still,
// which fades in over the fast part of the move. Lettering and plates are pinned by the engine, never drawn:
//   SIRENS on the overhead sign (sung 90.19), IN MY MIRROR on the mirror's lower edge (sung 91.09),
//   TVA 1729 / 4104 / 4096 on the three nearest sedans (tools/v4B/plate/plate.js, 1.5x a true plate, right-reading).
// All camera times are absolute song seconds, so the shot start (CAR_START in render/timeline/C.js) can move freely.
const S = 'media/shots/';
const WIDE = `${S}V2f3/kf_wide_b_fix_engraved.png`, CLOSE = `${S}V2f4/kf_close_b2_engraved_feather.png`;
const BODY = `${S}V2f4/kf_close_b2_engraved_body.png`;   // the close still cut to the mirror body (alpha)
const C0 = [960, 540];
const MW = [1335.8, 436.5];          // mirror centre in the wide, design px (tools/v4B/car/fix_wide.py -> kf_wide_b_fix.json)
const MC = [961.0, 585.3];           // mirror centre in the close, design px (kf.py MIRROR_SRC)
const R = 394.4 / 1866.8;            // close design px -> wide design px (mirror body widths)
const E_END = 1.08;                  // the close still's scale on the last frame
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
const wideCam = (t) => { const z = zoom(t); return { scale: z, x: (F[0] - C0[0]) * (1 - z), y: (F[1] - C0[1]) * (1 - z) }; };
const closeCam = (t) => { const z = zoom(t); return { scale: z * R,
  x: F[0] - C0[0] + z * (MW[0] - R * MC[0] - F[0] + R * C0[0]), y: F[1] - C0[1] + z * (MW[1] - R * MC[1] - F[1] + R * C0[1]) }; };
const apply = (cam, q) => q.map((v, i) => C0[i % 2] + (i % 2 ? cam.y : cam.x) + cam.scale * (v - C0[i % 2]));
// hand-over in two steps, both inside the fast part of the push: first the mirror body alone (it IS the wide's mirror,
// relaid, so only sharpness changes), then the rest of the close still (headliner above, black below) once the
// mirror fills most of the frame and what surrounds it is only a thin border.
const bodyOpacity = (t) => sm((zoom(t) - 1.6) / (2.6 - 1.6));
const closeOpacity = (t) => sm((zoom(t) - 3.7) / (4.6 - 3.7));
// road vibration on the lens: tiny, on twos, deterministic
const jig = (t, a, s) => a * Math.sin(Math.floor(t * 12) * 12.9898 + s) * Math.sin(Math.floor(t * 12) * 4.1414 + 2 * s);

const SIGN_Q = [840, 96, 1266, 96, 1266, 222, 840, 222];          // the blank panel of the gantry in the wide (design px)
const BEZEL_Q = [600, 822, 1320, 822, 1320, 912, 600, 912];        // the mirror's lower edge in the close (design px)
const PLATES = [  // blank plates the keyframe drew, in the close (design px): [text, TL TR BR BL]
  ['TVA 1729', [919.2, 674.3, 1012.7, 674.3, 1012.7, 718.6, 919.2, 718.6]],
  ['TVA 4104', [370.8, 606.1, 422.8, 606.1, 422.8, 632.1, 370.8, 632.1]],
  ['TVA 4096', [1509.8, 605.4, 1561.8, 605.4, 1561.8, 631.4, 1509.8, 631.4]],
];

export default function carShot(start, end = 92.79) {
  const cw = (lt, env) => wideCam(env.t), cc = (lt, env) => closeCam(env.t);
  const layers = [
    { id: 'car_wide', type: 'image', src: WIDE, fit: 'cover',
      scale: (lt, env) => cw(lt, env).scale, x: (lt, env) => cw(lt, env).x + jig(env.t, 1.2, 1), y: (lt, env) => cw(lt, env).y + jig(env.t, 1.6, 2) },
    { id: 'car_sign', type: 'canvas', module: 'pin', noRewind: true, params: { style: 'sign', text: 'SIRENS', sync: 'lyric', size: 120, padding: 30,
      corners: (lt, env) => apply(cw(lt, env), SIGN_Q) } },
    { id: 'car_body', type: 'image', src: BODY, fit: 'cover', opacity: (lt, env) => bodyOpacity(env.t),
      scale: (lt, env) => cc(lt, env).scale, x: (lt, env) => cc(lt, env).x + jig(env.t, 1.2, 1), y: (lt, env) => cc(lt, env).y + jig(env.t, 1.6, 2) },
    { id: 'car_close', type: 'image', src: CLOSE, fit: 'cover', opacity: (lt, env) => closeOpacity(env.t),
      scale: (lt, env) => cc(lt, env).scale, x: (lt, env) => cc(lt, env).x + jig(env.t, 1.2, 1), y: (lt, env) => cc(lt, env).y + jig(env.t, 1.6, 2) },
    ...PLATES.map(([text, q], i) => ({ id: `car_plate${i}`, type: 'canvas', module: 'tools/v4B/plate/plate.js', noRewind: true,
      params: { text, corners: q, grow: i ? 1.75 : 1.5, aspect: 2.3, dim: 0.12, light: 1, seed: 11 + i,
        cam: { scale: (lt, env) => cc(lt, env).scale, x: (lt, env) => cc(lt, env).x + jig(env.t, 1.2, 1), y: (lt, env) => cc(lt, env).y + jig(env.t, 1.6, 2) } } })),
    { id: 'car_etch', type: 'canvas', module: 'pin', noRewind: true, params: { style: 'etch', text: 'IN MY MIRROR', sync: 'lyric', uppercase: true,
      size: 64, align: 'center', color: 'rgba(236,231,220,0.86)', corners: (lt, env) => apply(cc(lt, env), BEZEL_Q) } },
  ];
  return { id: 'C_V2f_car', start, end, background: '#0b0b0c', layers,
    fx: [{ type: 'punch', amount: 0.012, on: 'beat' }] };
}
export const _debug = { F, PEND, R, zoom, wideCam, closeCam };
