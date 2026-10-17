// Section A: cold open, intro, Verse 1, pre-drop (0.00–40.65), shots C1, C3, C4, S1 (placement), S2, D1–D8, P1–P4.
// Not here: C2 (rewind teaser 1.90–7.24, REUSE assembled from final shots), P5/P6 onward.
// S1 media is the singing director's (media/sing/, see media/sing/NOTES.md); LIP picks the A/B/C lip-sync variant.
// The 13 R2 death tableaux are stills in media/shots/R2/ (see R2_STILLS below); Drop 1's director places them.
// Media: media/shots/<ID>/ (chosen.json per shot); track keys: media/shots/<ID>/track_*.json (tools/sectionA/track_quad.py).
import tracks from './_A_tracks.js';
import { subQuad, stepKeys } from '../../tools/v5/signs/quad.js';   // v5-signs: sub-quads of a sign track (D1)
import signTracks from '../../tools/v5/signs/tracks.js';            // v5-signs: D1 panels re-tracked per frame
import { D2_BILL_TOP, D2_BILL_BOT, D3_BILL_TOP, D3_BILL_BOT, D3_PLATE_R3, D3_ETCH_R3 } from '../../tools/v9/d23/d23_tracks_r7.js';   // v9 #2 round 7 (mirror on its sail at the window's front lower corner, camera 23 cm forward, drawn housing; round 5-6: d23_tracks_r5.js); round 5 (Acura TL door mirror, plate fitted to the drawn plate; round 3-4: d23_tracks.js); round 3: D2+D3 three.js scene, tracks from its rig (round 2: tools/v9/mirrors/d3_tracks_r2.js)

const S = (id, f) => `media/shots/${id}/${f}`;
const INK = '#0b0b0c', PAPER = '#ece7dc', ORANGE = '#F08A24';

