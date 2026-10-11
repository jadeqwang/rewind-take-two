# V2f4: the rear-view mirror close (v4, 1:30 car shot, option C): the END of the push

- **Layout reference:** `blockout_close.png` (`tools/v4B/car/car_scene.html?kf=close`).
- **Keyframes** (google/nano-banana-pro, 2K, no seed; prompts in `kf_log.jsonl`, `CLOSE` / `CLOSE_FIX` in
  `tools/v4B/car/kf.py`; $0.134 each, tags `v4B_car_kf_close_a|b|b2`):
  - `kf_close_a`: refs blockout + `media/shots/V2f1/kf_s.jpg`. Too busy (headliner, poles), mirror tilted. Not used.
  - `kf_close_b`: refs blockout + `media/shots/V2f2/kf_v3d.jpg`. Good, but badges on the grilles and lamps below.
  - **`kf_close_b2` (chosen):** an edit of close_b: plain grilles, plain black below, blank lower bezel.
- **Engraved:** `kf_close_b2_engraved.png` (`tools/engrave/engrave_still.py`); `_feather.png` (alpha fades the outer 4 %)
  and `_body.png` (alpha = the mirror body only) are the two hand-over layers of `tools/v4B/car/car_shot.js`.
- Plates are blank in the picture; `TVA 1729` / `4104` / `4096` and the words IN MY MIRROR are pinned by the engine.
