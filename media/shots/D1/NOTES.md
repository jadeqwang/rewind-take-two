# D1 (Section A)

- **Keyframe:** `kf_sdr1.jpg` (seedream-5-pro). Chase cam behind the Acura, blank gantry panels.
- **Video:** Seedance 2.0, 720p, first-frame-locked, raw jobs in `media/gen/A_D1/` (prompts in `tools/sectionA/vid.py`).
- **Chosen:** take 1, `take_1_engraved.mp4`, clip in 0.0 s, rate 1.0. Gantry with two blank panels passes overhead; sign text pinned on track_signL/R.json (LK track + extrapolation once the panel leaves frame). A pink-haired passenger appears after 2.4 s (unused).
- **Engrave:** `tools/sectionA/engrave_take.sh` (tools/engrave, 1080p, strength auto unless noted; matte in `take_N_matte/` where Jade is in frame).
- **Cost:** see tags `A_D1*` in `media/genlog.jsonl` / `media/gen/spend.jsonl` (keyframes ~$0.05-0.21 each, video $0.60-0.75 per take).

Video prompt (take 1):
> Night. Chase camera following close behind the white car at high speed, extremely fast. The overhead sign gantry with its two blank panels rushes toward the camera and passes overhead, leaving the top of the frame; streetlights stream past on both sides; the road lines rush under the car. The camera keeps the same distance behind the car. Keep the exact drawing style of the first frame throughout: black-and-white wood engraving world, only the anime girl in color. No text, no letters, no subtitles, no logos, no watermark.
