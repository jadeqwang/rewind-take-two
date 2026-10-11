# D5 (Section A)

- **Keyframe:** `kf_sdr1.jpg` (seedream-5-pro). Three symmetric agents, low angle.
- **Video:** Seedance 2.0, 720p, first-frame-locked, raw jobs in `media/gen/A_D5/` (prompts in `tools/sectionA/vid.py`).
- **Chosen:** take 1, `take_1_engraved.mp4`, clip in 0.0 s, rate 1.0. Three agents walking, backlit. Engine push-in (x2.2) on the centre agent so the lens-reflected lyric reads; a colourful extra girl walks in after 2.4 s (unused).
- **Engrave:** `tools/sectionA/engrave_take.sh` (tools/engrave, 1080p, strength auto unless noted; matte in `take_N_matte/` where Jade is in frame).
- **Cost:** see tags `A_D5*` in `media/genlog.jsonl` / `media/gen/spend.jsonl` (keyframes ~$0.05-0.21 each, video $0.60-0.75 per take).

Video prompt (take 1):
> Night. The three agents walk slowly toward the camera in perfect step, perfectly in sync, backlit by the blazing headlights; their long shadows stretch toward us; ties and jackets still, faces blank. Camera: slow steady dolly back, keeping the center agent large. Keep the exact drawing style of the first frame throughout: black-and-white wood engraving world, only the anime girl in color. No text, no letters, no subtitles, no logos, no watermark.
