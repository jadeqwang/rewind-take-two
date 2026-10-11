# Rough cut v1 review

Reviewed file: `deliverables/wip/rewind_roughcut_v1_preview.mp4` (960×540, 24 fps, 227.96 s, with the sound-design mix).
Reviewed 2026-10-11 by the QA/critic agent.

Section F was polished after v1: rainbow arcs removed, O4 text enlarged, the 3D F6b beat replaced by a 2D payoff at 192.34–195.42, and the F1 colour leak fixed.
Everything from 169.40 s on was therefore re-checked against **fresh stills from the current timeline** (`render.mjs --stills`, every 0.5 s), not the v1 file. F findings below refer to the current timeline unless marked "v1".

## How this was reviewed

- **Visual pass.** I extracted 929 frames: every 0.25 s for 0–30 s, every 0.5 s after that, and ±1 s at 0.25 s steps around every shot-list boundary. They went onto 39 labelled contact sheets, plus 6 sheets of current-timeline F stills and about 25 zoom crops. I looked at every sheet.
- **Automatic checks.** One full decode of all 5,471 frames measured:
  - luma, to find black and white frames;
  - a red-pixel mask (hue near 0°, saturation over 0.45; Jade's orange #F08A24 is excluded);
  - frame difference, which detected 165 cuts. I compared those cuts with `timing.json` beats, the 13+13 vocal chops and the section boundaries.
- **Outside model.** `google/gemini-3.8-flash` (Cloudflare unified catalog, the same call shape as the rare-earth review) watched the cut with audio, in two forms:
  - four overlapping chunks: 0–60, 55–115, 110–170 and 168–228 s;
  - the whole film in one request.

  The input was 480×270 at 380 kbit/s with mono audio, plus a burned-in "FILM TIME" strip under the picture so its timestamps are absolute. Usage was 45.7k input and 14.6k output+thinking tokens. The cost is about $0.05–0.10 at Flash list prices; the model isn't in our local catalog, so `spend.py` has no price for it. Raw answers are in `media/reviews/roughcut_v1/gemini_raw.md`. I treated it as one opinion: where I verified a claim, I say so, and its wrong claims are listed at the end.

---

## (a) Top 10 fixes, in priority order

1. **110.79–112.96: Jade has no face (C).** In V2m, and in the frozen V2m plate behind the CONTINUE? panel, her face is a blank white oval with no eyes or mouth. It shows for about 2 s at the climax of Verse 2 and is the worst broken frame in the film. **Fix:** regenerate V2m from a keyframe with the face drawn (side 3/4, eyes squeezed shut on impact). Or re-engrave with Jade's matte protecting the face; it looks like the engrave pass blew the face to paper. Re-freeze V2n from the new take.
2. **2.40–4.90: the C2 teaser gives away the colour payoff, and the HUD digit is clipped (B).** About 2.5 s of full-colour final-drop frames (the colour flood, the Bean, the melting clock, Klimt) play in the first 5 seconds. The film's biggest reveal, the world turning to colour at 169.40, is shown before the title. Separately, the HUD chip crops the counter to `ITERATION 4,09` for all of C2 (2.0–7.2), so the roll 4,096 → 4,097 can't be read. **Fix:**
   - Push every C2 flash sourced after 146.32 through the engrave pass, with Jade's matte kept in colour, or swap those sources for B&W ones such as the M-diorama, the ghost ring and the bridge jump. Keep the flashes at 2–3 frames.
   - Widen the HUD chip by about 20 px.
3. **113.89–119.44 and 127.88–128.76: the ghosts don't read as Jades (D).** The film's central mechanic is that ghosts are the committee. In E2 the frozen iterations are flat colour blobs. In E2c (117–119.4), the "constellation of 13 Jades" reads as coloured smudges around a clump of agents. At 128.0 the gold twin is a fully opaque yellow-jacket girl, and Gemini read her as a new character. **Fix:**
   - Re-bake the ghost sprites in the style of F6c and F8, which read perfectly: a crisp line-art Jade, a translucent hue fill at about 0.6, a bright outline and face detail.
   - Make the E2c ghosts at least 2× bigger (≥ 25% of frame height), even if the ring shot gets tighter.
   - Render the E5b twin at about 60% opacity with a glow outline.
4. **Lyrics that are missing or illegible (A, C, D, E).**
   - **30.16–31.92 (A).** "men in shades and suits" exists only in the lenses and can't be read even at full resolution. Fix: drop it to the lower third.
   - **98.28–104.22 (C).** "I zigzag across / the field of grass" is orange type laid into the grass hatching and is covered by agent sprites. Fix: lift it off the ground plane, or add a paper-coloured halo and draw it above the agents.
   - **119.44–122.95 (D).** E3 "Rewind" is orange text sitting on her orange jacket band. Fix: move it below the band or set it in ink, and add the period so it matches E4's "Rewind.".
   - **161.00–165.18 (E).** M2's "I'm speeding down Lake Shore, I dreamt" is painted on the Möbius road at about 8 px and is unreadable. Fix: scale the road type ×3, or add a lower third.
   - **168.12–169.40 (E).** M3's "…it couldn't **trace**" ends in a grey smear; the payoff word never resolves. Fix: draw the word in dotted line first, then let the line wander off.
5. **12.60–19.64: S1 is a 7-second static selfie right where the hook has to hold (A, with the singing director; the same treatment affects E3 at 119.44 (D) and V3S at 153.98 (E)).** The fisheye framing with the extended selfie arm reads as a phone vlog, not a drawing. The headphones are pink, not canon orange. Gemini's most repeated complaint (3 of 5 passes) was "webcam talking head breaks the style". Keep Jade's likeness, but:
   - push in about 1.3× to crop the selfie arm;
   - add the pencil-line grain used in E3;
   - shift the headphones to orange;
   - in S1, cut away for one bar on "my dissertation" (16.29), for example a 1.7 s Bean-reflection insert with the headlights on LSD, so the first verse isn't a single 7 s hold.
6. **40.65–42.38: the tape stop and pause menu (B).**
   - In P5 (40.67–41.38) the 2.39 letterbox bars invert with the frame, leaving a grey band across the top.
   - In P6 the selected menu item turns orange on top of her orange jacket band, so RESUME and REWIND can't be read (41.42–42.37).

   **Fix:** keep the letterbox bars pure black (exclude them from the invert), or drop the letterbox at 40.24 when P4 goes full frame. Put the menu on a dark ink panel and show the selected item in paper-white with the ◀◀ cursor.
7. **Red-audit failures (C, E, F, A).**
   - **94.06–98.28 (C).** The race split timer is red (`+0.38`). Make it white, then green.
   - **167.0–169.4 (E).** M3's colour bloom paints the doors and blocks crimson.
   - **211.64–215 (E).** O1's colour pass gives the central building brick-red.
   - **F, current timeline.** Brick-red buildings in F1 (170–173). Red Kandinsky rings at F7_04 and F7_07 (200.3–205.5). **Red chest patches on Jade's jacket in F8 (209.9–211.6)**, which also makes her off-model.
   - **28.40–30.16 (A).** The Acura's tail lights are red.

   **Fix:** rotate reds to orange or magenta in `colorpass.sh` and in the E 3D palette, and recolour the F8 patches to the canon pale-blue dot and 1420 patch. If "no red" was only meant for the B&W world, say so; F and O1 then pass, but C's timer and F8's jacket still fail.
8. **126.25–130.50: the anagram detour stalls the loudest section (D).** E5a leaves the right half of the frame as blank paper, and E5c then holds a POV of a note for 1.74 s at peak drop energy. Gemini flagged this in 3 of 5 passes as "kills Drop 2 velocity". **Fix:**
   - Cut E5c to 0.9 s (two beats), starting from the handoff with the text already written.
   - Give the time back to E5a with a matte-extended wall or rooftop so the frame isn't half empty.
   - Or move the slip into the E5b handoff, so it's legible in the twin's hand.
9. **Plate and continuity breaks (A, C).**
   - **37.96–39.68 (A).** P1 moves the agent from the Lake Shore shoulder to a brick city street.
   - **59.20–60.08 and 62.30–63.62 (C).** V2a3 has Jade driving a **convertible**; the car is the white Acura sedan everywhere else.
   - **104.22–105.98 (C).** V2k1 has paper margins on the left, right and top, so the plate doesn't fill the frame.
   - **60.08–61.40 (C) and 128.0–134 (D).** The skyline includes the Empire State Building and NYC water-tower rooftops in a Chicago film.

   **Fix:** reframe P1 on the lakefront plate. Regenerate V2a3 from the sedan interior (the C4 keyframe works). Crop or scale V2k1 by about 1.12. Re-prompt the D rooftop plates as "Chicago Loop", or paint out the Empire State Building.
10. **183.56–195.42: the final drop sags in its heavier half, and the pencil reads as a baseball bat (F, current timeline).**
    - F5a (183.56–187.08) has Jade swinging a giant pencil with no visible tip, plus headphones on her head. Gemini read it as a bat.
    - F5b (187.08–190.58) is a static wide of Jade watching.
    - F6b (192.34–195.42) is a held 2D clock with almost no motion.

    That is about 7 s of low motion right where the bass layer enters (183.56). **Fix:**
    - Show the sharpened graphite tip in F5a and move the headphones to her neck; this also applies to F6a 190.58–192.34 and the F7_11/F7_12 recap.
    - Trim F5b to one bar (to 188.85) and cut to a tight insert of agents dripping off the lip.
    - Give F6b a slow rotate or push, with the march animated and stepping on beats, so the closure "clunks" on 194.10.

---

## (b) Full issue list by section

Severity: **H** is broken or a rule violation, **M** hurts clarity or energy, **L** is polish.

### A: 0–40.65 and R2 42.65–48.42

| Time | Sev | Issue | Suggested fix |
|---|---|---|---|
| 0.00–1.90 | L | C1 is effectively a still for 1.9 s; only the motes drift. That's fine for frame 0, but a scroller sees no motion until about 2.4. | Add a slow push-in, plus a hair or cloth flutter and a 2% scale "breath". |
| 7.24–10.82 | L | The *jade wang* credit line under REWIND isn't visible in any frame (crop checked at 9.9 s). | Re-enable it, or confirm it was cut on purpose. |
| 10.82–12.60 | L | The `DEFENSE 9AM` sticky note is tiny and rotated; it can't be read at 540p. | A 1.5× push on the note, or a 6-frame insert at the end of the shot. |
| 12.60–19.64 | M | S1 static selfie: see top-10 #5. Also, the lower third "The night before…" is white type over her white jacket. | Add an ink halo or shadow to the lower third. |
| 21.38–23.16 | L | The gantry sign text is about 6 px, and *I dreamt* sits tiny on the car's bumper (23.0). | Hold the sign large for one beat before the rush; put *I dreamt* in the lower third. |
| 23.16–24.90 | L | D2 is framed so Jade looks like a passenger gazing out the window while "speeding" (Gemini). | Accept it, or flip the plate so the steering wheel is visible. |
| 24.90–28.40 | L | The mirror etch "chasing me I couldn't place" is grey on dark, about 7 px. | Raise contrast with a paper-white etch and a dark halo. |
| 28.40–30.16 | M | Red tail lights on the white Acura (red rule). | Hue-shift to orange or white. |
| 30.16–31.92 | H | "men in shades and suits" is illegible; it's only in the lenses. | Top-10 #4. |
| 37.96–39.68 | M | P1 background changes from the lakefront to a brick street. | Top-10 #9. |
| 40.24–40.65 | L | The whispered *shot* can't be seen on her torso (graphite on skin). | Move it beside the burst on paper, or tint it ink. |
| 42.65–48.42 | L | The R2 counter `ITERATION 4,0xx` is dark on dark, top-left, about 6 px, so the "counting backward" idea is lost. | Use the C2 paper chip behind it. |
| 47.70–48.15 | L | In R2 `12ice` Jade wears the headphones **on her ears** (off-model), and `13sedanb` has a Mercedes grille (A already noted this). | Fix on the next pass, or swap stills. |

### B: C2 1.90–7.24, 40.65–42.65, 48.42–56.54

| Time | Sev | Issue | Suggested fix |
|---|---|---|---|
| 2.40–4.90 | H | The colour spoiler and the clipped HUD digit. | Top-10 #2. |
| 1.90–7.24 | L | At 960 px the ◀◀ ×N speed steps are legible, but the counter roll to 4,097 isn't (clipped). | Same fix as #2. |
| 40.65–41.40 | H | The letterbox inverts to a grey band. | Top-10 #6. |
| 41.40–42.38 | H | Menu items are orange on her orange band and can't be read. | Top-10 #6. |
| 42.38–42.65 | L | R1 is mostly a white flash; the "shatter" doesn't register (B already noted this). | Accept it, or add 2 frames of shards before the flash. |
| 48.42–56.54 | L | The reversed reuse brings back old lyric layers: the D3 mirror etch at 51.0 and the gantry sign at 52.25. Each line technically appears twice. At 50.5 the mid-flip REWIND letters overlap into "WNIG" for about 4 frames. | Strip the etch and sign text layers from the reversed sources (the comp only renders `pre` layers, so these are baked into the plates; use the clean plates). |
| 55.3–56.54 | L | The decelerating push on the tiny car lingers for about 1.2 s (Gemini: "lingers too long"). | Optional: trim the ease so the stop lands at 55.9. |

### C: 56.54–112.96

| Time | Sev | Issue | Suggested fix |
|---|---|---|---|
| 59.20–60.08, 62.30–63.62 | H | Convertible interior, not the Acura sedan. | Top-10 #9. |
| 60.08–61.40 | M | The Empire State Building is in the skyline. | Top-10 #9. |
| 75.12–76.02, 78.66–79.56 | L | The road arrows point left while the car drives right (the side-scroll grammar is forward = right). | Mirror the arrows or the plate. |
| 84.86–86.18 | L | The "back" slam lands at top-left. The 84.875 frame is a full whiteout (flash plus grey wash), so the landing itself isn't seen for about 3 frames. | Shorten the flash to 2 frames so the slam reads. |
| 86.18–87.06 | M | The word "back" sits on top of Jade's head in the interior shot V2e2. | Clear "back" at the cut to 86.18, or move it to the right third. |
| 90.14–92.79 | L | The mirror etch "sirens in my mirror …" is low-contrast and only half legible. The HUD cluster crowds the mirror's top edge. | Paper-white etch with a halo; move the HUD inward or hide it for this shot. |
| 93.07–93.66 | L | The LOADING tip text is about 7 px; it reads at 960 but not on a phone. | +40% size. |
| 94.06–98.28 | H | The race split timer is red (`+0.38`). The ghost HUD sits over busy brick. | Top-10 #7; put the HUD on a paper chip. |
| 98.28–104.22 | H | The grass lyric is illegible. | Top-10 #4. |
| 104.17–104.25 | L | "they" appears while "the field of grass" is still on screen (about 2 frames of two lyric layers). | Clear V2j's text at 104.17. |
| 104.22–105.98 | H | V2k1 has paper margins, so the plate doesn't fill the frame. | Top-10 #9. |
| 104.22–108.67 | M | Off-model: in V2k, Jade's hair reads as loose or a ponytail with no visible pencil. That's before the hair-drop beat at 144.54, so it undercuts G2. | Re-key with the bun and pencil, or crop tighter on the clip. |
| 108.67–110.78 | L | The shot list asks for "pistol rises, low angle". The cut uses a full-body Jade in a ring, with an agent drawing in the background. It reads, but it's soft before the shot. | Accept it, or add a 2-beat insert of the pistol. |
| 110.78–110.96 | L | The whispered *shot* isn't visible. | Place it on the paper sky beside the burst. |
| 110.79–112.96 | H | Faceless Jade. | Top-10 #1. |
| 111.62–113.40 | L | "…and time stops" never appears as text (the same applies to 41.04–42.57 in B). The menu and CONTINUE? stand in for it. | Decision for Jade: accept the menus as the lyric, or add a tiny whisper-style line. |

### D: 112.96–141.00

| Time | Sev | Issue | Suggested fix |
|---|---|---|---|
| 113.0–113.9 | L | E1 tints the whole world sepia-orange for about 0.9 s. That's residue and allowed, but it reads more as a colour grade than as a burst from Jade. | Make the bloom radial from her start pose and quicker to clear. |
| 113.89–119.44 | H | The ghosts read as blobs. | Top-10 #3. |
| 117.0–119.44 | M | E2c: the agents are a dense clump in the centre, and Jade enters from the frame edges at a small size. The "13 ghosts surround the stunned agents" image doesn't land. | Same as #3; a tighter ring and bigger ghosts. |
| 119.44–122.95 | M | E3 "Rewind" is orange on orange (top-10 #4), and E3 has the same selfie framing as S1 (top-10 #5). | See #4 and #5. |
| 122.95–126.25 | L | The E4 stream reads as a rainbow smear rather than "a stream of Jades". It's better than E2, but the individual figures blur. | Lower the trail opacity; keep the 6 instances crisp. |
| 126.25–127.88 | M | E5a: the right half of the frame is blank paper. | Top-10 #8. |
| 127.88–128.76 | H | The gold twin is opaque and reads as a new character. | Top-10 #3. |
| 128.76–130.50 | M | The slip hold is too long. | Top-10 #8. |
| 128.0–134.0 | M | NYC skyline and rooftops. | Top-10 #9. |
| 134.0–139.0 | M | E7: 24 sine-wave ribbons pile up into a screensaver look by 137.5, cover the meter close-ups and agents, and lose the pencil grain at 540p. | Cap at about 10 ribbons, give them pencil grain and taper, and keep a clear subject window. |
| 139.0–140.12 | L | E8: the redaction bar is paper-white in alarm mode. Gemini read it as a "missing texture" placeholder. | Draw it as a black bar with a white outline, so it's still a solid block. |
| 140.12–141.00 | L | The terminal cuts on `TRACE: L▌` because the typing doesn't finish. | Type faster so `TRACE: LOCKED` completes about 0.1 s before 141.00. |

### E: 141.00–169.40 and O1 211.64–218.92

| Time | Sev | Issue | Suggested fix |
|---|---|---|---|
| 141.00–144.54 | L | G1 is 3.5 s of near-stillness (Gemini: "truncate 1.5 s"). I'd keep it, because the music is weightless, but give the drifting lines a little more motion. | Add more drift speed variance and one slow turn of her head toward the bun. |
| 144.54–145.2 | L | Her raised hand clips the top edge (E already noted this). | Reframe down 5%. |
| 148.08–152.62 and 214.9–218.92 | M | A set of concentric circles (a "target") sits left of the diorama with no explanation. In O1 it's coloured. Gemini read it as a leftover tracking anchor. | Make it read as something (the Bean from above? the turntable?) or remove it. |
| 151.62–169.40 | M | Jade is tiny in M1, M2 and M3: about 25–50 px tall at 960. The rule is "Jade large unless deliberate wide", and here every shot is a deliberate wide. | Add one tighter isometric framing per shot (M2 at the crank on 162.30; M3 on the crank turn at 166.30). |
| 157.39–157.84 | L | The V3S cutaway works. The lyric's white type over a light background has low contrast. | Add an ink halo. |
| 161.00–165.18 | H | The M2 road lyric is illegible. | Top-10 #4. |
| 159.14–165.18 | M | The Möbius loop reads as a twisted ribbon with tiny cars. "Speeding down Lake Shore" has no speed (Gemini: "crawls, lags behind the beat"). | Speed the sedans up about 2× and step them on the beat; flash the crank clunk at 162.30 harder. |
| 167.0–169.40 | H | Red blocks in the M3 bloom. | Top-10 #7. |
| 168.12–169.40 | H | The "trace" smear. | Top-10 #4. |
| 211.64–215.0 | H | O1's brick-red building (current timeline). | Top-10 #7. |

### F: 169.40–227.96 except O1 (current timeline)

| Time | Sev | Issue | Suggested fix |
|---|---|---|---|
| 169.40–211.64 | L | The treatment says Jade holds the pencil "throughout". It isn't visible in F1, F2, F3, F6c, F7_02 or F8. | Accept it, or add the pencil in hand to F1 and F8. |
| 170–173, 200.3–205.5 | M | Reds in the colour world. | Top-10 #7. |
| 175.59–183.33 | L | The whispered *never stop* tags are about 6 px. Fine as an easter egg, invisible on a phone. | +50% size (O4 has already been enlarged). |
| 176.48–180.02 | L | F3's Relativity frame is very busy; Jade and the falling agents compete. | Add a slight vignette or desaturation on the stairs away from her. |
| 183.56–192.34, 208.58–209.90 | M | The pencil reads as a bat, and the headphones are on her head. | Top-10 #10. |
| 187.08–190.58 | M | F5b is a static wide during the heavier half. | Top-10 #10. |
| 192.34–195.42 | M | F6b is held almost still. | Top-10 #10. |
| 209.90–211.64 | H | F8 has red patches on Jade's jacket (off-model and red). | Top-10 #7. |
| 211.64–218.92 | L | The O1 variance report's text is about 6 px at 960, and the stamp is the only line that reads on a phone. | Scale the panel to 1.6× (bottom-right still clears the diorama). |
| 219.4–222.78 | L | The O2 notice warps under the 6-key hand track. It reads "DISSERCATION DEFENSE / 9:00 AM" (the T renders like a C), and Gemini saw it jitter. | Add more track keys or a planar track; or render the notice on the door in the plate. |
| 222.78–226.00 | L | 3.2 s of black (Gemini: "dead"). This is per spec (ring-out); I'd keep it. | No change, unless you want O4's iteration HUD to appear at 225.4 so the black has a pulse. |

---

## Rules check, summarised

| Rule | Status |
|---|---|
| Only Jade in colour until G3 (146.32) | **Fails at 2.4–4.9.** C2 flashes full-colour F frames. Everything else before G3 that has colour is residue (motes, ribbons, the E1 wash, ghosts, the slip), which is allowed. After G3 the colour is by design. |
| No red anywhere | **Fails:** 28.4–30.2 (tail lights), 94–98 (split timer), 167–169.4 (M3 bloom), 170–173 and 200–205.5 (F reds), 209.9–211.6 (F8 jacket), 211.6–215 (O1 brick). The red detector found no hits in 0–94 apart from C2's F frames at 3.9–4.1. |
| No "Authority" / "TVA"; agency always `TIME VARIANCE █████████` | **Passes.** The LOADING tip is in mixed case, "The Time Variance ███", which is fine. E8 uses a paper-white bar in alarm mode (see the D table). |
| No head shots | **Passes.** Both hits are torso and mote bursts (P4 front, V2m side). |
| Jade on-model | **Fails:** faceless V2m (110.8–113); off-model hair in V2k (104–108.7); headphones on ears in R2 `12ice`, F5a, F6a and the F7 recap; red jacket patches in F8; the opaque gold twin. Singing Jade has pink headphones in S1, E3 and V3S. The bun and pencil hold everywhere else before 144.54, and the hair is down after it. O2 puts the pencil back in her hair. |
| ≤ 1 HUD cluster + lyric | **Mostly passes.** R3 stacks ◀◀×N, the clock ring and the big REWIND over reused footage that still carries the old etch and sign text (51.0, 52.25). V2f2's HUD crowds the mirror. |
| Every lyric line once, at the right time | Timing is good wherever text appears; words land on their onsets. **Missing or illegible:** V1-4b (30.16), PD-2 and B-2 "and time stops" (the menus stand in), V2-5 (illegible), V3-2 (illegible) and the word "trace". The whispered *shot* isn't visible twice. **Doubled:** R3/R4 reuse (old etch and sign) and 104.17 ("they" over "the field of grass"). I found no engine default lyric overlay on top of section text. |
| Cuts on the listed beats | **Passes.** All 13 R2 chop cuts and all 13 E2 chop cuts are within 1 frame of `vocal_chops`. Every section and shot boundary is within 1 frame (56.54, 63.62, 83.10, 84.86, 88.38, 92.79, 94.06, 98.28, 104.22, 112.96, 141.00, 144.54, 146.32, 148.08, 153.98, 159.14, 165.18, 169.40, 211.64, 218.92 and 222.78 checked). Cuts more than 70 ms off the eighth-note grid occur only inside speed-ramped reverse comps (R3/R4, 48.4–53.6), which is expected. |
| No placeholder slates, black frames or glitches | No slates. Black only where designed: 93.00–93.04 after the L-train, and 222.79–226.0. Glitches: faceless V2m, the P5 grey letterbox band, V2k1 paper margins, the clipped C2 HUD digit, the M3 "trace" smear. |
| Continuity at hand-offs | **56.54:** the hand-off from R4's slow stop on LSD to V2a's side-on chase works. **141.00:** the cut from the black terminal to the white page is the best transition in the film (fix the unfinished typing). **169.40:** the M3 pull-back on the riser, then a white flash, then the F1 flood from Jade works. **211.64:** the jump from F8's anime colour to O1's crayon diorama is still a style jump, but the colour diorama bridges it better than v1's did. Inside sections: P1's street (37.96), the V2a3 convertible, the NYC skyline. |

---

## (c) What's working best (protect these)

- **0.00: the first frame.** The wall-jump with a hanging bullet and five agents firing up through the engraving is a strong, legible thumbnail and a strong first image. Don't let anyone soften it.
- **7.24–10.82: the REWIND title.** It arrives mirrored and flips right-reading over the lake skyline. It's simple and on the bar.
- **42.65–48.42: R2's 13 death tableaux,** each on its chop, frame-accurate. Jade stays in colour mid-burst in each one. This is the clearest "game over, rewind" idea in the film.
- **48.42–56.54: the Braid rewind** with the blue tint, the clock ring and REWIND letters arriving D-first.
- **56.54–92.79: Verse 2's instrumental chase.** Every 2-beat cut is one legible near-miss (tilt lane, flipping sedan, falling lamp, truck squeeze). Then come the bridge hang through the band hole (84.04–84.74) and "back" landing on 84.86. Gemini rated it the film's strongest stretch too.
- **92.79–94.06: the L-train smash to black to LOADING "Reload."** and the respawn into the paper-white day level. Funny and on the lyric.
- **111.46–112.96: CONTINUE? 9 → 8,** the arcade-button slam, then white into Drop 2.
- **139.00–141.00: "Anomaly detected."** The negative agents snap to camera, the terminal types on the words, then the hard cut to the white page.
- **144.54: the pencil leaves the bun and the hair falls on the low boom.** This is the hero beat of the film, and it lands exactly. G3's colour stroke and the filings blooming to colour are a close second.
- **148.08–151.62: the Loop diorama** assembling on the music box (E). And **153.98: V3S**, a deliberate echo of S1, now showing the impossible city.
- **Current F:** the F1 colour flood from Jade (169.4); the F2 wall-run with ghosts; the F4 Bean dive into ripples; F6c's Super Meat Boy ghost stream (this is the ghost look D should copy); the F7_04 Klimt sky on the 200.25 swell; the F8 committee line; O4's "never stop." with the counter rolling past 4,100.

---

## (d) Verdict: pacing and energy against the music

The structure is right. The genre ladder changes exactly where the music changes, every impact and chop is cut to the frame, and the big structural beats (shot → pause, rewind, Reload, CONTINUE?, Anomaly, pencil, colour flood, black) are where the song puts them. As a rough cut it's already watchable end to end. The arc's shape is sound:

- a cold, dense open;
- an intimate verse;
- a mechanical, beat-locked Verse 2;
- a euphoric Drop 2;
- a weightless turn;
- a diorama verse;
- a maximal colour finale;
- a trailer-card outro.

Where the energy doesn't track the music:

1. **The hook leaks at 12.6 s.** C1 and C2 are dense and promising, but C2 shows the ending (in colour). After the title, S1 is a 7-second static selfie. Gemini rated the first 30 s **4/10** in the chunk pass and **7.5/10** in the full-film pass. My read: frame 0 stops a scroller, the C2 strobe holds them about 5 s, and S1 is where they leave. Top-10 #2 and #5 fix most of this.
2. **Drop 2 peaks too early and then stalls.** The loudest section should be the first big colour payoff. The ghost mechanic reads as smudges (113.9–119.4), and the middle (126–131) is a slip of paper. E6 and E7 recover it, but E7's ribbon pile-up turns into noise rather than a crescendo. Fixing #3 and #8 makes Drop 2 the second-biggest moment, as the treatment intends.
3. **Verse 3 is lovely but small.** The music is drumless and intimate, so low motion is right. But Jade is tiny, two of three lyric lines are unreadable, and the "it couldn't trace" payoff smears. The emotional thesis of the film lives here, so it has to read.
4. **The final drop is strong, with a 7-second sag right where the bass layer enters (183.6).** F5b and F6b hold almost still. Keep the escalation monotonic: cuts should get shorter after 183.56, not longer.

Overall: **a B-minus rough cut with an A-grade spine.** Nothing needs a rethink. The ten fixes above are mostly regenerations of single shots (V2m, V2a3, E2 ghosts, E5b), type and legibility passes, and a palette pass. Sections C, E and F are closest to locked. A and B need the hook work, and D needs the ghosts.

---

## Outside reviewer (Gemini 3.8 Flash): where it agreed, where it was wrong

- **Agreed and verified:** the singing-selfie style break (S1, E3, V3S); the P1 continuity jump (0:38); the illegible PAUSED menu; the illegible grass lyric; the Banach–Tarski note stalling Drop 2; the yellow-jacket twin reading as a new character; the static F5b; the "bat" in F5a; the unexplained concentric circles; the red ghost-race HUD (it said "GHOSTS 1 in faint red"; it's actually the split timer).
- **Wrong or stale:**
  - "whiteout 0.4 s ahead of 169.4": the flash is on 169.417.
  - "TIME VARIANO#" and "RESIDUE: UNTRACEAB" typos: those are mid-typing frames of the variance report, not typos.
  - "TTP:" on the LOADING screen: it reads TIP.
  - "subtitle counter hard-snaps 4,097 → 4,100": it rolls; fine in the current timeline.
  - "1:13–1:21 swell cuts slightly off": measured within 1 frame.
  - The 3D F6b and v1 F remarks no longer apply after the F polish.
- **Its scores (full pass):** hook 7.5, story clarity 5.5, cut rhythm 7, lyric legibility 4.5, visual polish 7.5. The two weakest sections it named were 0:13–0:38 and 2:06–2:13, which match top-10 #5 and #8.

## Files

- **Contact sheets, v1 (39):**
  - `media/reviews/roughcut_v1/sheet_00_000.00-005.75.jpg` … `sheet_38_223.04-227.50.jpg`
  - 4 columns × 6 rows, each frame labelled with time, frame number and owning section.
- **Contact sheets, current-timeline F (6):** `media/reviews/roughcut_v1/F_current_00_169.42-179.42.jpg` … `F_current_05_221.92-227.92.jpg`
- **Zoom crops:** `media/reviews/roughcut_v1/zoom_*.jpg`. The key ones:
  - `zoom_27_key_checks.jpg`: the C2 HUD clip, the missing credit, the whisper, the red split timer, faceless V2m, the M2 road lyric, the "trace" smear, the lens lyric and the O2 notice.
  - `zoom_07_red_check.jpg`: the red mask.
- **Gemini raw output and prompt:** `media/reviews/roughcut_v1/gemini_raw.md`
- **Scripts (scratchpad, not committed):**
  - `analyze.py`: frame stats and red mask;
  - `sheets.py`, `zoom.py`;
  - `gem/run_gemini.py`: chunked Gemini review with a burned-in timecode.