// chosen takes (mirrors media/shots/<ID>/chosen.json)
const PLATE = {
  C1: { src: S('C1', 'take_3_engraved_patch.mp4'), in: 0.0, rate: 1 },   // v9: sleeve roundel re-lettered 1420 / MHz (tools/sectionE/patchfix.py). v3: no bullet, a muzzle flare at the centre pistol; two pencils
  C3: { src: S('C3', 'take_1_engraved.mp4'), in: 0.0, rate: 1 },
  C4: { src: S('C4', 'take_4_engraved_bun.mp4'), in: 0.0, rate: 1 },   // v3: two crossed pencils; near (right) sleeve has no roundel. v7 (Jade 0:11): the pencils go through a bun, short points (tools/c4_bun.py)
  S2: { src: S('S2', 'take_1_lens.mp4'), in: 0.0, rate: 1 },
  D1: { src: S('D1', 'take_1_engraved.mp4'), in: 0.0, rate: 1 },
  D2: { src: S('D23', 'v9r7_engraved.mp4'), in: 0.0, rate: 1 },   // v9 round 3 (Jade 0:24): one three.js scene for D2+D3 (tools/v9/d23/, docs/revisions/v9/fix_2_round3_threejs.md): from the passenger seat, Jade driving, head turned to her door mirror; the billboard is in the glass. v3: S('D2', 'take_2_engraved.mp4'), the bulb billboard big in the window
  D3: { src: S('D23', 'v9r7_engraved.mp4'), in: 2.18, rate: 1 },   // v9 round 3 (Jade 0:27): the same take, zooming into the door mirror until the TVA sedan fills the glass. round 2: S('D3', 'v9_take_2_push_r2.mp4') (interior mirror); v8: take_2_engraved_eraser.mp4
  D4: { src: S('D4', 'take_2_engraved.mp4'), in: 0.9, rate: 1 },   // v3: both cars on the right shoulder, the black sedan behind the Acura
  D5cu: { src: S('D5', 'take_2_engraved.mp4'), in: 0.0, rate: 1 },   // v3: close-up of the shades (lyric in the lenses)
  D5: { src: S('D5', 'take_3_engraved.mp4'), in: 0.3, rate: 1 },   // v3: the three men on the same lakefront shoulder as D4
  D6: { src: S('D6', 'take_2_engraved_breath.mp4'), in: 0.4, rate: 1 },   // v3: starts one beat later (32.36). Restaged: from the passenger seat, agents at HER window (same view direction as D8); two pencils. v7 (Jade 0:33): whole pink eraser + canon blue eraser (tools/matte_fix.py, tools/blue_eraser.py); v7 (Jade): she breathes (tools/d6_breath.py)
  D7: { src: S('D7', 'take_2_engraved.mp4') },   // v3: the agent's view through her window; played backward (D7_SRC)
  D8: { src: S('D8', 'take_3_engraved.mp4'), in: 1.18, rate: 1.25 },   // v3: reverse angle, only the BACK of her card; needle slams on "do" (36.92)
  P1: { src: S('P1', 'take_v9_2_engraved_jade.mp4'), in: 0.3, rate: 1 },   // v9 #9: agent at her driver's door, nose left as in D7, Jade driving (tools/v9/p1_matte.py; docs/revisions/v9/fix_1a_9_car.md). v8: take_2_engraved.mp4 (lakefront, empty car)
  P2: { src: S('P2', 'take_v9_1_engraved.mp4'), in: 0.3, rate: 1 },   // v9 #1a: D7's angle, she is behind the wheel (tools/v9/car_kf.py, car_vid.py). v8: take_2_engraved_eraser.mp4. v3: the v2 keyframe with the two-pencil bun. v7 (Jade 0:39): blue eraser top back in colour (tools/matte_fix.py)
  P3: { src: S('P3', 'take_1_engraved.mp4'), in: 0.4, rate: 1 },
  P4: { src: S('P4', 'take_1_engraved.mp4'), in: 0.0, rate: 1 },
};
// S1, v3: the watercolor singer (media/sing/NOTES.md, "v3 watercolor"). The lip sync is baked into the file: file
// time 0 = song 12.60, rate 1. LIP nudges it (A = lips 0.15 s earlier, C = 0.15 s later).
// v2 (pencil trace): S1_SRC 'media/sing/S1/take_1_lips.mp4', S1_IN = 12.6 - 12.9 + 1.04, S2_her on take_1_lips_wide.mp4, push from 1.3
const LIP = 'B';
const S1_IN = 0 + { A: 0.15, B: 0, C: -0.15 }[LIP];   // clip time at song 12.60
// v4 (Jade: glossier hair, no smile; media/sing/NOTES.md, "v4"): same framing, scale and timing as v3. v3: 'media/sing/S1/v3_sync_1080.mp4'
// v4 _open: the same take with the blink at 12.93-13.14 replaced by open eyes (tools/sing/v4_noblink.py); plain: 'media/sing/S1/v4_sync_1080.mp4'
// v5 (Jade, 2026-10-16: "reshoot the 2 lip sync clips using these 2 new photos", the pencils photo here): her own photo
// over the plate, photographic; Seedance 2.5 take v5_take_2, lag +0.46 baked in, first-frame blink at 12.60-12.72 replaced
// by open eyes (_open); per-frame matte with the two pencils keyed back in (tools/sing/v5_pencils.py). media/sing/NOTES.md
// "v5", docs/revisions/v9/sing_v5.md. Same contract (file time 0 = 12.60, rate 1, 1920x1080). v4: 'media/sing/S1/v4_sync_1080_open.mp4'
// v5 re-sync (Jade: "the video lags behind audio"): lag +0.61 (was +0.46: 'media/sing/S1/v5_sync_1080_open.mp4'); ear-test
// variants +0.61/+0.76/+0.91 in media/sing/review/v5_S1_lag+*.mp4. v5 re-sync: 'media/sing/S1/v5_sync_1080_l061_open.mp4'
// v5c (Jade: "local_a is good"): S1 shot again from the re-tinted pencils photo (v5_first.py V5_REV=c), take v5c_take_2,
// lag +0.15 (measured +0.10, leaning early), first frame held 12.60-12.75; matte with the pencils keyed in. Ear-test
// variants: media/sing/review/v5c_S1_lag+*.mp4
// v5c re-sync (Jade by ear: +0.30 "closer but the lips are still late"; +0.90 "about right, for the first half"):
// lag +0.90, eyes patched open on file frames 1-6 (v4_noblink.py, ref 0); matte -> v5c_sync_1080_l090_matte/ (pencils
// keyed). +0.15: 'media/sing/S1/v5c_sync_1080.mp4'
// v6 (Jade: the approved selfie media/sing/selfie/selfie_r3b_pick.png, "let's just use the hair down in both"; no pencils):
// one figure for S1 and V3S (tools/sing/v6_first.py), take v6_take_1, lag +1.09 measured over the whole take and
// "my dissertation defense" (the "night before" window alone locks on pre-roll mouthing). Eyes open on every frame
// 12.60-16.14, so no noblink; plain BiRefNet matte (no pencils to key). Ear-test variants: media/sing/review/v6_S1_lag*.mp4.
// media/sing/NOTES.md "v6", docs/revisions/v9/sing_v6.md. v5c +0.90: 'media/sing/S1/v5c_sync_1080_l090_open.mp4'
// v6b (Jade 2026-10-17: more natural head movement and wind; "audio sync is perfect" on v6): v6b_take_2, lag +0.95 read
// by the same trace markers that give v6_take_1 its +1.09; the blink at the cutaway (file frames 81-86) patched open.
// v6 (sync "perfect"): 'media/sing/S1/v6_sync_1080.mp4'
const S1_SRC = 'media/sing/S1/v6b_t2_sync_1080_open.mp4';
// slow push over the three singing cuts (1.0 -> 1.08 keeps the band, dot and 1420 MHz roundel in frame)
const S1_PUSH = (a, b) => ({ from: { scale: a }, to: { scale: b }, ease: 'linear' });
// v4 (Jade, 0:13: "start further away and then zoom in"): S1 opens on the whole Bean and pushes in to the v3 framing,
// landing on beat 8:4 (13.92) as "before" is sung. Three planes at three rates (docs/revisions/v4/plans/bean.md): her
// about the bottom-centre; the Bean and plaza (with the take's own plate and the arc lyric) about a point near the
// Bean's top; the towers behind, slower, their foot locked to the paving line. Plates: media/sing/plates/plate_wide_v4.md.
// v3: S1 was the take alone with S1_PUSH(1.0, 1.04), and the lyric and her matte rode the same push.
const S1_MATTE = S1_SRC.replace(/\.mp4$/, '_matte/');
const BEAN = (() => {
  const HER0 = 0.42, BEAN0 = 0.47429, C = [955.79, 113.91], HZ = 752, FAR1 = 1.5, FAR_K = 1.55521;
  const T0 = 0.44, T1 = 1.32, CREEP = 0.03, DUR = 3.54;   // shot-local: hold (2 % creep) to 13.04, push 13.04 -> 13.92
  const ss = x => { x = Math.min(1, Math.max(0, x)); return x * x * (3 - 2 * x); };
  const e = lt => lt <= T0 ? CREEP * Math.max(0, lt) / T0 : CREEP + (1 - CREEP) * (1 - Math.pow(1 - ss((lt - T0) / (T1 - T0)), 1.4));
  const g = lt => 1 + 0.04 * Math.min(1, Math.max(0, lt / DUR));   // v3's slow push over the shot, about the frame centre
  const sB = lt => Math.pow(BEAN0, 1 - e(lt)), sH = lt => Math.pow(HER0, 1 - e(lt)), r = lt => sB(lt) / BEAN0, rF = lt => Math.pow(FAR1, e(lt));
  // a similarity s about point c, then g about the centre (the engine draws screen = 960 + x + scale * (p - 960))
  const about = (s, c) => ({ scale: lt => g(lt) * s(lt), x: lt => g(lt) * (c[0] - 960) * (1 - s(lt)), y: lt => g(lt) * (c[1] - 540) * (1 - s(lt)) });
  return {
    her: about(sH, [960, 1080]),
    bean: about(sB, C),                // layers drawn in the landed (v3) frame: the take, the arc lyric
    beanPlate: about(r, C),            // plate_wide_v4_bean.png, drawn in the wide frame
    far: { scale: lt => g(lt) * FAR_K * rF(lt), x: lt => g(lt) * (C[0] + r(lt) * (960 - C[0]) - 960),
      y: lt => g(lt) * (C[1] + r(lt) * (HZ - C[1]) - 540 + rF(lt) * (540 - HZ)) },
    takeIn: [[0, 0], [1.18, 0], [1.32, 1]],   // the take's own frame (live plate, headlights) takes over as the move lands
  };
})();
// v2's S2 push from her face into the Lake Shore Drive headlights (unused since v3; kept for switching back)
const HEAD = [1600, 690], PUSH = 4.5;
const PUSH_KB = { from: { scale: 1.08, x: 0, y: 0 }, to: { scale: PUSH, x: -(HEAD[0] - 960) * PUSH, y: -(HEAD[1] - 540) * PUSH }, ease: 'inCubic' };
// keyframes: used instead of the takes while USE_STILLS is true (layout checks before the takes exist)
const USE_STILLS = false;
const KF = { C1: 'still_hero_engraved.png', C3: 'kf_sdr2.jpg', C4: 'kf_sdr1f.jpg', S2: 'kf_nbp1.jpg', D1: 'kf_sdr1.jpg', D2: 'kf_sdr1.jpg',
  D3: 'kf_v9.png', D4: 'kf_nbp1.png', D5: 'kf_sdr1.jpg', D5cu: 'kf_v3_cu.jpg', D6: 'kf_v3_2.jpg', D7: 'kf_v3_2.jpg', D8: 'kf_v3_2.jpg', P1: 'kf_v9a.jpg',
  P2: 'kf_v9d.png', P3: 'kf_sdr1.jpg', P4: 'kf_torso1.jpg' };
