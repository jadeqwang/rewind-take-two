# plate_wide_v4: the wide Bean for S1 (v4, note 0:13), by v4B-bean

Model `google/nano-banana-pro`, 4K 16:9, script `tools/v4B/bean/plate.py` (prompts `PROMPTS`, refs and tags in each
candidate's `.json`). Tags `v4B_bean_wide_*`, $0.24 each, $0.72 total.

| File | What |
|---|---|
| `plate_wide_v4_guide_A.jpg` / `_B.jpg` / `_B2.jpg` | input canvases: `plate_close_1.jpg` unscaled at (1350, 106) in 5504x3072; A grey round it, B/B2 the previz collage (B2: skyline not mirrored) |
| `plate_wide_v4_A1.png` | guide A + `plate_sane_1` ref. Rejected: cream border and margin, towers crowd the Bean |
| `plate_wide_v4_B1.jpg` | guide B. Rejected: copied the collage's mirrored skyline (same X-braced tower both sides) |
| **`plate_wide_v4_B2.jpg`** | guide B2. **Picked**: whole Bean with arch, plaza, Loop towers behind, 7 pedestrians, hatched paving; the inset redrawn in register (template match at (1350, 106), scale 1.000) |
| `plate_wide_v4_B2_birefnet.png` | BiRefNet matte of B2 at 2048 wide (the Bean + the walking couple) |
| `plate_wide_v4.png` | B2 with the close plate's own pixels laid back inside the rim (feathered), padded to 5504x3096 (16:9) |
| `plate_wide_v4_bean.png` | Bean plane (RGBA): the Bean filled down to the ground, everything below the paving line (wide y 752), the people |
| `plate_wide_v4_far.jpg` | far plane: towers and sky, people above the paving line patched out, padded (covers wide x -533..2453, y -300..1380) |

Rebuild the plane images: `~/Documents/moongazing/.venv/bin/python tools/v4B/bean/plate.py finish` (free).
