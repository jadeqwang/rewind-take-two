#!/usr/bin/env bash
# v9 #2 round 7: the mirror on its sail at the window's front lower corner, a DRAWN housing, the camera 23 cm forward.
# -> media/shots/D23/v9r7_engraved.mp4, r7_billmask_frames/, tools/v9/d23/d23_tracks_r7.js   (round 6: build.sh, untouched)
#   0. (paid, already done: gen.py r7_h, r7_n, r7_house_c, r7_half, r7_blink) the plate, the housing drawing, the eye edits
#   1. the plate: skin tint + the sail painted in the window corner (make_plate_r7.py), its Jade matte (BiRefNet via
#      engrave_still, clipped to her), key + 2x upscale (make_plate_r4.py); her blink / lip-press variants (r7_frames.py)
#   2. the drawn housing: keyed, registered to the housing camera, its glass outline (housing_r7.py)
#   3. scene (beauty), Jade's matte, the billboard/plate-visibility mask (scene_r7.js, headless Chrome)
#   4. section A engrave pass with that matte; corner tracks from rig_r7.js
set -euo pipefail
cd "$(dirname "$0")/../../.."
export FFMPEG=${FFMPEG:-$HOME/Documents/1-music-shipped/moongazing/.venv/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2}
EPY=tools/engrave/.venv/bin/python
D=media/shots/D23
if [ "${SKIP_PLATE:-0}" != 1 ]; then
  $EPY tools/v9/d23/make_plate_r7.py | tail -1
  if [ ! -f $D/plate_r7_base_matte.png ]; then
    T=$(mktemp -d); $EPY tools/engrave/engrave_still.py $D/plate_r7_base.png -o $T/eng.png --matte-out $T >/dev/null
    cp $T/plate_r7_base_matte.png $D/plate_r7_base_matte.png; rm -rf $T
    $EPY tools/v9/d23/make_plate_r7.py | tail -1
  fi
  $EPY tools/v9/d23/make_plate_r4.py $D/plate_r7_base.png $D/plate_r7_base_matte_fixed.png $D/r7_plate | tail -1
  $EPY tools/v9/d23/r7_frames.py | tail -1
  for v in half blink press50 press100; do $EPY tools/v9/d23/make_plate_r4.py $D/plate_r7_$v.png $D/plate_r7_base_matte_fixed.png $D/r7_plate_$v | tail -1; done
  $EPY tools/v9/d23/housing_r7.py | tail -1
fi
rm -rf $D/r7_src_frames $D/r7_matte_frames $D/r7_billmask_frames
(cd render/three && node tools/capture.mjs --scene ../../../tools/v9/d23/scene_r7 --from 0 --to 5.24 --jobs 2 --crf 12 --out ../../$D/r7_src.mp4 --keep | grep -E "captured")
(cd render/three && node tools/capture.mjs --scene ../../../tools/v9/d23/scene_r7 --p.pass matte --from 0 --to 5.24 --jobs 2 --out ../../$D/r7_matte.mp4 --keep | grep -E "captured")
(cd render/three && node tools/capture.mjs --scene ../../../tools/v9/d23/scene_r7 --p.pass billmask --from 0 --to 5.24 --jobs 2 --out ../../$D/r7_billmask.mp4 --keep | grep -E "captured")
rm -f $D/r7_billmask.mp4
$EPY tools/engrave/engrave.py $D/r7_src.mp4 $D/v9r7_engraved.mp4 --out-height 1080 \
  --fallback-angle 0 --fallback-weight 1.0 --matte-in $D/r7_matte_frames/ 2>&1 | tail -1
node tools/v9/d23/tracks_r7.mjs | tail -3
