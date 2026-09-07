# Style reference — visual direction

Design language the album output aims for. Frame these as *rules for a layout
editor*, not instructions to alter photo content.

## Target look

Modern photography-book / magazine layout: big margins, cross-page bleeds,
red-and-black high contrast, torn-paper collage, ink-wash print texture.

- **Cover** — bold sans-serif English title, smaller Chinese subtitle, red /
  black colour blocks, faint paper grain.
- **Spine wall** — equal-width spine array, vertically-set book titles,
  black/white or red/black, alternating shades.
- **Spread** — left-image-right-text or full-bleed image; oversized bold
  titles, light serif captions; unified page numbers and running header.

## Palette

- Primary: black / white / red.
- Accents: ink-wash blue, ochre (赭石).
- Photos: low saturation underlaid with high-saturation geometric elements.

## Material

Matte paper, slight grain, torn-paper edges, collage offset — but never
over-filtered.

## Typography

- English: Inter / Bebas Neue (H1), Inter (body).
- Chinese: 思源黑体 / 思源宋体 (Noto Sans/Serif SC), clear hierarchy
  H1 / H2 / body / page number.

## Grid

12-column grid; margins 8%–15% (suggest 12%); images may bleed but subjects
must not be cropped away.

## Implementation note

The current deterministic styler (`src/styler.py`) implements this in a
**simplified form**: a mode selects a spread background colour and a cover
accent colour; typography uses open-source Noto fonts with a PIL-default
fallback. Textures (paper grain, torn edges, collage offsets) are future work
and are intentionally not applied by the v0.1.0 code — see `src/styler.py`
and the `mode` → colour maps in `MODE_BACKGROUND` / `MODE_ACCENT`.
