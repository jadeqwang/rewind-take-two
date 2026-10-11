# B — Research: chase grammar in Celeste and Super Meat Boy

**Method.** Footage was downloaded and viewed frame by frame (six clips, 32 MB; one at 720p60 for frame counts). Timestamps are clip seconds. *(written)* marks a text source, not frames I saw. Contact sheets: `/tmp/claude-1000/-home-jade-Documents-rewind-take-two/97956374-655c-4276-a4d1-7cbb4a4eb414/scratchpad/games/sheets/`.

| Key | Clip |
|---|---|
| O | Celeste, Oshiro boss chase, 720p60 — https://www.youtube.com/watch?v=nK_0tjAzeag |
| B | Celeste, Old Site Badeline chase, first 90 s — https://www.youtube.com/watch?v=c6tbaPHX3_s |
| T | Super Meat Boy official trailer — https://www.youtube.com/watch?v=25cdyGMtgX8 |
| R | "Super Meat Boy – 4 replays" — https://www.youtube.com/watch?v=z2hg_pfk-p8 |
| D | "Super Meat Boy: +100 deaths" (filmed off a screen, soft) — https://www.youtube.com/watch?v=yFjSAR2h3Js |


Written sources: **[1]** Celeste `Player.cs` (public source), https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs · **[2]** Maddy Thorson's forgiveness thread, https://threadreaderapp.com/thread/1238338574220546049.html · **[3]** https://celeste.ink/wiki/Badeline_Chaser · **[4]** https://celestegame.fandom.com/wiki/Presidential_Suite (search summary only; the page would not load) · **[5]** McMillen, "Why So Hard?", https://www.gamedeveloper.com/game-platforms/-i-super-meat-boy-i-s-mcmillen-explains-why-so-hard- · **[6]** Refenes on controls, https://www.gamedeveloper.com/business/my-time-with-the-steam-controller · **[7]** https://en.wikipedia.org/wiki/Super_Meat_Boy

## Celeste

**How a dash reads (O 8.10–8.90, every frame at 60 fps).**
- There is no wind-up pose. The anticipation is a freeze: three identical frames (0.05 s) at 8.55 with her still red-haired and falling. The same hold recurs seven times in the first 32 s of O; [1] confirms `Celeste.Freeze(.05f)`.
- Next frame the sprite goes dark for one frame; then a white ring bursts at her back; by the third frame her hair is blue.
- Travel lasts about 10 frames (0.17 s), dead straight, about 11% of screen width. [1]: 0.15 s at 240 px/s against a 90 px/s run. Direction is one of eight (a diagonal at B 34.0–34.3).
- Trail: three blue silhouettes of her, dropped 4–5 frames apart, plus a white speed line. They stay where dropped and fade over about 15 frames.
- End of dash: she does not stop. She leaves at two-thirds of dash speed [1] and gravity returns. Hair stays blue for the whole fall (8.77–10.7), flashes white on landing (10.73), and is red again by 10.9. Hair colour is the "dash available" light.
- Mid-air refill: at B 34.0–34.5 she touches a floating crystal, it shatters into a white ring, and her hair flashes back to red.
- *(written)* [1] adds a 0.2 s screen shake along the dash axis; I could not see it in frames.

**Falling short, then saved (O 8.10–8.90).** Take-off 8.10; apex about 8.35; visibly descending by 8.50; freeze 8.55; flat dash 8.60–8.77. The dash fires about 0.2 s after the apex, once the arc has clearly turned down. It is horizontal, adding distance, not height. The freeze is the "she won't make it" beat.

**Forgiveness** *(written)*: she can still jump 0.1 s after leaving a ledge [1][2], and gravity halves at the top of a held jump [2].

**Chase construction.**
- *Oshiro (O).* The pursuer lives at the left screen edge (5–10% of width). She sits about 40% across, so over half the frame is lookahead, and the camera scrolls right continuously. He hovers at her height, then charges every 4–5 s (8.9, 14.3, 18.3). Telegraph: at 8.90 a white lightning bolt spans the full width at his height and the whole frame splits into RGB fringes for about 0.5 s. He crosses in about 0.85 s trailing an orange smear, exits right at 10.35 and re-forms at the left edge by 11.7. [4] agrees.
- *Badeline (B).* The pursuer is her own recorded path. A dark twin with a red smear trail repeats her moves: the spot she occupies at 33.8 is reached by the twin at 35.5. [3] gives 1.55 s, plus 0.4 s per extra chaser, growing 1→2→3→5. Each room is one static screen lasting 5–13 s, with a slide of about 0.3 s to the next (B 12.0). The threat is stopping or doubling back.

