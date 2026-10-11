// Flat-shaded geometry builder: quads with outward normals and a per-quad id attribute (aId) used by the
// engraver to draw ink outlines between parts that share a material. Faces can be skipped, which is how
// the open ends of impossible-geometry pieces are made (see README: "seams").
import * as THREE from 'three';

const V = (x, y, z) => new THREE.Vector3(x, y, z);

export class Builder {
  constructor() { this.pos = []; this.nor = []; this.ids = []; this.nextId = 1; }

  newId() { return this.nextId++; }

  // a,b,c,d: Vector3 corners in order; out: intended outward direction (Vector3) to fix winding
  quad(a, b, c, d, id = 0, out = null) {
    const n = new THREE.Vector3().subVectors(b, a).cross(new THREE.Vector3().subVectors(c, a)).normalize();
    if (out && n.dot(out) < 0) { [b, d] = [d, b]; n.negate(); }
    for (const p of [a, b, c, a, c, d]) { this.pos.push(p.x, p.y, p.z); this.nor.push(n.x, n.y, n.z); this.ids.push(id); }
  }

  tri(a, b, c, id = 0, out = null) {
    const n = new THREE.Vector3().subVectors(b, a).cross(new THREE.Vector3().subVectors(c, a)).normalize();
    if (out && n.dot(out) < 0) { [b, c] = [c, b]; n.negate(); }
    for (const p of [a, b, c]) { this.pos.push(p.x, p.y, p.z); this.nor.push(n.x, n.y, n.z); this.ids.push(id); }
  }

  // oriented box: centre c, half-axis vectors X, Y, Z. skip: set of 'px','nx','py','ny','pz','nz' (local axes)
  obox(c, X, Y, Z, { id = this.newId(), skip = '' } = {}) {
    const P = (sx, sy, sz) => c.clone().addScaledVector(X, sx).addScaledVector(Y, sy).addScaledVector(Z, sz);
    const f = (name, axis, s, A, B) => {
      if (skip.includes(name)) return;
      const ctr = axis.clone().multiplyScalar(s);
      // corners of the face spanned by A and B
      const q = (a, b) => c.clone().add(ctr).addScaledVector(A, a).addScaledVector(B, b);
      this.quad(q(-1, -1), q(1, -1), q(1, 1), q(-1, 1), id, ctr);
    };
    f('px', X, 1, Y, Z); f('nx', X, -1, Y, Z);
    f('py', Y, 1, X, Z); f('ny', Y, -1, X, Z);
    f('pz', Z, 1, X, Y); f('nz', Z, -1, X, Y);
    return id;
  }

  // axis-aligned box from min/max corners
  box(x0, y0, z0, x1, y1, z1, opts = {}) {
    if (x0 > x1) [x0, x1] = [x1, x0];
    if (y0 > y1) [y0, y1] = [y1, y0];
    if (z0 > z1) [z0, z1] = [z1, z0];
    return this.obox(V((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), V((x1 - x0) / 2, 0, 0), V(0, (y1 - y0) / 2, 0), V(0, 0, (z1 - z0) / 2), opts);
  }

  // a beam (square section, half-thickness r) from point a to point b
  beam(a, b, r, opts = {}) {
    const d = new THREE.Vector3().subVectors(b, a);
    const L = d.length() / 2; d.normalize();
    let up = Math.abs(d.y) > 0.9 ? V(1, 0, 0) : V(0, 1, 0);
    const s = new THREE.Vector3().crossVectors(d, up).normalize();
    const u = new THREE.Vector3().crossVectors(s, d).normalize();
    return this.obox(a.clone().add(b).multiplyScalar(0.5), d.multiplyScalar(L), u.multiplyScalar(r), s.multiplyScalar(r), opts);
  }

  get empty() { return this.pos.length === 0; }

  geometry() {
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(this.pos, 3));
    g.setAttribute('normal', new THREE.Float32BufferAttribute(this.nor, 3));
    g.setAttribute('aId', new THREE.Float32BufferAttribute(this.ids, 1));
    g.computeBoundingSphere();
    return g;
  }
}

export { V };
