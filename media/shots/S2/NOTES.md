# S2 (Section A)

- **Keyframe:** `kf_nbp1.jpg` (nano-banana-pro). High 3/4 view of the white car on the curving drive.
- **Video:** Seedance 2.0, 720p, first-frame-locked, raw jobs in `media/gen/A_S2/` (prompts in `tools/sectionA/vid.py`).
- **Chosen:** take 1, `take_1_lens.mp4`, clip in 0.0 s, rate 1.0. Engine: S1 frame + clean Bean plate push into the LSD headlights, then this lens clip (engraved take run through tools/sectionA/lens.py, convex-mirror bend relaxing flat) dissolves in. A hooded girl appears in the raw take after 2.4 s (unused).
- **Engrave:** `tools/sectionA/engrave_take.sh` (tools/engrave, 1080p, strength auto unless noted; matte in `take_N_matte/` where Jade is in frame).
- **Cost:** see tags `A_S2*` in `media/genlog.jsonl` / `media/gen/spend.jsonl` (keyframes ~$0.05-0.21 each, video $0.60-0.75 per take).

Video prompt (take 1):
> Night. The white car speeds along the curving lakeside drive; the camera swoops down and forward toward it, fast smooth push-in, the car stays centered while streetlights slide past. Keep the exact drawing style of the first frame throughout: black-and-white wood engraving world, only the anime girl in color. No text, no letters, no subtitles, no logos, no watermark.