**Near-miss framing (O 9.4–10.0).** The hazard sweeps through the row she left about 0.3 s earlier. She clears him by less than her own height and comes off the top of his head. There is no cut, zoom or slow motion; the hazard is about twice her height.

## Super Meat Boy

- **Momentum and wall-jumps (T 29.7–32.5).** He climbs a shaft about three bodies wide. Saws sit on alternating walls, so the only safe line is a zigzag, at roughly 2–3 wall contacts per second, never resting. *(written)* Refenes tuned a "200MS delay" when pulling away from a wall [6].
- **Saw near-miss (T 28.3–29.6).** The saw is about four times his body width, on a swinging arm. He lands on a pillar at 28.7, slides, and jumps off at 29.2 with the rim about one body-width away. The saw passes through the spot he clung to at 29.4, about 0.25 s late.
- **Persistent trail (T 28.3–32.5).** Every surface he touches keeps a red smear, including both shaft walls and the pillar tops. [7]: the juice "left behind on surfaces that the player has touched remains."
- **Death to retry.** Not visible in my clips. *(written)* "almost instantaneous… imperative that the action never stop" [5].
- **All-attempts replay (T 60.8–63.8; R 0–12; D 10–50).**
  1. At t=0 every attempt is stacked on one spot and reads as a single character (R 0.0).
  2. Within 0.2–0.8 s the stack smears into a solid red bar along the floor and up the wall, because attempts differ by a few frames (R). On any constrained surface the bar re-forms (T 61.4–62.0).
  3. At each jump the bar fans into a sheaf of 10–15 copies on slightly different arcs, like a spread hand of cards (T 61.1, 62.3).
  4. At each hazard a cluster ends in place with a red starburst lasting 2–3 frames (T 63.0–63.2); others drop out of the bottom of frame (R 2.4–5.0).
  5. Attrition in R: about 30 at 2 s, about 6 at 6 s, 2–3 at 10 s, then one. The camera follows the survivor.
  6. What remains is one copy at the goal and a level painted by everyone's trails. *(written)* "40-plus attempts all playing at once" [5].

## Shared grammar

- Direction of travel is constant within a sequence (right in O, up in T), and the threat enters from where she has already been.
- The threat is always on screen or announced by a full-width telegraph before it arrives (O 8.90).
- Scale: Madeline is 6–8% of frame height, Meat Boy 3–5%; hazards are 2–4 times the character.
- Beat lengths: dash 0.2 s including freeze; near-miss margin 0.25–0.3 s; charge cycle 4–5 s; room 5–13 s; replay 3–12 s.

## What to steal for a 47-second chase where she only ever runs away

1. **Lock the geography.** Agents at the left edge, Jade about 40% across, the rest lookahead. Never reverse the angle.
2. **Agents follow her path on a delay.** They repeat her route about 1.5 s behind (Badeline), so standing still is the danger and nobody needs to touch her.
3. **(i) Platform → steel beam.** Let her run two or three frames past the platform lip before jumping (coyote time), hang at the apex, and land with a one-frame white flash. Keep the beam one body thick and the frame wide. Agents reach the lip 1.5 s later.
4. **(ii) Chasm.** At 24 fps: take-off; apex at about frame 6; four or five frames of visible drop with the far edge above her feet; a two-frame freeze; one dark frame; a white ring; then a flat four-frame dash covering about 11% of frame width with three afterimages left behind. Do not let the dash rise.
5. **Give her a dash light.** One colour accent (hair or jacket) flips when the dash is spent and flips back with a flash on landing.
6. **(iii) Zigzag under fire.** Turn the saw shaft on its side: change direction every 0.4 s, draw a full-width telegraph line before each shot, and land each shot where she was 0.25–0.3 s earlier, within one body height.
7. **Misses leave marks.** Each shot scars the field and her path stays drawn, so the zigzag is readable by the end.
8. **(iv) Many copies.** Start the rainbow Jades stacked as one, smear them into a bar, fan them at each jump, and thin them from about 30 to 6 to 1 over the shot. Copies peel off by falling short or fading rather than being hit. The camera stays on the real one.
9. **Budget beats.** One threat cycle every 4–5 s gives nine or ten in 47 s. Spend the freeze once, on the chasm.
10. **Stay wide.** Keep her at 6–8% of frame height for the action and let hazards be 2–4 times her size.
