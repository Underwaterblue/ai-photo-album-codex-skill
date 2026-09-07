"""Export one album object to PNG pages, a PDF and a spine-wall image.

Output layout per album (``album_{index:02d}/``)::

    cover.png      - the album cover
    page_000.png   - one PNG per cross-page spread (page_001, ...)
    album.pdf      - inner spreads merged into one PDF
    spine_wall.png - placeholder "book spines" wall

Notes
-----
* PDF export uses ``pypdf`` (the maintained successor of the deprecated
  PyPDF2). Each spread is first encoded by Pillow into an in-memory
  one-page PDF and then imported into a PdfWriter. If pypdf is missing the
  exporter falls back to Pillow's own multipage PDF writer.
* The PDF deliberately contains only the inner spreads; the cover is exported
  separately as cover.png. (Prepend ``album['cover']`` if you want it included.)
* All parent directories are created with ``os.makedirs`` before saving.
"""

import io
import os

from PIL import Image, ImageDraw, ImageFont

SPINE_COL_W = 120
SPINE_HEIGHT = 400

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(_BASE_DIR, "assets", "fonts")
REGULAR_FONT = os.path.join(FONT_DIR, "NotoSansSC-Regular.ttf")


def export_album(album, output_dir, index):
    """Persist ``album`` under ``output_dir/album_{index:02d}``."""
    pages = album["pages"]
    if not pages:
        return None

    dpi = int(album.get("dpi", 300) or 300)
    album_dir = os.path.join(output_dir, "album_{0:02d}".format(int(index)))
    os.makedirs(album_dir, exist_ok=True)

    album["cover"].save(os.path.join(album_dir, "cover.png"), "PNG", dpi=(dpi, dpi))

    for i, page in enumerate(pages):
        page.save(os.path.join(album_dir, "page_{0:03d}.png".format(i)),
                  "PNG", dpi=(dpi, dpi))

    _write_pdf(pages, os.path.join(album_dir, "album.pdf"), dpi)

    spine = build_spine_wall(album.get("title", "ALBUM"), len(pages))
    spine.save(os.path.join(album_dir, "spine_wall.png"), "PNG", dpi=(dpi, dpi))

    return album_dir


def _write_pdf(pages, pdf_path, dpi):
    """Merge the spreads into a single PDF."""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        # Fallback: let Pillow write the multipage PDF directly.
        pages[0].save(pdf_path, "PDF", save_all=True,
                      append_images=pages[1:], resolution=dpi)
        return

    writer = PdfWriter()
    for page in pages:
        buffer = io.BytesIO()
        page.save(buffer, "PDF", resolution=dpi)  # single-page in-memory PDF
        buffer.seek(0)
        writer.add_page(PdfReader(buffer).pages[0])
    with open(pdf_path, "wb") as handle:
        writer.write(handle)


def build_spine_wall(title, page_count):
    """Build a spine-wall placeholder image (black, one 120px spine each)."""
    count = max(1, int(page_count))
    image = Image.new("RGB", (count * SPINE_COL_W, SPINE_HEIGHT), color=(10, 10, 10))
    draw = ImageDraw.Draw(image)

    label = (str(title) if title else "ALBUM")[:8]
    font = _load_spine_font()
    line_gap = max(16, _font_height(font) + 6)
    total_h = len(label) * line_gap
    start_y = (SPINE_HEIGHT - total_h) // 2

    for spine_idx in range(count):
        centre_x = spine_idx * SPINE_COL_W + SPINE_COL_W // 2
        y = start_y
        for ch in label:
            text_w = draw.textlength(ch, font=font)
            draw.text((centre_x - text_w / 2, y), ch, font=font, fill=(235, 235, 235))
            y += line_gap

    return image


def _load_spine_font():
    try:
        return ImageFont.truetype(REGULAR_FONT, 22)
    except Exception:
        pass
    try:
        return ImageFont.load_default(22)
    except TypeError:
        return ImageFont.load_default()


def _font_height(font):
    try:
        ascent, descent = font.getmetrics()
        return ascent + descent
    except Exception:
        return 24
