"""Lead-only karaoke mix: retain backing voices and original vocal chops.

Reuses Orbital Sunrise's numpy STFT implementation and the Kim_Vocal_2 stem
already generated for this recording. UVR_MDXNET_KARA_2 splits that vocal stem
into estimated lead and retained backing. The lead estimate is subtracted only
over the reviewed main lyric cues, with short fades. All other samples stay
identical to the original source before the optional global headroom adjustment.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import math
import time

import numpy as np
import onnxruntime as ort
import soundfile as sf
import soxr

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'analysis/karaoke'
LYRICS = ROOT / 'analysis/lyric-video'
OUT = ROOT / 'deliverables'
MODEL = WORK / 'models/UVR_MDXNET_KARA_2.onnx'
MODEL_SHA = 'bf32e15105a09c0f7dddd2b67346146334d6f3ecb399ed7638eba2ab07cbf5f4'
SR = 48000


def separate():
    spec = importlib.util.spec_from_file_location('orbital_mdx',
             '/home/jade/Documents/orbital-sunrise-video/tools/vocal_stem.py')
    mdx = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mdx)
    mdx.NFFT, mdx.DIM_F, mdx.DIM_T = 5120, 2048, 256
    mdx.CHUNK = mdx.HOP * (mdx.DIM_T - 1)
    mdx.TRIM = mdx.NFFT // 2
    mdx.GEN = mdx.CHUNK - 2 * mdx.TRIM
    mdx.WIN = np.hanning(mdx.NFFT + 1)[:-1]
    assert hashlib.sha256(MODEL.read_bytes()).hexdigest() == MODEL_SHA
    vocals, sample_rate = sf.read(LYRICS / 'vocals.wav', dtype='float32', always_2d=True)
    assert sample_rate == SR
    mix = soxr.resample(vocals, SR, 44100).T.astype(np.float32)
    n = mix.shape[1]
    step = round(mdx.GEN * .75)
    offsets = list(range(0, n, step))
    padded = np.pad(mix, ((0, 0), (mdx.TRIM, mdx.CHUNK)))
    summed = np.zeros((2, n + mdx.GEN), np.float32)
    divider = np.zeros(n + mdx.GEN, np.float32)
    weight = np.maximum(np.hanning(mdx.GEN).astype(np.float32), .05)
    opts = ort.SessionOptions()
    opts.intra_op_num_threads = 4
    opts.inter_op_num_threads = 1
    opts.log_severity_level = 3
    sess = ort.InferenceSession(str(MODEL), sess_options=opts, providers=['CPUExecutionProvider'])
    name = sess.get_inputs()[0].name
    t0 = time.monotonic()
    print(f'Splitting lead / backing in {len(offsets)} overlapping windows (25% overlap, two-pass denoise).', flush=True)
    for index, offset in enumerate(offsets, 1):
        spectrum = mdx.stft(padded[:, offset:offset+mdx.CHUNK])[:, :mdx.DIM_F]
        spectrum[:, :3] = 0
        x = np.stack([spectrum[0].real, spectrum[0].imag,
                      spectrum[1].real, spectrum[1].imag])[None].astype(np.float32)
        y = (sess.run(None, {name: x})[0][0] - sess.run(None, {name: -x})[0][0]) / 2
        s = np.zeros((2, mdx.NFFT//2+1, mdx.DIM_T), np.complex64)
        s[0, :mdx.DIM_F] = y[0] + 1j*y[1]
        s[1, :mdx.DIM_F] = y[2] + 1j*y[3]
        backing = mdx.istft(s)[:, mdx.TRIM:-mdx.TRIM].astype(np.float32)
        summed[:, offset:offset+mdx.GEN] += backing*weight
        divider[offset:offset+mdx.GEN] += weight
        print(f'  {index}/{len(offsets)}: {min(n, offset+mdx.GEN)/44100:.1f}s; {time.monotonic()-t0:.1f}s elapsed', flush=True)
    backing44 = summed[:, :n]/divider[:n] * 1.065
    backing48 = soxr.resample(backing44.T, 44100, SR)[:len(vocals)]
    if len(backing48) < len(vocals):
        backing48 = np.pad(backing48, ((0, len(vocals)-len(backing48)), (0, 0)))
    lead = vocals - backing48
    sf.write(WORK / 'estimated_lead.wav', lead, SR, subtype='FLOAT')
    sf.write(WORK / 'estimated_backing.wav', backing48, SR, subtype='FLOAT')
    print('Lead/backing separation ready.', flush=True)


def mix():
    source, sr = sf.read(LYRICS / 'source.wav', dtype='float32', always_2d=True)
    lead, lead_sr = sf.read(WORK / 'estimated_lead.wav', dtype='float32', always_2d=True)
    backing, backing_sr = sf.read(WORK / 'estimated_backing.wav', dtype='float32', always_2d=True)
    vocals, vocal_sr = sf.read(LYRICS / 'vocals.wav', dtype='float32', always_2d=True)
    assert sr == lead_sr == backing_sr == vocal_sr == SR
    assert source.shape == lead.shape == backing.shape == vocals.shape
    vr_path = WORK/'vr/vr_backing.wav'
    if not vr_path.exists():
        raise RuntimeError('Run tools/karaoke_vr_check.py for the reviewed final-verse split first.')
    vr_backing, vr_sr = sf.read(vr_path, dtype='float32', always_2d=True)
    assert abs(len(vr_backing)/vr_sr-20.) < .01
    vr_backing = soxr.resample(vr_backing, vr_sr, SR)
    a, b = 155*SR, 175*SR
    # VR's final STFT frame can trim a few milliseconds at the excerpt tail;
    # this is after the last sung cue and therefore outside the subtraction gate.
    assert abs(len(vr_backing)-(b-a))/SR < .01
    vr_backing = vr_backing[:b-a]
    if len(vr_backing) < b-a:
        vr_backing = np.pad(vr_backing, ((0, b-a-len(vr_backing)), (0, 0)))
    # VR better suppresses the centered lead in this final verse while retaining
    # the stereo backing. Other passages keep the more permissive MDX split.
    backing[a:b] = vr_backing
    lead = vocals - backing
    timing = json.loads((LYRICS / 'timing.json').read_text())
    envelope = np.zeros(len(source), np.float32)
    fade = round(.035*SR)
    cue_ranges = []
    for line in timing['lines']:
        # The source lyric sheet has one "Never stop"; the later repetition is
        # treated as an outro backing/echo effect and retained in full.
        if line['index'] == 20:
            continue
        # Slight advance retains consonants in the lead estimate. End the fade
        # at the lyric's measured end, restoring following chops immediately.
        a = max(0, round((line['start']-.12)*SR))
        b = min(len(source), round(line['end']*SR))
        gate = np.ones(b-a, np.float32)
        f = min(fade, len(gate)//2)
        gate[:f] = np.linspace(0, 1, f)
        gate[-f:] = np.linspace(1, 0, f)
        envelope[a:b] = np.maximum(envelope[a:b], gate)
        cue_ranges.append(dict(index=line['index'], text=line['text'], start_s=a/SR, end_s=b/SR))
    removed = lead * envelope[:, None]
    karaoke = source - removed
    assert np.isfinite(karaoke).all()
    preserved = envelope == 0
    error = float(np.max(np.abs(karaoke[preserved] - source[preserved])))
    assert error == 0
    reconstruct = float(np.max(np.abs(vocals-lead-backing)))
    assert reconstruct < 1e-6
    peak = float(np.max(np.abs(karaoke)))
    gain_db = min(0., -1.5-20*math.log10(max(peak, 1e-12)))
    gain = 10**(gain_db/20)
    sf.write(WORK / 'karaoke_master.wav', karaoke*gain, SR, subtype='FLOAT')
    # Record the portions whose vocal effects and backing are exact source
    # samples, not a separated estimate.
    intervals = []
    mask = preserved.astype(np.int8)
    edges = np.diff(np.pad(mask, (1, 1)))
    for a, b in zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)):
        if (b-a)/SR > .1:
            intervals.append(dict(start_s=a/SR, end_s=b/SR))
    fulllead = envelope > .95
    ref = np.sum(vocals[fulllead].astype(np.float64)**2)
    retained = np.sum(backing[fulllead].astype(np.float64)**2)
    manifest = dict(source='inputs/Rewind_take_two.mp3', duration_s=len(source)/SR,
                    sample_rate=SR, source_sha256=hashlib.sha256((ROOT/'inputs/Rewind_take_two.mp3').read_bytes()).hexdigest(),
                    first_model='Kim_Vocal_2', first_model_role='all-vocal reference',
                    lead_backing_model='UVR_MDXNET_KARA_2', model_sha256=MODEL_SHA,
                    final_verse_model='6_HP-Karaoke-UVR',
                    final_verse_model_sha256=hashlib.sha256((WORK/'models/6_HP-Karaoke-UVR.pth').read_bytes()).hexdigest(),
                    final_verse_model_range_s=[155, 175],
                    model_compensation=1.065, overlap=.25, denoise=True,
                    subtraction='original source minus gated estimated lead',
                    lead_cue_ranges=cue_ranges, preserved_original_intervals=intervals,
                    retained_outro_repeat=dict(start_s=timing['lines'][20]['start'],
                                               end_s=timing['lines'][20]['end']),
                    preserved_original_max_error=error, vocal_reconstruction_max_error=reconstruct,
                    fixed_output_gain_db=gain_db, raw_sample_peak_db=20*math.log10(peak),
                    retained_backing_to_all_vocals_db=10*math.log10(retained/ref),
                    note='Backing vocals overlapping lead are model estimates; vocal chops and all material outside lead cues use original source samples.')
    (WORK / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Karaoke master ready: {len(source)/SR:.3f}s; gain {gain_db:.2f} dB; untouched sections error {error}.', flush=True)


def export():
    import sys
    sys.path.insert(0, str(ROOT/'tools'))
    import lyric_video as video
    manifest = json.loads((WORK/'manifest.json').read_text())
    target = OUT / 'Rewind_take_two_karaoke_backing_vocals.mp4'
    print('Muxing karaoke audio with the existing lyric graphics…', flush=True)
    video.run(['-i', OUT/'Rewind_take_two_lyric_video.mp4', '-i', WORK/'karaoke_master.wav',
               '-map', '0:v:0', '-map', '1:a:0', '-map_metadata', '-1',
               '-c:v', 'copy', '-c:a', 'aac', '-b:a', '320k', '-ar', SR,
               '-t', manifest['duration_s'], '-movflags', '+faststart',
               '-metadata', 'title=Rewind — Karaoke with Backing Vocals',
               '-metadata', 'artist=Jade Wang', target], 'encode_karaoke.log')
    video.run(['-i', WORK/'karaoke_master.wav', '-c:a', 'libmp3lame', '-b:a', '320k',
               '-metadata', 'title=Rewind — Karaoke with Backing Vocals',
               '-metadata', 'artist=Jade Wang', OUT/'Rewind_take_two_karaoke_backing_vocals.mp3'], 'encode_karaoke_mp3.log')
    video.run(['-v', 'error', '-xerror', '-i', target, '-f', 'null', '-'], 'karaoke_decode_check.log')
    exported = video.audio(target)
    master, _ = sf.read(WORK/'karaoke_master.wav', dtype='float32', always_2d=True)
    n = min(len(master), len(exported))
    corr = float(np.corrcoef(master[:n].ravel(), exported[:n].ravel())[0, 1])
    assert corr > .99
    assert abs(len(master)-len(exported))/SR < .05
    # Compare compressed video bitstreams to verify the graphics and timings
    # survived muxing byte for byte, without another video encode.
    def video_digest(path):
        return video.run(['-v', 'error', '-i', path, '-map', '0:v:0', '-c:v', 'copy',
                          '-f', 'hash', '-hash', 'sha256', '-']).stdout.decode().strip()
    original_video_hash = video_digest(OUT/'Rewind_take_two_lyric_video.mp4')
    assert video_digest(target) == original_video_hash
    manifest.update(video=str(target.relative_to(ROOT)),
                    audio_correlation_with_karaoke_master=corr,
                    full_decode_check='passed', video_bitstream_identical=True,
                    video_bitstream_hash=original_video_hash,
                    exported_audio_duration_s=len(exported)/SR,
                    video_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    (OUT/'karaoke_export_details.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(f'Export verified: {target}; audio correlation {corr:.6f}; video unchanged.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['separate', 'mix', 'export'])
    args = parser.parse_args()
    WORK.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    globals()[args.stage]()
