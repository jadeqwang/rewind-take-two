# Part 2 audit: sheets 0092-0137 (1:01.33-1:31.96), v8 master 1080p

Context: Lake Shore Drive / Chicago = right-hand traffic, left-hand-drive car, so Jade should sit on the car's LEFT, wheel in front of her.

## 1. **1:06.29-1:07.16 (f1591-f1611) C10_V2b3**, media/shots/V2b3/take_1_engraved.mp4 (in 0.0, rate 1)
- What's wrong: PASSENGER-SEAT STAGING. Camera is in the back seat looking forward; the steering wheel is on the LEFT (correct LHD), but Jade is in the RIGHT-hand (passenger) seat, twisted round to look back at camera, stretching her left arm across the console to grab the wheel. She is not in the driver's seat for the whole shot.
- Why error: she is the driver in the story (C06 just before shows her in the driver's seat holding the wheel with both hands); a passenger-seat grab reads as the generator misplacing her.
- Visibility: HIGH (0.9 s, she is half the frame).
- Fix idea: regenerate/re-stage with her in the left seat, hands on the wheel, glancing up at the flipping sedan through the windshield (or mirror-flip the plate so the wheel is on the right... no: flip makes the car RHD; re-stage instead).
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_f1593.jpg, .../zoom/p2_f1608.jpg

## 2. **1:06.50-1:06.54 (f1596-f1597) C10_V2b3**, media/shots/V2b3/take_1_engraved.mp4
- What's wrong: mid-shot pop. For the first ~5 frames (f1591-f1595) Jade is fully engraved B&W; at f1596/97 she snaps to colour (orange band, blue dot, navy trousers) AND the framing jumps in the same frame (camera zooms in, sedan jumps position and angle, her pose shifts), so it reads as a 1-frame jump cut + matte switching on.
- Why error: every other shot keeps Jade in colour from the first frame; here the matte only engages part-way and coincides with a take discontinuity, so it reads as a glitch rather than the authored colour/B&W device.
- Visibility: MED (it's on the 3rd beat of a 0.9 s shot; noticeable on a second watch).
- Fix idea: trim the shot in to start at the post-jump frame (cut in ~0.22 s later and extend the tail) or paint the matte for f1591-f1595.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_c10_pop.jpg

## 3. **1:06.50-1:07.16 (f1596-f1611) C10_V2b3**, media/shots/V2b3/take_1_engraved.mp4 + take_1_matte
- What's wrong: matte leakage. A ragged white cut-out patch with a wobbly black ink outline hangs round the flipping sedan's right edge and behind Jade's bun/neck (approx x1250-1540, y300-620 at 1080p), and in f1600 a stray wavy black matte-edge line runs from the wheel rim across the dashboard (x730-1100, y590-700). The colour layer also drags the sedan's underside into the "Jade" colour pass (it renders smoother/greyer than the engraved world).
- Why error: looks like a botched cut-out/sticker edge, not an authored effect.
- Visibility: MED (white blob behind her head is visible on pause; at speed it flickers).
- Fix idea: clean the take_1_matte (restrict to Jade's silhouette) and re-run the engrave pass, as was done for D3/D6/P2 in v7.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_f1600.jpg, .../zoom/p2_f1608.jpg

## 4. **1:06.29-1:07.16 (f1591-f1611) C10_V2b3**, media/shots/V2b3/take_1_engraved.mp4
- What's wrong: canon break: only ONE pencil in her bun (single pencil, pinkish eraser), and NO orange headphones round her neck, in every frame of the shot. C06 a few seconds earlier has both pencils (pink + blue) and headphones.
- Why error: prop continuity; reads as the generator forgetting the character's kit.
- Visibility: MED (her head is large in frame; fans of the canon will spot it on rewatch).
- Fix idea: fold into the re-stage of finding 1; otherwise paint a second (blue-eraser) pencil and the headphones.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_f1608.jpg

## 5. **1:06.75-1:07.16 (f1602-f1611) C10_V2b3**, media/shots/V2b3/take_1_engraved.mp4
- What's wrong: the flipping sedan is inside the cabin. As it rotates, its underbody overlaps the roof headliner and the top windshield frame (x250-1300, y0-130 in f1608): it is drawn in front of the car's own roof, i.e. passing through it.
- Why error: depth order is wrong (sedan should be outside the glass, clipped by the roof/A-pillars); reads as a compositing/generation mistake.
- Visibility: LOW-MED (busy frame; on pause it's clear).
- Fix idea: re-stage with the sedan fully outside the windshield, or mask the roof liner over it.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_f1608.jpg

## 6. **1:05.75-1:06.25 (f1578-f1590) C09_V2b2**, media/shots/V2b2/take_1_engraved.mp4 (in 0.3, rate 1.3)
- What's wrong: the "near miss" is actually a hit: the flipping black sedan's nose comes down ON the white Acura's roof (f1579-f1590: its front bumper rests on / sinks into the roof just behind the windshield, with a spark at the contact) while the Acura's roof stays undented and both cars carry on. In f1588-f1590 the flipping sedan also goes rubbery: windows become white blobs, the body outline smears, a door handle floats as a white lozenge (x1300,540 in f1590).
- Why error: objects intersecting without consequence + a melting car body are classic generation artefacts; the shotlist calls for a sedan flipping OVER the car.
- Visibility: MED (the contact is visible at speed; the melt in the last 3 frames is pause-level).
- Fix idea: trim the shot to end at ~f1584 (before the roof contact/melt), or re-generate with clearance above the roof.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_c09_flip.jpg, .../zoom/p2_f1590.jpg

## 7. **1:05.79-1:06.25 (f1579-f1590) C09_V2b2** (uncertain, LOW)
- What's wrong: two Interstate-style route shields on the left verge carry illegible garbled glyphs.
- Why error: unauthored AI text in-world; minor because they are tiny.
- Visibility: LOW.
- Fix idea: paint blank or authored numbers (e.g. "41" for Lake Shore Drive / US-41).
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_c09_signs.jpg

## 8. **1:07.16-1:08.06 (f1612-f1633) C11_V2b4**, media/shots/V2b4/take_2_engraved.mp4 (in 0.2, rate 1)
- What's wrong: the falling lamppost goes THROUGH the Acura. Its base is in the foreground bush, its shaft is drawn over the car's rear door and rear wheel, but its glowing head comes to rest BEHIND the car against the far railing/kiosk (f1625, f1633). The car sits motionless and undamaged the whole time (no dodge).
- Why error: a solid pole can't be in front of the car at one end and behind it at the other without passing through the body; reads as a 2D layering mistake. Shotlist intent is "a lamppost falls (dodge)".
- Visibility: MED (the pole across the car is the subject of the shot; the depth contradiction is noticed on a second look).
- Fix idea: re-stage so the pole falls into the lane ahead of the car (car swerves), or mask the shaft behind the car body.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_f1625.jpg, .../zoom/p2_f1633.jpg

## 9. **1:08.33-1:08.94 (f1640-f1655) C12_V2b4**, media/shots/V2b4/take_2_engraved.mp4 (in 1.2, rate 1.2)
- What's wrong: the fallen lamp head lands at the Acura's rear wheel; the spark burst replaces the rear wheel entirely and the rear door/quarter panel dissolves into scratchy hatching (f1644-f1647: car has one wheel, the body behind the B-pillar breaks up); by f1648-f1654 a white starburst shreds the whole car body into spikes, the front half vanishes, and C13 then cuts to an intact wheel close-up. The car still rolls on.
- Why error: the car body melting/losing a wheel is a generation artefact, not a scripted crash (she "dodges").
- Visibility: MED.
- Fix idea: trim C12 to end before ~f1642, or swap to a take where the lamp lands clear of the car.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_f1646.jpg, .../zoom/p2_c12_melt.jpg

## 10. **1:10.71-1:11.58 (f1697-f1717) C15_V2b6**, media/shots/V2b6/take_1_engraved.mp4 (in 1.6, rate 1.2)
- What's wrong: top-down "closing trucks": the two tractor units are mangled. Each cab's inner side stretches into a long bent, arm-like neck that runs down alongside the Acura and "grips" its wing mirrors (sparks where they touch); the cabs fold in to meet in front of the car's bonnet, so the trucks are physically fused around the car rather than two lorries closing a gap.
- Why error: no real tractor can bend like that; reads as AI body-merge between three vehicles.
- Visibility: MED (top-down, high contrast; the shapes read wrong even at speed, the detail on pause).
- Fix idea: re-generate with rigid tractor units (or composite two straight trucks and the car as separate elements); otherwise shorten to the first 6-8 frames.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_c15_cabs.jpg

## 11. **1:12.04-1:12.46 (f1729-f1739) C16_V2b6**, media/shots/V2b6/take_1_engraved.mp4 (in 3.5, rate 1.6)
- What's wrong: after the Acura squeezes out ahead, the two tractor cabs close and FUSE into a single object: by f1734-f1739 they become one flat T/winged shape with a single central spine, a roof lamp on each "wing", the two trailers hanging off it like one vehicle.
- Why error: two separate lorries melting into one is a generation morph, not a staged collision (no crumple, no impact).
- Visibility: MED (it's the payoff of the trap and the shot is held; the fused shape is legible at speed).
- Fix idea: end the shot ~f1730 (as the car clears), or composite a hard collision (flash/smash cut) over the merge.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_c16_merge.jpg

## 12. **1:17.13-1:17.50 (f1851-f1859) C21_V2c5**, media/shots/V2c5/take_2_engraved.mp4 + take_2_matte (in 0.3, rate 1.2)
- What's wrong: steering-wheel rim pops. For 9 frames the matte grabs the top of the rim: it turns from engraved line-art to a solid glossy black colour arc that is thicker and sits higher/larger than the engraved wheel beneath it (the held arc no longer lines up with the rest of the wheel, so it reads as a second, floating rim), then snaps back to engraved at f1860.
- Why error: a prop changing rendering style and size for a third of a second is a matte flicker, not the colour/B&W device (which is for Jade, not the car).
- Visibility: MED (hero shot, the wheel is centre frame; the pop on and off is noticeable).
- Fix idea: clean take_2_matte so the rim stays world (engraved) in f1851-f1859.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_c21_rim.jpg, .../zoom/p2_c21_wheel.jpg

## 13. **1:16.90-1:18.66 (f1846-f1888) C21_V2c5** (uncertain, LOW)
- What's wrong: driving geometry: the speedometer (the shot's subject, "needle pins") sits in the middle of the dashboard, well to the RIGHT of the wheel, with no instrument cluster behind the wheel. Seat side is correct (LHD, she is on the left, door mirror to her left).
- Why error: Acura sedans have the cluster behind the wheel; a lone centre gauge reads a little "generated" but some cars have centre gauges, so this is minor.
- Visibility: LOW.
- Fix idea: leave, or paint a cluster behind the wheel; not worth a re-gen alone.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_f1850.jpg

## 14. **1:19.58-1:20.44 (f1910-f1930) C23_V2c6**, media/shots/V2c6/take_1_engraved.mp4 (in 1.5, rate 1.2) (uncertain)
- What's wrong: driver's POV through the windshield, but the car's two headlamps are drawn ON TOP of the bonnet just below the windscreen, as glowing domes with starbursts, so the bonnet looks like it has headlights facing the driver. The windscreen frame also has no A-pillar/dash continuity (the frame is a single U shape, no dashboard, no mirror).
- Why error: from inside the cabin you can't see the headlamps; it reads as the generator pasting "headlights" onto the visible hood.
- Visibility: LOW-MED (the two bright starbursts are prominent, but the eye reads them as glare at speed).
- Fix idea: paint the domes out (leave a beam glow on the grating ahead), or accept as engraving stylisation.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_f1915.jpg

## 15. **1:23.98-1:24.86 (f2016-f2036) C27_V2d2**, media/shots/V2d2/take_4_engraved_blue.mp4 (in 2.0, rate 0.6, frameBlend)
- What's wrong: canon break: NO orange headphones round her neck in any frame; in their place is a pale-blue scarf/hood collar. (Pencils are fine: pink + blue, crossed through the bun.) The 1420 MHz patch reads as a garbled red badge with squiggle "text".
- Why error: the headphones are in every other close shot (C06, C21 hero, C29 next); dropping them on the hero mid-air close-up reads as the generator forgetting the costume.
- Visibility: MED (big close-up on "And now I'm", held 0.9 s).
- Fix idea: paint orange headphones over the blue collar (pixel pass like the v6/v7 eraser fixes), or regenerate the keyframe with the headphone ref.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_c27_jade.jpg, .../zoom/p2_f2022.jpg

## 16. **1:23.10-1:25.29 (f1995-f2047) C26_V2d1 -> C27_V2d2 -> C28_V2e1**, media/shots/V2d1/take_1_engraved.mp4, V2d2/take_4_engraved_blue.mp4, V2e1/take_1_engraved.mp4
- What's wrong: screen direction flips through the jump. C26 the car launches up and to the RIGHT; C27 (mid-air) its nose points LEFT; C28 it lands nose RIGHT. The car model also changes between shots (C27 is a 2001-style TL with round-ish lamps; C28 is a later TL/TSX with a different grille, lamps and plate position).
- Why error: a car reversing direction in mid-air for one shot and changing model reads as stitched-together generations, not a story beat. (Seat side in C27 is correct: nose-left shows the car's left/driver side and she leans out of the front driver window.)
- Visibility: MED (three consecutive hero shots on the drop; the direction reversal is felt at speed).
- Fix idea: hard to flip C27 without putting her in the passenger window; better to flip C26 + C28 (no text in either except HUD/lyric overlays, which are composited after) so all three read nose-left.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_c26_leaf.jpg, .../zoom/p2_f2022.jpg, .../zoom/p2_c28_car.jpg

## 17. **1:23.10-1:23.98 (f1995-f2015) C26_V2d1**, media/shots/V2d1/take_1_engraved.mp4 (in 2.0, rate 1) (uncertain)
- What's wrong: instead of launching off the leaf, the car sits pinned at the top of the far leaf for the whole shot: its front wheel rests on the leaf tip, rear wheel in mid-air, the leaf's girders pass behind/through the car's underside, and a spark fountain shoots from the nose as if it is welded there. It never leaves the leaf.
- Why error: reads as a stuck/merged object rather than a jump; physics breaks in a way that looks like an error.
- Visibility: LOW-MED (it is short and the spark draws the eye).
- Fix idea: use an earlier/later segment of the take where the car is clear of the leaf, or speed-ramp so it reads as launch.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_c26_leaf.jpg

## 18. **1:27.08-1:27.75 (f2090-f2106) C30_V2e3**, media/shots/V2e3/take_1_engraved.mp4 (in 0.0, rate 1.2)
- What's wrong: the skyline behind the bridge has a US-Capitol-style dome (plus a cupola tower), i.e. Washington DC, not Chicago. It sits left of the raised leaf for the first ~0.7 s, until the camera pans off it.
- Why error: the story places this on the Chicago River; a Capitol dome is a stock "city" hallucination, and Chicago viewers will spot it.
- Visibility: LOW-MED (small, mid-frame, engraved white on grey).
- Fix idea: paint the dome out (replace with a flat-roof block), or crop/scale to push it out of frame.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_c30_sedans.jpg

## 19. **1:27.75-1:28.38 (f2106-f2120) C30_V2e3** (uncertain)
- What's wrong: the two airborne agent sedans fly into the raised bridge leaf and pass behind/through it: the upper one is drawn in front of the leaf's lower edge in f2106 and then disappears behind the leaf grating by f2109-f2114, with no impact on the leaf; the lower one dissolves into the white spark burst at the road.
- Why error: an object occluded by a plane it was in front of a few frames earlier reads as a depth error.
- Visibility: LOW (busy background; the eye follows the Acura).
- Fix idea: trim C30's tail by ~6 frames or accept; low priority.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_c30_sedans.jpg

## 20. **1:28.42-1:29.26 (f2122-f2142) C31_V2f1**, media/shots/V2f1/take_1_engraved.mp4 (in 0.0, rate 1)
- What's wrong: (a) the white car that should be Jade's Acura is a different, boxier 80s/90s sedan AND carries a siren starburst on its roof like the agents' cars, so it reads as a white police car/taxi joining the pack, not her car being chased. (b) The pack is a dense overlapping mass: several black sedans interpenetrate (bonnets inside the car ahead, e.g. centre cluster x450-1100, y560-760) and strobes sprout from bonnets and wings, not just roofs. (c) The skyline again has a domed classical capitol building centre (x840-1060, y420-530).
- Why error: the hero car changing model and gaining a siren is identity drift; merged cars are a standard generation artefact.
- Visibility: MED for (a) (her car is the only white thing in frame); LOW for (b) and (c).
- Fix idea: paint out the white car's roof strobe (and ideally the grille to Acura) or composite the C30 Acura in its place; the pack overlaps are acceptable at 0.9 s.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_f2130.jpg, .../zoom/p2_c31_cars.jpg

## 21. **1:29.29-1:31.46 (f2143-f2195) C_V2f_car**, tools/v4B/car/car_shot.js (wide: media/shots/V2f3/take_1_engraved.mp4 / kf_wide_b_fix_engraved.png; close: media/shots/V2f4/kf_close_b2_engraved*.png)
- Driving staging check: seat side CORRECT (left-hand drive, Jade in the left seat, both hands on the wheel at ~10 and 2, Acura badge on the boss, centre stack to her right, passenger seat back to frame right). Road ahead is empty and curving; nothing contradicts right-hand traffic. Both pencils (pink + blue) and orange headphones present. No passenger-seat problem in this shot.
- What's wrong: the rear-view mirror has NO MOUNT and no windshield to hang from. In the wide there is no windscreen header, roof liner or stem; the mirror floats in the night air at road level, framed by the overpass/gantry beyond. During the push (f2186-f2195) the camera travels past the wheel and the mirror stays suspended outside the car among the overpass girders. Then at f2195-f2196 the close still cross-fades in with a completely different context: a roof liner, sun-visor clips and a stem holding the mirror. So the mirror appears outside the car, then is suddenly inside it.
- Why error: this is the very "impossible mirror" Jade wants gone from D3: the mirror is not physically attached to anything, so the over-the-shoulder restage still reads as a pasted-on mirror.
- Visibility: MED-HIGH (it's the subject of the push and is centre frame for 3 s; the missing stem plus overpass-behind-mirror is clear at speed once you look for it).
- Fix idea: paint a windscreen header + roof liner + stem into the wide (matching the close still's liner/visor clips) above the mirror, so the push travels under the roof; or start the cross-fade to the close still earlier (before f2188).
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_f2150.jpg, .../zoom/p2_v2f_handover.jpg

## 22. **1:29.29-1:30.96 (f2143-f2183) C_V2f_car** (LOW)
- What's wrong: the cabin is incomplete: no right A-pillar, no windscreen top edge, and the passenger seat back is a flat featureless upright slab (x1620-1920, y490-1080), as is her own seat back at bottom-left. The car reads as an open-topped box.
- Why error: AI interior simplification; adds to the floating-mirror impression in finding 21.
- Visibility: LOW.
- Fix idea: fold into the finding-21 paint pass (header + right pillar).
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_f2150.jpg

## 23. **1:31.50-1:31.96 (f2196-f2207) C_V2f_car** (uncertain, LOW)
- What's wrong: the mirror image shows the road and pursuing sedans directly, with no rear window frame, rear headrests or C-pillars round them, and the TVA plates (1729, 4104, 4096) read left-to-right instead of mirror-reversed.
- Why error: a real rear-view mirror frames the scene through the rear window and reverses text. The readable plates are authored and intentional (the text is the point), so this is a pedant's note only; the missing rear-window frame is the bit that reads "generated".
- Visibility: LOW.
- Fix idea: optional: lay a faint rear-window outline/headrest silhouettes into the mirror glass; keep plates readable.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_v2f_handover.jpg

## Shots checked with nothing to report (sheets 0092-0137)
C04_V2a4 / C05_V2a5 (to 1:02.30), C06_V2a3 (driver's seat, LHD, both pencils + headphones: OK), C07/C08_V2b1 (tilting-lane platforms: Escher, intended), C13_V2a2 (tyre close-up), C14_V2b5, C17_V2c1, C18_V2c2 (bridge rising), C19/C22_V2c3 (C22 J-turn shows the car spinning to face away; plausible as a skid), C20_V2c4, C24_V2c7 (tessellated fleet: intended), C25_V2c8 (gate crash: debris passes in front of car, coherent), C29_V2e2 (driver's seat LHD, both pencils + headphones: OK). No one-frame black/white flashes between shots in this range; all cuts land clean.

DONE: sheets 0092-0137 reviewed