const MATTE = id => ({ src: PLATE[id].src.replace('_engraved.mp4', '_matte/'), mode: 'luma' });
const vid = (id, extra = {}) => {
  if (USE_STILLS) { const { matte, ...rest } = extra; return { id: `${id}_plate`, type: 'image', src: S(id, KF[id]), fit: 'cover', ...rest }; }
  return { id: `${id}_plate`, type: 'video', fit: 'cover', ...PLATE[id], ...extra };
};

export const R2_STILLS = ['01train', '02marinab', '03picasso', '04bridge', '05fountain', '06watertower', '07riverwalk',
  '08skydeck', '09lightning', '10gearsb', '11ferris', '12ice', '13sedanb'];

// D5: push in on the centre agent's sunglasses so the reflected lyric reads (face at ~(992, 215) → (960, 420))
const D5_KB = { from: { scale: 1, x: 0, y: 0 }, to: { scale: 2.2, x: -(992 - 960) * 2.2, y: 440 - 540 - (215 - 540) * 2.2 }, ease: 'inOutSine' };
// shrink a corner-pin track toward its centre (fx, fy = fraction of width/height kept)
const inset = (keys, fx, fy) => keys.map(([t, q]) => {
  const cx = (q[0] + q[2] + q[4] + q[6]) / 4, cy = (q[1] + q[3] + q[5] + q[7]) / 4;
  return [t, q.map((v, i) => (i % 2 ? cy + (v - cy) * fy : cx + (v - cx) * fx))];
});
// v7 (Jade 0:11): the pencils now go through a bun (take_4_engraved_bun.mp4) at source y ~61-201, mostly under the
// top letterbox bar (y < 138) at scale 1, so the hold frames the plate C4_DOWN px lower; the push still lands on the note.
const C4_DOWN = 60;
const C4_PUSH = { scale: [[0, 1], [0.55, 1, 'inOutCubic'], [1.45, 2.6]], x: [[0, 0], [0.55, 0, 'inOutCubic'], [1.45, -(1326 - 960) * 2.6]],
  y: [[0, C4_DOWN], [0.55, C4_DOWN, 'inOutCubic'], [1.45, -(850 - 540) * 2.6]] };
