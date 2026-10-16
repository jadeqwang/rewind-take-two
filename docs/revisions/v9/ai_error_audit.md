# v8 audit: impossible things that read as AI errors

Frame-by-frame audit of `deliverables/rewind_v8_master_1080p_sfx.mp4` (24 fps, 5,857 frames), 2026-10-15.
Every frame was viewed on labelled contact sheets (16 frames/sheet); suspects were confirmed on full-res frames.
Intentional impossibility (Escher/Monument Valley geometry, rewinds, ghosts/residue Jades, glitch/VHS post, HUD,
authored text) is excluded. **No fixes made this round.**

Frame numbers are 0-based (`f N` = N/24 s). Visibility: **HIGH** noticeable at full speed, **MED** on a second watch or
pause, **LOW** only frame-stepping. Evidence crops were saved in the session scratchpad (`zoom/`), not the repo.

## Headliners

| # | Time | Shot | Problem | Vis. |
|---|---|---|---|---|
| 1a | 0:38.90-0:39.68 (also flashed in C2 at f154-156) | P2 | **Passenger seat ("With no warning").** The wheel sits at lower frame-left with an empty gap between it and her, so nobody is driving. D7 (0:34) and C4 (0:10) put her at the wheel in the left seat. Checked by hand at f943. Note: the part 1 reviewer marked P2 as fine; that was wrong. Fix: mirror the plate or re-stage with the wheel in front of her. The car is also facing the wrong way. Pass the 0:35 frame to the video model to give them context. Also fix it at 0:40. | HIGH |
| 1b | 1:06.29-1:07.16 (also flashed in C2 at f145) | C10_V2b3 | **Passenger seat again.** Left-hand-drive car, Jade in the right seat reaching across to grab the wheel (checked by hand at f1600). Same shot: matte pop to colour (f1596), white cut-out blobs round her head, the flipping sedan passes through the cabin roof, one pencil and no headphones. | HIGH |
| 2 | 0:25.34-0:28.40 | D3 | **Impossible mirror** (Jade's example): side mirror seen face-on through her window. Her fix: over-the-shoulder into a real rear-view mirror. | HIGH |
| 3 | 1:29.29-1:31.46 | C_V2f_car | **The existing over-the-shoulder rear-view mirror is impossible too:** no stem, no windscreen/roof, floats outside the car among the overpass girders; at f2196 the close still fades in with a roof liner and stem. Fix D3 and this together. Driving staging itself is right (LHD, her on the left, both hands on the wheel). | HIGH |
| 4 | 2:13.6-2:14.5 | C2b_letgo (+C2a f3203-3205) | Orange/blue twin colouring swaps between the girls mid-stride when they cross (screen-side mattes); jackets mix both colours; a hard vertical seam cuts the leaping twin half orange/half blue. | HIGH |
| 5 | 2:26.33-2:26.75 (f3512-3522) | G3 | **Three legs** (Jade's example): floating Jade has three trouser legs and three sneakers until the feet leave frame. Fix: start G3 ~11 frames later or paint out. | MED |
| 6 | 3:00.0-3:02.8 (contact f4373-4388) | F4 | **Impossible Bean reflection** (same family as the car mirror): the reflection Jade does not match the falling Jade. Reflection Jade is not wearing headphones, missing a pale blue dot on the jacket, and has legs positioned somewhat differently (apart as opposed to together.) Falling Jade’s arm patch is also gibberish instead of 1420 MHz. | HIGH |
| 7 | 2:33.13-2:33.54, 2:40.96-2:41.46, 2:43.29-2:43.79, 2:47.00-2:47.50, 2:49.33-2:49.38 (likely also 2:31.67-2:32.08); f3675-3685, f3863-3875, f3919-3931, f4008-4020, f4064-4065 (f3640-3650) | M1-M3 | Tiny Jade sprite blinks out for ~12 frames and pops back while her glow stays. Not AI: the reviewer traced it to `spriteFrame()` in `render/three/lib/engrave.js`, which wraps the frame index by atlas cell count, not clip frame count, so some indices land on empty cells. One-line fix, then re-render section E. | HIGH |
| 8 | 0:00-0:01.90 | C1 | Opening hero still: the sleeve roundel reads "1A7O / IMHZ" instead of "1420 MHz". The garbled roundel recurs in the R2 death stills, F7_02 (scrambles every frame, next to her face), F7_04, F8 and B2_glance. | MED |
| 9 | 0:37.96-0:40.24 | P1 / P1b | The white Acura behind the agent is empty (bare headrests), cut against P2 where she's in it. It’s also facing the wrong way. See 1a. | MED |

All 8 parts are complete. Reviewer totals (before dedupe): part 0 2H/1M/2L, part 1 0H/3M/5L, part 2 2H/12M/9L,
part 3 0H/3M/~14L, part 4 1H/6M/2L, part 5 1H/4M/3L, part 6 0H/4M/5L, part 7 0H/2M/2L. Recurring themes: pencil
count changes (one vs the canon two, extra pencils in a hand), the garbled 1420 MHz roundel, missing headphones,
and AI vehicle physics in the V2 chase (cars melting, passing through each other or the cabin).

Corrections to the per-part notes below: part 1 says P2 is fine; it isn't (see 1a). Grabs taken with
`-ss N/24+0.01` show frame N+1; use `-ss (N-0.5)/24`.

## Detail by time range

### Part 0 (sheets 0-45)

### Part 0 findings: sheets 0000-0045 (0:00.00-0:30.62)

Note on frame grabs: `-ss f/24+0.01` returns frame f+1 on this file (checked against `select=eq(n,83)`); all zooms below use `-ss f/24-0.01`, which matches the sheet labels.

Clean, nothing to report: C1 (0:00.00-0:01.90; agents, hands and pencils are fine, apart from the roundel text below), C3 (title over Lake Shore Drive; lamp posts stand on the lake-side shoulder, car OK), C4 hands on wheel (f260-f280).

- **0:12.46-0:12.58 (f299-f302) C4**, source `media/shots/C4/take_4_engraved_bun.mp4` (+ canvas:pencil)
  - What's wrong: in the last 4 frames before the cut to S1, a dark-outlined pale shape (her sleeve/arm edge?) slides in at lower left and a coarse wood-grain hatch spreads across the blank notebook page, over the left third of the page up to the "DEFENSE 9AM" note. The page was plain paper in f272-f298.
  - Why it reads as an error: the hatch is not a shadow shape and has no source in frame. It looks like the engrave pass "texturing" the paper as world, so it reads as the page surface crawling.
  - Visibility: LOW (4 frames, right on the cut)
  - Fix idea: end C4 at f298 (trim 4 frames, or hold f298), or matte the page so the engrave pass leaves it plain.
  - Evidence: zoom/p0_c4_page.jpg (f288, f296, f299, f300, f302)
  - (uncertain whether the source take intends a hand to enter; either way the hatching is a texture artefact)

- **0:10.82-0:12.00 (f260-f287) C4**, source `media/shots/C4/take_4_engraved_bun.mp4`
  - What's wrong: costume side swap. The camera sits behind her on the passenger side (US car, front of car to screen right), so the near side is her RIGHT. The pale-blue dot patch is on that near (right) chest, and the near sleeve has no 1420 roundel. Canon (director_brief.md) puts the dot AND the roundel on her LEFT, and C1/C2 show both on the same side. In C4 the dot is mirrored to the right chest. A.js already notes "near (right) sleeve has no roundel".
  - Seating/steering itself is coherent: she is in the left (driver) seat with both hands on the wheel, and the empty passenger seatback is in the right foreground.
  - Why it reads as an error: only a costume-continuity nit. Fans who freeze-frame would notice the patch side, but it doesn't read as AI slop.
  - Visibility: LOW
  - Fix idea: paint out the dot on the near chest (or accept).
  - Evidence: zoom/f266.jpg

- **0:00.00-0:01.90 (f0-f45, and again f46-f56 in C2) C1**, source `media/shots/C1/take_3_engraved.mp4`
  - What's wrong: the sleeve roundel on the hero still reads like "1A7O / IMHZ" instead of "1420 MHz": the 4 is an A, the 2 a 7, and "MHz" is a garbled IMHZ. S1 (f352) shows the correct, clean "1420 MHz", so the two shots disagree.
  - Why it reads as an error: classic AI text-garble, on the opening hero frame that is held for about 2.3 s with no motion.
  - Visibility: MED (the frame is static and centre-weighted, and anyone pausing on the first frame sees it)
  - Fix idea: paint "1420 MHz" over the roundel in the source still (one static patch tracks the whole take, since the figure barely moves).
  - Evidence: zoom/p0_c1_roundel.jpg (f10); correct reference zoom/p0_roundels_S1_C1.jpg (S1 f352)

Clean, nothing to report: S1 (0:12.60-0:16.14; Bean, background pedestrians, lips, "1420 MHz" roundel all fine), S1x (lakefront, the tiny figure on the promenade holds its form), S2 (Acura on the curve: 4 wheels and mirrors stay stable), D1 (gantry text "LAKE SHORE DR / I'M SPEEDING DOWN LAKE SHORE" and "SOUTH" are authored and clean; the octagonal sign on the right is blank-hatched rather than garbled, which is fine), D2 (pencils pink+blue stay stable, billboard lettering authored).

- **0:25.34-0:28.40 (f609-f687) D3**, source `media/shots/D3/take_2_engraved_eraser.mp4` (+ canvas:plate tools/v4B/plate/plate.js, etch)
  - What's wrong: the impossible mirror. The camera sits roughly at the dash/A-pillar and looks back at Jade, so her face is three-quarter to camera and her headrest and the rear window are behind her. She looks to screen right, which is HER LEFT, the driver's side, so the seat side is consistent with C4/D4 and she reads as the driver here. But the driver's door mirror fills the right half of the frame with its GLASS facing the camera head-on, showing the pursuing sedan ("TVA 1729") square and centred. From a camera ahead of her at the dash you would see the back of the mirror housing. The glass faces rearward towards her eyes, which sit off to screen left. The view through the same side window streams forward, so the window shows the road beside her while the mirror, at full size and face-on to the lens, shows the road behind. Her eyeline aims at the window frame/A-pillar edge, not at the mirror glass.
  - Why it reads as an error: wrong mirror optics in a 3 s hero hold. It's the "she checks her mirror" beat, and any driver feels the mirror is turned the wrong way.
  - Visibility: HIGH (3.06 s hold, centred composition)
  - Fix idea (Jade's plan): over her shoulder, into the interior rear-view mirror at the top of the windshield, framing her eyes plus the sedan in the glass. Or shoot from outside the driver's door, so the door mirror's glass faces the camera with her face visible through the window behind it. Keep the etched lyric on the mirror's lower edge. V2f (88.38, "same composition as D3") inherits the same fix.
  - Evidence: zoom/f630.jpg

Clean, nothing to report: D4 (driver on the correct side, i.e. the car's left, which is screen right since the car faces camera; hands on wheel; both cars on the right shoulder; the sedan's headlight flare is authored) and D5 (the three agents' legs, shades and faces hold steady frame by frame: zoom/p0_d5_center_face.jpg, zoom/p0_d5_agents.jpg).

- **PASSENGER-SEAT STAGING (Jade's "protagonist in the passenger seat"). In-range: C2 flashes at 0:06.42-0:06.50 (f154-f156) and 0:06.04-0:06.08 (f145-f146). The real shots are P2 (0:38.90-0:39.68, `media/shots/P2/take_2_engraved_eraser.mp4`) and C10_V2b3 (1:06.28-1:07.16, `media/shots/V2b3/` take 1, per C.js row `[66.28, 67.16, 'V2b3', 1, ...]`).**
  - What's wrong:
    - **P2 ("With no warning"), confirmed at full res f943 (39.29 s).** She faces camera, close-up, centred. The steering wheel and the driver's door mirror are at lower screen left, which is HER RIGHT, with an empty seat and the driver's window between her and the wheel. In a left-hand-drive car she is in the front PASSENGER seat and nobody is driving. C4 (0:10.82, driver's seat, both hands on the wheel), D3 (looking out her left window) and D4 (0:28.40, in the left seat at the wheel) all make her the driver.
    - **V2b3, seen in the C2 flash f145.** The camera is behind her right shoulder and the wheel sits in front of the left seat, but her torso is well right of the wheel, in the passenger position, and she reaches across with her left arm to hold the wheel's right rim while looking back. (uncertain: she could be leaning hard, but it reads as passenger-seat steering.)
    - V2a3 (f148) checked: she is correctly behind the wheel. Not a problem.
  - Why it reads as an error: car anatomy, not stylisation. Anyone who drives sees "the car has no driver", and P2 holds on her face with the wheel in frame.
  - Visibility: HIGH for P2 in place (0.78 s, centred close-up). LOW for the 2-frame C2 flashes alone (at ×16).
  - Fix idea: P2: mirror horizontally (wheel on her left, screen right), then re-check the pencils' side, the patch side and the subtitle; or crop/paint out the wheel so the seat side reads ambiguously. V2b3: mirror, or re-stage her behind the wheel. The C2 flashes inherit the fix automatically, since C2 replays the film.
  - Evidence: zoom/f943.jpg (P2), zoom/p0_c2_car_flashes.jpg (f145 V2b3, f148 V2a3 OK, f154 P2), zoom/f266.jpg (C4, correct driver's seat)

- **0:02.75-0:03.29 (f66-f79) and 0:04.04-0:04.21 (f97-f101), C2 flashes of later shots**: the 1420 MHz roundel is garbled here as well ("1A2O MHZ" and similar glyphs at f98). Folded into the C1 roundel entry; LOW at this speed. Evidence: zoom/f98.jpg

- Note on C2 (0:01.90-0:07.24): every C2 frame is a 2-5 frame backward flash of a LATER shot, with VHS chroma tearing over it. Defects inside those flashes belong to the source shots and are best fixed there; the parts covering those ranges should report them. I checked the in-range flashes for anything grossly broken. Hands, limbs and agents' faces held up through the tear: the agent grab f78-f79 (zoom/p0_c2_grab.jpg), the runner f124-f127 and the agent line f66-f67 are all fine. Only the seat side (above) and the roundel text are worth carrying.

DONE: sheets 0000-0045 reviewed

### Part 1 (sheets 46-91)

### Part 1 findings: sheets 0046-0091 (0:30.67-1:01.29)


#### Passenger-seat / driver-geometry check (Jade's request)
- **D6 (0:32.36-0:33.66, f777-f807)**, `media/shots/D6/take_2_engraved_breath.mp4`: coherent. Camera is in the front passenger seat looking left; the car's nose is frame-right (dash, cluster and centre vents on the right); Jade is in the driver's seat, both hands on the wheel directly in front of her; the agent with the stopwatch is outside the window beyond her, which is the driver's window. The second agent is beyond the A-pillar, off the front-left of the car. Her hands are on the wheel at about 10 and 2, with five fingers each. Nothing here contradicts "she is the driver". Evidence: `zoom/f790.jpg`, `zoom/p1_f790_hands.jpg`.
- **D7 (0:33.66-0:36.30)**, `media/shots/D7/take_2_engraved.mp4`: coherent. Seen from outside her door, the car's nose is frame-left, the wheel is ahead of her, and the wing mirror and A-pillar are frame-left. Evidence: `zoom/f820.jpg`.
- **D8 (0:36.30-0:37.96)**, `media/shots/D8/take_3_engraved.mp4`: coherent reverse angle from her seat out through her window: the A-pillar and wing mirror are frame-right, which is forward. The agent's stopwatch hand has a thumb plus four fingers; the stub at top-left is the watch's pusher button, not a finger. Evidence: `zoom/f880.jpg`, `zoom/p1_D8_f875_watchhand.jpg`.
- **P2 (0:38.90-0:39.68)**, `media/shots/P2/take_2_engraved_eraser.mp4`: coherent. This is the agent's POV from outside her (driver's) door, matching D7: the nose of the car is frame-left; the wheel is bottom-left, directly ahead of her; the rear-view mirror is top-left on the windscreen; through the far (passenger) window you see the wing mirror and door handle; the rear seats are frame-right behind her. Evidence: `zoom/f936.jpg`.
- Summary: in 0:30-0:40 Jade is never shown in the passenger seat. The only seat or presence problem is P1 (the car looks empty), listed below.

#### Issues

- **0:37.96-0:38.90 (f911-f933) P1, and again 0:39.68-0:40.24 (f953-f965) P1b**, source `media/shots/P1/take_2_engraved.mp4`
  - What's wrong: the white Acura behind the agent looks EMPTY. Through the rear window and the side windows you see two bare front headrests and empty seats. There's no Jade (black hair, white jacket) in the driver's seat. The agent also stands well clear of the car on the roadside, not at her window, where D6, D7 and D8 placed him a beat earlier. In the cut, P2 (her in the car) sits between P1 and P1b, so the car reads as empty, then occupied, then empty.
  - Why it reads as an error: the car fills the left third of the frame for 0.94 s, and the beat is "he's about to shoot HER", yet she isn't in the car.
  - Visibility: MED (noticed on a second watch; P1b is pushed in on the agent and shows less of the car).
  - Fix idea: paint a dark-haired silhouette into the driver's seat (the engraved interior makes this a simple 2D paint), or reframe P1 tighter on the agent, as P1b does, so the car's windows leave the frame.
  - Evidence: `zoom/p1_f920_car.jpg`, `zoom/f920.jpg`
- **0:39.58-0:39.67 (f950-f952) P2**, source `media/shots/P2/take_2_engraved_eraser.mp4`. (LOW, uncertain)
  - What's wrong: in the last 3 frames of the shot, a solid white disc about 40 px across pops onto the headliner, just right of the blue-eraser pencil. It drifts down and right over those frames, and it isn't there in f948. It has no light source and reads as a stray blob from the generator (or a passing light that pops in instead of entering frame).
  - Visibility: LOW.
  - Fix idea: trim P2's last 3 frames (cut at f949), or paint the dot out.
  - Evidence: `zoom/p1_P2_dot_f948_950_952.jpg`
- **0:42.65-0:48.42 (f1024-f1162) R2_01-R2_13** (all 13), stills `media/shots/R2/engraved/kf_*_engraved.png`
  - What's wrong: one pencil (pink eraser) in her bun instead of the canon crossed pair. This is already logged in `docs/revisions/v6/eraser_audit.md` as "pre-canon stills", but it was never fixed.
  - Why it reads as an error: prop continuity breaks against D6, D7 and P2 just before. It's a minor tell at full speed (each still is about 0.45 s), but anyone freeze-framing the death montage will see it.
  - Visibility: LOW.
  - Fix idea: the frames are static, so paint the blue-eraser pencil in crossing each one (12 paint jobs).
  - Evidence: `zoom/p1_R2_heads.jpg` (head crops of all 13 stills)
- **0:43.72-0:44.18 (f1050-f1060) R2_03, 0:44.18-0:44.61 (f1061-f1070) R2_04, 0:45.56-0:45.95 (f1094-f1102) R2_07, 0:46.82-0:47.27 (f1124-f1134) R2_10, 0:47.70-0:48.15 (f1145-f1155) R2_12**, stills `kf_03picasso`, `kf_04bridge`, `kf_07riverwalk`, `kf_10gearsb`, `kf_12iceb`
  - What's wrong: the sleeve roundel text is AI-garbled instead of the canon "1420 MHz":
    - R2_03 reads about "1AEE / DIFE";
    - R2_07 about "ZUEB / ARIZ";
    - R2_10 about "AU3 / 9H2", which looks mirrored;
    - R2_12 about "1420 / MBC".
    
    R2_04 reads about "14?0 NHZ" (near-miss). R2_02, R2_05, R2_06 and R2_11 read correctly.
  - Why it reads as an error: classic AI pseudo-text on a canon patch, sitting next to stills where the patch reads correctly.
  - Visibility: LOW (the patch is small and each still holds about 0.45 s).
  - Fix idea: paint a clean "1420 MHz" roundel over each one (copy it from kf_11ferris).
  - Evidence: `zoom/p1_R2_roundels.jpg` (03, 04, 07, 10 and 02 for reference), `zoom/p1_R2_12_sleeve.jpg`
- **0:46.82-0:47.27 (f1124-f1134) R2_10 and 0:47.27-0:47.70 (f1135-f1144) R2_11**, stills `kf_10gearsb_engraved.png`, `kf_11ferris_engraved.png`. (LOW, uncertain)
  - What's wrong: in both she faces the camera, and the blue chest dot is correctly on her left chest (frame-right). But the "1420 MHz" roundel is on the frame-left arm, which is her RIGHT sleeve. Canon is the left sleeve, and the V2 notes fixed exactly this mirrored-jacket error in V2a3, V2c5 and V2f2. In R2_10 the roundel text also reads as mirrored or garbled.
  - Visibility: LOW.
  - Fix idea: paint the roundel off the right sleeve and onto the left one, or accept it.
  - Evidence: `zoom/p1_R2_10_numerals_roundel.jpg`, `zoom/p1_R2_full_11ferris.jpg`
- **0:45.95-0:46.37 (f1103-f1112) R2_08 (skydeck)**, still `kf_08skydeck_engraved.png`
  - What's wrong: the colour matte failed on most of her: the navy cargo pants, crop top, jacket body and lower arms are engraved grey/black hatching, and her skin is paper-white. Only the orange bands, headphones and blue dot stay in colour. In every other R2 still she is fully in colour.
  - Why it reads as an error: "Jade stays in colour" is the film's rule. A half-engraved Jade reads as a matte dropout, the same class as the v7 eraser bugs.
  - Visibility: LOW-MED (it is a whole-body change, but on screen for only 0.42 s).
  - Fix idea: re-run the engrave with a corrected matte (`media/shots/R2/engraved/matte/`), or hand-mask the pants.
  - Evidence: `zoom/p1_R2_08_colourloss.jpg`, `zoom/f1108.jpg`
- **0:35.08 (f842) D7 dialogue box**, `render/engine/modules/dialogue.js` (layer A_dialogue in `render/timeline/A.js`, not a generated clip)
  - What's wrong: for one frame the box reads "I reach for my ID t   s". The "s" of "show" is typed before the "o" of "to". In timing.json, "to" ends at 35.00 and "show" starts at 35.00, but each word types over 0.22 s, so the two words overlap. f841 shows "ID t" and f843 shows "ID to sh".
  - Why it reads as an error: a garbled, out-of-order typewriter frame in the film's only dialogue box. It's an engine glitch, not AI generation, but the same kind of thing a viewer would read as a glitch.
  - Visibility: LOW (one frame).
  - Fix idea: in the dialogue module, start each word no earlier than the previous word's typing finishes (or clamp typeTime to the gap between words).
  - Evidence: `zoom/p1_D7_typewriter_f841_843.jpg`
- **0:58.30-0:59.20 (f1399-f1420) C02_V2a2 (tyre close-up)**, source `media/shots/V2a2/take_1_engraved.mp4` (`render/timeline/C.js` row `[58.30, 59.20, 'V2a2', 1, 0.5, 1]`)
  - What's wrong: the Acura faces the wrong way. In C01_V2a1 just before it, and in C03 and C04 after it, the chase runs left-to-right: the Acura's nose and the sedans' headlights are frame-right. In this close-up the front bumper, headlight edge and wheel arch are frame-LEFT, so the car is pointing left. The sparks also spray forward (ahead of the car, to the left) instead of trailing behind it.
  - Why it reads as an error: it breaks the screen direction in a side-scroll chase section whose whole grammar is left-to-right. The spark direction reads as physically wrong.
  - Visibility: MED (the flip is felt on a cut-on-the-bar insert even if it isn't consciously named).
  - Fix idea: mirror the plate horizontally (it has no text or roundel). The sparks then trail correctly too.
  - Evidence: `zoom/f1405.jpg`, `zoom/p1_C01_f1370_cars.jpg`
  - Side note (not an AI error): the paper-coloured HUD is invisible over the white car body in this shot (`zoom/p1_C02_f1405_ghosthud.jpg`), so for 0.9 s the HUD seems to vanish. It could use an ink chip like TESS_CHIP.

#### Checked and clean (no report)
- D5cu (sunglasses close-up): its lens lyric is authored, and there are no face artifacts.
- D6: hands, fingers, wheel, stopwatch and pencils are stable, and the blink is natural.
- D7: the card stays in colour, both hands have five fingers, and the "1420 MHz" roundel is on the correct sleeve.
- D8: the card and stopwatch hold, and the motes are intentional.
- P4 and P5 motes, the P6 menu, and the R1 flash all behave as intended.
- R3 and R4: the backward replays of verse 1, S1 and C3/C4 are reuse. The ripple, echo ghosts, mirrored REWIND and judder are all intentional. I found no transient limb or prop errors in the replayed frames beyond what the source shots contain.
- C01: the car wheels and doors are coherent. The siren strobes are intentional.
- C03: she is at the wheel (driver), both hands are fine, the pencils hold and the headphones are canon.
- C04: the multiplying sedans aren't fused, and the wheel counts are correct.
- One-frame flashes or dropouts at cuts: none found in this range. The D8-to-P1 dialogue box collapse (f909-f911) is the box's close animation.
DONE: sheets 0046-0091 reviewed

### Part 2 (sheets 92-137)

### Part 2 audit: sheets 0092-0137 (1:01.33-1:31.96), v8 master 1080p

Context: Lake Shore Drive / Chicago = right-hand traffic, left-hand-drive car, so Jade should sit on the car's LEFT, wheel in front of her.

#### 1. **1:06.29-1:07.16 (f1591-f1611) C10_V2b3**, media/shots/V2b3/take_1_engraved.mp4 (in 0.0, rate 1)
- What's wrong: PASSENGER-SEAT STAGING. Camera is in the back seat looking forward; the steering wheel is on the LEFT (correct LHD), but Jade is in the RIGHT-hand (passenger) seat, twisted round to look back at camera, stretching her left arm across the console to grab the wheel. She is not in the driver's seat for the whole shot.
- Why error: she is the driver in the story (C06 just before shows her in the driver's seat holding the wheel with both hands); a passenger-seat grab reads as the generator misplacing her.
- Visibility: HIGH (0.9 s, she is half the frame).
- Fix idea: regenerate/re-stage with her in the left seat, hands on the wheel, glancing up at the flipping sedan through the windshield (or mirror-flip the plate so the wheel is on the right... no: flip makes the car RHD; re-stage instead).
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_f1593.jpg, .../zoom/p2_f1608.jpg

#### 2. **1:06.50-1:06.54 (f1596-f1597) C10_V2b3**, media/shots/V2b3/take_1_engraved.mp4
- What's wrong: mid-shot pop. For the first ~5 frames (f1591-f1595) Jade is fully engraved B&W; at f1596/97 she snaps to colour (orange band, blue dot, navy trousers) AND the framing jumps in the same frame (camera zooms in, sedan jumps position and angle, her pose shifts), so it reads as a 1-frame jump cut + matte switching on.
- Why error: every other shot keeps Jade in colour from the first frame; here the matte only engages part-way and coincides with a take discontinuity, so it reads as a glitch rather than the authored colour/B&W device.
- Visibility: MED (it's on the 3rd beat of a 0.9 s shot; noticeable on a second watch).
- Fix idea: trim the shot in to start at the post-jump frame (cut in ~0.22 s later and extend the tail) or paint the matte for f1591-f1595.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_c10_pop.jpg

#### 3. **1:06.50-1:07.16 (f1596-f1611) C10_V2b3**, media/shots/V2b3/take_1_engraved.mp4 + take_1_matte
- What's wrong: matte leakage. A ragged white cut-out patch with a wobbly black ink outline hangs round the flipping sedan's right edge and behind Jade's bun/neck (approx x1250-1540, y300-620 at 1080p), and in f1600 a stray wavy black matte-edge line runs from the wheel rim across the dashboard (x730-1100, y590-700). The colour layer also drags the sedan's underside into the "Jade" colour pass (it renders smoother/greyer than the engraved world).
- Why error: looks like a botched cut-out/sticker edge, not an authored effect.
- Visibility: MED (white blob behind her head is visible on pause; at speed it flickers).
- Fix idea: clean the take_1_matte (restrict to Jade's silhouette) and re-run the engrave pass, as was done for D3/D6/P2 in v7.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_f1600.jpg, .../zoom/p2_f1608.jpg

#### 4. **1:06.29-1:07.16 (f1591-f1611) C10_V2b3**, media/shots/V2b3/take_1_engraved.mp4
- What's wrong: canon break: only ONE pencil in her bun (single pencil, pinkish eraser), and NO orange headphones round her neck, in every frame of the shot. C06 a few seconds earlier has both pencils (pink + blue) and headphones.
- Why error: prop continuity; reads as the generator forgetting the character's kit.
- Visibility: MED (her head is large in frame; fans of the canon will spot it on rewatch).
- Fix idea: fold into the re-stage of finding 1; otherwise paint a second (blue-eraser) pencil and the headphones.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_f1608.jpg

#### 5. **1:06.75-1:07.16 (f1602-f1611) C10_V2b3**, media/shots/V2b3/take_1_engraved.mp4
- What's wrong: the flipping sedan is inside the cabin. As it rotates, its underbody overlaps the roof headliner and the top windshield frame (x250-1300, y0-130 in f1608): it is drawn in front of the car's own roof, i.e. passing through it.
- Why error: depth order is wrong (sedan should be outside the glass, clipped by the roof/A-pillars); reads as a compositing/generation mistake.
- Visibility: LOW-MED (busy frame; on pause it's clear).
- Fix idea: re-stage with the sedan fully outside the windshield, or mask the roof liner over it.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_f1608.jpg

#### 6. **1:05.75-1:06.25 (f1578-f1590) C09_V2b2**, media/shots/V2b2/take_1_engraved.mp4 (in 0.3, rate 1.3)
- What's wrong: the "near miss" is actually a hit: the flipping black sedan's nose comes down ON the white Acura's roof (f1579-f1590: its front bumper rests on / sinks into the roof just behind the windshield, with a spark at the contact) while the Acura's roof stays undented and both cars carry on. In f1588-f1590 the flipping sedan also goes rubbery: windows become white blobs, the body outline smears, a door handle floats as a white lozenge (x1300,540 in f1590).
- Why error: objects intersecting without consequence + a melting car body are classic generation artefacts; the shotlist calls for a sedan flipping OVER the car.
- Visibility: MED (the contact is visible at speed; the melt in the last 3 frames is pause-level).
- Fix idea: trim the shot to end at ~f1584 (before the roof contact/melt), or re-generate with clearance above the roof.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_c09_flip.jpg, .../zoom/p2_f1590.jpg

#### 7. **1:05.79-1:06.25 (f1579-f1590) C09_V2b2** (uncertain, LOW)
- What's wrong: two Interstate-style route shields on the left verge carry illegible garbled glyphs.
- Why error: unauthored AI text in-world; minor because they are tiny.
- Visibility: LOW.
- Fix idea: paint blank or authored numbers (e.g. "41" for Lake Shore Drive / US-41).
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_c09_signs.jpg

#### 8. **1:07.16-1:08.06 (f1612-f1633) C11_V2b4**, media/shots/V2b4/take_2_engraved.mp4 (in 0.2, rate 1)
- What's wrong: the falling lamppost goes THROUGH the Acura. Its base is in the foreground bush, its shaft is drawn over the car's rear door and rear wheel, but its glowing head comes to rest BEHIND the car against the far railing/kiosk (f1625, f1633). The car sits motionless and undamaged the whole time (no dodge).
- Why error: a solid pole can't be in front of the car at one end and behind it at the other without passing through the body; reads as a 2D layering mistake. Shotlist intent is "a lamppost falls (dodge)".
- Visibility: MED (the pole across the car is the subject of the shot; the depth contradiction is noticed on a second look).
- Fix idea: re-stage so the pole falls into the lane ahead of the car (car swerves), or mask the shaft behind the car body.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_f1625.jpg, .../zoom/p2_f1633.jpg

#### 9. **1:08.33-1:08.94 (f1640-f1655) C12_V2b4**, media/shots/V2b4/take_2_engraved.mp4 (in 1.2, rate 1.2)
- What's wrong: the fallen lamp head lands at the Acura's rear wheel; the spark burst replaces the rear wheel entirely and the rear door/quarter panel dissolves into scratchy hatching (f1644-f1647: car has one wheel, the body behind the B-pillar breaks up); by f1648-f1654 a white starburst shreds the whole car body into spikes, the front half vanishes, and C13 then cuts to an intact wheel close-up. The car still rolls on.
- Why error: the car body melting/losing a wheel is a generation artefact, not a scripted crash (she "dodges").
- Visibility: MED.
- Fix idea: trim C12 to end before ~f1642, or swap to a take where the lamp lands clear of the car.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_f1646.jpg, .../zoom/p2_c12_melt.jpg

#### 10. **1:10.71-1:11.58 (f1697-f1717) C15_V2b6**, media/shots/V2b6/take_1_engraved.mp4 (in 1.6, rate 1.2)
- What's wrong: top-down "closing trucks": the two tractor units are mangled. Each cab's inner side stretches into a long bent, arm-like neck that runs down alongside the Acura and "grips" its wing mirrors (sparks where they touch); the cabs fold in to meet in front of the car's bonnet, so the trucks are physically fused around the car rather than two lorries closing a gap.
- Why error: no real tractor can bend like that; reads as AI body-merge between three vehicles.
- Visibility: MED (top-down, high contrast; the shapes read wrong even at speed, the detail on pause).
- Fix idea: re-generate with rigid tractor units (or composite two straight trucks and the car as separate elements); otherwise shorten to the first 6-8 frames.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_c15_cabs.jpg

#### 11. **1:12.04-1:12.46 (f1729-f1739) C16_V2b6**, media/shots/V2b6/take_1_engraved.mp4 (in 3.5, rate 1.6)
- What's wrong: after the Acura squeezes out ahead, the two tractor cabs close and FUSE into a single object: by f1734-f1739 they become one flat T/winged shape with a single central spine, a roof lamp on each "wing", the two trailers hanging off it like one vehicle.
- Why error: two separate lorries melting into one is a generation morph, not a staged collision (no crumple, no impact).
- Visibility: MED (it's the payoff of the trap and the shot is held; the fused shape is legible at speed).
- Fix idea: end the shot ~f1730 (as the car clears), or composite a hard collision (flash/smash cut) over the merge.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_c16_merge.jpg

#### 12. **1:17.13-1:17.50 (f1851-f1859) C21_V2c5**, media/shots/V2c5/take_2_engraved.mp4 + take_2_matte (in 0.3, rate 1.2)
- What's wrong: steering-wheel rim pops. For 9 frames the matte grabs the top of the rim: it turns from engraved line-art to a solid glossy black colour arc that is thicker and sits higher/larger than the engraved wheel beneath it (the held arc no longer lines up with the rest of the wheel, so it reads as a second, floating rim), then snaps back to engraved at f1860.
- Why error: a prop changing rendering style and size for a third of a second is a matte flicker, not the colour/B&W device (which is for Jade, not the car).
- Visibility: MED (hero shot, the wheel is centre frame; the pop on and off is noticeable).
- Fix idea: clean take_2_matte so the rim stays world (engraved) in f1851-f1859.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_c21_rim.jpg, .../zoom/p2_c21_wheel.jpg

#### 13. **1:16.90-1:18.66 (f1846-f1888) C21_V2c5** (uncertain, LOW)
- What's wrong: driving geometry: the speedometer (the shot's subject, "needle pins") sits in the middle of the dashboard, well to the RIGHT of the wheel, with no instrument cluster behind the wheel. Seat side is correct (LHD, she is on the left, door mirror to her left).
- Why error: Acura sedans have the cluster behind the wheel; a lone centre gauge reads a little "generated" but some cars have centre gauges, so this is minor.
- Visibility: LOW.
- Fix idea: leave, or paint a cluster behind the wheel; not worth a re-gen alone.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_f1850.jpg

#### 14. **1:19.58-1:20.44 (f1910-f1930) C23_V2c6**, media/shots/V2c6/take_1_engraved.mp4 (in 1.5, rate 1.2) (uncertain)
- What's wrong: driver's POV through the windshield, but the car's two headlamps are drawn ON TOP of the bonnet just below the windscreen, as glowing domes with starbursts, so the bonnet looks like it has headlights facing the driver. The windscreen frame also has no A-pillar/dash continuity (the frame is a single U shape, no dashboard, no mirror).
- Why error: from inside the cabin you can't see the headlamps; it reads as the generator pasting "headlights" onto the visible hood.
- Visibility: LOW-MED (the two bright starbursts are prominent, but the eye reads them as glare at speed).
- Fix idea: paint the domes out (leave a beam glow on the grating ahead), or accept as engraving stylisation.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_f1915.jpg

#### 15. **1:23.98-1:24.86 (f2016-f2036) C27_V2d2**, media/shots/V2d2/take_4_engraved_blue.mp4 (in 2.0, rate 0.6, frameBlend)
- What's wrong: canon break: NO orange headphones round her neck in any frame; in their place is a pale-blue scarf/hood collar. (Pencils are fine: pink + blue, crossed through the bun.) The 1420 MHz patch reads as a garbled red badge with squiggle "text".
- Why error: the headphones are in every other close shot (C06, C21 hero, C29 next); dropping them on the hero mid-air close-up reads as the generator forgetting the costume.
- Visibility: MED (big close-up on "And now I'm", held 0.9 s).
- Fix idea: paint orange headphones over the blue collar (pixel pass like the v6/v7 eraser fixes), or regenerate the keyframe with the headphone ref.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_c27_jade.jpg, .../zoom/p2_f2022.jpg

#### 16. **1:23.10-1:25.29 (f1995-f2047) C26_V2d1 -> C27_V2d2 -> C28_V2e1**, media/shots/V2d1/take_1_engraved.mp4, V2d2/take_4_engraved_blue.mp4, V2e1/take_1_engraved.mp4
- What's wrong: screen direction flips through the jump. C26 the car launches up and to the RIGHT; C27 (mid-air) its nose points LEFT; C28 it lands nose RIGHT. The car model also changes between shots (C27 is a 2001-style TL with round-ish lamps; C28 is a later TL/TSX with a different grille, lamps and plate position).
- Why error: a car reversing direction in mid-air for one shot and changing model reads as stitched-together generations, not a story beat. (Seat side in C27 is correct: nose-left shows the car's left/driver side and she leans out of the front driver window.)
- Visibility: MED (three consecutive hero shots on the drop; the direction reversal is felt at speed).
- Fix idea: hard to flip C27 without putting her in the passenger window; better to flip C26 + C28 (no text in either except HUD/lyric overlays, which are composited after) so all three read nose-left.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_c26_leaf.jpg, .../zoom/p2_f2022.jpg, .../zoom/p2_c28_car.jpg

#### 17. **1:23.10-1:23.98 (f1995-f2015) C26_V2d1**, media/shots/V2d1/take_1_engraved.mp4 (in 2.0, rate 1) (uncertain)
- What's wrong: instead of launching off the leaf, the car sits pinned at the top of the far leaf for the whole shot: its front wheel rests on the leaf tip, rear wheel in mid-air, the leaf's girders pass behind/through the car's underside, and a spark fountain shoots from the nose as if it is welded there. It never leaves the leaf.
- Why error: reads as a stuck/merged object rather than a jump; physics breaks in a way that looks like an error.
- Visibility: LOW-MED (it is short and the spark draws the eye).
- Fix idea: use an earlier/later segment of the take where the car is clear of the leaf, or speed-ramp so it reads as launch.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_c26_leaf.jpg

#### 18. **1:27.08-1:27.75 (f2090-f2106) C30_V2e3**, media/shots/V2e3/take_1_engraved.mp4 (in 0.0, rate 1.2)
- What's wrong: the skyline behind the bridge has a US-Capitol-style dome (plus a cupola tower), i.e. Washington DC, not Chicago. It sits left of the raised leaf for the first ~0.7 s, until the camera pans off it.
- Why error: the story places this on the Chicago River; a Capitol dome is a stock "city" hallucination, and Chicago viewers will spot it.
- Visibility: LOW-MED (small, mid-frame, engraved white on grey).
- Fix idea: paint the dome out (replace with a flat-roof block), or crop/scale to push it out of frame.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_c30_sedans.jpg

#### 19. **1:27.75-1:28.38 (f2106-f2120) C30_V2e3** (uncertain)
- What's wrong: the two airborne agent sedans fly into the raised bridge leaf and pass behind/through it: the upper one is drawn in front of the leaf's lower edge in f2106 and then disappears behind the leaf grating by f2109-f2114, with no impact on the leaf; the lower one dissolves into the white spark burst at the road.
- Why error: an object occluded by a plane it was in front of a few frames earlier reads as a depth error.
- Visibility: LOW (busy background; the eye follows the Acura).
- Fix idea: trim C30's tail by ~6 frames or accept; low priority.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_c30_sedans.jpg

#### 20. **1:28.42-1:29.26 (f2122-f2142) C31_V2f1**, media/shots/V2f1/take_1_engraved.mp4 (in 0.0, rate 1)
- What's wrong: (a) the white car that should be Jade's Acura is a different, boxier 80s/90s sedan AND carries a siren starburst on its roof like the agents' cars, so it reads as a white police car/taxi joining the pack, not her car being chased. (b) The pack is a dense overlapping mass: several black sedans interpenetrate (bonnets inside the car ahead, e.g. centre cluster x450-1100, y560-760) and strobes sprout from bonnets and wings, not just roofs. (c) The skyline again has a domed classical capitol building centre (x840-1060, y420-530).
- Why error: the hero car changing model and gaining a siren is identity drift; merged cars are a standard generation artefact.
- Visibility: MED for (a) (her car is the only white thing in frame); LOW for (b) and (c).
- Fix idea: paint out the white car's roof strobe (and ideally the grille to Acura) or composite the C30 Acura in its place; the pack overlaps are acceptable at 0.9 s.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_f2130.jpg, .../zoom/p2_c31_cars.jpg

#### 21. **1:29.29-1:31.46 (f2143-f2195) C_V2f_car**, tools/v4B/car/car_shot.js (wide: media/shots/V2f3/take_1_engraved.mp4 / kf_wide_b_fix_engraved.png; close: media/shots/V2f4/kf_close_b2_engraved*.png)
- Driving staging check: seat side CORRECT (left-hand drive, Jade in the left seat, both hands on the wheel at ~10 and 2, Acura badge on the boss, centre stack to her right, passenger seat back to frame right). Road ahead is empty and curving; nothing contradicts right-hand traffic. Both pencils (pink + blue) and orange headphones present. No passenger-seat problem in this shot.
- What's wrong: the rear-view mirror has NO MOUNT and no windshield to hang from. In the wide there is no windscreen header, roof liner or stem; the mirror floats in the night air at road level, framed by the overpass/gantry beyond. During the push (f2186-f2195) the camera travels past the wheel and the mirror stays suspended outside the car among the overpass girders. Then at f2195-f2196 the close still cross-fades in with a completely different context: a roof liner, sun-visor clips and a stem holding the mirror. So the mirror appears outside the car, then is suddenly inside it.
- Why error: this is the very "impossible mirror" Jade wants gone from D3: the mirror is not physically attached to anything, so the over-the-shoulder restage still reads as a pasted-on mirror.
- Visibility: MED-HIGH (it's the subject of the push and is centre frame for 3 s; the missing stem plus overpass-behind-mirror is clear at speed once you look for it).
- Fix idea: paint a windscreen header + roof liner + stem into the wide (matching the close still's liner/visor clips) above the mirror, so the push travels under the roof; or start the cross-fade to the close still earlier (before f2188).
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_f2150.jpg, .../zoom/p2_v2f_handover.jpg

#### 22. **1:29.29-1:30.96 (f2143-f2183) C_V2f_car** (LOW)
- What's wrong: the cabin is incomplete: no right A-pillar, no windscreen top edge, and the passenger seat back is a flat featureless upright slab (x1620-1920, y490-1080), as is her own seat back at bottom-left. The car reads as an open-topped box.
- Why error: AI interior simplification; adds to the floating-mirror impression in finding 21.
- Visibility: LOW.
- Fix idea: fold into the finding-21 paint pass (header + right pillar).
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_f2150.jpg

#### 23. **1:31.50-1:31.96 (f2196-f2207) C_V2f_car** (uncertain, LOW)
- What's wrong: the mirror image shows the road and pursuing sedans directly, with no rear window frame, rear headrests or C-pillars round them, and the TVA plates (1729, 4104, 4096) read left-to-right instead of mirror-reversed.
- Why error: a real rear-view mirror frames the scene through the rear window and reverses text. The readable plates are authored and intentional (the text is the point), so this is a pedant's note only; the missing rear-window frame is the bit that reads "generated".
- Visibility: LOW.
- Fix idea: optional: lay a faint rear-window outline/headrest silhouettes into the mirror glass; keep plates readable.
- Evidence: /tmp/claude-1000/-home-jade-Documents-rewind-take-two/bf7fbd61-c3f7-4db9-8473-202d9a92dac7/scratchpad/zoom/p2_v2f_handover.jpg

#### Shots checked with nothing to report (sheets 0092-0137)
C04_V2a4 / C05_V2a5 (to 1:02.30), C06_V2a3 (driver's seat, LHD, both pencils + headphones: OK), C07/C08_V2b1 (tilting-lane platforms: Escher, intended), C13_V2a2 (tyre close-up), C14_V2b5, C17_V2c1, C18_V2c2 (bridge rising), C19/C22_V2c3 (C22 J-turn shows the car spinning to face away; plausible as a skid), C20_V2c4, C24_V2c7 (tessellated fleet: intended), C25_V2c8 (gate crash: debris passes in front of car, coherent), C29_V2e2 (driver's seat LHD, both pencils + headphones: OK). No one-frame black/white flashes between shots in this range; all cuts land clean.

DONE: sheets 0092-0137 reviewed

### Part 3 (sheets 138-183)

### Part 3 findings (sheets 0138-0183, 1:32.00-2:02.62)

#### 1:32.00-1:32.79 C_V2f_car tail (rear-view mirror) — driving coherence check
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

#### Summary (part 3)
HIGH: 0
MED: 3. B2_chasm pose pop and faceless frame at f2331-2334. B2_G2 Jade drawn over the agent's arm at f2451-2458 (MED-HIGH). B2_G2 the same overlap at f2428-2430. C33_V2h1 floating orange block at f2253-2257 is borderline MED.
LOW / LOW-MED: E4a headless frame f2894; E2_08_kick ink blots; B2_glance rigid strap and garbled 1420 patch; B2_V2n1 garbled ◀◀ button; C33_V2h1 detached hand f2248; B2_G1 see-through hand; B2_chasm melting feet; plus uncertain items (B2_leap and B2_chasm jacket flip, B2_corner_in float, B2_pistol muzzle, CONTINUE double, V2g1 train, non-reversed mirror plates).
Car (V2f tail in range, f2208-2226): rear-view mirror shot, geometry coherent; no passenger-seat or steering content in this range.

DONE: sheets 0138-0183 reviewed

### Part 4 (sheets 184-229)

### Part 4 findings: sheets 0184-0229 (2:02.67-2:33.29)

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

#### Checked and judged intentional / clean (not reported)
- E7_02_leap / E7_04_chasm white or tinted falling Jade copies (f3267-3268, f3290-3295): ghostpop layers (v7 "ghost falls" canon).
- E7 multi-coloured Jade swarms, ribbons, motes: intentional.
- "HILBERT HOTEL" sign (E7_04/E7_05/E7_06): legible and spelled correctly, and it stays stable.
- E8a/E8b/E8c TVA ALERT text: authored, typed cleanly. The E8 negative agents are identical by design.
- G1 (f3384-3468): two pencils in the bun, headphones, 1420 MHz patch and hands all stable, no limb errors.
- G2 (f3469-3511): pencil pulled from bun, hair falls, second pencil drifts free. Consistent with canon; hands and legs fine.
- G4 diorama assembly (3D, procedural): no glitches beyond intended crank/assembly.
- C1_hold co-op plate book titles (Strogatz, Greene): authored, legible.

DONE: sheets 0184-0229 reviewed

### Part 5 (sheets 230-275)

### Part 5 findings: sheets 0230-0275 (2:33.33-3:03.96), M1 / V3S / M2 / M3 / F1-F4

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

### Part 6 (sheets 276-321)


### Part 6: sheets 0276-0321 (3:04.00-3:34.62), F5a-F8 + start of O1

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

#### Notes / checked clean
- Three-legs example: NOT in this range. I checked every Jade full-body shot (F5a-c, F6a, F6c, F7_01/02/04/07m/08/10-13, F8) and found no extra or fused legs.
- Car mirror example: not in this range (no car shots in F5-O1).
- F6a: F7_12 (f5017-f5027) reuses F6a take 4 at in 0.4, which is the clean early part with no double exposure.
- These are authored and clean: the F6b/F7_03 penrose_march sprite agents (identical suits are fine); the 194.10 "clunk" flash; F7_05/F7_09 melting clock and its burst; F7_07m hand-touch triangle-mesh dissolve and merge; F7_08 colour ghost trail and rewind paint; F7_11 giant pencil; F7_13 floating pose (legs, strap, sneakers stable); O1 3D agents and the variance report typing (f5080-f5151).
- Shot-head flashes at each cut are the EDL's authored flash fx, not dropouts. I found no black or one-frame dropouts between shots.
- Severity tally: HIGH 0 / MED 4 (F6a frame-blend smear, F6c second pencil, F7_02 roundel text, F7_10 pencil count) / LOW 5 (F6a headphones, F5b stub pencil (uncertain), F7_04 roundel, F7_05 walkers (uncertain), F8 roundel)

DONE: sheets 0276-0321 reviewed

Note on evidence frame numbers: the single grabs zoom/f<N>.jpg (f4416, f4500, f4520, f4532, f4580, f4596, f4605, f4614, etc.) were taken with -ss N/24+0.01, so each one actually shows frame N+1. I verified this by diffing against a PyAV decode. Everything in zoom/p6seq/ and the montages built from it (F6c_*, F7_*, F8_*) uses the exact decode index, which matches the sheet labels. The one-frame offset doesn't change any finding.

### Part 7 (sheets 322-367)

### Part 7 findings (sheets 0322-0367, 3:34.67-4:04.04)

Sheets 0322-0328 (O1 penrose_loop + variance report): three.js render plus authored typed/untyped TVA text ("CASE 4,098", "TIMELINE NOW CANON" stamp). Nothing to report.

Sheet 0328 f5255 (first O2 frame) is a cream white-out. That is the authored fx flash in F_edl.json (dur 0.12), not an error.

- **3:39.38-3:39.92 (f5265-f5278) O2**, media/shots/O2/take_3_engraved_dered_blue.mp4 (F_edl.json, clip_in 0.0)
  - What's wrong: while she pins the second pencil into her bun, her RIGHT hand (screen right) dissolves for about 14 frames. At f5260-f5263 it holds the second pencil horizontally. From f5264 it melts under the pencil, the pencil keeps sliding into the bun with nothing holding it, and from f5267 to f5278 the sleeve ends at the ribbed cuff with only a faint pink smear against the hair. The hand pops back fully formed at f5279-f5280. Her left hand stays fully drawn the whole time.
  - Why it's an error: a hand-on-head pose seen from behind should show both hands on the hair. Here one arm ends in a stump at the cuff, a classic generation dropout, not a stylistic choice.
  - Visibility: MED (the arms are raised at the centre of frame for about 0.4 s, so a second watch catches the stump)
  - Fix idea: start O2 at about f5280, when both hands are visible and the pencils are already crossed, or paint the right hand back in for f5266-f5278.
  - Evidence: zoom/p7_o2_pencil_insert_5260-5268.jpg (f5260, 62, 63, 64, 65, 66, 67, 68), zoom/p7_o2_righthand_5266-5280.jpg (grid of f5266, 68, 70, 72, 74, 76, 78, 79, 80), zoom/f5272_head.jpg, zoom/f5278_head.jpg

- **3:40.75-3:41.33 (f5310-f5312) O2**, media/shots/O2/take_3_engraved_dered_blue.mp4
  - What's wrong: the door hardware morphs as she grabs it. Up to f5310 the door has a round brass knob over a keyhole plate, and her fingers close around the knob. From f5312 on, the knob is gone and she holds a flat, vertical lever/plate handle on the same escutcheon. It stays a flat plate as the door opens (f5312-f5346).
  - Why it's an error: a prop changes type when the hand touches it, which is typical AI interpolation. Nothing in the treatment calls for it.
  - Visibility: MED (the knob is at the centre-left of a static wide shot right at the "Dissertation defense, 9:00" beat)
  - Fix idea: trim or crossfade past it, or paint the round knob through f5312-f5346 (or paint a lever plate from the start of the shot).
  - Evidence: zoom/p7_o2_knob_morph_5300-5332.jpg (crops of f5300, 02, 04, 06, 08, 10, 12, 14, 16, 20, 26, 32), zoom/f5320_door.jpg

- **3:40.25-3:40.42 (f5286-f5290) O2** (uncertain, LOW)
  - What's wrong: as her arms drop from the bun to her sides, her right hand smears into the dado rail and window mullion for 2-3 frames (f5288 is a blurred blob with no fingers), and her left hand briefly grips the door-frame edge (f5286).
  - Why it's an error: hands melt into scenery during fast motion. It reads as interpolation mush, not motion blur.
  - Visibility: LOW
  - Fix idea: leave it, or speed-ramp through f5284-f5292.
  - Evidence: zoom/p7_o2_armsdown_5282-5290.jpg (f5282, 5286, 5288, 5290)

Sheets 0334-0349 (O3_black, O4): an authored typewriter credit crawl, the hand-lettered "never stop." with its pencil cursor, the rolling ITERATION counter 4,098 to 4,112 and a fade-out. No AI imagery, nothing to report. The O2 to O3 cut at f5347 is a clean hard cut to black.

Sheets 0349-0354 (PC1_door, tools/sectionF/modules/hilbert_door.js with media/shots/PC/door_leaf.png, door_frame.png, doorway.jpg, press_hand.png): the "HILBERT HOTEL" lettering and the key/infinity crest read correctly at full res (zoom/f5604_door.jpg). The doorman's glove presses the brass bell plate and withdraws (zoom/f5612_hand.jpg). The leaf swings in true perspective and the text is not mirrored. Nothing to report.

Sheets 0354-0366 (PC2_lobby, tools/sectionF/modules/hilbert_lobby.js): the ledger names are canvas text and spelled correctly (Escher, Penrose x2, Kandinsky, Dali, Klimt, Mobius, Banach, Tarski, Hilbert). The faceless tinted figures at the far end of the queue are the intentional ghost0-6 sprites (zoom/p7_pc2_sprites_contact.jpg). The committee idle loops (media/shots/PC/idle/*) are clean at the size they play (zoom/p7_pc2_idle_others.jpg). The video ends cleanly on f5856.

- **3:56.4-4:04.0 (f5673-f5856, repeats every 5 s) PC2_lobby**, the protagonist's idle loop media/shots/PC/idle/jade/f_0055-f_0099 (src media/gen/v5_coda2_idle_jade/take_1.mp4) (uncertain about visibility, LOW)
  - What's wrong: while she raises her hand to the headphones, her hair grows a high top-knot/ponytail above the crown (loop frames 59-75) and then flattens back. The "1420 MHz" roundel on her left sleeve fades to a bare outline (loop frames 55-95) and pops back as the arm drops (frame 99).
  - Why it's an error: hairstyle and badge morphs during a 5 s idle are generation drift, not staging. Canon is a loose bun plus a roundel that is always there.
  - Visibility: LOW (she is about 250 px tall at the front of the queue, and the dialogue box covers her chest for much of the shot)
  - Fix idea: limit the idle to loop frames 1-50 and 100-120 (ping-pong), or swap the take.
  - Evidence: zoom/p7_pc2_idle_jade_55-111.jpg, zoom/p7_pc2_idle_jade_loop.jpg, zoom/p7_pc2_headphones_5822-5854.jpg

DONE: sheets 0322-0366 reviewed (0367 does not exist; index.tsv ends at 0366 / f5856)
