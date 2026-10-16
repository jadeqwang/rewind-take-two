# Part 3 findings (sheets 0138-0183, 1:32.00-2:02.62)

## 1:32.00-1:32.79 C_V2f_car tail (rear-view mirror) — driving coherence check
Checked f2208-f2226: this tail of the car shot is a straight-on view into a real interior rear-view mirror (stem to headliner, sun visors top corners, C-pillars and rear deck visible inside the mirror). No passenger-seat/steering content in this range; mirror geometry is coherent. One nit below.

- **1:32.00-1:32.75 (f2208-f2226) C_V2f_car**, source: tools/v4B/car/car_shot.js (mirror plate + tools/v4B/plate/plate.js plate overlays)
  - The plates in the mirror (TVA 4104 / TVA 1729 / TVA 4096) read left-to-right, not mirror-reversed. In a real rear-view mirror they would be backwards.
  - It's a film convention, so most viewers won't notice. Pedants might, given that the shot is literally captioned "IN MY MIRROR". The plates look like authored overlays, so this was probably a deliberate legibility choice.
  - Visibility: LOW
  - Fix idea: leave as is (legibility wins), or flip the plate overlays horizontally if she wants strict mirror logic.
  - Evidence: zoom/f2210.jpg

- **1:32.79-1:32.96 (f2227-f2231) C32_V2g1** (uncertain), source: media/shots/V2g1/take_1_engraved.mp4
  - The crashing L-train car is bent into a wraparound U, with both side walls fanning out from a single "front". Its wheel trucks hang in mid-air with no track under them.
  - The shotlist intends a train crashing down (kaizo trap), so the impossibility is authored. The warped body could still read as a generation morph, but it's only 3 clean frames before the white flash.
  - Visibility: LOW
  - Fix idea: none needed at this length; if anything, trim to the 2 most rigid frames.
  - Evidence: zoom/f2227.jpg

