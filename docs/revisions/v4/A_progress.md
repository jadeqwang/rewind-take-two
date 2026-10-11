# v4 instance A progress (the singing clips)

Updated: 2026-10-11 17:50. Clock times below are local (CDT). Brief: `docs/revisions/v4/A.md`.

## Done

- Read `docs/revisions/README.md`, `docs/revisions/v4/README.md`, `docs/revisions/v4/A.md`, `media/sing/NOTES.md`
  (v3 watercolor section), `docs/revisions/streams/SING.json`, `docs/TOOLS.md`, `tools/sing/wc_base.py`,
  `tools/sing/wc_paint.py`.
- Looked at `inputs/jade_watercolor_jacket_v6.png` (971×1620, the smiling reference) and
  `media/sing/first/v3_S1_first.jpg` (2576×1449, the v3 first frame).
- Spend at start: $222.57 of $400. Disk: 21 GB free. Nothing generated yet in v4 (A's soft limit $50, tags `v4A_…`).

- Wrote `tools/sing/v4_stills.py` (`gen` makes candidates, `sheet` builds the contact sheets). Dry run: 18 calls,
  est $2.44. Hair (gloss, natural) and expression (e1 soft closed-lip smile, e2 trace, e3 neutral, e4 tense) are
  edited separately on the top of the portrait. Models: nano-banana-pro, gpt-image-2.5-flare, seedream-5-pro,
  grok-imagine-image-2.0, flux-1-kontext-max.
- `v4-B` answered the framing question (see "What B needs" below).

- **Still batch, round 1, done** ($2.44, tags `v4A_still_hair` / `v4A_still_face`; total spend $225.01).
  18 candidates in `media/sing/v4/stills/` (`<key>.png|jpg` + `<key>.json` with model, prompt, input, cost).
  Landmark-aligned copies in `_in/<key>_aligned.jpg` (portrait geometry, 971x1620), likeness numbers in
  `metrics.json`. Sheet letters → keys: `sheet_hair_keys.json`, `sheet_face_keys.json`.
  - **Contact sheet for Jade: `media/sing/v4/stills/contact_sheet_v4A.jpg`** (copy:
    `media/reviews/v4/A/stills_contact_sheet.jpg`).
  - Hair: H1 nbp gloss, H2 gpt gloss, H3 seedream gloss (strong shine), H4 grok gloss (barely changed),
    H5 kontext gloss (**reject**: repainted her face, no glasses), H6 nbp natural, H7 gpt natural, H8 seedream
    natural (H6-H8 turned the hair brown; canon is black).
  - Expression: F1 nbp / F2 gpt small closed-lip smile; F3 nbp / F4 gpt / F5 seedream a trace; F6 nbp / F7 gpt /
    F8 seedream neutral; F9 nbp / F10 gpt tense (these read sad or tired).
  - Resolution: nbp 1.9 px per portrait px, seedream 1.83, gpt only 1.05 (the film uses 1.37, so a gpt pick is
    slightly soft and should be re-made or upscaled for the final still).
  - seedream-5-pro `size` must be multiples of 16 and at most 4,194,304 px: `1792x2240` works.
- Manifest started: `docs/revisions/v4/review_A.json` (status `question`).

- **Combine step ready:** `tools/sing/v4_pick.py HAIR_KEY FACE_KEY` (MPY venv, no paid call) lays the F pick's face
  into the H pick's hair on the portrait at 2x (1942x3240) → `media/sing/v4/stills/pick_<hair>+<face>.png`, `.json`,
  `_check.jpg`. Tested on two example pairs (H1+F3, H2+F6): no visible seam, glasses line up. Examples for Jade:
  `media/sing/v4/stills/combined_examples_v4A.jpg` (copy `media/reviews/v4/A/stills_combined_examples.jpg`).
- **Animation scripts take a version switch** (`WC_VER=v4`; the default is still v3 and the v3 take prompts are
  byte-identical, checked by hash): `wc_base.py` (also `WC_SRC=<pick png>`, `WC_SRC_SCALE=2`), `wc_paint.py`,
  `wc_restore.py`, `wc_comp.py`, `wc_takes.py` (v4 prompt: she never smiles, tense and determined; S1 1968 and
  V3S 1992 characters of the 2000 cap; tags `v4A_sing_<SHOT>`), `wc_post.py` (`SYNC_V4` is empty until the takes are
  measured; writes `v4_sync_1080.mp4`). Not committed yet at the time of this note if `git status` shows them
  modified. The v4 prompt wording assumes an unsmiling pick: if Jade picks F1/F2 (small smile), soften `LOOK["v4"]`
  and `V4` in `wc_takes.py`.

- **Jade asked for a combo sheet (17:15):** H1, H2, H3 × F5, F6, F7, F10 → 12 combined stills
  `media/sing/v4/stills/pick_<H>+<F>.png` (2x portrait, each with `.json` and `_check.jpg`), sheet
  `media/sing/v4/stills/combos_H123_F5-6-7-10.jpg` (copy `media/reviews/v4/A/stills_combos_H123_F5-6-7-10.jpg`).
  No paid calls. Keys: H1 `hair_gloss__nbp_1`, H2 `hair_gloss__gpt_1`, H3 `hair_gloss__sdr_1`, F5
  `face_e2_trace__sdr_1`, F6 `face_e3_neutral__nbp_1`, F7 `face_e3_neutral__gpt_1`, F10 `face_e4_tense__gpt_1`.
  F7 still measures a slight smile (0.18); F5, F6, F10 measure none.

- **v4 first frames done** (17:32). `media/sing/first/v4_S1_first.jpg` (over `plate_close_1`), `v4_V3S_first.jpg`
  (over `plate_truth_1`), `v4_her_mask_first_frame.png`, `v4_fig.jpg` + `v4_her_alpha.png` (sheet geometry). Copies
  for review: `media/reviews/v4/A/still_S1_first_frame.jpg`, `still_V3S_first_frame.jpg`.
  - **Method changed from v3: no repaint.** `wc_paint.py` with the new portrait shrank her to 0.77x on both tries
    (`media/sing/first/v4_paint_wc_{1,2}.*`, rejected, $0.27). Instead `tools/sing/v4_first.py`: the pick on a paper
    sheet in v3 geometry (`v4pick_sheet.jpg`), BiRefNet matte straight off the portrait
    (`WC_VER=v4pick $EPY tools/sing/wc_comp.py matte …` → `v4pick_her_alpha.png`, clean, no blossom), composited over
    the plates; the sleeve ends past the portrait's edges come from the v3 figure. Every pixel of her is the pick's.
  - Against v3: same x0/y0/scale; bottom-row figure span v3 673-1928, v4 674-1938 (crop px of 2576); matte area
    x1.011. `v4_base16.jpg` / `v4_base.json` exist too (from `wc_base.py`, x0 pinned to 724) but are not used.

- **Takes done** (17:39; 4 x Seedance 2.5 720p, $6.94; spend total about $232.21). All 16:9, none reframed, none
  smile. Lags from `look.py` (`media/sing/<SHOT>/v4_take_N.look.json`, `_look.jpg`, `_win.jpg`):
  - S1 `v4_take_1` **pick**: closures +0.47 / +0.41, opening +0.49 → one lag +0.45. Blink at about 16.2 (off her, on
    the cutaway). `v4_take_2`: lag drifts 0.39 → 0.66, eyes closed at 12.9; spare.
  - V3S `v4_take_2` **pick**: closures +0.04 / +0.06, corr +0.13 (r .68) → one lag +0.09. Blinks at about 154.05 and
    157.1. `v4_take_1`: no blinks, but mouth runs at 0.9x (lag 0 → -0.3), would need a retime; spare.
- **Synced files done** (`SYNC_V4` in `tools/sing/wc_post.py`; untouched frames, 0 cross-fades):
  `media/sing/S1/v4_sync_1080.mp4` (7.46 s), `media/sing/V3S/v4_sync_1080.mp4` (5.54 s); file time 0 = shot in.
  Mattes: `media/sing/S1/v4_sync_1080_matte/` (179 PNG), `media/sing/V3S/v4_sync_1080_matte/` (133 PNG), BiRefNet on
  the synced file, no grow. Plain review clips (take + song, not rendered in the film):
  `media/reviews/v4/A/0012_singing_S1_take.mp4`, `0233_singing_V3S_take.mp4`.

- **Checked against v3** (17:40): face height 343.7 vs 341.5 px, eye midpoint within 2 px on frame 0; S1 take matte
  bottom span 478-483 / 1422-1429 (v3 472-484 / 1417-1427), no gap on any frame; matte clean over pale paper.
  `v4-B` told and agreed (it is not editing A.js / E.js; its Bean push for S1 waits on Jade's go and will build on the
  v4 paths).
- **Timelines point at v4** (17:41, uncommitted until the preview renders pass): `render/timeline/A.js` `S1_SRC` and
  the `A_S1_lyric` `HER.src` matte dir; `render/timeline/E.js` `V3S_SRC` and the `V3S_lyric` `HER.src`.

- **Rendered in the film** (17:42, 540p preview): `media/reviews/v4/A/0012_singing_S1.mp4` (12.6-19.64),
  `media/reviews/v4/A/0233_singing_V3S.mp4` (153.98-159.14). Both checked on frame sheets: lyric arcs sit behind her
  with the v4 mattes, no smile, hair holds. V3S opens with her eyes closed for 6 frames (0.25 s).
- **Manifest** `docs/revisions/v4/review_A.json`: status `done`, with one question (the V3S opening blink).
- **Notes** `media/sing/NOTES.md`: v4 section added. Timelines, docs and scripts committed.
- **Spend:** v4A total $9.64 of the $50 soft limit (stills $2.44, rejected repaint $0.27, takes $6.94).

## Running now

Nothing. **Jade approved both clips** (see decisions). A's brief is done unless B's Bean push needs a re-check (step 8).

## Next steps, in order

1. (done) Read the v3 method scripts.
2. (done) Asked `v4-B` about the Bean framing.
3. (done) Still candidates in `media/sing/v4/stills/`, each with a JSON beside it (model, prompt, inputs, cost). Edit the
   portrait itself, so the v3 plate/restore/comp steps can follow. Vary separately:
   - hair: glossier, more natural (strands, highlights, weight), still watercolor;
   - smile: a few steps from a little less to none (closed-mouth faint, neutral/determined).
   At least two image models (nano-banana-pro, gpt-image-2.5, seedream-5-pro, maybe flux kontext). `--dry-run`
   to price first.
4. (done) Jade picked H2+F6.
4b. Combine the picks into one portrait (free, local: both are aligned to the portrait, so paste the face oval of
   the F pick into the H pick with a feathered mask; or one nano-banana-pro call with both as references if the
   seam shows). Save as `media/sing/v4/stills/pick_portrait.png` (971x1620 geometry or 2x), show Jade once.
5. (done) Animate the pick (v3 method, except the first frames, see above: `wc_base` → `wc_paint` → `wc_restore` → `wc_comp` → `wc_takes` → `look.py` →
   `wc_post.py`), S1 and V3S only. The v3 scripts hard-code `inputs/jade_watercolor_jacket_v6.png`, `v3_` file
   names and the prompt line "begins on her painted smile and sings from it": give them a v4 source/prefix and
   rewrite that line for the picked expression. Outputs: `media/sing/first/v4_*`, `media/sing/<SHOT>/v4_take_N.*`,
   `media/sing/<SHOT>/v4_sync_1080.mp4` + `v4_sync_1080_matte/` (see "What B needs"). E3 is on hold (B's 2:00 note replaces it; ask `v4-B` first).
6. (done) Review clips and manifest; hand-over says to listen for lip sync.
7. If Jade wants a blink-free V3S: `WC_VER=v4 $PY tools/sing/wc_takes.py submit V3S --note="no blink at the start"`
   (about $1.62), `look.py V3S v4_take_3`, set `SYNC_V4["V3S"]` in `wc_post.py`, `sync`, `matte`, re-render
   153.98-159.14. Or use spare `v4_take_1` with knots (153.98, 0.29), (154.722, 0.958), (157.12, 3.125),
   (159.14, 5.25): rates about 0.9, so every frame is a cross-fade.
8. When `v4-B` puts the wide Bean push into `A.js` (waiting on Jade's go), re-check S1 lip sync at small scale and
   re-cut `0012_singing_S1.mp4` if B asks.

## Jade's decisions (verbatim, with time)

- 17:15, Jade: "can you show me H1, H2, H3, combined with F5, F6, F7, f10 on a sheet?" (done).
- 17:25, Jade: "let's go with H2+F6". **The pick is `media/sing/v4/stills/pick_H2+F6.png`** (hair `hair_gloss__gpt_1`,
  face `face_e3_neutral__nbp_1`). Unsmiling, so the v4 take prompt in `wc_takes.py` stands as written.

- After watching `0012_singing_S1.mp4` and `0233_singing_V3S.mp4`, Jade: "both of those look good, i didn't even notice
  blinking". Both takes approved; no blink-free V3S take needed (step 7 is off).

## What B needs (v4-B, 2026-10-11 ~17:25)

- S1: her on the plate as `media/sing/S1/v4_sync_1080.mp4` **and** a per-frame matte dir
  `media/sing/S1/v4_sync_1080_matte/` (B lifts her onto a new wide Bean plate; the on-plate file is the fallback
  and the end framing). Chest-up is enough.
- Keep the v3 figure scale, position and bottom cut line exactly (B shows her at 40-45 % of v3 scale at the
  widest, anchored to the bottom edge, pushing in to the v3 framing by about 13.9 s).
- No camera move or zoom baked into the take. Clean hair edge in the matte (she sits over a brighter plate at
  the start).
- In/out unchanged: S1 12.60-19.64 (on her 12.60-16.14), V3S 153.98-159.14. V3S keeps its v3 framing.
- E3 is going (replaced by game action). Do not remake it.
- In `render/timeline/A.js` B edits S1's layers (plate, scale, kenBurns) and the `A_S1_lyric` overlay; A changes
  only `S1_SRC` / `S1_IN`. B builds against the v3 files until ours land. Tell B before editing.

### More from v4-B (~17:15), for the S1 take

Previz: `media/reviews/v4/B/plans/bean/previz.mp4`, plan `docs/revisions/v4/plans/bean.md`.
1. Matte dir is `<take file minus .mp4>_matte/` (`v4_sync_1080_matte/`), tight like v3's: BiRefNet on the synced
   file, no grow, no extra feather (she sits over pale paving at 42 % scale; a grown matte carries a dark rim).
2. Her figure must reach the bottom edge of the frame across her whole width on every frame 12.60-13.92, arms at
   her sides as in v3 (she is anchored to that edge while small).
3. Behind her keep `plate_close_1` in the v3 crop: no baked push, grain or grade.
4. Tell B if her scale, position or bottom cut line moves more than a few px from v3.
B's push runs 13.04-13.92: she is small (face about 13 % of frame height) on "The" at 13.20, full size by
"before". B has not edited `A.js` for S1 yet.

## Open questions

None.
