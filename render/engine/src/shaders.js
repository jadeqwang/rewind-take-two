// shaders.js: GLSL for the compositor (GLSL 3, RawShaderMaterial; values stay in sRGB-encoded space end to end).
// Coordinates: every pass works in "design px" (1920x1080, y down) through uS = output px per design px.

export const VS = /* glsl */`
in vec3 position;
out vec2 vUv;
void main(){ vUv = position.xy * .5 + .5; gl_Position = vec4(position.xy, 0., 1.); }`;

export const LIB = /* glsl */`
float hash12(vec2 p){ vec3 p3 = fract(vec3(p.xyx) * .1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y) * p3.z); }
float vnoise(vec2 p){ vec2 i = floor(p), f = fract(p); vec2 u = f * f * (3. - 2. * f);
  return mix(mix(hash12(i), hash12(i + vec2(1, 0)), u.x), mix(hash12(i + vec2(0, 1)), hash12(i + vec2(1, 1)), u.x), u.y); }
float fbm(vec2 p){ float v = 0., a = .5; for (int i = 0; i < 5; i++){ v += a * vnoise(p); p = p * 2.03 + vec2(17.1, 9.2); a *= .5; } return v; }
float luma(vec3 c){ return dot(c, vec3(.2126, .7152, .0722)); }
mat2 rot2(float a){ float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }
vec3 safe3(vec3 c){ if (any(isnan(c)) || any(isinf(c))) return vec3(0.); return c; }
vec3 lin2srgb(vec3 c){ c = max(c, 0.); return mix(c * 12.92, 1.055 * pow(c, vec3(1. / 2.4)) - .055, step(.0031308, c)); }
float linescreen(vec2 px, float v, float cell, float ang){
  vec2 q = rot2(ang) * px / cell; float f = abs(fract(q.y) - .5);
  float w = clamp(v, 0., 1.) * .5; float aa = .75 / cell;
  return 1. - smoothstep(w - aa, w + aa, f); }
`;

