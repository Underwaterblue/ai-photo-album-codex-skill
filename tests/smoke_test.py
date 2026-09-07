"""Smoke test for the full pipeline.

No real photos are needed: 200x200 gradient images (RGB(50,50,50) ->
RGB(200,200,200)) with added random noise are generated with Pillow so they
pass the quality filter. Runs clean_photos -> group_photos -> apply_style ->
export_album -> build_preview and verifies the produced files.

Run from anywhere:

    python tests/smoke_test.py     # prints "Smoke test passed"
"""

import os
import random
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from PIL import Image

from cleaner import clean_photos
from exporter import export_album
from grouper import group_photos
from previewer import build_preview
from styler import apply_style


def _make_placeholder_photo(path, seed):
    """200x200 gradient RGB(50,50,50)->RGB(200,200,200) + random noise."""
    size = 200
    rng = random.Random(seed)
    image = Image.new("RGB", (size, size))
    px = image.load()
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2.0 * (size - 1))          # diagonal 0..1
            base = 50 + int(150 * t)                  # 50 .. 200
            r = base + rng.randint(-40, 40)
            g = base + rng.randint(-40, 40)
            b = base + rng.randint(-40, 40)
            px[x, y] = (max(0, min(255, r)),
                        max(0, min(255, g)),
                        max(0, min(255, b)))
    image.save(path, "PNG")


def main():
    tmp_dir = tempfile.mkdtemp(prefix="ai_photo_album_smoke_")
    cwd = os.getcwd()
    try:
        os.chdir(tmp_dir)  # temp_blurred/ is created relative to the CWD
        photo_dir = os.path.join(tmp_dir, "photos")
        os.makedirs(photo_dir)

        expected = []
        for i in range(4):
            path = os.path.join(photo_dir, "photo_{0:02d}.png".format(i))
            _make_placeholder_photo(path, seed=1000 + i)
            expected.append(path)

        photos = clean_photos(photo_dir)
        assert photos, "clean_photos() returned no photos"
        assert len(photos) == len(expected), (
            "expected {} valid photos, got {}".format(len(expected), len(photos)))
        for blurred in photos:
            assert os.path.isfile(blurred), "blurred copy missing: {}".format(blurred)

        groups = group_photos(photos, 2)
        assert groups, "group_photos() returned no groups"
        assert all(g for g in groups), "group_photos() returned an empty group"

        out_dir = os.path.join(tmp_dir, "output")
        exported = 0
        for index, group in enumerate(groups):
            album = apply_style(group, "auto", "balanced", "16:9", 150)
            export_album(album, out_dir, index)
            exported += 1

        build_preview(out_dir)

        assert os.path.exists(os.path.join(out_dir, "index.html")), \
            "index.html was not created"

        album_dirs = [name for name in os.listdir(out_dir)
                      if name.startswith("album_")]
        assert len(album_dirs) == exported, \
            "expected {} album dirs, got {}".format(exported, len(album_dirs))

        for name in album_dirs:
            album_dir = os.path.join(out_dir, name)
            for filename in ("cover.png", "spine_wall.png"):
                assert os.path.exists(os.path.join(album_dir, filename)), \
                    "{} missing in {}".format(filename, name)
            pages = [f for f in os.listdir(album_dir)
                     if f.startswith("page_") and f.endswith(".png")]
            assert pages, "no page_*.png images in {}".format(name)
            assert os.path.exists(os.path.join(album_dir, "album.pdf")), \
                "album.pdf missing in {}".format(name)

        print("Smoke test passed")
    finally:
        os.chdir(cwd)
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
