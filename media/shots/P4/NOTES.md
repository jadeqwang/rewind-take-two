# P4 (Section A)

- **Keyframe:** `kf_torso1.jpg` (nano-banana-pro). Torso only (no head), orange/blue mote burst; flash card kf_flash1.png.
- **Video:** Seedance 2.0, 720p, first-frame-locked, raw jobs in `media/gen/A_P4/` (prompts in `tools/sectionA/vid.py`).
- **Chosen:** take 1, `take_1_engraved.mp4`, clip in 0.0 s, rate 1.0. 3-frame engraved muzzle-flash still (kf_flash1) then the torso mote burst; engine motes + whisper "shot" on top.
- **Engrave:** `tools/sectionA/engrave_take.sh` (tools/engrave, 1080p, strength auto unless noted; matte in `take_N_matte/` where Jade is in frame).
- **Cost:** see tags `A_P4*` in `media/genlog.jsonl` / `media/gen/spend.jsonl` (keyframes ~$0.05-0.21 each, video $0.60-0.75 per take).

Video prompt (take 1):
> Extremely fast: the cloud of glowing orange and sky-blue square motes bursts outward from her side, more and more of her torso dissolving into motes that fly outward toward the camera, then everything slows down and the motes hang suspended in the air. No blood. Static camera. Keep the exact drawing style of the first frame throughout: black-and-white wood engraving world, only the anime girl in color. No text, no letters, no subtitles, no logos, no watermark.

## v3 revision (2026-10-11, stream V1B): engine mote burst time

`render/timeline/A.js` had the P4 `motes` layer at `at: 40.37`. The module reads a number as shot-local, so the burst
was scheduled for 80.61 s and never fired; only the motes baked into the take showed, and the engine burst popped in
at the P5 cut (B.js starts it at the same instant, layer-local −0.28). Now `at: 0.13` (= 40.37): a two-frame hit
flash and the burst start in P4 and run straight into P5. P5/P6 frames are unchanged (compared at 40.70, 41.00, 41.50
and 42.20 against v2). `render/timeline/B.js` was not touched.
