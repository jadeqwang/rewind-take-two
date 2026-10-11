// Escher wood-engraving renderer for three.js (WebGL2).
//
//   1. shadow pass   : scene depth from an orthographic sun camera (own depth texture, own PCF)
//   2. G-buffer pass : every mesh uses an Engraver material (RawShaderMaterial, GLSL3, 3 MRT outputs)
//                      o0 = world normal, material id      o1 = world position, view depth
//                      o2 = sun light * shadow, albedo, facade pattern, object id
//   3. composite     : screen-uniform, world-anchored engraving lines whose width swells with darkness
//                      (wood-engraving "white line" look in the shadows), up to 3 cross-hatch layers,
//                      plane-distance + normal + id ink edges with hand wobble, paper tooth, unfinished
//                      fade at the bottom of the diorama, and a colored-pencil layer (Jade + color bloom)
//   4. downsample    : supersampled composite -> whatever render target was bound when render() was called
//
// Everything is a pure function of the uniforms we set: no clock, no randomness.
import * as THREE from 'three';

export const MAT = {
  bg: 0, stone: 1, brick: 2, steel: 3, ties: 4, rail: 5, roof: 6, ground: 7, glass: 8,
  suit: 9, skin: 10, shades: 11, shirt: 12,
  jJacket: 13, jBand: 14, jHair: 15, jPants: 16, jShoe: 17, jTop: 18, jPencil: 19,
  brass: 20, tower: 21, door: 22, darkStone: 23, phones: 24, sprite: 25, car: 26, road: 27, water: 28,
};
export const N_MAT = 32;

// colored-pencil palette per material (sRGB hex). Warm: orange, sky blue, gold; Klimt/Kandinsky accents.
export const PALETTE = {
  [MAT.stone]: '#F2B42A', [MAT.brick]: '#F58A1F', [MAT.steel]: '#3B97EC', [MAT.ties]: '#C77A3A',
  [MAT.rail]: '#2E4790', [MAT.roof]: '#EE9A22', [MAT.ground]: '#F3D08C', [MAT.glass]: '#2754C2',
  [MAT.suit]: '#24262E', [MAT.skin]: '#E9B494', [MAT.shades]: '#101014', [MAT.shirt]: '#F4F1EA',
  [MAT.jJacket]: '#F6F3EC', [MAT.jBand]: '#FF7A1A', [MAT.jHair]: '#17151A', [MAT.jPants]: '#1C2A4A',
  [MAT.jShoe]: '#F8F6F0', [MAT.jTop]: '#121216', [MAT.jPencil]: '#F2C230', [MAT.brass]: '#E0A526',
  [MAT.tower]: '#D9A21E', [MAT.door]: '#A8327E', [MAT.darkStone]: '#D9822F', [MAT.phones]: '#FF7A1A',
  [MAT.car]: '#1A1B22', [MAT.road]: '#C9C2B4', [MAT.water]: '#4FA3E0',
};

export const DEFAULT_STYLE = {
  paper: '#ECE7DC', ink: '#141210',
  hatchPx: 5.2,        // engraving line pitch in output pixels
  edgePx: 1.35,        // ink outline half-width in output pixels
  contrast: 1.15,
  wobblePx: 1.1,       // hand wobble of outlines (output px)
  boil: 1.0,           // 0 = frozen drawing, 1 = line boil on twos
  ambient: 0.36,
  fadeY: [-2.6, 0.2],  // world y range where the drawing dissolves into blank paper
  island: [7, -3, 14, 14], // plan centre x,z and half extents rx,rz of the drawn island (beyond: unfinished)
  skyLines: 1.0,
};

const GBUF_VS = /* glsl */`
precision highp float;
in vec3 position; in vec3 normal; in float aId; in vec2 uv;
uniform mat4 modelMatrix, viewMatrix, projectionMatrix;
// depth push: the Monument Valley occlusion fix. A piece that is really k*(1,1,1) nearer than the piece it
// visually joins is pushed back along the view axis by k*sqrt(3), so it depth-sorts like the piece it joins.
// Screen position is unchanged (orthographic). Scaled by uMagic (1 at the magic angle, 0 off-angle).
uniform vec3 uPushAxis, uPushOrigin;
uniform float uPushRate, uPushMax, uPushConst, uMagic;
out vec3 vN; out vec3 vP; out float vId; out float vViewZ; out vec2 vUv;
void main() {
  vec4 wp = modelMatrix * vec4(position, 1.0);
  vP = wp.xyz; vUv = uv;
  vN = normalize(mat3(modelMatrix) * normal);
  vec4 mv = viewMatrix * wp;
  vViewZ = -mv.z;
  float push = uPushConst + clamp(dot(wp.xyz - uPushOrigin, uPushAxis), 0.0, uPushMax) * uPushRate;
  mv.z -= push * uMagic;
  vId = aId;
  gl_Position = projectionMatrix * mv;
}`;

