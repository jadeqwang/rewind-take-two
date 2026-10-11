#!/usr/bin/env bash
# Section F color pass: link take N from media/gen into media/shots/<SHOT>/ and run tools/engrave in "color world" mode
# (strength 0 + full bloom = the Seedance colour, upscaled to 1080p with the anime upscaler, plus Jade's matte).
# The style test showed that a partial engrave over the colored-pencil footage only adds gray blotches, so the colour
# world keeps the hatching nano-banana drew into it. F1 additionally gets a plain engraved twin (strength 1, no bloom).
#   tools/sectionF/colorpass.sh SHOT [TAKE] [--twin]
set -euo pipefail
ROOT=/home/jade/Documents/rewind-take-two
EPY=$ROOT/tools/engrave/.venv/bin/python
SHOT=$1; TAKE=${2:-1}; TWIN=${3:-}
SRC=$ROOT/media/gen/$SHOT/take_$TAKE.mp4
D=$ROOT/media/shots/$SHOT
mkdir -p "$D"
ln -f "$SRC" "$D/take_$TAKE.mp4"
if [ ! -s "$D/take_${TAKE}_engraved.mp4" ]; then
  $EPY $ROOT/tools/engrave/engrave.py "$D/take_$TAKE.mp4" "$D/take_${TAKE}_engraved.mp4" --out-height 1080 \
      --bloom $ROOT/media/shots/F_style/white_720.png --strength 0 --matte-out "$D/take_${TAKE}_matte" 2>&1 | tail -1
  rm -f "$D/take_${TAKE}_matte/"*.png      # keep matte.mp4 only (the PNG sequence is large)
fi
if [ "$TWIN" = "--twin" ] && [ ! -s "$D/take_${TAKE}_twin_engraved.mp4" ]; then
  $EPY $ROOT/tools/engrave/engrave.py "$D/take_$TAKE.mp4" "$D/take_${TAKE}_twin_engraved.mp4" --out-height 1080 \
      --ramp-in 0 2>&1 | tail -1
fi
