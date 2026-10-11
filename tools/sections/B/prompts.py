"""Revision B prompts: design references, keyframes (KF) and Seedance motion prompts (VID).
One level, always left to right: L station platform -> steel beam -> chasm -> lawn by the Hilbert -> hotel corner -> hotel wall
-> the tabletop roof (Escher's "Still Life and Street"). Plan: docs/revisions/B_research.md"""

JREF = "media/shots/_B_refs/jade_ref_v3.png"            # canon turnaround + rev-A's two-pencil bun sheet, stacked
AGENT = "media/design/takes/agent_turn_nano_t2_styleref.jpg"
HOTEL = "media/shots/B_hilbert/kf_v1.jpg"
LEVEL = "media/shots/B_level/kf_v1.jpg"

DAY = ("Bright day, drawn as an M.C. Escher wood engraving: mostly warm off-white paper with crisp black ink line work "
       "and dense hatching in the shadows, no gray wash. ")
STYLE = ("Rendered as an M.C. Escher wood engraving / lithograph: crisp black ink lines on warm off-white paper, dense "
         "precise parallel hatching and cross-hatching that follows form, high contrast, no gray wash, no color anywhere "
         "except the girl. The girl is a full-color anime character (clean cel shading) exactly matching the reference "
         "sheet. Full bleed, edge to edge, no border, no margin, no paper edge, no frame, 16:9. No text, no letters, no "
         "numbers, no signature, no watermark.")
STYLE_NOGIRL = ("Rendered as an M.C. Escher wood engraving / lithograph: crisp black ink lines on warm off-white paper, "
                "dense precise parallel hatching and cross-hatching that follows form, high contrast, no gray wash, no "
                "color anywhere. Full bleed, edge to edge, no border, no margin, no paper edge, no frame, 16:9. No "
                "signature, no watermark.")
NOTEXT = "No text, no letters, no numbers anywhere. "
JADE = ("The girl is EXACTLY the anime girl from the attached character reference sheet: same face, same anime drawing "
        "style and cel shading, black hair with a centre part and long curtain bangs swept to both sides, and exactly her "
        "outfit: white cropped bomber jacket with one orange band across the chest and around both sleeves, small "
        "pale-blue dot patch on her left chest, round white roundel patch with a black ring reading '1420' over 'MHz' on "
        "her LEFT upper sleeve only, black mock-neck crop top, navy-blue wide-leg cargo pants with hanging orange straps, "
        "chunky white sneakers, orange over-ear headphones resting around her NECK (never on her head). ALL of her long "
        "hair is gathered up into a bun high on the back of her head, with TWO yellow wooden pencils crossed in a narrow "
        "X through the bun exactly as in the bun close-ups of the reference sheet (one with a pink eraser, one with a "
        "pale-blue eraser, erasers pointing up); no long hair hanging down her back. ")
TWINS = ("There are two identical copies of the same girl in this picture (the same character twice, same face, same "
         "outfit, both in full color). ")
AGENTS = ("The agents are EXACTLY the men of the attached engraved agent reference sheet: identical plain black narrow "
          "suits, white shirts, thin black ties, opaque black sunglasses, nearly blank mannequin-like engraved faces with "
          "no expression, short slicked hair carved as tight parallel lines, a coiled earpiece wire behind the ear. They "
          "are drawn in the same black-and-white engraving as the world, never in color. ")
SIDE = ("Exact side view like a 2D side-scrolling platformer video game: the camera is perpendicular to her path, horizon "
        "level, and everything travels from left to right. ")
HILBERT = ("The Hilbert Hotel is exactly the hotel of the attached hotel reference: a grand 1920s Chicago lakefront hotel, "
           "a broad thirteen-storey limestone block with a rusticated base of tall arched ground-floor windows, regular "
           "rows of windows above, a heavy stone cornice, and on its flat roof a steel gantry carrying a large two-panel "
           "billboard sign framed with rows of light bulbs. ")
LEVELREF = "Match the place shown in the attached wide location reference (same structures, same engraving). "

