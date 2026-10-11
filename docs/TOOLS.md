# Generation tools: how-to for agents

Everything runs on the Cloudflare account through `tools/gen/` (copied from moongazing and moongazing-public-version, then adapted).
Read `docs/recon/pipeline.md` first. The standing rules:

- **Never deploy, modify or delete Cloudflare Workers or KV namespaces.** We only write our own `job:*:rewind2/...` keys into the relay's KV and read back our own results.
- This repo is **public**. Never commit tokens, the account id, the KV namespace id, or media. `media/` and `work/` are gitignored (only `*.md` files under `media/` can be committed).
- Every paid call is logged. The project hard cap is **$400** (all images and video together). Check spend before and after each batch, and ask Jade before going past a budget you were given.

## Setup

| What | Where |
|---|---|
| Python | `PY=~/Documents/moongazing/.venv/bin/python` (it has jsonschema, PyAV, PIL, numpy and torch). `/usr/bin/python3` has no numpy. |
| ffmpeg | `~/Documents/moongazing/.venv/bin/ffmpeg` (static v7.0.2: no `drawtext`, but libass works). There is no ffprobe: use PyAV (`gen.probe(path)`). Override with `FFMPEG=`. |
| Auth | Wrangler OAuth token in `~/.config/.wrangler/config/default.toml`, read by `tools/gen/cfauth.py` at call time and refreshed automatically via `npx -y wrangler whoami` (run that by hand if a call returns 401; if it still fails, ask Jade to run `npx wrangler login`). |
| Local ids (gitignored) | `work/cf_account_id.txt` (account id) and `work/gen_kv_ns.txt` (relay JOBS namespace). Alternatively set `CF_ACCOUNT_ID` / `GEN_KV_NS`. |
| Model catalog | `docs/gen_catalog/<author>-<model>.json` (schemas and list prices), `INDEX.tsv`, `LIVE.tsv`. Refresh with `$PY tools/gen/catalog.py` (a free probe). |

## Images (sync): `tools/gen/cf.py`

```python
import sys; sys.path.insert(0, "tools/gen"); import cf
cf.generate("google/nano-banana-pro",
            {"prompt": "...", "aspect_ratio": "16:9", "image_size": "2K", "image_input": ["file:inputs/jade_in_outfit.png"]},
            "media/x/frame.png", tag="my_tag")          # returns [paths]; validates the schema, checks the cap, logs
```
CLI: `$PY tools/gen/cf.py MODEL OUT '<json input>' --tag=x [--dry-run]`. Any `"file:<path>"` string becomes a data URI.
Add `--dry-run` to validate a call and see its cost estimate without spending anything.

Input shapes per model:
- `openai/gpt-image-2`, `openai/gpt-image-2.5-sunburst|-flare`: `{prompt, size:"1536x1024", quality:"high", images:[...]}`. Output is at most 1536×1024 (3:2), so crop it to 16:9 yourself.
- `google/nano-banana-pro`: `{prompt, aspect_ratio:"16:9", image_size:"2K", image_input:[≤3]}` (2K = 2752×1536).
- `bytedance/seedream-5-pro`: `{prompt, size:"2560x1440", watermark:false, image: str | [≤10]}`.
- `xai/grok-imagine-image-2.0`: `{prompt, aspect_ratio:"16:9", resolution:"2k", quality:"medium", response_format:"b64_json", images:[{"url": ...}]}` (`b64_json` is required).
- Style-test adapters (all four models above): `media/style_tests/scripts/st.py` `inp_for(model, prompt, refs)`.

## Video (async relay queue): `tools/gen/gen.py` + `tools/gen/vgen.py`

Video takes about 5–5.5 min from submit to file (a 2 min queue lead plus generation). Submit first, then do other work while it runs.
1. Add the shot to `tools/gen/shots.py` (`SHOTS["NAME"] = dict(model, image=<first frame under media/>, duration, prompt, camera_fixed=...)`).
2. `$PY tools/gen/vgen.py submit NAME --res=480p --dry-run` (validate and estimate), then run it again without `--dry-run`.
3. `$PY tools/gen/vgen.py wait NAME` (or `collect NAME`). This writes `media/gen/NAME/take_N.mp4` plus `take_N_sheet.jpg` (6 frames).
Lower level: `gen.py spec|submit|status|collect|wait|requeue|ref-image|audio-ref` (see its docstring). The job prefix is `rewind2/`.
Models: `bytedance/seedance-2.0` (480p $0.07/s, keyframe-locked), `minimax/h3` (768P $0.08/s; strip its audio), and `bytedance/seedance-2.5` for singing only.

## ElevenLabs (via the catalog; there is no xi-api-key)

```python
cf.generate("elevenlabs/eleven-v3", {"text": "[whispering] Never stop.", "voice_id": "<voice id>",
            "output_format": "mp3_44100_128"}, "media/audio/never_stop.mp3", tag="vo")          # $0.0001/char
cf.generate("elevenlabs/music-v2", {"prompt": "tape rewind whoosh", "music_length_ms": 4000,
            "force_instrumental": True}, "media/audio/rewind_sfx.mp3", tag="sfx")              # $0.0025/s
```
ElevenLabs has no SFX model in the catalog; use `music-v2` for sound effects. For speech-to-text, use `xai/grok-stt` or `@cf/openai/whisper-large-v3-turbo`.

## Spend

`$PY tools/gen/spend.py` (add `--tags` for a per-tag breakdown) prints the running total across `media/genlog.jsonl` (every sync call, plus relay submits and results)
and `media/gen/spend.jsonl` (vgen takes). Rows are matched by job id, so nothing is counted twice. Errored jobs are refunded. The cap is `REWIND_CAP` (default 400).
`cf.generate`, `gen.submit` and `vgen.submit` refuse any call that would exceed it. All figures are list-price estimates, because the token cannot read the bill.
