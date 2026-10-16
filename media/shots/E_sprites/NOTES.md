# Jade sprite clips for the isometric Three.js diorama (hair down, pencil in hand)

Each folder holds `rgba/f_%04d.png` (1-based; RGBA with straight alpha; the white background is decontaminated from the edges; fixed box), `info.json`, `sheet.jpg` (checkerboard, red = feet baseline, blue = hips centre) and `preview.mp4` (over paper colour).
Pipeline: Seedance 2.0 720p clip → BiRefNet matte (`tools/engrave/matte.py` Matter + DIS flow temporal smoothing, largest component) → for the walks, remove the travel trend (quadratic fit of hip x and feet y, linear fit of height for perspective scale) → crop a fixed box (union of all frames + 5% margin, symmetric about the hips) → loop = the best mask-IoU pair at least 22 frames apart (one full gait cycle).
Script: kept outside the repo (scratchpad); the logic is described here.

| clip | take used | box | feet y | loop [first,last] (IoU) | notes |
|---|---|---|---|---|---|
| walk_front | take_1 (E_walk_front, static cam) | 246×452 | 416 | 58–98 (0.968), 1.67 s | Good steady walk to lower-right, pencil in right hand. Smallest source (≈380 px tall). |
| walk_back | take_3 (E_walk_back3, camera tracks her) | 448×662 | 608 | 43–77 (0.967), 1.42 s | Three-quarter back toward upper-left, back circle + long hair. Takes 1–2 (static cam) left the frame after 1–2 s. Seedance zooms and drifts, so those were rejected. |
| crank | take_2 (E_crank2, static cam) | 360×648 | 618 | 62–105 (0.995), 1.79 s | Fists circle up to chest and back down at waist height, pencil in right fist. Modest amplitude. Take_1 was a near-static wringing motion. |

Keyframes: nano-banana-pro, refs = canon turnaround + pencil sheet panel 3 (`_refs/`). The model's "high angle" is mild (≈20–30°), not a true 35° isometric view.
Cost: keyframes $0.54 + 6 takes $4.50 = $5.04.
