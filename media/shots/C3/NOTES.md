# C3 (Section A)

- **Keyframe:** `kf_sdr2.jpg` (seedream-5-pro). Night skyline over the lake, Lake Shore Drive curve, one white car.
- **Video:** Seedance 2.0, 720p, first-frame-locked, raw jobs in `media/gen/A_C3/` (prompts in `tools/sectionA/vid.py`).
- **Chosen:** take 1, `take_1_engraved.mp4`, clip in 0.0 s, rate 1.0. Slow aerial push; a stray pedestrian appears at ~5 s (outside the used range).
- **Engrave:** `tools/sectionA/engrave_take.sh` (tools/engrave, 1080p, strength auto unless noted; matte in `take_N_matte/` where Jade is in frame).
- **Cost:** see tags `A_C3*` in `media/genlog.jsonl` / `media/gen/spend.jsonl` (keyframes ~$0.05-0.21 each, video $0.60-0.75 per take).

Video prompt (take 1):
> Night. Slow steady aerial drift forward over the dark lake toward the skyline. The tiny white car glides along the curving lakeside drive, its headlights moving; the lake ripples shimmer gently; city windows twinkle. Camera: slow smooth push-in, no cuts. Keep the exact drawing style of the first frame throughout: black-and-white wood engraving world, only the anime girl in color. No text, no letters, no subtitles, no logos, no watermark.
