// Section E, M2 (159.14-165.18): Mobius Lake Shore Drive (Escher's Mobius Strip II).
//
// Lake Shore Drive is a Mobius band floating over the engraved lake. The agency's black sedans speed round it; on the
// second lap they are on the other face, upside down (Escher's ants). The join is a crank-turned segment that pivots on
// the band's incoming end: at first it points out of the loop onto an exit road toward Jade, and the lead sedan is
// heading for it. In the instrumental hole (161.63-162.27, under "down Lake") Jade turns the crank; the segment clunks
// round on the 162.30 chord stab, carrying the lead car back into the band: they loop forever.
// The lyric "I'm speeding down Lake Shore, I dreamt" is painted on the road surface, each word appearing as it is sung,
// and it follows the twist.
import * as THREE from 'three';
import { Stage, ISO_AZ, ISO_EL, boilSeed } from '../lib/stage.js';
import { Builder, V } from '../lib/build.js';
import { MAT } from '../lib/engrave.js';
import { SpriteActor, loadJadeSprites } from '../lib/sprite.js';
import { WORDS, bb } from '../lib/songgrid.js';
import { clunk, smoother, smooth, clamp, lerp } from '../lib/util.js';

const START = 159.14, END = 165.18;
const R = 3.4, HWB = 0.72, Y = 2.2;              // band radius, half width, height above the lake
const UJ = 0;                                      // the join sits at the right-front of the loop
const DEL = 0.30;                                  // half-angle of the join gap
const ROT0 = 161.72, ROT1 = bb(93, 1);             // crank turn: lands on the 162.30 stab
const LANE = 0.34;                                 // cars drive in the right-hand lane (v offset)

// band geometry (u unbounded: b is 4*pi periodic, so the face flips after one lap, as on a real Mobius strip)
const C = (u) => V(R * Math.cos(u), Y, R * Math.sin(u));
const Tn = (u) => V(-Math.sin(u), 0, Math.cos(u));
const TWISTS = 3;                                   // half-twists (odd = one-sided: a Mobius band)
// the half-twists are concentrated on the left of the loop (u' in [0.30, 0.64] of a lap); front and back stay flat
const twistA = (u) => { const w = (u - UJ) / (2 * Math.PI), k = Math.floor(w), f = w - k; const g = Math.min(1, Math.max(0, (f - 0.22) / 0.46)); return TWISTS * Math.PI * (k + g * g * (3 - 2 * g)); };
const Bv = (u) => { const r = V(Math.cos(u), 0, Math.sin(u)), a = twistA(u); return r.multiplyScalar(Math.cos(a)).add(V(0, Math.sin(a), 0)); };
const Nv = (u) => new THREE.Vector3().crossVectors(Bv(u), Tn(u)).normalize();   // +y at the join on lap 0
const P = (u, v) => C(u).addScaledVector(Bv(u), v);

