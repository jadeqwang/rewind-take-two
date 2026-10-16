# v9 fix 8: the "1420 / MHz" sleeve roundel (C1, R2, F7_02, F7_04, F8, B2_glance)

Status: done on sources. I didn't render (no render.mjs), so the lead's integrated preview still needs to pick up the
timeline/EDL changes listed at the end.

## What was wrong
The video and image models drew pseudo-text inside Jade's roundel: C1 "1A7O / IMHZ", R2_03 "1AEE / DIFE", R2_04
"14?0 NHZ", R2_07 "ZUEB / ARIZ", R2_10 "AU3 / 9H2" (sideways), R2_12 "1420 / MBC", F7_02 scrambled glyphs that change
every frame, F7_04 "ŁATH / UTEIN", F8 "LAZO / BHLZ", B2_glance "PWD"/"P10" changing every frame.

## What I made
Every fix uses `tools/sectionE/patchfix.py`, the same pass that made the G1-G3 `*_patch` clips. It keeps the clip's own
ring, sleeve shading and occluders. It re-letters only the inside of the ring with Overpass "1420 / MHz", which is warped
onto the fitted ellipse and follows the sleeve every frame. Ink is the ring's own dark and the paper is the patch's own white. Each new file has a new
name, and its frame count, fps, size and encode settings match the source (97 frames, 24 fps, x264 CRF 12, yuv420p bt709).

| Shot | Source | New file | Frames re-lettered |
|---|---|---|---|
| C1 (0:00-1.90, also replayed in C2) | `media/shots/C1/take_3_engraved.mp4` | `media/shots/C1/take_3_engraved_patch.mp4` | 0-96 |
| R2_03 | `media/shots/R2/engraved/kf_03picasso_engraved.png` | `.../kf_03picasso_patch_engraved.png` | still |
| R2_04 | `kf_04bridge_engraved.png` | `kf_04bridge_patch_engraved.png` | still |
| R2_07 | `kf_07riverwalk_engraved.png` | `kf_07riverwalk_patch_engraved.png` | still |
| R2_10 | `kf_10gearsb_engraved.png` | `kf_10gearsb_patch_engraved.png` | still |
| R2_12 | `kf_12iceb_engraved.png` | `kf_12iceb_patch_engraved.png` | still |
| F7_02 | `media/shots/F7b/take_3_engraved_dered.mp4` | `media/shots/F7b/take_3_engraved_dered_patch.mp4` | 0-24 (the ring is behind hair from 25) |
| F7_04 and F7_13 (same file) | `media/shots/F7c/take_2_engraved_dered.mp4` | `media/shots/F7c/take_2_engraved_dered_patch.mp4` | 0-62 (F7_04 uses ~0-42, F7_13 ~43-53) |
| F8 | `media/shots/F8/take_4_engraved_dered.mp4` | `media/shots/F8/take_4_engraved_dered_patch.mp4` | 0-64 (uses ~12-54) |
| B2_glance | `media/shots/B_glance/take_1_engraved.mp4` | `media/shots/B_glance/take_1_engraved_patch.mp4` | 0-50 (uses ~8-42) |

Commands (all with `tools/engrave/.venv/bin/python`, `FFMPEG=<moongazing imageio ffmpeg>`):
- C1: `--init 1131,263,20 --from 0 --to 96 --guess -15` (the take is near-static; tracked 97/97).
- F7_02: `--init 1144,407,0 --from 0 --to 24 --sigma 0,0,0 --occ 0.45 --keys "$(cat docs/revisions/v9/fix_8/F7b_keys.txt)"`.
  The roundel is held on twos and jumps 20-100 px between pairs, so normal tracking can't follow it. A round-hole detector
  found each frame's ring centre, and I checked each one by eye (`F7b_keys.txt`). I read the baseline angle by eye for
  each pair: -30 deg on frames 0-4, -15 to -5 on 6-17, -60 on 18-24. Smoothing is off, so the decal never lags a jump.
