// The Loop diorama: a stylised Chicago Loop block with elevated L girders, a Penrose staircase circuit
// (Escher's Ascending and Descending) and a Monument Valley turntable.
//
// The magic camera is true isometric: looking down -(1,1,1). Any two points that differ by k*(1,1,1)
// land on the same pixel. The circuit climbs K = 6 units per lap and its last leg (D) ends at
// E = S + (6,6,6): directly in front of its own start S on the view ray. See README.md.
import * as THREE from 'three';
import { Builder, V } from './build.js';
import { MAT } from './engrave.js';

export const ISO_DIR = new THREE.Vector3(1, 1, 1).normalize();
export const K = 6;                         // rise per lap (and the seam offset along (1,1,1))
export const Y0 = 3;                        // L-track deck height at the seam start S
export const RUN = 0.5, RISE = 0.25, NSTEP = 12, HW = 0.65; // stair run/rise, steps per flight, half width
export const AX = 13.3;                     // x of the A/B corner
export const ZBC = -7.3;                    // z of the B/C corner
export const XD = AX + ZBC;                 // = 6, x of leg D (= K, which closes the loop)
export const PIVOT = new THREE.Vector3(9.6, Y0, 0); // turntable pivot on leg A
export const BR_HALF = 1.2;                 // half length of the turntable bridge
export const J_DROP = 2;                    // P2 (exit walkway) is J_DROP*(1,1,1) behind the bridge's far end
export const P2_START = new THREE.Vector3(PIVOT.x - J_DROP, Y0 - J_DROP, -BR_HALF - J_DROP);
export const DOOR_Z = -6.65;
// depth ramp for leg D: 0 at z=D_PUSH0, full K*sqrt(3) at the seam end
export const D_PUSH0 = 0.85, D_END = K - HW;

// ---------------------------------------------------------------- paths
// A path is a list of segments {a, b (Vector3 centreline ends), stairs (n steps) | 0}. s = plan arc length.
export class Path {
  constructor(segs, closed = false) {
    this.segs = segs; this.closed = closed;
    let s = 0;
    for (const g of segs) {
      g.s0 = s; g.len = Math.hypot(g.b.x - g.a.x, g.b.z - g.a.z); s += g.len; g.s1 = s;
      g.dir = new THREE.Vector3(g.b.x - g.a.x, 0, g.b.z - g.a.z).normalize();
    }
    this.length = s;
  }
  seg(s) {
    if (this.closed) s = ((s % this.length) + this.length) % this.length;
    else s = Math.max(0, Math.min(this.length - 1e-6, s));
    let i = 0; while (i < this.segs.length - 1 && s >= this.segs[i].s1) i++;
    return { g: this.segs[i], i, u: s - this.segs[i].s0, s };
  }
  // position of the feet at arc length s, plus heading
  at(s) {
    const { g, i, u } = this.seg(s);
    const f = g.len > 0 ? u / g.len : 0;
    const p = g.a.clone().lerp(g.b, f);
    if (g.stairs) {
      const n = g.stairs, run = g.len / n, rise = (g.b.y - g.a.y) / n;
      const k = Math.min(n - 1, Math.floor(u / run)), fr = u / run - k;
      const e = Math.min(1, fr / 0.45); const sm = e * e * (3 - 2 * e);
      p.y = g.a.y + rise * (k + sm);
    }
    // heading: blend into the next segment's direction near corners
    let dir = g.dir.clone();
    const nxt = this.segs[i + 1] || (this.closed ? this.segs[0] : null);
    const prv = this.segs[i - 1] || (this.closed ? this.segs[this.segs.length - 1] : null);
    const R = 0.35;
    if (nxt && g.len - u < R && nxt.dir.dot(g.dir) < 0.99) dir.lerp(nxt.dir, 0.5 * (1 - (g.len - u) / R)).normalize();
    else if (prv && u < R && prv.dir.dot(g.dir) < 0.99) dir.lerp(prv.dir, 0.5 * (1 - u / R)).normalize();
    return { p, dir, seg: g, segIndex: i };
  }
}

