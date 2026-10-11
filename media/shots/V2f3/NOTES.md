# V2f3: the wide over her right shoulder (v4, 1:30 car shot, option C)

- **Layout reference:** `blockout_wide.png` (`tools/v4B/car/car_scene.html?kf=wide`, three.js). `canvas.png` = that
  blockout with the finished mirror of `../V2f4/kf_close_b2.png` laid in (`tools/v4B/car/kf.py canvas`).
- **Keyframes:** `kf_wide_a.jpg`, `kf_wide_b.jpg`: google/nano-banana-pro, 2K, refs canvas.png +
  media/design/jade_canon_turnaround.png + media/design/jade_bun_two_pencils.png; no seed (the model takes none);
  full prompt in `kf_log.jsonl` (`WIDE` in `tools/v4B/car/kf.py`). $0.134 each, tags `v4B_car_kf_wide_a|b`.
- **Chosen: wide_b.** It has the blank sign gantry and shows her cheek and eye; wide_a had no sign and only her ear.
- **Free fixes:** `tools/v4B/car/fix_wide.py` -> `kf_wide_b_fix.png`: the left eraser recoloured pale blue (the model
  drew two pink ones), and the close keyframe's mirror laid back in over the model's mirror so the push ends in
  register. Then `tools/engrave/engrave_still.py` -> `kf_wide_b_fix_engraved.png` (matte in `kf_wide_b_fix_matte/`).
- **Canon check (full size):** left-hand drive, wheel in front of her; two straight crossed yellow pencils (one pink,
  one pale-blue eraser); orange headphones round her neck; white bomber, orange band on the sleeve; black mock-neck;
  engraved world. The model drew an Acura badge on the wheel and numerals on the dials (tiny at 540p). The gantry sits
  above the windshield header (a cheat). No red.
- **Use:** `tools/v4B/car/car_shot.js` (still + engine push), not a video take.
