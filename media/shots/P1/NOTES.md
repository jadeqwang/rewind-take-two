# P1 (Section A)

- **Keyframe:** `kf_sdr1.jpg` (seedream-5-pro). Agent at waist height reaching into his jacket.
- **Video:** Seedance 2.0, 720p, first-frame-locked, raw jobs in `media/gen/A_P1/` (prompts in `tools/sectionA/vid.py`).
- **Chosen:** take 1, `take_1_engraved.mp4`, clip in 0.0 s, rate 1.0. Hand into jacket. A cyan ghost girl appears after 1.5 s in the raw take (unused).
- **Engrave:** `tools/sectionA/engrave_take.sh` (tools/engrave, 1080p, strength auto unless noted; matte in `take_N_matte/` where Jade is in frame).
- **Cost:** see tags `A_P1*` in `media/genlog.jsonl` / `media/gen/spend.jsonl` (keyframes ~$0.05-0.21 each, video $0.60-0.75 per take).

Video prompt (take 1):
> Night. The agent's hand slides smoothly inside his black suit jacket toward the holster, the lapel lifting; his blank face does not change. Static camera. Keep the exact drawing style of the first frame throughout: black-and-white wood engraving world, only the anime girl in color. No text, no letters, no subtitles, no logos, no watermark.