const GBUF_FS = /* glsl */`
precision highp float;
precision highp sampler2D;
layout(location = 0) out vec4 o0;
layout(location = 1) out vec4 o1;
layout(location = 2) out vec4 o2;
in vec3 vN; in vec3 vP; in float vId; in float vViewZ; in vec2 vUv;
uniform float uMat, uAlbedo, uObjId;
uniform sampler2D uDecal; uniform float uDecalOn; // text/lines painted on the surface (alpha = ink); uDecalOn 2 = residue orange
uniform vec3 uSun;
uniform sampler2D uShadowMap;
uniform mat4 uLightVP;
uniform float uShadowOn, uShadowTexel, uReceive, uFlatLight;
uniform vec4 uWin;      // cell w, cell h, glass w frac, glass h frac  (x=0: no windows)
uniform vec4 uWinBox;   // x0, z0, size x, size z  (facade origin for centring the window grid)
uniform vec4 uWinY;     // y min, y max of window band, chicago-window flag, belt courses flag

float shadowAt(vec3 p, vec3 n) {
  if (uShadowOn < 0.5 || uReceive < 0.5) return 1.0;
  vec4 lp = uLightVP * vec4(p + n * 0.03, 1.0);
  vec3 c = lp.xyz / lp.w * 0.5 + 0.5;
  if (c.x < 0.0 || c.x > 1.0 || c.y < 0.0 || c.y > 1.0 || c.z > 1.0) return 1.0;
  float s = 0.0;
  for (int i = -2; i <= 2; i++) for (int j = -2; j <= 2; j++) {
    float d = texture(uShadowMap, c.xy + vec2(float(i), float(j)) * uShadowTexel).r;
    s += (c.z - 0.0012 <= d) ? 1.0 : 0.0;
  }
  return s / 25.0;
}

// facade windows: returns 0 wall, 1 glass, 0.5 frame/mullion, 0.25 belt course
float facade(vec3 p, vec3 n) {
  if (uWin.x <= 0.0 || abs(n.y) > 0.5) return 0.0;
  bool xFace = abs(n.x) > abs(n.z);
  float coord = xFace ? (p.z - uWinBox.y) : (p.x - uWinBox.x);
  float width = xFace ? uWinBox.w : uWinBox.z;
  float cells = floor(width / uWin.x + 0.001);
  float margin = (width - cells * uWin.x) * 0.5;
  float lc = coord - margin;
  float yl = p.y - uWinY.x;
  float floors = floor((uWinY.y - uWinY.x) / uWin.y + 0.001);
  float belt = 0.0;
  if (uWinY.w > 0.5 && yl > -0.02 && yl < floors * uWin.y + 0.02) {
    float fy = fract(yl / uWin.y);
    if (fy > 0.93 || fy < 0.025) belt = 0.25;
  }
  if (lc < 0.0 || lc > cells * uWin.x || yl < 0.0 || yl > floors * uWin.y) return belt;
  float fx = fract(lc / uWin.x) - 0.5;
  float fy = fract(yl / uWin.y) - 0.45;
  float hw = uWin.z * 0.5, hh = uWin.w * 0.5;
  if (abs(fx) < hw && abs(fy) < hh) {
    // Chicago window: wide fixed pane flanked by two narrow sashes
    if (uWinY.z > 0.5) {
      float m = abs(fx) / hw;
      if (abs(m - 0.52) < 0.07) return 0.5;
    } else if (abs(fy) < 0.06 * hh * 2.0) return 0.5;
    return 1.0;
  }
  return belt;
}

void main() {
  vec3 n = normalize(vN);
  if (!gl_FrontFacing) n = -n;
  vec3 L = normalize(uSun);
  float diff = clamp(max(dot(n, L), 0.0) / max(L.y, 0.3), 0.0, 1.15);
  float sh = diff > 0.0 ? shadowAt(vP, n) : 1.0;
  sh = mix(0.18, 1.0, sh);
  if (uFlatLight > 0.0) { diff = mix(diff, 0.78, uFlatLight); sh = mix(sh, 1.0, uFlatLight * 0.6); }
  float pat = facade(vP, n);
  float idPat = pat;
  if (uDecalOn > 0.5) {
    float m = texture(uDecal, vUv).a;
    if (m > 0.02) { pat = (uDecalOn > 1.5 ? 4.0 : 2.0) + min(m, 0.999); idPat = 0.0; }
  }
  o0 = vec4(n, uMat);
  o1 = vec4(vP, vViewZ);
  o2 = vec4(diff * sh, uAlbedo, pat, uObjId + vId * 0.0137 + idPat * 0.31);
}`;

const SPRITE_FS = /* glsl */`
precision highp float;
precision highp sampler2D;
layout(location = 0) out vec4 o0;
layout(location = 1) out vec4 o1;
layout(location = 2) out vec4 o2;
in vec3 vN; in vec3 vP; in float vId; in float vViewZ; in vec2 vUv;
uniform sampler2D uAtlas;
uniform vec4 uCell;    // u0, v0, du, dv of the current frame in the atlas
uniform float uFlipX, uObjId, uAlphaCut;
void main() {
  vec2 st = vec2(uFlipX > 0.5 ? 1.0 - vUv.x : vUv.x, vUv.y);
  vec4 c = texture(uAtlas, uCell.xy + st * uCell.zw);
  if (c.a < uAlphaCut) discard;
  o0 = vec4(normalize(vN), 25.0);
  o1 = vec4(vP, vViewZ);
  o2 = vec4(c.rgb, uObjId);
}`;

const QUAD_VS = /* glsl */`
precision highp float;
in vec3 position; in vec2 uv;
out vec2 vUv;
void main() { vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`;

