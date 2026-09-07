"""Photo cleaning + privacy blur (local-only).

clean_photos() scans a folder, keeps the photos that pass a quality filter
(brightness / contrast / sharpness) and de-duplicates by file name. Then, as
this version's privacy protection, it writes a **full-image Gaussian-blurred
copy (radius 10)** of every accepted photo into ``./temp_blurred/`` and
returns those blurred temp paths. Every later stage works on the blurred
copies; the original files are never modified and never used downstream.

Future work (see TODO below): replace the blanket blur with precise
detection + redaction of faces / license plates / door plates so the rest of
an image can stay sharp. Original files are never uploaded anywhere and this
code contains no network calls.
"""

import os

from PIL import Image, ImageFilter, ImageStat

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

# Privacy-blur working directory, relative to the process working directory.
TEMP_BLURRED_DIR = "temp_blurred"
BLUR_RADIUS = 10  # this version's full-image privacy protection

# Quality thresholds, normalised to 0..1 on a small greyscale copy.
MIN_BRIGHTNESS = 0.15
MAX_BRIGHTNESS = 0.85
MIN_CONTRAST_STD = 0.12
# Variance of the FIND_EDGES result below which an image is considered blurry.
# Kept conservative so real photos are not over-filtered; tune if needed.
BLUR_VAR_THRESHOLD = 100.0


def clean_photos(folder):
    """Return blurred temp-file paths for the valid photos under ``folder``.

    # TODO: 未来可替换为精确的人脸/车牌/门牌识别打码。
    # 本版本使用全图高斯模糊（radius=10）作为隐私保护占位：
    # 原图保持不动，仅把模糊副本交给后续流程使用。
    """
    if not folder or not os.path.isdir(folder):
        return []

    os.makedirs(TEMP_BLURRED_DIR, exist_ok=True)
    valid_blurred = []
    seen_names = set()

    for root, dirs, files in os.walk(folder):
        # Do not descend into hidden directories.
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for name in sorted(files):
            ext = os.path.splitext(name)[1].lower()
            if ext not in SUPPORTED_EXTENSIONS:
                continue

            key = name.lower()
            if key in seen_names:
                continue  # simple de-duplication by file name

            source = os.path.join(root, name)
            if not _passes_quality_filter(source):
                continue

            seen_names.add(key)
            blurred_path = _write_blurred_copy(source)
            if blurred_path:
                valid_blurred.append(blurred_path)

    return valid_blurred


def _passes_quality_filter(path):
    """Return True when brightness/contrast/sharpness all look acceptable."""
    try:
        with Image.open(path) as im:
            im.load()
            gray = im.convert("L")
            gray.thumbnail((160, 160))
            stat = ImageStat.Stat(gray)
    except Exception:
        # Unreadable / corrupt image -> treat as invalid and move on.
        return False

    mean = stat.mean[0] / 255.0
    std = stat.stddev[0] / 255.0

    if not (MIN_BRIGHTNESS <= mean <= MAX_BRIGHTNESS):
        return False  # too dark or too bright
    if std <= MIN_CONTRAST_STD:
        return False  # too flat / low contrast

    edges = gray.filter(ImageFilter.FIND_EDGES)
    edge_var = ImageStat.Stat(edges).var[0]
    if edge_var < BLUR_VAR_THRESHOLD:
        return False  # too blurry (no detectable edges)

    return True


def _write_blurred_copy(source):
    """Save a GaussianBlur copy of ``source`` into ./temp_blurred/.

    Returns the path of the blurred copy, or None on failure. File names are
    unique within a run because clean_photos() de-duplicates by base name.
    """
    try:
        with Image.open(source) as im:
            rgb = im.convert("RGB")
            blurred = rgb.filter(ImageFilter.GaussianBlur(radius=BLUR_RADIUS))
            stem = os.path.splitext(os.path.basename(source))[0]
            target = os.path.join(TEMP_BLURRED_DIR, "{0}.png".format(stem))
            blurred.save(target, "PNG")
            return target
    except Exception:
        return None