// D7 (v3): source time of take_2 over the shot's 2.64 s, backward: hand in the jacket (3.1) → card held up (0.0)
const D7_SRC = [[0, 3.1, 'inOutSine'], [2.1, 0.3, 'out'], [2.64, 0.0]];
// v3 in-world lyrics: lettering cut into the woodblock (lenses) / bulb-sign letters (rooftop billboard)
const WOODCUT = 'tools/sectionA/modules/woodcut.js';
// D2: the plate sits 90 px lower so the billboard's top panel clears the letterbox bar
const D2_DOWN = { y: 90 };
// D5cu: he is still walking: a small bob on every step (one step per beat, 0.44 s) on top of the take's own motion
const D5_BOB = { scale: 1.04, y: (lt) => -11 * Math.abs(Math.sin(Math.PI * lt / 0.44)) + 6, x: (lt) => 5 * Math.sin(Math.PI * lt / 0.88) };
// D3: two etched lines in the mirror's dark sky, left of the streetlight (the tracked strip, narrowed, deepened, moved left)
const D3_QUAD = inset(tracks.D3_etch, 0.62, 2.3).map(([t, q]) => [t, q.map((v, i) => v + (i % 2 ? 40 : -185))]);
// v5 (Jade, 0:22: "highway signs, add woodcut texture"; 0:50: "during rewind, lyrics on billboards and highway signs").
// The D1 gantry signs are cut into the block: an engraved face (tools/v5/signs/woodpanel.js, like the V2f SIRENS panel)
// under woodcut capitals in paper, each line in its own projective sub-quad of the tracked panel. They, and a
// rewind-only lettering of the D2 billboard, are also drawn inside the R3 rewind comp (B.js), and only there: C2 and
// later replays stay as before. docs/revisions/v5/signs.md. The panels are re-tracked per source frame
// (tools/v5/signs/track_d1.py; the v3 right-panel track sheared from ~0.6 s) and held per frame like the plate.
// v4: two `pin` style 'sign' layers (noRewind) on tracks.D1_signL ("LAKE SHORE DR\nI'm speeding down Lake Shore") and
// tracks.D1_signR ("SOUTH").
const PANEL = 'tools/v5/signs/woodpanel.js';
const REWIND_RUN = t => t >= 48.42 && t < 56.54;
const FWD_OR_RW = (lt, env) => (!env.rewinding || REWIND_RUN(env.frameT) ? 1 : 0);   // own shot + the rewind run
const RW_ONLY = (lt, env) => (env.rewinding && REWIND_RUN(env.frameT) ? 1 : 0);      // only replayed in the rewind run
const D1_SIGNS = (() => {
  const L = signTracks.D1_signL, R = signTracks.D1_signR, FACE = [0.035, 0.06, 0.965, 0.94];
  const pin = (keys, r) => stepKeys(subQuad(keys, r));
  const wc = (text, keys, r, box, extra = {}) => ({ type: 'canvas', module: WOODCUT, opacity: FWD_OR_RW,
    params: { text, at: -1, color: PAPER, box, pad: 4, hatch: 0.34, flecks: 10, corners: pin(keys, r), ...extra } });
  return [
    // left: the route name large, the lyric small on a band left solid (no gouges behind small letters)
    { type: 'canvas', module: PANEL, opacity: FWD_OR_RW, params: { corners: pin(L, FACE), box: [480, 255], plain: [[0.6, 1]], seed: 1 } },
    wc('LAKE SHORE DR', L, [0.07, 0.12, 0.93, 0.56], [600, 165]),
    wc("I'M SPEEDING DOWN LAKE SHORE", L, [0.08, 0.63, 0.92, 0.88], [700, 110], { hatch: 0, flecks: 0, space: 0.3 }),
    { type: 'canvas', module: PANEL, opacity: FWD_OR_RW, params: { corners: pin(R, FACE), box: [480, 240], seed: 2 } },
    wc('SOUTH', R, [0.12, 0.18, 0.88, 0.82], [500, 200]),
  ];
})();
const LETTERBOX = { type: 'letterbox', aspect: 2.39, amount: 1 };
const lower = (extra = {}) => ({ type: 'canvas', module: 'lowerthird', stage: 'post',
  params: { color: PAPER, size: 50, y: 1022, halo: 0, ...extra } });

