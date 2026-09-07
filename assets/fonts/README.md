# Fonts

Only **open-source fonts** may live in this folder (or be referenced from it).
Commercial / proprietary font files are **not** allowed in this repository.

## Which fonts the code expects (optional)

The styling code tries to load, in order:

1. `assets/fonts/NotoSansSC-Regular.ttf`
2. `assets/fonts/NotoSansSC-Bold.ttf`

When a font file is missing the code silently falls back to Pillow's built-in
default font, so the tool keeps working even without any fonts installed
(the text is simply smaller/plainer). Font loading is wrapped in
`try/except` everywhere.

## How to get open-source fonts

Use **Noto Sans SC** / **Noto Serif SC** — both are published under the
open-source SIL Open Font License 1.1 (OFL-1.1).

* Google Fonts: <https://fonts.google.com/noto/specimen/Noto+Sans+SC>
* Google Fonts: <https://fonts.google.com/noto/specimen/Noto+Serif+SC>
* Google Noto (GitHub): <https://github.com/googlefonts/noto-cjk>

Suggested setup so the tool looks its best (Chinese + Latin):

```bash
mkdir -p assets/fonts
# Download the two files below and place them here:
#   assets/fonts/NotoSansSC-Regular.ttf
#   assets/fonts/NotoSansSC-Bold.ttf
```

### License note

Keep the OFL license text together with any font file you add
(`assets/fonts/OFL.txt`). Do **not** commit unlicensed or commercial font
files. The rendered album output is generated on the user's machine and is
not distributed as a font work.