const COMPOSITE_FS = /* glsl */`
precision highp float;
precision highp sampler2D;
in vec2 vUv;
out vec4 fragColor;
uniform sampler2D tN, tP, tL;
uniform vec2 uRes;          // composite resolution (supersampled)
uniform float uSS;          // supersample factor
uniform float uPPU;         // composite pixels per world unit
uniform vec3 uCamR, uCamU, uCamV;  // camera right, up, toward-camera (world)
uniform float uSeed;        // boil seed (changes on twos)
uniform vec3 uPaper, uInk;
uniform float uHatchPx, uEdgePx, uContrast, uWobblePx, uAmbient, uSkyLines;
uniform vec2 uFade;
uniform vec4 uIsland;
uniform vec3 uPal[${N_MAT}];
uniform vec4 uBlooms[4];    // colour blooms: centre xy, radius (composite px; r <= 0: unused), softness
uniform float uBloomAll;    // 1 = everything coloured
uniform vec2 uSunPx;        // Kandinsky sun centre (composite px)
uniform float uSunR;        // sun radius (composite px), 0 = none
uniform vec4 uSkyBox;       // sky gradient: y0 (bottom, uv), y1 (top, uv)
uniform vec3 uTarget;       // camera look-at point (aerial lightening of what lies behind it)
uniform vec2 uAerial;       // distance behind target where lightening starts / is full

// ---------- noise ----------
float h21(vec2 p) { p = fract(p * vec2(123.34, 456.21)); p += dot(p, p + 45.32); return fract(p.x * p.y); }
float h11(float x) { return fract(sin(x * 127.1 + 311.7) * 43758.5453); }
float vnoise(vec2 p) {
  vec2 i = floor(p), f = fract(p); vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(mix(h21(i), h21(i + vec2(1, 0)), u.x), mix(h21(i + vec2(0, 1)), h21(i + vec2(1, 1)), u.x), u.y);
}
float fbm(vec2 p) { float v = 0.0, a = 0.5; for (int i = 0; i < 4; i++) { v += a * vnoise(p); p = p * 2.03 + 17.1; a *= 0.5; } return v; }
float vnoise3(vec3 p) {
  return mix(vnoise(p.xy + floor(p.z) * 31.7), vnoise(p.xy + (floor(p.z) + 1.0) * 31.7), smoothstep(0.0, 1.0, fract(p.z)));
}

// ---------- G-buffer access ----------
struct G { vec3 n; float mat; vec3 p; float vz; float light; float alb; float pat; float id; };
G fetchG(vec2 uv) {
  G g;
  vec4 a = texture(tN, uv), b = texture(tP, uv), c = texture(tL, uv);
  g.n = a.xyz; g.mat = floor(a.w + 0.5); g.p = b.xyz; g.vz = b.w; g.light = c.x; g.alb = c.y; g.pat = c.z; g.id = c.w;
  return g;
}

// screen-space pitch of the world-space line family u = dot(P, w) on a plane with normal n (per composite pixel)
float pitchOf(vec3 w, vec3 n) {
  float vn = dot(uCamV, n);
  vn = sign(vn) * max(abs(vn), 0.06);
  float wv = dot(w, uCamV);
  vec2 g = vec2(dot(w, uCamR) - dot(uCamR, n) * wv / vn, dot(w, uCamU) - dot(uCamU, n) * wv / vn);
  return max(length(g), 1e-4) / uPPU;  // world-u change per composite pixel
}

// one engraved line family. tone 0 = black .. 1 = white. returns ink coverage
float lineFamily(vec3 P, vec3 n, vec3 w, float cover, float seed, float pitchPx, float fin) {
  if (cover <= 0.001) return 0.0;
  float g = pitchOf(w, n);
  float u = dot(P, w) / (g * pitchPx);           // line index space: 1 unit = one line pitch on screen
  // the engraver's hand: slow waviness + tremor, plus boil on twos
  vec3 q = P * uPPU / (uSS * 90.0);
  u += 0.22 * (vnoise3(q * 1.0 + seed * 7.0 + uSeed * 0.37) - 0.5);
  u += 0.06 * (vnoise3(q * 6.0 + seed * 3.0 + uSeed) - 0.5);
  float li = floor(u);
  // along-line coordinate for swelling and breaks (world-anchored)
  vec3 al = normalize(cross(n, w) + 1e-4);
  float a = dot(P, al) * uPPU / (uSS * 14.0);
  float swell = 0.72 + 0.56 * vnoise(vec2(a + li * 13.7, li * 1.91 + seed));
  float w0 = clamp(cover * swell * (0.85 + 0.3 * h11(li + seed * 17.0)), 0.0, 0.84);
  // light lines break up into flicks (white-line engraving reads the other way round)
  float brk = vnoise(vec2(a * 2.3 + li * 7.1, li + seed * 5.0));
  w0 *= smoothstep(0.08, 0.35, brk + cover * 1.2);
  // unfinished drawing: each line stops crisply where the finish field drops below its own threshold
  w0 *= step(0.15 + 0.7 * h11(li * 3.7 + seed * 11.0), fin);
  float d = abs(fract(u) - 0.5);
  float aa = 0.55 / pitchPx;
  return (1.0 - smoothstep(w0 * 0.5 - aa, w0 * 0.5 + aa, d)) * smoothstep(0.0, 0.07, w0);
}

void axes(vec3 n, out vec3 w1, out vec3 w2, out vec3 w3) {
  vec3 an = abs(n);
  if (an.y >= an.x && an.y >= an.z) {        // tops: lines run along x, cross along z, then diagonal
    w1 = vec3(0.0, 0.0, 1.0); w2 = vec3(1.0, 0.0, 0.0); w3 = normalize(vec3(1.0, 0.0, -1.0));
  } else if (an.x >= an.z) {                  // walls facing x: horizontal courses, then verticals
    w1 = vec3(0.0, 1.0, 0.0); w2 = vec3(0.0, 0.0, 1.0); w3 = normalize(vec3(0.0, 1.0, 1.0));
  } else {                                    // walls facing z
    w1 = vec3(0.0, 1.0, 0.0); w2 = vec3(1.0, 0.0, 0.0); w3 = normalize(vec3(-1.0, 1.0, 0.0));
  }
}

float toneOf(G g) {
  float sky = 0.5 + 0.5 * g.n.y;
  float t = g.alb * (uAmbient * (0.75 + 0.25 * sky) + (1.0 - uAmbient) * g.light);
  // facade: glass is dark, frames light
  if (g.pat > 1.5) {}
  else if (g.pat > 0.9) t *= 0.22 + 0.25 * g.light;
  else if (g.pat > 0.4) t = max(t, 0.55);
  else if (g.pat > 0.2) t *= 0.8;
  // hand-modulated tone
  t *= 0.92 + 0.16 * vnoise(g.p.xz * 0.35 + g.p.y * 0.21);
  // aerial perspective: the engraver uses fewer lines for what lies far behind the subject
  float behind = dot(uTarget - g.p, uCamV);
  t = mix(t, 1.0, 0.5 * smoothstep(uAerial.x, uAerial.y, behind));
  t = clamp((t - 0.5) * uContrast + 0.5, 0.0, 1.0);
  return t;
}

// drawn-ness of a point: 1 inside the finished drawing, 0 where the engraver stopped
float finished(vec3 p, float mat) {
  float ny = fbm(p.xz * 0.45 + 3.0) - 0.5;
  float f = smoothstep(uFade.x, uFade.y, p.y + ny * 1.4);
  vec2 d = abs(p.xz - uIsland.xy) - uIsland.zw;
  float e = max(d.x, d.y) + (fbm(p.xz * 0.3 + p.y * 0.2) - 0.5) * 2.2;
  if (mat == 7.0) f *= 1.0 - smoothstep(-3.5, 0.0, e);   // only the ground plane frays at the island edge
  return f;
}

// --- ink edges: plane distance, normal crease, object id, background. ---
float edgeAt(vec2 uv, G c, float rpx) {
  vec2 px = 1.0 / uRes;
  float e = 0.0;
  for (int k = 0; k < 8; k++) {
    float ang = float(k) * 0.78539816;
    vec2 o = vec2(cos(ang), sin(ang)) * rpx;
    G s = fetchG(uv + o * px);
    if (c.mat < 0.5 && s.mat < 0.5) continue;
    if ((c.mat < 0.5) != (s.mat < 0.5)) {
      float fz = c.mat < 0.5 ? finished(s.p, s.mat) : finished(c.p, c.mat);
      e = max(e, step(0.45, fz));
      continue;
    }
    float pd = abs(dot(s.p - c.p, c.n));
    float tol = 0.035 + rpx / uPPU * 0.25;
    float de = smoothstep(tol, tol * 2.5, pd);
    float ne = smoothstep(0.18, 0.4, 1.0 - dot(s.n, c.n));
    float ie = abs(s.id - c.id) > 0.004 ? 1.0 : 0.0;
    e = max(e, max(de, max(ne, ie)));
    // silhouettes (big plane-distance jumps) get a heavier line
    G s2 = fetchG(uv + o * px * 1.9);
    if (s2.mat > 0.5) e = max(e, smoothstep(0.6, 1.2, abs(dot(s2.p - c.p, c.n))) * 0.95);
  }
  return e;
}

// ---------- colored pencil ----------
// pigment coverage of a pencil stroke field in screen space at angle ang, pressure 0..1
float pencil(vec2 px, float ang, float pressure, float seed) {
  vec2 d = vec2(cos(ang), sin(ang)), nn = vec2(-d.y, d.x);
  float s = dot(px, nn) / (2.4 * uSS);
  float a = dot(px, d) / uSS;
  float li = floor(s);
  float streak = vnoise(vec2(a * 0.05 + li * 9.13 + seed, li * 0.71));
  float tooth = vnoise(px / (1.3 * uSS) + seed * 11.0) * 0.6 + vnoise(px / (3.7 * uSS) + seed) * 0.4;
  float strokeBody = 1.0 - smoothstep(0.32, 0.5, abs(fract(s) - 0.5));
  float p = pressure * (0.7 + 0.5 * streak) * (0.65 + 0.35 * strokeBody);
  return clamp((p - tooth * 0.75) * 2.4 + 0.25 * p, 0.0, 1.0);
}

vec3 shadeColor(vec3 c) {
  // shadow pencil: deepen while keeping the hue (squaring orange made it crimson: no red in this film),
  // cooled toward ultramarine (colored-pencil layering)
  return mix(c * 0.7, vec3(0.22, 0.25, 0.52), 0.32);
}

// Klimt gold mosaic (towers, turntable): returns pattern ink (0..1) and color tweak
vec4 klimt(vec3 P, vec3 n, float big) {
  vec3 an = abs(n);
  vec2 q = an.y > max(an.x, an.z) ? P.xz : (an.x > an.z ? P.zy : P.xy);
  q *= 2.6 / big;
  vec2 cell = floor(q), f = fract(q) - 0.5;
  float r = h21(cell);
  vec3 col = r < 0.33 ? vec3(0.88, 0.66, 0.15) : (r < 0.66 ? vec3(0.96, 0.52, 0.16) : (r < 0.85 ? vec3(0.35, 0.62, 0.92) : vec3(0.95, 0.83, 0.42)));
  float ink = 0.0;
  if (r > 0.5) { // spiral / concentric eye
    float rr = length(f);
    float sp = fract(rr * 7.0 - atan(f.y, f.x) / 6.2831853 * (r > 0.75 ? 1.0 : 0.0));
    ink = (1.0 - smoothstep(0.08, 0.2, abs(sp - 0.5))) * step(rr, 0.42);
  } else {       // little square inside the square
    vec2 af = abs(f);
    float sq = max(af.x, af.y);
    ink = 1.0 - smoothstep(0.02, 0.06, abs(sq - 0.26));
  }
  float border = 1.0 - smoothstep(0.44, 0.49, max(abs(f.x), abs(f.y)));
  return vec4(col, max(ink, 1.0 - border) * 0.85);
}

void main() {
  vec2 frag = vUv * uRes;
  // hand wobble: the whole drawing is very slightly warped (on twos)
  vec2 wob = vec2(vnoise(frag / (uSS * 140.0) + uSeed * 0.13), vnoise(frag / (uSS * 140.0) + 51.3 + uSeed * 0.13)) - 0.5;
  vec2 uvW = vUv + wob * uWobblePx * uSS * 2.0 / uRes;
  G g = fetchG(uvW);

  // ---------- paper ----------
  float fib = vnoise(vec2(frag.x / (uSS * 2.5), frag.y / (uSS * 22.0)));
  float tooth = vnoise(frag / (uSS * 1.4));
  float blot = fbm(frag / (uSS * 260.0));
  vec3 paper = uPaper * (1.0 - 0.045 * blot - 0.025 * fib - 0.02 * tooth);
  vec2 vc = vUv - 0.5;
  paper *= 1.0 - 0.10 * dot(vc, vc);

  float ink = 0.0;
  vec3 col = paper;
  float bloom = 0.0;
  bloom = uBloomAll;
  {
    // colour floods out from each centre as pencil strokes that end at staggered lengths
    vec2 dd = vec2(cos(1.05), sin(1.05));
    float sIdx = floor(dot(frag, vec2(-dd.y, dd.x)) / (2.4 * uSS));
    float jag0 = (h11(sIdx * 1.7) - 0.5) * 34.0 * uSS;
    float wan = (fbm(frag / (uSS * 90.0)) - 0.5);
    for (int k = 0; k < 4; k++) {
      vec4 B = uBlooms[k];
      if (B.z <= 0.0) continue;
      float dist = length(frag - B.xy);
      float jag = jag0 * min(1.0, B.z / (200.0 * uSS)) + wan * min(160.0 * uSS, B.z * 0.45);
      bloom = max(bloom, 1.0 - smoothstep(B.z - 10.0 * uSS, B.z, dist + jag));
    }
  }

  if (g.mat > 24.5 && g.mat < 25.5) {
    // ---------- anime sprite (Jade): her own colour, on the paper, with an ink outline from the edge pass
    col = mix(g.light * vec3(1.0), g.light * vec3(1.0), 0.0);
    col = vec3(g.light, g.alb, g.pat);
    col *= mix(vec3(1.0), uPaper / max(max(uPaper.r, uPaper.g), uPaper.b), 0.35);
    vec2 ew = vec2(vnoise(frag / (uSS * 23.0) + uSeed * 0.71), vnoise(frag / (uSS * 23.0) + 9.1 + uSeed * 0.71)) - 0.5;
    vec2 uvE = uvW + ew * 1.0 * uSS / uRes;
    G ge = fetchG(uvE);
    ink = edgeAt(uvE, ge, uEdgePx * uSS * 0.8) * 0.85;
  } else if (g.mat < 0.5) {
    // ---------- sky: fine horizontal engraved lines, swelling toward the top; clouds are reserved paper ----------
    float pitch = uHatchPx * uSS * 1.25;
    float u = frag.y / pitch + 0.12 * (vnoise(vec2(frag.x / (uSS * 300.0), frag.y / (uSS * 500.0)) + uSeed * 0.11) - 0.5);
    float li = floor(u);
    float cloud = fbm(vec2(frag.x / (uSS * 520.0), frag.y / (uSS * 150.0)) + 4.0);
    float dens = pow(smoothstep(uSkyBox.x, uSkyBox.y, vUv.y), 1.4) * uSkyLines;
    dens *= 1.0 - 0.85 * smoothstep(0.5, 0.66, cloud);
    float sw = 0.75 + 0.5 * vnoise(vec2(frag.x / (uSS * 40.0) + li * 7.7, li));
    float w0 = clamp(dens * 0.42 * sw, 0.0, 0.8);
    w0 *= smoothstep(0.05, 0.3, vnoise(vec2(frag.x / (uSS * 14.0) + li * 3.3, li)) + dens * 1.5);
    float d = abs(fract(u) - 0.5);
    ink = (1.0 - smoothstep(w0 * 0.5 - 0.5 / pitch, w0 * 0.5 + 0.5 / pitch, d)) * smoothstep(0.0, 0.07, w0);
    // sun: concentric rings (Kandinsky when coloured)
    if (uSunR > 0.0) {
      float r = length(frag - uSunPx) / uSunR;
      if (r < 1.0) ink *= smoothstep(0.92, 1.0, r);
      float ring = abs(fract(r * 4.0) - 0.5);
      ink = max(ink, (1.0 - smoothstep(0.035, 0.07, ring)) * step(r, 1.02) * 0.9);
      if (bloom > 0.0 && r < 1.0) {
        float k = floor(r * 4.0);
        vec3 rc = k < 1.0 ? vec3(0.97, 0.52, 0.13) : k < 2.0 ? vec3(0.96, 0.78, 0.22) : k < 3.0 ? vec3(0.33, 0.63, 0.95) : vec3(0.98, 0.52, 0.18);
        float cov = pencil(frag, 1.05 + k * 0.6, 0.95, 3.0 + k) * bloom;
        col = mix(col, col * rc, cov);
      }
    }
    if (bloom > 0.0) {
      vec3 sky = uPal[0];
      float cov = pencil(frag, 1.05, mix(0.85, 0.45, 1.0 - vUv.y) , 1.0) * bloom;
      col = mix(col, col * sky, cov * 0.85);
      ink *= mix(1.0, 0.38, bloom);
    }
  } else {
    float tone = toneOf(g);
    float fin = finished(g.p, g.mat);
    vec3 n = g.n;
    vec3 w1, w2, w3; axes(n, w1, w2, w3);
    float pitch = uHatchPx * uSS;
    float jade = (g.mat >= 13.0 && g.mat <= 19.0) || g.mat == 24.0 ? 1.0 : 0.0;
    float coloured = max(bloom, jade);
    // engraving: line families switch on as the tone darkens
    float t = tone;
    float hatchAmt = mix(1.0, 0.6, coloured * (1.0 - jade)) * mix(1.0, 0.25, jade);
    float c1 = clamp((0.97 - t) * 1.2, 0.0, 0.8);
    float c2 = clamp((0.58 - t) * 1.6, 0.0, 0.62);   // capped: white lines must survive in the darks
    float c3 = clamp((0.26 - t) * 2.2, 0.0, 0.42);
    float l1 = lineFamily(g.p, n, w1, c1 * hatchAmt, 1.0, pitch, fin);
    float l2 = lineFamily(g.p, n, w2, c2 * hatchAmt, 2.0, pitch * 1.08, fin * 0.92);
    float l3 = lineFamily(g.p, n, w3, c3 * hatchAmt, 3.0, pitch * 1.2, fin * 0.85);
    ink = max(l1, max(l2 * 0.95, l3 * 0.9));
    if (g.mat == 28.0) {
      // water: horizontal engraved wave lines in screen space, sparser toward the light
      float wp = pitch * 2.0;
      float u = frag.y / wp + 0.35 * sin(frag.x / (uSS * 37.0) + floor(frag.y / wp) * 1.7) + 0.15 * vnoise(frag / (uSS * 60.0) + uSeed * 0.2);
      float li = floor(u);
      float w0 = clamp((1.0 - t) * 0.5 + 0.06, 0.0, 0.42) * (0.5 + 0.9 * vnoise(vec2(frag.x / (uSS * 25.0) + li * 5.3, li)));
      w0 *= step(0.48, vnoise(vec2(frag.x / (uSS * 70.0) + li * 2.1, li * 0.7)));
      ink = (1.0 - smoothstep(w0 * 0.5 - 0.5 / wp, w0 * 0.5 + 0.5 / wp, abs(fract(u) - 0.5))) * smoothstep(0.0, 0.07, w0) * fin;
    }
    if (g.mat == 11.0 || g.mat == 15.0 || g.mat == 18.0) ink = max(ink, 0.93 * fin); // solid blacks: shades, hair, crop top
    float decal = g.pat > 1.5 && g.pat < 3.5 ? g.pat - 2.0 : 0.0;          // painted text/lines (ink)
    float decalO = g.pat > 3.5 ? g.pat - 4.0 : 0.0;                         // painted residue (orange pencil)
    if (decal > 0.0) ink = max(ink * (1.0 - decal), decal);

    if (coloured > 0.0) {
      vec3 base = uPal[int(g.mat)];
      float cov;
      if (g.mat == 21.0 || g.mat == 20.0) {
        vec4 k = klimt(g.p, n, g.mat == 20.0 ? 0.6 : 1.0);
        base = mix(base, k.rgb, 0.7);
        ink = max(ink * 0.6, k.a * 0.55 * bloom);
      }
      float press = mix(1.1, 0.78, tone) * (jade > 0.5 ? 1.15 : 1.0);
      cov = pencil(frag, 1.05, press, g.mat);
      float covS = pencil(frag, -0.45, (1.0 - tone) * 0.9, g.mat + 7.0);
      vec3 c = mix(vec3(1.0), base, cov * coloured);
      c = mix(c, c * shadeColor(base) * 1.6, covS * coloured * 0.6);
      // white materials (jacket, sneakers, shirt) only get cool shading
      if (g.mat == 13.0 || g.mat == 17.0 || g.mat == 12.0) c = mix(vec3(1.0), vec3(0.72, 0.8, 0.95), covS * coloured * (1.0 - tone) * 0.9);
      col = paper * mix(vec3(1.0), c, fin);
    }
    if (decalO > 0.0) {
      float cov = pencil(frag, 0.6, 1.2, 9.0);
      col = mix(col, col * vec3(0.94, 0.47, 0.13) * 1.05, clamp(decalO * (0.55 + 0.45 * cov), 0.0, 1.0));
      ink *= 1.0 - 0.8 * decalO;
    }
    // engraver's halo: reserve a thin band of white paper around figures so they read against hatching
    bool isFig = (g.mat >= 9.0 && g.mat <= 19.0) || g.mat == 24.0 || g.mat == 25.0;
    if (!isFig) {
      float halo = 0.0;
      for (int k = 0; k < 12; k++) {
        float ang = float(k) * 0.5235988;
        G f = fetchG(uvW + vec2(cos(ang), sin(ang)) * 3.2 * uSS / uRes);
        bool fFig = (f.mat >= 9.0 && f.mat <= 19.0) || f.mat == 24.0 || f.mat == 25.0;
        if (fFig && dot(f.p - g.p, uCamV) > 0.05) halo = 1.0;
      }
      ink *= 1.0 - halo;
    }
    // ---------- ink outlines ----------
    vec2 ew = vec2(vnoise(frag / (uSS * 23.0) + uSeed * 0.71), vnoise(frag / (uSS * 23.0) + 9.1 + uSeed * 0.71)) - 0.5;
    vec2 uvE = uvW + ew * 1.4 * uSS / uRes;
    G ge = fetchG(uvE);
    float e = 0.0;
    if (ge.mat > 0.5) {
      e = edgeAt(uvE, ge, uEdgePx * uSS);
      float press = 0.78 + 0.22 * vnoise(frag / (uSS * 40.0) + uSeed * 0.3);
      e *= press;
      e *= step(0.3 + 0.4 * vnoise(frag / (uSS * 9.0)), finished(ge.p, ge.mat));
    } else {
      // silhouette from the outside
      e = edgeAt(uvE, ge, uEdgePx * uSS) * 0.95;
    }
    ink = max(ink, e);
  }
  // ink granulation on paper tooth
  float gran = 0.86 + 0.14 * smoothstep(0.2, 0.8, tooth);
  ink = clamp(ink * gran, 0.0, 1.0);
  col = mix(col, uInk, ink);
  fragColor = vec4(col, 1.0);
}`;

