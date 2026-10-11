"""Independent transcription to locate verse and refrain boundaries."""
from pathlib import Path
import json
import os
import sys
import subprocess

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'analysis/lyric-video'
sys.path.extend(str(p) for p in Path('/home/jade/.cache/uv/archive-v0').iterdir() if p.is_dir())
os.environ['OMP_NUM_THREADS'] = '4'
os.environ['NUMBA_CACHE_DIR'] = str(WORK / 'numba-cache')
from faster_whisper import WhisperModel
import imageio_ffmpeg
import numpy as np
model_path = next(Path('/home/jade/.cache/huggingface/hub/models--Systran--faster-whisper-large-v3/snapshots').iterdir())
model = WhisperModel(str(model_path), device='cpu', compute_type='int8', cpu_threads=4)
decoded = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', str(ROOT / 'inputs/Rewind_take_two.mp3'),
                          '-map', '0:a:0', '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
audio = np.frombuffer(decoded, dtype=np.float32).copy()
segments, info = model.transcribe(audio, language='en',
                                  beam_size=3, word_timestamps=True, vad_filter=False,
                                  condition_on_previous_text=False,
                                  initial_prompt="Song lyrics: The night before my dissertation defense. I'm speeding down Lake Shore. Rewind. Sirens in my mirror, Reload. Never stop.")
result = []
for s in segments:
    print(f'{s.start:.2f}–{s.end:.2f} {s.text}', flush=True)
    result.append(dict(start=s.start, end=s.end, text=s.text,
                       words=[dict(w=w.word, start=w.start, end=w.end, probability=w.probability) for w in s.words]))
(WORK / 'transcription_check.json').write_text(json.dumps(result, indent=2) + '\n')