export default ({ T }) => ({
  section: 'A',
  fx: [{ type: 'grain', amount: 0.035, seed: 'twos' }],
  shots: [
    // ---------------------------------------------------------------- cold open: the hook
    { id: 'C1', start: 0.0, end: 1.9, background: PAPER,
      layers: [
        vid('C1', { kenBurns: { from: { scale: 1.0 }, to: { scale: 1.05 }, ease: 'linear' } }),
        { type: 'solid', stage: 'post', color: PAPER, rect: [36, 40, 380, 54], opacity: 0.92, fadeIn: 0.25, start: 0.4 },
        { type: 'canvas', module: 'hud', stage: 'post', fadeIn: 0.25, start: 0.4,
          params: { mode: 'iteration', value: 4095, side: 'left', color: INK, size: 24 } },   // v5 counters (docs/revisions/v5/counters.md): 4095 dies mid-air
      ] },
    // ---------------------------------------------------------------- intro: title over the lake
    { id: 'C3', start: 7.24, end: 10.82, background: INK,
      layers: [
        vid('C3'),
        { type: 'canvas', module: 'title', stage: 'post',
          params: { color: PAPER, size: 210, y: 470, arrive: { at: 0, every: 0 }, flip: { at: 0.55, dur: 0.45, stagger: 0.09 }, subtitle: 'jade wang', subtitleSize: 92, subtitleDy: 126, subtitleTracking: 10, subtitleHalo: 0.85 } },   // v4 (Jade 0:09): the name was 38 px and lost in the shoreline lights
      ], fx: [LETTERBOX] },
    { id: 'C4', start: 10.82, end: 12.6, background: INK,
      layers: [
        // hold on her, then push 2.6x onto the sticky note (centre ~(1326, 850)) so DEFENSE 9AM reads: the stakes of the hook
        vid('C4', C4_PUSH),
        { type: 'canvas', module: 'pencil', noRewind: true, ...C4_PUSH, params: { text: 'DEFENSE\n9AM', at: 0.75, cps: 14, size: 46, corners: tracks.C4_note, color: '#1a1815', point: false, grain: 0.2 } },
      ], fx: [LETTERBOX] },
    // ---------------------------------------------------------------- verse 1: the cutscene
    { id: 'S1', start: 12.6, end: 16.14, background: INK,
      layers: [
        // the towers and the Bean plane, pre-rendered with these same transforms by tools/v4B/bean/bg.py (antialiased and
        // given a slight motion blur; drawn here from the 5504 px plates they crawled). Frame k = song frame 303 + k.
        // Unfiltered fallback: { type: 'image', src: 'media/sing/plates/plate_wide_v4_far.jpg', ...BEAN.far } under
        // { type: 'image', src: 'media/sing/plates/plate_wide_v4_bean.png', ...BEAN.beanPlate }, both fit 'cover', end 1.4
        // v5 (Jade 0:13: "make that rooftop staircase an actual impossible staircase"): the wide plane and the take carry a
        // Penrose stair on the near rooftop in place of the square stairwell (docs/revisions/v5/stairs.md). The take has
        // the plate baked in, so the stair is a still overlay riding the take's own transform and fade-in (she never
        // comes near it; her matte is unchanged). v4: S1_wide src 'media/shots/S1_wide/bg_1080/', no S1_stairs layer.
        // v5 round 2 (Jade: "copy the one from later in the same video ... inside the clock at 3:13"): the stair is the F6b
        // clock stair lifted off its plate (tools/v5/stairs2/comp.py). Round 1: 'bg_1080_stairs/', 'overlay_S1.png'.
        { id: 'S1_wide', type: 'video', src: 'media/shots/S1_wide/bg_1080_stairs_clock/', in: -0.024, rate: 1, fit: 'cover', end: 1.4 },
        { id: 'S1_take', type: 'video', src: S1_SRC, in: S1_IN, rate: 1, fit: 'cover', opacity: BEAN.takeIn, ...BEAN.bean },
        { id: 'S1_stairs', type: 'image', src: 'media/sing/plates/stairs_v5/overlay_S1_clock.png', fit: 'cover', opacity: BEAN.takeIn, ...BEAN.bean },
        // her again by matte, so the comps that replay S1 (C2, R4) show her in the wide part too
        { id: 'S1_her', type: 'video', src: S1_SRC, in: S1_IN, rate: 1, fit: 'cover', matte: { src: S1_MATTE, mode: 'luma' }, ...BEAN.her },
      ] },
    // cutaway (bar 10): the Bean's reflection of Lake Shore Drive, headlights streaming (engraved Seedance take)
    // v3 (Jade): every word of V1-1 is sung by 17.43 and she only holds the note after, so no return to her: the
    // reflection holds two bars and the road follows on "I'm speeding down" (v2: S1x to 17.88, S1b 17.88-19.64 on her,
    // S2 pushing from her face into the headlights)
    { id: 'S1x', start: 16.14, end: 19.64, background: INK,
      layers: [{ id: 'S1x_plate', type: 'video', src: S('S1x', 'take_1_engraved.mp4'), in: 0.2, rate: 1, fit: 'cover', scale: 1.04 }] },
    { id: 'S2', start: 19.64, end: 21.38, background: INK,
      // the reflection becomes the world: the engraved road from above, bent by the convex lens and relaxing flat
      layers: [vid('S2')] },
    { id: 'D1', start: 21.38, end: 23.16, background: INK,
      layers: [
        vid('D1'),
        ...D1_SIGNS,   // v5: woodcut signs, also in the R3 rewind
        lower({ text: 'I dreamt', sync: 'lyric' }),
      ], fx: [LETTERBOX] },
    // v3: the rooftop bulb billboard IS the lyric (it read HILBERT / VACANCY in v2). Each panel is dark until its word
    // is sung, then flickers on like a lamp. One beat longer (to 25.34) so "chasing" (24.78) can be read.
    { id: 'D2', start: 23.16, end: 25.34, background: INK,
      layers: [
        vid('D2'),
        // v9 round 3: the billboard is seen IN her door mirror; the lettering is pinned to the mirror image of each panel
        // (tracks from the scene's rig) with its corners swapped so it reads forward (Jade's plate cheat, applied to the lyric)
        { type: 'canvas', module: WOODCUT, noRewind: true, params: { text: 'A SHADOW', sync: 'lyric', reveal: 'bulb', unlit: 0.82, color: INK, flecks: 0, hatch: 0.3, box: [460, 96], pad: 6, corners: D2_BILL_TOP } },
        { type: 'canvas', module: WOODCUT, noRewind: true, params: { text: 'CHASING', sync: 'lyric', reveal: 'bulb', unlit: 0.82, color: INK, flecks: 0, hatch: 0.3, box: [460, 96], pad: 6, corners: D2_BILL_BOT } },
        // whatever is in front of the billboard (lamp poles, the glass's edge, the A-pillar) is re-drawn over the lettering:
        // the same clip through the inverse of the scene's billboard-visibility mask
        vid('D2', { id: 'D2_occluder', matte: { src: S('D23', 'r7_billmask_frames/'), mode: 'lumaInv' } }),
        // v5-signs: drawn only when R3 replays this shot (51.5-52.0): the whole of "a shadow chasing" lit on the upper
        // panel, the lower panel switched off (the REWIND title sits on it). Forward D2 is unchanged.
        // (round 3: after the occluder, which hid them in the replay)
        { type: 'canvas', module: WOODCUT, opacity: RW_ONLY, params: { text: 'A SHADOW\nCHASING', at: -1, color: INK, flecks: 0, hatch: 0.3, box: [460, 96], pad: 4, corners: D2_BILL_TOP } },
        { type: 'canvas', module: PANEL, opacity: RW_ONLY, params: { corners: D2_BILL_BOT, box: [460, 96], lines: 16, cut: 0.14, rule: 0, opacity: 0.9, seed: 3 } },
      ], fx: [LETTERBOX] },
    { id: 'D3', start: 25.34, end: 28.4, background: INK,
      layers: [
        vid('D3'),
        // the billboard stays lit in the glass (whole line, as D2 ends) until the sedan drives in front of it
        { type: 'canvas', module: WOODCUT, noRewind: true, params: { text: 'A SHADOW', at: -1, color: INK, flecks: 0, hatch: 0.3, box: [460, 96], pad: 6, corners: D3_BILL_TOP } },
        { type: 'canvas', module: WOODCUT, noRewind: true, params: { text: 'CHASING', at: -1, color: INK, flecks: 0, hatch: 0.3, box: [460, 96], pad: 6, corners: D3_BILL_BOT } },
        // v4 (Jade, 0:26): the sedan's front plate reads TVA 1729. v9 round 3: seen in her door mirror, pinned to the
        // mirror image of the plate, corners swapped so it reads FORWARD (Jade: legible, though a real mirror reverses it)
        { type: 'canvas', module: 'tools/v4B/plate/plate.js', noRewind: true, params: { text: 'TVA 1729', corners: D3_PLATE_R3, grow: 1.0, aspect: null, dim: 0.12, light: 0.8 } },
        // round 4: the occluder re-draws the clip wherever the mask is black, so the lettering AND the plate only show
        // where they are really seen (inside the glass; the sedan slides into it during the zoom)
        vid('D3', { id: 'D3_occluder', matte: { src: S('D23', 'r7_billmask_frames/'), mode: 'lumaInv' } }),
        // etch on the glass itself, two lines in the top-left sky of the glass (round 5; round 4 ran along the bottom edge)
        { type: 'canvas', module: 'etch', noRewind: true, x: 2, y: 2, opacity: 0.85, params: { text: "me I couldn't\nplace", sync: 'lyric', size: 60, padding: 4, corners: D3_ETCH_R3, color: INK } },
        { type: 'canvas', module: 'etch', noRewind: true, params: { text: "me I couldn't\nplace", sync: 'lyric', size: 60, padding: 4, corners: D3_ETCH_R3, color: '#fbf8f1' } },
      ], fx: [LETTERBOX] },
    // v3 restage: three beats on the shoulder, two on the men, four on the shades (cuts on beats 29.74, 30.60, 32.36)
    { id: 'D4', start: 28.4, end: 29.74, background: INK,
      layers: [vid('D4'),
        // v3 (Jade): she stays in colour in the driver's seat. The engrave matte missed her (small, behind the windshield),
        // so the raw take is laid back inside a static soft window round her (she doesn't move: centroid within 3 px)
        { id: 'D4_jade', type: 'video', src: S('D4', 'take_2.mp4'), in: 0.9, rate: 1, fit: 'cover', keepColor: true, grade: { saturation: 1.35 },
          matte: { src: S('D4', 'v3_colour_mask.mp4'), mode: 'luma' } },
        lower({ text: 'I pulled over', sync: 'lyric' })], fx: [LETTERBOX] },
    { id: 'D5', start: 29.74, end: 30.6, background: INK,
      layers: [vid('D5', { kenBurns: { from: { scale: 1.0, y: 40 }, to: { scale: 1.12, y: 110 }, ease: 'linear' } })], fx: [LETTERBOX] },
    // the shades fill the frame; "men in shades" / "and suits" are cut into the lenses, white line on black, word-timed
    { id: 'D5cu', start: 30.6, end: 32.36, background: INK,
      layers: [
        vid('D5cu', D5_BOB),
        { type: 'canvas', module: WOODCUT, noRewind: true, blend: 'screen', ...D5_BOB, params: { text: 'MEN IN\nSHADES', times: [0, 0.21, 0.28], box: [560, 400], corners: tracks.D5_cuL } },
        { type: 'canvas', module: WOODCUT, noRewind: true, blend: 'screen', ...D5_BOB, params: { text: 'AND\nSUITS', times: [0.96, 1.15], box: [560, 400], corners: tracks.D5_cuR } },
      ], fx: [LETTERBOX] },
    { id: 'D6', start: 32.36, end: 33.66, background: INK,
      layers: [vid('D6')], fx: [LETTERBOX] },
    { id: 'D7', start: 33.66, end: 36.3, background: INK,
      layers: [
        // The take is "she puts the card away", played backward: she reaches into her jacket ("I reach for my ID"),
        // draws the card out and holds it up to the window ("to show them"), landing on the keyframe. The card's
        // photo and redaction bars are drawn into the plate: no engine text on it.
        vid('D7', { srcTime: D7_SRC }),
      ], fx: [LETTERBOX] },
    { id: 'D8', start: 36.3, end: 37.96, background: INK,
      layers: [
        vid('D8'),
        // residue shimmering off the card as the needle slams (card centre ~(680, 500) in this plate); `at` is shot-local
        { type: 'canvas', module: 'motes', keepColor: true, params: { at: 0.48, x: 680, y: 440, count: 60, speed: 700, drag: 2.0, gravity: -110, size: 10, life: 1.3, ring: false, shape: 'square', spread: 0.3, angle: -90 } },
      ], fx: [LETTERBOX] },
    // ---------------------------------------------------------------- pre-drop: game over
    { id: 'P1', start: 37.96, end: 38.9, background: INK, layers: [vid('P1')], fx: [LETTERBOX] },
    { id: 'P2', start: 38.9, end: 39.68, background: INK,
      // v3: framed lower with a gentler push, so the two crossed pencils (erasers at the plate's top edge) stay inside
      // the letterbox; the plate's own top edge stays behind the bar
      layers: [vid('P2', { kenBurns: { from: { scale: 1.0, y: 60 }, to: { scale: 1.1, y: 100 } } })], fx: [LETTERBOX] },   // v9: v8 was 1.02/130 -> 1.07/148
    // v3 (Jade, 0:39): the gun pointed into the car put her head above the roof line, so no gun shot: back to the
    // agent, his hand at the holster inside his jacket, pushing in on it, then the hit (P4). v2: P3 take_1, in 0.4.
    { id: 'P1b', start: 39.68, end: 40.24, background: INK,
      layers: [vid('P1', { in: 0.3 + (39.68 - 37.96), kenBurns: { from: { scale: 1.3, x: -280, y: -40 }, to: { scale: 1.6, x: -560, y: -60 }, ease: 'in' } })],
      fx: [LETTERBOX] },
    { id: 'P4', start: 40.24, end: 40.65, background: INK,
      layers: [
        // v3 (Jade, 0:39: "just cut to the colorful pixel burst"): no gun-flash still (v2: kf_flash1.png for 3 frames);
        // the torso's first frame held under the shot's white hit flash instead, so P4's clip timing and P5 don't move
        { ...vid('P4'), id: 'P4_hold', end: 0.125, freeze: 0 },
        { ...vid('P4'), start: 0.125 },
        { type: 'canvas', module: 'motes', keepColor: true, params: { at: 0.13, x: 640, y: 620, count: 140 } },   // shot-local: the hit at 40.37 (B.js P5 continues this burst)
        { type: 'canvas', module: 'whisper', stage: 'post', params: { text: 'shot', sync: 'lyric', x: 1640, y: 990, color: PAPER } },
      ], fx: [{ type: 'flash', at: 0, dur: 0.12, amount: 0.6, color: PAPER }, { type: 'shake', amp: 8, freq: 14, decay: 0.3 }] },
  ],
  overlays: [
    // v3: V1-1 lives in the world, not in a lower third, and no word is shown in more than one shot (Jade). S1: "THE
    // NIGHT BEFORE" cut into the Bean's mirror on arcs just inside its rim (white-line woodcut capitals,
    // render/timeline/_arc_lyric.js), one word per sung onset, behind her (her matte is laid back over it). S1x: "MY
    // DISSERTATION DEFENSE" (no comma, Jade v4) on the plaza paving of the reflection. Layer times are local to 12.60: S1 0-3.54, S1x 3.54-7.04.
    { id: 'A_S1_lyric', start: 12.6, end: 19.64, layers: (() => {
      const ARC = 'render/timeline/_arc_lyric.js', HER = { src: S1_MATTE, mode: 'luma' };   // v6: S1_MATTE = 'media/sing/S1/v6_sync_1080_matte/'; v5c +0.90: 'media/sing/S1/v5c_sync_1080_l090_open_matte/' (-> v5c_sync_1080_l090_matte/); v5c: S1_MATTE = 'media/sing/S1/v5c_sync_1080_matte/'; v5: 'media/sing/S1/v5_sync_1080_l061_open_matte/' (-> v5_sync_1080_l061_matte/); v4 A: 'media/sing/S1/v4_sync_1080_matte/'
      const arc = (text, times, r, at) => ({ text, times, cx: 965, cy: 981, r, ...at, size: 88, style: 'woodcut' });
      const LEFT = [arc('THE NIGHT', ['word:the@13', 'word:night@13'], 1014, { to: -31 }), arc('BEFORE', ['word:before@13'], 930, { to: -31 })];
      // S1x: the plate drifts left about 38 px/s; the quad rides it (plate px before the layer's 1.04 scale)
      const PLAZA = (dx, dy) => [172 + dx, 640 + dy, 690 + dx, 626 + dy, 662 + dx, 960 + dy, 140 + dx, 986 + dy];
      return [
        // v4: the lyric rides the Bean plane and she rides her own (v3: both kenBurns: S1_PUSH(1.0, 1.04))
        ...LEFT.map(params => ({ type: 'canvas', module: ARC, stage: 'pre', noRewind: true, start: 0, end: 3.54, ...BEAN.bean, params })),
        { type: 'video', stage: 'pre', noRewind: true, start: 0, end: 3.54, src: S1_SRC, in: S1_IN, rate: 1, fit: 'cover', ...BEAN.her, matte: HER },
        { type: 'canvas', module: 'pin', stage: 'pre', noRewind: true, start: 3.54, end: 7.04, scale: 1.04, blend: 'multiply',
          params: { style: 'ground', font: 'slab', uppercase: true, text: 'MY\nDISSERTATION\nDEFENSE', times: ['word:my@16', 'word:dissertation@16', 'word:defense@17'],
            size: 92, color: INK, grain: 0.3, corners: [[0, PLAZA(8, -2)], [3.5, PLAZA(-125, 22)]] } },
      ];
    })() },
    { id: 'A_dialogue', start: 33.6, end: 37.96, layers: [
      // v3: a compact box at lower left, mostly in the letterbox bar, so it never covers the card or a hand in D7/D8
      // v7 (Jade, 0:37): text given explicitly so the line ends without the lyric sheet's trailing comma
      { type: 'canvas', module: 'dialogue', stage: 'post', params: { text: 'I reach for my ID to show them and I do', sync: 'lyric', rect: [80, 856, 960, 132], size: 46, speaker: 'JADE' } }] },
    { id: 'A_predrop_lyric', start: 37.96, end: 40.24, layers: [lower({ text: 'With no warning I get', sync: 'lyric' })] },
  ],
});
