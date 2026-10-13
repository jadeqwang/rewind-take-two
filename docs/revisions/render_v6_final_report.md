# v6 final encodes and verification report

Completed 2026-10-13, following [render_v6_final.md](render_v6_final.md). **Both uploads meet the 100,000,000-byte limit, all three files pass technical verification, and all sixteen requested fix checks pass.** Visible compression artifacts remain in both uploads. **The 720p upload looks better overall at normal viewing size**, especially in the colored ghosts, triangle merge, and glass-door glow.

| File | Bytes | Decimal MB | Result |
| --- | ---: | ---: | --- |
| [Existing 1080p master](../../deliverables/rewind_v6_master_1080p_sfx.mp4) | 2,051,243,305 | 2,051.243305 | Verified; read-only |
| [1080p 100 MB upload](../../deliverables/rewind_v6_upload_1080p_sfx_100MB.mp4) | **96,557,639** | **96.557639** | PASS; 3,442,361 bytes under limit |
| [720p 100 MB upload](../../deliverables/rewind_v6_upload_720p_sfx_100MB.mp4) | **96,103,616** | **96.103616** | PASS; 3,896,384 bytes under limit |

Both uploads are within the requested 95–99 MB aim. The 720p upload is 454,023 bytes smaller. Neither required a bitrate retry.

## Waiting, disk space, and master log

Ran `df -h .` before work: **11 GB available**, above the 2 GB stop threshold. Polled `deliverables/wip/rewind_v6_master_render.log` every **30 s** until a line starting `[encode] done` appeared, with a 25-minute timeout. Completion was detected after **330.03 s**; no unrecovered error was encountered. [Wait/poll record](../../deliverables/wip/rewind_v6_master_wait.json).

The completed log contains:

```text
[render] 5857 frames in 355.9 s = 16.46 fps (0.69x realtime), incl. browser start-up
[encode] done in 158.3 s → /home/jade/Documents/rewind-take-two/deliverables/rewind_v6_master_1080p_sfx.mp4
```

There are **36 Canvas2D readback performance warnings** and **three recovered detached-image worker failures**, at frames **5773, 5799, and 5809**. These are the retries described by the brief; the final render count accounts for all **5,857 frames**. No backend fallback is logged. [Existing master render log](../../deliverables/wip/rewind_v6_master_render.log).

Ran `df -h .` again after master completion: **6.2 GB available**. The measured free space before encoding was 6,589,669,376 bytes, and after encoding and evidence extraction it was 5,829,406,720 bytes. The master, mix, and render log retained their byte sizes and modification times throughout verification.

## Commands and encoding results

Used FFmpeg **7.0.2-static** and the prescribed Python environment with PyAV **19.0.1**, NumPy **2.5.3**, and SciPy **1.18.1**. No system ffprobe is installed; probing used PyAV as directed. The complete automation command was:

```sh
/home/jade/Documents/moongazing/.venv/bin/python -u \
  deliverables/wip/rewind_v6_encode_verify.py
```

The [helper source](../../deliverables/wip/rewind_v6_encode_verify.py) and [complete executed FFmpeg argv record](../../deliverables/wip/rewind_v6_commands.json) preserve the commands and validation logic. Additional Pillow crops isolate six small fix details in the [feature crop manifest](../../deliverables/wip/rewind_v6_spotchecks/feature_crop_manifest.json).

Both uploads used two-pass x264, `-preset slow`, target video bitrate **2,980k**, H.264 High, yuv420p, 24 fps. Audio was mapped from the master's audio stream and encoded as AAC 192k, 48 kHz stereo. The 1080p encode retained 1920×1080; the 720p encode used `scale=1280:720:flags=lanczos`. Both used `-movflags +faststart`.

Encoding command pattern, with the executed parameters listed below:

```sh
/home/jade/Documents/moongazing/.venv/bin/ffmpeg \
  -hide_banner -loglevel info -stats -stats_period 10 -y \
  -i /home/jade/Documents/rewind-take-two/deliverables/rewind_v6_master_1080p_sfx.mp4 \
  -map 0:v:0 [SCALE] -c:v libx264 -preset slow -b:v 2980k \
  -profile:v high -pix_fmt yuv420p -r 24 \
  -passlogfile PASSLOG -pass 1 -an -f null -

/home/jade/Documents/moongazing/.venv/bin/ffmpeg \
  -hide_banner -loglevel info -stats -stats_period 10 -y \
  -i /home/jade/Documents/rewind-take-two/deliverables/rewind_v6_master_1080p_sfx.mp4 \
  -map 0:v:0 -map 0:a:0 [SCALE] -c:v libx264 -preset slow -b:v 2980k \
  -profile:v high -pix_fmt yuv420p -r 24 \
  -passlogfile PASSLOG -pass 2 \
  -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart OUTPUT
```

