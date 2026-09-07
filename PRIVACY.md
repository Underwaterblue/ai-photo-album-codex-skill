# Privacy & Data-Safety Statement

## 1. Local-only processing

All photo processing happens **on the user's local machine**. The project
contains **no networking code**: it does not upload, stream or phone home
anything, and it does not call any external image / AI / API service.

## 2. No training

No model is trained, fine-tuned or fed with your photos. Styling is a small,
deterministic pipeline (resize, contrast/colour enhancement, layout text).

## 3. Privacy protection — this version uses full-image Gaussian blur

`src/cleaner.py` copies every accepted photo into `./temp_blurred/` as a
**full-image Gaussian-blurred version (radius = 10)**, and **all downstream
steps (grouping, styling, export) work only on those blurred copies**. The
original files are never modified and never participate in the output.

This is an intentional, simple privacy placeholder: faces, license plates and
house numbers are made unrecognisable by blurring the whole frame. The cost is
that output images are soft/blurred.

> Precision redaction (detect faces / plates / doors and blur only those
> regions, keeping the rest sharp) is **deferred to a later version** and
> marked with `# TODO` in `src/cleaner.py`. Until then, treat every generated
> album as fully blurred.

## 4. Data you must not commit

* `photos/` — your source photos (git-ignored).
* `output/` — generated albums / previews (git-ignored).
* `temp_blurred/` — privacy-blur working copies (git-ignored).
* `.env` and any secrets (git-ignored, and none are needed anyway).

Check before a commit with:

```bash
git status
git check-ignore photos output temp_blurred   # all three should be listed
```

## 5. What the tool will/won't do to pictures

It only blurs (this version), crops/fits, lightens colours and overlays
typography — it will not warp faces, swap faces, add unrelated objects,
generate garbled text, or change the identity of buildings or scenes.
Original source photos are **never modified**.

## 6. License & responsibility

You are responsible for having the legal right to process the photos you
input. This tool does not supply or condone using copyrighted content.
