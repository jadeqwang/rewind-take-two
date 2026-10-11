// Low-poly figures: dark-suited agents in sunglasses, and a placeholder Jade (white cropped jacket with an
// orange band, black crop top, navy cargo pants with orange straps, white sneakers, black bun with a pencil,
// orange headphones round the neck). ~1.0 world unit tall. Pose is a pure function of (stride phase, gait).
import * as THREE from 'three';
import { MAT } from './engrave.js';

let FIG_ID = 500;

function boxPart(eng, parent, mat, albedo, size, pos, pushConst, { pivot = null, extra = {} } = {}) {
  const g = new THREE.BoxGeometry(size[0], size[1], size[2]);
  if (pivot) g.translate(-pivot[0], -pivot[1], -pivot[2]);
  const m = new THREE.Mesh(g, eng.material({ mat, albedo, id: (FIG_ID += 7) * 0.01, pushConst, ...extra }));
  m.position.set(pos[0], pos[1], pos[2]);
  parent.add(m);
  return m;
}

// kind: 'agent' | 'jade'
export function makeFigure(eng, kind = 'agent', { hairDown = false } = {}) {
  const root = new THREE.Group();
  const body = new THREE.Group(); root.add(body);
  const pushConst = { value: 0 };
  const J = kind === 'jade';
  const suit = J ? MAT.jPants : MAT.suit, suitA = J ? 0.32 : 0.16;
  const P = (mat, alb, size, pos, opt) => boxPart(eng, body, mat, alb, size, pos, pushConst, opt);

  // legs: thigh pivots at hip, shin at knee
  const legs = [];
  for (const s of [-1, 1]) {
    const hip = new THREE.Group(); hip.position.set(0.075 * s, 0.5, 0); body.add(hip);
    const thigh = boxPart(eng, hip, suit, suitA, [0.12, 0.26, 0.14], [0, -0.12, 0], pushConst);
    const knee = new THREE.Group(); knee.position.set(0, -0.25, 0); hip.add(knee);
    const shin = boxPart(eng, knee, suit, suitA, [0.11, 0.24, 0.12], [0, -0.12, 0], pushConst);
    const shoe = boxPart(eng, knee, J ? MAT.jShoe : MAT.shades, J ? 0.95 : 0.1, J ? [0.14, 0.08, 0.24] : [0.12, 0.06, 0.21], [0, -0.25, 0.04], pushConst);
    if (J) boxPart(eng, knee, MAT.jBand, 0.7, [0.125, 0.035, 0.13], [0, -0.06, 0], pushConst); // orange strap
    legs.push({ hip, knee, thigh, shin, shoe });
  }
  // torso
  if (J) {
    P(MAT.jTop, 0.1, [0.3, 0.14, 0.17], [0, 0.57, 0]);                     // black crop top (midriff)
    P(MAT.jJacket, 0.95, [0.36, 0.27, 0.21], [0, 0.765, 0]);               // white cropped jacket
    P(MAT.jBand, 0.65, [0.365, 0.05, 0.215], [0, 0.8, 0]);                 // orange chest band
    P(MAT.jTop, 0.1, [0.12, 0.2, 0.01], [0, 0.77, 0.106]);                 // open front shows black top
  } else {
    P(MAT.suit, 0.16, [0.36, 0.42, 0.21], [0, 0.71, 0]);                   // jacket
    P(MAT.shirt, 0.95, [0.1, 0.16, 0.01], [0, 0.83, 0.106]);               // shirt V
    P(MAT.shades, 0.08, [0.035, 0.15, 0.012], [0, 0.82, 0.112]);           // tie
  }
  // arms: pivot at shoulder
  const arms = [];
  for (const s of [-1, 1]) {
    const sh = new THREE.Group(); sh.position.set(0.225 * s, 0.88, 0); body.add(sh);
    const arm = boxPart(eng, sh, J ? MAT.jJacket : MAT.suit, J ? 0.93 : 0.16, [0.09, 0.36, 0.11], [0, -0.17, 0], pushConst);
    if (J) boxPart(eng, sh, MAT.jBand, 0.65, [0.095, 0.05, 0.115], [0, -0.09, 0], pushConst);
    boxPart(eng, sh, MAT.skin, 0.85, [0.07, 0.07, 0.08], [0, -0.38, 0], pushConst);
    if (J && hairDown && s === 1) { const pc = boxPart(eng, sh, MAT.jPencil, 0.85, [0.025, 0.025, 0.24], [0, -0.4, 0.08], pushConst); pc.rotation.x = 0.3; }
    arms.push(sh);
  }
  // head
  const head = new THREE.Group(); head.position.set(0, 0.92, 0); body.add(head);
  boxPart(eng, head, MAT.skin, J ? 0.9 : 0.8, [0.08, 0.06, 0.08], [0, 0.03, 0], pushConst);           // neck
  boxPart(eng, head, MAT.skin, J ? 0.92 : 0.82, [0.19, 0.22, 0.2], [0, 0.17, 0], pushConst);           // face
  if (J && hairDown) {
    boxPart(eng, head, MAT.jHair, 0.08, [0.21, 0.1, 0.22], [0, 0.27, -0.01], pushConst);              // hair cap
    boxPart(eng, head, MAT.jHair, 0.08, [0.23, 0.62, 0.07], [0, 0.0, -0.1], pushConst);               // long hair down the back
    boxPart(eng, head, MAT.jHair, 0.08, [0.04, 0.34, 0.12], [0.1, 0.1, 0.02], pushConst);             // side strands
    boxPart(eng, head, MAT.jHair, 0.08, [0.04, 0.34, 0.12], [-0.1, 0.1, 0.02], pushConst);
    boxPart(eng, head, MAT.phones, 0.7, [0.27, 0.06, 0.06], [0, -0.01, 0.06], pushConst);
    boxPart(eng, head, MAT.phones, 0.7, [0.05, 0.1, 0.1], [0.13, 0.0, 0.03], pushConst);
    boxPart(eng, head, MAT.phones, 0.7, [0.05, 0.1, 0.1], [-0.13, 0.0, 0.03], pushConst);
  } else if (J) {
    boxPart(eng, head, MAT.jHair, 0.08, [0.21, 0.1, 0.22], [0, 0.27, -0.01], pushConst);              // hair cap
    boxPart(eng, head, MAT.jHair, 0.08, [0.21, 0.2, 0.06], [0, 0.18, -0.09], pushConst);              // back hair
    boxPart(eng, head, MAT.jHair, 0.08, [0.12, 0.11, 0.11], [0, 0.34, -0.06], pushConst);             // bun
    const pencil = boxPart(eng, head, MAT.jPencil, 0.85, [0.3, 0.025, 0.025], [0, 0.35, -0.06], pushConst); // pencil through bun
    pencil.rotation.z = 0.35;
    boxPart(eng, head, MAT.phones, 0.7, [0.27, 0.06, 0.06], [0, -0.01, 0.06], pushConst);             // headphones (neck)
    boxPart(eng, head, MAT.phones, 0.7, [0.05, 0.1, 0.1], [0.13, 0.0, 0.03], pushConst);
    boxPart(eng, head, MAT.phones, 0.7, [0.05, 0.1, 0.1], [-0.13, 0.0, 0.03], pushConst);
  } else {
    boxPart(eng, head, MAT.shades, 0.1, [0.205, 0.07, 0.205], [0, 0.285, -0.005], pushConst);        // short hair
    boxPart(eng, head, MAT.shades, 0.05, [0.21, 0.05, 0.03], [0, 0.19, 0.1], pushConst);              // sunglasses
    boxPart(eng, head, MAT.shades, 0.05, [0.215, 0.025, 0.2], [0, 0.2, 0.0], pushConst);              // temples
  }

  function pose(phase, gait = 1, march = 0) {
    // phase: radians of the stride cycle; gait 0 = standing .. 1 = walking; march adds stiff-armed lockstep
    const sw = Math.sin(phase) * gait;
    const amp = 0.5 + 0.12 * march;
    for (let i = 0; i < 2; i++) {
      const s = i === 0 ? 1 : -1;
      const L = legs[i];
      L.hip.rotation.x = s * sw * amp;
      const lift = Math.max(0, Math.sin(phase + (i === 0 ? 0 : Math.PI) + 0.9)) * gait;
      L.knee.rotation.x = 0.85 * lift;
      arms[i].rotation.x = -s * sw * (0.45 - 0.15 * march);
      arms[i].rotation.z = s * 0.06;
    }
    body.position.y = Math.abs(Math.cos(phase)) * 0.025 * gait - 0.01 * gait;
    body.rotation.x = 0.04 * gait;
  }
  pose(0, 0);

  body.scale.setScalar(1.2);
  root.traverse((o) => { if (o.isMesh) o.userData.figure = true; });
  return { root, pose, pushConst, kind };
}
