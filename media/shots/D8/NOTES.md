# D8 (Section A)

- **Keyframe:** `kf_nbp1.jpg` (nano-banana-pro). Agent with the ID (colour) and meter at max.
- **Video:** Seedance 2.0, 720p, first-frame-locked, raw jobs in `media/gen/A_D8/` (prompts in `tools/sectionA/vid.py`).
- **Chosen:** take 2, `take_2_engraved.mp4`, clip in 0.2 s, rate 1.0. Take 1 morphed the ID portrait into a different anime girl (off-model): rejected. Take 2 keeps the card; head tilt reads. Needle movement is subtle.
- **Engrave:** `tools/sectionA/engrave_take.sh` (tools/engrave, 1080p, strength auto unless noted; matte in `take_N_matte/` where Jade is in frame).
- **Cost:** see tags `A_D8*` in `media/genlog.jsonl` / `media/gen/spend.jsonl` (keyframes ~$0.05-0.21 each, video $0.60-0.75 per take).

Video prompt (take 2):
> Night. The agent holds the small ID card perfectly still; the card and the tiny portrait on it stay exactly as in the first frame, unchanged. Faint orange and sky-blue motes drift up off the card. In his other hand the brass meter's needle swings hard to the far right end of the dial and quivers there. His head tilts slowly to one side, uncanny. Static camera. Keep the exact drawing style of the first frame throughout: black-and-white wood engraving; no new people or characters appear. No text, no letters, no subtitles, no logos.

## v3 revision (2026-10-11, stream V1B): restaged

Jade, 0:37: "he's holding his own id looking at the back of it? you should only see the back of an ID".

- **Staging:** `blockout_D8.png` (`tools/sectionA/blockout/`): from her seat, out through the driver's window. The
  agent holds HER card up and reads its front; the card's front faces him, so the camera sees only the back.
- **Keyframe:** `kf_v3_1.jpg` (nano-banana-pro; refs: blockout, agent sheet, v2 D6 keyframe) had the meter in a huge
  foreground hand coming from the corner (whose hand?) and in brass colour. **`kf_v3_2.jpg`** is an edit: his own hand
  holds the meter, engraved, no colour. Prompts: `tools/sectionA/kf_v3_id.py`.
- **Video:** Seedance 2.0 720p, 4 s, job `media/gen/revA_v1b_D8/` → **`take_3.mp4`** (prompt in `tools/sectionA/vid_v3_id.py`).
  The card never turns. The needle whips round and pins at about 2.0–2.5 s; the head tilt is slight.
- **Engrave:** `tools/sectionA/engrave_take.sh D8 3 --keep-color` → `take_3_engraved.mp4` (the card's pale-blue stripe
  and the motes stay in colour; everything else is ink).
- **In the cut:** clip in 1.18, rate 1.25, so the needle goes on "do" (36.92). The engine adds a small upward burst
  of orange/blue motes off the card at 36.78 (`motes`, shot-local `at: 0.48`).
- **Same card as D7:** white card, pale-blue band; here its back: pale-blue stripe on the top edge, black magnetic stripe.
- **Weak:** the dial is a stopwatch face, so "max" reads as the needle whipping round and stopping dead at the top,
  not as a gauge pinned at its end stop. He looks over the card toward her as much as at it.
- **Cost:** 2 keyframe calls $0.27, 1 take $0.60 (tags `revA_v1b_D8*`).
