"""Independent VR karaoke separation for lead leakage review."""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT/'analysis/karaoke'
sys.path.extend(str(p) for p in Path('/home/jade/.cache/uv/archive-v0').iterdir() if p.is_dir())
os.environ['NUMBA_CACHE_DIR'] = str(WORK/'numba-cache')
import imageio_ffmpeg
import numpy as np
import soundfile as sf
import torch
from audio_separator.separator import Separator
torch.set_num_threads(4)
torch.set_num_interop_threads(1)
bin_dir = WORK/'bin'
bin_dir.mkdir(exist_ok=True)
if not (bin_dir/'ffmpeg').exists():
    (bin_dir/'ffmpeg').symlink_to(imageio_ffmpeg.get_ffmpeg_exe())
os.environ['PATH'] = str(bin_dir)+os.pathsep+os.environ['PATH']
parser = argparse.ArgumentParser()
parser.add_argument('--full', action='store_true')
args = parser.parse_args()
out = WORK/'vr'
out.mkdir(exist_ok=True)
source = ROOT/'analysis/lyric-video/vocals.wav'
if not args.full:
    v, sr = sf.read(source, dtype='float32')
    source = WORK/'vr_check_vocals.wav'
    sf.write(source, v[round(155*sr):round(175*sr)], sr, subtype='FLOAT')
separator = Separator(model_file_dir=str(WORK/'models'), output_dir=str(out),
                      output_format='WAV', sample_rate=44100, use_soundfile=True,
                      normalization_threshold=1., amplification_threshold=0.,
                      vr_params=dict(batch_size=1, window_size=512, aggression=5,
                                     enable_tta=True, enable_post_process=False,
                                     post_process_threshold=.2, high_end_process=False))
separator.load_model(model_filename='6_HP-Karaoke-UVR.pth')
files = separator.separate(str(source), custom_output_names={'Vocals':'vr_lead', 'Instrumental':'vr_backing'})
print('VR output files:', files, flush=True)
