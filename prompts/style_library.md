# style_library.md — style vocabulary (placeholder)

Reference vocabulary for the five visual styles used in `src/styler.py`.

| Mode        | Scene suggestion   | Visual keywords                                             |
|-------------|--------------------|-------------------------------------------------------------|
| modern      | city / architecture| 12-column grid, bold sans-serif, generous whitespace        |
| ink_print   | landscape          | low saturation, ink/paper texture, serif titles             |
| collage     | street / human     | torn-paper edges, offset layering, high contrast            |
| fashion     | portrait / travel  | soft film-like tones, airy margins, editorial hierarchy     |
| neon        | night              | dark background, fluorescent accents, bold type             |

In code, a mode currently maps to: a spread background colour, a cover accent
colour, and (via `strength`) the amount of contrast/colour adjustment. New
styles should be added as new entries in these maps, keeping the simple
pipeline unchanged.
