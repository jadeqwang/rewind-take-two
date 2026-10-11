"""Build render/engine/data/timing.stub.json: a stand-in timing map until analysis/cinematic/timing.json exists.

Snapshot of the analysis agent's intermediate files (read-only):
  analysis/cinematic/work/grid_beats.npy (gap-filled beat_this grid) or bt_mix_raw_beats.npy
  analysis/cinematic/work/bt_mix_raw_down.npy (downbeats)
  analysis/cinematic/work/whisper_voc.json (Whisper word stamps on the vocal stem; lines split at punctuation)
The engine prefers analysis/cinematic/timing.json automatically as soon as it exists; this file is only a fallback.

  ~/Documents/moongazing/.venv/bin/python render/engine/tools/make_stub_timing.py
"""
import json
import pathlib
import re

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
W = ROOT / 'analysis/cinematic/work'
OUT = ROOT / 'render/engine/data/timing.stub.json'

beats_f = W / 'grid_beats.npy' if (W / 'grid_beats.npy').exists() else W / 'bt_mix_raw_beats.npy'
beats = np.load(beats_f).astype(float)
downs = np.load(W / 'bt_mix_raw_down.npy').astype(float)
# snap downbeats onto the grid
downs = np.array(sorted({float(beats[np.argmin(np.abs(beats - d))]) for d in downs}))

words, lines = [], []
segs = json.load(open(W / 'whisper_voc.json'))
li = 0
for s in segs:
    cur = []
    for w in s.get('words', []):
        txt = w['w'].strip()
        if not txt:
            continue
        cur.append({'w': txt, 'start': round(w['start'], 3), 'end': round(w['end'], 3), 'line': li})
        if re.search(r'[.,!?;]$', txt):
            words += cur
            lines.append({'text': ' '.join(x['w'] for x in cur), 'start': cur[0]['start'], 'end': cur[-1]['end']})
            li += 1
            cur = []
    if cur:
        words += cur
        lines.append({'text': ' '.join(x['w'] for x in cur), 'start': cur[0]['start'], 'end': cur[-1]['end']})
        li += 1

# Whisper stretches a word's start back over a preceding gap (e.g. "The" 12.28-13.24); cap words at 0.9 s before their end
for w in words:
    if w['end'] - w['start'] > 0.9:
        w['start'] = round(w['end'] - 0.9, 3)
for l in lines:
    ws = [w for w in words if w['line'] == lines.index(l)]
    l['start'] = ws[0]['start']

d = {
    'stub': True,
    'note': 'ENGINE STUB built by render/engine/tools/make_stub_timing.py from analysis/cinematic/work snapshots; '
            'superseded automatically by analysis/cinematic/timing.json',
    'duration': 227.97,
    'bpm': round(float(60 / np.median(np.diff(beats))), 3),
    'beats_per_bar': 4,
    'first_bar': 1,
    'beats': [round(float(b), 4) for b in beats],
    'downbeats': [round(float(b), 4) for b in downs],
    'lines': lines,
    'words': words,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(d, indent=None, separators=(',', ':')))
print(f'{OUT}: {len(beats)} beats ({beats_f.name}), {len(downs)} downbeats, {len(lines)} lines, {len(words)} words, bpm {d["bpm"]}')
