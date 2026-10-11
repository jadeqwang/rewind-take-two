"""Use the original project's cached vocal model solely for lyric timing review."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = Path('/home/jade/Documents/rewind-music-video')
spec = importlib.util.spec_from_file_location('reference_karaoke', ORIGINAL / 'tools/karaoke.py')
reference = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reference)
reference.WORK = ROOT / 'analysis/lyric-video'
reference.SOURCE = ROOT / 'inputs/Rewind_take_two.mp3'
reference.finalize = lambda: print('Vocal timing reference ready; export still uses the original MP3.', flush=True)
reference.separate()
