PROGRESS: viewed all sheets 0230-0275; entries verified at full res.
# Part 5 findings: sheets 0230-0275 (2:33.33-3:03.96), M1 / V3S / M2 / M3 / F1-F4

Note on frame numbers: the suggested grab command (`-ss frame/24 + 0.01`) returns frame N+1, because ffmpeg takes the first frame with pts >= t. I checked this with `-copyts` + showinfo. All frame numbers below use exact frame indices that match the contact-sheet labels (grabbed at frame/24 - 0.005). My zoom files are named `zoom/p5f<frame>.jpg`.

- **Jade sprite blinks out (systemic, one root cause): M1 2:33.13-2:33.54 (f3675-f3685); M2 2:40.96-2:41.46 (f3863-f3875) and 2:43.29-2:43.79 (f3919-f3931); M3 2:47.00-2:47.50 (f4008-f4020) and 2:49.33-2:49.38 (f4064-f4065, last 2 frames before F1)**. Source: render/three/lib/engrave.js spriteFrame() + render/three/lib/sprite.js loadSpriteClip(), used by render/three/scenes/e_loop.js (M1, M3) and e_mobius.js (M2); clips media/shots/E_sprites/{walk_front,crank}
  - What's wrong: the tiny Jade sprite vanishes completely for 11-13 frames at a time, then pops back. In M1 she's walking the L track beside the blue post: gone at f3675, back at f3686 a step further on, in the middle of the push-in on her. In M2 she disappears from the booth by the crank twice. In M3 she disappears from the stoop at the crank post for about half a second, right at "it couldn't" while the agents close in.
  - Root cause, confirmed by arithmetic that predicts every observed window to the frame: spriteFrame() wraps the frame index modulo cols*rows of the atlas, not modulo the clip's real frame count. The walk_front atlas holds 40 frames in 29x2 = 58 cells, and crank holds 43 frames in 28x2 = 56 cells, so indices 40-57 (walk) and 43-55 (crank) sample empty transparent cells. Crank and idle advance at 24 fps, so she's invisible for 13 of every 56 frames: 0.54 s in every 2.33 s.
  - Why it reads as an error: the protagonist blinks out of existence at the focal point of the shot, with no ghost or rewind device. It reads as a render glitch.
  - Visibility: HIGH (M1 push-in, M3 at "it couldn't"). MED (M2 crank: she's small, but she's beside the action).
  - Fix idea: one line in spriteFrame(): wrap by the clip's frame count n (store n on the material's userData) instead of cols*rows. Re-render E. The same bug predicts a blink at M1 f3640-f3650 (2:31.67-2:32.08, part 4's range; she's tiny in the wide there), and it affects G4 or any other shot that uses SpriteActor.
  - Evidence: zoom/p5_M1_vanish.jpg (f3670-f3688), zoom/p5_M1_f3680_full.jpg, zoom/p5_M2_jadegap.jpg (f3861-f3932: present, gone, present), zoom/p5_sprite_check.jpg (M3 f4007 present, f4008/f4020 gone, f4021 present; f4063 present, f4064-f4065 gone)