KEEP = ("Keep the first frame's look: the world stays a crisp black-and-white Escher-style wood engraving, only the anime "
        "girl in full color with her exact outfit (white cropped bomber with orange band, navy cargo pants, orange "
        "headphones round her neck, black hair in a bun with two crossed yellow pencils). Her face keeps its shape, "
        "forehead smooth, never a face close-up. No text, no letters, no logos.")
KEEP_NOGIRL = ("Keep the first frame's look: everything stays a crisp black-and-white Escher-style wood engraving, no "
               "color, no gray wash. No text, no letters, no numbers.")
LOCK = "Static locked-off camera: the camera does not move, pan or zoom at all; the background stays perfectly still. "
TRACK = "The camera tracks sideways at exactly her speed, side-scrolling like a 2D platformer, never turning. "

KF = {
    # ---- design references (no characters) -------------------------------------------------------------------------
    "hilbert": dict(refs=[], prompt=DAY + (
        "Architectural view of a grand 1920s Chicago lakefront hotel, modelled on the Drake Hotel, seen from across a "
        "wide open lawn in three-quarter view so that its long front and one side wall and the sharp corner between them "
        "are all visible: a broad thirteen-storey limestone block, a rusticated base with tall arched ground-floor "
        "windows and a striped awning over the entrance, regular rows of windows above, a heavy stone cornice at the "
        "top, a plain side wall with a zigzag iron fire escape. On the flat roof a steel lattice gantry carries a large "
        "two-panel billboard sign, each panel framed with a row of round light bulbs; the two panels spell one word "
        "between them in tall bold capital letters: HILBERT. That is the only writing in the picture. Flat mown lawn in "
        "the foreground carved as flowing engraved strokes, a few trees, Lake Michigan and a low horizon beyond. ") +
        STYLE_NOGIRL),
    "level": dict(refs=[HOTEL], prompt=DAY + (
        "A very wide side elevation of one continuous place, like the map of a side-scrolling platformer level, read "
        "from left to right at one constant scale, camera perfectly side-on and level. From the left: (1) an elevated "
        "Chicago 'L' train station platform high above the street, a wooden plank deck on riveted steel trestle girders "
        "with a wooden canopy on cast-iron posts; (2) at the platform's right end the deck stops and a single bare "
        "riveted steel I-beam, no thicker than a person, continues to the right in mid-air on one slender column; (3) "
        "the beam ends over a deep chasm, a gap where the span is missing, the street and tiny cars far below; (4) on "
        "the far side of the chasm a stone retaining wall topped by a broad flat mown lawn at the same height as the "
        "beam, running a long way to the right, with a few small trees; (5) at the far right the lawn ends at the "
        "attached hotel, a thirteen-storey limestone block with a rooftop billboard sign on a gantry, its sharp corner "
        "and side wall facing us. Lake Michigan's horizon behind everything. No people. ") + NOTEXT + STYLE_NOGIRL),

    # ---- Verse 2: the level, played once ----------------------------------------------------------------------------
    "plat": dict(refs=[JREF, AGENT, LEVEL], prompt=DAY + SIDE + LEVELREF + (
        "On the elevated 'L' station platform (the left part of the location reference): a wooden plank deck runs "
        "straight across the lower third of the frame from edge to edge, with the wooden canopy on cast-iron posts "
        "overhead. Two large rectangular station sign boards hang from the canopy beam in the upper half of the frame, "
        "side by side, each about a quarter of the frame wide, both completely blank white. Open sky and the lake "
        "horizon behind. The girl sprints from left to right along the deck at about one third of the way across the "
        "frame, mid-stride, leaning forward, her full body about 40% of the frame height. At the far left edge of the "
        "frame two agents burst out of a stairwell onto the platform, running after her, partly cut off by the frame "
        "edge. The right half of the platform ahead of her is empty. ") + JADE + AGENTS + STYLE),
    "leap": dict(refs=[JREF, LEVEL], prompt=DAY + SIDE + LEVELREF + (
        "Wide shot. The right-hand end of the elevated station platform fills the left 40% of the frame: the plank deck "
        "at mid height, ending in a clean lip, on riveted steel girders. Beyond the lip is open air: a gap about twice "
        "her body length. Then a single bare riveted steel I-beam, no thicker than her torso, begins at about 58% across "
        "the frame, slightly lower than the deck, and runs level out of the right edge of the frame, held up by one "
        "slender steel column. Far below, a street with tiny cars. Open sky and the lake horizon. The girl sprints on "
        "the deck toward the lip at about 20% from the left edge, her full body about one third of the frame height. "
        "No other people. ") + JADE + STYLE),
    "chasm": dict(refs=[JREF, LEVEL], prompt=DAY + SIDE + LEVELREF + (
        "Wide shot. A single bare riveted steel I-beam, no thicker than her torso, enters from the left edge of the "
        "frame a little below mid height and ends abruptly at about 36% across the frame, a slender column under its "
        "end. Then the chasm: a wide gap of open air about four of her body lengths across, the street and tiny cars "
        "very far below. At about 78% across, the far side: the top corner of a tall stone retaining wall with a flat "
        "mown lawn on top, level with the beam, running out of the right edge of the frame; the wall's face drops "
        "straight down out of the bottom of the frame. Small in the far right distance, the hotel. Open sky. The girl "
        "runs on the beam toward the gap at about 12% from the left edge, arms slightly out for balance, her full body "
        "about 30% of the frame height. No other people. ") + JADE + STYLE),
    "lawn": dict(refs=[JREF, AGENT, LEVEL], prompt=DAY + LEVELREF + (
        "Wide shot from a slightly raised three-quarter side view, camera about 20 degrees above the ground, looking "
        "across a broad flat mown lawn carved as flowing engraved strokes, which fills the lower two thirds of the "
        "frame. At the left edge of the frame a line of four agents stands in a firing stance, all facing right, each "
        "aiming a pistol held low at hip height toward the right. The girl sprints away from them toward the right, at "
        "about 38% across the frame, leaning hard into a sharp turn, her full body about 30% of the frame height. At the "
        "right edge of the frame, at the end of the lawn, stands the hotel of the reference, about 60% of the frame "
        "height, with its rooftop billboard panels blank white. The lake horizon behind. ") + JADE + AGENTS + STYLE),
    "lawn2": dict(refs=[JREF, AGENT, LEVEL], prompt=DAY + SIDE + LEVELREF + (
        "Medium-wide shot at ground level on the mown lawn. In the right foreground stands a park notice board on two "
        "wooden posts: a large rectangular board about 30% of the frame wide and 22% of the frame high, completely "
        "blank white. The girl sprints from left to right at about 30% across the frame, cutting hard to one side in a "
        "low lean, her full body about half the frame height. Far behind her at the left edge, small, three agents aim "
        "pistols held low at hip height toward her. In the right distance the hotel, its rooftop billboard blank. ") +
        JADE + AGENTS + STYLE),
    "ear": dict(refs=[AGENT, JREF, LEVEL], prompt=DAY + (
        "Medium shot, side-on, on the mown lawn. Three agents stand at the left and centre of the frame, all facing "
        "right in profile. The nearest, large in frame from the waist up, has lowered his pistol to his side and "
        "presses two fingers to the coiled earpiece at his ear, his mouth slightly open as he speaks. The two behind "
        "him still aim pistols low at hip height toward the right. Far in the right background, very small, the girl "
        "runs away across the lawn toward the hotel of the location reference, which stands at the right edge with its "
        "rooftop billboard blank. ") + AGENTS + JADE + STYLE),
    "skip": dict(refs=[JREF, AGENT, LEVEL], prompt=DAY + SIDE + (
        "At ground level on the mown lawn. The girl sprints from left to right at about 42% across the frame, large, "
        "her full body about 55% of the frame height, the bun with the two crossed pencils plainly visible. Behind her "
        "on the left a staggered group of five agents runs after her, the nearest a few strides behind at the left "
        "edge. Ahead of her at the right edge of the frame, the rusticated stone base and arched windows of the hotel "
        "of the location reference are just coming into view. The lake horizon behind. ") + JADE + AGENTS + STYLE),
    "glance": dict(refs=[JREF, HOTEL], prompt=DAY + SIDE + (
        "Medium shot. The girl runs from left to right along the long front of the hotel of the attached reference: "
        "its rusticated limestone base with tall arched windows fills the background, no sign visible. She is at about "
        "45% across the frame, framed from the knees up, about 65% of the frame height, still running, with her head "
        "turned to look back over her shoulder toward the left, wary. Behind her on the left the lawn is completely "
        "empty: nobody is following. No other people in the picture. ") + JADE + STYLE),
    "corner": dict(refs=[JREF, AGENT, HOTEL], prompt=DAY + SIDE + (
        "Wide shot, camera locked off. The sharp stone corner of the base of the hotel of the attached reference "
        "(rusticated limestone quoins) stands at about 62% across the frame and runs the full height of the frame. "
        "Left of it is the hotel's front wall with one tall arched window, and a strip of pavement and lawn along the "
        "bottom. Right of the corner the building turns away: open air and the receding side wall. Just right of the "
        "corner, at about 74% across, an agent stands facing left with his feet planted, a pistol held low at hip "
        "height pointing left at body level. The girl runs in from the left at about 22% across the frame, sprinting "
        "toward the corner, her full body about 38% of the frame height. No other people. ") + JADE + AGENTS + STYLE),
    "pistol": dict(refs=[JREF, AGENT, HOTEL], prompt=DAY + (
        "Low-angle shot, the camera at knee height behind an agent's hip. In the lower right foreground, large and "
        "slightly soft, the agent's hand in a black suit sleeve with a white cuff holds a pistol low beside his hip, "
        "the barrel pointing left and slightly downward, level with the girl's waist. Beyond it at the left centre, "
        "sharp, the girl has skidded to a halt facing him, seen full length from the knees up, hands half raised at "
        "her sides, eyes wide; her head is well above the line of the barrel. Behind her the rusticated limestone "
        "wall of the hotel. ") + JADE + AGENTS + STYLE),
    "shot": dict(refs=[JREF], prompt=DAY + (
        "A medium side view by the limestone wall of a grand hotel, lawn at her feet: the girl recoils as she is hit "
        "in the side of the torso (never the head), her body bending away to the left, her face in three-quarter view "
        "with her eyes squeezed shut; from the impact point on her jacket a burst of glowing orange and pale-blue square "
        "motes explodes outward. At the right edge of the frame, a white engraved muzzle-flash starburst. The bun with "
        "the two crossed pencils is plainly visible. ") + JADE + STYLE),
    # ---- Drop 2 ----------------------------------------------------------------------------------------------------
    "wall": dict(refs=[JREF, HOTEL], prompt=DAY + (
        "Flat frontal elevation, camera square to the wall and locked off: the limestone side wall of a two-storey "
        "wing of the hotel of the attached reference fills the whole frame. Along the bottom, a strip of pavement. A "
        "striped canvas awning over a door at the lower left. A zigzag iron fire escape with two landings climbs the "
        "wall right of centre. Deep stone window ledges. Along the very top of the frame runs the heavy stone cornice "
        "of the flat roof. The whole wall in frame is about four times her height. The girl stands on the pavement at "
        "the lower left, running toward the wall, her full body about 24% of the frame height. No other people. ") +
        JADE + STYLE),
    "boost": dict(refs=[JREF, HOTEL], prompt=DAY + TWINS + (
        "Flat frontal view of the top of the limestone side wall of the hotel of the attached reference, camera locked "
        "off. An iron fire-escape landing with a railing crosses the lower third of the frame. The heavy stone cornice "
        "of the flat roof runs along the very top of the frame, about one and a half times her height above the "
        "landing. On the landing at the centre, the first copy of the girl kneels on one knee facing left, both hands "
        "cupped together low in front of her knee as a step. The second copy of the girl climbs onto the landing from "
        "the left, one foot already stepping toward the cupped hands, looking up at the cornice. Both full figures, "
        "each about 40% of the frame height. ") + JADE + STYLE),
    "haul": dict(refs=[JREF], prompt=DAY + TWINS + (
        "On the edge of a flat rooftop, camera low on the roof and locked off, looking along the heavy stone cornice, "
        "which runs from the lower left of the frame to the right. The first copy of the girl lies on her stomach on "
        "the roof at the edge, reaching down over the cornice with both arms and gripping the wrist of the second copy, "
        "who hangs from the ledge below it by one hand, looking up, her head and shoulders visible above the stone. Far "
        "below and behind, a lawn with a few tiny agents in black suits. Open sky. Both girls large in frame. ") +
        JADE + STYLE),
    "slide": dict(refs=[JREF], prompt=DAY + TWINS + (
        "A homage to M.C. Escher's 1937 woodcut 'Still Life and Street': the flat top of a wooden table runs without a "
        "break into a Chicago street between rows of brick buildings. Enormous hardbound books, each as tall as the "
        "buildings, lean against the house fronts and lie stacked along the street, with other giant tabletop objects "
        "among the buildings: an inkwell, a pipe, a matchbox, a fan of playing cards, all engraved in black and white. "
        "One enormous closed book lies tilted across the frame, its plain cloth cover a long smooth ramp sloping down "
        "from the upper left to the lower right. The two copies of the girl slide down this cover from left to right, "
        "hand in hand: the leading one, lower and further right, pulls the other along by the hand; both crouched low "
        "in a slide, each about 30% of the frame height. All book spines and covers are blank. ") + JADE + STYLE),
    "spine": dict(refs=[JREF], prompt=DAY + TWINS + (
        "Camera locked off. The background is a wall of enormous upright book spines standing side by side like a row "
        "of house fronts, each spine as wide as a building and taller than the frame, cloth-bound with raised bands, "
        "engraved in black and white. The two spines in the middle of the frame are identical twins; each carries one "
        "large blank white title label, a plain horizontal rectangle, in the upper half of the frame. A wooden table "
        "top is the ground. In the lower left, the first copy of the girl points up with an outstretched arm at the "
        "twin spines while looking back at the second copy. In the lower right, the second copy looks up to where she "
        "points. Both framed from the knees up, each about 50% of the frame height, neither covering the two labels. "
        "No lettering on anything. ") + JADE + STYLE),
    "roll": dict(refs=[JREF, AGENT], prompt=DAY + SIDE + (
        "Wide shot, camera locked off, in the world of M.C. Escher's woodcut 'Still Life and Street': the ground is a "
        "flat wooden table top that is also a street; enormous blank hardbound books as tall as buildings lean against "
        "brick house fronts at the left and right of the frame, open sky in the middle. The girl stands in the centre "
        "of the frame in a low ready crouch, her full body about 34% of the frame height. Three agents rush at her "
        "from the left edge and three from the right edge, arms reaching, mid-stride. ") + JADE + AGENTS + STYLE),
    "two": dict(refs=[JREF, AGENT], prompt=DAY + TWINS + SIDE + (
        "Wide shot, camera locked off, in the world of M.C. Escher's woodcut 'Still Life and Street': the ground is a "
        "flat wooden table top that is also a street; enormous blank hardbound books as tall as buildings lean against "
        "brick house fronts at the left and right of the frame, open sky in the middle. In the centre, six agents lie "
        "tangled in a heap where they have crashed into each other. The two copies of the girl have just landed back "
        "to back in front of the heap, each in a low sprinter's crouch: the left copy at about 38% across facing left, "
        "the right copy at about 62% across facing right. Each about 34% of the frame height. ") + JADE + AGENTS + STYLE),
    "roundcorner": dict(refs=[JREF, AGENT, HOTEL], prompt=DAY + (
        "High three-quarter view looking down at about 45 degrees at the sharp stone corner of the base of the hotel "
        "of the attached reference, so we can see around the corner and she cannot. The hotel's long front wall, a "
        "rusticated limestone base with tall arched windows, runs from the lower left of the frame up to the corner at "
        "the centre; the hotel's side wall turns away from the corner toward the upper right. A pavement runs along "
        "both walls, lawn beyond. The girl sprints along the pavement beside the front wall from the lower left toward "
        "the corner, about a third of the way there, her full body about 30% of the frame height. Just around the "
        "corner, on the pavement beside the side wall and hidden from her by the corner, one agent stands waiting, "
        "facing the corner, his pistol held low beside his hip. Nobody else. ") + JADE + AGENTS + STYLE),
}