const DOWN_FS = /* glsl */`
precision highp float;
in vec2 vUv; out vec4 fragColor;
uniform sampler2D tSrc; uniform vec2 uSrcRes; uniform float uSS;
void main() {
  // tent filter, 2 output pixels wide, over the supersampled composite (offsets land on texel centres)
  vec2 base = vUv * uSrcRes;
  vec3 acc = vec3(0.0); float wsum = 0.0;
  int n = int(uSS + 0.5);
  for (int i = 0; i < 8; i++) {
    if (i >= 2 * n) break;
    for (int j = 0; j < 8; j++) {
      if (j >= 2 * n) break;
      vec2 o = vec2(float(i), float(j)) - uSS + 0.5;
      float w = max(0.0, 1.0 - abs(o.x) / uSS) * max(0.0, 1.0 - abs(o.y) / uSS);
      acc += texture(tSrc, (base + o) / uSrcRes).rgb * w; wsum += w;
    }
  }
  fragColor = vec4(acc / max(wsum, 1e-5), 1.0);
}`;

function hexToVec3(hex) {
  const h = String(hex).replace('#', '');
  return new THREE.Vector3(parseInt(h.slice(0, 2), 16) / 255, parseInt(h.slice(2, 4), 16) / 255, parseInt(h.slice(4, 6), 16) / 255);
}

