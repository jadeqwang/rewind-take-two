# v4 instance A progress (the singing clips)

Updated: 2026-10-11, session start. Brief: `docs/revisions/v4/A.md`.

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

## Running now

Nothing. **Waiting for Jade's pick** (asked in the pane ~17:45): one H and one F from the contact sheet.

## Next steps, in order

1. (done) Read the v3 method scripts.
2. (done) Asked `v4-B` about the Bean framing.
3. (done) Still candidates in `media/sing/v4/stills/`, each with a JSON beside it (model, prompt, inputs, cost). Edit the
   portrait itself, so the v3 plate/restore/comp steps can follow. Vary separately:
   - hair: glossier, more natural (strands, highlights, weight), still watercolor;
   - smile: a few steps from a little less to none (closed-mouth faint, neutral/determined).
   At least two image models (nano-banana-pro, gpt-image-2.5, seedream-5-pro, maybe flux kontext). `--dry-run`
   to price first.
4. (asked, waiting) Jade picks one H and one F. **Do not animate before she picks.**
4b. Combine the picks into one portrait (free, local: both are aligned to the portrait, so paste the face oval of
   the F pick into the H pick with a feathered mask; or one nano-banana-pro call with both as references if the
   seam shows). Save as `media/sing/v4/stills/pick_portrait.png` (971x1620 geometry or 2x), show Jade once.
5. Animate the pick (v3 method: `wc_base` → `wc_paint` → `wc_restore` → `wc_comp` → `wc_takes` → `look.py` →
   `wc_post.py`), S1 and V3S only. The v3 scripts hard-code `inputs/jade_watercolor_jacket_v6.png`, `v3_` file
   names and the prompt line "begins on her painted smile and sings from it": give them a v4 source/prefix and
   rewrite that line for the picked expression. Outputs: `media/sing/first/v4_*`, `media/sing/<SHOT>/v4_take_N.*`,
   `media/sing/<SHOT>/v4_sync_1080.mp4` + `v4_sync_1080_matte/` (see "What B needs"). E3 is on hold (B's 2:00 note replaces it; ask `v4-B` first).
6. Review clips in `media/reviews/v4/A/`, manifest `docs/revisions/v4/review_A.json`. Say in the hand-over that
   Jade should listen for lip sync.

## Jade's decisions (verbatim, with time)

None yet in this session.

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

## Open questions

None.
