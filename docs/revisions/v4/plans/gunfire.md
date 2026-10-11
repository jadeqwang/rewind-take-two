# v4 plan: the gunfire on the lawn (notes 1:39 and 1:41)

Status: **built** (v4B-gun, 2026-10-11, 18:40); see Execution. Blockout: `media/reviews/v4/B/plans/gunfire/contact_sheet.jpg`.

## Execution (keep current; resume from here)

**State 2026-10-11 18:40: built and handed over.** After clip `media/reviews/v4/B/0139_gunfire.mp4` (96.3-105.5,
540p, song audio only, 6 MB), stills `media/reviews/v4/B/0139_gunfire_{99.4,101.2,103.0}.jpg`, fragment
`docs/revisions/v4/fragments/gunfire.json`. Spend on `v4B_gun`: **$4.76** of the $12 cap (13 nano calls, 5 Seedance
takes). No commits.

Jade's decisions (relayed by v4-B): "gunshot - go with the earpiece closeup"; "frame height seems fine, only 2 agents
firing is fine". So: G1 98.28-100.70 (B, B, C, C); G2 100.70-102.46; earpiece close-up G3 102.46-104.22. The cut at
98.28 is unchanged. "grass" (102.395) stays the lower third over G3 (`C_lyr_grass`, unchanged).

What is in the timeline:
- `render/timeline/_B_verse2.js`: `const V4_GUN = true` pushes `gunfireShots()` in place of `B2_lawn`, `B2_lawn2`,
  `B2_ear`. The v3 code is kept in the `else` branch (set `false` for before/after). Nothing else in the file changed.