VID = {
    # take: kf = keyframe[:version], fixed = locked-off camera (default True), girl = keep a Jade matte (default True)
    "plat": dict(kf="plat", dur=5, prompt=(
        "The girl sprints extremely fast from left to right along the platform and runs out of the right edge of the "
        "frame. The agents pour out of the stairwell at the left and run after her across the platform, more of them "
        "following. The two hanging sign boards stay blank and still.")),
    "leap": dict(kf="leap", dur=4, prompt=(
        "The girl flies across the gap in a long running leap, lands on the narrow steel beam, wobbles for an instant "
        "with her arms out, and keeps sprinting to the right along the beam and out of the frame. Then two men in black "
        "suits run in along the platform from the left and stop dead at the lip, arms windmilling, looking down at the "
        "drop.")),
    "chasm_short": dict(kf="chasm:2", dur=5, prompt=(
        "The girl runs fast to the end of the beam and jumps toward the far wall. Her jump is too short: she arcs "
        "through the air, reaches for the top of the wall, misses it by an arm's length, and falls straight down into "
        "the chasm, out of the bottom of the frame.")),
    "chasm_dash": dict(kf="chasm:2", dur=5, prompt=(
        "The girl runs fast to the end of the beam and jumps toward the far wall in a high arc. Past the top of the arc "
        "she begins to drop, falling short of the wall. Then she suddenly shoots forward through the air in a flat "
        "horizontal dive, her body stretched out straight like a superhero dash, crosses the rest of the gap, and lands "
        "on the lawn on top of the wall in a low skidding slide, then springs up and runs on to the right.")),
    "lawn": dict(kf="lawn", dur=5, prompt=(
        "The girl sprints away across the lawn toward the hotel in a sharp zigzag, cutting hard to one side and then "
        "the other every half second, low and fast, getting further away and smaller. The agents stay where they "
        "stand, tracking her with their pistols, their arms swinging to follow her. No muzzle flashes, no smoke.")),
    "lawn2": dict(kf="lawn2", dur=4, prompt=(
        "The girl sprints from left to right in a sharp zigzag, cuts hard around the notice board, passing in front of "
        "it, and runs out of the right edge of the frame. The notice board stays blank and perfectly still. The small "
        "agents far behind keep aiming. No muzzle flashes.")),
    "ear": dict(kf="ear", dur=4, prompt=(
        "The nearest agent presses two fingers to his earpiece and calmly speaks a few words, then gives one small "
        "nod. The two agents behind him keep aiming. Far away the tiny girl keeps running toward the hotel.")),
    "skip": dict(kf="skip", dur=6, fixed=False, prompt=TRACK + (
        "She sprints extremely fast to the right; the agents behind run after her; the hotel's stone base slides "
        "slowly further into the frame from the right.")),
    "glance": dict(kf="glance", dur=4, fixed=False, prompt=TRACK + (
        "She runs to the right along the hotel wall and turns her head to look back over her shoulder to the left. "
        "She sees the empty lawn behind her, puzzled, slows a little, then looks ahead again. Nobody else appears.")),
    "skid": dict(kf="corner", dur=5, prompt=(
        "The girl runs toward the corner, sees the agent standing there, and digs her heels in, skidding to a stop a "
        "few steps in front of him, arms out for balance, startled. The agent does not move his feet; he slowly raises "
        "the pistol from his hip, keeping it low at body level.")),
    "kick": dict(kf="corner", dur=5, prompt=(
        "The girl sprints at the hotel wall, jumps, plants one foot high on the stone and kicks off it in a big "
        "acrobatic wall-kick, catches the stone ledge above the arched window and pulls herself up out of the top of "
        "the frame. The agent lunges forward and grabs at empty air where she was.")),
    "pistol": dict(kf="pistol:2", dur=4, prompt=(
        "The agent's hand slowly and deliberately raises the pistol from beside his hip until it points level at the "
        "girl's waist. The girl stands frozen, hands half raised, breathing fast, her eyes following the pistol.")),
    "shot": dict(kf="shot", dur=4, prompt=(
        "She recoils from the hit in her side, bending away, eyes shut; the orange and pale-blue square motes burst "
        "outward from her jacket and swirl in the air; the white starburst at the right flares and fades.")),
    "climb": dict(kf="wall", dur=6, prompt=(
        "The girl sprints to the wall and climbs it extremely fast like a parkour runner: she jumps onto the striped "
        "awning, springs from it to a stone window ledge, leaps across to the iron fire escape, swings up onto its "
        "first landing, runs up its stairs to the top landing, jumps from the railing and reaches for the stone cornice "
        "at the top of the wall, her fingertips just missing it.")),
    "boost": dict(kf="boost", dur=5, prompt=(
        "The standing girl steps into the kneeling girl's cupped hands; the kneeling girl heaves and launches her "
        "straight up; she flies up, catches the stone cornice with both hands and pulls herself up and over it onto the "
        "roof, out of the top of the frame. The kneeling girl stays on the landing, watching her go.")),
    "haul": dict(kf="haul:2", dur=5, prompt=(
        "The girl lying on the roof hauls the hanging girl up by the wrist; the hanging girl swings a leg over the "
        "stone cornice and rolls onto the roof beside her. Both get up onto one knee, breathing hard, and look at each "
        "other.")),
    "slide": dict(kf="slide", dur=5, prompt=(
        "The two girls slide fast down the tilted book cover from the upper left to the lower right, hand in hand, the "
        "lower one pulling the other, both leaning back as on a playground slide, hair and jacket straps streaming; "
        "they shoot off the bottom edge of the book onto the table top and out of the right side of the frame.")),
    "spine": dict(kf="spine", dur=5, prompt=(
        "The girl on the left keeps pointing up at the two identical book spines and looks back at the other girl. The "
        "girl on the right looks up at the spines, tilts her head, then her eyes widen and she breaks into a slow "
        "knowing smirk and looks at the first girl. The two blank labels stay blank and perfectly still.")),
    "roll": dict(kf="roll", dur=5, prompt=(
        "The agents charge at her from both sides. At the last instant she dives low to the right in an extremely fast "
        "forward shoulder roll under their reaching arms; the two groups of agents crash into each other where she was "
        "standing and fall in a heap. She comes out of the roll and springs high into the air in a big leap, arms "
        "spread.")),
    "two": dict(kf="two", dur=5, prompt=(
        "Both girls burst out of their crouches at the same instant and sprint away in opposite directions extremely "
        "fast, the left one out of the left edge of the frame and the right one out of the right edge. The agents "
        "scramble up from the heap, look left and right in confusion, then split, half running after each.")),
    # retake of `roll` (Drop 2 agent): in take 1 the agents pile onto her and she ends up standing on the heap
    "roll_b": dict(kf="roll", dur=5, prompt=(
        "The agents charge at her from both sides. At the last instant she dives low to the right and tumbles along "
        "the ground in one extremely fast forward shoulder roll that carries her far to the right, passing under the "
        "outstretched arms of the agents on the right, and she comes up on her feet alone at the right side of the "
        "frame, well clear of everyone, on bare table top. Behind her, in the centre of the frame where she was "
        "standing, the two groups of agents crash head-on into each other and fall in a heap. She never touches an "
        "agent and never stands on them; the heap stays in the centre, she stays at the right. Then she springs "
        "straight up from the bare ground at the right into a very high leap, arms spread wide, far above the "
        "agents' heads.")),
    # retake of `haul` (Drop 2 agent): in take 1 the hauled girl crawls over the lying one, so the two cannot be told
    # apart frame by frame; here they stay side by side with a gap
    "haul_b": dict(kf="haul:2", dur=5, prompt=(
        "The girl lying on the roof stays lying flat on her stomach in the same place at the left the whole time and "
        "pulls the hanging girl up by the wrist. The hanging girl climbs up the wall to the RIGHT of her, swings one "
        "leg over the stone cornice on the right side, rolls onto the roof and comes up kneeling on one knee at the "
        "right, a clear gap of an arm's length between the two girls. They never overlap: after the wrist lets go, "
        "neither girl crosses in front of or behind the other. Both look at each other, breathing hard.")),
    # retake of `chasm_dash` (Verse 2 agent): take 1 jumps high over the lawn, so her own arc never looks short; here
    # the jump is low and visibly falling short before the dash
    "chasm_dash_b": dict(kf="chasm:2", dur=5, prompt=(
        "The girl runs fast to the end of the beam and jumps toward the far wall, but the jump is low and weak: she "
        "rises only a little, then starts to fall while still over the gap, her feet dropping below the top edge of "
        "the far wall; she is clearly not going to make it. Then in mid-fall she suddenly shoots straight forward "
        "horizontally in a fast flat dash, body stretched out level, reaches the top of the wall and lands on the lawn "
        "just past the edge in a low skid, then springs up and runs on to the right.")),
    "slide_point": dict(kf="slidept", dur=5, prompt=(
        "The two girls slide fast down the tilted book cover from the upper left to the lower right, hand in hand. "
        "The leading girl keeps her other arm stretched out, pointing at the blank label on the spine of the huge "
        "upright book at the right, and turns her head back to the other girl; the other girl looks where she points. "
        "They shoot off the bottom edge of the book onto the table top past the upright book. The label stays blank "
        "and perfectly still.")),
    "swarm_boost": dict(kf="swarmboost", dur=5, prompt=(
        "The agents rush in from both sides toward the two girls. The kneeling girl heaves her cupped hands upward and "
        "launches the standing girl straight up into the air; she flies high, up to the top part of the frame, and "
        "hangs at the peak of the jump with her arms and legs spread wide. Below her the agents from the left and the "
        "agents from the right crash head-on into each other in the centre and fall in a tangled heap on the table "
        "top. The girl in the air never touches an agent.")),
    "skip_b": dict(kf="skipfar", dur=6, fixed=False, prompt=TRACK + (
        "She sprints extremely fast to the right. The agents behind her run much faster than she does: they close "
        "the gap quickly and steadily, growing larger as they gain, until the nearest is only a few strides behind her "
        "at the end. The hotel's stone base slides further into the frame from the right.")),
    "round_corner": dict(kf="roundcorner", dur=5, prompt=(
        "The girl sprints along the pavement to the corner and rounds it at full speed without slowing, and comes "
        "face to face with the waiting agent just around the corner, almost running into him. She skids to a stop an "
        "arm's length from him, startled, leaning back. The agent stays where he is; his pistol stays low beside his "
        "hip, pointing at the ground.")),
    "slide_point_b": dict(kf="slidept:2", dur=5, prompt=(
        "The two girls slide fast down the tilted book cover from the upper left to the lower right, hand in hand. "
        "The leading girl keeps her other arm stretched out, pointing at the blank label on the spine of the huge "
        "upright book at the right, and BOTH girls keep looking at that label the whole time, their heads turning to "
        "follow it as they slide past it. They shoot off the bottom edge of the book onto the table top past the "
        "upright book. The label stays blank and perfectly still.")),
    "round_corner_b": dict(kf="roundcorner", dur=5, prompt=(
        "The girl sprints along the pavement and swings round the corner at full speed without slowing, onto the "
        "pavement beside the side wall, and runs smack into the waiting agent's chest before she can stop. She "
        "bounces off him, her arms flying up, staggers backward several steps and nearly falls, catching her balance "
        "with one hand on the stone wall, wide-eyed. The agent rocks back half a step from the bump, then steadies. "
        "His pistol stays low beside his hip pointing at the ground the whole time. Lively, cartoonish physical comedy "
        "timing, like a platformer character bumping into an enemy.")),
}
