# C_coop: the co-op level (v4, 129.18–134.88 s) and the E5/E6c fixes

Plan and status: `docs/revisions/v4/plans/coop.md`. Tools: `tools/v4B/coop/`. Spend tag prefix `v4B_coop_`.

## Keyframes (google/nano-banana-pro, 2K 16:9; prompt text saved beside each file as `*.prompt.txt`)

| File | How | Verdict |
|---|---|---|
| `kf_c1_v1.jpg` | text + canon ref; the model coloured BLUE itself | rejected: perspective view, pencil not on her path |
| `kf_c1_v2.jpg` | same + flat layout sketch | rejected: still perspective; BLUE costume drifted (no chest band) |
| `kf_c1_v3.jpg` | layout sketch (`layout_c1.png`) + identical canon twins | good layout; headphones on their heads |
| `kf_c1_v4.jpg` | edit of v3: headphones to neck, chest band | lost the bun and pencils |
| `kf_c1_v5.png` | edit of v4: bun back (refs v3 + canon) | headphones back on heads |
| **`kf_c1_v6.jpg`** | edit of v5: headphones only (ref v4) | **used**: bun with two pencils, headphones round the neck, chest band |
| `kf_c1_v7.png` | edit of v6: girls moved back | rejected: the left girl grew |
| **`kf_c1_v8.png`** | composite (`assets.py`): plate + pencil/buttons + both girls from take_1 frame 0, shifted left | **used for take 2** |
| `kf_plate_v1.jpg` → `plate.png` | edit of the engraved take 1 frame 0: girls, pencil and buttons removed | the clean plate |
| **`kf_c2_v1.jpg`** | edit of v6: left girl springing off the left button, right girl pressing the right button, two agents at the left edge (agent ref) | **used** |

No seed is exposed by the catalog for nano-banana-pro. The twins are identical in the keyframes; BLUE (the girl further
right) is recoloured after the engrave by `tools/v4B/coop/recolor.py`.

## Takes (bytedance/seedance-2.0, 720p, 5 s, camera_fixed; prompts in `tools/v4B/coop/gen.py` VID)

- `c1/take_1.mp4` from `kf_c1_v6.jpg`: not used for the girls (the girl ahead starts over the gap); not used at all now.
- **`c1/take_2.mp4`** from `kf_c1_v8.png`: run in, left girl crouches on the button (1.6), right girl waits at the lip,
  crosses 3.25–4.0 and crouches on the far button (4.3). Used for C1.
- **`c2/take_1.mp4`** from `kf_c2_v1.jpg`: 0–1.9 used (spring, grab, crawl to the lip, landing); 1.5–2.25 the agents
  dive into the gap (not shown: their matte is frozen at 1.1); 3.56–4.88 used (let go, run out).
- Engraved with `tools/v4B/coop/gen.py engrave` (`take_N_engraved.mp4` + `take_N_matte/`).
- Derived layers (`level.py`): `c1t2_*`, `c2t1_*`, `c1t1_*` = `_bo.mp4` (BLUE recoloured), `_L`/`_R` girl mattes, `_ag`
  agent matte. Sprites (`assets.py`): `pencil.png`, `btn_l.png`, `btn_r.png`, `patch_hinge.png`, `patch_strip_*.png`.

## Other media here

- `animatic/p2.png`–`p9.png`: storyboard panels at 1920×1080 (`tools/v4B/coop/storyboard.py --animatic`).
- `two_bo/take_1_engraved_bo.mp4`: `media/shots/B_two/take_1_engraved.mp4` with the right twin recoloured BLUE (E6c).
- `e5_arm/ghost_matte/`: the gold ghost's matte with her pointing forearm and hand recovered (`armfix.py`);
  `e5_arm/ghost_slideptb_v4_{rgb,alpha}.mp4`: the ghost rebaked from it (`tools/sections/D/ghostseq.py ... "#C9A227" ... 0.85 4.4333`).
- v6 (`tools/v4B/coop/e5feet.py`): `e5_arm/ghost_matte_v6/` (the gold ghost's left leg, take frames 19-39, moved in from the
  live matte; v6b also her left trouser edge beside the protagonist's sneaker, frames 36-89) and `e5_arm/live_v6/`
  (PNG + `matte.mp4`, the jade layer's matte: leg and trouser edge out, sneaker soles and two trouser holes back in); `e5_arm/ghost_slideptb_v6_{rgb,alpha}.mp4` rebaked from `ghost_matte_v6` with the same ghostseq.py arguments.
- `layout_c1.png`, `layout_c2.png`: composition sketches given to the image model (`layout.py`).

Cost: $3.46 (3 keyframes, 6 edits, 3 Seedance 720p takes), tag prefix `v4B_coop_`.

## Phase 3 (Jade's notes on the co-op clip)

- `kf_agents_v1.png` (nano, agent ref): two agents sprinting right on blank paper; too large, so `kf_agents_v2.png` is it scaled 0.36 onto paper (free).
- `agents/take_1.mp4` (Seedance 2.0 720p 5 s from v2): run in place 0–2.3, thrown up-left 2.3–3.3, land 3.5–4.0, sit up 4.25+. Matte `agents/take_1_matte.mp4` (`tools/v4B/coop/agents.py`: ink + small-hole fill; the springboard wedge the model drew is removed).
- `hinge.png`, `patch_tail.png` (`tools/v4B/coop/hinge.py`): the drawn iron hinge at the near lip.
- Phase 3 cost $0.88; total $4.34.
