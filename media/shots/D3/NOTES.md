# D3 (Section A)

- **Keyframe:** `kf_sdr3.jpg` (seedream-5-pro). Rearview mirror, unlit black sedan, eyes glancing.
- **Video:** Seedance 2.0, 720p, first-frame-locked, raw jobs in `media/gen/A_D3/` (prompts in `tools/sectionA/vid.py`).
- **Chosen:** take 1, `take_1_engraved.mp4`, clip in 0.0 s, rate 1.0. Unlit sedan in the mirror; etched lyric along the TOP of the mirror glass (the bottom strip is bright road and swallowed the frosted etch).
- **Engrave:** `tools/sectionA/engrave_take.sh` (tools/engrave, 1080p, strength auto unless noted; matte in `take_N_matte/` where Jade is in frame).
- **Cost:** see tags `A_D3*` in `media/genlog.jsonl` / `media/gen/spend.jsonl` (keyframes ~$0.05-0.21 each, video $0.60-0.75 per take).

Video prompt (take 1):
> Night, inside the moving car. In the rearview mirror the unlit black sedan follows steadily, staying the same distance behind, the road unrolling behind it; passing streetlights flicker across the mirror. The girl's eyes flick up to the mirror and hold there, wary; she does not turn her head. Static camera locked to the car. Her face stays exactly as in the first frame: forehead smooth, brows relaxed, head keeps the first frame's angle, never a face close-up. Keep the exact drawing style of the first frame throughout: black-and-white wood engraving world, only the anime girl in color. No text, no letters, no subtitles, no logos, no watermark.
