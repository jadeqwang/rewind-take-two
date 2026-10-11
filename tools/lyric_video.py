"""Render and verify the acoustic lyric video with the original committee graphics."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'analysis/lyric-video'
OUT = ROOT / 'deliverables'
SOURCE = ROOT / 'inputs/Rewind_take_two.mp3'
BACKGROUND = ROOT / 'assets/lyric-background.png'
ASS = OUT / 'Rewind_take_two_lyrics.ass'
VIDEO = OUT / 'Rewind_take_two_lyric_video.mp4'
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def run(args, log=None):
    command = [FFMPEG, '-hide_banner', '-nostdin', '-y', *map(str, args)]
    if log:
        with open(WORK / log, 'w') as stream:
            subprocess.run(command, stdout=stream, stderr=stream, check=True)
        return None
    return subprocess.run(command, capture_output=True, check=True)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp(t, srt=False):
    scale = 1000 if srt else 100
    n = round(t * scale)
    hours, n = divmod(n, 3600 * scale)
    minutes, n = divmod(n, 60 * scale)
    seconds, fraction = divmod(n, scale)
    return (f'{hours:02}:{minutes:02}:{seconds:02},{fraction:03}' if srt else
            f'{hours}:{minutes:02}:{seconds:02}.{fraction:02}')


def design():
    timing = json.loads((WORK / 'timing.json').read_text())
    lines = timing['lines']
    duration = timing['duration_s']
    assert len(lines) == 21
    starts = [max(0, line['start'] - 1.4, lines[i - 1]['end'] if i else 0)
              for i, line in enumerate(lines)]
    # Match the original lyric video's typography, positions, and colors.
    rows = ['[Script Info]', 'Title: Rewind — acoustic lyrics', 'ScriptType: v4.00+',
            'PlayResX: 1920', 'PlayResY: 1080', 'WrapStyle: 2', 'ScaledBorderAndShadow: yes',
            '', '[V4+ Styles]',
            'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
            'Style: Lyrics,DejaVu Sans,62,&H00FFD0CF,&H00FFFFFF,&H00151015,&H90000000,-1,0,0,0,100,100,0,0,1,2.5,1,5,100,100,0,1',
            'Style: Next,DejaVu Sans,32,&H005FC5F4,&H005FC5F4,&H00151015,&H90000000,0,0,0,0,100,100,0,0,1,1.5,0,5,100,100,0,1',
            'Style: Label,DejaVu Sans,25,&H00D4D4D4,&H00D4D4D4,&H00151015,&H90000000,0,0,0,0,100,100,2,0,1,1,0,5,100,100,0,1',
            '', '[Events]', 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']

    def event(a, b, style, text):
        if b > a:
            rows.append(f'Dialogue: 0,{stamp(a)},{stamp(b)},{style},,0,0,0,,{text}')

    event(0, starts[0] - .05, 'Lyrics', r'{\pos(960,932)\1c&HFFFFFF&\fad(400,200)}REWIND')
    event(0, starts[0] - .05, 'Label', r'{\pos(960,1000)\fad(400,200)}JADE WANG')
    audit = []
    for i, line in enumerate(lines):
        end = min(line['end'] + .8, starts[i + 1] if i + 1 < len(lines) else duration)
        cursor = round(starts[i] * 100)
        text = ''
        for j, word in enumerate(line['words']):
            a = max(cursor, round(word['start'] * 100))
            b = max(a, round(word['end'] * 100))
            text += f'{{\\k{a - cursor}}}' + ('\u200b' if j == 0 else ' ')
            text += f'{{\\kf{b - a}}}' + word['w']
            cursor = b
        size = 62
        while ImageFont.truetype(FONT, size).getlength(line['text']) > 1700:
            size -= 1
        event(starts[i], end, 'Lyrics', f'{{\\pos(960,934)\\fs{size}}}' + text)
        if i + 1 < len(lines):
            event(starts[i], end, 'Next', r'{\pos(960,1009)}' + lines[i + 1]['text'])
        nextstart = starts[i + 1] if i + 1 < len(lines) else duration
        if nextstart - end > 3:
            event(end + .05, nextstart - .05, 'Label', r'{\pos(960,1000)}INSTRUMENTAL')
        audit.append(dict(**line, display_start=starts[i], display_end=end, font_size=size))
    ASS.write_text('\n'.join(rows) + '\n')
    (OUT / 'Rewind_take_two_lyrics.srt').write_text('\n\n'.join(
        f"{i+1}\n{stamp(l['start'], True)} --> {stamp(l['end'], True)}\n{l['text']}"
        for i, l in enumerate(lines)) + '\n')
    (WORK / 'lyric_cues.json').write_text(json.dumps(audit, indent=2, ensure_ascii=False) + '\n')
    print('Prepared acoustic word highlighting and subtitles.', flush=True)


def render():
    duration = json.loads((WORK / 'timing.json').read_text())['duration_s']
    print(f'Exporting 1920×1080 / 30 fps, full acoustic audio ({duration:.3f}s)…', flush=True)
    run(['-loop', '1', '-framerate', '30', '-i', BACKGROUND, '-i', SOURCE,
         '-map', '0:v:0', '-map', '1:a:0', '-map_metadata', '-1',
         '-vf', f"ass='{ASS}'", '-t', duration,
         '-c:v', 'libx264', '-preset', 'medium', '-tune', 'stillimage', '-crf', '18',
         '-pix_fmt', 'yuv420p', '-threads', '6', '-c:a', 'aac', '-b:a', '320k', '-ar', '48000',
         '-metadata', 'title=Rewind — Acoustic Lyric Video', '-metadata', 'artist=Jade Wang',
         '-movflags', '+faststart', VIDEO], 'encode.log')
    print(f'Exported {VIDEO}', flush=True)


def audio(path):
    raw = run(['-v', 'error', '-i', path, '-map', '0:a:0', '-ac', '2', '-ar', '48000',
               '-f', 'f32le', '-']).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)


def verify():
    run(['-v', 'error', '-xerror', '-i', VIDEO, '-f', 'null', '-'], 'decode_check.log')
    source, exported = audio(SOURCE), audio(VIDEO)
    n = min(len(source), len(exported))
    corr = float(np.corrcoef(source[:n].ravel(), exported[:n].ravel())[0, 1])
    gain = float(np.sum(source[:n].astype(np.float64) * exported[:n]) /
                 np.sum(source[:n].astype(np.float64) ** 2))
    assert corr > .99, f'Audio correlation too low: {corr}'
    assert abs(20 * math.log10(gain)) < .1, f'Unexpected audio level change: {gain}'
    assert abs(len(source) - len(exported)) / 48000 < .05
    timing = json.loads((WORK / 'timing.json').read_text())
    for i, line in enumerate(timing['lines']):
        assert 0 <= line['start'] < line['end'] <= timing['duration_s']
        if i:
            assert line['start'] >= timing['lines'][i-1]['end']
    shots = [(.5, 'title'), (timing['lines'][0]['start'] + .8, 'verse1'),
             (timing['lines'][4]['words'][7]['start'] + .1, 'them'),
             (timing['lines'][6]['start'] + .4, 'rewind1'),
             (timing['lines'][8]['start'] + .8, 'verse2'),
             (timing['lines'][16]['start'] + .8, 'verse3'),
             (timing['lines'][19]['start'] + .3, 'outro'),
             (timing['duration_s'] - .5, 'end')]
    thumbs = []
    for t, name in shots:
        path = WORK / f'preview_{name}.jpg'
        run(['-ss', t, '-i', VIDEO, '-frames:v', '1', '-q:v', '2', path])
        thumb = Image.open(path).resize((640, 360))
        ImageDraw.Draw(thumb).text((12, 12), f'{name} / {t:.2f}s',
                                  font=ImageFont.truetype(FONT, 18), fill='white', stroke_width=2, stroke_fill='black')
        thumbs.append(thumb)
    sheet = Image.new('RGB', (1280, 360 * 4))
    for i, thumb in enumerate(thumbs):
        sheet.paste(thumb, (i % 2 * 640, i // 2 * 360))
    sheet.save(WORK / 'contact_sheet.jpg')
    details = dict(source=str(SOURCE.relative_to(ROOT)), source_sha256=digest(SOURCE),
                   background_sha256=digest(BACKGROUND), video_sha256=digest(VIDEO),
                   duration_s=len(source)/48000, resolution=[1920, 1080], fps=30,
                   video_codec='H.264', audio_codec='AAC', audio_bitrate=320000,
                   sample_rate=48000, audio_gain_db=0, audio_correlation=corr,
                   measured_gain_db=20*math.log10(gain), decoded_video_audio_s=len(exported)/48000,
                   full_decode_check='passed', lyric_lines=len(timing['lines']),
                   graphics_source='rewind-music-video/analysis/karaoke/background.png')
    (OUT / 'export_details.json').write_text(json.dumps(details, indent=2) + '\n')
    print(json.dumps(details, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['design', 'render', 'verify'])
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    globals()[args.stage]()
