# D2 (Section A)

- **Keyframe:** `kf_sdr1.jpg` (seedream-5-pro). Out the passenger window, bulb-lined blank rooftop sign.
- **Video:** Seedance 2.0, 720p, first-frame-locked, raw jobs in `media/gen/A_D2/` (prompts in `tools/sectionA/vid.py`).
- **Chosen:** take 1, `take_1_engraved.mp4`, clip in 0.0 s, rate 1.0. Hotel sign HILBERT / VACANCY pinned by template tracking; Jade re-composited over it with take_1_matte_left (matte limited to the left of the frame because BiRefNet also grabbed the bulb sign).
- **Engrave:** `tools/sectionA/engrave_take.sh` (tools/engrave, 1080p, strength auto unless noted; matte in `take_N_matte/` where Jade is in frame).
- **Cost:** see tags `A_D2*` in `media/genlog.jsonl` / `media/gen/spend.jsonl` (keyframes ~$0.05-0.21 each, video $0.60-0.75 per take).

Video prompt (take 1):
> Night, inside the moving car. Outside the passenger window the engraved city slides past from right to left at speed; the rooftop sign with its ring of glowing bulbs passes by. The girl in the foreground stays still, looking out, a few hair strands stirring. Camera locked to the car. Keep the exact drawing style of the first frame throughout: black-and-white wood engraving world, only the anime girl in color. No text, no letters, no subtitles, no logos, no watermark.

## v3 revision (2026-10-11, stream V1A)

Jade's note (0:24): "where it currently says 'hilbert vacancy' it can display a lyric".
- **Keyframe:** `kf_v3_d.jpg`. `kf_v3_comp` = the v2 keyframe with the billboard enlarged 1.55x (local composite); `kf_v3_c` = nano-banana-pro clean-up of the composite plus two crossed pencils; `kf_v3_d` = one eraser recoloured pale blue. (`kf_v3_a` and `kf_v3_b` are rejects: the model redrew the whole frame.)
- **Take 2** (job `revA_v1a_D2`): the billboard drifts slowly left and stays whole inside the window; panels stay blank.
- **Engine:** the plate sits 90 px lower so the top panel clears the letterbox. Each panel is dark until its word is sung, then flickers on: `A SHADOW` (23.97 / 24.22), `CHASING` (24.78). No lower third. HILBERT / VACANCY is gone from this shot.
- Track: `track_v3_sign.json` (whole billboard, LK) → `track_v3_top.json`, `track_v3_bot.json`.
