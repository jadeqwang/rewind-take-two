# v5-signs: progress (notes 0:22 and 0:50)

Cap $4, tag `v5_signs_`. **Spent: $0** (no generations; the total moved from $243.44 to $244.12 because of other
streams).

**Status: done, handed over.** Clips: `media/reviews/v5/0022_signs.mp4` (21.38–23.16),
`media/reviews/v5/0050_rewind_signs.mp4` (42.38–56.54, re-encoded at crf 27 to fit under 10 MB). Fragment:
`docs/revisions/v5/fragments/signs.json`. Nothing committed.

## Findings (v4 preview)

- **D1 (21.38–23.16):** the plate's two gantry panels are blank paper faces with an engraved rim. v4 laid `pin`
  `style: 'sign'` panels over them: flat black boxes with clean Overpass text (the "digital" look). The v3 track of
  the right panel (`_A_tracks.js` D1_signR) shears into a parallelogram from about 0.6 s. Both tracks were also
  sampled between frames, so they ran up to one frame ahead of the plate (D1 starts at 21.38, mid-frame).
- **Rewind run:** R2_01–R2_13 (`A_R2.js`) are the death stills: there are no billboards or road signs in them.
  R3 (48.42–52.48) and R4 (52.48–56.54) live in **`render/timeline/B.js`**, not A.js. Both are `comp` layers that
  replay the film backward. R3 plays D8 → D1 (37.94 → 21.40, about ×4, with 12 fps judder). R4 plays S2 → S1x → S1 → C4 → C3,
  and none of those shots has a sign. Inside a comp every `noRewind` layer is skipped, so the D2 bulb billboard
  (about 51.50–52.04) and the D1 gantry (about 52.04–52.48) replayed as blank white panels. Those are the blank signs
  Jade saw.
- The R3 REWIND title (size 300, y 640, right-reading after 50.52) covers y ≈ 410–650, which puts it right on
  D2's lower billboard panel. D2's upper panel and the D1 gantry sit above it.

## What was done

1. `tools/v5/signs/woodpanel.js` (new): a sign face cut in the block. It is an ink face cleared by hand-uneven
   vertical gouges, with a paper rule standing inside the edge. It also takes `plain` bands, left solid behind small
   lettering. The block's resolution follows the face's size on screen, so the gouges do not moiré as the gantry rushes in.
2. `tools/v5/signs/track_d1.py` → `tools/v5/signs/tracks.js` (new): the D1 faces re-tracked, one quad per source
   frame. Each quad is an edge-line fit on the white faces. Once the frame cuts a face, a scale + translation of the
   last whole frame is fitted to the corners still visible, then carried on after the faces leave. Debug sheet:
   `--debug out.jpg`.
3. `tools/v5/signs/quad.js` (new): `subQuad` (projective sub-rectangles of a track, so each line of lettering sits in the
   panel's perspective) and `stepKeys` (holds each quad for its whole source frame, like the video layer).
4. `render/timeline/A.js`:
   - two imports;
   - a `D1_SIGNS` block (with `PANEL`, `REWIND_RUN`, `FWD_OR_RW`, `RW_ONLY`) above `LETTERBOX`;
   - D1's two `pin` layers replaced by `...D1_SIGNS`: left LAKE SHORE DR over I'M SPEEDING DOWN LAKE SHORE, right
     SOUTH, all woodcut in paper on woodpanel faces;
   - D2: two rewind-only layers. The upper panel reads A SHADOW / CHASING (ink woodcut, lit, like forward D2) and the
     lower panel is switched off (a dark face). Forward D2 is untouched.
   - Gating: the D1 sign layers draw in their own shot and inside a comp only while the frame is in 48.42–56.54, and
     the D2 additions draw only in that case. So C2's teaser flashes and later replays are as before.

   No other row changed. The S1 rows belong to `v5-stairs`, and B.js itself was not edited.

## Decisions

- **Which words in the rewind:** the lines this stretch is rewinding through, not the word being sung. The only sung
  word at 48–56 is "Rewind.", and the title already says it. D2 carries V1-3 (A SHADOW / CHASING) and D1 keeps its own
  V1-2 lettering, so the replay shows the same world it showed going forward.
- **Right-reading, not mirrored:** by 51.5 the title has flipped to right-reading, and mirrored words would not read
  in the roughly 0.5 s each sign is up at ×8. **No reverse word-by-word reveal:** forward D2 lights its words one by one,
  so played backward the panel would be lit for only about 0.14 s. The signs stay whole and lit through the rewind.
- **D2's lower panel switched off**, so no lettering sits under the REWIND title (it also gives the title a darker ground).

## Checked (540p, frame by frame)

- D1: all 43 frames. The faces stay locked to the plate with no jitter, including the frames where the frame top
  cuts them. LAKE SHORE DR and SOUTH read from about 21.8, the small line from about 22.2. No red.
- Rewind: 51.43–52.6 frame by frame. A SHADOW / CHASING reads for about 12 frames, and the gantry signs for about 5.
  Frames elsewhere in 42.38–56.54 are unchanged against the v4 preview (mean abs diff 0 to 0.9 grey levels, which is
  encode noise).
- Known: on the last 2–3 frames of R3 (52.40–52.48) the far gantry's small line tucks under the top of the title.

## Open questions for Jade

1. Keep light-on-dark cut faces (matches SIRENS), or ink letters straight on the plate's white faces (matches D2)?
2. Is the small overlap of the gantry with the title on R3's last frames OK?
3. Should the D3 mirror etch and the D5cu lens lyrics also come back in the rewind? (They are not signs, so they are
   still dropped.) And should C2's teaser flash of the gantry (about 7.0 s) show the new signs?