- F7_04: `--init 1082,206,20 --from 0 --to 62 --rad 14 --guess 0 --scale 0.74 --thr 150`. At the default `--thr 120`
  the ring's thin top-right arc was painted out on frames ~45 and 55.
- F8: `--init 1076,364,30 --from 0 --to 64 --guess 0 --scale 0.76 --thr 150 --drop 29,30`. At `--thr 120` the thin
  right arc of the ring was painted over on frames 26-31. At 150 only 29-30 misfit (the top glyphs fuse with the ring), so
  those two frames are interpolated.
- B2_glance: `--init 686,362,0 --from 0 --to 50 --rad 15 --sigma 0.6,0.8,1.0 --scale 0.76 --ring-fill 0.95 --keys
  "$(cat docs/revisions/v9/fix_8/B_glance_keys.txt)"`. Per-frame centres come from template matching, checked by eye. The
  baseline angle follows the 20-frame arm cycle: 22 deg with the arm back, 0 with it forward. Frames 18, 26 and 46 are
  motion-blurred and have no ring to fit, so their centres were set by eye.
- R2 stills (`IN.png OUT.png --init X,Y,0 --rot A --scale S`): 03picasso `1215,690 rot 10 scale 0.84`, 04bridge
  `1691,466 rot 5`, 07riverwalk `1200,390 rot 10`, 10gearsb `1068,312 rot 90 scale 0.68 --rad 22 --thr 150`, 12iceb
  `1288,404 rot -25` (scale 0.76 where not given). R2_10's lettering runs along the sleeve, as the still drew it.

`tools/sectionE/patchfix.py` changes. All are optional and off by default, so old commands reproduce the old output:
- `--keys "F:X,Y[,ANG];..."`: per-frame seed centres. If every key has an angle, the baseline angle is interpolated
  between keys instead of carried by optical flow. An untracked frame with a key takes its centre from the key.
- `--sigma C,S,A`: temporal smoothing of centre, shape and angle. The default is the old 0.8,1.6,1.5.
- `--occ`: the occluder opening radius, default the old 0.26.
- `--ring-fill`: also repaint inside this fraction of the fitted ellipse.
- `--drop` and `--skip`: frame lists.
- Still images in and out (`.png`/`.jpg`).

Evidence (small jpgs, before | after, zoomed): `docs/revisions/v9/fix_8/C1_before_after.jpg`, `R2_before_after.jpg`,
`F7_02_before_after.jpg` (src f4, f9, f14, f20), `F7_04_before_after.jpg` (f20, f48), `F8_before_after.jpg`,
`B2_glance_before_after.jpg` (f12, f22, f26, f36), and `preview_after.jpg`, which shows six patched frames at 640 px to
check that the roundel sits naturally at preview size.

How I checked: I frame-stepped every patched frame of every clip on zoomed contact sheets (C1 0-47, F7b 0-27, F7c 0-62,
F8 10-59, B_glance 0-50) and compared the results with G1's patched roundel and the canon S1/kf_11ferris roundels. Each
problem frame I found (F8 26-31, F7c 45 and 55, B_glance 18/26/46, F7b 21/23) was fixed or is listed below.

## Spend
$0. I made no paid calls. Running `spend.py` gave $252.72 before and $258.74 after; the difference is other agents'
concurrent calls, and none of the new spend is tagged `v9_8`.

## Other garbled roundels in the master (listed only, not fixed)
- **C27_V2d2** (1:23.98-1:24.86, `media/shots/V2d2/take_4_engraved_blue.mp4`): the roundel is a red badge with squiggle
  text (confirmed at f2022). The same shot has no headphones.
- **F7_10** (3:28.17-3:28.58, `media/shots/F1/take_3_wipe_dered.mp4`, clip_in 2.3): "CATZ / UTHT" (confirmed at f4999).
  **F1** (2:49.40-2:52.96) plays the same take from 0.0, so its small roundel is very likely garbled too.