// ---- one layer: sample a source through an inverse affine (design px → layer unit coords), key, matte, grade ----
export const FS_LAYER = /* glsl */`
precision highp float;
in vec2 vUv; out vec4 o;
${LIB}
uniform sampler2D tSrc, tSrc2, tMatte;
uniform float uMix, uHasSrc2;
uniform int uMatte;            // 0 none, 1 luma, 2 alpha, 3 luma inverted, 4 alpha inverted
uniform float uFlip, uMatteFlip;
uniform mat3 uInv;
uniform vec4 uCrop;            // x0, y0, w, h in source uv (y down)
uniform vec2 uRepeat;
uniform vec2 uRes; uniform float uS;
uniform float uOpacity, uLinear, uPremul;
uniform int uKey;              // 0 none, 1 luma, 2 chroma
uniform vec3 uKeyColor; uniform float uKeyLo, uKeyHi, uKeySpill, uKeyInvert;
uniform float uSat, uExposure, uContrast, uGamma, uInvert, uHue; uniform vec3 uTint, uLift; uniform vec4 uColorize;
uniform vec4 uColor;           // solid layers: rgba (uses no texture)
uniform int uMode;             // 0 colour, 1 coverage (mask write: alpha in all channels)
uniform float uSolid;
vec4 samp(sampler2D t, vec2 uv, vec2 gx, vec2 gy, float flip){
  if (flip > .5) { uv.y = 1. - uv.y; gx.y = -gx.y; gy.y = -gy.y; }
  return textureGrad(t, uv, gx, gy);
}
void main(){
  vec2 px = vec2(gl_FragCoord.x, uRes.y - gl_FragCoord.y) / uS;      // design px, y down
  vec3 l = uInv * vec3(px, 1.);
  vec2 u = l.xy;
  vec2 gx = dFdx(u), gy = dFdy(u);
  if (uRepeat.x > .5) u.x = fract(u.x);
  if (uRepeat.y > .5) u.y = fract(u.y);
  if (u.x < 0. || u.x > 1. || u.y < 0. || u.y > 1.) { o = vec4(0.); return; }
  vec4 c;
  if (uSolid > .5) c = uColor;
  else {
    vec2 suv = uCrop.xy + u * uCrop.zw;
    vec2 sgx = gx * uCrop.zw, sgy = gy * uCrop.zw;
    c = samp(tSrc, suv, sgx, sgy, uFlip);
    if (uHasSrc2 > .5) c = mix(c, samp(tSrc2, suv, sgx, sgy, uFlip), uMix);
    if (uPremul > .5 && c.a > 1e-5) c.rgb /= c.a;
    if (uLinear > .5) c.rgb = lin2srgb(c.rgb);
    if (uMatte > 0) {
      vec4 m = samp(tMatte, suv, sgx, sgy, uMatteFlip);
      float a = (uMatte == 1 || uMatte == 3) ? luma(m.rgb) : m.a;
      if (uMatte >= 3) a = 1. - a;
      c.a *= a;
    }
    if (uKey == 1) {
      float k = smoothstep(uKeyLo, uKeyHi, luma(c.rgb));
      if (uKeyInvert > .5) k = 1. - k;
      c.a *= k;
    } else if (uKey == 2) {
      // chroma key in a YCbCr-ish space: distance of chroma from the key colour
      vec2 cc = vec2(dot(c.rgb, vec3(-.169, -.331, .5)), dot(c.rgb, vec3(.5, -.419, -.081)));
      vec2 kc = vec2(dot(uKeyColor, vec3(-.169, -.331, .5)), dot(uKeyColor, vec3(.5, -.419, -.081)));
      float d = distance(cc, kc);
      float k = smoothstep(uKeyLo, uKeyHi, d);
      c.a *= k;
      // spill: pull the key hue out of the edge
      if (uKeySpill > 0.) { float sp = (1. - k) * uKeySpill; vec3 g = vec3(luma(c.rgb)); c.rgb = mix(c.rgb, g, clamp(sp * 2., 0., 1.)); }
    }
    // grade
    c.rgb = c.rgb * uExposure;
    c.rgb = (c.rgb - .5) * uContrast + .5;
    c.rgb = mix(vec3(luma(c.rgb)), c.rgb, uSat);
    if (uHue != 0.) {   // hue rotation in YIQ
      float Y = dot(c.rgb, vec3(.299, .587, .114)), I = dot(c.rgb, vec3(.596, -.274, -.322)), Qq = dot(c.rgb, vec3(.211, -.523, .312));
      float ch = cos(uHue), sh = sin(uHue); float I2 = I * ch - Qq * sh, Q2 = I * sh + Qq * ch;
      c.rgb = vec3(Y + .956 * I2 + .621 * Q2, Y - .272 * I2 - .647 * Q2, Y - 1.106 * I2 + 1.703 * Q2);
    }
    if (uColorize.a > 0.) { float l = luma(c.rgb); c.rgb = mix(c.rgb, uColorize.rgb * (.18 + 1.05 * l) + vec3(.9) * smoothstep(.75, 1., l) * .25, uColorize.a); }
    c.rgb = c.rgb * uTint + uLift * (1. - c.rgb);
    c.rgb = pow(clamp(c.rgb, 0., 1.), vec3(1. / uGamma));
    if (uInvert > .5) c.rgb = 1. - c.rgb;
  }
  c.a = clamp(c.a * uOpacity, 0., 1.);
  c.rgb = safe3(clamp(c.rgb, 0., 1.));
  o = uMode == 1 ? vec4(c.a) : vec4(c.rgb * c.a, c.a);                 // premultiplied
}`;