export function createScene(defaults = {}) {
  const meta = { name: 'e_mobius', duration: END - START, fps: 24, width: 1920, height: 1080, output: 'srgb' };
  let st, params, seg, segPivot, cars = [], jade, textCanvas, textTex, crank, fontOK = false;
  const E_IN = P(UJ - DEL, 0), E_OUT = P(UJ + DEL, 0);
  const dB = new THREE.Vector3().subVectors(E_OUT, E_IN).normalize();
  const segLen = E_IN.distanceTo(E_OUT);
  const OUTW = V(Math.cos(UJ), 0, Math.sin(UJ));
  // state A direction: the segment swung 90 deg off the chord, pointing out of the loop
  const dA = V(dB.z, 0, -dB.x); if (dA.dot(OUTW) < 0) dA.negate();
  const thA = Math.atan2(-dA.z, dA.x), thB = Math.atan2(-dB.z, dB.x);   // rotation.y that maps local +x to dA / dB

  async function init(renderer, p = {}) {
    params = { textFlipX: false, textFlipY: false, ...defaults, ...p };
    st = new Stage(renderer, params);
    const eng = st.eng;
    st.eng.fitShadow(V(0, 1, 0), 14);
    // lyric font
    try {
      const f = new FontFace('IMFellE', 'url(/render/fonts/IMFeENrm28P.ttf)');
      await f.load(); document.fonts.add(f); fontOK = true;
    } catch (e) { fontOK = false; }
    textCanvas = new OffscreenCanvas(8192, 512);
    textTex = new THREE.CanvasTexture(textCanvas); textTex.colorSpace = THREE.NoColorSpace; textTex.anisotropy = 8;
    textTex.wrapS = THREE.ClampToEdgeWrapping;

    // ---- lake + shore
    const water = new Builder(); water.box(-14, -0.6, -14, 14, 0, 14, { skip: 'px nx pz nz ny' });
    st.scene.add(new THREE.Mesh(water.geometry(), eng.material({ mat: MAT.water, albedo: 0.78, id: 1.1 })));
    const shore = new Builder();
    shore.box(-14, 0, -14, -6.5, 0.5, 14, { skip: 'nx ny pz nz' });           // the city side
    shore.box(-6.5, 0, -14, -6.2, 0.35, 14, { skip: 'ny pz nz' });           // breakwater step
    st.scene.add(new THREE.Mesh(shore.geometry(), eng.material({ mat: MAT.ground, albedo: 0.92, id: 1.3 })));
    const city = new Builder();
    const bl = [[-12, -12, -8.5, -8, 6], [-12, -7.5, -8.8, -3.5, 9], [-12, -3, -9.2, 1, 5], [-12, 1.5, -8.6, 5.5, 7.5], [-12, 6, -9, 10, 4.5]];
    for (const [x0, z0, x1, z1, h] of bl) city.box(x0, 0.5, z0, x1, 0.5 + h, z1);
    st.scene.add(new THREE.Mesh(city.geometry(), eng.material({ mat: MAT.brick, albedo: 0.86, id: 1.5, windows: { cell: [0.8, 1.15], glass: [0.6, 0.55], box: [-12, -12, 3.5, 22], y: [1.0, 9], chicago: true } })));

    // ---- the Mobius band (open at the join), with uv for the painted lyric
    const NU = 520, NV = 6, u0 = UJ + DEL, u1 = UJ + 2 * Math.PI - DEL;
    const pos = [], nor = [], uv = [], idx = [];
    for (let i = 0; i <= NU; i++) {
      const u = u0 + (u1 - u0) * i / NU, n = Nv(u);
      for (let j = 0; j <= NV; j++) {
        const v = -HWB + 2 * HWB * j / NV, q = P(u, v);
        pos.push(q.x, q.y, q.z); nor.push(n.x, n.y, n.z);
        uv.push((u - UJ) / (2 * Math.PI), j / NV);
      }
    }
    for (let i = 0; i < NU; i++) for (let j = 0; j < NV; j++) {
      const a = i * (NV + 1) + j, b = a + NV + 1;
      idx.push(a, b, a + 1, b, b + 1, a + 1);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
    g.setIndex(idx);
    st.scene.add(new THREE.Mesh(g, eng.material({ mat: MAT.road, albedo: 0.95, id: 2.1, side: THREE.DoubleSide, decal: textTex, flatLight: 0.75 })));
    // kerbs: thin walls along both edges of the band (they make the twist legible)
    for (const sgn of [-1, 1]) {
      const kp = [], kn = [], ki = [];
      for (let i = 0; i <= NU; i++) {
        const u = u0 + (u1 - u0) * i / NU, n = Nv(u), b = Bv(u);
        for (const [dv, dn] of [[0, 0], [0, 0.09], [0.05 * sgn, 0.09], [0.05 * sgn, 0]]) {
          const q = P(u, sgn * HWB + dv).addScaledVector(n, dn); kp.push(q.x, q.y, q.z);
        }
      }
      // build quads between rings of 4 points (3 faces)
      const kb = new Builder();
      for (let i = 0; i < NU; i++) for (let f = 0; f < 3; f++) {
        const a = (k) => V(kp[(i * 4 + k) * 3], kp[(i * 4 + k) * 3 + 1], kp[(i * 4 + k) * 3 + 2]);
        const c = (k) => V(kp[((i + 1) * 4 + k) * 3], kp[((i + 1) * 4 + k) * 3 + 1], kp[((i + 1) * 4 + k) * 3 + 2]);
        kb.quad(a(f), c(f), c(f + 1), a(f + 1), 0);
      }
      st.scene.add(new THREE.Mesh(kb.geometry(), eng.material({ mat: MAT.steel, albedo: 0.7, id: 2.3 + sgn * 0.1, side: THREE.DoubleSide })));
    }
    // pylons holding the band over the lake (at the join side only: the far side floats, it is a drawing)
    const py = new Builder();
    for (const u of [UJ + 0.9, UJ - 0.9, UJ + 2.4, UJ - 2.4]) { const q = P(u, 0); py.box(q.x - 0.12, 0, q.z - 0.12, q.x + 0.12, Math.min(q.y, Y) - 0.15, q.z + 0.12); }
    st.scene.add(new THREE.Mesh(py.geometry(), eng.material({ mat: MAT.steel, albedo: 0.7, id: 2.7 })));

    // ---- the join: segment on a turntable pivoting at the band's incoming end, the exit road, the crank pier
    segPivot = new THREE.Group(); segPivot.position.copy(E_IN); st.scene.add(segPivot);
    const sb = new Builder();
    sb.box(-0.05, -0.16, -HWB, segLen + 0.02, 0, HWB, { skip: '' });
    sb.box(0, 0, -HWB, segLen, 0.09, -HWB + 0.05); sb.box(0, 0, HWB - 0.05, segLen, 0.09, HWB);
    seg = new THREE.Mesh(sb.geometry(), eng.material({ mat: MAT.road, albedo: 0.9, id: 3.1, side: THREE.DoubleSide }));
    segPivot.add(seg);
    const drum = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.5, Y - 0.16, 20, 1), eng.material({ mat: MAT.brass, albedo: 0.78, id: 3.3 }));
    drum.position.set(E_IN.x, (Y - 0.16) / 2, E_IN.z); st.scene.add(drum);
    // exit road: from the state-A end of the segment, straight out toward the shore and Jade's pier
    const xs = E_IN.clone().addScaledVector(dA, segLen + 0.02), xe = xs.clone().addScaledVector(dA, 6);
    const ex = new Builder(), perp = V(-dA.z, 0, dA.x);
    const q = (a, s, y) => a.clone().addScaledVector(perp, s).setY(y);
    ex.quad(q(xs, -HWB, Y), q(xe, -HWB, Y), q(xe, HWB, Y), q(xs, HWB, Y), 1, V(0, 1, 0));
    ex.quad(q(xs, -HWB, Y - 0.16), q(xe, -HWB, Y - 0.16), q(xe, -HWB, Y), q(xs, -HWB, Y), 2, perp.clone().negate());
    ex.quad(q(xs, HWB, Y - 0.16), q(xe, HWB, Y - 0.16), q(xe, HWB, Y), q(xs, HWB, Y), 2, perp);
    for (const k of [1.6, 4.0]) { const c0 = xs.clone().addScaledVector(dA, k); ex.box(c0.x - 0.12, 0, c0.z - 0.12, c0.x + 0.12, Y - 0.16, c0.z + 0.12); }
    st.scene.add(new THREE.Mesh(ex.geometry(), eng.material({ mat: MAT.road, albedo: 0.9, id: 3.5 })));
    // Jade's pier beside the pivot, with the crank
    const pierC = E_IN.clone().addScaledVector(dB, -1.25).addScaledVector(OUTW, 1.05);
    const pb = new Builder();
    pb.box(pierC.x - 0.75, 0, pierC.z - 0.75, pierC.x + 0.75, Y, pierC.z + 0.75);
    st.scene.add(new THREE.Mesh(pb.geometry(), eng.material({ mat: MAT.stone, albedo: 0.92, id: 3.7 })));
    crank = new THREE.Group(); crank.position.set(pierC.x + 0.38, Y + 0.72, pierC.z - 0.3); st.scene.add(crank);
    const cp = new Builder();
    cp.box(-0.08, -0.72, -0.08, 0.08, -0.05, 0.08);
    { const cpm = new THREE.Mesh(cp.geometry(), eng.material({ mat: MAT.brass, albedo: 0.7, id: 3.9 })); cpm.position.copy(crank.position); st.scene.add(cpm); }
    const ck = new Builder(); ck.box(-0.03, -0.05, -0.03, 0.03, 0.04, 0.03); ck.box(-0.03, 0.0, -0.03, 0.34, 0.05, 0.03); ck.box(0.29, 0.0, -0.04, 0.35, 0.2, 0.04);
    crank.add(new THREE.Mesh(ck.geometry(), eng.material({ mat: MAT.brass, albedo: 0.66, id: 4.1 })));
    this_pier = pierC;

    // ---- sedans (the agency's black cars) with an agent silhouette inside
    for (let k = 0; k < 3; k++) {
      const grp = new THREE.Group();
      const cb = new Builder();
      cb.box(-0.3, 0.05, -0.14, 0.3, 0.17, 0.14);           // body (local x forward, y up)
      cb.box(-0.14, 0.17, -0.12, 0.12, 0.28, 0.12);         // cabin
      for (const [x, z] of [[0.18, 0.15], [-0.18, 0.15], [0.18, -0.15], [-0.18, -0.15]]) cb.box(x - 0.06, 0, z - 0.02, x + 0.06, 0.1, z + 0.02);
      grp.add(new THREE.Mesh(cb.geometry(), eng.material({ mat: MAT.car, albedo: 0.18, id: 5 + k })));
      const wb = new Builder(); wb.box(0.12, 0.18, -0.11, 0.125, 0.27, 0.11); wb.box(-0.145, 0.18, -0.11, -0.14, 0.27, 0.11);
      grp.add(new THREE.Mesh(wb.geometry(), eng.material({ mat: MAT.shirt, albedo: 0.95, id: 5.5 + k })));
      grp.scale.setScalar(1.75);
      st.scene.add(grp); cars.push(grp);
    }
    // ---- Jade
    jade = new SpriteActor(st.eng, params.sprites === false ? {} : await loadJadeSprites());
    st.scene.add(jade.root);
    meta.jadeSprite = !jade.fallback;
    return meta;
  }
  let this_pier;

  // ---------------------------------------------------------------- the lyric painted on the road
  // u-range of the band (texture x = (u-UJ)/2pi): the words run round the back of the loop, left to right on screen
  function paintText(s) {
    const g = textCanvas.getContext('2d');
    g.clearRect(0, 0, 8192, 512);
    const fs = 150;
    g.font = `${fs}px ${fontOK ? 'IMFellE' : 'serif'}`;
    g.textBaseline = 'middle';
    // centre-line dashes (painted road)
    g.fillStyle = 'rgba(0,0,0,0.85)';
    for (let x = 0; x < 8192; x += 180) g.fillRect(x, 250, 80, 12);
    // the lyric runs along the flat back stretch of the loop (u = 215..345 deg), left to right on screen
    const words = WORDS.filter((w) => w[1] > 160.9 && w[1] < 164.5);
    const gap = fs * 0.36;
    const total = words.reduce((acc, w) => acc + g.measureText(w[0]).width + gap, -gap);
    const uMid = (277 / 360) * 8192;
    let x = uMid - total / 2;
    for (const [w, ws] of words) {
      const width = g.measureText(w).width;
      const a = clamp((s - ws) * 12);                       // 2-frame ink bleed in
      // orientation on screen of the texture axes at this word (u -> texture x, v -> texture up)
      const u = UJ + (x + width / 2) / 8192 * 2 * Math.PI;
      const p0 = st.project(P(u, 0)), pu = st.project(P(u + 0.01, 0)), pv = st.project(P(u, 0.05));
      const fx = (pu.x - p0.x) < 0, fy = (pv.y - p0.y) > 0;  // screen y grows downward
      if (a > 0) {
        g.save(); g.globalAlpha = a;
        g.clearRect(x - 10, 70, width + 20, 372);           // the dashes make way for the word
        g.fillStyle = '#000';
        g.translate(x + width / 2, 256); g.scale(fx ? -1 : 1, fy ? -1 : 1);
        g.fillText(w, -width / 2, 0);
        g.restore();
      }
      x += width + gap;
    }
    textTex.needsUpdate = true;
  }

  // ---------------------------------------------------------------- motion
  const OMEGA = 1.55;                                     // rad/s: a lap in ~4 s, "speeding"
  const theta = (s) => lerp(thA, thB, clunk((s - ROT0) / (ROT1 - ROT0)));
  function carState(k, s) {
    // unbounded band parameter; the lead car (k=0) reaches the join's incoming end just as Jade starts the crank
    const uArrive = UJ - DEL + 2 * Math.PI * 2;           // lap parity even: on the top face at the join
    const tArrive = ROT0 - 0.05;
    const u = uArrive - OMEGA * (tArrive - s) - k * 1.55;
    const vSeg = OMEGA * R;                                // linear speed
    if (k === 0 && s > tArrive) {
      // on the segment: drives in along state A, brakes while the crank turns, then exits along the chord
      const d = Math.min(vSeg * (s - tArrive), 0.55);
      const th = theta(s);
      const after = s > ROT1 ? vSeg * (s - ROT1) * smooth(ROT1, ROT1 + 0.25, s) : 0;
      const local = d + after;
      if (local < segLen) {
        const dir = V(Math.cos(th), 0, -Math.sin(th));
        return { p: E_IN.clone().addScaledVector(dir, local).addScaledVector(V(-dir.z, 0, dir.x), -LANE), fwd: dir, up: V(0, 1, 0) };
      }
      const uu = UJ + DEL + (local - segLen) / R + 2 * Math.PI * 2;
      return onBand(uu);
    }
    const um = ((u - (UJ - DEL)) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI);
    if (um > 2 * Math.PI - 2 * DEL) {
      // crossing the join on the closed segment (state B) - followers only arrive after the crank
      const f = (um - (2 * Math.PI - 2 * DEL)) / (2 * DEL);
      const lapUp = Nv(u - um).y > 0 ? 1 : -1;
      return { p: E_IN.clone().addScaledVector(dB, f * segLen).addScaledVector(V(-dB.z, 0, dB.x), -LANE * lapUp), fwd: dB.clone(), up: V(0, lapUp, 0) };
    }
    return onBand(u);
  }
  function onBand(u) {
    const n = Nv(u), t = Tn(u);
    const lane = -LANE * Math.sign(n.y || 1) * 0 - LANE;
    return { p: P(u, lane), fwd: t, up: n };
  }

  function songTime(lt, env) { return env && Number.isFinite(env.t) ? env.t : START + lt; }

  function update(s) {
    segPivot.rotation.y = theta(s);
    crank.rotation.y = -(theta(s) - thA) * 4;
    const m = new THREE.Matrix4();
    for (let k = 0; k < cars.length; k++) {
      const c = carState(k, s);
      const z = new THREE.Vector3().crossVectors(c.fwd, c.up).normalize();
      const y = new THREE.Vector3().crossVectors(z, c.fwd).normalize();
      m.makeBasis(c.fwd, y, z);
      cars[k].quaternion.setFromRotationMatrix(m);
      cars[k].position.copy(c.p);
    }
    const cranking = s > ROT0 - 0.12 && s < ROT1 + 0.1;
    const jp = this_pier.clone().setY(Y).addScaledVector(OUTW, -0.05).add(V(-0.1, 0, 0.25));
    jade.update({ pos: jp, dir: V(1, 0, 0), mode: cranking ? 'crank' : 'idle', t: s - START, camAz: ISO_AZ });
    // camera: wide on the loop, in toward Jade and the join for the crank, back out on "Lake Shore"
    const inU = smoother(160.2, ROT0, s) * (1 - smoother(ROT1 + 0.1, 163.4, s));
    const tgt = V(0.2, 1.7, 0.6).lerp(V(1.6, Y + 0.1, -0.2), inU);
    st.setCamera(tgt, lerp(9.6, 7.4, inU), ISO_AZ, ISO_EL);
    paintText(s);
  }

  function draw(lt, env) {
    const s = songTime(lt, env);
    update(s);
    const pj = st.project(this_pier.clone().setY(Y + 0.6));
    const ppu = st.pixelsPerUnit();
    st.render({ seed: boilSeed(s, 1000), target: st.target, sun: params.sun === false ? null : { x: 250, y: 165, r: 64 },
      blooms: [{ x: pj.x, y: pj.y, r: ppu * (0.85 + 0.9 * smooth(ROT0, ROT1 + 0.5, s)) }] });
  }

  function anchors(lt, env) {
    const s = songTime(lt, env); update(s);
    return { jade: st.project(this_pier.clone().setY(Y)), pixelsPerUnit: st.pixelsPerUnit(), join: st.project(E_IN) };
  }
  function dispose() { st.dispose(); }
  return { meta, init, draw, anchors, dispose, get stage() { return st; } };
}

const inst = createScene();
export const meta = inst.meta;
export const init = inst.init, draw = inst.draw, anchors = inst.anchors, dispose = inst.dispose;
export default inst;