- **1:33.67 (f2248) C33_V2h1**, source: media/shots/V2h1/take_2_engraved.mp4 (in 0.25, rate 1.2)
  - On the first frame of the respawn run, a semi-transparent, orange-tinted fist floats in front of her hip. It isn't attached to either arm: the front arm is raised at chest height and the back arm is hidden. A pale white sliver (a phantom third leg/pant edge) also shows behind the trailing leg. Both are gone by f2249.
  - The pose doesn't match f2249 (it reads as a take seam or morph frame). A detached third hand is a classic AI-generation artefact, not respawn VFX.
  - Visibility: LOW (1 frame, though it's the first frame after a cut)
  - Fix idea: trim 1 frame (start the clip at in 0.30) or hold f2249.
  - Evidence: zoom/c33_f2248_extrahand.jpg, zoom/c33_seq.jpg

- **1:33.88-1:34.04 (f2253-f2257) C33_V2h1**, source: media/shots/V2h1/take_2_engraved.mp4
  - Her back arm disappears and a flat, rectangular orange block floats behind her backside at hip height, detached from her body, for 4-5 frames (f2254-f2257, faint at f2253). It's probably the back hand or cuff rendered as a smear, but it reads as an orange box hovering behind her.
  - Missing limb plus a detached blob: AI slop, not costume (no orange pouch in canon).
  - Visibility: MED (orange on paper-white is eye-catching, about 0.2 s)
  - Fix idea: paint out the block and draw the back arm, or end the shot ~4 frames earlier (cut at 93.88).
  - Evidence: zoom/c33_f2256_orangeblock.jpg, zoom/c33_seq.jpg

- **1:34.08-1:35.42 B2_plat (f2258-f2290)**: checked, nothing to report. The agents (identical, fine) have correct limb counts at full res (zoom/plat_f2276_agents.jpg). Jade's run cycle is clean.

- **1:35.67-1:35.88 (f2296-f2301) B2_leap** (uncertain), source: media/shots/B_leap/take_1_engraved.mp4 (in 0.30, rate 1.3)
  - Costume flicker across the landing. Through f2295 her cropped bomber is zipped closed (orange band across the chest). From f2296 to f2300 it is suddenly hanging open over the black crop top, with an orange strap end flapping at the waist. By f2301-f2302 it's zipped again, and the neck piece/headphones change shape with it. (Open-bomber-over-black-crop-top is the canon outfit per docs/treatment.md, so each state is fine on its own. The 6-frame open/shut flip is the problem.)
  - A garment unzipping and re-zipping in a quarter second, with no hand involved, is a generation morph.
  - Visibility: LOW. Downgraded after checking B2_skip, where the same open/closed look turned out to be just her torso rotating (zoom/skip_jacket_f2519_2520_2531_2532.jpg). Here the flip is faster and has no visible rotation, but it may still be the same thing.
  - Fix idea: paint the jacket closed on f2296-f2300 (the torso region is small), or retime so the landing skips those frames.
  - Evidence: zoom/leap_seq.jpg, zoom/leap_jacket_f2296_2298_2300_2302.jpg

- **1:36.75-1:36.79 (f2321-f2322) B2_chasm**, source: media/shots/B_chasm_dash_b/take_1_engraved.mp4 (layer A, in 0.3)
  - As she reaches the beam end, both sneakers melt into one grey-white smear fused with the pant hems. Her hands also lose their colour and render as grey hatched mitts.
  - Melting feet are typical AI motion smear. The grey hands look like the colour matte dropping them.
  - Visibility: LOW
  - Fix idea: hold f2320 for 2 frames, or fix the matte so the hands keep colour.
  - Evidence: zoom/chasm_feet_f2319_2321.jpg (third panel)

- **1:37.12-1:37.25 (f2331-f2334) B2_chasm**, source: media/shots/B_chasm_dash_b/take_1_engraved.mp4 (src ~1.3, the take-b jump)
  - Inside a single continuous shot, her pose pops twice in 3 frames:
    - f2331: deep crouch, arms swept back
    - f2332: standing almost upright, arms hanging (the camera/beam framing also shifts)
    - f2334: already mid-stride in a leap
  - On f2334 her face is a blank skin-coloured oval with no eyes, nose or mouth. Her forward arm is a grey, hatched, crumpled sleeve, and the orange headphones are gone from her neck. They stay missing on f2335-f2337 and come back later.
  - The source clock is continuous here (the rate change at jumpL is smooth), so the discontinuity is inside the generated take. A faceless frame plus pose teleport is textbook AI slop, and it lands on the key "she jumps" beat.
  - Visibility: MED (the crouch-to-stand-to-leap stutter reads as a hiccup at speed; the blank face only on pause)
  - Fix idea: cut from the crouch (f2331) straight to f2335 by dropping 3 frames, or frame-blend over them; or paint a face on f2334.
  - Evidence: zoom/chasm_pop_f2331_2334.jpg, zoom/chasm_face_f2334_2337.jpg, zoom/chasm_seq.jpg

- **1:37.71-1:37.96 (f2345-f2351) B2_chasm** (uncertain), source: media/shots/B_chasm_dash_b/take_1_engraved.mp4
  - The same bomber open/close flicker as in B2_leap. During the fall (arms going up) the bomber flips from zipped to open, showing the black crop top (f2344-f2349), right before the dash fx. It's canon-consistent as a single state; the issue is the flip.
  - Visibility: LOW
  - Fix idea: leave it; the dash fx swallows it.
  - Evidence: zoom/chasm_seq.jpg (row 3)

- Intentional and fine in B2_chasm: the graphite shadow sliding down the wall and bursting into motes, the black freeze frame/white ring/blue afterimages (dash fx), the prone landing on the wall top with dust puffs. HILBERT HOTEL sign is authored and legible (zoom/chasm_f2320_hotel.jpg).

- **1:40.08-1:40.17 (f2402-f2404) B2_G1**, source: composite in render/timeline/_B_gunfire.js g1() (agents cut-out over the lawn/hotel still card; see media/shots/B_* per _B_glayout.js)
  - As the camera pushes past agent A, his foreground pistol hand doesn't leave frame. It dissolves in place: f2402 is motion-smeared, and on f2403 hand and pistol are half-transparent with the lawn hatching showing through. On f2404 they're gone.
  - A see-through hand reads as a compositing/AI ghost rather than a camera move.
  - Visibility: LOW (1-2 frames, during a fast push)
  - Fix idea: slide the cut-out out of frame (or scale it past the lens) instead of fading it, or hard-cut it off at f2403.
  - Evidence: zoom/g1_hand_fade_f2400_2402_2403_2408.jpg (panel 3)

- **1:41.17-1:41.25 (f2428-f2430) B2_G2**, source: composite in render/timeline/_B_gunfire.js g2() (Jade's take layered over the G2 agents plate)
  - Depth-order error. Jade is far back by the ACROSS notice board, but as the near right-hand agent swings his arm out, her trailing leg and foot draw over his sleeve and hand (clearest on f2429). A distant figure overlapping a foreground hand reads as a paste-up.
  - Visibility: MED (it's right where the eye is, on the gunshot beat)
  - Fix idea: matte the agent's arm over the Jade layer for f2427-f2431 (hold-out roto), or nudge her path left/up by ~60 px for those frames.
  - Evidence: zoom/g2_hand_f2428_2431.jpg (panel 3 = f2429)

- B2_G1 otherwise checked (f2359-f2416). Agents' hands and pistols are coherent, the HILBERT HOTEL sign and "I ZIGZAG" are authored, and Jade's back-view run is coherent (zoom/g1_jade_seq.jpg).

- **1:42.12-1:42.42 (f2451-f2458) B2_G2**, same source as above (Jade layer over the G2 plate)
  - The same depth-order error, longer and more visible. Jade runs right past the near right-hand agent, and her head and torso draw on top of his raised elbow and sleeve for about 8 frames instead of going behind it. In the same frames she is heavily motion-blurred: her two legs fuse into one dark wedge (f2452-f2453), and a white matte halo outlines her head and back (f2451).
  - Visibility: MED-HIGH (the overlap sits at the frame's centre of interest for a third of a second)
  - Fix idea: hold-out roto of the agent's arm over Jade, or end her path before the elbow. Re-time the blur so the legs stay separate.
  - Evidence: zoom/g2_overlap_f2451_2458.jpg

- B2_G3 (f2460-f2501) checked: the earpiece hands have correct finger counts and the coil cords are coherent (zoom/g3_f2470_hands.jpg). Nothing to report.
- B2_skip (f2502-f2543) checked. The jacket looks like it flips open/closed in the contact sheet, but at full res it's open throughout and only her torso rotates (zoom/skip_jacket_f2519_2520_2531_2532.jpg). Her feet slide against the faster world plate, which is the authored clock split and reads as stylization. Nothing to report.

- **1:46.88-1:47.17 (f2565-f2572) B2_glance**, source: media/shots/B_glance/take_1_engraved.mp4 (src 0.35-1.8)
  - One of the orange pant straps sticks straight out behind her hip as a stiff horizontal rod, detached from the leg with paper showing between rod and pants. It hangs in mid-air for about 8 frames and never swings.
  - Fabric doesn't hold a rigid horizontal pose. It reads as a floating stick or prop.
  - Visibility: LOW-MED (orange on B&W draws the eye, but she's moving)
  - Fix idea: paint it out on those frames, or connect it to the cargo-pocket buckle.
  - Evidence: zoom/glance_strap_f2566_2569_2571.jpg

- **1:46.00-1:47.25 (whole shot) B2_glance** (also the B2_skip close frames), same source
  - The round shoulder patch (canon: "1420 MHz") is garbled pseudo-text that changes from frame to frame ("PWD", "P10" and so on).
  - It's AI-garbled lettering on a canon prop.
  - Visibility: LOW (small, only on pause)
  - Fix idea: track a clean "1420" decal over the patch, or blur it to an emblem.
  - Evidence: zoom/glance_strap_f2566_2569_2571.jpg (top-left of each panel)

- **1:48.75-1:49.62 (f2610-f2631) B2_corner_in** (uncertain), source: media/shots/B_round_corner_b/take_1_engraved.mp4 (punch-in, src 1.6-4.1)
  - After "smack into his chest", she doesn't bounce off. For about 20 frames she hangs in front of the agent with her back against his torso, both arms up, one leg kicked out horizontally and the other barely touching the pavement. Her body overlaps his silhouette. Limb counts are fine (2 legs, 2 arms throughout), but there's no support and no recoil. It reads as a weightless pose, as if she's pinned or floating, not the "bounces off, staggers back" the code comment describes.
  - Physics that reads as an AI-motion error rather than a game hit-stun, though the stylised hit-stun could arguably be intended.
  - Visibility: LOW-MED
  - Fix idea: speed the src through 2.0-3.4 (shorter hang), or swap to a take with a clear recoil.
  - Evidence: zoom/cornerin_seq.jpg, zoom/cornerin_legs.jpg

- **1:50.67-1:50.75 (f2656-f2658) B2_pistol** (uncertain), source: media/shots/B_pistol/take_1_engraved.mp4 (in 1.1, rate 1.15)
  - The muzzle end of the engraved pistol turns into a smooth, solid-black rounded cap (unlike the hatched, engraved metal everywhere else) for the last 3 frames of the shot. The gun also gains a second dark block (grip butt) under the fist from about f2650, so it briefly reads as having grips at both ends.
  - It's a prop morph, but small and at the very end of the shot.
  - Visibility: LOW
  - Fix idea: trim the last 3 frames (end at 110.65), or hold f2655.
  - Evidence: zoom/pistol_seq.jpg, zoom/pistol_hand.jpg

- **1:51.21-1:51.46 (f2671-f2675) C_V2n_continue** (uncertain), source: media/shots/B_shot/take_1_engraved_blue.mp4 (freeze at 0.44 + matte layer, slide x 0→330)
  - During the slide-right and paper wash, a grey, semi-transparent second Jade (legs on f2671, face/arm on f2673) sits about 70-100 px left of the colour Jade. It's the B&W plate's own Jade showing through the paper solid while the colour matte copy sits slightly offset, so it reads as a misregistered double exposure rather than one of the styled line-art ghosts.
  - Visibility: LOW (it's under the CONTINUE? wipe)
  - Fix idea: cut her out of the plate layer (lumaInv matte) for the first 0.3 s, as B2_skip does.
  - Evidence: zoom/continue_ghost.jpg

- **1:52.67-1:52.75 (f2704-f2706) B2_V2n1**, source: media/shots/V2n1/take_1_engraved.mp4 (in 1.78)
  - The ◀◀ icon on the big arcade button is a garbled grey pixel-smudge on f2704-f2705 before resolving to a clean ◀◀ on f2707. On f2706 a stepped, staircase-shaped outline cuts across the button's face (a generation seam).
  - AI-garbled iconography on the hero prop of the shot.
  - Visibility: LOW (2-3 frames at the start of a 0.3 s shot)
  - Fix idea: start the clip ~3 frames later (in 1.90), or paint a clean ◀◀ over the button face.
  - Evidence: zoom/v2n1_hand.jpg

- f2712 (1:53.00) is a pure-white frame at the E1 start. Authored (docs/sections/D.md: "with a white flash"), so not reported.

- E1_E2a_tracks (f2712-f2757) checked: the sprint legs are coherent at full res (zoom/e1_legs.jpg), and the superman dive and upside-down column kick are authored (D.md). The ghosts and ◀◀ scrub slit-scan are intentional. Nothing to report.
- E2_04_leap, E2_05_chasm_short, E2_06_lawn and E2_07_lawn2 checked. The agents' hands and guns are coherent (zoom/lawn_agents.jpg, zoom/lawn2_agents.jpg). The blank notice board in lawn2 has no text (fine). Nothing to report.

- **1:56.71-1:56.92 (f2801-f2806) E2_08_kick**, source: media/shots/B_kick/take_1_engraved.mp4 (see render/timeline/D.js E2_08_kick)
  - Two smudgy black ink blots (one larger, horizontal) float on the blank wall just above her raised hand and head for the whole second half of the shot. They aren't attached to anything and look like toner smears. This is the same "engrave black blot" artefact D.md mentions being patched on the E5 book cover. A thin yellow-green translucent stick also crosses her waist on f2802-f2806.
  - Dirt on the plate reads as a defect, not as drawing.
  - Visibility: LOW-MED (dark on a white wall, right above her face)
  - Fix idea: paint the blots out of the plate (static camera, so one clean patch works).
  - Evidence: zoom/kick_blots.jpg, zoom/kick_seq.jpg

- E2_09_climb (f2807-f2866) and R1_unclimb (f2867-f2879) checked. The wall-run off the awning and the hang/reach at the top of the fire escape (f2853-f2859, zoom/climb_float_f2857.jpg) read as game jumps. The ghosts, the "Rewind." text and the ◀◀ scrub are authored. Nothing to report.

- **2:00.54-2:00.62 (f2893-f2895) E4a_ladder**, source: media/shots/B_climb/take_1_engraved.mp4 (in 3.45, rate 1.89)
  - On f2894 she is headless. The torso (jacket with orange band) and the trousers are there, but there's no head, hair, bun or arms above the shoulders, just the plate behind her. On f2893 her head and bun are top-left of the torso. On f2895 the head is back but jumped about 100 px right and lower, with one arm now raised on the rail, and the whole body has shifted right. It's a 1-frame morph/teleport in the generated climb (sped up 1.9x, which exposes it).
  - Visibility: LOW-MED (1 frame, but a missing head on the protagonist is the classic slop tell)
  - Fix idea: drop f2894 (hold f2893 for 2 frames) or frame-blend f2893→f2895.
  - Evidence: zoom/ladder_headless_f2893_2895.jpg, zoom/ladder_seq.jpg

- E4a_ladder (rest) and E4b_haul (f2912-f2943) checked. In the haul, the hand-to-ghost-hand grip is coherent (zoom/haul_hands.jpg), the two pencils are in her bun and the orange headphones are at her neck. The tiny agents far below are fine at this scale. Nothing to report.

## Summary (part 3)
HIGH: 0
MED: 3. B2_chasm pose pop and faceless frame at f2331-2334. B2_G2 Jade drawn over the agent's arm at f2451-2458 (MED-HIGH). B2_G2 the same overlap at f2428-2430. C33_V2h1 floating orange block at f2253-2257 is borderline MED.
LOW / LOW-MED: E4a headless frame f2894; E2_08_kick ink blots; B2_glance rigid strap and garbled 1420 patch; B2_V2n1 garbled ◀◀ button; C33_V2h1 detached hand f2248; B2_G1 see-through hand; B2_chasm melting feet; plus uncertain items (B2_leap and B2_chasm jacket flip, B2_corner_in float, B2_pistol muzzle, CONTINUE double, V2g1 train, non-reversed mirror plates).
Car (V2f tail in range, f2208-2226): rear-view mirror shot, geometry coherent; no passenger-seat or steering content in this range.

DONE: sheets 0138-0183 reviewed