export class Engraver {
  constructor(renderer, { width = 1920, height = 1080, ss = 2, style = {}, shadowSize = 4096 } = {}) {
    this.r = renderer;
    this.style = { ...DEFAULT_STYLE, ...style };
    this.ss = ss;
    this.shared = {
      uSun: { value: new THREE.Vector3(...(this.style.sun || [0.1, 1.0, 0.72])).normalize() },
      uShadowMap: { value: null },
      uLightVP: { value: new THREE.Matrix4() },
      uShadowOn: { value: 1 },
      uShadowTexel: { value: 1 / shadowSize },
      uMagic: { value: 1 },
    };
    this.shadowRT = new THREE.WebGLRenderTarget(shadowSize, shadowSize, { depthBuffer: true });
    this.shadowRT.depthTexture = new THREE.DepthTexture(shadowSize, shadowSize, THREE.FloatType);
    this.shared.uShadowMap.value = this.shadowRT.depthTexture;
    this.lightCam = new THREE.OrthographicCamera(-30, 30, 30, -30, 0.1, 200);
    this.depthMat = new THREE.MeshBasicMaterial({ colorWrite: false });
    this.palette = [];
    for (let i = 0; i < N_MAT; i++) this.palette.push(hexToVec3(PALETTE[i] || '#888888'));
    this.palette[0] = hexToVec3('#62B8FA'); // slot 0 = sky
    this.quadGeo = new THREE.PlaneGeometry(2, 2);
    this.compMat = new THREE.RawShaderMaterial({
      glslVersion: THREE.GLSL3, vertexShader: QUAD_VS, fragmentShader: COMPOSITE_FS, depthTest: false, depthWrite: false,
      uniforms: {
        tN: { value: null }, tP: { value: null }, tL: { value: null },
        uRes: { value: new THREE.Vector2() }, uSS: { value: ss }, uPPU: { value: 50 },
        uCamR: { value: new THREE.Vector3() }, uCamU: { value: new THREE.Vector3() }, uCamV: { value: new THREE.Vector3() },
        uSeed: { value: 0 }, uPaper: { value: hexToVec3(this.style.paper) }, uInk: { value: hexToVec3(this.style.ink) },
        uHatchPx: { value: this.style.hatchPx }, uEdgePx: { value: this.style.edgePx }, uContrast: { value: this.style.contrast },
        uWobblePx: { value: this.style.wobblePx }, uAmbient: { value: this.style.ambient }, uSkyLines: { value: this.style.skyLines },
        uFade: { value: new THREE.Vector2(...this.style.fadeY) }, uIsland: { value: new THREE.Vector4(...this.style.island) },
        uPal: { value: this.palette }, uBlooms: { value: [0, 1, 2, 3].map(() => new THREE.Vector4(0, 0, -1, 0)) }, uBloomAll: { value: 0 },
        uSunPx: { value: new THREE.Vector2() }, uSunR: { value: 0 }, uSkyBox: { value: new THREE.Vector4(...(this.style.skyBox || [0.58, 1.0, 0, 0])) },
        uTarget: { value: new THREE.Vector3() }, uAerial: { value: new THREE.Vector2(...(this.style.aerial || [6, 22])) },
      },
    });
    this.downMat = new THREE.RawShaderMaterial({
      glslVersion: THREE.GLSL3, vertexShader: QUAD_VS, fragmentShader: DOWN_FS, depthTest: false, depthWrite: false,
      uniforms: { tSrc: { value: null }, uSrcRes: { value: new THREE.Vector2() }, uSS: { value: ss } },
    });
    this.quad = new THREE.Mesh(this.quadGeo, this.compMat);
    this.quad.frustumCulled = false;
    this.quadScene = new THREE.Scene(); this.quadScene.add(this.quad);
    this.quadCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    this.setSize(width, height);
  }

