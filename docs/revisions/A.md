# Instance A: everything outside the chase (0:00–1:34 and 2:21–end)

Read `docs/revisions/README.md` first. Instance B owns 1:34–2:21 (94.06–141.00 s); leave those shots alone, except
for the two notes below that Jade gave to you even though they sit at or inside B's window (1:52 and 2:21). Tell B
before you touch either.

Start by mapping each note to its shot IDs and files (`docs/shotlist.md`, `docs/sections/A.md`, `C.md`, `E.md`,
`F.md`, the timelines in `render/timeline/`), and look at the v2 frames at each timestamp before changing anything.

## Jade's notes, verbatim

> This is a really strong start, and the bones of a really fantastic music video are there.

* strong intro, especially love the fast rewind through the whole thing, maybe we don’t need the bullet, just muzzle flare for shots
* let’s use the watercolor version of me for singing, because part of the point, I realized, is that the art style I’m rendered in mismatches the surroundings (I’ve added images to /inputs)
* let’s use the environment for some of the words, instead of all subtitles, which is also a good way of creating visual interest and keeping audience attention. I’m thinking of the way that in “Golden” from Kpop Demon Hunters, there’s large text lyrics that fit naturally into the environment (see Downloads/kdh_screenhots)
* 0:24 where it currently says “hilbert vacancy” it can display a lyric
* 0:25 - pencil is not in a coherent straight line, we should just decide that she has 2 pencils if she’s going to have 2 and just always style it consistently. (maybe
* 0:29 - pulled over - the cars should not be facing each other with the girl in the back, and it should not be a limo. it should be the black car behind the Acura on the right side of the road
* 0:30 - I really like the idea of displaying the words on the shades. an idea: you see the 3 men in shades and suits and quickly cut to a closeup of the shades (still walking, but you see the words in the shades, rendered in an Escher woodcut native typeface)
* 0:35 - ID - test should not overlay fingers. you can just have redacted bars on the card image itself. also, the entire body is half-missing and weird. maybe you should use Three.js to figure out how to stage this shot
* 0:37 - he’s holding his own id looking at the back of it? you should only see the back of an ID
* 1:24 - facial expression is too happy for this high in the air, she’s still terrified and hasn’t landed the car safely yet
* 1:26 - Chicago / US is where the steering wheel is always on the left side of the car
* 1:33 - make the redacted blocks the same typeface (or at least size) as the text around it
* 1:52 - don’t use ‘continue’ voiceover
* 2:21 - arm patch text consistency
* 3:21 - love the color and change in art style, no hime bangs, curtain bangs like in the other scenes, keep jacket styling consistent even though the world is colorful, shirt is still mock neck
* 3:05 - idea: what if, we see her swinging a pencil as though a sword but it turns into a drawing/writing motion, and the core of the pencil is rainbow colored?
* 3:13 - great colors - good time for all of them to all be traveling clockwise instead of going from down to up, and for it to be an actual infinite staircase, Escher style (do as many web searches as you want for a reference on how to draw one)
* an idea: books and other tabletop objects alongside buildings
* 3:40 - jacket consistency, and putting hair in updo with pencil – do as many google searches as you need to to see how that actually works because this is incorrect, and the door opens the wrong way, and the label on the door is weird (may as well have the information in subtitle format)

## Pointers (from the setup session, not from Jade)

- **Watercolor reference:** use `inputs/jade_watercolor_jacket_v6.png` for the singing shots. Jade confirmed on
  2026-10-11 that the jacket version is the one for this video (watercolor Jade in the canon jacket: white cropped
  jacket, orange band, pale-blue dot, `1420 MHz` arm patch, black mock-neck top). `inputs/jade_watercolor.png` is
  the earlier portrait without the jacket, kept only as a style reference. Both were copied in from
  `../moongazing-public-version/inputs/`,
  where the same watercolor singer was built; `../moongazing-public-version/review/singer_v6/` has finished
  watercolor singing clips worth studying for method. The singing shots here are S1, E3 and V3S (`media/sing/`,
  `media/sing/NOTES.md`). E3 sits at 119.44–122.95 s inside B's window, so tell B when you replace it.
- **Environmental lyrics reference:** `~/Downloads/kdh_screenshots/` (nine screenshots; the folder is spelled with
  an "s", the note has a typo). The engine's typography kit and corner-pinning are in `render/engine/README.md`.
- **The 0:25 note is cut off** mid-parenthesis ("(maybe"). Ask Jade what the rest was. The pencil count and styling
  you settle on is canon for B too, so tell B the decision.
- **1:52 "continue" voiceover:** the cue is `continue_vo` in `media/sfx/cues.json`, built by `tools/sfx/`. The audio
  mix is shared, so tell B before rebuilding it.
- **2:21 arm patch:** the reference patch reads `1420 MHz`. That spelling is the consistency target everywhere,
  including B's shots, so tell B.
- **1:33 redaction blocks** sit on the LOADING screen (V2h, 93.07–94.06 s), right at the hand-off to B.
- The cut points at 94.06 and 141.00 s are shared edges with B. Agree any change there with B first.
