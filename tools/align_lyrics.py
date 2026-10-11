"""Align the supplied acoustic performance using a locally cached Whisper model."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'analysis/lyric-video'
WORK.mkdir(parents=True, exist_ok=True)

# Reuse installed, cached packages without modifying the original project's environment.
sys.path.extend(str(p) for p in Path('/home/jade/.cache/uv/archive-v0').iterdir() if p.is_dir())
os.environ['NUMBA_CACHE_DIR'] = str(WORK / 'numba-cache')
os.environ['OMP_NUM_THREADS'] = '4'
import imageio_ffmpeg
import numpy as np
import stable_whisper
import torch

torch.set_num_threads(4)
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
reference = WORK / 'vocals.wav'
if not reference.exists():
    reference = ROOT / 'inputs/Rewind_take_two.mp3'
decoded = subprocess.run([ffmpeg, '-v', 'error', '-i', str(reference),
                          '-map', '0:a:0', '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'],
                         check=True, capture_output=True).stdout
audio = np.frombuffer(decoded, dtype=np.float32).copy()
lines = [s.strip() for s in (ROOT / 'inputs/Rewind lyrics.md').read_text().splitlines()
         if s.strip() and not s.startswith('#')]
# The MP3's embedded lyrics include the sung word 'them'.
lines[4] = 'I reach for my ID to show them … and I do,'
model_path = next(Path('/home/jade/.cache/huggingface/hub/models--Systran--faster-whisper-large-v3/snapshots').iterdir())
print(f'Acoustic duration: {len(audio) / 16000:.3f}s; aligning {len(lines)} lines', flush=True)
model = stable_whisper.load_faster_whisper(str(model_path), device='cpu', compute_type='int8', cpu_threads=4)
# Independent transcription located these sections. Constrain alignment to each
# sung passage so the long instrumental breaks cannot attract lyric words.
# The performance sings 'Never stop' twice in the outro.
lines.append('Never stop.')
passages = [(10.5, 28.5, 0, 3), (28.5, 44.5, 3, 6),
            (49.8, 52.5, 6, 7), (53.7, 56.2, 7, 8),
            (84.5, 101.2, 8, 11), (101.2, 117.0, 11, 14),
            (122.0, 125.0, 14, 15), (126.2, 128.5, 15, 16),
            (155.0, 175.0, 16, 19), (178.5, 182.0, 19, 20), (186.0, 189.0, 20, 21)]
aligned = []
raw = []
for a, b, first, last in passages:
    print(f'Aligning passage {a:.1f}–{b:.1f}s (lines {first}–{last-1})', flush=True)
    result = model.align(audio[round(a*16000):round(b*16000)], '\n'.join(lines[first:last]),
                         language='en', original_split=True, regroup=False,
                         suppress_silence=False, nonspeech_skip=None, verbose=True)
    assert len(result.segments) == last-first
    raw.append(dict(offset_s=a, result=result.to_dict()))
    for index, segment in enumerate(result.segments, first):
        aligned.append(dict(index=index, text=lines[index], start=round(segment.start+a, 3),
                            end=round(segment.end+a, 3),
                            words=[dict(w=w.word.strip(), start=round(w.start+a, 3),
                                        end=round(w.end+a, 3), line_idx=index) for w in segment.words]))
(WORK / 'alignment_refined.json').write_text(json.dumps(raw, indent=2, ensure_ascii=False) + '\n')
# Whisper can attach a long preceding pause to a short word. Trim those lead-ins
# against the isolated vocal envelope, retaining 40 ms for quiet consonants.
hop = 160
envelope = np.sqrt(np.mean(audio[:len(audio)//hop*hop].reshape(-1, hop)**2, axis=1))
envelope = np.convolve(envelope, np.ones(3)/3, mode='same')
adjustments = []
for line in aligned:
    for word in line['words']:
        if not any(c.isalpha() for c in word['w']) or word['w'].lower() == 'across':
            continue
        a, b = round(word['start']*100), round(word['end']*100)
        if b-a < 15:
            continue
        levels = envelope[a:b]
        active = np.flatnonzero(levels > np.max(levels)*.20)
        if not len(active):
            continue
        # Use the vocal cluster following any substantial intervening silence.
        gaps = np.flatnonzero(np.diff(active) > 40)
        first = active[gaps[-1]+1] if len(gaps) else active[0]
        newstart = max(word['start'], (a+first)/100-.04)
        if newstart-word['start'] > .12:
            adjustments.append(dict(line=line['index'], word=word['w'],
                                    old_start=word['start'], start=round(newstart, 3)))
            word['start'] = round(newstart, 3)
    line['start'] = line['words'][0]['start']

# Isolated one-word sung refrains have weak attention alignment. Use the
# independently transcribed onsets and ends, checked against the vocal waveform.
for i, a, b in [(6, 50.70, 51.64), (7, 54.12, 55.52),
                (14, 122.82, 124.06), (15, 126.74, 127.86)]:
    aligned[i]['start'], aligned[i]['end'] = a, b
    aligned[i]['words'][0]['start'], aligned[i]['words'][0]['end'] = a, b
# Reviewed on the vocal waveform: quiet function words following pauses can
# inherit a preceding sustained syllable or introductory choir in attention DTW.
for i, j, start in [(0, 0, 13.50), (0, 3, 16.68), (8, 0, 86.20), (16, 3, 161.64)]:
    old = aligned[i]['words'][j]['start']
    aligned[i]['words'][j]['start'] = start
    if j == 0:
        aligned[i]['start'] = start
    adjustments.append(dict(line=i, word=aligned[i]['words'][j]['w'], old_start=old,
                            start=start, method='vocal waveform review'))
(WORK / 'timing_adjustments.json').write_text(json.dumps(adjustments, indent=2) + '\n')
(WORK / 'timing.json').write_text(json.dumps(dict(duration_s=len(audio)/16000, lines=aligned),
                                            indent=2, ensure_ascii=False) + '\n')
for line in aligned:
    print(f"{line['index']:02}: {line['start']:.3f}–{line['end']:.3f} {line['text']}", flush=True)
