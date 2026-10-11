#!/usr/bin/env python3
"""Paid source material for the Rewind SFX layer (ElevenLabs via the Cloudflare catalog).

Only two things are generated; everything else in the layer is synthesized in tools/sfx/build.py:
  * the arcade announcer "Continue?" (elevenlabs/eleven-v3, several voices/seeds so build.py can pick
    the take whose Whisper transcript and length fit the 111.22-112.49 hole), and
  * organic impact candidates (elevenlabs/music-v2 used as an SFX generator, 3 s minimum, instrumental),
    used only as layers under the procedural cores after an objective check (onset, tonality, length).

Every file is cached: re-running never pays twice. Costs are logged by tools/gen/cf.py.

    ~/Documents/moongazing/.venv/bin/python tools/sfx/generate.py [--dry-run] [name ...]
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools", "gen"))
import cf  # noqa: E402

OUT = os.path.join(ROOT, "media", "sfx", "gen")

# ElevenLabs premade voices (deep/booming announcer candidates)
ADAM, ARNOLD, CLYDE, GEORGE = "pNInz6obpgDQGcFmaJgB", "VR6AewLTigWG4xSOukaG", "2EiwWnXFnvU5JabPnv8n", "JBFqnCBsd6RMkjVDRZzb"

VOICE = {
    # name: (voice_id, text, seed)
    "continue_adam_a": (ADAM, "[booming arcade announcer] Continue?", 7),
    "continue_adam_b": (ADAM, "[dramatic] Continue?", 11),
    "continue_arnold_a": (ARNOLD, "[booming arcade announcer] Continue?", 7),
    "continue_clyde_a": (CLYDE, "[dramatic] Continue?", 7),
    "continue_george_a": (GEORGE, "[booming arcade announcer] Continue?", 7),
}

NEG = "no melody, no music, no drums, no beat, no instruments, single sound effect only, foley, silence after the hit"
MUSIC = {
    # name: (prompt, length_ms, variant)   (music-v2 rejects `seed` together with `prompt`)
    "train_smash": ("Sound effect: one enormous metal train crash impact, steel crunching and glass shattering, "
                    "a single hit at the very start then debris settling. " + NEG, 3000, 1),
    "train_smash_b": ("Foley sound design: heavy steel train car slamming down onto asphalt, one massive metallic "
                      "impact with sparks and scraping, at the very start. " + NEG, 3000, 2),
    "car_slam": ("Foley sound effect: a car landing hard on a road after a jump, suspension bottoming out, metal "
                 "chassis slam and tire screech, one impact at the very start. " + NEG, 3000, 3),
    "gunshot_far": ("Sound effect: a single distant pistol gunshot echoing between city buildings at night, long "
                    "reverberant tail, heard from far away. " + NEG, 3000, 4),
}


def main(argv):
    dry = "--dry-run" in argv
    only = [a for a in argv if not a.startswith("--")]
    os.makedirs(OUT, exist_ok=True)
    for name, (vid, text, seed) in VOICE.items():
        if only and name not in only:
            continue
        out = os.path.join(OUT, name + ".mp3")
        if os.path.exists(out):
            continue
        cf.generate("elevenlabs/eleven-v3", {"text": text, "voice_id": vid, "seed": seed,
                                             "output_format": "mp3_44100_192"}, out, tag="sfx_vo", dry_run=dry)
    for name, (prompt, ms, seed) in MUSIC.items():
        if only and name not in only:
            continue
        out = os.path.join(OUT, name + ".mp3")
        if os.path.exists(out):
            continue
        cf.generate("elevenlabs/music-v2", {"prompt": prompt, "music_length_ms": ms, "force_instrumental": True,
                                            "output_format": "mp3_48000_192"}, out, tag="sfx_gen",
                    dry_run=dry)


if __name__ == "__main__":
    main(sys.argv[1:])
