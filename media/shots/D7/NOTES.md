# D7 (Section A)

- **Keyframe:** `kf_nbp1.jpg` (nano-banana-pro). Hands pulling the colour ID card from the jacket.
- **Video:** Seedance 2.0, 720p, first-frame-locked, raw jobs in `media/gen/A_D7/` (prompts in `tools/sectionA/vid.py`).
- **Chosen:** take 1, `take_1_engraved.mp4`, clip in 0.0 s, rate 1.0. Colour ID card; DOCTORAL CANDIDATE / JADE WANG pinned on track_card.json (LK, smoothed).
- **Engrave:** `tools/sectionA/engrave_take.sh` (tools/engrave, 1080p, strength auto unless noted; matte in `take_N_matte/` where Jade is in frame).
- **Cost:** see tags `A_D7*` in `media/genlog.jsonl` / `media/gen/spend.jsonl` (keyframes ~$0.05-0.21 each, video $0.60-0.75 per take).

Video prompt (take 1):
> Her hands raise the colored ID card a little and hold it out steadily toward the car window, the card staying flat and facing the camera, fingers adjusting their grip. Slow, careful motion. Static camera. Keep the exact drawing style of the first frame throughout: black-and-white wood engraving world, only the anime girl in color. No text, no letters, no subtitles, no logos, no watermark.
