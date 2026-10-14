# v7: D6, she breathes (Jade: "perfectly still at the wheel ... except for a single blink, no breathing")

**The shot:** D6 runs 32.36–33.66 (A.js; in 0.4, so source frames ~10–41 of `media/shots/D6/take_2_engraved_eraser.mp4`). The camera is in the passenger seat, she is at the wheel, and the agent shows the stopwatch at her window.
- D5cu before it (30.60–32.36) is the sunglasses close-up, with no Jade in it.
- D7 after it (33.66–36.30) has her reaching for her ID, and moves naturally.

**What was wrong.** Phase correlation on the source over the used range:
- her shoulders move less than 0.5 px;
- her hands move less than 0.3 px;
- her head barely moves until about frame 36;
- only the blink moves.

**Least invasive first.**
- No livelier stretch of take 2 exists: the whole 4 s take is equally still, and she only turns her head slightly after about frame 36.
- D6 take 1 is the older v2 staging, so it does not match.
- I therefore used a warp of just her.

**What I did:** `tools/d6_breath.py`, a pixel pass with no generative model, which writes `media/shots/D6/take_2_engraved_breath.mp4`. `A.js` D6 now points at it, with `in` still 0.4.
- **Her layer.** It uses the colour matte from `tools/matte_fix.py tools/matte_fix_specs/D6.json --check-only`, which includes the pencil tops. That way the bun, both pencils and the pink and blue erasers move with her head, and the eraser fix is kept.
- **Breath.** A smooth field rises by up to 5 px at 1080p:
  - it is full over her head, shoulders, upper back and chest;
  - it falls off down the torso to zero at the waist (y 900);
  - it falls off along the forearms to zero at the hands (x 1120), so her hands stay on the wheel and her arms flex in between;
  - her chest also swells forward by 0.25 of the rise.
  
  The cycle is 2.8 s with its low point at 0.1 s take time. She is already rising on the shot's first frame, peaks at about 1.5 s, and is turning into the exhale as the cut comes.
- **Head settle.** Her head sinks back 1.5 px relative to her shoulders over the shot.
- **Blink.** Kept: it is in the source, and the pass only moves pixels.
- **Composite.** Her warped layer goes over the untouched frame, so the agents, stopwatch, window frame, wheel and seat are never warped. Where she moves off a pixel, which only happens along downward-facing edges such as under her jaw, the world pixel straight below is copied in. Without this, a pale strip of her old chin edge showed under the jaw.

**Check.** I rendered `node render/engine/render.mjs --range 30 37 --preview --encode` to `render/engine/out/rewind/rewind_preview_30.00-37.00.mp4` and checked frames across the shot at 2–3× zoom: her hair, bun, pencils and erasers, jaw, back against the seat, and hands on the wheel. I found no swimming or edge artefacts.

Measured in the preview with phase correlation:
- her shoulder rises a steady 3.2 px at 540p over the shot;
- the agent's face stays within 0.3 px, apart from its own motion in the take.

Sheet: `d6_breath.jpg`, still against breath at source frames 10, 26 and 40, with fixed guide lines.

**Not done.**
- No hand shifting on the wheel. It would mean moving pixels over the wheel, so I left the hands fixed and only let the arms flex.
- The rise is subtle: 5 px at 1080p. Raise `AMP` in the script if Jade wants more.
- Nothing is committed.