- **2:40.21-2:40.58 (f3845-f3854) and 2:41.50-2:41.67 (f3876-f3880) M2**, source: render/three/scenes/e_mobius.js (carState(), the "state B" branch)
  - What's wrong: before the crank turns (ROT0 = 161.72, f3881), the join segment still points out to the exit road, so the band has an open gap. The follower sedans cross the join anyway, on the straight chord dB. They drive off the band's incoming end, slice through the edge of the white pier deck and the top of the pier column (f3850-f3852, f3876-f3878), and hang in mid-air over the water before landing on the far band end (f3853-f3854, f3879-f3880). The code comment says "followers only arrive after the crank", but with OMEGA = 3.1 (about a 2 s lap) and a 2.3 rad spacing, they arrive about every 0.7 s from the start of the shot.
  - Why it reads as an error: the story beat is that the loop is broken until Jade turns the crank. Cars hopping the gap through solid geometry is a physics or collision bug, not Escher. It also undercuts the crank payoff.
  - Visibility: MED (small black cars, but they're beside Jade's booth while the camera pushes in toward her for the crank)
  - Fix idea: keep followers queued or braking before E_IN until ROT1 (or hide them under the band's far side), so nobody crosses the join in state A.
  - Evidence: zoom/p5_M2_gap2.jpg (f3849-f3857), zoom/p5_M2_gap3.jpg (f3874-f3881)

- **2:42.42-2:42.62 (f3898-f3903), 2:44.25-2:44.46 (f3942-f3947), and again around f3916-f3919 and f3960-f3963 M2**, source: render/three/scenes/e_mobius.js (carState() state B with lapUp = -1: underside cars on the join segment)
  - What's wrong: after the crank, the cars on their second lap ride the underside of the band. On the white join segment, an upside-down car's four wheels poke up through the road surface as four black dashes (f3900-f3903, clearest). Where a top-side car and an underside car overlap on the segment, the two meshes interpenetrate into one double-height black blob (f3898-f3899, f3943-f3947).
  - Why it reads as an error: it's geometry clipping through a slab. The Möbius "other face" idea (Escher's ants) is intended, but wheels poking through the deck and two merged cars aren't.
  - Visibility: LOW for the wheel dashes (they read like road markings at speed). MED for the merged double car at f3943-f3947 (centre of frame, by Jade).
  - Fix idea: give the segment thickness and offset the underside cars by it (or skip rendering underside cars on the segment), and stagger the cars so a top-side and an underside car never share the segment.
  - Evidence: zoom/p5_M2_seg_a.jpg (f3896-f3903), zoom/p5_M2_jadecars.jpg (f3936-f3947)

- **(uncertain) 2:40.17-2:41.67 (around f3844-f3880) M2**, source: render/three/scenes/e_mobius.js
  - What's wrong: a dark hatched smear flickers on the band's incoming end where it meets the white segment and pier. Its shape changes every frame (zoom/p5_M2_deck.jpg, zoom/p5_M2_gap3.jpg f3874-f3880). It looks like z-fighting between the band end and the segment, or a car under the band poking through.
  - Visibility: LOW
  - Fix idea: small offset or polygonOffset between the band end cap and the segment, or check which mesh it is
  - Evidence: zoom/p5_M2_deck.jpg, zoom/p5_M2_gap3.jpg

- **2:49.67-2:52.96 (f4072-f4151) F1, two-pencil runs at f4077-f4081, f4093-f4096, f4119-f4123, f4130-f4131, f4141-f4143**, source: media/shots/F1/take_3_wipe_dered.mp4 (rate 1.1)
  - What's wrong: (a) **Two pencils.** In those runs she holds one pencil diagonally across her chest in her screen-right fist AND a second pencil in her screen-left hand down by her hip. In the frames between, one or the other vanishes (e.g. f4082-f4085 has only the low pencil, f4086-f4089 only the chest pencil), so the pencil hops between hands every few frames. (b) **The jacket design changes frame to frame.** The orange chest band crosses both panels at f4082-f4085 and f4116-f4118 and is gone elsewhere. The black round sleeve badge and the light-blue chest dot pop in and out from frame to frame (e.g. the badge is present at f4119-f4121 and f4130-f4131, gone at f4124-f4129; the blue dot is present at f4122-f4125 and f4144-f4147, gone at f4119-f4121 and f4126-f4129). The orange belt strap swaps hips. (c) The badge text is garbled AI scribble ("LLM 080"-like).
  - Why it reads as an error: canon is one drawing pencil (the two pencils in her bun are hair). A second pencil and a sleeve badge that blink in and out are textbook AI temporal inconsistency. It happens on the hero shot (colour-flood impact, running straight at camera, centre frame).
  - Visibility: MED (it reads as boil at speed; on a pause there are clearly two pencils, about 20 of 80 frames)
  - Fix idea: paint out the low screen-left pencil in the two-pencil runs and either paint out the badge or keep it constant. Or regenerate F1 with one pencil locked (reference sheet: pencil in right hand only).
  - Evidence: zoom/p5_F1_twopencils.jpg (f4079, f4080, f4094, f4095 full res), zoom/p5_F1_hands_a.jpg (f4076-f4099), zoom/p5_F1_hands_b.jpg (f4116-f4151)

