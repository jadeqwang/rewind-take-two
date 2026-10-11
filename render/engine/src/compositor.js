// compositor.js: one three.js WebGLRenderer owns the GL context. Layers are drawn as full-screen passes into
// premultiplied render targets (any affine, key, matte, grade, blend), then post → post-stage layers → final → canvas.
// Three.js scene modules render into their own targets on the same renderer (zero-copy).
import * as THREE from 'three';
import { VS, FS_LAYER, FS_POST, FS_FINAL } from './shaders.js';
import { hexRgb } from './core.js';

const BLEND = {   // premultiplied-alpha blend functions: [srcRGB, dstRGB, srcA, dstA]
  normal: [THREE.OneFactor, THREE.OneMinusSrcAlphaFactor, THREE.OneFactor, THREE.OneMinusSrcAlphaFactor],
  add: [THREE.OneFactor, THREE.OneFactor, THREE.OneFactor, THREE.OneFactor],
  screen: [THREE.OneFactor, THREE.OneMinusSrcColorFactor, THREE.OneFactor, THREE.OneMinusSrcAlphaFactor],
  multiply: [THREE.DstColorFactor, THREE.OneMinusSrcAlphaFactor, THREE.OneFactor, THREE.OneMinusSrcAlphaFactor],
  erase: [THREE.ZeroFactor, THREE.OneMinusSrcAlphaFactor, THREE.ZeroFactor, THREE.OneMinusSrcAlphaFactor],
  max: [THREE.OneFactor, THREE.OneFactor, THREE.OneFactor, THREE.OneFactor],
};

