PROGRESS: last sheet reviewed = sheet_0321 (all sheets 0276-0321 done)

# Part 6: sheets 0276-0321 (3:04.00-3:34.62), F5a-F8 + start of O1

- **3:11.71-3:12.33 (f4601-f4616) F6a**, media/shots/F6a/take_4_engraved_dered.mp4 (plate layer, rate 0.65, frameBlend: true; F_edl.json)
  - What's wrong: in the last ~0.6 s of F6a the source camera pans/pushes fast, and the 0.65x frame-blend cross-fades two source frames that are far apart. Jade becomes a semi-transparent double exposure: two raised arms, two pencils (one with a blue eraser, one without), two hair masses, a see-through torso with the buildings showing through her jacket and pants, plus doubled water towers, triangles and dots in the background (clearest at f4610-f4616).
  - Why it's an error: it's not the authored ghost/residue look (the ghost Jades are discrete copies). This reads as a smeary, melting body, the "mushy AI video" look, right before the cut to F6b.
  - Visibility: MED (reads as a smear at speed; obviously a double exposure on a pause)
  - Fix: set frameBlend off for this layer (nearest-frame hold at 0.65x), or trim F6a to end at ~191.70, or play the tail at rate 1.0.
  - Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/f4605.jpg, /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/f4614.jpg (clean reference: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/f4596.jpg)

- **3:10.58-3:12.33 (f4574-f4616) F6a**, media/shots/F6a/take_4_engraved_dered.mp4
  - What's wrong: costume continuity. The orange headphones that she wears round her neck in F5a (f4416), and the pale-blue chest-dot patch, are both missing for the whole shot. The jacket here is a generic white/orange bomber with a high orange collar.
  - Why it's an error: canon (director_brief.md) puts the headphones round her neck in every shot, and the shot either side has them. An object popping off between consecutive hero shots reads as a generation inconsistency.
  - Visibility: LOW (a costume-continuity note; few viewers will clock it in a 1.8 s wide shot)
  - Fix: paint the headphones onto the plate/matte (static-ish pose, about 40 frames), or accept it.
  - Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/f4580.jpg, /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/f4596.jpg vs /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/f4416.jpg

- **3:07.08-3:08.83 (f4490-f4532) F5b**, media/shots/F5b/take_3_engraved_dered.mp4 (uncertain)
  - What's wrong: from behind, she holds a pencil in EACH hand (two separate pencils). The left-hand pencil is long early in the shot (f4492-f4508). By f4512-f4531 it reads as a short stub, and its far end is left in the background as a detached grey stick behind the book stack.
  - Why it might read as an error: the prop melts into the scenery; canon is one pencil in her hand.
  - Visibility: LOW (frame-stepping only; small in frame)
  - Fix: leave it, or paint out the left-hand pencil.
  - Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/F5b_hands_seq2.jpg, /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/f4500_jade.jpg

- **3:18.50-3:19.38 (f4764-f4784) F7_02**, media/shots/F7b/take_3_engraved_dered.mp4
  - What's wrong: the "1420 MHz" roundel on her left sleeve is model-drawn text, and it is garbled and changes every frame. It reads roughly "1420 / MHz" at f4764-f4766. By f4768-f4772 it has turned into scrambled glyphs ("1¿20 / WRZ"), and at f4780-f4782 it is unreadable bars. The roundel is large here (the shot is a medium close-up, about 70 px across), right next to her grinning face.
  - Why it's an error: unauthored, shimmering pseudo-text is a classic AI tell. The brief says "No model-drawn text, ever".
  - Visibility: MED (reads as shimmering marks at speed; obviously garbled on a pause)
  - Fix: track a clean "1420 MHz" roundel decal onto the sleeve (about 21 frames), or blur it to a plain roundel.
  - Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/F7_02_roundel.jpg (frames f4764-f4782, every 2nd)

