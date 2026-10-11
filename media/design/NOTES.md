# Character design: Jade and the TIME VARIANCE █████████ agents

Made 2026-10-11. Design spend was **$4.41** at list price, against a budget of about $8. It was logged under the `design_*` tags in `media/genlog.jsonl`. Seedream failed 4 times (HTTP 500/504 upstream); those calls were not billed.
Prompts are in `scripts/prompts.py` and the runs are in `scripts/r1.py`–`r5.py`. Every take, including the rejected ones, is in `takes/`. Contact sheets are built with `scripts/sheets.py`.
All the sheets are on plain off-white backgrounds, so they can be used as reference images.

## Contact sheets
- `sheet_1_jade_canon.jpg`: Jade canon set (deliverable 1)
- `sheet_2_agents.jpg`: agents (deliverable 2)
- `sheet_3_sprite_scale.jpg`: sprite scale reference (deliverable 3)

## Files, models and quality judgement

| File | Model | Verdict |
|---|---|---|
| `jade_canon_turnaround.png` | gpt-image-2.5-flare (style_tests) | Canon. Copied unchanged. |
| `jade_expressions.png` | flare, ref = canon | **Good.** Five busts: determined, scared, smirk, calm with eyes closed, singing. Face, bun, pencil, headphones and patches all hold. Take t3 was chosen because t1/t2's singing read as a yawn. |
| `jade_action_movement.png` | flare, ref = canon | **Good.** Sprint, dash with orange/blue speed lines, wall-jump kick, dodge roll, slide, landing crouch. Outfit is consistent. The roll is a little hard to read, which is normal for a curled pose. |
| `jade_action_pencil.png` | flare, ref = canon | **Good.** Three panels: she pulls the pencil out as the bun comes undone and her hair falls, she draws in the air with an orange-to-sky-blue line coming from the pencil tip, and she stands with her hair down. |
| `agent_turnaround_male.png` | flare (no ref) | **Best of 4 models.** True Escher-style hatching, blank mannequin faces, insets of the hands-less clock pin and the earpiece coil. |
| `agent_turnaround_female.png` | flare, ref = male | **Good, and matches the male.** Tight low bun, trousers, same pin and coil. |
| `agent_action.png` | flare, ref = male | **Good.** Three agents running in step, pointing, pistol held low at hip height, the residue meter (a stopwatch dial with a coiled cable to a wand), mid-stride with speed lines, and a woman touching her earpiece. "Frozen" reads more as "running" than "paused". For a freeze, nano's ghost after-image take is in `takes/agent_action_nano_t1.jpg`. |
| `agent_formation_v12.png` | flare, ref = male | **Good. Exactly 12** (a pair of point men, then 5 + 5), seen from behind, earpiece coils visible. Earlier takes had 11, because the models make a V symmetric with a single point man. |
| `sprite_scale_jade_agent.png` | flare, refs = canon + male agent | **Good.** Both figures side-on facing right, same baseline, Jade in colour and the agent engraved. Measured heights at 1536×1024: Jade 832 px (crown incl. pencil to sole), agent 918 px, so the ratio is **0.91** (165 cm vs 185 cm). |

## Model notes
- **gpt-image-2.5-flare** won everything here, including the engraved agents. Its hatching is the closest to the approved world plates, and it follows multi-figure layouts best.
- **nano-banana-pro** draws the agents as bold, solid-black linocut, which is less Escher-like. It also drew hands on the pin once and cropped figures on the action sheet. The best alternative is `takes/agent_turn_nano_t2_styleref.jpg`, which used a world plate as a line-technique reference.
- **seedream-5-pro**'s turnaround (`takes/agent_turn_seedream_t1.jpg`) has the truest hatching, but the pin is oversized. Its action and formation runs failed upstream.
- Clock-pin wording that works: "twelve tick marks, completely EMPTY centre: NO hands, no centre dot, no numbers, coin-sized".
- No sheet contains "Authority" or "TVA". The only text on any image is "1420 MHz" on Jade's sleeve.

## v3 revision pass: two pencils (2026-10-11, rev-A; $0.40, tag `revA_design_2pencils`)

Jade's v2 review: "maybe we have 2 pencils, one graphite, one rainbow". The canon is in `docs/revisions/A_streams.md`.

- **`jade_bun_two_pencils.png`: the reference for the bun.** Front, three-quarter and side heads plus a prop callout of
  the two pencils (both yellow hex barrels; graphite = pink eraser + grey point, rainbow = pale-blue eraser +
  rainbow-swirl point). The pencils cross in a narrow X at the back of the bun, erasers up. nano-banana-pro, edited
  from take 1. The back view was painted out because it drew a rainbow-striped barrel (raw: `takes/jade_bun_two_pencils_t2_raw.jpg`).
- Use it **together with** `jade_canon_turnaround.png` (outfit, proportions, patch lettering); the turnaround still
  shows one pencil, so say "two crossed pencils as in the bun reference" in the prompt.
- Rejected: `takes/jade_canon_turnaround_2pencils_reject.jpg` (an edit of the turnaround: oversized pencils, the
  roundel lettering garbled, the face drifted) and `takes/jade_bun_two_pencils_t1.png` (points stick out beside
  the face like horns; rainbow-striped barrel in the callout).
