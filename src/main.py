"""CLI entry point.

Pipeline: clean_photos(input) -> group_photos(photos, albums)
          -> apply_style(group, style_mode, style_strength, ratio, dpi) per group
          -> export_album(album, output, index)
          -> build_preview(output)

All processing happens locally. Photos are never uploaded, and privacy is
protected this version by working on full-image Gaussian-blurred copies
(see cleaner.py).
"""

import argparse
import os
import sys

from cleaner import clean_photos
from exporter import export_album
from grouper import group_photos
from previewer import build_preview
from styler import apply_style

STYLE_CHOICES = ["auto", "modern", "ink_print", "collage", "fashion", "neon"]
STRENGTH_CHOICES = ["mild", "balanced", "strong"]


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Local-first AI photo album generator "
                    "(clean -> group -> style -> export -> preview).")
    parser.add_argument("--input", required=True,
                        help="Folder containing the source photos (jpg/jpeg/png).")
    parser.add_argument("--albums", type=int, default=3,
                        help="Number of albums to produce (default: 3).")
    parser.add_argument("--pages", type=int, default=12,
                        help="Pages per album. Reserved for now: the actual "
                             "page count follows the number of available "
                             "photos (default: 12).")
    parser.add_argument("--ratio", choices=["16:9", "A4"], default="16:9",
                        help="Single page ratio (default: 16:9).")
    parser.add_argument("--dpi", type=int, default=300,
                        help="Output resolution in DPI (default: 300).")
    parser.add_argument("--style-mode", choices=STYLE_CHOICES, default="auto",
                        help="Style mode: auto / modern / ink_print / collage / "
                             "fashion / neon (default: auto).")
    parser.add_argument("--style-strength", choices=STRENGTH_CHOICES,
                        default="balanced",
                        help="Style strength preset: mild / balanced / strong "
                             "(default: balanced).")
    parser.add_argument("--output", default="./output",
                        help="Output folder (default: ./output).")
    return parser.parse_args(argv)


def main(argv=None):
    # Ensure Chinese log output is UTF-8 regardless of the OS console code page.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    args = parse_args(argv)

    output = args.output
    os.makedirs(output, exist_ok=True)

    photos = clean_photos(args.input)
    if not photos:
        print("[warning] 未找到可用照片，跳过画册生成：{}".format(args.input))
        print("[info]    请确认目录内含 .jpg/.jpeg/.png，并满足质量过滤"
              "（亮度/对比度/清晰度）。")
        build_preview(output)  # still produce an (empty) preview page
        print("完成：输出目录 {}（无画册，仅生成 index.html）。"
              .format(os.path.abspath(output)))
        return 0

    print("[1/4] 清洗照片：共 {} 张可用照片（已生成全图模糊副本用于隐私保护）"
          .format(len(photos)))

    groups = group_photos(photos, args.albums)
    print("[2/4] 分组：生成 {} 本画册".format(len(groups)))

    for index, group in enumerate(groups):
        print("[3/4] 风格应用：画册 {}/{} ...".format(index + 1, len(groups)))
        album = apply_style(group, args.style_mode, args.style_strength,
                            args.ratio, args.dpi)
        album_dir = export_album(album, output, index)
        print("      -> {}  |  标题: {} · {}  |  模式: {}  |  页数: {}"
              .format(album_dir, album["title"], album["subtitle"],
                      album["mode"], len(album["pages"])))

    print("[4/4] 生成 HTML 预览 ...")
    build_preview(output)

    preview_file = os.path.join(output, "index.html")
    print("完成！")
    print("  输出目录：{}".format(os.path.abspath(output)))
    print("  预览文件：{}".format(os.path.abspath(preview_file)))
    print("  请在浏览器中打开上面的 index.html。")
    print("说明：所有照片均在本地处理，不会上传，不用于训练，不含密钥。")
    print("隐私：本版本对整张照片应用高斯模糊副本（radius=10）作为隐私保护，"
          "精确的人脸/车牌/门牌识别打码留待后续版本。")
    return 0


if __name__ == "__main__":
    main()
