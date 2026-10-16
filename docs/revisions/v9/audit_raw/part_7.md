# Part 7 findings (sheets 0322-0367, 3:34.67-4:04.04)

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
