// Section B (chase restage) compositing helpers: dash(), traceMiss(), doubling(). Each returns plain layer / fx objects
// to splice into a shot (see _B_fxdemo.js). Files starting with "_" are skipped by the film merge.
//
// Conventions shared by the three:
//   clip      {src, matte, in, rate, fit, scale, x, y}: the matted Jade clip exactly as the shot's plate plays it
//             (matte: a path or {src, mode}). The shot must also hold a matted video layer of it (default id 'jade')
//             for the tracker to follow.
//   times     shot-local seconds on the shot's content clock, or absolute song seconds when `shotStart` (the shot's
//             start, seconds) is given.
//   scroll    world motion on a tracking plate: [vx, vy] px/s, or lt => [dx, dy] (cumulative px at shot time lt).
//             Marks, afterimages and scars ride it, so they stay where they were made. Static camera: leave it out.
import { val } from '../engine/src/keys.js';

const F = 1 / 24, E = F / 4;                       // one frame; a quarter-frame guard for key times
export const INK = '#0b0b0c', PAPER = '#ece7dc', ORANGE = '#F08A24', BLUE = '#8DB8E8';
export const HUES = ['#F08A24', '#3E6FD8', '#C9A227', '#C23B8E', '#3FA55B', '#E4572E', '#8DB8E8', '#E8D04A', '#8E5CC8', '#2BA59A',
  '#F28DB2', '#4B4FC4', '#9CCB3B'];

const matteOf = m => (typeof m === 'string' ? { src: m, mode: 'luma' } : { mode: 'luma', ...m });
const place = c => { const o = {}; for (const k of ['fit', 'scale', 'x', 'y', 'rotate', 'anchor']) if (c[k] !== undefined) o[k] = c[k]; return o; };
const dispOf = scroll => (typeof scroll === 'function' ? t => { const d = scroll(t); return Array.isArray(d) ? d : [d, 0]; }
  : t => [(scroll?.[0] || 0) * t, (scroll?.[1] || 0) * t]);
const local = (t, shotStart) => (shotStart === undefined ? t : t - shotStart);
// a clip-relative window as a mask: source crop + the rect it came from (holds for an unscaled 16:9 cover clip)
const windowOf = c => (c ? { crop: c, rect: [c[0] * 1920, c[1] * 1080, (c[2] - c[0]) * 1920, (c[3] - c[1]) * 1080] } : {});