- **F4** (3:00-3:02.8): gibberish patch. Another agent owns F4, so I didn't touch it.
- **B2_skip** close frames (the audit groups them with B2_glance): a different plate, not patched.
- **PC2_lobby** Jade idle loop (`media/shots/PC/idle/jade/`): the roundel fades to an outline on loop frames 55-95. That is
  drift, not garbled text.
- **C2 f66-79 / f97-101**: these are flashes of later shots, so they inherit the fixes above through the `film` comp. The f98
  garble the audit names is G1 (already patched in v3), smeared by C2's chroma/VHS tear rather than wrong at the source.
- Placement, not text: R2_10 and R2_11 have the roundel on her RIGHT sleeve, F7_04 has it on her left collarbone, and C4's
  near sleeve has none. Moving them was out of scope.

## Still imperfect
- F7_02 src frames 21 and 23: a ~3 px dark crescent remains at the ring's right edge, where a bold source glyph fused
  with the ring and so falls outside the fitted interior. Frame 21 is on screen for one frame; 23 is probably past the cut.
- B2_glance src frame 26 (motion blur): a faint grey fleck at the lower ring edge.
- R2_10: a blue mote that overlapped the top of the ring is partly painted out (its lower half is now patch-white).
- F7_04 frames 43-45 (start of F7_13): the ring's top-right arc is a little thinner than in the source.
- The angles for F7_02 and B2_glance were read by eye. They follow the source's motion, but between held pairs the text
  turns as abruptly as the take does (it's animated on twos).
- The lettering is the patchfix Overpass font, as on G1-G3. S1 and kf_11ferris have a slightly different hand-drawn
  "MHz".

## Exact timeline / EDL changes (for the lead; I did not edit these files)
1. `render/timeline/A.js`, `PLATE.C1`:
   `src: S('C1', 'take_3_engraved.mp4')` -> `src: S('C1', 'take_3_engraved_patch.mp4')`
2. `render/timeline/A_R2.js`, `STILLS`: `'03picasso'` -> `'03picasso_patch'`, `'04bridge'` -> `'04bridge_patch'`,
   `'07riverwalk'` -> `'07riverwalk_patch'`, `'10gearsb'` -> `'10gearsb_patch'`, `'12iceb'` -> `'12iceb_patch'`. The
   template `kf_${s}_engraved.png` then resolves to the new files. A.js's exported `R2_STILLS` isn't used by A_R2.js.
3. `render/timeline/_B_verse2.js` line 190 (B2_glance):
   `src: plate('glance')` -> `src: \`${S}B_glance/take_1_engraved_patch.mp4\`` (this is the only `plate('glance')` use;
   `S` is the file's existing `media/shots/` prefix).
4. `media/shots/F_edl.json`:
   - F7_02 `"file"`: `media/shots/F7b/take_3_engraved_dered.mp4` -> `media/shots/F7b/take_3_engraved_dered_patch.mp4`
   - F7_04 **and** F7_13 `"file"`: `media/shots/F7c/take_2_engraved_dered.mp4` -> `media/shots/F7c/take_2_engraved_dered_patch.mp4`
   - F8 `"file"`: `media/shots/F8/take_4_engraved_dered.mp4` -> `media/shots/F8/take_4_engraved_dered_patch.mp4`
   - `matte_file` entries stay the same (the geometry hasn't changed).
   The EDL is generated by `tools/sectionF/edl.py`. To make a regeneration keep these, add
   `file=S + "F7b/take_3_engraved_dered_patch.mp4"`, `file=S + "F7c/take_2_engraved_dered_patch.mp4"` and
   `file=S + "F8/take_4_engraved_dered_patch.mp4"` to `CHOSEN["F7b"]`, `CHOSEN["F7c"]` and `CHOSEN["F8"]`. The matte
   default is derived from `take`, and the `_dered` lookup finds no `*_patch_dered.mp4`, so the patch file is kept.

---

# Round 2 (Jade: fix the other garbled roundels too)

Same rules apply: new files with new names, no timeline/EDL edits, no render.mjs. F4 was left alone (another agent owns it:
`take_2_engraved_dered_v9refl.mp4`). Spend: $0 (no paid calls; `spend.py` reads $261.56 before and after, and nothing is tagged `v9_8`).
I used the 540p preview `render/engine/out/rewind/rewind_preview.mp4` to confirm where each shot plays.

## C27_V2d2 (1:23.98-1:24.86): red badge -> canon roundel
- Source actually used: `media/shots/V2d2/take_4_engraved_blue.mp4`. That is C.js `BLUE_ERASER['V2d2_4']`, played from in 2.0 at rate
  0.6, i.e. src frames ~48-61.
- The model drew a red rounded-square badge with a grey plate and squiggle glyphs, half hidden behind the dark lattice
  pillar beside her shoulder. It has no ring with a white interior, so patchfix has nothing to re-letter. I wrote a small
  new tool for it, `tools/v9/roundel_decal.py`, which reuses patchfix's lettering artwork:
  1. It erases the red badge: the red pixels' convex hull plus the plate inside it, grown 3 px, is filled with the
     sleeve's own colour.
  2. It paints a canon roundel (white face, black ring, "1420 / MHz") at the badge's position.
  Both steps stop at the pillar's edge, so the pillar still occludes the roundel's right side as it did the badge.
  The badge doesn't move in this take (I template-tracked it to within 0 px over frames 44-66), so the roundel is static.
- Spec: `docs/revisions/v9/fix_8/V2d2_roundel.json` (frames 36-80, centre 1189,391, r 15.5, baseline -6 deg).
- Command: `tools/engrave/.venv/bin/python tools/v9/roundel_decal.py media/shots/V2d2/take_4_engraved_blue.mp4
  media/shots/V2d2/take_4_engraved_blue_roundel.mp4 --spec docs/revisions/v9/fix_8/V2d2_roundel.json`
- Output: **`media/shots/V2d2/take_4_engraved_blue_roundel.mp4`** (121 frames, 24 fps; the blue-eraser fix is kept, and
  the matte is unchanged because the badge was already inside her matte).
- I frame-stepped frames 44-67. The roundel is clean in every one and the pillar edge stays crisp.
- **Headphones are still missing in this shot**, with a pale-blue collar where they should be. I didn't fix it: painting
  headphones onto a 0.9 s, 1.3-1.5x punched-in close-up, frame-blended per frame, isn't a cheap, clean pixel job.
  It would need a keyframe regen or a tracked paint pass.

## F1 (2:49.40-2:52.96) and F7_10 (3:28.17-3:28.58): same take
- The EDL plays `media/shots/F1/take_3_wipe_dered.mp4` for both shots. `edl.py`'s CHOSEN names `take_3_wipe.mp4`, but
  `plate()` swaps in the `_dered` file when it exists. F1 uses src 0 to ~94 (clip_in 0, rate 1.1) and F7_10 uses src ~55-67.
- The roundel is on screen in about 60 of the 96 frames. It is often half behind her hair, and it pops in and out with
  the arm swing on twos. I read each visible pair's centre and baseline angle by eye from gridded frame-steps and marked
  every one to check. The keys are in `docs/revisions/v9/fix_8/F1_keys.txt`, and the frames with no roundel (behind
  hair or arm, or out of frame) are in `F1_skip.txt`.
- I ran it in two passes, because the tracker loses the ring on frames 70-73 after the run of frames with no roundel:
  1. `patchfix.py take_3_wipe_dered.mp4 passA.mp4 --init 1090,404,0 --from 0 --to 95 --keys "$(cat F1_keys.txt)" --skip
     "$(cat F1_skip.txt),70,71,72,73" --sigma 0,0,0 --occ 0.45 --scale 0.76 --ring-fill 0.93 --crf 0`
  2. `patchfix.py passA.mp4 take_3_wipe_dered_patch.mp4 --init 1100,365,70 --from 70 --to 73 --keys
     "70:1100,365,-12;71:1100,365,-12;72:1108,375,-12;73:1108,375,-12" --sigma 0,0,0 --occ 0.45 --scale 0.76 --ring-fill 0.93`
- Output: **`media/shots/F1/take_3_wipe_dered_patch.mp4`** (121 frames, 24 fps). The matte is unchanged.
- I frame-stepped every patched frame. On frames 26-27 the roundel is seen edge-on; I re-lettered it along the ring, which
  reads as a foreshortened "1420 / MHz". On frames 6-9 the ring is a tiny edge-on oval with no lettering, so I left it.
  Frames 96-97 are past both shots' ranges, so I left them alone.

## B2_skip: nothing to fix
I frame-stepped every frame the shot uses (`media/shots/B_skip_b/take_1_engraved.mp4` src 14-58, `jade` layer in 0.6).
She runs three-quarter toward camera-right, and no roundel is visible on either sleeve in any frame, so there is no
garbled text there. The audit's "B2_skip close frames" note belongs to the B2_glance entry, which round 1 fixed.

## PC2 lobby idle: left alone
In `media/shots/PC/idle/jade/` the roundel sits edge-on at the sleeve's silhouette, with no readable lettering
(checked at f_0030). The only issue is the outline fade the audit describes, and that is drift, not wrong lettering.

## Round 2 evidence
`docs/revisions/v9/fix_8/`:
- `C27_V2d2_before_after.jpg` (src f50, f60)
- `F1_before_after.jpg` (src f0, 16, 30, 46, 58, 62, 72, 86; F7_10 covers 58/62)
- `round2_preview_after.jpg` (640 px frames of both patched clips)

## Still imperfect (round 2)
- F1 frames 70-71: a small grey wedge (a source glyph fused to the ring) remains at the ring's inner right edge.
- F1 frame 84: a thin dark arc remains along the inside top-right of the ring, where the source drew a double ring.
- F1 frames 56-57 and 64-65: hair crosses the roundel and partly covers the new "1420", as it covered the old glyphs.
  This is correct occlusion, but the digits read as cut.
- C27_V2d2: the new roundel is a flat, clean decal on a frame-blended close-up, so it is slightly crisper than the
  engraved sleeve around it. Headphones are still missing (see above).

## Round 2 changes for the lead to apply (I edited none of these files)
1. `render/timeline/C.js` line 73, `BLUE_ERASER`:
   `V2d2_4: 'take_4_engraved_blue.mp4'` -> `V2d2_4: 'take_4_engraved_blue_roundel.mp4'`
   `matte()` is keyed by take, not by file, so V2d2 keeps `take_4_matte`.
2. `media/shots/F_edl.json`: change the F1 **and** F7_10 `"file"` from `media/shots/F1/take_3_wipe_dered.mp4` to
   `media/shots/F1/take_3_wipe_dered_patch.mp4`. The `matte_file` (`media/shots/F1/take_3_matte/matte.mp4`) stays
   the same.
3. `tools/sectionF/edl.py` line 16, `CHOSEN["F1"]`: `file=S + "F1/take_3_wipe.mp4"` -> `file=S + "F1/take_3_wipe_dered_patch.mp4"`.
   `plate()` then looks for `take_3_wipe_dered_patch_dered.mp4`, finds none, and keeps the patch file. The matte
   default still comes from `take=3`. Any other code that reads `CHOSEN["F1"]["file"]` as the un-dered wipe (none
   that I found in edl.py) would now see the patched file.
4. Nothing for B2_skip or PC2.
