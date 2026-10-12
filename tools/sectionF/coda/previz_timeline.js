// SUPERSEDED by the built scene (tools/sectionF/edl.py PC1_door / PC2_lobby, docs/revisions/v5/build.md): PC1 now starts
// at 232.80, so this previz would overlap it. Kept for the record; do not run.
// v5-coda previz (docs/revisions/v5/coda.md): the film as it stands (render/timeline.js, which already carries the
// extended credits to 234.00) plus the proposed post-credits scene. Not part of the film until Jade signs it off.
//   node render/engine/render.mjs --timeline tools/sectionF/coda/previz_timeline.js --range 230 245.2 --preview --encode \
//     --force --audio media/reviews/v5/plans/coda/previz_audio.wav --out media/reviews/v5/plans/coda/coda_previz_540p.mp4
import film from '../../../render/timeline.js';

const DIR = 'media/reviews/v5/plans/coda';
export const PC = { black: 234.00, door: 234.70, lobby: 237.70, line: 240.10, end: 245.20 };

export default async function previz(ctx) {
  const tl = await film(ctx);
  const grain = { type: 'grain', amount: 0.03, seed: 'twos' };
  tl.shots.push(
    { id: 'PC0_black', start: PC.black, end: PC.door, layers: [{ type: 'solid', color: '#000000' }] },
    // PC1: Jade's POV at the door; the doorman's white glove opens it, the spring bell rings as it moves (235.75)
    { id: 'PC1_door', start: PC.door, end: PC.lobby, fx: [grain],
      layers: [{ id: 'plate', type: 'video', src: 'media/gen/v5_coda_door/take_1_dered.mp4', in: 0.4, rate: 1.0, fit: 'cover' }] },
    // PC2: the receptionist looks up from the ledger at the endless queue of Jades; the text box types the line
    { id: 'PC2_lobby', start: PC.lobby, end: PC.end, fx: [grain],
      layers: [
        { type: 'canvas', module: 'tools/sectionF/coda/hilbert_lobby.js', params: {
          plate: `${DIR}/lobby_empty_engraved.jpg`, sprites: `${DIR}/sprites`, vp: [960, 518], deskY: 853,
          front: { x: 1210, feet: 1311, h: 1090 }, lane: -340, step: 0.8, count: 600, jitter: 40, zig: 110, zigN: 10, weave: 380, weaveF: 0.42, ghostAlpha: 0.9,
          camScale: [[0, 2.2], [0.7, 2.2, 'inOutCubic'], [2.2, 1.0]], camX: [[0, 1010], [0.7, 1010, 'inOutCubic'], [2.2, 960]],
          camY: [[0, 835], [0.7, 835, 'inOutCubic'], [2.2, 540]] } },
        { type: 'canvas', module: 'dialogue', stage: 'post', start: PC.line - PC.lobby,
          params: { rect: [80, 856, 960, 132], size: 46, speaker: 'FRONT DESK', text: 'Of course we have space for you.', at: 0.2, cps: 16 } },
      ] },
  );
  tl.name = 'coda_previz';
  tl.range = [230, PC.end];
  return tl;
}
