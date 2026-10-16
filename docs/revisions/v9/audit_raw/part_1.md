# Part 1 findings: sheets 0046-0091 (0:30.67-1:01.29)
PROGRESS: last sheet reviewed = sheet_0091 (complete)


## Passenger-seat / driver-geometry check (Jade's request)
- **D6 (0:32.36-0:33.66, f777-f807)**, `media/shots/D6/take_2_engraved_breath.mp4`: coherent. Camera is in the front passenger seat looking left; the car's nose is frame-right (dash, cluster and centre vents on the right); Jade is in the driver's seat, both hands on the wheel directly in front of her; the agent with the stopwatch is outside the window beyond her, which is the driver's window. The second agent is beyond the A-pillar, off the front-left of the car. Her hands are on the wheel at about 10 and 2, with five fingers each. Nothing here contradicts "she is the driver". Evidence: `zoom/f790.jpg`, `zoom/p1_f790_hands.jpg`.
- **D7 (0:33.66-0:36.30)**, `media/shots/D7/take_2_engraved.mp4`: coherent. Seen from outside her door, the car's nose is frame-left, the wheel is ahead of her, and the wing mirror and A-pillar are frame-left. Evidence: `zoom/f820.jpg`.
- **D8 (0:36.30-0:37.96)**, `media/shots/D8/take_3_engraved.mp4`: coherent reverse angle from her seat out through her window: the A-pillar and wing mirror are frame-right, which is forward. The agent's stopwatch hand has a thumb plus four fingers; the stub at top-left is the watch's pusher button, not a finger. Evidence: `zoom/f880.jpg`, `zoom/p1_D8_f875_watchhand.jpg`.
- **P2 (0:38.90-0:39.68)**, `media/shots/P2/take_2_engraved_eraser.mp4`: coherent. This is the agent's POV from outside her (driver's) door, matching D7: the nose of the car is frame-left; the wheel is bottom-left, directly ahead of her; the rear-view mirror is top-left on the windscreen; through the far (passenger) window you see the wing mirror and door handle; the rear seats are frame-right behind her. Evidence: `zoom/f936.jpg`.
- Summary: in 0:30-0:40 Jade is never shown in the passenger seat. The only seat or presence problem is P1 (the car looks empty), listed below.

## Issues

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

## Checked and clean (no report)
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
