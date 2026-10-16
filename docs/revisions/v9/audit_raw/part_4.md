# Part 4 findings: sheets 0184-0229 (2:02.67-2:33.29)

- **2:06.83-2:07.08 (f3044-f3050) E6a_swarm**, source clip `media/shots/B_swarm_boost/take_1_engraved.mp4` (bg + Jade layer; in 0.315, rate 1.14)
  - What's wrong: the rear agent of the right-hand pair (behind the lead agent, screen right of the blue ghost) changes identity. f3044-f3046 his face/hair is drawn in a different hatched style, the sunglasses half-dissolve and he reads as an older man with a moustache. f3047-f3049 his hair turns white-blond, and by f3050-f3051 he is a dark-haired clone of the lead agent again.
  - Why it reads as an error: the agents are identical by design, so one that briefly gets a different face and hair colour is the classic AI identity drift, not a deliberate beat.
  - Visibility: MED (the white hair flashes against the black suits; you catch it on a second watch)
  - Fix idea: paint or roto that agent's head from f3050 back over f3044-f3049, or re-time so the swarm starts from f3050.
  - Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p4_e6a_blond.jpg

- **2:07.25-2:07.88 (f3054-f3069) E6a_swarm**, source clips `media/shots/B_swarm_boost/take_1_engraved.mp4` + ghost `media/shots/_D/v3/ghost_swarm_rgb.mp4`/`ghost_swarm_alpha.mp4`
  - What's wrong: when the agents pile onto the kneeling blue ghost, their bodies melt into shapeless black masses. From about f3058 the two or three agents become bulbous black silhouettes with no readable arms or legs, and their heads/sunglasses float inside the translucent ghost body. Limbs merge (one leg sticks out of a blob) and the head count doesn't match the body count.
  - Why it reads as an error: it isn't a clean overlap of ghost over agent; the agent bodies themselves lose their anatomy and turn into the "melting crowd" look typical of AI video. The ghost glow makes it worse because you can see agent faces through her torso.
  - Visibility: MED (it's on screen for about 0.6 s at the centre of frame, though Jade's dive above pulls the eye)
  - Fix idea: cut out of E6a around f3056 (into E6b earlier), or composite the ghost opaque over the pile so the merged bodies are hidden.
  - Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p4_e6a_pile.jpg

