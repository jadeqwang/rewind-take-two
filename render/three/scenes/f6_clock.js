// Section F, F6 3D element (190.58-195.86): the melting clock's hands become a Penrose staircase.
//
// The circuit from penrose_loop, re-dressed as a clock: the seam corner S is the clock's centre, leg A is the minute
// hand lying on the (melting, Klimt-gold) face, leg D is the hour hand - really floating 6 units above the face - and
// the two stone flights hang between their tips. Seen from the side it is a broken clock with a stray beam in the
// air. The camera orbits with her gesture and clunks into the magic angle on 194.10 (bar 111): both hands now spring
// from the centre and, with the flights, close into Ascending and Descending. Agents drip off the clock's melting lip
// onto it and march it forever. The world is in colour (final drop); agents stay ink.
//   params: from (song s, default 190.58), snap (194.10), color (1)
import * as THREE from 'three';
import { Stage, ISO_AZ, ISO_EL, boilSeed } from '../lib/stage.js';
import { Builder, V } from '../lib/build.js';
import { MAT } from '../lib/engrave.js';
import { loopPath, loopPush, K, Y0, AX, ZBC, XD, HW, NSTEP, RUN, RISE, D_PUSH0, D_END } from '../lib/loopset.js';
import { makeFigure } from '../lib/figures.js';
import { clunk, smoother, smooth, clamp, lerp, hash } from '../lib/util.js';

