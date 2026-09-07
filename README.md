# ai-photo-album-codex-skill

A **local-first** AI photo album generator. Point it at a folder of photos and
it produces a set of themed photo albums — each with a cover, cross-page
spreads, a PDF, a "book spine wall" placeholder and a local HTML preview.

Everything runs **on your machine**. No photos are uploaded anywhere, nothing
is used for training, and no network access or API keys are involved.

```
照片清洗 (clean)  ->  分组 (group)  ->  风格应用 (style)  ->  导出 (export)  ->  预览 (preview)
```

---

## Features

* Multi-album output from one input folder (`--albums`, `--pages`).
* 5 visual styles + automatic mode (`modern / ink_print / collage /
  fashion / neon`, default `auto`).
* Spread ratio `16:9` or `A4`, output resolution via `--dpi`.
* Quality filter (brightness / contrast / sharpness) + simple file-name
  de-duplication before styling.
* PNG pages + merged `album.pdf` + `spine_wall.png` per album.
* A self-contained `index.html` preview that opens straight from disk.
* Privacy: every photo is copied to `./temp_blurred/` as a full-image
  Gaussian-blurred version (radius 10) and only those copies are used
  downstream (see [PRIVACY.md](PRIVACY.md)).

> **Privacy note**: this version protects privacy by working on **full-image
> Gaussian-blurred copies** (`radius = 10`) written to `./temp_blurred/` by
> `src/cleaner.py`; original files are never used downstream. Precise
> face / license-plate / door-plate redaction is **deferred** (`# TODO` in
> `src/cleaner.py`). Output albums are therefore fully blurred — review before
> publishing. See [PRIVACY.md](PRIVACY.md).

---

## Quick start

### 1. Install

```bash
pip install -r requirements.txt
```

Only two real dependencies are used: **Pillow** and **pypdf**.

### 2. Put photos in place

```bash
mkdir -p photos   # drop .jpg / .jpeg / .png files here
```

### 3. Generate albums

One-shot script (bash):

```bash
./run.sh ./photos ./output
```

or manually:

```bash
python src/main.py \
  --input ./photos \
  --albums 3 --pages 12 \
  --ratio 16:9 --dpi 300 \
  --style-mode auto --style-strength balanced \
  --output ./output
```

### 4. Open the preview

Open `./output/index.html` in a browser. It lists the spine wall and every
album with a cover thumbnail and a `album.pdf` download link.

### 5. Verify

```bash
python tests/smoke_test.py    # prints "Smoke test passed"
```

---

## Codex Skill entry (SKILL.md)

[SKILL.md](SKILL.md) is the agent-facing brief: parameters, capabilities,
constraints and run commands. `prompts/` holds the style library and art
direction used to steer the output:

* `prompts/main_prompt.md` — overall "photo album curator" prompt.
* `prompts/style_library.md` — the five style modes & rules.
* `prompts/style_reference.md` — target visual direction (red/black,
  torn-paper collage, ink-print, magazine spreads).
* `prompts/negative_prompt.md` — hard do-not-do constraints.

---

## Local shell (app/)

`app/` is a **static parameter shell** (no server, no Python execution). Open
`app/index.html` in a browser to pick input/output folders, albums, pages,
ratio, DPI, style mode and strength — it renders the equivalent `python
src/main.py …` command for you to run in a terminal, then you open
`output/index.html` to browse the result. It never reads or uploads photos.

---

## Command-line parameters

| Argument        | Meaning                                   | Default      | Choices / notes                        |
|-----------------|-------------------------------------------|--------------|----------------------------------------|
| `--input`       | Source photo folder (required)            | —            | jpg / jpeg / png                       |
| `--albums`      | Number of albums to produce               | `3`          | Groups are evenly split                |
| `--pages`       | Pages per album (reserved)                | `12`         | Actual count follows available photos  |
| `--ratio`       | Single-page ratio                         | `16:9`       | `16:9` → 1920×1080; `A4` → 2480×3508   |
| `--dpi`         | Output resolution (PNG + PDF)             | `300`        | —                                      |
| `--style-mode`  | Visual style                              | `auto`       | auto / modern / ink_print / collage / fashion / neon |
| `--style-strength` | Style-strength preset                  | `balanced`   | mild / balanced / strong (see Styles)  |
| `--output`      | Output folder                             | `./output`   | —                                      |

