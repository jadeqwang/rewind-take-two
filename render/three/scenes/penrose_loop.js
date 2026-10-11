// Scene 1 - "Penrose Loop".
// Isometric diorama of a Loop block: L girders, Escher's Ascending and Descending as a Penrose circuit
// (two stair flights + two L-track legs that climb K=6 per lap and close only at the magic angle).
// Six agents march it forever. Mid-clip the camera orbits away (the seam visibly splits: leg D hangs
// in mid-air 6 units in front of its own start), then snaps back into alignment.
//
// Interface (render/engine): init(renderer, params) -> meta ; draw(t) renders into the renderer's
// current render target ; anchors(t) -> screen positions for compositing ; dispose().
// t is seconds, deterministic. The clip loops seamlessly with period meta.loop (10 s).
import * as THREE from 'three';
import { Stage, ISO_AZ, ISO_EL, boilSeed } from '../lib/stage.js';
import { createLoopSet, loopPath, loopPush, PIVOT } from '../lib/loopset.js';
import { makeFigure } from '../lib/figures.js';
import { clunk, smoother, inv } from '../lib/util.js';

export const meta = { name: 'penrose_loop', duration: 10, fps: 24, loop: 10, width: 1920, height: 1080, output: 'srgb' };

export function createScene() {
  let st, path, agents, L, v, s0, stride, params;
  const N = 6, LAP = 30;

  function init(renderer, p = {}) {
    params = { orbit: true, orbitAz: 0.65, orbitEl: -0.2, color: 0, pull: null, pullDur: 7.28, pullFrom: [12.6, 4.6, -3.6], ...p };
    if (typeof params.pull === 'string') params.pull = params.pull.split(',').map(Number);
    if (params.pull) { params.orbit = false; meta.duration = params.pullDur; }
    st = new Stage(renderer, params);
    const set = createLoopSet(st.eng, { turntable: true, spur: false, exit: false });
    st.scene.add(set.root);
    st.eng.fitShadow(new THREE.Vector3(7, 4, -3), 24);
    path = loopPath();
    L = path.length; v = L / LAP;
    // phase so that seam crossings happen at t = 1.5 + 5k: none while the illusion is broken (1.8..6.4 s)
    s0 = L - 1.5 * v;
    const travel = v * meta.loop;
    stride = travel / Math.round(travel / 0.66);
    agents = [];
    for (let i = 0; i < N; i++) { const f = makeFigure(st.eng, 'agent'); st.scene.add(f.root); agents.push(f); }
    return meta;
  }

  function camAt(t) {
    const out = smoother(1.8, 3.8, t);
    const back = clunk(inv(4.6, 6.4, t));
    const k = t < 4.6 ? out : 1 - back;
    const drift = t > 3.8 && t < 4.6 ? 0.02 * Math.sin((t - 3.8) / 0.8 * Math.PI) : 0;
    const az = ISO_AZ + (params.orbitAz + drift) * k; // default ~37 degrees off the magic azimuth
    const el = ISO_EL + params.orbitEl * k;
    const tgt = new THREE.Vector3(6.6, 5.0, -3.2);
    return { az, el, tgt, viewH: 25 + 1.0 * k };
  }

  function update(t) {
    let c = params.orbit ? camAt(t) : { az: ISO_AZ, el: ISO_EL, tgt: new THREE.Vector3(6.6, 5.0, -3.2), viewH: 25 };
    if (params.pull) {
      // O1: slow pull-back from the agents climbing flight B to the whole circuit (pull = [viewH start, viewH end])
      const u = smoother(0, params.pullDur, t), e = 1 - Math.pow(1 - u, 1.6);
      c = { az: ISO_AZ, el: ISO_EL, viewH: params.pull[0] + (params.pull[1] - params.pull[0]) * e,
        tgt: new THREE.Vector3(...params.pullFrom).lerp(new THREE.Vector3(6.6, 5.4, -3.2), e) };
    }
    st.setCamera(c.tgt, c.viewH, c.az, c.el);
    const phase = (v * t) / stride * Math.PI * 2;
    for (let i = 0; i < N; i++) {
      const s = s0 + i * L / N + v * t;
      const a = path.at(s);
      const f = agents[i];
      f.root.position.copy(a.p);
      f.root.rotation.y = Math.atan2(a.dir.x, a.dir.z);
      f.pose(phase, 1, 1);
      f.pushConst.value = loopPush(path, s);
    }
  }

  function draw(t) {
    update(t);
    st.render({ seed: boilSeed(t, meta.loop), sun: { x: 250, y: 165, r: 64 }, target: st.target, bloomAll: params.color });
  }

  // compositing anchors: where a 2D Jade billboard could stand (the seam corner and the turntable)
  function anchors(t) {
    update(t);
    const seam = st.project(path.at(0).p), pivot = st.project(PIVOT);
    return { seam, pivot, pixelsPerUnit: st.pixelsPerUnit(), magic: st.magic };
  }

  function dispose() { st.dispose(); }
  return { meta, init, draw, anchors, dispose, get stage() { return st; } };
}

const inst = createScene();
export const init = inst.init, draw = inst.draw, anchors = inst.anchors, dispose = inst.dispose;
export default inst;
