# B_g2clean (v4 gunfire, notes 1:39 / 1:41)

Plan: docs/revisions/v4/plans/gunfire.md. Prompts in tools/v4B/gunfire/gen.py (KF / VID entries `g2clean`).

Verdict: kf_v1 = B_g2 kf_v2 with the girl removed; take_1 used for G2 (agents only, engraved --no-matte); pistol track take_1_gun.json (tools/v4B/gunfire/gun_track.py).

## Paid calls

- 2026-10-11T23:17:05Z `google/nano-banana-pro` tag `v4B_gun_edit_g2clean` -> ['media/shots/B_g2clean/kf_v1.jpg'] (no seed set)
  prompt: Remove the girl completely from this engraving and fill the place where she was with the same engraved lawn strokes and the blank notice board, continuing them seamlessly, so the lawn in front of the board is empty. Change nothing else at all: the three agents in exactly the same poses (the left one
- 2026-10-11T23:17:23Z `bytedance/seedance-2.0` tag `v4B_gun_B_g2clean` -> None (no seed set)
  prompt: Static locked-off camera: the camera does not move, pan or zoom at all; the background stays perfectly still. The middle agent holds his arm out, his pistol pointed down at the lawn near the left post of the notice board, and fires twice, about a second apart: each time the pistol kicks up a little 
- take 1 `bytedance/seedance-2.0` 720p 4 s, first frame media/shots/B_g2clean/kf_v1.jpg, job rewind2/v4B_gun_B_g2clean-0fccb290af
  prompt: Static locked-off camera: the camera does not move, pan or zoom at all; the background stays perfectly still. The middle agent holds his arm out, his pistol pointed down at the lawn near the left post of the notice board, and fires twice, about a second apart: each time the pistol kicks up a little and comes straight back to the same aim; between the shots his arm drifts slowly a little to the right. The agent on the left keeps two fingers pressed to his earpiece and nods slightly as he speaks. Within the first second the agent on the right raises his free hand, the one nearer the middle of the picture, presses two fingers to the earpiece at his ear and keeps it there. All three keep their backs to the camera and never turn round. Nobody else appears. The notice board stays blank and perfectly still. No muzzle flash, no smoke, no color at all. Keep the first frame's look: everything stays a crisp black-and-white Escher-style wood engraving, no color, no gray wash. No text, no letters, no numbers.
- take None `bytedance/seedance-2.0` None None s, first frame None, job None
  prompt: None
