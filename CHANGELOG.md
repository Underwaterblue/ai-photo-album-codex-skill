# Changelog

All notable changes to this project are documented in this file.

## [v0.1.0] - 2026-09-07

### Added
- CLI entry point `src/main.py` (`--input`, `--albums`, `--pages`, `--ratio`,
  `--dpi`, `--style-mode`, `--style-strength`, `--output`).
- Pipeline: clean -> group -> style -> export -> preview.
- `src/cleaner.py`: recursive scan for `.jpg/.jpeg/.png`, brightness /
  contrast / sharpness quality filter, file-name de-duplication, and privacy
  via full-image Gaussian-blurred copies (`radius = 10`) written to
  `./temp_blurred/`; all later stages use only those copies (originals
  untouched). Precise redaction deferred (`# TODO`).
- `src/grouper.py`: sort by (modification time, file name) then even split
  into `num_albums` groups + title generation (`ALBUM <3-digit>` / 主题画册).
- `src/styler.py`: album object generation — cross-page spreads at
  16:9 (1920×1080) or A4 (2480×3508), 5 style modes + `auto` (new brightness /
  contrast / saturation rules), `--style-strength` presets (mild / balanced /
  strong) driving contrast/colour adjustments, cover, safe font fallback,
  per-page failure fallback to a marked placeholder.
- `src/exporter.py`: `cover.png`, `page_NNN.png`, `album.pdf` (pypdf with a
  Pillow fallback) and `spine_wall.png`.
- `src/previewer.py`: local `index.html` preview with spine wall and album
  cards (black/white, relative paths only).
- `tests/smoke_test.py`: offline end-to-end smoke test using Pillow-generated
  placeholder photos.
- `run.sh`, `package.sh`, `requirements.txt`, `.gitignore`, `.env.example`.
- Docs: `README.md`, `PRIVACY.md`, `assets/fonts/README.md`.
- GitHub Actions CI (`.github/workflows/ci.yml`) running the smoke test.
- MIT `LICENSE`.
- `SKILL.md` agent-facing brief (parameters / capabilities / constraints).
- `app/` static local shell (`index.html` / `style.css` / `preview.js`) that
  assembles the CLI command; never executes Python or reads photos.
- `prompts/style_reference.md` art-direction reference (red/black,
  torn-paper collage, ink-print, magazine spreads).
- Package markers `src/__init__.py`, `tests/__init__.py` and
  `tests/fixtures/README.md`.

### Notes / limitations
- `--pages` is parsed but reserved: actual page count follows the number of
  available photos.
- This version's privacy protection is a full-image Gaussian blur
  (`radius = 10`) applied to copies in `./temp_blurred/`; output albums are
  therefore soft/blurred. Precision face / plate / doorplate redaction is
  deferred (see `PRIVACY.md`).
- The `./temp_blurred/` working folder is git-ignored and accumulates
  per-run blurred copies; safe to delete at any time.
- No HEIC/RAW input, no EXIF-based grouping, no perceptual-hash de-duplication
  (kept intentionally dependency-free).
- Textures described in `prompts/style_reference.md` (paper grain, torn
  edges, collage offsets) are a target direction; v0.1.0 applies only the
  simplified background/accent-colour mapping in `src/styler.py`.
