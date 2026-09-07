"""Simple photo grouping + album title generation.

Grouping is intentionally naive: photos are first sorted by modification
time / file name (so photos from the same moment or with similar names tend
to land in the same album) and then split evenly. No clustering, no EXIF
parsing and no external models — keep it simple and predictable.
"""

import os
import random

_SUBTITLE = "主题画册"


def group_photos(photos, num_albums):
    """Split ``photos`` into at most ``num_albums`` non-empty groups.

    Photos are sorted by (modification time, file name) first, then split as
    evenly as possible. When there are fewer photos than requested albums we
    emit one-photo groups, so every returned group has at least one photo.
    Empty input returns [].
    """
    photos = list(photos)
    if not photos:
        return []

    photos = sorted(photos, key=_sort_key)
    num_albums = max(1, int(num_albums))
    base, remainder = divmod(len(photos), num_albums)

    groups = []
    cursor = 0
    for k in range(min(num_albums, len(photos))):
        size = base + (1 if k < remainder else 0)
        if size <= 0:
            break
        groups.append(photos[cursor:cursor + size])
        cursor += size
    return groups


def _sort_key(path):
    """Sort by modification time first, then by file name."""
    try:
        mtime = os.path.getmtime(path)
    except OSError:
        mtime = 0.0
    return (mtime, os.path.basename(path))


def generate_title(group):
    """Return {"title": "ALBUM <random 3-digit>", "subtitle": "主题画册"}."""
    return {
        "title": "ALBUM {}".format(random.randint(100, 999)),
        "subtitle": _SUBTITLE,
    }
