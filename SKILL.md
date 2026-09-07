# AI Photo Album Codex Skill

Auto-generate **multi-style photo albums** from a local folder of photos:
cleaning → grouping → style matching → layout → export → local preview.
Local-first: photos never leave the machine, nothing is used for training.

## Parameters

| Parameter      | Default  | Allowed / notes                                     |
|----------------|----------|-----------------------------------------------------|
| `--input`      | —        | photo folder (jpg/jpeg/png) — required              |
| `--albums`     | 3        | number of albums (2–26 recommended)                 |
| `--pages`      | 12       | pages per album (8–20 recommended). Reserved: actual page count follows the available photos |
| `--ratio`      | 16:9     | `A4` (2480×3508) or `16:9` (1920×1080)              |
| `--dpi`        | 300      | export resolution (PNG + PDF)                       |
| `--style-mode` | auto     | auto / modern / ink_print / collage / fashion / neon |
| `--style-strength` | balanced | preset: mild / balanced / strong (see presets below) |
| `--output`     | ./output | output folder                                       |

## Capabilities

- Clean & de-duplicate photos: quality filter (brightness / contrast /
  sharpness) + file-name de-dupe, recursive scan.
- Group photos evenly; per group generate an English title (`ALBUM nnn`)
  and a Chinese subtitle (主题画册).
- Auto-match a style per group from the library in `prompts/style_library.md`
  (`auto` decides from the group's brightness/saturation).
- Produce a cover, cross-page spreads, a spine-wall placeholder, a merged
  PDF (`pypdf`), and a local `index.html` preview.
- Static local shell `app/index.html` for assembling parameters & commands.

## Constraints

- Local only — no public upload, no network code, no training use.
- Privacy: every photo is copied to `./temp_blurred/` as a full-image
  Gaussian-blurred version (radius 10) and only those copies are used
  downstream; precise face/plate/door redaction is deferred (`# TODO` in
  `src/cleaner.py`).
- Preserve original subjects & architecture: only crop/fit, light colour
  grading and typography. No face warp/swap, no added objects, no garbled text.
- Open-source fonts only (`assets/fonts/README.md`); a missing font falls
  back to the PIL default. No hard-coded keys. Never commit `photos/`,
  `output/` or `temp_blurred/` (all git-ignored).

Style-strength presets (contrast × / colour ×): mild `1+0.2 / 1−0.1`,
balanced `1+0.4 / 1−0.25`, strong `1+0.6 / 1−0.4`.

## Run

```bash
pip install -r requirements.txt
python src/main.py --input ./photos --albums 3 --pages 12 \
  --ratio 16:9 --dpi 300 --style-mode auto --style-strength balanced \
  --output ./output
# open ./output/index.html in a browser
```

Smoke test:

```bash
python tests/smoke_test.py    # prints "Smoke test passed"
```
