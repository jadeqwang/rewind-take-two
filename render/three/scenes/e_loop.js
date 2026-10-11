// Section E, the Loop diorama shots (one module, params.shot selects the shot):
//
//  G4  148.08-151.62  Kick returns: the camera snaps perspective -> orthographic and clunks 90 degrees into the magic
//                     angle on the kick; the Loop diorama then assembles itself piece by piece on the music-box 16ths,
//                     the impossible leg D landing last (151.18, beat 86:4).
//  M1  151.62-153.98  Continuous from G4: push in to Jade (hair down, pencil) walking the L track; agents enter.
//  M3  165.18-169.40  "a shadow chasing me - it couldn't trace": agents chase her up the spur onto the swing bridge;
//                     she turns the crank on the stoop (95:2), the bridge clunks round and carries them into the Penrose
//                     circuit, where they march Ascending and Descending; pull back on the riser.
//
// Time: the engine calls draw(lt, env) and env.t is the absolute song time; the standalone harness passes local time
// (song time = shot start + t). Every move is keyed to tracked beats (lib/songgrid.js).
import * as THREE from 'three';
import { Stage, ISO_AZ, ISO_EL, boilSeed } from '../lib/stage.js';
import { createLoopSet, loopPath, loopPush, PIVOT, BR_HALF, P2_START, Y0 } from '../lib/loopset.js';
import { makeFigure } from '../lib/figures.js';
import { SpriteActor, loadJadeSprites } from '../lib/sprite.js';
import { bb } from '../lib/songgrid.js';
import { clunk, smoother, smooth, clamp, hash, lerp } from '../lib/util.js';

const SHOTS = { G4: [148.08, 151.62], M1: [151.62, 153.98], M3: [165.18, 169.40] };
const DEG = Math.PI / 180;
const V = (x, y, z) => new THREE.Vector3(x, y, z);