- **3:20.25-3:22.02 (f4806-f4848) F7_04**, media/shots/F7c/take_2_engraved_dered.mp4
  - What's wrong: the "1420 MHz" roundel is model-drawn gibberish (something like "ŁATH / UTEIN" in blocky glyphs), and it sits on her left collarbone rather than her sleeve. It's stable across the shot, not flickering. Hands (five fingers, pencil in her right hand), legs and headphones all check out clean.
  - Why it's an error: unauthored garbled text on the hero's costume, in a centre-frame hero shot held for 1.8 s.
  - Visibility: LOW (roundel is about 45 px; you'd only read it on a pause)
  - Fix: paint a clean "1420 MHz" decal over it (the shot is near-static, so one tracked patch works).
  - Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/F7_04_roundel.jpg, /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p6seq/f4830.jpg

- **3:22.02-3:22.88 (f4849-f4869) F7_05**, media/shots/F7d/take_1_engraved_dered.mp4 (uncertain)
  - What's wrong: the six suited walkers on the street under the melting clock are posed mid-stride, but they barely translate across the shot (compare f4852 with f4862). They read as stride-locked, walking in place.
  - Why it might read as an error: AI-video "treadmill walkers". But the shot is only 0.86 s, and the agents' stiffness could pass as intent.
  - Visibility: LOW
  - Fix: none needed; or trim, or accept.
  - Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/F7_05_people_zoom.jpg

- **3:28.17-3:28.58 (f4996-f5005) F7_10**, media/shots/F1/take_3_wipe_dered.mp4 (clip_in 2.3, rate 1.1)
  - What's wrong: the pencil count changes from frame to frame while she runs at camera.
    - f4997 and f5002-f5003: a pencil in EACH hand.
    - f4998-f5001: a pencil in her right hand plus a second pencil gripped against her chest by the left hand, and a third dark stick showing behind her right hip.
    - f5004-f5005: only one pencil (right hand); the left hand is an empty fist.
  - The "1420 MHz" sleeve roundel is also garbled ("CATZ / UTHT") in the same frames.
  - Why it's an error: props duplicating and vanishing between consecutive frames is a textbook AI-video glitch. Canon is a single pencil in her hand.
  - Visibility: LOW-MED (0.44 s shot; the flip from 2 pencils to 1 is readable on a second watch)
  - Fix: use a different 0.44 s window of F1 take 3 with a stable single pencil, or shorten to f5002-f5005 only. If F1 at 2:49 uses the same frames, check it too.
  - Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/F7_10_pencils.jpg, /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/F7_10_body.jpg

- **3:15.42-3:17.60 (f4705-f4714, f4727, f4733-f4735) F6c**, media/shots/F6c/take_3_engraved_dered.mp4 (clip_in 0.3)
  - What's wrong: a run-cycle prop duplication. Her front hand holds the pencil at chest height the whole time. Each time the rear arm swings forward to her hip, that hand also grips a SECOND pencil, and it vanishes again on the back-swing:
    - clear at f4707 and f4711-f4714;
    - again at f4727 and f4733-f4735;
    - the rear hand is empty at f4691-f4704 and f4715-f4726.
  - The cropped jacket also opens and closes on a cycle: the black crop top shows clearly at f4708-f4714 and f4728-f4735, then the chest goes solid white (jacket closed, no crop top) at f4716-f4722 and f4736-f4742.
  - No extra legs: I checked every frame f4691-f4742, and both legs stay distinct through the cycle.
  - Why it's an error: a pencil that pops in and out of the second hand, and a garment that changes construction mid-stride, are classic AI-video continuity glitches, not authored residue.
  - Visibility: MED for the pencil (a hero side-run with the second pencil at hip height, readable on a second watch); LOW for the jacket (reads as the jacket flapping at speed)
  - Fix: paint out the hip pencil on about 15 frames (the rear hand is small and the background is a flat building), or swap to a take with a stable single pencil.
  - Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/F6c_body_a.jpg, /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/F6c_body_b.jpg, /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/F6c_body_c.jpg (full frames in /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p6seq/f4691-f4742.jpg)

- **3:29.90-3:31.64 (f5038-f5079) F8**, media/shots/F8/take_4_engraved_dered.mp4
  - What's wrong: the "1420 MHz" sleeve roundel is model-drawn pseudo-text, reading something like "LAZO / BHLZ". It is centre frame on the hero, in a near-static, held, breathing shot, so it's easy to read on a pause. The text itself is stable, not flickering.
  - Hands, the single pencil (held low in her right hand), headphones and legs are all fine. The ghost line-up is intended.
  - Why it's an error: garbled glyphs where real text belongs is an AI tell. This is the held "settle" moment the eye lingers on.
  - Visibility: LOW-MED (about 50 px roundel, chest height, 1.7 s hold)
  - Fix: paint a clean "1420 MHz" roundel decal (near-static shot; one tracked patch).
  - Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/F8_torso.jpg

## Notes / checked clean
- Three-legs example: NOT in this range. I checked every Jade full-body shot (F5a-c, F6a, F6c, F7_01/02/04/07m/08/10-13, F8) and found no extra or fused legs.
- Car mirror example: not in this range (no car shots in F5-O1).
- F6a: F7_12 (f5017-f5027) reuses F6a take 4 at in 0.4, which is the clean early part with no double exposure.
- These are authored and clean: the F6b/F7_03 penrose_march sprite agents (identical suits are fine); the 194.10 "clunk" flash; F7_05/F7_09 melting clock and its burst; F7_07m hand-touch triangle-mesh dissolve and merge; F7_08 colour ghost trail and rewind paint; F7_11 giant pencil; F7_13 floating pose (legs, strap, sneakers stable); O1 3D agents and the variance report typing (f5080-f5151).
- Shot-head flashes at each cut are the EDL's authored flash fx, not dropouts. I found no black or one-frame dropouts between shots.
- Severity tally: HIGH 0 / MED 4 (F6a frame-blend smear, F6c second pencil, F7_02 roundel text, F7_10 pencil count) / LOW 5 (F6a headphones, F5b stub pencil (uncertain), F7_04 roundel, F7_05 walkers (uncertain), F8 roundel)

DONE: sheets 0276-0321 reviewed

Note on evidence frame numbers: the single grabs zoom/f<N>.jpg (f4416, f4500, f4520, f4532, f4580, f4596, f4605, f4614, etc.) were taken with -ss N/24+0.01, so each one actually shows frame N+1. I verified this by diffing against a PyAV decode. Everything in zoom/p6seq/ and the montages built from it (F6c_*, F7_*, F8_*) uses the exact decode index, which matches the sheet labels. The one-frame offset doesn't change any finding.