// ---------------------------------------------------------------------------------------------------------------
// dash(): a Celeste-style air dash at shot time `at`.
//   `freeze` frames        the whole picture stands still on the pose at `at` (fx hold)
//   `dark` frame(s)        still frozen, Jade darkened
//   then                   a white ring bursts at her centre (6 frames); while she travels, `afterimages` pale-blue
//                          silhouettes are dropped every `every` frames, stay put and fade over `fade` frames; a thin
//                          white speed line trails her
//   at `land`              a one-frame white disc at her feet and a dust ring (10 frames)
//   shade     0 = flat silhouettes in `color`; up to 1 = her own shading shows through in `color` (reads better on paper)
//   crops     optional [[x0, y0, x1, y1], ...] source windows (afterimage k; [0] also masks the dark frame) for a
//             matte that holds more than her body; unscaled 16:9 cover clips only
// `at` / `land` are on the content clock: everything after `at` plays (freeze + dark - 1) frames later in real time.
// Pass shotStart so `at` snaps to the frame grid (the freeze is then exactly freeze + dark identical frames).
// Returns {fx, under, over, layers, at, land}: put `under` below the Jade layer, `over` above it, add `fx` to the shot.
export function dash({ clip, at, land, shotStart, layer = 'jade', freeze = 2, dark = 1, darken = 0.22,
  afterimages = 3, every = 3, fade = 15, color = BLUE, opacity = 0.6, shade = 0.55, crops = null,
  center = {}, feet = {}, scroll = null, ring = {}, disc = {}, dust = {}, line = {}, id = 'dash' }) {
  if (shotStart !== undefined) {                   // absolute → local, snapped up to the frame grid
    const snap = t => Math.ceil((t - 1e-6) * 24) / 24 - shotStart;
    const d = land === undefined ? undefined : land - at;
    at = snap(at); if (d !== undefined) land = at + d;
  }
  const m = matteOf(clip.matte), D = dispOf(scroll), base = { src: clip.src, in: clip.in ?? 0, rate: clip.rate ?? 1, ...place(clip) };
  const cen = { layer, point: 'centroid', smooth: 2, ...center }, ft = { layer, point: 'bottom', smooth: 2, ...feet };
  const hold = (freeze + dark - 1) * F;
  const fx = [{ type: 'hold', at, until: at + hold }];
  const under = [], over = [];

  // afterimages: her matted silhouette frozen on the frame she was at, washed pale blue, riding the world scroll
  for (let k = 0; k < afterimages; k++) {
    const tf = at + k * every * F, t0 = tf + F - E;
    const bx = clip.x, by = clip.y;
    under.push({ id: `${id}_after${k}`, type: 'ghosts', ...base, matte: m, loop: false, freeze: tf, ...windowOf(crops?.[k]),
      x: (lt, env) => (val(bx, lt, env, 0) ?? 0) + D(lt)[0] - D(tf)[0], y: (lt, env) => (val(by, lt, env, 0) ?? 0) + D(lt)[1] - D(tf)[1],
      opacity: [[0, 0, 'hold'], [t0, 1], [t0 + fade * F, 0]],
      instances: [shade > 0 ? { opacity, color, tint: 1, grade: { contrast: shade } } : { opacity, color, tint: 0, grade: { exposure: 0, lift: color } }] });
  }
  const marks = part => ({ id: `${id}_marks_${part}`, type: 'canvas', module: 'b_dashfx', keepColor: true,
    params: { at, land, center: cen, feet: ft, scroll, ring, disc, dust, line, part } });
  under.push(marks('under'));                       // the speed line passes behind her
  // the dark frame: Jade alone, held on the freeze pose, on the real clock (the content clock is stopped here)
  if (dark > 0) over.push({ id: `${id}_dark`, type: 'video', ...base, matte: m, realtime: true, freeze: at, keepColor: true, ...windowOf(crops?.[0]),
    opacity: [[0, 0, 'hold'], [at + freeze * F - E, 1, 'hold'], [at + (freeze + dark) * F - E, 0, 'hold']], grade: { exposure: darken, saturation: 0.7 } });
  over.push(marks('over'));                         // ring, landing disc, dust ring
  return { fx, under, over, layers: [...under, ...over], at, land };
}

// ---------------------------------------------------------------------------------------------------------------
// traceMiss(): agents fire at her from behind and miss. For each time tb: from tb - lead a thin ruled, dashed ink line
// draws from `origin` (the pistol, design px, [x, y] or keys) to the point at her feet where she was at tb - lag; at tb
// a 2-frame muzzle starburst at the origin and a burst of ink turf flecks at that point; an ink scar stays there for
// the rest of the shot. `target` is a follow spec on her matte ({layer, point: 'bottom', smooth, offset}); `targets`
// ([[x, y], ...] design px at tb - lag) overrides the track per shot. `size` scales every mark (1 suits a figure
// about a third of the frame tall).
// Returns {under, over, layers}: `under` (scars) below the Jade layer, `over` (line, starburst, flecks) above it.
export function traceMiss({ origin, times, shotStart, layer = 'jade', target = {}, targets = null, scroll = null, lag = 0.25, lead = 0.33,
  size = 1, width, dash: dashes, burst, flecks, scar, id = 'miss' }) {
  const params = { origin, times: times.map(t => local(t, shotStart)), target: { layer, point: 'bottom', smooth: 3, ...target }, targets, scroll, lag, lead,
    size, width, dash: dashes, burst, flecks, scar };
  const mk = part => ({ id: `${id}_${part}`, type: 'canvas', module: 'b_tracemiss', params: { ...params, part } });
  const under = [mk('under')], over = [mk('over')];
  return { under, over, layers: [...under, ...over] };
}

