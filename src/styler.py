"""Style application: turn one group of photo paths into an album object.

Album object keys
-----------------
    title, subtitle : strings
    mode            : the resolved style mode (== requested, except for "auto")
    strength        : the style-strength preset ("mild"/"balanced"/"strong")
                      or a numeric value passed to the API
    dpi, ratio      : values applied at export time
    pages           : list of PIL Images, each a two-page cross-page spread
    cover           : PIL Image (single page)

The style ``mode`` only changes the spread background colour and the cover
accent colour. ``strength`` only scales the per-page adjustments
(contrast / colour enhancement) according to the table in
``_contrast_color_factors``. No further filters, no models, no network.

Privacy note: photos passed to this module are already blurred full-image
copies produced by ``cleaner.clean_photos`` (this version's privacy
protection). Exact face / plate / door redaction is deferred; see the TODO
in ``cleaner.py``.
"""

import os

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageStat

from grouper import generate_title

# Single-page pixel dimensions per ratio.
PAGE_SIZES = {
    "16:9": (1920, 1080),
    "A4": (2480, 3508),
}

# Cross-page spread background colour per style mode.
MODE_BACKGROUND = {
    "modern": (0xF8, 0xF8, 0xF8),
    "ink_print": (0xF0, 0xEB, 0xE4),
    "collage": (0xEA, 0xE6, 0xE2),
    "fashion": (0xFA, 0xF8, 0xF5),
    "neon": (0x0A, 0x0A, 0x0A),
}
DEFAULT_BACKGROUND = (0xF5, 0xF5, 0xF5)

# Cover accent colour per style mode (subtitle colour on the dark cover).
MODE_ACCENT = {
    "modern": (150, 180, 255),
    "ink_print": (205, 175, 125),
    "collage": (255, 130, 95),
    "fashion": (235, 190, 170),
    "neon": (125, 255, 125),
}
DEFAULT_ACCENT = (220, 220, 220)

# Named style-strength presets: (contrast factor, colour factor).
_STRENGTH_PRESETS = {
    "mild": (1 + 0.2, 1 - 0.1),
    "balanced": (1 + 0.4, 1 - 0.25),
    "strong": (1 + 0.6, 1 - 0.4),
}

# Fonts are optional: a missing font falls back to the PIL default font so the
# program never crashes on font problems. Point these at assets/fonts.
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(_BASE_DIR, "assets", "fonts")
REGULAR_FONT = os.path.join(FONT_DIR, "NotoSansSC-Regular.ttf")
BOLD_FONT = os.path.join(FONT_DIR, "NotoSansSC-Bold.ttf")


def apply_style(group, mode, strength, ratio, dpi):
    """Build an album object (dict) from a list of photo paths.

    ``strength`` may be a preset string ("mild" / "balanced" / "strong") or a
    numeric value, in which case contrast = 1 + value*0.6 and
    colour = 1 - value*0.3.
    """
    if ratio not in PAGE_SIZES:
        ratio = "16:9"
    page_w, page_h = PAGE_SIZES[ratio]

    resolved_mode = _resolve_mode(group, mode)
    bg = MODE_BACKGROUND.get(resolved_mode, DEFAULT_BACKGROUND)
    text_color = _text_color_for(bg)
    accent = MODE_ACCENT.get(resolved_mode, DEFAULT_ACCENT)

    contrast_factor, colour_factor = _contrast_color_factors(strength)

    info = generate_title(group)
    title, subtitle = info["title"], info["subtitle"]

    pages = []
    for idx, photo_path in enumerate(group):
        try:
            pages.append(_make_spread(photo_path, page_w, page_h,
                                      bg, text_color, contrast_factor,
                                      colour_factor, idx))
        except Exception:
            # A single failing photo must not kill the whole album:
            # fall back to a marked placeholder spread.
            pages.append(_placeholder_spread(page_w, page_h, bg, text_color, idx))

    cover = _make_cover(page_w, page_h, title, subtitle, accent)

    return {
        "title": title,
        "subtitle": subtitle,
        "mode": resolved_mode,  # the requested mode, or the auto-resolved one
        "strength": strength,
        "ratio": ratio,
        "dpi": int(dpi),
        "pages": pages,
        "cover": cover,
    }


def _resolve_mode(group, requested):
    """Return the concrete style mode for this group."""
    if requested != "auto":
        return requested
    return _detect_style(group)


def _detect_style(group):
    """Auto mode: pick a style from the whole group's brightness / contrast /
    saturation.

    # Auto 判定规则（保留说明）：
    # 计算所有照片的平均亮度（灰度均值）、平均对比度（灰度标准差）和平均饱和度。
    #   平均亮度 < 0.3                        -> neon
    #   平均亮度 > 0.7 且平均对比度 > 0.3       -> modern
    #   平均饱和度 > 0.5                       -> fashion
    #   否则                                   -> ink_print
    """
    brightnesses, contrasts, saturations = [], [], []
    for path in group:
        try:
            with Image.open(path) as im:
                small = im.convert("RGB")
                small.thumbnail((64, 64))
                gray = small.convert("L")
                gstat = ImageStat.Stat(gray)
                brightnesses.append(gstat.mean[0] / 255.0)
                contrasts.append(gstat.stddev[0] / 255.0)
                _, sat, _ = small.convert("HSV").split()
                saturations.append(ImageStat.Stat(sat).mean[0] / 255.0)
        except Exception:
            continue

    if not brightnesses:
        return "modern"

    avg_brightness = sum(brightnesses) / len(brightnesses)
    avg_contrast = sum(contrasts) / len(contrasts)
    avg_saturation = sum(saturations) / len(saturations)

    if avg_brightness < 0.3:
        return "neon"
    if avg_brightness > 0.7 and avg_contrast > 0.3:
        return "modern"
    if avg_saturation > 0.5:
        return "fashion"
    return "ink_print"


