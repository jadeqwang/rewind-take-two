// Section B effect prototypes on existing clips (helpers: _B_fx.js; modules: b_dashfx, b_tracemiss). Not part of the film.
//   node render/engine/render.mjs --timeline render/timeline/_B_fxdemo.js --range 96.30 98.60 --preview --encode     dash
//   node render/engine/render.mjs --timeline render/timeline/_B_fxdemo.js --range 104.22 105.98 --preview --encode   traceMiss
//   node render/engine/render.mjs --timeline render/timeline/_B_fxdemo.js --range 133.56 136.19 --preview --encode   doubling
import { dash, traceMiss, doubling, INK } from './_B_fx.js';

const S = 'media/shots/';

export default ({ T }) => {
  // ---- 1. dash on V2i4 (she leaps off the end of the L). Read off the frames: the arc tops out around source frame
  // 36-44 and is clearly dropping by 52; she is down and running by 86. Freeze on 52 (on the 97.62 beat), then the
  // clip plays at 3x through the dash (Celeste's "different gear") and lands on 86.
  const dStart = 96.30, dAt = 97.62, atL = Math.ceil(dAt * 24 - 1e-6) / 24 - dStart, landL = atL + (86 - 52) / 24 / 3;
  // This take's engrave matte also covers the streak the video model baked in behind her, so the demo uses a body-only
  // matte derived from it (media/shots/V2i4/take_1_bmatte/, made by the make_bmatte.py beside it).
  const v2i4 = { src: `${S}V2i4/take_1_engraved.mp4`, matte: { src: `${S}V2i4/take_1_bmatte/matte.mp4`, mode: 'luma' },
    in: 52 / 24 - atL, rate: [[0, 1, 'hold'], [atL, 3, 'hold'], [landL, 0.8]], fit: 'cover' };
  // the plate tracks her, so the world slides left (measured on the frames, px/s at each playback rate)
  const seg = [[0, [-530, -25]], [atL, [-1300, -180]], [landL, [-210, -100]]];
  const scroll = lt => { let x = 0, y = 0; for (let i = 0; i < seg.length; i++) { const a = seg[i][0], b = Math.min(lt, seg[i + 1]?.[0] ?? 1e9); if (b > a) { x += seg[i][1][0] * (b - a); y += seg[i][1][1] * (b - a); } } return [x, y]; };
  const d = dash({ clip: v2i4, at: dStart + atL, land: dStart + landL, shotStart: dStart, scroll, feet: { offset: [0, 25] } });
  const dashShot = { id: 'B_dash', start: dStart, end: 98.60, background: INK, fx: [...d.fx], layers: [
    { id: 'plate', type: 'video', ...v2i4, matte: undefined },
    ...d.under,
    { id: 'jade', type: 'video', ...v2i4, keepColor: true },
    ...d.over] };

  // ---- 2. traceMiss on V2k2 take 2 (side-scroll sprint, agents at frame left), film range, one shot per beat.
  // Plain plate here: the film's beat stutter jumps the ground, which world-space marks cannot ride.
  const mStart = 104.22, mEnd = 105.98;
  const v2k2 = { src: `${S}V2k2/take_2_engraved.mp4`, matte: { src: `${S}V2k2/take_2_matte/matte.mp4`, mode: 'luma' }, in: 1.2, rate: 1, fit: 'cover', scale: 1.06 };
  const m = traceMiss({ origin: [130, 540], size: 1.6, times: T.beats.filter(t => t > mStart + 0.34 && t < mEnd - 0.05), shotStart: mStart,
    target: { point: 'bottom', smooth: 3 }, scroll: [-2290, 0] });   // ground speed read off planted feet: ~90 px per source frame
  const missShot = { id: 'B_miss', start: mStart, end: mEnd, background: INK, layers: [
    { id: 'plate', type: 'video', ...v2k2, matte: undefined },
    ...m.under,
    { id: 'jade', type: 'video', ...v2k2, keepColor: true },
    ...m.over] };

  // ---- 3. doubling on the E4 stream clip (static camera, Jade-only matte): 1, 2, 4, 8, 16 on four beats from 134.00
  const gStart = 133.56, gEnd = 136.19;
  const e4 = { src: `${S}E4/take_e4_stream_2_engraved.mp4`, matte: { src: `${S}E4/take_e4_stream_2_jmatte/matte.mp4`, mode: 'luma' }, in: 0.45, rate: 1.1, fit: 'cover' };
  const g = doubling({ clip: e4, times: T.beats.filter(t => t > 133.99 && t < 135.33), shotStart: gStart, spacings: [18, 30, 42, 48] });
  const dblShot = { id: 'B_doubling', start: gStart, end: gEnd, background: INK, fx: [...g.fx], layers: [
    { id: 'plate', type: 'video', ...e4, matte: undefined },
    ...g.layers,
    { id: 'jade', type: 'video', ...e4, keepColor: true }] };

  return { name: 'B_fxdemo', audio: 'inputs/Rewind - cinematic edition (Remastered).mp3', range: [dStart, gEnd], background: '#000000',
    fx: [{ type: 'grain', amount: 0.035 }], shots: [dashShot, missShot, dblShot] };
};