export class Compositor {
  constructor(canvas, W, H) {
    this.W = W; this.H = H; this.S = H / 1080;
    THREE.ColorManagement.enabled = true;
    const r = this.renderer = new THREE.WebGLRenderer({ canvas, antialias: false, alpha: false, preserveDrawingBuffer: true });   // no powerPreference: on this dual-GPU box Chrome answers 'high-performance' with a context loss
    r.setPixelRatio(1); r.setSize(W, H, false); r.autoClear = false;
    r.outputColorSpace = THREE.SRGBColorSpace;
    const gl = r.getContext();
    this.info = { renderer: (() => { const e = gl.getExtension('WEBGL_debug_renderer_info'); return e ? gl.getParameter(e.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER); })() };
    this.cam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    this.scene = new THREE.Scene();
    this.quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), null); this.quad.frustumCulled = false; this.scene.add(this.quad);
    const raw = (fs, uniforms, blend) => {
      const m = new THREE.RawShaderMaterial({ vertexShader: VS, fragmentShader: fs, uniforms, glslVersion: THREE.GLSL3, depthTest: false, depthWrite: false, transparent: !!blend });
      if (blend) { const b = BLEND[blend]; m.blending = THREE.CustomBlending; m.blendEquation = m.blendEquationAlpha = blend === 'max' ? THREE.MaxEquation : THREE.AddEquation; [m.blendSrc, m.blendDst, m.blendSrcAlpha, m.blendDstAlpha] = b; m.premultipliedAlpha = true; }
      return m;
    };
    this.white = new THREE.DataTexture(new Uint8Array([255, 255, 255, 255]), 1, 1); this.white.needsUpdate = true;
    const U = this.U = {
      tSrc: { value: this.white }, tSrc2: { value: this.white }, tMatte: { value: this.white }, uMix: { value: 0 }, uHasSrc2: { value: 0 },
      uMatte: { value: 0 }, uFlip: { value: 0 }, uMatteFlip: { value: 0 }, uInv: { value: new THREE.Matrix3() }, uCrop: { value: new THREE.Vector4(0, 0, 1, 1) },
      uRepeat: { value: new THREE.Vector2() }, uRes: { value: new THREE.Vector2(W, H) }, uS: { value: this.S }, uOpacity: { value: 1 }, uLinear: { value: 0 }, uPremul: { value: 0 },
      uKey: { value: 0 }, uKeyColor: { value: new THREE.Vector3(0, 1, 0) }, uKeyLo: { value: 0 }, uKeyHi: { value: 0.1 }, uKeySpill: { value: 0 }, uKeyInvert: { value: 0 },
      uSat: { value: 1 }, uExposure: { value: 1 }, uContrast: { value: 1 }, uGamma: { value: 1 }, uInvert: { value: 0 }, uTint: { value: new THREE.Vector3(1, 1, 1) }, uLift: { value: new THREE.Vector3() },
      uHue: { value: 0 }, uColorize: { value: new THREE.Vector4() }, uRim: { value: 0 },
      uColor: { value: new THREE.Vector4(0, 0, 0, 1) }, uMode: { value: 0 }, uSolid: { value: 0 },
    };
    this.layerMat = {}; for (const b of Object.keys(BLEND)) this.layerMat[b] = raw(FS_LAYER, U, b);
    this.postU = {}; this.postMat = raw(FS_POST, this.postU, null);
    this.finalU = {}; this.finalMat = raw(FS_FINAL, this.finalU, null);
    this.rts = new Map();
    this.texCache = new Map();
  }

  rt(name, opts = {}) {
    const w = opts.w || this.W, h = opts.h || this.H, key = `${name}:${w}x${h}`;
    let t = this.rts.get(key);
    if (!t) {
      t = new THREE.WebGLRenderTarget(w, h, { type: THREE.UnsignedByteType, depthBuffer: !!opts.depth, stencilBuffer: false, samples: opts.samples || 0,
        magFilter: THREE.LinearFilter, minFilter: THREE.LinearFilter, generateMipmaps: false });
      t.texture.colorSpace = THREE.NoColorSpace;
      this.rts.set(key, t);
    }
    return t;
  }
  // always clears to transparent black (colours are painted with solid layers, so no colour-space conversion is involved)
  clear(target) { const r = this.renderer; r.setRenderTarget(target); r.setClearColor(0x000000, 0); r.clear(true, true, false); }
  _draw(mat, target) { this.quad.material = mat; this.renderer.setRenderTarget(target); this.renderer.render(this.scene, this.cam); }

  // texture for a source object (ImageBitmap / canvas), one GPU texture per slot; re-uploaded when the source changes
  tex(slot, src, { mips = true } = {}) {
    let e = this.texCache.get(slot);
    if (!e) {
      const t = src instanceof HTMLCanvasElement ? new THREE.CanvasTexture(src) : new THREE.Texture(src);
      t.flipY = false; t.premultiplyAlpha = false; t.colorSpace = THREE.NoColorSpace;
      t.generateMipmaps = mips; t.minFilter = mips ? THREE.LinearMipmapLinearFilter : THREE.LinearFilter; t.magFilter = THREE.LinearFilter;
      t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping;
      e = { t, src: null }; this.texCache.set(slot, e);
    }
    if (e.src !== src || src instanceof HTMLCanvasElement) { e.t.image = src; e.t.needsUpdate = true; e.src = src; }
    e.used = this.tick;
    return e.t;
  }
  // after each frame: free GPU textures for slots unused in the last 2 frames once there are many (ghost frames, old shots)
  sweep() {
    this.tick = (this.tick || 0) + 1;
    if (this.texCache.size < 96) return;
    for (const [k, e] of this.texCache) if ((e.used ?? 0) < this.tick - 2) { e.t.dispose(); this.texCache.delete(k); }
  }

  // draw one layer op into target. op: {tex|solid, tex2, mix, matte, matteMode, flip, matteFlip, linear, premul, inv (Matrix3 elements, row-major),
  //   crop [x0,y0,w,h], repeat [x,y], opacity, blend, key {...}, grade {...}, mode: 'color'|'coverage'}
  drawLayer(op, target) {
    const U = this.U;
    U.uSolid.value = op.solid ? 1 : 0;
    if (op.solid) { const c = hexRgb(op.solid); U.uColor.value.set(c[0], c[1], c[2], 1); }
    U.tSrc.value = op.tex || this.white; U.tSrc2.value = op.tex2 || this.white; U.uHasSrc2.value = op.tex2 ? 1 : 0; U.uMix.value = op.mix || 0;
    U.tMatte.value = op.matte || this.white; U.uMatte.value = op.matte ? (op.matteMode ?? 1) : 0; U.uMatteFlip.value = op.matteFlip ? 1 : 0;
    U.uFlip.value = op.flip ? 1 : 0; U.uLinear.value = op.linear ? 1 : 0; U.uPremul.value = op.premul ? 1 : 0;
    U.uInv.value.set(...op.inv);
    const cr = op.crop || [0, 0, 1, 1]; U.uCrop.value.set(cr[0], cr[1], cr[2], cr[3]);
    U.uRepeat.value.set(op.repeat?.[0] ? 1 : 0, op.repeat?.[1] ? 1 : 0);
    U.uOpacity.value = op.opacity ?? 1;
    const k = op.key;
    U.uKey.value = !k ? 0 : k.type === 'chroma' ? 2 : 1;
    if (k) {
      if (k.type === 'chroma') { const c = hexRgb(k.color || '#00ff00'); U.uKeyColor.value.set(c[0], c[1], c[2]); U.uKeyLo.value = k.tolerance ?? 0.12; U.uKeyHi.value = (k.tolerance ?? 0.12) + (k.softness ?? 0.08); U.uKeySpill.value = k.spill ?? 0.5; }
      else { U.uKeyLo.value = k.low ?? 0.04; U.uKeyHi.value = k.high ?? 0.2; U.uKeyInvert.value = k.invert ? 1 : 0; }
    }
    const g = op.grade || {};
    U.uSat.value = g.saturation ?? 1; U.uExposure.value = g.exposure ?? 1; U.uContrast.value = g.contrast ?? 1; U.uGamma.value = g.gamma ?? 1; U.uInvert.value = g.invert ? 1 : 0;
    const tn = g.tint ? hexRgb(g.tint) : [1, 1, 1]; U.uTint.value.set(tn[0], tn[1], tn[2]);
    const lf = g.lift ? hexRgb(g.lift) : [0, 0, 0]; U.uLift.value.set(lf[0], lf[1], lf[2]);
    U.uHue.value = (g.hue || 0) * Math.PI / 180; U.uRim.value = g.residueRim || 0;
    if (g.colorize) { const cz = hexRgb(g.colorize); U.uColorize.value.set(cz[0], cz[1], cz[2], g.colorizeAmount ?? 0.65); } else U.uColorize.value.set(0, 0, 0, 0);
    U.uMode.value = op.mode === 'coverage' ? 1 : 0;
    this._draw(this.layerMat[op.blend || 'normal'] || this.layerMat.normal, target);
  }

  post(src, mask, target, P) {
    const u = this.postU, set = (k, v) => { if (!u[k]) u[k] = { value: v }; else u[k].value = v; };
    set('tComp', src.texture); set('tMask', mask ? mask.texture : this.white); set('uHasMask', mask ? 1 : 0);
    set('uRes', new THREE.Vector2(this.W, this.H)); set('uS', this.S); set('uTime', P.time || 0);
    for (const k of ['zoom', 'spin', 'drop', 'squash', 'warble', 'warbleSeed', 'wobble', 'tracking', 'trackPos', 'rewindLines', 'ripple', 'ripplePhase', 'chroma', 'vhs', 'iso', 'engrave',
      'engraveCell', 'engraveAngle', 'sat', 'contrast', 'exposure', 'lift', 'grain', 'grainSize', 'grainSeed', 'paper', 'paperSeed', 'scan', 'vignette', 'letterbox', 'neg']) set(k, +P[k] || 0);
    set('shake', new THREE.Vector2(P.shakeX || 0, P.shakeY || 0));
    for (const k of ['tint', 'isoInk', 'isoPaper', 'bg', 'boxC']) { const c = hexRgb(P[k]); set(k, new THREE.Vector3(c[0], c[1], c[2])); }
    this.postMat.uniformsNeedUpdate = true;
    this._draw(this.postMat, target);
  }

  final(src, P) {
    const u = this.finalU, set = (k, v) => { if (!u[k]) u[k] = { value: v }; else u[k].value = v; };
    set('tSrc', src.texture); set('uRes', new THREE.Vector2(this.W, this.H)); set('uTime', P.time || 0);
    set('flash', +P.flash || 0); set('fade', +P.fade || 0); set('dither', P.dither ?? 1);
    const f = hexRgb(P.flashC || '#ffffff'); set('flashC', new THREE.Vector3(f[0], f[1], f[2]));
    this.finalMat.uniformsNeedUpdate = true;
    this._draw(this.finalMat, null);
  }

  // FNV-1a over the drawn canvas pixels (determinism checks)
  hashPixels() {
    const gl = this.renderer.getContext(), px = new Uint8Array(this.W * this.H * 4);
    gl.bindFramebuffer(gl.FRAMEBUFFER, null); gl.readPixels(0, 0, this.W, this.H, gl.RGBA, gl.UNSIGNED_BYTE, px);
    let h = 2166136261 >>> 0; const v = new Uint32Array(px.buffer);
    for (let i = 0; i < v.length; i++) { h ^= v[i]; h = Math.imul(h, 16777619); }
    return (h >>> 0).toString(16).padStart(8, '0');
  }
}
