# Selfie: light makeup and the film's jacket

**Why:** a friend said neither singing reference photo looks like Jade, because both had been beautified. So this starts from her real bare-faced selfie, `inputs/nomakeup_selfie.png` (512×683, left unchanged).

**What changes:**
- Light natural makeup: lips, lashes and a little skin evening. Freckles and moles may go. The brows stay untouched.
- Light hair tidying.
- The film's jacket replaces her top.

The face shape, proportions and brows must not change. These are candidates for her to look at; nothing is wired in.

**Picks:**
- **Model edit: `selfie_pick_model.png`** (= `nb2_1`, nano-banana-2). Every measured ratio is within the noise floor. The makeup is visible but light (soft rose lips, a little mascara, evened skin). It keeps the frames' gunmetal-green colour and her hair.
- **Hybrid: `selfie_pick_hybrid.png`** (= `hyb_nb2_2`). Her exact face from the selfie, with a light local makeup pass, set onto the nano-banana-2 take-2 jacket and hair. Its likeness is guaranteed by construction. The face was 2× upscaled from the 512 px selfie, so it is a little softer than the hair around it.

Script: `tools/sing/selfie_dress.py` (`gen`, `hybrid`, `check`). Sheet: `contact_sheet.jpg`. Numbers: `metrics.json`.

## Spend
$1.82 logged under `selfie_*` in `media/genlog.jsonl`, over 18 paid calls. One extra call, the first try-on, failed with HTTP 400 and was not billed.

| model | calls | logged |
|---|---|---|
| gpt-image-2.5-flare | 3 | $0.64 |
| seedream-5-pro | 3 | $0.32 |
| nano-banana-pro | 2 | $0.27 |
| nano-banana-2 | 4 | $0.27 |
| flux-1-kontext-max | 2 | $0.16 |
| flux-2-max | 2 | $0.14 |
| p-image-try-on | 2 | $0.03 |

The real list price is likely about **$2.03**. `cf.estimate` logs flux-2-max at its first-megapixel price, $0.07, but a 1536×2048 output plus inputs is about $0.17 each. It also leaves out try-on's $0.008 per input image.

## What each model returns
| model | output size |
|---|---|
| nano-banana-pro / nano-banana-2 | 1792×2400 (2K, 3:4) |
| seedream-5-pro | 1536×2048 |
| flux-2-max | 1536×2048 |
| gpt-image-2.5 | 1024×1536 (2:3 only; it gets the selfie cropped to x 28–483) |
| flux-1-kontext-max | 880×1184 |
| p-image-try-on | 896×1184 |

- **Inputs:** every model except kontext gets both the selfie and `_in/jacket_ref.png`, which is the jacket cut from the pencils photo with the chin and neck painted black so that no face goes in. Kontext takes one image only, so it gets the jacket in words.
- **The prompts** say that only the clothes come from the reference, keep the eyes, nose, jaw and face width, and leave the brows completely alone. Take 2 added an explicit eye lock ("same hooded lids, don't open her eyes wider") and the glasses' colour. Take 3 for seedream added "no beauty filter".

## Likeness method
- Each candidate gets a similarity fit (scale, rotation, translation) onto the selfie. I report the mean and max residual of all 478 landmarks in selfie pixels; the inter-ocular distance is 128 px.
- I compute proportion ratios: face width/height, jaw width at the mouth corners, inter-ocular/face width, each eye's height/width, nose width/inter-ocular, mouth width/inter-ocular, and chin length.
- The brow checks are arch height/brow length, brow length, brow thickness, and the inner and outer brow ends relative to the eye corners (in % of the inter-ocular distance).
- **Noise floor:** the selfie upscaled 3×, re-JPEG'd, blurred, sharpened or brightened gives residuals up to 0.75 / 2.44 px.
  - Eye height/width moves up to 4.8% on those unchanged images.
  - Everything else moves up to 1.8%.
  - The hybrids confirm this. Their geometry is her original face, yet they read eye ratios up to −5% (from the lash darkening) and chin −4.7% on `hyb_flux2_1` (the neck context changed).
  - So **FLAG** means more than 3% beyond that feature's floor. I judged anything near the line by eye at 2× face crops.
- **Caveat:** MediaPipe's brow points are partly model-fitted, so the brow numbers catch big re-arching (nb2_3, kontext), not subtle grooming. I checked brows by eye as well.