`[SCALE]` was omitted for 1080p and was `-vf scale=1280:720:flags=lanczos` for 720p. `PASSLOG` was the absolute workspace path to `deliverables/wip/rewind_v6_1080p_100MB_x264` or `deliverables/wip/rewind_v6_720p_100MB_x264`; `OUTPUT` was the corresponding upload listed above. All four passes returned **exit 0**.

| Encode | First pass wall | Second pass wall | Combined wall | Evidence |
| --- | ---: | ---: | ---: | --- |
| 1080p | 29.38 s | 45.14 s | **74.52 s** | [Metrics and exact commands](../../deliverables/wip/rewind_v6_1080p_100MB_encode_2980k.json), [pass 1 log](../../deliverables/wip/rewind_v6_1080p_100MB_2980k_pass1.log), [pass 2 log](../../deliverables/wip/rewind_v6_1080p_100MB_2980k_pass2.log) |
| 720p | 19.81 s | 34.96 s | **54.77 s** | [Metrics and exact commands](../../deliverables/wip/rewind_v6_720p_100MB_encode_2980k.json), [pass 1 log](../../deliverables/wip/rewind_v6_720p_100MB_2980k_pass1.log), [pass 2 log](../../deliverables/wip/rewind_v6_720p_100MB_2980k_pass2.log) |

## Probe and complete decode

All three files have exactly **one video stream and one audio stream**, starting at 0. Video is **H.264 High, yuv420p, 24/1 fps**, with **5,857 frames** and video duration **244.041667 s**. Audio is **AAC-LC, 48 kHz stereo**. All durations meet **244.05 ± 0.05 s**, and all frame counts meet **5,857 ± 1**.

| Measurement | Master | 1080p upload | 720p upload |
| --- | ---: | ---: | ---: |
| Frame size | 1920×1080 | 1920×1080 | 1280×720 |
| Container duration | 244.041667 s | 244.053 s | 244.053 s |
| Audio stream duration | 244.041 s | 244.053 s | 244.053 s |
| Video bitrate, measured | 66,924,070 bit/s | 2,963,151 bit/s | 2,948,248 bit/s |
| Audio bitrate, measured | 312,783 bit/s | 196,618 bit/s | 196,618 bit/s |
| Container bitrate, measured | 67,242,396 bit/s | 3,165,136 bit/s | 3,150,253 bit/s |
| `moov` offset | 32 | 32 | 32 |
| `mdat` offset | 168,204 | 167,372 | 167,967 |

`moov` precedes `mdat` in both uploads, confirming **fast start**. Measured average bitrates differ slightly from their encoder targets, as expected with two-pass encoding and AAC. Probe evidence: [master](../../deliverables/wip/rewind_v6_master_probe.json), [1080p](../../deliverables/wip/rewind_v6_1080p_probe.json), [720p](../../deliverables/wip/rewind_v6_720p_probe.json).

Decoded every frame of each file using:

```sh
/home/jade/Documents/moongazing/.venv/bin/ffmpeg \
  -hide_banner -v error -stats_period 10 -progress pipe:1 \
  -i X -f null -
```

`X` was each file's absolute path. **All three decodes returned exit 0, emitted no errors, and decoded 5,857 frames with zero duplicates or drops.** Master decode took 12.03 s, 1080p took 3.16 s, and 720p took 2.14 s. Each separate error log is empty. Decode results and commands: [master](../../deliverables/wip/rewind_v6_master_decode.json), [1080p](../../deliverables/wip/rewind_v6_1080p_decode.json), [720p](../../deliverables/wip/rewind_v6_720p_decode.json).

## Audio alignment

Decoded the supplied MP3 mix and each video audio stream to mono 8 kHz float PCM:

```sh
/home/jade/Documents/moongazing/.venv/bin/ffmpeg \
  -hide_banner -v error -i X -map 0:a:0 -ac 1 -ar 8000 -f f32le pipe:1
```

NumPy/SciPy correlated the complete waveforms over a ±1 s offset search and normalized the correlation over the best-offset overlap. Positive offset would mean video audio is late relative to the mix. The complete **244.050 s** mix overlaps all three decoded tracks: **1,952,400 samples**. Each video produced 1,952,427 decoded samples, including a small AAC tail.