- **2:03.00-2:05.25 (f2952-f3006) E5_slide_point** (uncertain), source clip `media/shots/B_slide_point_b/take_1_engraved.mp4`
  - What's wrong: soft grey/black smudge blobs drift in the blank paper sky above and right of Jade's head (e.g. f2953-f2958 near her shoulder and above the bun; specks along the top edge through f2996). They are out of focus and don't belong to the engraving.
  - Why it reads as an error: they look like dirt or generation noise rather than ink motes (no glow or colour, not following any motion path).
  - Visibility: LOW
  - Fix idea: clean-plate or paint out the sky region over the shot (it's a fixed patch area already: patch_slideptb.png).
  - Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p4_e5b.jpg

- **2:08.79-2:08.83 (f3091-f3092) E6c_two**, source clip `media/shots/C_coop/two_bo/take_1_engraved_bo.mp4` ("play" layer starts at shot+0.44 s with in=0.55)
  - What's wrong: a 2-frame washed-out flash in the middle of the shot. f3090 (the "still" layer, with motes) is full contrast; f3091 is lifted almost to white-grey and f3092 is half-lifted; f3093 is back to normal. The flash comes from the head of the source clip, which fades up from white where the "play" layer takes over.
  - Why it reads as an error: no beat or effect explains it; it looks like a render hiccup or dropped frame at an internal splice.
  - Visibility: MED (a 2-frame flicker is easy to feel at speed even if you can't say what it was)
  - Fix idea: set the "play" layer `in` about 2-3 frames later (≈0.65) or hold the still layer 2 frames longer.
  - Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p4_e6c_run.jpg (bottom row: f3090, f3091, f3092), plus zoom/f3091.jpg

- **2:09.08-2:09.17 (f3098-f3100) E6c_two**, source clip `media/shots/C_coop/two_bo/take_1_engraved_bo.mp4` + `media/shots/_D/v3/patch_two.png` ("unstreak" layer from shot+0.79)
  - What's wrong: as the two Jades sprint off, their lower bodies go translucent. In f3099-f3100 you can see the agent pile through the left Jade's legs and hips, smeared shoes and a ghost leg print are left on the floor, and the right Jade's legs dissolve into the agents behind. It looks like the clean-plate patch is crossfading over the running figures rather than only over the streaks.
  - Why it reads as an error: it's a half-dissolve double exposure of limbs and agents, not one of the distinct glowing residue copies.
  - Visibility: LOW (3 frames, motion-blurred, right on the cut to C1_hold)
  - Fix idea: end E6c 2 frames earlier (cut at f3098) or matte the Jades above the unstreak patch.
  - Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p4_e6c_legs.jpg

- **2:13.46-2:13.54 (f3203-f3205) C2a_swap**, source `media/shots/C_coop/c2t1_bo.mp4` with girl mattes `c2t1_L.mp4`/`c2t1_R.mp4` (BLUE recolour via `tools/v4B/coop/recolor.py`)
  - What's wrong: as the orange twin jumps over the crouching blue twin, the recolour split runs as a hard vertical seam straight through the leaping girl. In f3204 her torso and arm are sliced by a vertical line. In f3205 her left forearm is still orange/cream but everything right of the seam (jacket stripes, sleeve, collar) is BLUE, so for one frame she becomes a half-orange, half-blue girl with a visible cut line. Her shoe at lower left is also chopped by the same seam, so the sneaker reads as detached. The crouching twin's two bun pencils are tinted blue in these frames too (canon: wooden pencils).
  - Why it reads as an error: it's a matte/recolour failure where the twins overlap, a straight-edge cut through a body, nothing a game would do.
  - Visibility: MED (2 frames, but the colour jump on the leaping figure flashes right before the cut to C2b)
  - Fix idea: hand-fix the L/R mattes for f3203-f3205 (assign the leaping girl entirely to L), or trim C2a 3 frames earlier.
  - Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p4_c2_f3205.jpg

- **2:13.58-2:14.54 (f3206-f3229) C2b_letgo**, same mechanism (C2b layers "blue"/"orange" from the `_bo.mp4` plus L/R girl mattes)
  - What's wrong: once the twins stand side by side and overlap, the orange/blue colour coding bleeds and flips between the two girls:
    - f3206-f3214: the rear (right) twin wears orange headphones and an orange chest band together with a blue sleeve patch, so one jacket carries both colours, and the stripes shift from frame to frame.
    - f3216-f3218: the left twin has blue sleeve stripes under an orange collar.
    - f3223-f3225: the front girl is ORANGE. f3226-f3228: the same girl in the same continuous stride is BLUE (blue stripes, blue headphones, blue strap). f3229: she is ORANGE again.
    - f3224-f3225: the rear girl has a mixed orange/blue jacket.
  - Why it reads as an error: the colour is the only thing that tells the twins apart, and it flickers on one figure mid-stride. It reads as a glitchy recolour rather than a swap beat (the swap is staged by the jump in C2a, not here).
  - Visibility: HIGH (the f3226-f3229 orange to blue to orange flip is on the hero figure, in the centre of interest, right as the agents are flung)
  - Fix idea: redo the L/R mattes for C2b by tracking (the girls cross), or recolour by per-frame identity, not screen side. At minimum fix f3223-f3229.
  - Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p4_c2b_book.jpg (f3223-f3229 sequence), /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p4_c2_merge.jpg (f3206-f3214 mixed jackets)

- **2:26.33-2:26.75 (f3512-f3522) G3**, source clip `media/shots/G3/take_5_engraved_soft_patch.mp4` (matte `media/shots/G3/take_5_matte/matte_dilated9.mp4`, in 1.3, rate 1.6; render/timeline/E.js line 25). **Probably Jade's "three legs" frame.**
  - What's wrong: the floating Jade has THREE LEGS. From the first frame of G3, three sneakers are visible at the bottom of frame: two side by side at lower left, each at the end of its own trouser leg, plus a third on the bent leg with the cargo pocket and orange strap at right. That makes three trouser legs coming out of one pair of hips. It's clearest f3512-f3518. By f3519-f3521 the left pair is being cropped off the bottom edge as the camera rises, and by about f3523 only the bent leg's shoe is left, so the error "goes away" after roughly 0.4 s.
  - Why it reads as an error: classic AI extra-limb; nothing in the scene motivates a third leg (no ghost/residue tint, same solid render as her body).
  - Visibility: MED (it's at the bottom edge on a hard cut while the eye goes to the rainbow pencil stroke at upper left; easy to miss at speed, obvious on pause)
  - Fix idea: start G3 about 11 frames later (in ≈ 1.3 + 11/24*1.6 ≈ 2.03 s, retime to keep the stroke on the beat), or paint out the middle leg/shoe for f3512-f3522, or reposition/scale the layer so the feet sit below frame from the cut.
  - Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p4_g3_threelegs.jpg (full-res crops f3512/f3514/f3518/f3522), /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p4_g3feet_a.jpg (timeline strip), full frame /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/f3514.jpg

- **2:33.13-2:33.50 (f3675-f3684) M1**, 3D scene `render/three/scenes/e_loop.js` (shot 'M1', Jade sprite layer; render/timeline/E.js line 88)
  - What's wrong: the tiny Jade sprite on the elevated track blinks out. She is visible beside the blue-highlighted pillar in f3671-f3674, then disappears for 10 frames (f3675-f3684) while her orange glow and the blue path tint stay where she was, and she pops back in f3685. The camera is pushing in at that moment, so she is exactly where the eye is led.
  - Why it reads as an error: the glow without its subject looks like a missing layer or a depth/occlusion bug (the pillar isn't in front of her), not a beat. NOT an AI-generation artefact: it's an engine/sprite issue, but it reads as the same kind of glitch. Range note: it runs 5 frames past this part's last sheet (f3679).
  - Visibility: MED (she's the focal subject of the push-in)
  - Fix idea: check the sprite's depth test/visibility window in e_loop.js for M1 around t=153.1-153.5, and force it to render over the pillar.
  - Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p4_m1_seq.jpg (rows 3-5), /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/f3674.jpg vs /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/f3678.jpg

## Checked and judged intentional / clean (not reported)
- E7_02_leap / E7_04_chasm white or tinted falling Jade copies (f3267-3268, f3290-3295): ghostpop layers (v7 "ghost falls" canon).
- E7 multi-coloured Jade swarms, ribbons, motes: intentional.
- "HILBERT HOTEL" sign (E7_04/E7_05/E7_06): legible and spelled correctly, and it stays stable.
- E8a/E8b/E8c TVA ALERT text: authored, typed cleanly. The E8 negative agents are identical by design.
- G1 (f3384-3468): two pencils in the bun, headphones, 1420 MHz patch and hands all stable, no limb errors.
- G2 (f3469-3511): pencil pulled from bun, hair falls, second pencil drifts free. Consistent with canon; hands and legs fine.
- G4 diorama assembly (3D, procedural): no glitches beyond intended crank/assembly.
- C1_hold co-op plate book titles (Strogatz, Greene): authored, legible.

DONE: sheets 0184-0229 reviewed
