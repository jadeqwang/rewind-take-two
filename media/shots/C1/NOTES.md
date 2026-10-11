# C1 (Section A)

- **Keyframe:** `kf_hero.jpg` (nano-banana-pro). 11 variants (3 compositions x nbp/flare, then 2 refinement rounds). Low-angle canyon with 5 agents in the foreground won: the bullet wake leads straight back to the centre agent's pistol, so the whole story reads in one look.
- **Video:** Seedance 2.0, 720p, first-frame-locked, raw jobs in `media/gen/A_C1/` (prompts in `tools/sectionA/vid.py`).
- **Chosen:** take 1, `take_1_engraved.mp4`, clip in 0.0 s, rate 1.0. Hero: kf_hero (= kf_nbpc4). Take 1 holds the freeze (only hair/motes drift); take 2 pushes in too far by 2 s. Engraved at fixed strength 0.35 + keep-color so the motes stay orange/blue.
- **Engrave:** `tools/sectionA/engrave_take.sh` (tools/engrave, 1080p, strength auto unless noted; matte in `take_N_matte/` where Jade is in frame).
- **Cost:** see tags `A_C1*` in `media/genlog.jsonl` / `media/gen/spend.jsonl` (keyframes ~$0.05-0.21 each, video $0.60-0.75 per take).

Video prompt (take 1):
> Time is frozen. Nothing moves except a few loose strands of the girl's hair drifting slowly and the small glowing orange and blue motes drifting very slowly in the air, like dust in still light. The girl, the bullet, its wake and the agents stay perfectly still, a paused frame. Camera: very slow smooth push-in toward the girl. Her face stays exactly as in the first frame: forehead smooth, brows relaxed, head keeps the first frame's angle, never a face close-up. Keep the exact drawing style of the first frame throughout: black-and-white wood engraving world, only the anime girl in color. No text, no letters, no subtitles, no logos, no watermark.