export function loopPath() {
  const S = V(0, Y0, 0);
  const pts = [
    [S, V(AX, Y0, 0), 0],
    [V(AX, Y0, 0), V(AX, Y0, -HW), 0],
    [V(AX, Y0, -HW), V(AX, Y0 + 3, -HW - NSTEP * RUN), NSTEP],
    [V(AX, Y0 + 3, -HW - NSTEP * RUN), V(AX, Y0 + 3, ZBC), 0],
    [V(AX, Y0 + 3, ZBC), V(AX - HW, Y0 + 3, ZBC), 0],
    [V(AX - HW, Y0 + 3, ZBC), V(AX - HW - NSTEP * RUN, Y0 + K, ZBC), NSTEP],
    [V(AX - HW - NSTEP * RUN, Y0 + K, ZBC), V(XD, Y0 + K, ZBC), 0],
    [V(XD, Y0 + K, ZBC), V(XD, Y0 + K, K), 0],     // leg D ends at E = S + K*(1,1,1)
  ];
  return new Path(pts.map(([a, b, n]) => ({ a, b, stairs: n })), true);
}

// depth push (world units along the view axis) for something standing on the loop at arc length s
export function loopPush(path, s) {
  const { g, i } = path.seg(s);
  if (i !== path.segs.length - 1) return 0;
  const p = path.at(s).p;
  const f = Math.max(0, Math.min(1, (p.z - D_PUSH0) / (D_END - D_PUSH0)));
  return f * K * Math.sqrt(3);
}

