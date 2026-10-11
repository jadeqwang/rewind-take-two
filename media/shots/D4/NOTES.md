# D4 (Section A)

- **Keyframe:** `kf_nbp1.png` (nano-banana-pro). Car on the shoulder, sedan pulling in.
- **Video:** Seedance 2.0, 720p, first-frame-locked, raw jobs in `media/gen/A_D4/` (prompts in `tools/sectionA/vid.py`).
- **Chosen:** take 1, `take_1_engraved.mp4`, clip in 2.0 s, rate 1.0. Clip in 2.0 so the black sedan's headlight starbursts flare inside the shot.
- **Engrave:** `tools/sectionA/engrave_take.sh` (tools/engrave, 1080p, strength auto unless noted; matte in `take_N_matte/` where Jade is in frame).
- **Cost:** see tags `A_D4*` in `media/genlog.jsonl` / `media/gen/spend.jsonl` (keyframes ~$0.05-0.21 each, video $0.60-0.75 per take).

Video prompt (take 1):
> Night. The white car rolls slowly to a stop on the gravel shoulder; the black sedan behind it glides in and stops; its headlight starbursts swell brighter and their rays wash across the frame. Static low camera, no camera move. Keep the exact drawing style of the first frame throughout: black-and-white wood engraving world, only the anime girl in color. No text, no letters, no subtitles, no logos, no watermark.
