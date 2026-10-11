// Scene 2 - "Rotate to connect" (and, with bloom, Scene 3 - "Color bloom").
//
// Monument Valley mechanic on the Loop diorama. A crank-driven turntable bridge sits in leg A of the
// Penrose circuit. Jade (placeholder: white jacket, orange band) walks in on her own L spur; the bridge
// is rotated 90 degrees and, at the magic isometric angle, its far end lines up with a street-level stoop
// that is really J_DROP*(1,1,1) = 2 units lower and further back. She walks across the impossible joint
// and into a door. The crank turns again with the pursuing agent standing on the bridge: it swings him
// round into leg A and he joins the agents marching the infinite loop.
//
// Motion is simulated once at init (fixed 240 Hz steps, deterministic); draw(t) samples it.
import * as THREE from 'three';
import { Stage, ISO_AZ, ISO_EL, boilSeed } from '../lib/stage.js';
import { createLoopSet, loopPath, loopPush, PIVOT, BR_HALF, P2_START, DOOR_Z, Y0 } from '../lib/loopset.js';
import { makeFigure } from '../lib/figures.js';
import { clunk, smoother, clamp } from '../lib/util.js';

const DT = 1 / 240;

export function createScene(defaults = {}) {
  const meta = { name: defaults.bloom ? 'color_bloom' : 'rotate_connect', duration: 10, fps: 24, width: 1920, height: 1080 };
  let st, set, path, sim, figs, params, jade, pursuer, loopers;

  // ---------------------------------------------------------------- timeline
  const ROT1 = [1.15, 2.75];         // bridge 0 -> -90 deg: Jade's spur joins the stoop (magic joint)
  let ROT2 = [4.95, 6.45];           // bridge -90 -> -180 deg: back into leg A, carrying the pursuer
  const theta = (t) => {
    const a = -Math.PI / 2 * clunk((t - ROT1[0]) / (ROT1[1] - ROT1[0]));
    const b = -Math.PI / 2 * clunk((t - ROT2[0]) / (ROT2[1] - ROT2[0]));
    return a + b;
  };
  const connectedP2 = (t) => t >= ROT1[1] && t < ROT2[0];
  const loopClosed = (t) => t < ROT1[0] || t >= ROT2[1];

  function simulate() {
    const n = Math.ceil(meta.duration / DT) + 2;
    const rec = (k) => ({ x: new Float32Array(n), y: new Float32Array(n), z: new Float32Array(n), h: new Float32Array(n), d: new Float32Array(n), g: new Float32Array(n), push: new Float32Array(n), vis: new Uint8Array(n), kind: k });
    const L = path.length, gap0 = PIVOT.x - BR_HALF, gap1 = PIVOT.x + BR_HALF;
    const vLoop = 1.0, vJade = 1.2, vPur = 1.5;
    // loop agents: initial arc positions chosen so the bridge is clear when it first turns
    const sLoop = [3.2, 12.0, 19.5, 27.5, 35.0].map((s) => s);
    const A = sLoop.map((s) => ({ s, d: 0, g: 1, r: rec('agent') }));
    const J = { z: 4.55, onP2: false, pz: 0, d: 0, g: 1, done: false, r: rec('jade') };
    const P = { mode: 'spur', z: 8.0, lx: 0, th0: 0, s: 0, d: 0, g: 1, r: rec('agent') };
    let jadeTeleport = null;
    const put = (o, i, p, head, push = 0, vis = 1) => {
      o.r.x[i] = p.x; o.r.y[i] = p.y; o.r.z[i] = p.z; o.r.h[i] = head; o.r.d[i] = o.d; o.r.g[i] = o.g; o.r.push[i] = push; o.r.vis[i] = vis;
    };
    const gaitTo = (o, moving) => { o.g += ((moving ? 1 : 0) - o.g) * Math.min(1, DT / 0.12); };
    for (let i = 0; i < n; i++) {
      const t = i * DT;
      // --- Jade
      if (!J.onP2) {
        let nz = J.z - vJade * DT;
        if (!connectedP2(t) && nz < BR_HALF + 0.2) nz = Math.max(J.z, Math.min(J.z, BR_HALF + 0.2));
        const moving = nz < J.z - 1e-6; J.d += J.z - nz; J.z = nz; gaitTo(J, moving);
        if (J.z <= -BR_HALF) { J.onP2 = true; J.pz = P2_START.z - (-BR_HALF - J.z); jadeTeleport = t; }
        put(J, i, new THREE.Vector3(PIVOT.x, Y0, J.z), Math.PI);
      } else {
        let nz = J.pz - vJade * DT; const moving = !J.done;
        if (J.pz < DOOR_Z + 0.25) J.done = true;
        if (!J.done) { J.d += vJade * DT; J.pz = nz; }
        gaitTo(J, moving);
        put(J, i, new THREE.Vector3(P2_START.x, P2_START.y, J.pz), Math.PI, 0, J.pz > DOOR_Z + 0.3 ? 1 : 0);
      }
      // --- pursuer
      const th = theta(t);
      if (P.mode === 'spur') {
        const nz = P.z - vPur * DT;
        P.d += vPur * DT; P.z = nz; gaitTo(P, true);
        if (P.z <= BR_HALF) { P.mode = 'bridge'; P.lx = P.z; }
        put(P, i, new THREE.Vector3(PIVOT.x, Y0, P.z), Math.PI);
      } else if (P.mode === 'bridge') {
        // walks the bridge (local x = world z at -90 deg) until the crank turns, then rides it
        const rotating = t >= ROT2[0];
        if (!rotating) { P.lx -= vPur * DT; P.d += vPur * DT; }
        gaitTo(P, !rotating);
        const c = Math.cos(th), s = Math.sin(th);
        // bridge frame: local (lx,0,0) -> world (lx cos, 0, -lx sin)
        const p = new THREE.Vector3(PIVOT.x + P.lx * c, Y0, PIVOT.z - P.lx * s);
        // heading: walking toward local -x
        const dir = new THREE.Vector3(-c, 0, s);
        put(P, i, p, Math.atan2(dir.x, dir.z));
        if (t >= ROT2[1]) { P.mode = 'loop'; P.s = p.x; }
      } else {
        P.s += vLoop * DT; P.d += vLoop * DT; gaitTo(P, true);
        const a = path.at(P.s);
        put(P, i, a.p, Math.atan2(a.dir.x, a.dir.z), loopPush(path, P.s));
      }
      // --- loop agents: march, queue at the gap while the bridge is away, keep spacing
      const order = A.map((a, k) => k).sort((a, b) => A[a].s - A[b].s);
      for (const k of order) {
        const a = A[k];
        let ns = a.s + vLoop * DT;
        const sm = ((ns % L) + L) % L;
        if (!loopClosed(t) && sm > gap0 - 0.55 && sm < gap1 && ((a.s % L) + L) % L <= gap0 - 0.55 + 1e-4) ns = a.s;
        // spacing behind any walker ahead on the loop (other agents and the pursuer once he is on it)
        for (const b of A) if (b !== a) { const ds = ((b.s - ns) % L + L) % L; if (ds < 0.85 && ds > 0) ns = Math.min(ns, a.s); }
        if (P.mode === 'loop') { const ds = ((P.s - ns) % L + L) % L; if (ds < 0.85 && ds > 0) ns = Math.min(ns, a.s); }
        const moving = ns > a.s + 1e-7; a.d += ns - a.s; a.s = ns; gaitTo(a, moving);
        const p = path.at(a.s);
        put(a, i, p.p, Math.atan2(p.dir.x, p.dir.z), loopPush(path, a.s));
      }
    }
    return { n, A, J, P, jadeTeleport };
  }

  function init(renderer, p = {}) {
    params = { bloom: false, ...defaults, ...p };
    st = new Stage(renderer, params);
    set = createLoopSet(st.eng, { turntable: true, spur: true, exit: true });
    st.scene.add(set.root);
    st.eng.fitShadow(new THREE.Vector3(7, 4, -3), 24);
    path = loopPath();
    sim = simulate();
    jade = makeFigure(st.eng, 'jade');
    pursuer = makeFigure(st.eng, 'agent');
    loopers = sim.A.map(() => makeFigure(st.eng, 'agent'));
    figs = [[jade, sim.J.r], [pursuer, sim.P.r], ...loopers.map((f, k) => [f, sim.A[k].r])];
    for (const [f] of figs) st.scene.add(f.root);
    meta.jadeTeleport = sim.jadeTeleport;
    return meta;
  }

  function camAt(t) {
    if (params.bloom) {
      // wider: the colour has the whole Loop to flood. A slow settle-in keeps it alive.
      const k = smoother(0, 10, t);
      return { tgt: new THREE.Vector3(6.8, 5.6, -3.2), viewH: 25.5 - 2.0 * k };
    }
    const k = smoother(0, 10, t);
    return { tgt: new THREE.Vector3(8.4 - 0.4 * k, 2.6, -1.4), viewH: 15.5 - 0.8 * k };
  }

  function update(t) {
    const c = camAt(t);
    st.setCamera(c.tgt, c.viewH, ISO_AZ, ISO_EL);
    const th = theta(t);
    set.tt.bridge.rotation.y = th;
    set.tt.crank.rotation.z = th * 4;
    const i = Math.max(0, Math.min(sim.n - 1, Math.round(t / DT)));
    for (const [f, r] of figs) {
      f.root.visible = !!r.vis[i];
      f.root.position.set(r.x[i], r.y[i], r.z[i]);
      f.root.rotation.y = r.h[i];
      f.pose(r.d[i] / 0.66 * Math.PI * 2, r.g[i], f.kind === 'agent' ? 1 : 0);
      f.pushConst.value = r.push[i];
    }
  }

  // colour bloom: starts when the joint locks, floods out from the pivot
  function bloomAt(t) {
    if (!params.bloom) return null;
    const pv = st.project(new THREE.Vector3(PIVOT.x, Y0, PIVOT.z));
    const u = clamp((t - (ROT1[1] - 0.25)) / 6.2);
    const r = 2600 * (u * u * (3 - 2 * u)) * (0.35 + 0.65 * u);
    return { x: pv.x, y: pv.y, r };
  }

  function draw(t) {
    update(t);
    const b = bloomAt(t);
    st.render({ seed: boilSeed(t, meta.duration), bloom: b && b.r > 0 ? b : null, target: st.target, sun: { x: 250, y: 165, r: params.bloom ? 84 : 64 } });
  }

  // compositing anchors: Jade's feet in output pixels (for a 2D sprite), her depth and scale
  function anchors(t) {
    update(t);
    const i = Math.max(0, Math.min(sim.n - 1, Math.round(t / DT)));
    const r = sim.J.r;
    const feet = new THREE.Vector3(r.x[i], r.y[i], r.z[i]);
    return {
      jade: { ...st.project(feet), visible: !!r.vis[i], heading: r.h[i], world: feet.toArray() },
      pivot: st.project(new THREE.Vector3(PIVOT.x, Y0, PIVOT.z)),
      pixelsPerUnit: st.pixelsPerUnit(), bridgeAngle: theta(t), magic: st.magic,
    };
  }

  function dispose() { st.dispose(); }
  return { meta, init, draw, anchors, dispose, get stage() { return st; } };
}

const inst = createScene();
export const meta = inst.meta;
export const init = inst.init, draw = inst.draw, anchors = inst.anchors, dispose = inst.dispose;
export default inst;