export function createScene(defaults = {}) {
  const meta = { name: 'f6_clock', duration: 5.28, fps: 24, width: 1920, height: 1080, output: 'srgb' };
  let st, params, path, agents = [], hands;

  function init(renderer, p = {}) {
    params = { from: 190.58, snap: 194.10, color: 1, ...p };
    meta.duration = 195.86 - params.from;
    st = new Stage(renderer, params);
    const eng = st.eng;
    st.eng.fitShadow(V(5, 3, -3), 22);
    const dPush = { origin: [XD, Y0 + K, D_PUSH0], axis: [0, 0, 1], max: D_END - D_PUSH0, rate: K * Math.sqrt(3) / (D_END - D_PUSH0) };

    // ---- the melting clock face: a gold disc centred on S whose front lip droops and drips
    const R = 11.5, N = 96, cy = Y0 - 0.35;
    const pos = [], nor = [], idx = [];
    const droop = (x, z) => { const d = Math.hypot(x, z); const front = Math.max(0, (x + z) / (Math.SQRT2 * R)); return -(Math.max(0, d - R * 0.55) ** 2) * 0.09 * (0.3 + 1.7 * front ** 2); };
    for (let i = 0; i <= 24; i++) for (let j = 0; j <= N; j++) {
      const r = R * i / 24, a = j / N * Math.PI * 2, x = r * Math.cos(a), z = r * Math.sin(a);
      pos.push(x, cy + droop(x, z), z); nor.push(0, 1, 0);
    }
    for (let i = 0; i < 24; i++) for (let j = 0; j < N; j++) { const a = i * (N + 1) + j, b = a + N + 1; idx.push(a, a + 1, b, b, a + 1, b + 1); }
    const face = new THREE.BufferGeometry();
    face.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); face.setIndex(idx); face.computeVertexNormals();
    face.setAttribute('normal', face.getAttribute('normal'));
    st.scene.add(new THREE.Mesh(face, eng.material({ mat: MAT.tower, albedo: 0.95, id: 1.1, side: THREE.DoubleSide })));
    // rim + twelve tick marks (the agency pin: no numerals)
    const rim = new Builder(), ticks = new Builder();
    for (let j = 0; j < N; j++) {
      const a0 = j / N * Math.PI * 2, a1 = (j + 1) / N * Math.PI * 2;
      const p0 = V(R * Math.cos(a0), 0, R * Math.sin(a0)), p1 = V(R * Math.cos(a1), 0, R * Math.sin(a1));
      p0.y = cy + droop(p0.x, p0.z); p1.y = cy + droop(p1.x, p1.z);
      rim.quad(p0.clone().setY(p0.y - 0.35), p1.clone().setY(p1.y - 0.35), p1.clone().setY(p1.y + 0.18), p0.clone().setY(p0.y + 0.18), 1, V(Math.cos(a0), 0, Math.sin(a0)));
    }
    for (let k = 0; k < 12; k++) {
      const a = k / 12 * Math.PI * 2, r0 = R * 0.82, r1 = R * (k % 3 === 0 ? 0.68 : 0.74);
      const c = V((r0 + r1) / 2 * Math.cos(a), 0, (r0 + r1) / 2 * Math.sin(a)); c.y = cy + droop(c.x, c.z) + 0.04;
      ticks.obox(c, V(Math.cos(a), 0, Math.sin(a)).multiplyScalar((r0 - r1) / 2), V(0, 0.05, 0), V(-Math.sin(a), 0, Math.cos(a)).multiplyScalar(k % 3 === 0 ? 0.22 : 0.12));
    }
    st.scene.add(new THREE.Mesh(rim.geometry(), eng.material({ mat: MAT.brass, albedo: 0.8, id: 1.3, side: THREE.DoubleSide })));
    st.scene.add(new THREE.Mesh(ticks.geometry(), eng.material({ mat: MAT.rail, albedo: 0.3, id: 1.5 })));
    // drips hanging from the lip
    const drips = new Builder();
    for (let k = 0; k < 7; k++) {
      const a = Math.PI / 4 + (k - 3) * 0.16, x = R * Math.cos(a), z = R * Math.sin(a), y = cy + droop(x, z);
      const len = 0.8 + 2.2 * hash(k, 3);
      drips.box(x - 0.12, y - len, z - 0.12, x + 0.12, y, z + 0.12);
    }
    st.scene.add(new THREE.Mesh(drips.geometry(), eng.material({ mat: MAT.brass, albedo: 0.8, id: 1.7 })));

    // ---- the hands: A (minute) on the face from the centre, D (hour) really 6 up and 6 across, ending (open) at E
    const ha = new Builder();
    const hand = (b, x0, z0, x1, z1, y, w, skipEnd) => b.box(x0, y - 0.22, z0 - (x1 > x0 ? w : 0), x1 + (z1 > z0 ? w : 0), y, z1 + (x1 > x0 ? w : 0), { skip: skipEnd || '' });
    ha.box(-HW, Y0 - 0.25, -HW, AX - HW, Y0, HW);                                   // minute hand (leg A) + hub
    ha.box(AX - HW - 0.02, Y0 - 0.25, -HW * 0.5, AX + 0.5, Y0 - 0.05, HW * 0.5);     // arrow tip under the flight
    st.scene.add(new THREE.Mesh(ha.geometry(), eng.material({ mat: MAT.rail, albedo: 0.42, id: 2.1 })));
    const hd = new Builder();
    hd.box(XD - HW, Y0 + K - 0.25, ZBC - HW, XD + HW, Y0 + K, D_END, { skip: 'pz' });   // hour hand (leg D), open end
    st.scene.add(new THREE.Mesh(hd.geometry(), eng.material({ mat: MAT.rail, albedo: 0.42, id: 2.3, push: dPush })));
    const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.9, 0.9, 0.3, 24, 1), eng.material({ mat: MAT.brass, albedo: 0.85, id: 2.5 }));
    hub.position.set(0, Y0 + 0.05, 0); st.scene.add(hub);
    // ---- the two flights between the hands' tips (stone, gold in colour)
    const stairs = (start, dir, baseY) => {
      const b = new Builder(), perp = V(-dir.z, 0, dir.x);
      const P = (a, y, c) => V(start.x + dir.x * a + perp.x * c, y, start.z + dir.z * a + perp.z * c);
      for (let i = 0; i < NSTEP; i++) {
        const id = b.newId(), a0 = i * RUN, a1 = (i + 1) * RUN, yb = start.y + i * RISE, yt = yb + RISE;
        b.quad(P(a0, yt, -HW), P(a1, yt, -HW), P(a1, yt, HW), P(a0, yt, HW), id, V(0, 1, 0));
        b.quad(P(a0, yb, -HW), P(a0, yt, -HW), P(a0, yt, HW), P(a0, yb, HW), id, dir.clone().negate());
        b.quad(P(a0, baseY, HW), P(a1, baseY, HW), P(a1, yt, HW), P(a0, yt, HW), id, perp);
        b.quad(P(a0, baseY, -HW), P(a1, baseY, -HW), P(a1, yt, -HW), P(a0, yt, -HW), id, perp.clone().negate());
        b.quad(P(a0, baseY, -HW), P(a1, baseY, -HW), P(a1, baseY, HW), P(a0, baseY, HW), id, V(0, -1, 0));
      }
      return b;
    };
    const fl = stairs(V(AX, Y0, -HW), V(0, 0, -1), Y0 - 1.2);
    const landing = new Builder();
    landing.box(AX - HW, Y0 - 1.2, -HW, AX + HW, Y0, HW);
    landing.box(AX - HW, Y0 + 1.8, ZBC - HW, AX + HW, Y0 + 3, ZBC + HW);
    landing.box(XD - HW, Y0 + 4.8, ZBC - HW, XD + HW, Y0 + K, ZBC + HW);
    const fc = stairs(V(AX - HW, Y0 + 3, ZBC), V(-1, 0, 0), Y0 + 1.8);
    for (const b of [fl, fc, landing]) st.scene.add(new THREE.Mesh(b.geometry(), eng.material({ mat: MAT.stone, albedo: 0.93, id: 3.1 })));

    path = loopPath();
    for (let i = 0; i < 8; i++) { const f = makeFigure(st.eng, 'agent'); st.scene.add(f.root); agents.push(f); }
    return meta;
  }

  const songTime = (lt, env) => (env && Number.isFinite(env.t) ? env.t : params.from + lt);

  function update(s) {
    // camera: rotates with her gesture (two big arcs) and clunks into the magic angle on the snap
    const u = clamp((s - params.from) / (params.snap - params.from));
    const k = clunk(u);
    const az = ISO_AZ + (1 - k) * 1.45 + 0.25 * Math.sin(u * Math.PI) * (1 - k);
    const el = lerp(0.22, 0.6155, k);
    const viewH = lerp(24, 20.5, smoother(params.from, params.snap + 1.5, s));
    st.setCamera(V(5.2, 3.8, -3.0), viewH, az, el);
    // agents drip off the melting lip onto the circuit after the snap, then march
    const L = path.length;
    for (let i = 0; i < agents.length; i++) {
      const f = agents[i];
      const tLand = params.snap + 0.1 + i * 0.14;
      const sl = (i / agents.length) * L + 1.4 * Math.max(0, s - tLand);
      const a = path.at(sl);
      const fall = Math.max(0, tLand - s);
      f.root.visible = s > tLand - 0.6;
      f.root.position.copy(a.p).add(V(0, 9.81 * 0.5 * fall * fall * 3.0, 0));
      f.root.rotation.y = Math.atan2(a.dir.x, a.dir.z);
      f.pose(sl / 0.66 * Math.PI * 2, s > tLand ? 1 : 0, 1);
      f.pushConst.value = loopPush(path, sl);
    }
  }

  function draw(lt, env) {
    const s = songTime(lt, env);
    update(s);
    st.render({ seed: boilSeed(s, 1000), target: st.target, bloomAll: params.color, sun: { x: 250, y: 165, r: 84 } });
  }
  function anchors(lt, env) { const s = songTime(lt, env); update(s); return { center: st.project(V(0, Y0, 0)), pixelsPerUnit: st.pixelsPerUnit(), magic: st.magic }; }
  function dispose() { st.dispose(); }
  return { meta, init, draw, anchors, dispose, get stage() { return st; } };
}

const inst = createScene();
export const meta = inst.meta;
export const init = inst.init, draw = inst.draw, anchors = inst.anchors, dispose = inst.dispose;
export default inst;