- **3:00.04-3:02.83 (f4321-f4389) F4, impossible reflection in the Bean**, source: media/shots/F4/take_2_engraved_dered.mp4 (rate 1.3)
  - What's wrong: Jade dives head-down at the Bean, facing camera, arms spread (pencil in her screen-left hand). Her "reflection" in the Bean below her is a smaller, translated copy rather than a mirror image. (1) It shows her FRONT (face, black crop top, belly). A mirror behind her, from the camera's side, would show her back and the back of her head. (2) It isn't flipped about the surface: its sneakers point up toward her face and its head is at the bottom (f4321-f4366), so the two figures meet head to feet. (3) It's missing the orange headphones and the sleeve badge she has. Then at contact it morphs to fix itself. From f4373 to f4388 its grey arms spread just under her white arms, so she reads as one four-armed figure. Its face then slides up under hers until the two heads merge (f4384-f4389) inside the ripple rings.
  - Why it reads as an error: the beat ("the Bean reflects her, she dives into the reflection") needs a believable mirror, and this one breaks mirror logic (facing and orientation). It's the same class of problem as Jade's "impossible mirror" in the car. The four-arm and head-merge at contact, on "never stop", reads as body-merge slop.
  - Visibility: MED (centre frame for about 2.3 s, and the reflection is what the shot is about; the four arms are visible at speed at the climax)
  - Fix idea: re-stage. Composite a true mirrored copy of her matte into the Bean (flipped about the surface so the heads meet, showing the back of her head and her soles, warped to the curve). Or reframe from behind or over her shoulder so the Bean shows her face coming up to meet her. Cheapest: roto out the reflection's arms from f4373 and cut to the ripple at about f4384.
  - Evidence: zoom/p5_F4_mirror.jpg (f4330, f4344, f4356, f4366), zoom/p5_F4_wide.jpg (f4330, f4356 full frame), zoom/p5_F4_contact.jpg (f4366-f4397)

- **(uncertain) 2:37.12-2:37.25 (f3771-f3773) V3S**, source: media/sing/V3S/v4_sync_1080.mp4
  - What's wrong: the vocal for "my" starts at about 157.15 s (f3771), and the "MY" lettering appears on that frame, but her eyes are closed and her mouth stays shut for 3 frames (f3771-f3773). Her lips start to part at f3774 and are open at f3775. The rest of V3S/V3S_b ("the night before", "dissertation defense") tracks the vocal well, and her face, glasses, badges and stripes are stable.
  - Why it might read as an error: a short lip-sync lag on the first syllable after the pause. Viewers may sense it, but it's not mush.
  - Visibility: LOW
  - Fix idea: none needed. If anything, slip V3S by 2-3 frames around 157.1 (V3S_LAG is global, so only if it doesn't hurt "the night before").
  - Evidence: zoom/p5_V3S_my.jpg, zoom/p5_V3S_mouth_a.jpg

Reviewed with no issue to report: V3S/V3S_b (face, glasses, badges and stripes stable; lyric lettering is authored), V3S_cut, M3 agents and camera move, F2/F2b (wall-run with ghost Jades: ghosts are canon), F3 (Relativity flip, falling agents: intended; limbs check out at full res, zoom/p5_F3_legs.jpg). No one-frame flashes or dropouts at the M1/V3S, V3S_b/M2, M2/M3, M3/F1, F1/F2, F2b/F3 or F3/F4 cuts (the F1 white flash at 169.40 is authored).

DONE: sheets 0230-0275 reviewed
