# P2 (Section A)

- **Keyframe:** `kf_sdr1.jpg` (seedream-5-pro). Shocked eyes in the driver's seat.
- **Video:** Seedance 2.0, 720p, first-frame-locked, raw jobs in `media/gen/A_P2/` (prompts in `tools/sectionA/vid.py`).
- **Chosen:** take 1, `take_1_engraved.mp4`, clip in 0.6 s, rate 1.0. Clip in 0.6 skips a blink at 0.33 s; eyes wide throughout the used range.
- **Engrave:** `tools/sectionA/engrave_take.sh` (tools/engrave, 1080p, strength auto unless noted; matte in `take_N_matte/` where Jade is in frame).
- **Cost:** see tags `A_P2*` in `media/genlog.jsonl` / `media/gen/spend.jsonl` (keyframes ~$0.05-0.21 each, video $0.60-0.75 per take).

Video prompt (take 1):
> Her eyes widen in sudden shock, a small quick intake of breath, shoulders tense up; then she freezes. Static locked-off camera. Her face stays exactly as in the first frame: forehead smooth, brows relaxed, head keeps the first frame's angle, never a face close-up. Keep the exact drawing style of the first frame throughout: black-and-white wood engraving world, only the anime girl in color. No text, no letters, no subtitles, no logos, no watermark.