If no valid photo is found, the tool prints a warning, still writes an empty
preview page and exits cleanly — it never crashes.

---

## Styles

| Mode        | Look / mood                              | Spread background |
|-------------|------------------------------------------|-------------------|
| `modern`    | City / architecture — grid, bold, airy   | `#f8f8f8`         |
| `ink_print` | Landscape — low saturation, paper feel   | `#f0ebe4`         |
| `collage`   | Street / human — high contrast           | `#eae6e2`         |
| `fashion`   | Portrait / travel — soft, roomy margins  | `#faf8f5`         |
| `neon`      | Night — dark background, bright text     | `#0a0a0a`         |

`auto` picks a style from the group's average brightness / contrast /
saturation (`src/styler.py` → `_detect_style`):

1. average brightness < 0.3 → `neon`
2. else brightness > 0.7 **and** average contrast > 0.3 → `modern`
3. else average saturation > 0.5 → `fashion`
4. else → `ink_print`

Style mode only changes the spread background colour and the cover accent
colour. `--style-strength` selects how strongly each photo is adjusted:

| Preset     | Contrast × | Colour × |
|------------|------------|----------|
| `mild`     | 1 + 0.2    | 1 − 0.1  |
| `balanced` | 1 + 0.4    | 1 − 0.25 |
| `strong`   | 1 + 0.6    | 1 − 0.4  |

No extra filters are applied to the photo itself.

---

## Output layout

```
output/
├── index.html                 # local preview (spine wall + albums)
├── album_00/
│   ├── cover.png              # cover
│   ├── page_000.png           # cross-page spreads (page_001, …)
│   ├── album.pdf              # all spreads merged into one PDF
│   └── spine_wall.png         # "book spine" placeholder wall
├── album_01/
└── album_02/
```

The `album.pdf` contains the inner spreads only; `cover.png` is exported
separately (edit `src/exporter.py` if you prefer to include it).

---

## Project layout

```
SKILL.md            agent-facing brief (parameters / capabilities / constraints)
src/
  __init__.py
  main.py           CLI entry point (argparse + pipeline orchestration)
  cleaner.py        scan, quality filter, de-duplicate, Gaussian-blur temp copies
  grouper.py        sort by mtime/name then even split + title generation
  styler.py         per-group style application (album object)
  exporter.py       PNG / PDF / spine-wall export
  previewer.py      index.html preview generator
app/
  index.html        static local shell (pick parameters -> build command)
  style.css
  preview.js
prompts/            main_prompt / style_library / style_reference / negative_prompt
tests/
  smoke_test.py     end-to-end smoke test on placeholder photos
  fixtures/         README for optional copyright-free fixtures
assets/fonts/       open-source font README (no fonts are committed)
.github/workflows/ci.yml
```

---

## Fonts

Open-source fonts only. If `assets/fonts/NotoSansSC-*.ttf` are missing, the
code falls back to Pillow's default font (see [assets/fonts/README.md](assets/fonts/README.md)).

---

## Privacy & safety

* Local-only processing — no uploads, no training, no network code.
* No hard-coded secrets, no API keys, no `.env` required.
* `photos/`, `output/` and `temp_blurred/` are git-ignored; do **not** commit
  personal photos.
* Privacy is protected by working on **full-image Gaussian-blurred copies**
  (`radius = 10`) in `./temp_blurred/`; precise face/plate/door redaction is
  deferred (`# TODO` in `src/cleaner.py`). See [PRIVACY.md](PRIVACY.md).
* The tool never distorts faces, never swaps faces, never adds objects and
  never alters building/scene identity — it only blurs (this version),
  crops/fits, recolours lightly and overlays layout text.

---

## Releasing on GitHub

1. Generate a clean archive:
   ```bash
   ./package.sh      # -> ai-photo-album-codex-skill.zip (photos/ & output/ excluded)
   ```
2. Inspect what would be committed, make sure no personal data is tracked:
   ```bash
   git status
   git check-ignore photos output temp_blurred   # all three should print
   ```
3. Commit, tag and push:
   ```bash
   git add .
   git commit -m "Release v0.1.0"
   git tag v0.1.0
   git push origin main --tags
   ```
4. Create a GitHub Release from tag `v0.1.0` and attach the `.zip` from
   step 1. CI runs `python tests/smoke_test.py` on every push/PR.

---

## License

MIT — see [LICENSE](LICENSE).