| File | Offset | Normalized correlation | Result |
| --- | --- | ---: | --- |
| Master | **0 samples / 0.000 ms** | **0.9998820461** | PASS; within ±20 ms |
| 1080p upload | **0 samples / 0.000 ms** | **0.9990224220** | PASS; within ±20 ms |
| 720p upload | **0 samples / 0.000 ms** | **0.9990224220** | PASS; within ±20 ms |

[Detailed audio alignment results](../../deliverables/wip/rewind_v6_audio_alignment.json). The uploads' matching results are consistent with encoding the same master audio using the same AAC settings.

## Black-frame scans

Ran on every video track:

```sh
/home/jade/Documents/moongazing/.venv/bin/ffmpeg \
  -hide_banner -loglevel info -i X -map 0:v:0 \
  -vf 'blackdetect=d=0.041:pix_th=0.02:pic_th=0.98' -an -f null -
```

| File | Start (s) | End (s) | Duration (s) | Assessment |
| --- | ---: | ---: | ---: | --- |
| Master | 93.000000 | 93.083333 | 0.083333 | Expected authored two-frame cut before “Reload.” |
| 1080p upload | 93.000000 | 93.083333 | 0.083333 | Same expected cut |
| 720p upload | 93.000000 | 93.083333 | 0.083333 | Same expected cut |
| Master | 222.791667 | 225.625000 | 2.833333 | Expected credits on black |
| 1080p upload | 222.791667 | 225.250000 | 2.458333 | Expected credits on black |
| 720p upload | 222.791667 | 225.250000 | 2.458333 | Expected credits on black |
| Master | 232.750000 | 232.833333 | 0.083333 | Expected credits-to-coda boundary |
| 1080p upload | 232.750000 | 232.833333 | 0.083333 | Same expected boundary |
| 720p upload | 232.750000 | 232.833333 | 0.083333 | Same expected boundary |

**PASS: no unexpected black interval in any file.** The credits boundary is within the brief's approximate 222.8–232.8 s interval. The detector requires ≥98% near-black pixels, so enough visible credits text ends a detection span before the credits sequence ends. Compression affects that threshold crossing slightly, explaining the different first credits endpoints. It does not indicate additional black frames.

Results and exact commands: [master](../../deliverables/wip/rewind_v6_master_blackdetect.json), [1080p](../../deliverables/wip/rewind_v6_1080p_blackdetect.json), [720p](../../deliverables/wip/rewind_v6_720p_blackdetect.json). Full logs: [master](../../deliverables/wip/rewind_v6_master_blackdetect.log), [1080p](../../deliverables/wip/rewind_v6_1080p_blackdetect.log), [720p](../../deliverables/wip/rewind_v6_720p_blackdetect.log).

## Master contact sheet

Created and visually inspected [rewind_v6_master_sheet.jpg](../../deliverables/wip/rewind_v6_master_sheet.jpg): **62 frames at 0, 4, 8, …, 244 s**, six columns, with four unused padding cells. Extraction command:

```sh
/home/jade/Documents/moongazing/.venv/bin/ffmpeg \
  -hide_banner -loglevel warning \
  -i /home/jade/Documents/rewind-take-two/deliverables/rewind_v6_master_1080p_sfx.mp4 \
  -map 0:v:0 -vf 'select=not(mod(n\,96)),scale=320:180' \
  -fps_mode vfr -q:v 2 -y \
  /home/jade/Documents/rewind-take-two/deliverables/wip/rewind_v6_master_sheet_frames/frame_%03d.jpg
```

Pillow added timestamps and assembled the 1976×2340 sheet. **No sampled frame looks wrong:** no grey section slate, missing major layer, accidental blank, or glitched frame was found. The 224 s sample contains the start of credits text on black; 228 s and 232 s show the expected credits/end text. The 93 s cut falls between four-second samples and is covered by the full black scan. The rewind distortion and translucent ghosts are intentional imagery.

JPEG extraction completed successfully with a deprecated pixel-format warning; this is recorded in the [sheet extraction log](../../deliverables/wip/rewind_v6_master_sheet_extraction.log).

## Sixteen requested fix checks

Saved all sixteen full-resolution pairs in [rewind_v6_spotchecks](../../deliverables/wip/rewind_v6_spotchecks/manifest.json), **master on the left, 1080p 100 MB upload on the right**. Each picture panel is 1920×1080, with labels above it. Visually inspected the paired overviews and native-pixel crops where the small text or eraser colors required them.

Frame extraction used:

```sh
/home/jade/Documents/moongazing/.venv/bin/ffmpeg \
  -hide_banner -v error -ss T -i X -map 0:v:0 -frames:v 1 -y OUTPUT.png
```

