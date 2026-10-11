# P2 (Section A)

- **Keyframe:** `kf_sdr1.jpg` (seedream-5-pro). Shocked eyes in the driver's seat.
- **Video:** Seedance 2.0, 720p, first-frame-locked, raw jobs in `media/gen/A_P2/` (prompts in `tools/sectionA/vid.py`).
- **Chosen:** take 1, `take_1_engraved.mp4`, clip in 0.6 s, rate 1.0. Clip in 0.6 skips a blink at 0.33 s; eyes wide throughout the used range.
- **Engrave:** `tools/sectionA/engrave_take.sh` (tools/engrave, 1080p, strength auto unless noted; matte in `take_N_matte/` where Jade is in frame).
- **Cost:** see tags `A_P2*` in `media/genlog.jsonl` / `media/gen/spend.jsonl` (keyframes ~$0.05-0.21 each, video $0.60-0.75 per take).

Video prompt (take 1):
> Her eyes widen in sudden shock, a small quick intake of breath, shoulders tense up; then she freezes. Static locked-off camera. Her face stays exactly as in the first frame: forehead smooth, brows relaxed, head keeps the first frame's angle, never a face close-up. Keep the exact drawing style of the first frame throughout: black-and-white wood engraving world, only the anime girl in color. No text, no letters, no subtitles, no logos, no watermark.

## v3 revision (2026-10-11, stream V1B): two pencils (follow-up asked by rev-A, not a note of Jade's)

- **Left-hand drive: already correct.** Checked on the take at full size: the camera is at the driver's-door front
  quarter, so the wheel is on screen-left with the passenger door and its mirror beyond her. Nothing flipped.
- **Keyframe:** `kf_v3_1.jpg` = the v2 keyframe (`kf_sdr1.jpg`) edited by nano-banana-pro: only the bun changed, to two
  crossed pencils with pink and pale-blue erasers (`media/design/jade_bun_two_pencils.png`).
- **Video:** Seedance 2.0 720p 4 s, job `media/gen/revA_v1b_P2/` → **`take_2.mp4`**; engraved under the shared lock →
  `take_2_engraved.mp4`, `take_2_matte/`. Clip in 0.3.
- **Framing (A.js):** kenBurns scale 1.02 → 1.07, y +130 → +148, so the erasers at the plate's top edge sit inside the
  2.39 letterbox. The sleeve roundel is out of frame as a result (it was half cut in v2).
- **Cost:** 1 keyframe call $0.13, 1 take $0.60 (tags `revA_v1b_P2*`).
