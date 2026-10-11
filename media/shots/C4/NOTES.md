# C4 (Section A)

- **Keyframe:** `kf_sdr1f.jpg` (seedream-5-pro (mirrored, patch un-mirrored by hand)). Side profile driving, dissertation + blank sticky note on the passenger seat. Note text DEFENSE 9AM is engine pencil, corner-pinned on track_note.json.
- **Video:** Seedance 2.0, 720p, first-frame-locked, raw jobs in `media/gen/A_C4/` (prompts in `tools/sectionA/vid.py`).
- **Chosen:** take 2, `take_2_engraved.mp4`, clip in 0.0 s, rate 1.0. Take 1 had the 1420 MHz patch mirrored (the keyframe was flipped for screen direction); take 2 from the patch-fixed keyframe. One slow blink at the end of the used range.
- **Engrave:** `tools/sectionA/engrave_take.sh` (tools/engrave, 1080p, strength auto unless noted; matte in `take_N_matte/` where Jade is in frame).
- **Cost:** see tags `A_C4*` in `media/genlog.jsonl` / `media/gen/spend.jsonl` (keyframes ~$0.05-0.21 each, video $0.60-0.75 per take).

Video prompt (take 2):
> Night drive. The girl drives calmly, eyes on the road, hands steady on the wheel, one slow blink. Pools of white streetlight sweep across her, the dashboard and the dissertation on the seat, front to back, rhythmically; the car sways very slightly. Camera locked to the car, no camera move. Her face stays exactly as in the first frame: forehead smooth, brows relaxed, head keeps the first frame's angle, never a face close-up. Keep the exact drawing style of the first frame throughout: black-and-white wood engraving world, only the anime girl in color. No text, no letters, no subtitles, no logos, no watermark.