| Time | Pair | Finding in both master and 1080p upload |
| --- | --- | --- |
| 0.5 s | [Pair](../../deliverables/wip/rewind_v6_spotchecks/compare_t0000.5.png) | **PASS:** top left reads `ITERATION 4,095`. It is faint during the HUD fade-in over dense hatching; compression reduces its contrast further. [Text crop](../../deliverables/wip/rewind_v6_spotchecks/feature_t0000.5.png). |
| 59.5 s | [Pair](../../deliverables/wip/rewind_v6_spotchecks/compare_t0059.5.png) | **PASS:** car interior, two pencils in her bun, one pink eraser and one pale-blue eraser. Both colors remain distinguishable. [Bun crop](../../deliverables/wip/rewind_v6_spotchecks/feature_t0059.5.png). |
| 93.3 s | [Pair](../../deliverables/wip/rewind_v6_spotchecks/compare_t0093.3.png) | **PASS:** “Reload.”, `×4,096` at top right, and `TIP: TVA agents can only follow what they can trace.` are present and readable. |
| 95.0 s | [Pair](../../deliverables/wip/rewind_v6_spotchecks/compare_t0095.0.png) | **PASS:** `GHOST: ITERATION 4,094`; clock **04:08.46**, split **+0.26** beside it. |
| 98.5 s | [Pair](../../deliverables/wip/rewind_v6_spotchecks/compare_t0098.5.png) | **PASS:** field HUD reads `ITERATION 4,097`, `×4,096`, and **04:11.96**. |
| 101.3 s | [Pair](../../deliverables/wip/rewind_v6_spotchecks/compare_t0101.3.png) | **PASS:** “ACROSS THE …” notice board stands behind her in the field; foreground agents have attached, opaque arms/elbows. No floating elbow or see-through agent arm is apparent. |
| 103.5 s | [Pair](../../deliverables/wip/rewind_v6_spotchecks/compare_t0103.5.png) | **PASS:** earpiece agents fill the foreground; she is small and far off toward the hotel at right. |
| 116.2 s | [Pair](../../deliverables/wip/rewind_v6_spotchecks/compare_t0116.2.png) | **PASS:** orange ghost beside her at the notice board. No floating pistol hand is apparent; the distant agents' guns remain attached to their hands. |
| 124.3 s | [Pair](../../deliverables/wip/rewind_v6_spotchecks/compare_t0124.3.png) | **PASS:** gold ghost beside her on the book; trousers next to her sneaker are translucent, with book detail visible through the lower leg. [Trouser crop](../../deliverables/wip/rewind_v6_spotchecks/feature_t0124.3.png). |
| 133.0 s | [Pair](../../deliverables/wip/rewind_v6_spotchecks/compare_t0133.0.png) | **PASS:** co-op pencil bridge, with proportionate background agents and no oversized agent head. |
| 140.6 s | [Pair](../../deliverables/wip/rewind_v6_spotchecks/compare_t0140.6.png) | **PASS:** full-screen terminal reads `TVA ALERT` / `ANOMALY DETECTED.`; the following line is still typing. |
| 145.2 s | [Pair](../../deliverables/wip/rewind_v6_spotchecks/compare_t0145.2.png) | **PASS:** pencil pull and blue dot on her left chest. |
| 175.0 s | [Pair](../../deliverables/wip/rewind_v6_spotchecks/compare_t0175.0.png) | **PASS:** running up the tower from behind; white jacket back with a large blue dot partly covered by her hair, and no orange band across the back. The upper-arm orange stripes remain. [Back crop](../../deliverables/wip/rewind_v6_spotchecks/feature_t0175.0.png). |
| 215.0 s | [Pair](../../deliverables/wip/rewind_v6_spotchecks/compare_t0215.0.png) | **PASS:** report box reads `TVA REPORT` / `ANOMALY DETECTED` / `CASE 4,098`. |
| 221.0 s | [Pair](../../deliverables/wip/rewind_v6_spotchecks/compare_t0221.0.png) | **PASS:** dissertation door shot has one blue and one pink eraser in the bun. [Bun crop](../../deliverables/wip/rewind_v6_spotchecks/feature_t0221.0.png). |
| 233.9 s | [Pair](../../deliverables/wip/rewind_v6_spotchecks/compare_t0233.9.png) | **PASS:** `ITERATION 4,114` at bottom right while the gloved hand presses the brass plate. The digits overlap bright glove/grid detail and have low contrast, but the updated value is visible in both. [Counter crop](../../deliverables/wip/rewind_v6_spotchecks/feature_t0233.9.png). |

## Compression quality and upload comparison

**Both 100 MB files show visible blocking, smearing, and loss of fine detail compared with the master.** These artifacts are separate from the authored woodcut grain and rewind distortion. The 720p file reduces much of the disruptive breakup but softens fine lines through downscaling; it still has compression artifacts.

