# D8 (Section A)

- **Keyframe:** `kf_nbp1.jpg` (nano-banana-pro). Agent with the ID (colour) and meter at max.
- **Video:** Seedance 2.0, 720p, first-frame-locked, raw jobs in `media/gen/A_D8/` (prompts in `tools/sectionA/vid.py`).
- **Chosen:** take 2, `take_2_engraved.mp4`, clip in 0.2 s, rate 1.0. Take 1 morphed the ID portrait into a different anime girl (off-model): rejected. Take 2 keeps the card; head tilt reads. Needle movement is subtle.
- **Engrave:** `tools/sectionA/engrave_take.sh` (tools/engrave, 1080p, strength auto unless noted; matte in `take_N_matte/` where Jade is in frame).
- **Cost:** see tags `A_D8*` in `media/genlog.jsonl` / `media/gen/spend.jsonl` (keyframes ~$0.05-0.21 each, video $0.60-0.75 per take).

Video prompt (take 2):
> Night. The agent holds the small ID card perfectly still; the card and the tiny portrait on it stay exactly as in the first frame, unchanged. Faint orange and sky-blue motes drift up off the card. In his other hand the brass meter's needle swings hard to the far right end of the dial and quivers there. His head tilts slowly to one side, uncanny. Static camera. Keep the exact drawing style of the first frame throughout: black-and-white wood engraving; no new people or characters appear. No text, no letters, no subtitles, no logos.
