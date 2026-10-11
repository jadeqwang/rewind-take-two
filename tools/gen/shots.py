"""Shot registry for tools/gen/vgen.py (Rewind take two). Prompts only: no secrets, no private names.

Each entry: model, image (first frame, repo-relative path under media/), duration (s), prompt, and optional
camera_fixed, aspect, avatar (Seedance use_virtual_avatar), refs (reference images), audio (reference audio mp3).
"""
SD20 = "bytedance/seedance-2.0"
H3 = "minimax/h3"

ENGRAVED = ("The whole world stays a black-and-white Escher-style wood engraving: crisp black ink lines and dense "
            "cross-hatching on off-white paper, no gray wash, no color anywhere except the girl.")
ONLY_HER_COLOR = ("Only the anime girl is in full color (white bomber jacket with orange band, navy cargo pants, orange "
                  "headphones round her neck, black hair in a bun with a yellow pencil through it); she keeps her colors "
                  "and design exactly.")
NO_TEXT = "No text, no letters, no subtitles, no logos, no watermark."

SHOTS = {
    # style test C (2026-10-11): does the engraving hold and does only Jade stay in color during fast motion?
    "ST_run": dict(model=SD20, image="media/style_tests/video/ST_run_first.jpg", duration=5, camera_fixed=False,
                   prompt=(f"Side-scrolling platformer shot: the anime girl sprints extremely fast from left to right along "
                           f"the elevated train tracks, legs a blur of long powerful strides, hair bun bouncing, arms "
                           f"pumping. The camera tracks sideways with her at the same speed, keeping her in the same place "
                           f"in frame while the engraved girders, buildings and rooftops scroll past quickly from right to "
                           f"left. {ENGRAVED} {ONLY_HER_COLOR} {NO_TEXT}")),
}