  setSize(w, h) {
    this.w = w; this.h = h;
    const W = Math.round(w * this.ss), H = Math.round(h * this.ss);
    if (this.gbuf) { this.gbuf.dispose(); this.comp.dispose(); }
    this.gbuf = new THREE.WebGLRenderTarget(W, H, { count: 3, type: THREE.FloatType, minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter, depthBuffer: true });
    this.comp = new THREE.WebGLRenderTarget(W, H, { type: THREE.UnsignedByteType, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, depthBuffer: false });
    this.compMat.uniforms.uRes.value.set(W, H);
    this.downMat.uniforms.uSrcRes.value.set(W, H);
  }

  // A G-buffer material. opts: mat (MAT id), albedo 0..1, id (object id for outlines), receive (shadows),
  // windows: { cell:[w,h], glass:[fw,fh], box:[x0,z0,sx,sz], y:[y0,y1], chicago, belts }
  // push: { origin:[x,y,z], axis:[x,y,z] (unit), max, rate } depth ramp; pushConst: shared {value} uniform (figures)
  material({ mat = MAT.stone, albedo = 0.9, id = 0, receive = true, windows = null, side = THREE.FrontSide, push = null, pushConst = null, decal = null, decalMode = 1, flatLight = 0 } = {}) {
    const W = windows;
    const m = new THREE.RawShaderMaterial({
      glslVersion: THREE.GLSL3, vertexShader: GBUF_VS, fragmentShader: GBUF_FS, side, blending: THREE.NoBlending,
      uniforms: {
        ...this.shared,
        uMat: { value: mat }, uAlbedo: { value: albedo }, uObjId: { value: id }, uReceive: { value: receive ? 1 : 0 },
        uWin: { value: W ? new THREE.Vector4(W.cell[0], W.cell[1], W.glass[0], W.glass[1]) : new THREE.Vector4(0, 0, 0, 0) },
        uWinBox: { value: W ? new THREE.Vector4(...W.box) : new THREE.Vector4() },
        uWinY: { value: W ? new THREE.Vector4(W.y[0], W.y[1], W.chicago ? 1 : 0, W.belts === false ? 0 : 1) : new THREE.Vector4() },
        uPushAxis: { value: new THREE.Vector3(...(push ? push.axis : [0, 0, 1])) },
        uPushOrigin: { value: new THREE.Vector3(...(push ? push.origin : [0, 0, 0])) },
        uPushRate: { value: push ? push.rate : 0 }, uPushMax: { value: push ? push.max : 0 },
        uPushConst: pushConst || { value: 0 },
        uDecal: { value: decal }, uDecalOn: { value: decal ? decalMode : 0 }, uFlatLight: { value: flatLight },
      },
    });
    return m;
  }