## Verdicts
| key | verdict | why |
|---|---|---|
| nb2_1 | **PICK (model)** | resid 0.73/2.35 px; eyes +0.8/+1.6%, nose −2.4%, mouth −4.3% (the floor is up to 1.8%), brows unchanged; light visible makeup |
| nb2_4 | OK, a close second | resid 0.61/2.04 px; within floor |
| nb2_2 | OK | within floor numerically (eyes +4.1/+3.9%), but her eyes look a touch more open at 2× |
| nbp_1 | OK | very faithful (0.56/2.01 px), but the makeup is barely visible and the frames turned silver |
| gpt_2 | OK | within floor (0.48/1.48 px); skin smoothed; the best jacket (full patch and disc visible) |
| gpt_3 | OK | within floor; skin smoothed |
| sdr_2 | OK | shape fine, but beauty-filter brightened, smooth skin |
| nbp_2 | REJECT | **eyes enlarged** +19/+15%, mouth −8%, brow arch +5% |
| nb2_3 | REJECT | **eyes enlarged** +11/+9%, **brows re-arched** +8/+6%, chin +9% |
| gpt_1 | REJECT | **eyes enlarged** +10/+7%, smoothed |
| flux2_1 | REJECT | **eyes enlarged** +15/+9%, chin −6%, blotchy skin |
| flux2_2 | REJECT | **nose widened** +4%, mottled skin |
| kontext_1, kontext_2 | REJECT | a different, beautified person; **brows reshaped** (arch ±7–10%, thickness −9 to −11%) |
| sdr_1, sdr_3 | REJECT | red gradient lipstick, not light makeup; sdr_3 also chin +5.5% |
| tryon_1, tryon_2 | REJECT | the face is kept, but the floral top still shows under the jacket and there is no makeup |
| hyb_nb2_2 | **PICK (hybrid)** | her face exactly, the nb2_2 jacket and tidied hair |
| hyb_nb2_1, hyb_nb2_4, hyb_nbp_1, hyb_sdr_1, hyb_sdr_2, hyb_flux2_1 | OK | her face exactly; differ only in the jacket and hair from the base take (the patch is cut off on the sdr ones) |
| hyb_gpt_1, hyb_gpt_2 | REJECT | smeared edges, because gpt's 2:3 crop leaves 28 px strips that had to be filled |

**Edits that slimmed the face, enlarged the eyes, or narrowed the nose or jaw:** nbp_2, nb2_3, gpt_1 and flux2_1 enlarged the eyes, and flux2_2 widened the nose. No candidate slimmed her face or narrowed her jaw beyond the floor. The kontext takes changed her identity outright.

## Hybrid details
- **Base:** each hybrid is the take mapped into the selfie's framing at 2× (1024×1366).
- **Face area taken from the selfie:** her face oval, with the upper edge pushed out to the hairline and the jaw line pulled in, plus the whole glasses band. It is feathered and taken from the selfie (Lanczos 2×, light unsharp mask).
- **Toning:** the face is toned halfway to the take's skin so that the seams vanish.
- **Local makeup pass (no model):** a little flush evening, concealing of the darker spots part way, the lips moved toward the take's lip colour, and a slight darkening of the upper lash line. The brows are never touched.
- **Hair** comes from the take, so the light tidying shows outside the hairline.
- **Masks** are in `_in/hyb_*_mask.png`.

---

# Round 2: subtle "no-makeup makeup" glow-up

Jade: *"can you ask the models for a subtle no make-up make up glow-up?"*

**The look:** healthy, rested, lightly dewy skin, even tone, softened under-eye shadows, a hint of natural flush, tinted-balm lips near her own colour, and fine lash definition. It should read as a great-skin day, not makeup.

**Rules unchanged:**
- Face shape and every proportion stay as they are.
- Brows keep their shape.
- No eye enlargement, no slimming, no nose or jaw change.
- Real skin texture stays.
- The gunmetal frames and the film's jacket stay.

The prompt spells out the geometry rules: "a 'glow-up' here means skin and colour only", plus the eye lock and the brow lock.

**Picks:**
- **Model edit: `selfie_r2_pick_model.png`** (= `r2/a_nb2_2`, nano-banana-2, route A, 1792×2400).
  - Shape: residual 0.49/1.56 px, the lowest of any round-2 take. Every ratio is within the floor (largest: eyeR +2.8%, mouth −2.4%), and the brows are unchanged.
  - Look: a soft glow with real texture still there (pores, the mole by her mouth), balm lips and fine lashes, without the shine some takes had.
