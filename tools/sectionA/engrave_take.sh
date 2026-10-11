#!/bin/bash
# Engrave one Section A take: engrave_take.sh SHOT TAKE [extra engrave.py flags]
#   -> media/shots/SHOT/take_TAKE_engraved.mp4 (+ take_TAKE_matte/ unless --no-matte)
set -e
cd /home/jade/Documents/rewind-take-two
S=$1; N=$2; shift 2
D=media/shots/$S
SRC=$D/take_$N.mp4
[ -e "$SRC" ] || SRC=media/gen/A_$S/take_$N.mp4
EXTRA=()
case " $* " in *" --no-matte "*) ;; *) EXTRA=(--matte-out $D/take_${N}_matte);; esac
tools/engrave/.venv/bin/python tools/engrave/engrave.py "$SRC" $D/take_${N}_engraved.mp4 --out-height 1080 "${EXTRA[@]}" "$@" 2>&1 | grep -vE "^\s*$|it/s|frame " | tail -3