// ---------------------------------------------------------------------------------------------------------------
// doubling(): the number of Jades doubles on each of the given times (1, 2, 4, 8, 16 for four times).
// Every Jade already on screen splits: the new copy starts stacked on its parent (same place, same frame of the clip)
// and peels away over `peel` s to its own slot in a bar ahead of and behind her. A slot is `spacing` px and
// `slotTime` s of her own clip, so the copies are her past and future selves on the same route (behind = earlier).
// With steps [-8, 4, -2, 1] the slots after each beat are {0,-8}, {-8,-4,0,4}, {-10..4 step 2}, {-10..5}: the bar
// keeps its length and fills in. Copy n (in birth order) takes hues[(n - 1) % 13]; the real Jade stays untinted on
// top (her own layer, above these).
//   spacing   px per slot: a number or [dx, dy];  spacings: one of those per beat (the whole bar re-spaces on each beat)
//   stagger   px: odd and even slots sit this far above / below the line, so overlapping copies stay readable
// Returns {layers, fx, copies}: `layers` (back to front) go under the Jade layer; `fx` is a soft flash on each beat.
export function doubling({ clip, times, shotStart, steps = [-8, 4, -2, 1], spacing = 64, spacings = null, slotTime = F, stagger = 0, peel = 0.3,
  hues = HUES, opacity = 0.9, tint = 0.82, flash = 0.12, id = 'dbl' }) {
  const tb = times.map(t => local(t, shotStart)), G = tb.length, m = matteOf(clip.matte), in0 = clip.in ?? 0;
  steps = steps.slice(0, G);
  const vec = s => (Array.isArray(s) ? s : [s, 0]);
  const sp = Array.from({ length: G }, (_, g) => vec(spacings ? spacings[Math.min(g, spacings.length - 1)] : spacing));
  const ease = u => 1 - (1 - Math.min(1, Math.max(0, u))) ** 3;
  const spacingAt = lt => {                           // px per slot now (eases to each generation's value on its beat)
    let s = sp[0];
    for (let g = 1; g < G; g++) { const e = ease((lt - tb[g]) / peel); s = [s[0] + (sp[g][0] - s[0]) * e, s[1] + (sp[g][1] - s[1]) * e]; }
    return s;
  };
  const copies = [];
  for (let n = 1; n < 1 << G; n++) {
    const gen = 31 - Math.clz32(n), parent = n - (1 << gen);         // born on beat `gen` out of copy `parent` (0 = Jade)
    const slotOf = i => steps.reduce((a, s, g) => a + ((i >> g) & 1 ? s : 0), 0);
    copies.push({ n, gen, parent, slot: slotOf(n), from: slotOf(parent), t: tb[gen], color: hues[(n - 1) % hues.length] });
  }
  const layers = [...copies].sort((a, b) => Math.abs(b.slot) - Math.abs(a.slot) || a.n - b.n).map(c => {
    const slotAt = lt => c.from + (c.slot - c.from) * ease((lt - c.t) / peel);
    const row = ((c.slot % 2) + 2) % 2 ? stagger : -stagger, bx = clip.x, by = clip.y;
    return { id: `${id}_${String(c.n).padStart(2, '0')}`, type: 'ghosts', src: clip.src, matte: m, rate: clip.rate ?? 1, loop: false, ...place(clip),
      in: lt => in0 + slotAt(lt) * slotTime,
      x: (lt, env) => (val(bx, lt, env, 0) ?? 0) + slotAt(lt) * spacingAt(lt)[0],
      y: (lt, env) => (val(by, lt, env, 0) ?? 0) + slotAt(lt) * spacingAt(lt)[1] + row * ease((lt - c.t) / peel),
      opacity: [[0, 0, 'hold'], [c.t - E, 0], [c.t + 2 * F, 1]],
      instances: [{ color: c.color, tint, opacity }] };
  });
  const fx = flash > 0 ? [{ type: 'flash', at: tb, dur: 0.05, amount: flash }] : [];
  return { layers, fx, copies };
}
