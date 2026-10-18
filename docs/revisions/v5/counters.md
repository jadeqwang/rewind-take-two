# v5 counters: who dies how (2026-10-12)

Kenton's notes on the "final" v5: the ghost labelled 4,096 dies differently from the real 4096, the 1:38 HUD reads
ITERATION 4,097 ×4,097, the timer counts down, goes negative and then counts up again, and "Time Variance
[redacted]" is too on the nose. These are Jade's rulings:

- The 1:32 L-train kaizo trap → "Reload." is a **rewind, not a death**, so ×4,096 holds.
- The timer shows **this run's time**. The grass level is later in the game than the car chase, so the clock jumps
  forward at the respawn.

## 2026-10-18 renumbering (Jade)

Jade: "the first iteration we see (where she hands over her ID) [should] be iteration 1, and then the quick succession of
shots that all have different numbers be increasing. a two digit number, a few 3 and 4 digit numbers. perhaps pick numbers
of some significance before we get to 4095?"

- **C2 teaser (1.9-7.24):** the rewind rolls `ITERATION` from 4,095 all the way down to **1**, accelerating with the ◀◀
  multiplier (`inCubic`, 2.5-6.5 s), then holds on 1 into the title. It no longer ticks to 4,096.
- **Verse 1 (0:12-0:40, her ID at 0:34) is iteration 1.** It has no HUD of its own.
- **R2 death tableaux (0:42.65-0:48.42) count UP:** 42 (the Answer), 137 (1/fine-structure constant), 314 (pi), 404 (not
  found), 1,024 (2^10), 1,420 (the hydrogen line, as on her patch), 1,618 (golden ratio), 1,729 (Hardy-Ramanujan; the
  0:26 plate's TVA 1729), 2,048 (2^11), 2,520 (lcm of 1-10), 2,718 (e), 2,998 (c = 2.998e8 m/s), 4,093 (the largest prime
  below 4,096).
- 4,096 is now never shown; the ×4,096 death count in 4,097's HUD still holds.

## The map (before 2026-10-18; rows 4,081-4,093 and 4,096 are superseded above)

| Iteration | On screen | Fate | HUD |
|---|---|---|---|
| 4,081–4,093 | 0:42.65–0:48.42, the thirteen R2 death tableaux (train first) | thirteen earlier deaths, one per still | `ITERATION` flips 4,093 → 4,081, randomized but decreasing (v7; was 4,095 → 4,084, which reused 4,095 and repeated 4,084) |
| 4,094 | 1:34–1:38, the graphite ghost on the L tracks | misses the chasm jump | race HUD `GHOST: ITERATION 4,094` (was 4,096) |
| 4,095 | 0:00 cold open, mid-air jump-kick | shot by the ring of agents | `ITERATION 4,095` (was 4,096); the C2 ◀◀ teaser ticks 4,095 → 4,096 (was 4,096 → 4,097) |
| 4,096 | 0:12–0:40 verse 1, shows her ID at 0:34 | shot at 0:40 | no HUD |
| 4,097 | 0:56 car chase; 1:32 the L-train trap, which she rewinds out of ("Reload."); 1:33 L tracks; 1:38 grass | shot at the Hilbert Hotel corner, 1:50 | `ITERATION 4,097 ×4,096` throughout (the loading screen, respawn and field read ×4,096; were ×4,097) |
| 4,098 | 1:52 CONTINUE ◀◀ to the end | **canon** | TVA report `CASE 4,098` (was 4,097); the credits counter reads 4,098 at 3:46 and ticks to 4,114 (was 4,097 → 4,113) |

## The timer (4097's run clock)

- 0:56–1:32: 00:00 → 00:36, as in v5.
- From the respawn (1:33.66): `offset: RELOAD_SKIP` (210 s, `render/timeline/_B_verse2.js`), so it reads 04:07 and
  counts up to about 04:25 when she is shot. Change that one constant to move the jump.
- The race HUD (1:34–1:38) keeps the run clock on its second line, with the ghost split beside it
  (`04:08.46  +0.26`). Before, the split replaced the clock, which is what read as a timer going negative.
  Engine change: `hud` race mode takes an optional `timer`.

## TVA text

- 2:19 terminal panel and 2:20 full-screen terminal: `TVA ALERT` / `ANOMALY DETECTED.` (`tools/sections/D/build_timeline.py` TERM).
- 3:35 report: `TVA REPORT` / `ANOMALY DETECTED` / `CASE 4,098` / … (`tools/sectionF/edl.py`).
- 1:33 loading tip: `TIP: TVA agents can only follow what they can trace.`
- The 0:26 plate still reads TVA 1729.

The SFX mix is unchanged: the credits counter ticks happen at the same times, and only the digits shown changed.
