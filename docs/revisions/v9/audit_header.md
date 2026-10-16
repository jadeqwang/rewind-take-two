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
| 1a | 0:38.90-0:39.68 (also flashed in C2 at f154-156) | P2 | **Passenger seat ("With no warning").** The wheel sits at lower frame-left with an empty gap between it and her, so nobody is driving. D7 (0:34) and C4 (0:10) put her at the wheel in the left seat. Checked by hand at f943. Note: the part 1 reviewer marked P2 as fine; that was wrong. Fix: mirror the plate or re-stage with the wheel in front of her. | HIGH |
| 1b | 1:06.29-1:07.16 (also flashed in C2 at f145) | C10_V2b3 | **Passenger seat again.** Left-hand-drive car, Jade in the right seat reaching across to grab the wheel (checked by hand at f1600). Same shot: matte pop to colour (f1596), white cut-out blobs round her head, the flipping sedan passes through the cabin roof, one pencil and no headphones. | HIGH |
| 2 | 0:25.34-0:28.40 | D3 | **Impossible mirror** (Jade's example): side mirror seen face-on through her window. Her fix: over-the-shoulder into a real rear-view mirror. | HIGH |
| 3 | 1:29.29-1:31.46 | C_V2f_car | **The existing over-the-shoulder rear-view mirror is impossible too:** no stem, no windscreen/roof, floats outside the car among the overpass girders; at f2196 the close still fades in with a roof liner and stem. Fix D3 and this together. Driving staging itself is right (LHD, her on the left, both hands on the wheel). | HIGH |
| 4 | 2:13.6-2:14.5 | C2b_letgo (+C2a f3203-3205) | Orange/blue twin colouring swaps between the girls mid-stride when they cross (screen-side mattes); jackets mix both colours; a hard vertical seam cuts the leaping twin half orange/half blue. | HIGH |
| 5 | 2:26.33-2:26.75 (f3512-3522) | G3 | **Three legs** (Jade's example): floating Jade has three trouser legs and three sneakers until the feet leave frame. Fix: start G3 ~11 frames later or paint out. | MED |
| 6 | 3:00.0-3:02.8 (contact f4373-4388) | F4 | **Impossible Bean reflection** (same family as the car mirror): the reflection shows her front and face instead of her back, isn't flipped, and has no headphones. At contact its grey arms sit under her white ones (four arms), then the heads merge. Re-stage like D3. | HIGH |
| 7 | f3675-3685, f3863-3875, f3919-3931, f4008-4020, f4064-4065 (likely also f3640-3650) | M1-M3 | Tiny Jade sprite blinks out for ~12 frames and pops back while her glow stays. Not AI: the reviewer traced it to `spriteFrame()` in `render/three/lib/engrave.js`, which wraps the frame index by atlas cell count, not clip frame count, so some indices land on empty cells. One-line fix, then re-render section E. | HIGH |
| 8 | 0:00-0:01.90 | C1 | Opening hero still: the sleeve roundel reads "1A7O / IMHZ" instead of "1420 MHz". The garbled roundel recurs in the R2 death stills, F7_02 (scrambles every frame, next to her face), F7_04, F8 and B2_glance. | MED |
| 9 | 0:37.96-0:40.24 | P1 / P1b | The white Acura behind the agent is empty (bare headrests), cut against P2 where she's in it. | MED |

All 8 parts are complete. Reviewer totals (before dedupe): part 0 2H/1M/2L, part 1 0H/3M/5L, part 2 2H/12M/9L,
part 3 0H/3M/~14L, part 4 1H/6M/2L, part 5 1H/4M/3L, part 6 0H/4M/5L, part 7 0H/2M/2L. Recurring themes: pencil
count changes (one vs the canon two, extra pencils in a hand), the garbled 1420 MHz roundel, missing headphones,
and AI vehicle physics in the V2 chase (cars melting, passing through each other or the cabin).

Corrections to the per-part notes below: part 1 says P2 is fine; it isn't (see 1a). Grabs taken with
`-ss N/24+0.01` show frame N+1; use `-ss (N-0.5)/24`.

## Detail by time range