Inspected [three-way comparison samples](../../deliverables/wip/rewind_v6_spotchecks/quality/manifest.json), with the master, 1080p upload, and 720p upload at matching times. The 720p frames were enlarged to 1920×1080 with **FFmpeg Lanczos** before comparison. Sampled these ranges:

| Range | Times inspected | Finding |
| --- | --- | --- |
| Rewind, 42–57 s | 44.0, 48.0, 51.6, 55.0 s | Both uploads lose fine hatching and grain around particles, clothing, and warped edges. The difference is modest in the quieter frames. At 51.6 s, 720p has less mottled breakup around the billboard, while 1080p retains some finer line detail. |
| Early ghosts, 94–98 s | 94.5, 96.5, 97.5 s | 1080p shows patchier pale backgrounds and more broken character/ghost outlines. 720p generally holds the outlines together better but remains softer than the master. |
| Late ghosts, 134–138 s | 134.5, 136.5, 137.5 s | The 136.5 s colored crowd has conspicuous compression damage in both uploads, strongest in 1080p. 720p keeps clothing contours and color fills cleaner. The surrounding shots have milder loss of texture. |
| Triangle merge | 204.0 s | Strong blocking and smearing around faces, dark clothing, and thin triangle edges in 1080p. 720p looks clearly cleaner, with remaining softness/artifacts. |
| Lobby | 233.9, 234.5, 236.5, 238.5, 242.0, 243.5 s | The translucent glass-door glow at 233.9–234.5 s becomes patchy/blocky in both uploads, more strongly in 1080p. 720p smooths this breakup. Ledger names and final dialogue remain readable. The quieter queue frames look close, with a slight fine-hatching/sharpness advantage for 1080p. |

**Banding:** no pronounced smooth contour bands were apparent in the reviewed samples. The visible lobby gradient defect is chiefly patchy/blocky tonal transitions and lost grain; neither upload reproduces the master's gradient texture exactly. No claim is made that every possible banding artifact in every frame was excluded.

Also saved six full-resolution [1080p-versus-720p pairs](../../deliverables/wip/rewind_v6_spotchecks/720_vs_1080/manifest.json), each with 1080p on the left and Lanczos-upscaled 720p on the right. Inspected the common-resolution detail crops as well as the normal-size three-way views:

| Time | Pair | Preference at normal viewing size |
| --- | --- | --- |
| 51.6 s | [Pair](../../deliverables/wip/rewind_v6_spotchecks/720_vs_1080/compare_t0051.6.png) | **720p, modestly:** cleaner billboard/rewind edges; some fine hatching is softer. |
| 96.5 s | [Pair](../../deliverables/wip/rewind_v6_spotchecks/720_vs_1080/compare_t0096.5.png) | **720p:** cleaner outlines and less patchy cream background. |
| 136.5 s | [Pair](../../deliverables/wip/rewind_v6_spotchecks/720_vs_1080/compare_t0136.5.png) | **720p, clearly:** less blocky colored ghosts and more continuous clothing contours. |
| 204.0 s | [Pair](../../deliverables/wip/rewind_v6_spotchecks/720_vs_1080/compare_t0204.0.png) | **720p, clearly:** better triangle edges, faces, and dark clothing. |
| 234.5 s | [Pair](../../deliverables/wip/rewind_v6_spotchecks/720_vs_1080/compare_t0234.5.png) | **720p:** smoother glass-door glow and less broken gradient texture. |
| 243.5 s | [Pair](../../deliverables/wip/rewind_v6_spotchecks/720_vs_1080/compare_t0243.5.png) | **Close; slight 1080p detail advantage:** finer architectural hatching; 720p remains readable and only slightly softer. |

**Recommendation: choose the 720p file for the 100 MB delivery.** The reduction in conspicuous blocking outweighs the loss of some fine woodcut texture at normal viewing size. Retain the master for full-quality viewing. The comparison is based on the stated still samples and native-pixel crops; every frame was decoded and black-scanned, while visual review used the contact sheet and listed samples.

## Disposition

All requested outputs and checks are complete. No unexpected black frames, unrecovered decoding errors, audio offset, or missing requested fix was found. The documented compression artifacts and low-contrast counters are quality observations, rather than a failed format, content, or alignment requirement. [Machine-readable encode/verification results](../../deliverables/wip/rewind_v6_encode_verification_summary.json).

Only the two requested uploads, files under `deliverables/wip/`, and this report were written. The existing master was used without re-rendering. No `render.mjs`, git, or delete command was run.

DONE