// ---------------------------------------------------------------- builders
export function createLoopSet(eng, { turntable = true, spur = true, exit = true } = {}) {
  const root = new THREE.Group();
  const mats = new Map();
  let meshId = 1;
  const M = (key, opts) => { if (!mats.has(key)) mats.set(key, eng.material(opts)); return mats.get(key); };
  function addMesh(b, matOpts, { parent = root, noShadow = false, key = null } = {}) {
    if (b.empty) return null;
    const m = new THREE.Mesh(b.geometry(), key ? M(key, matOpts) : eng.material({ ...matOpts, id: (meshId++) * 0.1 }));
    if (key) m.material.uniforms.uObjId.value = (meshId++) * 0.1;
    m.userData.noShadow = noShadow;
    parent.add(m);
    return m;
  }
  const dPush = { origin: [XD, Y0 + K, D_PUSH0], axis: [0, 0, 1], max: D_END - D_PUSH0, rate: K * Math.sqrt(3) / (D_END - D_PUSH0) };

  // ---- ground island ----
  {
    const b = new Builder();
    b.box(-7, -3.5, -17, 21, 0, 11, { skip: 'px nx pz nz ny' }); // just the drawn ground plane; edges dissolve
    addMesh(b, { mat: MAT.ground, albedo: 0.97 });
    // sidewalks / kerbs (raised slabs) around building blocks
    const k = new Builder();
    const kerb = (x0, z0, x1, z1) => k.box(x0, 0, z0, x1, 0.07, z1);
    kerb(12.0, -12.2, 21, 1.3);       // east blocks
    kerb(4.7, -17, 12.0, -6.0);       // north block
    kerb(-7, -17, -1.6, -0.8);        // west blocks
    kerb(1.6, -17, 4.7, -7.4);        // between the street and the north block
    kerb(-7, 2.0, 8.4, 11);           // south-west plaza
    kerb(10.8, 2.0, 21, 11);          // south-east plaza
    addMesh(k, { mat: MAT.ground, albedo: 0.9 });
  }

  // ---- L girder track along an axis ----
  function girderTrack({ axis, from, to, at, y, bents = [], colBottom = 0, skipStart = false, skipEnd = false, push = null, noShadow = false, parent = root, stubs = false }) {
    const P = (a, yy, c) => (axis === 'x' ? V(a, yy, at + c) : V(at + c, yy, a));
    const bx = (a0, y0, c0, a1, y1, c1, b, opt = {}) => {
      const p = P(a0, y0, c0), q = P(a1, y1, c1);
      let skip = opt.skip || '';
      return b.box(p.x, p.y, p.z, q.x, q.y, q.z, { ...opt, skip });
    };
    const sk = (s, e) => (s && skipStart ? (axis === 'x' ? 'nx' : 'nz') : '') + (e && skipEnd ? (axis === 'x' ? 'px' : 'pz') : '');
    const steel = new Builder(), ties = new Builder(), rails = new Builder();
    // deck plate
    bx(from, y - 0.14, -0.68, to, y - 0.06, 0.68, steel, { skip: sk(1, 1) });
    // ties
    for (let a = from + 0.1; a < to - 0.05; a += 0.3) bx(a, y - 0.06, -0.74, Math.min(a + 0.16, to), y, 0.74, ties);
    // rails
    for (const c of [-0.36, 0.36]) bx(from, y, c - 0.035, to, y + 0.075, c + 0.035, rails, { skip: sk(1, 1) });
    // plate girders with flanges and stiffeners
    for (const s of [-1, 1]) {
      const c = 0.64 * s;
      bx(from, y - 0.9, c - 0.03, to, y - 0.14, c + 0.03, steel, { skip: sk(1, 1) });
      bx(from, y - 0.2, c - 0.11, to, y - 0.14, c + 0.11, steel, { skip: sk(1, 1) });
      bx(from, y - 0.9, c - 0.11, to, y - 0.84, c + 0.11, steel, { skip: sk(1, 1) });
      for (let a = from + 0.6; a < to - 0.2; a += 1.2) bx(a, y - 0.84, c + 0.03 * s, a + 0.07, y - 0.2, c + 0.06 * s, steel);
    }
    // bents: two columns, a cap beam and X bracing
    for (const a of bents) {
      bx(a - 0.14, y - 1.05, -0.82, a + 0.14, y - 0.9, 0.82, steel);
      for (const s of [-1, 1]) {
        const c = 0.55 * s;
        bx(a - 0.11, colBottom, c - 0.11, a + 0.11, y - 1.05, c + 0.11, steel, { skip: stubs ? 'ny' : '' });
        bx(a - 0.16, colBottom, c - 0.16, a + 0.16, colBottom + 0.25, c + 0.16, steel); // base plate / plinth
      }
      const yTop = y - 1.25, yBot = Math.max(colBottom + 0.5, yTop - 2.2);
      if (yTop - yBot > 0.6) {
        steel.beam(P(a, yTop, -0.5), P(a, yBot, 0.5), 0.035);
        steel.beam(P(a, yTop, 0.5), P(a, yBot, -0.5), 0.035);
        bx(a - 0.05, yBot - 0.05, -0.5, a + 0.05, yBot + 0.05, 0.5, steel);
      }
    }
    const o = { parent, noShadow };
    addMesh(steel, { mat: MAT.steel, albedo: 0.82, push }, o);
    addMesh(ties, { mat: MAT.ties, albedo: 0.95, push }, o);
    addMesh(rails, { mat: MAT.rail, albedo: 0.35, push }, o);
  }

  // ---- stone stair flight. start = centreline at the foot of the first riser; dir = unit plan vector ----
  function stairs({ start, dir, n = NSTEP, run = RUN, rise = RISE, hw = HW, baseY, push = null }) {
    const b = new Builder();
    const perp = V(-dir.z, 0, dir.x);
    const P = (a, y, c) => V(start.x + dir.x * a + perp.x * c, y, start.z + dir.z * a + perp.z * c);
    for (let i = 0; i < n; i++) {
      const id = b.newId();
      const a0 = i * run, a1 = (i + 1) * run, yb = start.y + i * rise, yt = yb + rise;
      b.quad(P(a0, yt, -hw), P(a1, yt, -hw), P(a1, yt, hw), P(a0, yt, hw), id, V(0, 1, 0));               // tread
      b.quad(P(a0, yb, -hw), P(a0, yt, -hw), P(a0, yt, hw), P(a0, yb, hw), id, dir.clone().negate());       // riser
      b.quad(P(a0, baseY, hw), P(a1, baseY, hw), P(a1, yt, hw), P(a0, yt, hw), id, perp);                   // side +
      b.quad(P(a0, baseY, -hw), P(a1, baseY, -hw), P(a1, yt, -hw), P(a0, yt, -hw), id, perp.clone().negate());
      // nosing: thin overhang lip per tread (adds the engraved step edge)
      b.box(...[P(a0 - 0.04, yt - 0.05, -hw - 0.03), P(a0 + 0.08, yt, hw + 0.03)].flatMap((p, k) => (k === 0 ? [p.x, p.y, p.z] : [p.x, p.y, p.z])), { id });
    }
    addMesh(b, { mat: MAT.stone, albedo: 0.93, push });
  }

  // ---- building with Chicago windows, cornice and parapet ----
  function building({ x0, z0, x1, z1, h, y0 = 0, mat = MAT.brick, albedo = 0.84, cell = [0.8, 1.15], glass = [0.62, 0.55], chicago = true, cornice = true, parapet = 'all', base = true }) {
    const b = new Builder();
    b.box(x0, y0, z0, x1, y0 + h, z1);
    addMesh(b, { mat, albedo, windows: { cell, glass, box: [x0, z0, x1 - x0, z1 - z0], y: [y0 + (base ? 0.5 : 0.25), y0 + h - 0.5], chicago } });
    const s = new Builder();
    if (base) s.box(x0 - 0.05, y0, z0 - 0.05, x1 + 0.05, y0 + 0.4, z1 + 0.05);
    if (cornice) {
      s.box(x0 - 0.14, y0 + h - 0.3, z0 - 0.14, x1 + 0.14, y0 + h - 0.12, z1 + 0.14);
      s.box(x0 - 0.06, y0 + h - 0.42, z0 - 0.06, x1 + 0.06, y0 + h - 0.3, z1 + 0.06);
    }
    const pt = 0.14, ph = 0.32, Y = y0 + h;
    const edges = parapet === 'all' ? 'nx px nz pz' : parapet || '';
    if (edges.includes('nx')) s.box(x0, Y, z0, x0 + pt, Y + ph, z1);
    if (edges.includes('px')) s.box(x1 - pt, Y, z0, x1, Y + ph, z1);
    if (edges.includes('nz')) s.box(x0, Y, z0, x1, Y + ph, z0 + pt);
    if (edges.includes('pz')) s.box(x0, Y, z1 - pt, x1, Y + ph, z1);
    addMesh(s, { mat: MAT.stone, albedo: 0.9 });
  }

  function waterTower(x, y, z) {
    const g = new THREE.Group(); g.position.set(x, y, z); root.add(g);
    const legs = new Builder();
    for (const [a, c] of [[-0.4, -0.4], [0.4, -0.4], [0.4, 0.4], [-0.4, 0.4]]) legs.box(a - 0.05, 0, c - 0.05, a + 0.05, 1.0, c + 0.05);
    legs.beam(V(-0.4, 0.15, 0.42), V(0.4, 0.9, 0.42), 0.025); legs.beam(V(0.4, 0.15, 0.42), V(-0.4, 0.9, 0.42), 0.025);
    legs.beam(V(0.42, 0.15, -0.4), V(0.42, 0.9, 0.4), 0.025); legs.beam(V(0.42, 0.15, 0.4), V(0.42, 0.9, -0.4), 0.025);
    addMesh(legs, { mat: MAT.steel, albedo: 0.55 }, { parent: g });
    const tank = new THREE.Mesh(new THREE.CylinderGeometry(0.62, 0.62, 1.2, 20, 1), eng.material({ mat: MAT.ties, albedo: 0.62, id: (meshId++) * 0.1 }));
    tank.position.y = 1.6; g.add(tank);
    const roof = new THREE.Mesh(new THREE.ConeGeometry(0.68, 0.55, 20, 1), eng.material({ mat: MAT.roof, albedo: 0.8, id: (meshId++) * 0.1 }));
    roof.position.y = 2.47; g.add(roof);
  }

  function lamp(x, z, y = 0.07) {
    const b = new Builder();
    b.box(x - 0.05, y, z - 0.05, x + 0.05, y + 1.6, z + 0.05);
    b.box(x - 0.1, y, z - 0.1, x + 0.1, y + 0.2, z + 0.1);
    b.box(x - 0.13, y + 1.6, z - 0.13, x + 0.13, y + 1.85, z + 0.13);
    b.box(x - 0.16, y + 1.85, z - 0.16, x + 0.16, y + 1.9, z + 0.16);
    addMesh(b, { mat: MAT.rail, albedo: 0.35 });
  }

  // ================================================================ the circuit
  // Leg A: L track at Y0 along +x from the seam corner S to building B (turntable gap at the pivot)
  const gap0 = PIVOT.x - BR_HALF, gap1 = PIVOT.x + BR_HALF;
  girderTrack({ axis: 'x', from: -HW, to: gap0, at: 0, y: Y0, bents: [0, 3.2, 6.4] });
  girderTrack({ axis: 'x', from: gap1, to: AX - HW, at: 0, y: Y0, bents: [11.9] });

  // Building B (east): roof at Y0 carries flight B
  building({ x0: AX - HW, z0: -6.65, x1: 16.9, z1: HW, h: Y0, parapet: 'px pz', cell: [0.85, 1.2] });
  stairs({ start: V(AX, Y0, -HW), dir: V(0, 0, -1), baseY: Y0 });
  // Building C (north): roof at Y0+3 carries flight C
  building({ x0: XD - HW, z0: -11.6, x1: 16.9, z1: ZBC + HW, h: Y0 + 3, parapet: 'px nz', cell: [0.85, 1.2] });
  stairs({ start: V(AX - HW, Y0 + 3, ZBC), dir: V(-1, 0, 0), baseY: Y0 + 3 });
  // turret at the C/D corner: carries the top landing at Y0+K
  {
    const b = new Builder();
    b.box(XD - HW, Y0 + 3, ZBC - HW, XD + HW, Y0 + K, ZBC + HW);
    b.box(XD - HW - 0.08, Y0 + K - 0.18, ZBC - HW - 0.08, XD + HW + 0.08, Y0 + K - 0.05, ZBC + HW + 0.08);
    addMesh(b, { mat: MAT.stone, albedo: 0.9, windows: { cell: [0.6, 0.9], glass: [0.34, 0.5], box: [XD - HW, ZBC - HW, 2 * HW, 2 * HW], y: [Y0 + 3.6, Y0 + K - 0.4], chicago: false, belts: false } });
  }
  // Leg D: the impossible leg. Track at Y0+K along +z ending (open, no end faces) at E = S + K(1,1,1).
  // Stub columns stop at y = K, which at the magic angle is exactly the street under the seam corner.
  girderTrack({ axis: 'z', from: ZBC + HW, to: D_END, at: XD, y: Y0 + K, bents: [-3.6, -0.4, 2.8], colBottom: K - 0.0, skipEnd: true, push: dPush, stubs: true });

  // ---- surrounding city ----
  building({ x0: -6.6, z0: -16.5, x1: -2.0, z1: -10.5, h: 9.2, cell: [0.8, 1.15] });
  building({ x0: -6.6, z0: -10.0, x1: -2.0, z1: -5.0, h: 6.0, mat: MAT.stone, albedo: 0.88, cell: [0.8, 1.0], chicago: false });
  building({ x0: 2.0, z0: -16.5, x1: 4.6, z1: -7.8, h: 7.6, mat: MAT.stone, albedo: 0.86, cell: [0.75, 1.1], chicago: false });
  building({ x0: 12.6, z0: -16.5, x1: 16.9, z1: -12.2, h: 10.5, cell: [0.85, 1.2] });
  building({ x0: 17.3, z0: -12.0, x1: 20.6, z1: -4.0, h: 8.2, mat: MAT.stone, albedo: 0.88, cell: [0.8, 1.05], chicago: false });
  building({ x0: 17.3, z0: -3.6, x1: 20.6, z1: 1.0, h: 5.0, cell: [0.8, 1.15] });
  // the tower (a nod to the Board of Trade): stepped shaft and pyramid roof
  {
    const tx0 = 5.0, tx1 = 12.0, tz0 = -16.5, tz1 = -12.3;
    building({ x0: tx0, z0: tz0, x1: tx1, z1: tz1, h: 11.5, mat: MAT.tower, albedo: 0.9, cell: [0.7, 1.15], glass: [0.5, 0.66], chicago: false, parapet: '' });
    building({ x0: tx0 + 1.2, z0: tz0 + 0.6, x1: tx1 - 1.2, z1: tz1 - 0.6, y0: 11.5, h: 4.0, mat: MAT.tower, albedo: 0.9, cell: [0.6, 1.0], glass: [0.4, 0.7], chicago: false, parapet: '', base: false });
    building({ x0: tx0 + 2.2, z0: tz0 + 1.1, x1: tx1 - 2.2, z1: tz1 - 1.1, y0: 15.5, h: 2.4, mat: MAT.tower, albedo: 0.9, cell: [0.5, 0.8], glass: [0.4, 0.7], chicago: false, parapet: '', base: false, cornice: true });
    const roof = new THREE.Mesh(new THREE.ConeGeometry(1.6, 2.2, 4, 1), eng.material({ mat: MAT.roof, albedo: 0.75, id: (meshId++) * 0.1 }));
    roof.geometry = roof.geometry.toNonIndexed(); roof.geometry.computeVertexNormals();
    roof.rotation.y = Math.PI / 4; roof.position.set((tx0 + tx1) / 2, 17.9 + 1.1, (tz0 + tz1) / 2); root.add(roof);
    const st = new Builder(); const cx = (tx0 + tx1) / 2, cz = (tz0 + tz1) / 2;
    st.box(cx - 0.1, 20.1, cz - 0.1, cx + 0.1, 20.8, cz + 0.1); st.box(cx - 0.2, 20.5, cz - 0.05, cx + 0.2, 20.6, cz + 0.05);
    addMesh(st, { mat: MAT.brass, albedo: 0.7 });
  }
  waterTower(15.2, Y0 + 3 + 0.0, -9.6);
  waterTower(-4.0, 9.2, -13.6);
  for (const [x, z] of [[-2.8, 3.2], [2.0, 3.2], [7.6, 3.2], [12.2, 3.2], [16.0, 3.2], [-2.5, -0.2]]) lamp(x, z);

  // ================================================================ turntable (Monument Valley crank piece)
  const tt = { group: null, bridge: null, crank: null };
  if (turntable) {
    const fixed = new Builder();
    const pier = new THREE.Mesh(new THREE.CylinderGeometry(0.62, 0.75, Y0 - 1.05 + 0.0, 24, 1), eng.material({ mat: MAT.stone, albedo: 0.88, id: (meshId++) * 0.1 }));
    pier.position.set(PIVOT.x, (Y0 - 1.05) / 2, PIVOT.z); root.add(pier);
    const drum = new THREE.Mesh(new THREE.CylinderGeometry(1.22, 1.22, 0.16, 40, 1), eng.material({ mat: MAT.brass, albedo: 0.78, id: (meshId++) * 0.1 }));
    drum.position.set(PIVOT.x, Y0 - 1.0, PIVOT.z); root.add(drum);
    // gear teeth on the drum rim
    for (let i = 0; i < 28; i++) {
      const a = (i / 28) * Math.PI * 2;
      const c = V(PIVOT.x + Math.cos(a) * 1.25, Y0 - 1.0, PIVOT.z + Math.sin(a) * 1.25);
      fixed.obox(c, V(Math.cos(a) * 0.06, 0, Math.sin(a) * 0.06), V(0, 0.07, 0), V(-Math.sin(a) * 0.06, 0, Math.cos(a) * 0.06));
    }
    // crank housing on the front of the pier
    fixed.box(PIVOT.x - 0.28, 0.9, PIVOT.z + 0.62, PIVOT.x + 0.28, 1.55, PIVOT.z + 0.9);
    addMesh(fixed, { mat: MAT.brass, albedo: 0.72 });
    const crank = new THREE.Group(); crank.position.set(PIVOT.x, 1.22, PIVOT.z + 0.9); root.add(crank);
    const cb = new Builder();
    cb.box(-0.05, -0.05, 0, 0.05, 0.05, 0.12);              // axle
    cb.box(-0.06, -0.06, 0.12, 0.06, 0.62, 0.2);            // arm
    cb.box(-0.08, 0.5, 0.2, 0.08, 0.66, 0.42);              // knob
    addMesh(cb, { mat: MAT.brass, albedo: 0.66 }, { parent: crank });
    const cw = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.06, 18, 1), eng.material({ mat: MAT.brass, albedo: 0.8, id: (meshId++) * 0.1 }));
    cw.rotation.x = Math.PI / 2; cw.position.z = 0.1; crank.add(cw);
    // rotating bridge (local x along the bridge)
    const g = new THREE.Group(); g.position.copy(PIVOT); g.position.y = 0; root.add(g);
    const bridge = new THREE.Group(); g.add(bridge);
    girderTrackLocal(bridge);
    tt.group = g; tt.bridge = bridge; tt.crank = crank;
  }
  function girderTrackLocal(parent) {
    // same construction as girderTrack, in the turntable's local frame (centred on the pivot)
    const save = { root };
    girderTrack({ axis: 'x', from: -BR_HALF, to: BR_HALF, at: 0, y: Y0, bents: [], parent });
    const b = new Builder(); // centre capstan disk on the deck
    addMesh(b, { mat: MAT.brass, albedo: 0.8 }, { parent });
    const cap = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.3, 0.05, 24, 1), eng.material({ mat: MAT.brass, albedo: 0.85, id: (meshId++) * 0.1 }));
    cap.position.set(0, Y0 + 0.01, 0); parent.add(cap);
    return save;
  }

  // ================================================================ Jade's spur and the exit
  if (spur) {
    girderTrack({ axis: 'z', from: BR_HALF + 0.05, to: 10.6, at: PIVOT.x, y: Y0, bents: [4.0, 7.2, 10.2], skipStart: false });
  }
  if (exit) {
    // P2: a stone stoop at street level + J_DROP... starting exactly J_DROP*(1,1,1) behind the bridge's far end
    const b = new Builder();
    b.box(P2_START.x - HW, 0, DOOR_Z, P2_START.x + HW, P2_START.y, P2_START.z);
    for (let i = 0; i < 4; i++) b.box(P2_START.x + HW, 0, P2_START.z - 0.5 - i * 0.6, P2_START.x + HW + 0.25 + 0.0, P2_START.y * (0.25 + i * 0.25) - 0.0, P2_START.z - 0.5 - i * 0.6 - 0.45, {}); // side buttresses
    addMesh(b, { mat: MAT.stone, albedo: 0.9 });
    // vestibule (open front) into building C
    const v = new Builder(), d = new Builder();
    const x0 = P2_START.x - 0.48, x1 = P2_START.x + 0.48, y0 = P2_START.y, y1 = y0 + 1.5, z0 = DOOR_Z, z1 = DOOR_Z + 0.55;
    v.box(x0 - 0.16, y0, z0, x0, y1 + 0.18, z1);           // left jamb wall
    v.box(x1, y0, z0, x1 + 0.16, y1 + 0.18, z1);           // right jamb wall
    v.box(x0 - 0.16, y1, z0, x1 + 0.16, y1 + 0.35, z1);    // lintel
    v.box(x0 - 0.3, y1 + 0.35, z0, x1 + 0.3, y1 + 0.47, z1 + 0.12); // hood
    addMesh(v, { mat: MAT.stone, albedo: 0.92 });
    d.quad(V(x0, y0, z0 + 0.01), V(x1, y0, z0 + 0.01), V(x1, y1, z0 + 0.01), V(x0, y1, z0 + 0.01), 1, V(0, 0, 1));
    addMesh(d, { mat: MAT.door, albedo: 0.04 });
  }

  return { root, tt };
}