- **Hybrid: `selfie_r2_pick_hybrid.png`** (= `r2/hyb_a_nb2_2`, 1024×1366). Her exact selfie face on the a_nb2_2 jacket and hair, with the local glow pass (described at the end). Likeness is guaranteed by construction.

Script: `tools/sing/selfie_glow.py` (`gen`, `hybrid`, `check`), reusing `selfie_dress.py`'s metrics. Sheet: `contact_sheet_r2.jpg`. The original selfie and the round-1 pick are at its head. Numbers: `r2/metrics_r2.json`. All candidates are in `r2/`.

## Routes
- **A (`a_*`)**: from the original selfie plus the jacket reference, with makeup and jacket in one edit.
- **B (`b_*`)**: from `selfie_pick_model.png` (round 1, jacket already on), glow only.

Both routes are measured against the **original** selfie, so B's two edits add up.

## Spend
- **Round 2:** $2.07 logged over 19 calls, tagged `selfie_r2_<route>_<model>`, with no failures.

  | route | gpt-image-2.5 | nano-banana-2 | nano-banana-pro | seedream-5-pro |
  |---|---|---|---|---|
  | A | 2 takes, $0.43 | 4 takes, $0.27 | 2 takes, $0.27 | 2 takes, $0.21 |
  | B | 1 take, $0.20 | 3 takes, $0.20 | 2 takes, $0.27 | 3 takes, $0.23 |

- **Selfie total, rounds 1 + 2:** $3.89 logged. Adding the flux-2/try-on under-count from round 1, it is about $4.1.
- **Models left out:** I skipped flux-2-max and kontext this round. In round 1 they gave blotchy skin and a different face.

## Verdicts
The same metrics, noise floor, brow checks and reject rule as round 1: FLAG means more than 3% beyond the feature's floor, and I judged everything by eye at 2× face crops too.

| key | verdict | notes |
|---|---|---|
| a_nb2_2 | **PICK (model)** | 0.49/1.56 px, all within floor; real texture, soft glow, balm lips |
| b_sdr_1 | OK, runner-up | the most visible "great-skin day" glow and flush; 0.72/2.29 px, within floor |
| b_nb2_2 | OK, runner-up | even and rested, a bit smoother; within floor |
| a_nbp_1, a_nbp_2 | OK | faithful; nbp_1 slightly smooth, nbp_2 glow very subtle |
| a_nb2_3 | OK | stronger flush; the cheeks read a bit red |
| a_sdr_1 | OK | natural and faithful; light flush |
| b_nb2_1 | OK | the round-1 pick with a bit more glow |
| b_nb2_3 | OK | eyes +5.3%, at the floor edge |
| b_nbp_1, b_nbp_2 | OK | soft-focus smooth skin |
| b_sdr_2, b_sdr_3 | OK | even, a bit smooth; sdr_3 mouth −4.5% is within floor |
| a_gpt_1, a_gpt_2 | OK | faithful, but airbrushed-smooth skin |
| a_nb2_1 | REJECT | greasy shine on the nose and forehead; eyes +6.7% |
| a_nb2_4 | REJECT | shiny nose, reads greasy |
| a_sdr_2 | REJECT | brow arch flattened −4.4% (beyond floor + 3) |
| b_gpt_1 | REJECT | **eyes enlarged** +7.3/+7.6%, and smoothed |
| hyb_a_nb2_2 | **PICK (hybrid)** | her face exactly, plus the glow pass |
| hyb_a_nbp_1, hyb_b_sdr_1 | OK | her face exactly, plus the glow pass |

**Takes that changed her features:**
- **Eyes enlarged:** only b_gpt_1. gpt keeps widening eyes when it re-edits.
- **Brows reshaped:** only a_sdr_2 (flattened).
- **Slimmed face or narrowed nose/jaw:** none beyond the floor.

The spelled-out geometry block mostly held. Unlike round 1, no nano-banana take blew up the eyes.

## Local glow pass (hybrid)
`selfie_glow.glow()` does the following, with no change to geometry:
- evens out the blotchy flush;
- conceals dark spots part way;
- lifts a band under each lower lid toward the cheek's broad lightness, to soften the under-eye shadow;
- adds a faint even flush on the cheek apples (+2 a*);
- gently boosts the broad highlight planes for the dewy look;
- takes the lips halfway to the take's lip colour, with a little balm sheen;
- darkens the upper lash line slightly.

The brows are excluded from every mask. The face is set onto the take as in round 1: face oval out to the hairline plus the glasses band, feathered, toned halfway to the take's skin.
