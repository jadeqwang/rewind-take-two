# P3 (Section A)

- **Keyframe:** `kf_sdr1.jpg` (seedream-5-pro). Shallow focus pistol, her torso beyond.
- **Video:** Seedance 2.0, 720p, first-frame-locked, raw jobs in `media/gen/A_P3/` (prompts in `tools/sectionA/vid.py`).
- **Chosen:** take 1, `take_1_engraved.mp4`, clip in 0.4 s, rate 1.0. Pistol rises level at her torso through the window (never the head).
- **Engrave:** `tools/sectionA/engrave_take.sh` (tools/engrave, 1080p, strength auto unless noted; matte in `take_N_matte/` where Jade is in frame).
- **Cost:** see tags `A_P3*` in `media/genlog.jsonl` / `media/gen/spend.jsonl` (keyframes ~$0.05-0.21 each, video $0.60-0.75 per take).

Video prompt (take 1):
> Night. The agent's pistol rises quickly into frame and levels at the girl's body through the open car window, aimed low at her torso, then holds steady. The other agents stay still. Static camera. Keep the exact drawing style of the first frame throughout: black-and-white wood engraving world, only the anime girl in color. No text, no letters, no subtitles, no logos, no watermark.
