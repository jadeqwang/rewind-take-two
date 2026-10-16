#!/usr/bin/env bash
# v9 round 3-5: D2+D3 three.js scene -> media/shots/D23/v9r6_engraved.mp4 + tools/v9/d23/d23_tracks_r5.js (tracks unchanged in round 6)
#   1. scene (beauty) and Jade's matte, 126 frames, headless Chrome (render/three/tools/capture.mjs)
#   2. section A engrave pass with that matte (Jade passes through in colour), flat areas engraved horizontally
#   3. the billboard-visibility mask (PNG frames, the engine's occlusion matte for the lyric)
#   4. corner tracks for the engine (billboard lyric, plate, glass etch) from the same rig
set -euo pipefail
cd "$(dirname "$0")/../../.."
export FFMPEG=${FFMPEG:-$HOME/Documents/1-music-shipped/moongazing/.venv/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2}
D=media/shots/D23
rm -rf $D/r6_src_frames $D/r6_matte_frames $D/r6_billmask_frames
(cd render/three && node tools/capture.mjs --scene ../../../tools/v9/d23/scene --from 0 --to 5.24 --jobs 2 --crf 12 --out ../../$D/r6_src.mp4 --keep | grep -E "wrote|captured")
(cd render/three && node tools/capture.mjs --scene ../../../tools/v9/d23/scene --p.pass matte --from 0 --to 5.24 --jobs 2 --out ../../$D/r6_matte.mp4 --keep | grep -E "wrote|captured")
# billboard-visibility mask (white = a billboard panel is what you see): the engine occludes the pinned lyric with it
(cd render/three && node tools/capture.mjs --scene ../../../tools/v9/d23/scene --p.pass billmask --from 0 --to 5.24 --jobs 2 --out ../../$D/r6_billmask.mp4 --keep | grep -E "captured")
rm -f $D/r6_billmask.mp4
tools/engrave/.venv/bin/python tools/engrave/engrave.py $D/r6_src.mp4 $D/v9r6_engraved.mp4 --out-height 1080 \
  --fallback-angle 0 --fallback-weight 1.0 --matte-in $D/r6_matte_frames/ 2>&1 | tail -1
node tools/v9/d23/tracks.mjs | tail -1
