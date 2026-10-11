# D6 (Section A)

- **Keyframe:** `kf_sdr1.jpg` (seedream-5-pro). Past her shoulder, agents at the window with the meter.
- **Video:** Seedance 2.0, 720p, first-frame-locked, raw jobs in `media/gen/A_D6/` (prompts in `tools/sectionA/vid.py`).
- **Chosen:** take 1, `take_1_engraved.mp4`, clip in 0.3 s, rate 1.0. Residue meter needle twitches; Jade looks up.
- **Engrave:** `tools/sectionA/engrave_take.sh` (tools/engrave, 1080p, strength auto unless noted; matte in `take_N_matte/` where Jade is in frame).
- **Cost:** see tags `A_D6*` in `media/genlog.jsonl` / `media/gen/spend.jsonl` (keyframes ~$0.05-0.21 each, video $0.60-0.75 per take).

Video prompt (take 1):
> Night. The agent at the car window leans in and holds the brass residue meter out toward the girl; its needle starts twitching and ticking upward in small jerks. The second agent stands still behind him. The girl stays still, looking up at them. Static camera. Her face stays exactly as in the first frame: forehead smooth, brows relaxed, head keeps the first frame's angle, never a face close-up. Keep the exact drawing style of the first frame throughout: black-and-white wood engraving world, only the anime girl in color. No text, no letters, no subtitles, no logos, no watermark.

## v3 revision (2026-10-11, stream V1B): restaged (follow-up asked by rev-A, not a note of Jade's)

Why: v2 had one pencil and now cuts into the two-pencil D7, and its layout (the wheel between her and agents at
screen right) did not match the restaged D7/D8.

- **Staging:** `blockout_D6.png` (`tools/sectionA/blockout/`, shot `D6`): camera at the passenger seat looking across
  her to the driver's window. Car front = screen right, as in D8; D7 is the reverse angle. She is at the wheel.
- **Keyframe:** `kf_v3_1.jpg` (nano-banana-pro; refs: blockout, `media/design/jade_bun_two_pencils.png`, the D8
  keyframe for the agent and meter) had extra orange bands at the cuffs and hem. **`kf_v3_2.jpg`** is the edit: one
  orange band only, two pencils. Prompts: `tools/sectionA/kf_v3_id.py`.
- **Video:** Seedance 2.0 720p 4 s, job `media/gen/revA_v1b_D6/` → **`take_2.mp4`** (prompt in `tools/sectionA/vid_v3_id.py`).
- **Engrave:** `flock media/.engrave.lock tools/sectionA/engrave_take.sh D6 2` → `take_2_engraved.mp4`, `take_2_matte/`.
- **In the cut:** 32.36–33.66 (V1A's retime), clip in 0.4.
- **Weak:** from the side the two pencils make a narrow V, and the second eraser reads grey-blue rather than pale blue.
  The needle only twitches. Her jacket reads slightly pink-white next to D7.
- **Cost:** 2 keyframe calls $0.27, 1 take $0.60 (tags `revA_v1b_D6*`).