def _contrast_color_factors(strength):
    """Map a strength preset / number to (contrast factor, colour factor)."""
    if isinstance(strength, str):
        key = strength.lower()
        contrast, colour = _STRENGTH_PRESETS.get(key, _STRENGTH_PRESETS["balanced"])
    else:
        value = float(strength)
        contrast = 1.0 + value * 0.6
        colour = 1.0 - value * 0.3
    return contrast, max(0.0, colour)


def _text_color_for(bg):
    """Return text colour that contrasts with the given background."""
    luminance = (bg[0] + bg[1] + bg[2]) / 3.0
    return (35, 35, 35) if luminance > 140 else (240, 240, 240)


def _make_spread(path, w, h, bg, text_color, contrast_factor, colour_factor, idx):
    """Build one cross-page spread (width w*2) from a single photo."""
    canvas = Image.new("RGB", (w * 2, h), color=bg)

    with Image.open(path) as opened:
        photo = opened.convert("RGB")

    # Apply the contrast/colour adjustments driven by ``strength``.
    photo = ImageEnhance.Contrast(photo).enhance(contrast_factor)
    photo = ImageEnhance.Color(photo).enhance(colour_factor)

    # Fit the photo inside the *left page*, keeping its aspect ratio and a
    # small margin. The right page stays empty as the text area.
    box_w = int(w * 0.92)
    box_h = int(h * 0.90)
    scale = min(box_w / photo.width, box_h / photo.height)
    new_w = max(1, int(photo.width * scale))
    new_h = max(1, int(photo.height * scale))
    photo = photo.resize((new_w, new_h), Image.LANCZOS)

    left = (w - new_w) // 2
    top = (h - new_h) // 2
    canvas.paste(photo, (left, top))

    _draw_page_number(canvas, w, h, text_color, idx)
    return canvas


def _draw_page_number(canvas, w, h, text_color, idx):
    """Draw 'PAGE n' at the bottom-right of the (right page) text area."""
    draw = ImageDraw.Draw(canvas)
    label = "PAGE {}".format(idx + 1)
    font_size = max(18, min(80, int(min(w, h) * 0.035)))
    font = _load_font(REGULAR_FONT, font_size)
    text_w = draw.textlength(label, font=font)
    margin = int(w * 0.05)
    x = 2 * w - margin - text_w
    y = h - margin - font_size
    draw.text((x, y), label, font=font, fill=text_color)


def _placeholder_spread(w, h, bg, text_color, idx):
    """A marked placeholder used when one photo could not be processed."""
    canvas = Image.new("RGB", (w * 2, h), color=bg)
    draw = ImageDraw.Draw(canvas)
    message = "IMAGE UNAVAILABLE"
    font_size = max(18, int(h * 0.05))
    font = _load_font(REGULAR_FONT, font_size)
    text_w = draw.textlength(message, font=font)
    draw.text(((2 * w - text_w) / 2, h / 2 - font_size / 2),
              message, font=font, fill=text_color)
    return canvas


def _make_cover(w, h, title, subtitle, accent):
    """Generate the cover: dark background, title centred, subtitle below."""
    cover = Image.new("RGB", (w, h), color=(10, 10, 10))
    draw = ImageDraw.Draw(cover)

    max_w = int(w * 0.86)
    title_font_size = max(24, int(min(w, h) * 0.085))
    sub_font_size = max(18, int(title_font_size * 0.38))

    title_font = _load_font(BOLD_FONT, title_font_size)
    title_lines = _wrap_text(draw, title, title_font, max_w)
    line_gap = int(title_font_size * 1.15)
    block_h = max(1, len(title_lines)) * line_gap
    y = int(h * 0.46) - block_h // 2

    for line in title_lines:
        text_w = draw.textlength(line, font=title_font)
        draw.text(((w - text_w) / 2, y), line, font=title_font, fill=(245, 245, 245))
        y += line_gap

    sub_font = _load_font(REGULAR_FONT, sub_font_size)
    sub_lines = _wrap_text(draw, subtitle, sub_font, max_w)
    y += int(title_font_size * 0.45)
    for line in sub_lines:
        text_w = draw.textlength(line, font=sub_font)
        draw.text(((w - text_w) / 2, y), line, font=sub_font, fill=accent)
        y += int(sub_font_size * 1.4)

    return cover


def _wrap_text(draw, text, font, max_w):
    """Split ``text`` into lines that fit within ``max_w`` pixels."""
    lines = []
    for paragraph in str(text).split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        line = ""
        for word in words:
            candidate = (line + " " + word).strip()
            if draw.textlength(candidate, font=font) <= max_w or not line:
                line = candidate
            else:
                lines.append(line)
                # Very long single word: break by characters.
                buffer = ""
                for ch in word:
                    if draw.textlength(buffer + ch, font=font) <= max_w:
                        buffer += ch
                    else:
                        lines.append(buffer)
                        buffer = ch
                line = buffer
        if line:
            lines.append(line)
    return lines or [str(text)]


def _load_font(path, size):
    """Load a TrueType font, falling back to the PIL default font."""
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        pass
    try:
        # Pillow >= 10.1 can scale the bundled default font.
        return ImageFont.load_default(size)
    except TypeError:
        return ImageFont.load_default()
