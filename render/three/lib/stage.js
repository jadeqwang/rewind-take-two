// Shared stage for the diorama scenes: orthographic "magic angle" camera, engraver, projection helpers.
import * as THREE from 'three';
import { Engraver } from './engrave.js';

export const ISO_EL = Math.atan(1 / Math.SQRT2);  // 35.264 deg: view direction (1,1,1)
export const ISO_AZ = Math.PI / 4;

export class Stage {
  constructor(renderer, params = {}) {
    this.renderer = renderer;
    const size = new THREE.Vector2();
    renderer.getDrawingBufferSize(size);
    this.width = params.width || size.x || 1920;
    this.height = params.height || size.y || 1080;
    this.eng = new Engraver(renderer, { width: this.width, height: this.height, ss: params.ss ?? 2, style: params.style || {} });
    this.scene = new THREE.Scene();
    this.camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 400);
    this.target = new THREE.Vector3();
    this.viewH = 20;
  }

  // az/el in radians; viewH = world units visible vertically at the target; target = look-at point.
  // persp 0 = orthographic (the magic camera), 1 = perspective with vertical fov `fov` (deg) framing the same viewH
  // at the target. In between, the projection matrices are blended: the "snap to orthographic" move.
  setCamera(target, viewH, az = ISO_AZ, el = ISO_EL, roll = 0, persp = 0, fov = 38) {
    this.target.copy(target); this.viewH = viewH;
    const c = this.camera, aspect = this.width / this.height;
    c.left = -viewH * aspect / 2; c.right = viewH * aspect / 2; c.top = viewH / 2; c.bottom = -viewH / 2;
    const d = new THREE.Vector3(Math.cos(el) * Math.sin(az), Math.sin(el), Math.cos(el) * Math.cos(az));
    const dist = persp > 0 ? viewH / 2 / Math.tan(fov * Math.PI / 360) : 150;
    c.position.copy(target).addScaledVector(d, dist);
    c.up.set(Math.sin(roll), Math.cos(roll), 0);
    c.lookAt(target);
    c.near = persp > 0 ? -300 : 1; c.far = 400;
    c.updateProjectionMatrix(); c.updateMatrixWorld();
    if (persp > 0) {
      const P = new THREE.Matrix4().makePerspective(-0.5 * aspect, 0.5 * aspect, 0.5, -0.5, 0.5 / Math.tan(fov * Math.PI / 360), 400);
      const O = c.projectionMatrix.clone();
      const e = c.projectionMatrix.elements, pe = P.elements, oe = O.elements;
      // blend in a smoothed space so the move reads as a snap, not a slow dolly
      for (let i = 0; i < 16; i++) e[i] = oe[i] + (pe[i] - oe[i]) * persp;
      c.projectionMatrixInverse.copy(c.projectionMatrix).invert();
    }
    // the illusion only holds at the magic angle: depth pushes fade out as the camera leaves it
    const dev = Math.hypot(az - ISO_AZ, el - ISO_EL) * 180 / Math.PI + persp * 10;
    const m = 1 - Math.min(1, Math.max(0, (dev - 0.15) / 1.5));
    this.eng.shared.uMagic.value = m * m * (3 - 2 * m);
    this.magic = this.eng.shared.uMagic.value;
  }

  // world point -> output pixel coords {x, y (from top), depth (view distance)}
  project(p) {
    const v = p.clone().project(this.camera);
    const e = this.camera.matrixWorldInverse.elements;
    const depth = -(e[2] * p.x + e[6] * p.y + e[10] * p.z + e[14]);
    return { x: (v.x * 0.5 + 0.5) * this.width, y: (1 - (v.y * 0.5 + 0.5)) * this.height, depth };
  }

  pixelsPerUnit() { return this.height / this.viewH; }

  render(frame) { this.eng.render(this.scene, this.camera, frame); }
  dispose() { this.eng.dispose(); }
}

// seed for line boil: changes on twos (12 drawings/s at 24 fps) and repeats every `period` seconds
export function boilSeed(t, period = 10, rate = 12) {
  const n = Math.floor(((t % period) + period) % period * rate + 1e-6);
  return (n % 997) * 1.618;
}