  // Alpha-tested anime sprite drawn INTO the G-buffer (depth-tested against the set, inked, haloed, never hatched).
  // atlas: THREE.Texture holding cols x rows frames. Set frame with spriteFrame(m, index, flipX).
  spriteMaterial({ atlas, cols = 1, rows = 1, id = 77.7, pushConst = null, alphaCut = 0.5 }) {
    const m = new THREE.RawShaderMaterial({
      glslVersion: THREE.GLSL3, vertexShader: GBUF_VS, fragmentShader: SPRITE_FS, side: THREE.DoubleSide, blending: THREE.NoBlending,
      uniforms: {
        uMagic: this.shared.uMagic,
        uAtlas: { value: atlas }, uCell: { value: new THREE.Vector4(0, 0, 1 / cols, 1 / rows) }, uFlipX: { value: 0 },
        uObjId: { value: id }, uAlphaCut: { value: alphaCut },
        uPushAxis: { value: new THREE.Vector3(0, 0, 1) }, uPushOrigin: { value: new THREE.Vector3() },
        uPushRate: { value: 0 }, uPushMax: { value: 0 }, uPushConst: pushConst || { value: 0 },
      },
    });
    m.userData.grid = [cols, rows];
    return m;
  }
  spriteFrame(m, index, flipX = false) {
    const [cols, rows] = m.userData.grid;
    const i = ((Math.floor(index) % (cols * rows)) + cols * rows) % (cols * rows);
    const c = i % cols, r = Math.floor(i / cols);
    // atlas row 0 is the TOP row of the image (flipY texture): v grows upward
    m.uniforms.uCell.value.set(c / cols, 1 - (r + 1) / rows, 1 / cols, 1 / rows);
    m.uniforms.uFlipX.value = flipX ? 1 : 0;
  }

