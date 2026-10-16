# Style test stills: gongbi vs soft painted ("Braid-like")

Look test only, not wired into anything. There are two styles × two reference photos × two models, which makes 8 stills. Each one is matted (BiRefNet) and laid over a plate in roughly the v4_S1_first framing: the pencils photo goes over `plate_close_1`, the long-hair photo over `plate_truth_1`.

**Start with `contact_sheet.jpg`.** Each row is one style / photo pair. It begins with a crop of the source photo for likeness comparison, followed by nano-banana-pro (the raw still, then on the plate) and gpt-image-2.5-flare (raw, then on the plate).

Script: `tools/sing/style_stills.py` (gen / matte / comp / sheet, with the venvs listed in its docstring). The prompt for each still is in its `<key>.json`.

## Spend
8 calls, no failures or refusals, no retries: **$1.34** (list-price estimates, tagged `style_still_gongbi` / `style_still_braid`). Project total is $276.02 of $400.

## What each still does

| still | style read | likeness | glasses / pencils / patch / expression |
|---|---|---|---|
| gongbi_pencils__nbp_1 | **Real gongbi**: even ink line, flat mineral washes, silk ground | Drifted: the face is heavier and a little older, the freckles are overdone, and the head is turned square to camera | Glasses ok; both pencils and erasers ok; patch ok; serious. The jacket snaps came out green |
| gongbi_pencils__gpt_1 | Weak: reads as a line-traced photo on linen, not gongbi | Very close to the photo | All ok; keeps the photo's faint closed-lip smile |
| gongbi_long__nbp_1 | Strong gongbi | Drifted toward an idealised illustration: narrower face, glossy lips, faint smirk | Glasses ok (frame lighter grey); patch turned azurite blue and is cut at the edge (as in the source) |
| gongbi_long__gpt_1 | Weak: a coloured-pencil filter over the photo | Very close | All ok; neutral |
| braid_pencils__nbp_1 | **Good painterly look**: warm side light, blue/gold, loose brushwork | Good: wide face, freckles, her eyes | **Smiling** (closed-lip, more than the source); glossy lips; patch ring broken open (text ok); pencils ok |
| braid_pencils__gpt_1 | Weak: an oil-paint filter on the jacket and background, with an almost photographic face | Very close | Patch, pencils and glasses ok; the photo's faint smile |
| braid_long__nbp_1 | Painterly | **Beautified**: narrower, longer face; hair turned light brown; glossy lips | Glasses ok; patch ok; slight smirk |
| braid_long__gpt_1 | Weak: a filter over the photo, with orange rim light on the hair | Very close | All ok; neutral |

The pattern is consistent. nano-banana-pro actually changes the style but drifts her face. gpt-image-2.5-flare keeps her face almost exactly but barely changes the style, so its versions look like a photo with a filter.

## Favourites
- **Gongbi: `gongbi_pencils__nbp_1`**. It is the only one that truly reads as gongbi, and the pencils come across as hairpins, but the face needs a likeness pass. It is heavier and older than she is.
- **Braid: `braid_pencils__nbp_1`**. It has the warm glowing painted light and is the best likeness of the painterly ones. It has a smile that has to come out, and the patch ring needs fixing.

## Composite caveats (look test)
- Placement is by scale and shift only, from eye distance and eye centre. The bottom of each still sits on the frame bottom, and the scale is capped so the bun and pencils stay in frame. That makes the pencils versions sit a little smaller than v4_S1.
- Where a still crops her shoulders, the figure ends in a soft vertical edge.
- The Braid stills keep a faint glow of their painted ground round the hair after matting.

## Files (all in `media/sing/style/`)
- `contact_sheet.jpg` (2955×1874)
- Raw stills, each with a `<key>.json` beside it: `gongbi_pencils__nbp_1.jpg`, `gongbi_pencils__gpt_1.png`, `gongbi_long__nbp_1.png`, `gongbi_long__gpt_1.png`, `braid_pencils__nbp_1.png`, `braid_pencils__gpt_1.png`, `braid_long__nbp_1.png`, `braid_long__gpt_1.png`
- Composites: `<key>_comp.jpg` for each of the 8
- `_matte/<key>.png` (BiRefNet alpha) and `_matte/comp.json`; `_in/` holds the padded copies of the photos that were sent to the models (the sources are untouched)
