# E4 (section D) — notes

Prompts: keyframes `tools/sections/D/kf.py` (KF["E4_*"]), video `tools/sections/D/dgen.py` (D_SHOTS). Keyframes: nano-banana-pro 2K
($0.134 each), margins trimmed by `tools/sections/D/trim.py`. Video: Seedance 2.0 720p, first-frame locked, 4–5 s ($0.60–0.75).
Engrave: `tools/sections/D/publish.py` (tools/engrave, --out-height 1080, matte kept). Jade-only mattes (agents removed):
`tools/sections/D/jmatte.py` → `*_jmatte/`; twin mattes for the co-op ghost → `*_twin/`.
Chosen takes and in-points: `media/shots/_D/takes.json` (+ chosen.json here, keyed by clip). Usage: `render/timeline/D.js`.
Full judgement and the ghost table: `docs/sections/D.md`.
