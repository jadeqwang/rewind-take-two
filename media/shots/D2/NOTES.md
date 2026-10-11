# D2 (Section A)

- **Keyframe:** `kf_sdr1.jpg` (seedream-5-pro). Out the passenger window, bulb-lined blank rooftop sign.
- **Video:** Seedance 2.0, 720p, first-frame-locked, raw jobs in `media/gen/A_D2/` (prompts in `tools/sectionA/vid.py`).
- **Chosen:** take 1, `take_1_engraved.mp4`, clip in 0.0 s, rate 1.0. Hotel sign HILBERT / VACANCY pinned by template tracking; Jade re-composited over it with take_1_matte_left (matte limited to the left of the frame because BiRefNet also grabbed the bulb sign).
- **Engrave:** `tools/sectionA/engrave_take.sh` (tools/engrave, 1080p, strength auto unless noted; matte in `take_N_matte/` where Jade is in frame).
- **Cost:** see tags `A_D2*` in `media/genlog.jsonl` / `media/gen/spend.jsonl` (keyframes ~$0.05-0.21 each, video $0.60-0.75 per take).

Video prompt (take 1):
> Night, inside the moving car. Outside the passenger window the engraved city slides past from right to left at speed; the rooftop sign with its ring of glowing bulbs passes by. The girl in the foreground stays still, looking out, a few hair strands stirring. Camera locked to the car. Keep the exact drawing style of the first frame throughout: black-and-white wood engraving world, only the anime girl in color. No text, no letters, no subtitles, no logos, no watermark.
