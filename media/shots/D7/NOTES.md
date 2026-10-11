# D7 (Section A)

- **Keyframe:** `kf_nbp1.jpg` (nano-banana-pro). Hands pulling the colour ID card from the jacket.
- **Video:** Seedance 2.0, 720p, first-frame-locked, raw jobs in `media/gen/A_D7/` (prompts in `tools/sectionA/vid.py`).
- **Chosen:** take 1, `take_1_engraved.mp4`, clip in 0.0 s, rate 1.0. Colour ID card; DOCTORAL CANDIDATE / JADE WANG pinned on track_card.json (LK, smoothed).
- **Engrave:** `tools/sectionA/engrave_take.sh` (tools/engrave, 1080p, strength auto unless noted; matte in `take_N_matte/` where Jade is in frame).
- **Cost:** see tags `A_D7*` in `media/genlog.jsonl` / `media/gen/spend.jsonl` (keyframes ~$0.05-0.21 each, video $0.60-0.75 per take).

Video prompt (take 1):
> Her hands raise the colored ID card a little and hold it out steadily toward the car window, the card staying flat and facing the camera, fingers adjusting their grip. Slow, careful motion. Static camera. Keep the exact drawing style of the first frame throughout: black-and-white wood engraving world, only the anime girl in color. No text, no letters, no subtitles, no logos, no watermark.

## v3 revision (2026-10-11, stream V1B): restaged

Jade, 0:35: "ID - test should not overlay fingers. you can just have redacted bars on the card image itself. also, the
entire body is half-missing and weird. maybe you should use Three.js to figure out how to stage this shot".

- **Blockout:** `tools/sectionA/blockout/` (three.js boxes: left-hand-drive cabin, seated figure, arms, card, agent,
  with the letterbox and dialogue box drawn on top). Three stagings tried: `blockout_D7a_overlay.png` (passenger-seat
  profile) and `blockout_D7b_overlay.png` (from the dash): body complete, but the card is small and sits in the
  dialogue box. **Chosen: `blockout_D7c.png`**, the agent's point of view through her open driver's window: she turns
  and holds the card's front up to us. D8 is the reverse angle, so D7 shows the front and D8 only the back.
- **Keyframe:** `kf_v3_1.jpg` (nano-banana-pro; refs: blockout, canon turnaround, v2 D6 keyframe). Right, but pencil
  tips to card bottom ran over 83 % of the frame height, more than the 2.39 letterbox shows. `kf_v3_1b.jpg` = the same
  with one eraser recoloured pale blue (the rainbow pencil; local pixel edit); `kf_v3_2_canvas.png` = that at 80 % on a
  grey canvas; **`kf_v3_2.jpg`** = nano-banana-pro continuing the drawing into the margins. Prompts: `tools/sectionA/kf_v3_id.py`.
- **Video:** Seedance 2.0 720p, 4 s, job `media/gen/revA_v1b_D7/` → **`take_2.mp4`**. The prompt is the action in
  reverse (she draws the card in and pockets it); the engine plays it backward (`D7_SRC` in `render/timeline/A.js`),
  so the shot ends exactly on the keyframe. Prompt: `tools/sectionA/vid_v3_id.py`.
- **Engrave:** `tools/sectionA/engrave_take.sh D7 2` → `take_2_engraved.mp4`, `take_2_matte/`.
- **Card:** white, pale-blue header band, portrait photo, four black redaction bars. Nothing is pinned on it by the
  engine. Two fingers rest on the blue header band; none cross the photo or the bars.
- **Canon check:** left-hand drive (wheel screen-left seen from outside her window), two crossed pencils (pink and
  pale-blue erasers), roundel `1420 / MHz` on her left sleeve, pale-blue dot on her left chest, mock-neck top.
- **Weak:** the night sky engraves lighter (grey hatching) than the keyframe's black; her right hand keeps holding the
  jacket front through the whole shot.
- **Cost:** 3 keyframe calls $0.40, 1 take $0.60 (tags `revA_v1b_D7*`).