- New: `_B_gunfire.js` (shots B2_G1, B2_G2, B2_G3), `_B_glayout.js` (lawn in metres, G1 camera, agent aim/recoil),
  `_B_gunribbon.js` (her ribbon on the grass), `_B_gtrack.js` / `_B_ggun.js` (generated data: Jade's track in the G1
  take, C's muzzle + barrel in the G2 take). `_B_fx.js` unchanged: misses use the existing `traceMiss`.
- How each miss is made coherent: G1, muzzle = the cut-out's muzzle after the engine turns it to point at the impact
  (impact = her layout position 0.25 s earlier, on the grass, projected each frame). G2, muzzle and barrel direction are
  read off the take frame by frame (`tools/v4B/gunfire/gun_track.py`); both impacts lie on that barrel line, and her
  path was laid through those points (100.70 and 100.55), so no line crosses her. Checked frame by frame at each miss.

**Tell v4-B (not edited by me):** the `b_miss_board` cue at 101.14 (`tools/sfx/build.py`) is now a miss into turf, not
the board; the time is unchanged. The other five gunshot cues are unchanged.

Files: keyframes and takes in `media/shots/B_g1world`, `B_g1clean`, `B_g2`, `B_g2clean`, `B_g3ear`, `B_gagent`
(rejected), `B_gcut` (the cut-out); each has a `NOTES.md` (prompts, models, verdicts). Tools: `tools/v4B/gunfire/`
(`gen.py`, `cutout.py`, `track.py`, `gun_track.py`, `blockout.py`).

Rejected along the way: gagent v1-v4 (head cut off), g1world v1 (Jade too big), g2 v1 (Jade side-on), g2 take_1 (she
turns back toward the agents), g2 take_2 (she runs beside the pistol and gets an orange muzzle flash).

Open: (1) G1 agents are a still cut-out (turn + recoil only). (2) G2's C aims low, so misses land a few metres behind
her. (3) B's arm swings wide toward her as he raises it to his ear (101.0-101.3). (4) Jade is upscaled about 1.5x in
G2. (5) No SFX in the after clip (song only).

## What changes

The three v3 lawn shots (side view, 98.28–104.22) become two shots seen from **behind the agents**, looking down
the lawn at her and the Hilbert. Agents: A (left), B (right) on a firing line, C a few metres ahead of them.

| Shot | In–out | Picture | Lyric | Misses (muzzle → where it lands) |
|---|---|---|---|---|
| chasm (kept) | 96.30–98.28 | unchanged | unchanged | |
| **G1** | 98.28–100.70 | Behind A's and B's shoulders. The camera starts slowly, drives between the two of them and settles over C's shoulder (about 6 m of travel, lens tightening). She zigzags away, 19 m off at the cut, 29 m by the end; a turn every second beat, so each zig is about 5 m wide and her orange ribbon draws it on the grass. | `I ZIGZAG` painted on the lawn in the gap between the shoulders, like a road marking; word-timed (98.28, 98.47, 98.78) | 98.94 B, 99.38 B, 99.82 C, 100.26 C. Each lands where she was a quarter second earlier, fired from 18–21 m. |
| **G2** | 100.70–104.22 | Long lens from further back. A and B fill the frame edges with their backs to us; C stands between them, further on. Only C fires. A's hand goes to his earpiece (there by 100.95), then B's (101.58). On the 102.46 downbeat the lens snaps in; C lowers his pistol at 102.90: she is 38 m off and gone. | `ACROSS THE / FIELD OF GRASS` on a notice board beyond her, all five words, word-timed. She crosses in front of the board's blank lower half, so she never covers a letter. | 101.14 C: through the spot she left and on into the board (a hole). 102.00 C: turf. Both a whole beat behind her now. |
| side-scroll (kept) | 104.22– | unchanged: the pack starts far back | unchanged | |

What this answers:
- **Close range.** Every shot is fired at a sprinting, cutting target 20–27 m away.
- **Bullets vs. guns.** Seen from behind, each line runs from a pistol into the picture along its barrel to a
  point she has already left. The shot always comes from the side she is running away from, so no line crosses her.
- **One fires, two call.** That is all of G2, and it has 3.5 s to be read. A never gets a shot off in G1; he is the
  first to call it in.
- The v3 earpiece shot (102.46–104.22) goes: its job is done inside G2, and "grass" lands on the board with the
  rest of its line.

Two costs of the staging, so you are not surprised: she is smaller (15% of frame height at the first frame, about
22% from 100 s on; v3 has her at half the frame), and we see her back, not her face. Her jacket's blue circle,
the bun and pencils, and the ribbon carry her.

## How it is made

Layers in the engine, so the camera move and every position are ours:
1. **Lawn and hotel:** one clean engraved still per shot (nano-banana-pro with the v3 hotel and level references, 2K,
   no people; G2's has the blank notice board).
2. **Agents:** one keyframe per shot of the three from behind, large, on blank paper (v3 agent sheet as reference),
   then one Seedance take each with a locked camera: G1 they fire and recoil; G2 two lower their pistols and put two
   fingers to the earpiece, one keeps firing, then lowers. Engraved; keyed off the paper; one cut-out per agent.
3. **Jade:** a keyframe and a Seedance take of her sprinting away, seen from behind, large in frame, with hard cuts
   left and right. Matted as in v3, retimed so her turns land on the beats, composited small at her true spot.
4. **The push** is an engine move: each agent cut-out and the plate get their own keyed position and scale from the
   blockout's camera, so the shoulders slide past while the lawn only tightens. No generated camera move.
5. **Tracers:** the existing `traceMiss`, given each muzzle (known, because we place the agents) and each landing
   point (known, because we place her). Nothing is tracked by eye.

## Cost

Keyframes and plates 5 × $0.13; Seedance 720p takes: agents ×2 and Jade ×2 at $0.75. First round **$3.70**; with
one retake of everything **about $7.50**; I would stop and ask at **$12**. Budget for both notes was $25.

## Risks

- Agents on blank paper may look pasted onto the lawn. They are framed from the knees up, so no feet to plant;
  fallback is to generate them standing on the lawn plate and cut them out with a clean plate behind.
- From behind, "talking into an earpiece" is an elbow and a hand. I will ask for B's head turned in profile towards
  A so a jaw moves. If it still does not read, see question 1.
- G2 is 3.5 s, twice the length of its neighbours. The snap-in on 102.46 and C lowering his pistol are there to hold
  it.
- `I ZIGZAG` is steeply foreshortened and slides out under the camera by about 100.0; it is clear for 1.5 s.

## Questions for Jade

1. **G2 as one 3.5 s shot** (default), or keep the cut on 102.46 and go to a close shot of the earpiece for the last
   1.8 s (about $2 more; "grass" would go back to a lower third, as in v3)?
2. **Her size:** about a fifth of the frame height, back to camera, for these six seconds. Fine, or should she be
   nearer (at a third of the frame she is about 12 m from the nearest gun)?
3. **G1 shooters:** B, B, C, C, with A only aiming. Fine, or do you want all three to fire? (Then the push stops at
   their shoulders instead of passing them, so A's pistol stays in frame.)

---

## Build notes (for whoever builds it; not needed to approve)

- Blockout tool: `~/Documents/moongazing/.venv/bin/python tools/v4B/gunfire/blockout.py` (PIL only, about 5 s).
  The layout is the first block of the file: Jade's turn points, agent positions, camera keys, shot times,
  lag. It writes the stills, two top views, `contact_sheet.jpg` and `geometry.json` (metres, camera keys, and the
  960×540 pixel position of every muzzle and impact in each still; `checks` lists, per miss, the on-beat clearance
  between the line and Jade and whether muzzle and impact are in frame: all six pass).
- Beats checked in `analysis/cinematic/timing.json`: 98.50, 98.94, 99.38, 99.82, 100.26, 100.70, 101.14, 101.58,
  102.00, 102.46, 102.90, 103.34, 103.76, 104.22 are tracked beats; 100.70, 102.46, 104.22 are downbeats.
  **98.28 is not a beat**: it is the first word of "I zigzag", halfway between 98.06 and 98.50. v3 already cuts
  there and this plan leaves that cut alone; moving it to 98.50 is v4-B's call.
- Miss times are v3's, so the six gunshot cues in `tools/sfx/build.py` (98.94, 99.38, 99.82, 100.26,
  `b_miss_board` 101.14, `b_miss_turf` 102.00) need no retiming. No cue sat on the 102.46 cut.
- Timeline: replace `B2_lawn`, `B2_lawn2`, `B2_ear` in `render/timeline/_B_verse2.js` with `B2_G1`, `B2_G2`; drop
  the `C_lyr_grass` lower third (102.46–104.17); the HUD overlays are untouched. `pin` takes keyed `corners`,
  `traceMiss` a keyed `origin` and explicit `targets`, layers keyed `x`/`y`/`scale`: stock modules are enough.
  `HILBERT` (woodcut billboard) shows only at the start of G1; the lens loses it after that.
- The plate is scaled, not re-projected, so near turf slides a little against a true dolly. It is hidden under the
  agents and the lettering; if it shows, project the plate on a ground plane in a small `three` layer.
- Layout cheats: the hotel is backdrop (drawn at v3's size, 235 m off in the layout); C walks forward at 1.2 m/s
  while he fires, which is what puts him between A and B for G2.
- Prices: nano-banana-pro $0.134 per image, Seedance 2.0 720p $0.15/s (from `media/genlog.jsonl` and
  `media/gen/spend.jsonl`). Spend when this was written: $224.71 of $400. Tag calls `v4B_gun_`.
- Order of work once approved: plates → agent and Jade keyframes (show Jade the stills) → takes → engrave
  (`flock media/.engrave.lock`) → cut-outs → timeline → 540p after clip → `docs/revisions/v4/review_B.json`.
