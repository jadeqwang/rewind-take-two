# D5 (Section A)

- **Keyframe:** `kf_sdr1.jpg` (seedream-5-pro). Three symmetric agents, low angle.
- **Video:** Seedance 2.0, 720p, first-frame-locked, raw jobs in `media/gen/A_D5/` (prompts in `tools/sectionA/vid.py`).
- **Chosen:** take 1, `take_1_engraved.mp4`, clip in 0.0 s, rate 1.0. Three agents walking, backlit. Engine push-in (x2.2) on the centre agent so the lens-reflected lyric reads; a colourful extra girl walks in after 2.4 s (unused).
- **Engrave:** `tools/sectionA/engrave_take.sh` (tools/engrave, 1080p, strength auto unless noted; matte in `take_N_matte/` where Jade is in frame).
- **Cost:** see tags `A_D5*` in `media/genlog.jsonl` / `media/gen/spend.jsonl` (keyframes ~$0.05-0.21 each, video $0.60-0.75 per take).

Video prompt (take 1):
> Night. The three agents walk slowly toward the camera in perfect step, perfectly in sync, backlit by the blazing headlights; their long shadows stretch toward us; ties and jackets still, faces blank. Camera: slow steady dolly back, keeping the center agent large. Keep the exact drawing style of the first frame throughout: black-and-white wood engraving world, only the anime girl in color. No text, no letters, no subtitles, no logos, no watermark.

## v3 revision (2026-10-11, stream V1A)

Jade's note (0:30): "you see the 3 men in shades and suits and quickly cut to a closeup of the shades (still walking, but you see the words in the shades, rendered in an Escher woodcut native typeface)".
- **Wide (D5, 29.74–30.60):** `kf_v3_w.jpg` (nano-banana-pro, location ref = D4's `kf_v3_b.png`) → take 3 (job `revA_v1a_D5w`). The v2 wide was a wooded road; this one is the D4 shoulder with the lake and skyline.
- **Close-up (D5cu, 30.60–32.36):** `kf_v3_cu.jpg` (wayfarers fill the frame, lenses solid black) → take 2 (job `revA_v1a_D5cu`); the head rises and dips with the walk, plus a small per-beat bob in the engine.
- **Lettering:** `tools/sectionA/modules/woodcut.js`: Anton capitals (already vendored) cut as white line on the black lenses, hatched through the lower part of each letter, with nicks and gouge flecks; each word arrives as an outline, then is cut solid. Word-timed: men 30.57, in 30.81, shades 30.88, and 31.56, suits 31.75. No lower third.
- The close-up runs one beat into what was D6 (to 32.36) so "suits" can be read; D6 now starts at 32.36.
