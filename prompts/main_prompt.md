# main_prompt.md — design intent (placeholder)

Placeholder for the optional prompt template that would steer a generative /
styling pass. This project does **not** call any external image API.

Intent summary for a future local "album art direction" pass:

- Keep the source scene intact: no face warping, no face swap, no added
  objects, no identity change of buildings/scenes.
- Only layout, crop/fit, light recolouring, typography.
- Respect the selected style mode (modern / ink_print / collage / fashion /
  neon) and the style-strength preset (mild / balanced / strong).
- Add page numbers and titles only; no garbled text.

This document is intentionally small — see `style_library.md` and
`negative_prompt.md` for the style/negative vocabulary.
