# Part 0 findings: sheets 0000-0045 (0:00.00-0:30.62)
PROGRESS: last sheet reviewed = sheet_0045 (complete)

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