  // fit the sun's orthographic shadow camera around a world-space box
  fitShadow(center, radius) {
    const L = this.shared.uSun.value;
    this.lightCam.position.copy(center).addScaledVector(L, 80);
    this.lightCam.lookAt(center);
    this.lightCam.left = -radius; this.lightCam.right = radius; this.lightCam.top = radius; this.lightCam.bottom = -radius;
    this.lightCam.near = 1; this.lightCam.far = 160;
    this.lightCam.updateProjectionMatrix(); this.lightCam.updateMatrixWorld();
  }

  // frame: { seed, bloom: {x,y,r} | blooms: [{x,y,r} x<=4] (output px), bloomAll, sun: {x,y,r} (output px), target }
  render(scene, camera, frame = {}) {
    const r = this.r;
    const out = r.getRenderTarget();
    const prevAuto = r.autoClear;
    const prevClear = new THREE.Color(); r.getClearColor(prevClear); const prevAlpha = r.getClearAlpha();
    r.autoClear = true;

    // 1. shadow map
    scene.updateMatrixWorld();
    this.lightCam.updateMatrixWorld();
    const hidden = [];
    scene.traverse((o) => { if (o.isMesh && o.visible && o.userData.noShadow) { o.visible = false; hidden.push(o); } });
    scene.overrideMaterial = this.depthMat;
    r.setRenderTarget(this.shadowRT);
    r.setClearColor(0x000000, 0); r.clear();
    r.render(scene, this.lightCam);
    scene.overrideMaterial = null;
    for (const o of hidden) o.visible = true;
    this.shared.uLightVP.value.multiplyMatrices(this.lightCam.projectionMatrix, this.lightCam.matrixWorldInverse);

    // 2. G-buffer
    r.setRenderTarget(this.gbuf);
    r.setClearColor(0x000000, 0); r.clear();
    r.render(scene, camera);

    // 3. composite
    const u = this.compMat.uniforms;
    u.tN.value = this.gbuf.textures[0]; u.tP.value = this.gbuf.textures[1]; u.tL.value = this.gbuf.textures[2];
    camera.updateMatrixWorld();
    const e = camera.matrixWorld.elements;
    u.uCamR.value.set(e[0], e[1], e[2]).normalize();
    u.uCamU.value.set(e[4], e[5], e[6]).normalize();
    u.uCamV.value.set(e[8], e[9], e[10]).normalize();
    const viewH = (camera.top - camera.bottom) / camera.zoom;
    if (frame.target) u.uTarget.value.copy(frame.target);
    u.uPPU.value = (this.h * this.ss) / viewH;
    u.uSeed.value = frame.seed ?? 0;
    const S = this.ss;
    const blooms = frame.blooms || (frame.bloom ? [frame.bloom] : []);
    for (let k = 0; k < 4; k++) {
      const b = blooms[k];
      if (b && b.r > 0) u.uBlooms.value[k].set(b.x * S, (this.h - b.y) * S, b.r * S, 0); else u.uBlooms.value[k].set(0, 0, -1, 0);
    }
    u.uBloomAll.value = frame.bloomAll ?? 0;
    if (frame.sun) { u.uSunPx.value.set(frame.sun.x * S, (this.h - frame.sun.y) * S); u.uSunR.value = frame.sun.r * S; }
    else u.uSunR.value = 0;
    this.quad.material = this.compMat;
    r.setRenderTarget(this.comp);
    r.render(this.quadScene, this.quadCam);

    // 4. downsample into the caller's target
    this.downMat.uniforms.tSrc.value = this.comp.texture;
    this.quad.material = this.downMat;
    r.setRenderTarget(out);
    r.render(this.quadScene, this.quadCam);

    r.autoClear = prevAuto; r.setClearColor(prevClear, prevAlpha);
  }

  dispose() {
    this.gbuf.dispose(); this.comp.dispose(); this.shadowRT.dispose();
    this.compMat.dispose(); this.downMat.dispose(); this.quadGeo.dispose();
  }
}
