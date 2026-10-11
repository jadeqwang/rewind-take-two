# Rewind — acoustic lyric video

The acoustic recording is `inputs/Rewind_take_two.mp3`. The video uses the same committee illustration, dark lower gradient, lavender word highlighting, and gold next-line preview as the lyric video in `rewind-music-video`.

## Export

- `deliverables/Rewind_take_two_lyric_video.mp4`: 1920 × 1080, 30 fps, H.264 with stereo AAC audio at 320 kbps.
- `deliverables/Rewind_take_two_lyrics.ass`: word-highlighted subtitle source.
- `deliverables/Rewind_take_two_lyrics.srt`: line-timed subtitles.
- `deliverables/export_details.json`: source hashes and export verification.
- `deliverables/Rewind_take_two_karaoke_backing_vocals.mp4`: the same lyric video with the main lead vocal reduced, retaining backing vocals and vocal chops.
- `deliverables/Rewind_take_two_karaoke_backing_vocals.mp3`: the same karaoke mix as audio only.
- `deliverables/karaoke_export_details.json`: karaoke mixing decisions and verification.

The soundtrack is the full 216.760-second acoustic recording, with its original pitch, tempo, and audio level. Timing is measured from this performance rather than scaled from the previous recording. The lyric “I reach for my ID to show them … and I do” follows the MP3's embedded lyrics, which include “them.” The outro cues both sung repetitions of “Never stop.”

## Rebuild

Install `requirements-video.txt` in a Python environment. The current machine can reuse `/home/jade/Documents/rewind-music-video/.venv-karaoke/bin/python`; the alignment scripts also locate cached speech-model dependencies and the locally cached `faster-whisper-large-v3` model.

The verified timing is stored in `analysis/lyric-video/timing.json`. To rebuild from that timing:

```sh
python tools/lyric_video.py design
python tools/lyric_video.py render
python tools/lyric_video.py verify
```

The background in `assets/lyric-background.png` is copied directly from `rewind-music-video/analysis/karaoke/background.png`; its original illustration is `assets/character/anime/committee_v3_long_ponytails_ff.png` in that project.

## Karaoke with backing vocals

The karaoke mix first uses the existing Kim_Vocal_2 vocal reference, reusing the numpy STFT from `orbital-sunrise-video/tools/vocal_stem.py`. A karaoke-specific `UVR_MDXNET_KARA_2` pass estimates the lead and backing parts within that stem. The final verse uses `6_HP-Karaoke-UVR`, which better suppresses its centered lead while retaining stereo backing. The lead estimate is subtracted from the original mix only during the reviewed main lyric lines, using short fades. Outside those lines, samples are identical to the original source before video/MP3 audio encoding. This preserves the chopped “stops” and “wind” phrases, the instrumental breaks, and the later “Never stop” outro repetition as original audio.

Backing voices overlapping the lead are separated estimates, so some lead bleed remains. The mix prioritizes preserving backing parts. No gain change, pitch change, time stretch, or dynamic normalization is applied. The karaoke video's compressed graphics are identical to the original lyric video's video stream.

Model references: [UVR public models](https://github.com/TRvlvr/model_repo/releases/tag/all_public_uvr_models) and [audio-separator's maintainer discussion of background-vocal preservation](https://github.com/nomadkaraoke/python-audio-separator/discussions/82).

With the cached models and reference WAVs available, rebuild with:

```sh
python tools/karaoke_backing.py separate
python tools/karaoke_vr_check.py
python tools/karaoke_backing.py mix
python tools/karaoke_backing.py export
```

The VR pass uses the cached `audio-separator` package and a 20-second vocal excerpt (155–175 seconds). Model files, intermediate stems, and model caches stay under `analysis/karaoke/`.