export function createScene(defaults = {}) {
  const meta = { name: 'e_loop', duration: 3.54, fps: 24, width: 1920, height: 1080, output: 'srgb' };
  let st, set, path, params, agents = [], jade, start, end, arrivals = [];

  async function init(renderer, p = {}) {
    params = { shot: 'G4', ...defaults, ...p };
    [start, end] = SHOTS[params.shot];
    meta.duration = end - start; meta.name = 'e_loop_' + params.shot;
    st = new Stage(renderer, params);
    set = createLoopSet(st.eng, { turntable: true, spur: true, exit: true, split: params.shot === 'G4', stoopCrank: params.shot === 'M3' });
    st.scene.add(set.root);
    st.eng.fitShadow(V(7, 4, -3), 24);
    path = loopPath();
    if (params.shot === 'G4') planAssembly();
    const nAg = params.shot === 'M1' ? 4 : params.shot === 'M3' ? 7 : 0;
    for (let i = 0; i < nAg; i++) { const f = makeFigure(st.eng, 'agent'); st.scene.add(f.root); agents.push(f); }
    if (params.shot !== 'G4') {
      const clips = params.sprites === false ? {} : await loadJadeSprites();
      jade = new SpriteActor(st.eng, clips);
      st.scene.add(jade.root);
      meta.jadeSprite = !jade.fallback;
    }
    return meta;
  }

  // ---------------------------------------------------------------- G4 assembly plan
  function planAssembly() {
    const q = (bar, beat) => bb(bar, beat);
    const six = (k) => q(85, 3) + k * (q(85, 4) - q(85, 3)) / 4;      // 16ths from 148.98
    const T = {
      ground: -9, city: -9, tower: -9, props: q(86, 2),
      bldB: q(85, 2), bldC: q(85, 3), turret: six(2),
      trackA: q(85, 4), turntable: q(86, 1), spur: q(86, 1) + 0.11, exit: q(86, 2) + 0.11,
      trackD: q(86, 4), misc: q(86, 3),
    };
    arrivals = set.pieces.map((pc) => {
      let t0 = T[pc.tag] ?? T.misc, from = 'drop';
      if (pc.tag === 'stairsB' || pc.tag === 'stairsC') {
        // one step per 16th, B from the bottom up, C a 16th behind it: the music box climbing
        t0 = q(85, 4) + (pc.seq + (pc.tag === 'stairsC' ? 1 : 0)) * (q(86, 1) - q(85, 4)) / 4 * 0.62;
      }
      if (pc.tag === 'bldB' || pc.tag === 'bldC' || pc.tag === 'turret' || pc.tag === 'exit') from = 'rise';
      if (pc.tag === 'trackA' || pc.tag === 'spur') t0 += hash(pc.obj.id) * 0.06;
      return { obj: pc.obj, t0, from, dur: from === 'rise' ? 0.36 : 0.24, base: pc.obj.position.clone() };
    });
  }
  function applyAssembly(s) {
    for (const a of arrivals) {
      const u = (s - a.t0) / a.dur;
      a.obj.visible = u > 0;
      if (u <= 0) continue;
      const e = clunk(u);
      const off = a.from === 'rise' ? -7 * (1 - e) : 4.5 * (1 - e);
      a.obj.position.set(a.base.x, a.base.y + off, a.base.z);
    }
  }

  // ---------------------------------------------------------------- cameras
  function camG4(s) {
    // kick (148.08): projection snaps to orthographic, the city clunks 90 degrees into the magic angle
    const k = clunk((s - 148.08) / (bb(85, 2) + 0.12 - 148.08));
    const persp = 1 - smooth(148.08, 148.08 + 0.3, s);
    const az = ISO_AZ + 90 * DEG * (1 - k);
    const el = lerp(14 * DEG, ISO_EL, smoother(148.08, 148.66, s));
    const viewH = 25.5 - 0.7 * smoother(149.0, 151.62, s);
    return { tgt: V(6.6, 5.0, -3.2), viewH, az, el, persp };
  }
  function jadeM1(s) {
    const x = 2.1 + 1.15 * (s - 151.62);
    return { pos: V(x, Y0, 0), dir: V(1, 0, 0), dist: x };
  }
  function camM1(s) {
    const u = smoother(151.62, 153.98, s) ;
    const j = jadeM1(s).pos;
    const tgt = V(6.6, 5.0, -3.2).lerp(V(j.x + 0.6, j.y + 0.9, j.z - 0.4), u);
    return { tgt, viewH: lerp(24.8, 6.2, Math.pow(u, 0.8)), az: ISO_AZ, el: ISO_EL, persp: 0 };
  }
  // M3 beats
  const M3 = { rot0: bb(95, 2), rot1: bb(95, 4), crank0: bb(95, 1) + 0.08 };
  function camM3(s) {
    const u = smoother(bb(95, 4), 169.40, s);
    const tgt = V(8.7, 2.6, -1.9).lerp(V(7.6, 4.6, -3.0), u);
    return { tgt, viewH: lerp(5.9, 17.5, u * u * (3 - 2 * u)), az: ISO_AZ, el: ISO_EL, persp: 0 };
  }

  // ---------------------------------------------------------------- actors
  const thetaM3 = (s) => -Math.PI / 2 - Math.PI / 2 * clunk((s - M3.rot0) / (M3.rot1 - M3.rot0));
  function updateM3(s) {
    const th = thetaM3(s);
    set.tt.bridge.rotation.y = th; set.tt.crank.rotation.z = th * 4;
    if (set.tt.stoopCrank) set.tt.stoopCrank.rotation.y = -(th + Math.PI / 2) * 3;
    const L = path.length;
    // three chasers run up the spur onto the bridge, freeze when it moves, ride it round into leg A, then march on
    const vRun = 2.4, vMarch = 1.35;
    for (let k = 0; k < 3; k++) {
      const f = agents[k];
      const zAt = (tt) => 2.4 + 0.7 * k - vRun * (tt - 165.18);
      let p, dir, dist, gait = 1, push = 0;
      if (s < M3.rot0) {
        const z = zAt(s);
        p = V(PIVOT.x, Y0, z); dir = V(0, 0, -1); dist = 2.4 + 0.7 * k - z;
      } else {
        const lx = zAt(M3.rot0);              // bridge-local position when the crank turned
        const c = Math.cos(th), sn = Math.sin(th);
        if (s < M3.rot1) {
          p = V(PIVOT.x + lx * c, Y0, PIVOT.z - lx * sn); dir = V(-c, 0, sn); dist = 2.4 + 0.7 * k - lx; gait = 0;
        } else {
          const sl = PIVOT.x - lx + vMarch * (s - M3.rot1);
          const a = path.at(sl); p = a.p; dir = a.dir; dist = sl; push = loopPush(path, sl);
          gait = smooth(M3.rot1, M3.rot1 + 0.2, s);
        }
      }
      f.root.position.copy(p); f.root.rotation.y = Math.atan2(dir.x, dir.z);
      f.pose(dist / 0.66 * Math.PI * 2, gait, 1); f.pushConst.value = push;
    }
    // the rest of the agency: already marching the circuit, forever (they queue at the gap while the bridge is away)
    for (let k = 3; k < agents.length; k++) {
      const f = agents[k];
      const s0 = [17.0, 22.5, 28.0, 34.0][k - 3];
      const sl = s0 + 1.0 * (s - 165.18);
      const a = path.at(sl);
      f.root.position.copy(a.p); f.root.rotation.y = Math.atan2(a.dir.x, a.dir.z);
      f.pose(sl / 0.66 * Math.PI * 2, 1, 1); f.pushConst.value = loopPush(path, sl);
    }
    // Jade on the stoop, at the crank post
    const jp = V(P2_START.x - 0.1, P2_START.y, P2_START.z - 1.15);
    const cranking = s > M3.crank0 && s < M3.rot1 + 0.15;
    jade.update({ pos: jp, dir: V(1, 0, 0), mode: cranking ? 'crank' : 'idle', t: s - 165.18, camAz: ISO_AZ });
  }
  function updateM1(s) {
    set.tt.bridge.rotation.y = 0;
    const L = path.length;
    // agents enter from the edges: two come down leg D toward her (perceived: behind her on the track), two climb B
    const s0 = [L - 5.2, L - 3.6, 15.4, 16.6];
    for (let k = 0; k < agents.length; k++) {
      const sl = s0[k] + 1.45 * (s - 151.62);
      const a = path.at(sl), f = agents[k];
      f.root.position.copy(a.p); f.root.rotation.y = Math.atan2(a.dir.x, a.dir.z);
      f.pose(sl / 0.66 * Math.PI * 2, 1, 1); f.pushConst.value = loopPush(path, sl);
    }
    const j = jadeM1(s);
    jade.update({ pos: j.pos, dir: j.dir, mode: 'walk', dist: j.dist, t: s - 151.62, camAz: ISO_AZ });
  }

  function songTime(lt, env) { return env && Number.isFinite(env.t) ? env.t : start + lt; }

  function update(s) {
    let c;
    if (params.shot === 'G4') { set.tt.bridge.rotation.y = 0; applyAssembly(s); c = camG4(s); }
    else if (params.shot === 'M1') { updateM1(s); c = camM1(s); }
    else { updateM3(s); c = camM3(s); }
    st.setCamera(c.tgt, c.viewH, c.az, c.el, 0, c.persp);
    return c;
  }

  function draw(lt, env) {
    const s = songTime(lt, env);
    update(s);
    const frame = { seed: boilSeed(s, 1000), target: st.target, sun: params.sun === false ? null : { x: 250, y: 165, r: 64 } };
    if (params.shot === 'M3' || params.shot === 'M1') {
      // Jade's residue: a small patch of coloured pencil round her that grows as she redraws the world
      const jp = params.shot === 'M3' ? V(P2_START.x - 0.1, P2_START.y + 0.6, P2_START.z - 1.15) : jadeM1(s).pos.clone().add(V(0, 0.6, 0));
      const pj = st.project(jp);
      const ppu = st.pixelsPerUnit();
      const r = params.shot === 'M3' ? ppu * (0.9 + 1.6 * smooth(M3.rot0, M3.rot1 + 0.4, s) + 2.5 * smooth(168.6, 169.4, s)) : ppu * 0.9;
      frame.blooms = [{ x: pj.x, y: pj.y, r }];
      if (params.shot === 'M3') {
        const pv = st.project(V(PIVOT.x, Y0, PIVOT.z));
        frame.blooms.push({ x: pv.x, y: pv.y, r: ppu * 1.4 * smooth(M3.rot1 - 0.1, M3.rot1 + 0.5, s) });
      }
    }
    st.render(frame);
  }

  function anchors(lt, env) {
    const s = songTime(lt, env);
    update(s);
    const out = { pixelsPerUnit: st.pixelsPerUnit(), magic: st.magic, pivot: st.project(V(PIVOT.x, Y0, PIVOT.z)) };
    if (params.shot === 'M1') out.jade = st.project(jadeM1(s).pos);
    if (params.shot === 'M3') out.jade = st.project(V(P2_START.x - 0.1, P2_START.y, P2_START.z - 1.15));
    return out;
  }

  function dispose() { st.dispose(); }
  return { meta, init, draw, anchors, dispose, get stage() { return st; } };
}

const inst = createScene();
export const meta = inst.meta;
export const init = inst.init, draw = inst.draw, anchors = inst.anchors, dispose = inst.dispose;
export default inst;