// ---- post: everything that treats the composite as a picture ----
export const FS_POST = /* glsl */`
precision highp float;
in vec2 vUv; out vec4 o;
${LIB}
uniform sampler2D tComp, tMask;
uniform vec2 uRes; uniform float uS, uTime, uHasMask;
uniform float zoom, spin, drop, squash, warble, warbleSeed, wobble, tracking, trackPos, rewindLines, ripple, ripplePhase;
uniform vec2 shake;
uniform float chroma, vhs, iso, engrave, engraveCell, engraveAngle, sat, contrast, exposure, lift, neg;
uniform vec3 tint, isoInk, isoPaper, bg;
uniform float grain, grainSize, grainSeed, paper, paperSeed, scan, vignette, letterbox; uniform vec3 boxC;
vec2 distort(vec2 uv){
  vec2 a = vec2(uRes.x / uRes.y, 1.);
  vec2 q = (uv - .5) * a;
  q = rot2(spin) * q / zoom;
  if (ripple > 0.) { float r = length(q); q += normalize(q + 1e-5) * sin(r * 26. - ripplePhase) * ripple * .012 * smoothstep(0., .3, r); }
  q.y /= max(.2, 1. - squash);
  uv = q / a + .5;
  uv += vec2(-shake.x, shake.y) / vec2(1920., 1080.);
  uv.y += drop / 1080.;
  float sy = (1. - uv.y) * 1080.;                                        // design y, down
  if (warble > 0.) {
    float band = floor(sy / 6.);
    float n = vnoise(vec2(band * .37, warbleSeed * 3.1)) - .5;
    float slow = sin(sy * .011 + warbleSeed * 1.7) * .5;
    uv.x += (n * .6 + slow * .4) * warble * 7. / 1920.;
  }
  if (wobble > 0.) uv.x += sin(sy * .045 + uTime * 21.) * wobble * 3.5 / 1920. + sin(sy * .006 - uTime * 3.) * wobble * 6. / 1920.;
  if (tracking > 0.) {
    float d = abs(sy - trackPos);
    float m = smoothstep(52., 0., d);
    uv.x += m * tracking * (vnoise(vec2(sy * .35, warbleSeed)) - .3) * 46. / 1920.;
  }
  if (rewindLines > 0.) {
    // VHS search: a few hard horizontal bands that crawl upward and shear the picture sideways
    for (int k = 0; k < 3; k++) {
      float fk = float(k);
      float by = fract(uTime * (.23 + .11 * fk) + fk * .37 + warbleSeed * .01) * 1180. - 50.;
      float m = smoothstep(26. + 10. * fk, 0., abs(sy - by));
      uv.x += m * rewindLines * (30. + 25. * fk) / 1920.;
    }
  }
  return uv;
}
vec3 fetch(vec2 uv){
  if (uv.x < 0. || uv.y < 0. || uv.x > 1. || uv.y > 1.) return bg;
  vec4 c = texture(tComp, uv); return c.rgb + bg * (1. - c.a);
}
void main(){
  vec2 uv = distort(vUv);
  vec2 px = vec2(vUv.x * 1920., (1. - vUv.y) * 1080.);
  float sy = (1. - uv.y) * 1080.;
  // chromatic split: radial + a horizontal misregistration
  vec2 dir = (uv - .5) * 2.;
  vec2 cs = (vec2(chroma) * (dir * .6 + vec2(.8, 0.))) / vec2(1920., 1080.);
  vec3 col = vec3(fetch(uv + cs).r, fetch(uv).g, fetch(uv - cs).b);
  // VHS: chroma bleeds sideways, luma stays sharper, plus tape noise
  if (vhs > 0.) {
    vec3 acc = vec3(0.); float w = 0.;
    for (int i = -3; i <= 3; i++) { float fi = float(i); vec3 s = fetch(uv + vec2(fi * 2.6 * vhs / 1920., 0.)); float wi = 1. - abs(fi) / 4.; acc += s * wi; w += wi; }
    acc /= w;
    float Y = luma(col);
    vec3 bleed = acc - vec3(luma(acc)) + vec3(Y);
    col = mix(col, bleed, clamp(vhs, 0., 1.));
    float n = hash12(floor(px / vec2(3., 1.)) + fract(uTime * 13.7) * 311.) - .5;
    col += n * .07 * vhs;
    float line = step(.996 - .004 * vhs, hash12(vec2(floor(sy), floor(uTime * 24.))));
    col += line * .5 * vhs * vnoise(vec2(px.x * .05, sy));
  }
  if (rewindLines > 0.) {
    for (int k = 0; k < 3; k++) {
      float fk = float(k);
      float by = fract(uTime * (.23 + .11 * fk) + fk * .37 + warbleSeed * .01) * 1180. - 50.;
      float m = smoothstep(20. + 8. * fk, 0., abs(sy - by));
      float sn = hash12(vec2(floor(px.x / 2.), floor(sy / 2.)) + fract(uTime * 7.3) * 97.);
      col = mix(col, vec3(sn * .9 + .1), m * rewindLines * .55 * step(.35, sn));
    }
  }
  if (tracking > 0.) { float d = abs(sy - trackPos); col += smoothstep(20., 0., d) * tracking * .25 * (hash12(px + uTime) - .3); }
  // colour isolation: the world becomes ink on paper (optionally engraved); masked layers keep their colour
  if (iso > 0.) {
    float m = uHasMask > .5 ? texture(tMask, uv).r : 0.;
    float l = clamp(luma(col), 0., 1.);
    vec3 world = mix(isoInk, isoPaper, smoothstep(.02, .95, l));
    if (engrave > 0.) {
      float cov = linescreen(px, 1. - l, engraveCell, engraveAngle);
      float cov2 = linescreen(px, 1. - l * 1.6, engraveCell, engraveAngle + 1.2);   // cross-hatch in the darks
      vec3 eng = mix(isoPaper, isoInk, clamp(max(cov, cov2), 0., 1.));
      world = mix(world, eng, engrave);
    }
    col = mix(col, world, iso * (1. - m));
  }
  // woodblock negative: the world's luminance flips (white lines on ink), masked layers keep their colour
  if (neg > 0.) {
    float m = uHasMask > .5 ? texture(tMask, uv).r : 0.;
    float l = clamp(luma(col), 0., 1.);
    vec3 nw = mix(isoInk, isoPaper, 1. - smoothstep(.04, .96, l));
    col = mix(col, nw, neg * (1. - m));
  }
  // grade
  col *= exposure;
  col = (col - .5) * contrast + .5;
  col = mix(vec3(luma(col)), col, sat);
  col = col * tint + lift * (1. - col);
  // paper fibre (static, it is the stock) and grain (seeded per frame)
  if (paper > 0.) {
    float f = fbm(px * vec2(.012, .03) + paperSeed) - .5;
    float fine = hash12(floor(px * .7) + paperSeed) - .5;
    col *= 1. + paper * (f * .22 + fine * .06);
  }
  if (grain > 0.) {
    float g = hash12(floor(px / grainSize) + fract(grainSeed * .1371) * 1000.) - .5;
    float l = luma(col);
    col += g * grain * (.35 + 1.3 * l * (1. - l));
  }
  if (scan > 0.) { float s = .5 + .5 * sin(px.y * 3.14159 * .5); col *= 1. - scan * .35 * s; }
  vec2 vq = vUv - .5; col *= 1. - vignette * dot(vq, vq) * 1.8;
  float yy = 1. - vUv.y; if (yy < letterbox || yy > 1. - letterbox) col = boxC;   // bars sit under post-stage layers (HUD, lyrics)
  o = vec4(clamp(safe3(col), 0., 1.), 1.);
}`;

// ---- final: flash, fade, dither ----
export const FS_FINAL = /* glsl */`
precision highp float;
in vec2 vUv; out vec4 o;
${LIB}
uniform sampler2D tSrc; uniform vec2 uRes;
uniform float flash, fade, dither, uTime; uniform vec3 flashC;
void main(){
  vec4 c = texture(tSrc, vUv);
  vec3 col = c.rgb;
  col = mix(col, flashC, clamp(flash, 0., 1.));
  col *= 1. - clamp(fade, 0., 1.);
  col += (hash12(vUv * uRes + fract(uTime) * 61.) - .5) * dither / 255.;
  o = vec4(clamp(col, 0., 1.), 1.);
}`;
