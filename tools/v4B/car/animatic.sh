#!/usr/bin/env bash
# Animatic of the 1:30 car blockout for the V2f2 slot (90.14-92.79 s), one clip per camera option, with the song.
#   tools/v4B/car/animatic.sh [A B C]     -> media/reviews/v4/B/plans/car/animatic_<opt>.mp4 (960x540, the slot played 3 times)
# Software GL, no paid calls. Frames go to a temp dir and are removed.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../../.." && pwd)"; cd "$REPO"
FFMPEG="${FFMPEG:-$HOME/Documents/moongazing/.venv/bin/ffmpeg}"
OUTDIR="media/reviews/v4/B/plans/car"; N=64
for OPT in "${@:-A B C}"; do for O in $OPT; do
  TMP="$(mktemp -d -p "${FRAMES_TMP:-/tmp}")"; JOBS=()   # FRAMES_TMP, not TMPDIR: Chrome aborts when TMPDIR is a long path
  for i in $(seq 0 $((N - 1))); do JOBS+=("$O:$(awk -v i="$i" 'BEGIN{t=90.14+i/24; if(t>92.78)t=92.78; printf "%.4f", t}'):$(printf 'f_%03d' "$i")"); done
  OUT="$TMP" node tools/v4B/car/capture.mjs "${JOBS[@]}" > /dev/null
  "$FFMPEG" -y -loglevel error -framerate 24 -i "$TMP/f_%03d.png" -ss 90.14 -t 2.6667 -i analysis/cinematic/source.wav \
    -filter_complex "[0:v]loop=2:$N:0[v];[1:a]aloop=2:size=128000[a]" -map "[v]" -map "[a]" \
    -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart "$OUTDIR/animatic_$O.mp4"
  rm -rf "$TMP"; echo "wrote $OUTDIR/animatic_$O.mp4"
done; done
