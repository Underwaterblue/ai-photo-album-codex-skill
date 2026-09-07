"""Generate a local ``index.html`` that previews all exported albums.

The page has two sections:

  * a spine-wall area - every album's spine_wall.png laid out horizontally
  * per-album cards   - cover thumbnail (links to the PDF) + download link

All assets are referenced with relative paths so the page can be opened
straight from the file system (no server needed).
"""

import html
import os


def build_preview(output_dir):
    """Scan ``output_dir`` for album_* folders and write index.html."""
    os.makedirs(output_dir, exist_ok=True)

    albums = []
    for name in sorted(os.listdir(output_dir)):
        album_dir = os.path.join(output_dir, name)
        if not (name.startswith("album_") and os.path.isdir(album_dir)):
            continue
        albums.append({
            "name": name,
            "cover": os.path.join(name, "cover.png"),
            "spine": os.path.join(name, "spine_wall.png"),
            "pdf": os.path.join(name, "album.pdf"),
            "has_spine": os.path.exists(os.path.join(album_dir, "spine_wall.png")),
            "has_pdf": os.path.exists(os.path.join(album_dir, "album.pdf")),
            "pages": _count_pages(album_dir),
        })

    page = _render(albums)
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as handle:
        handle.write(page)


def _count_pages(album_dir):
    count = 0
    for name in os.listdir(album_dir):
        if name.startswith("page_") and name.endswith(".png"):
            count += 1
    return count


def _render(albums):
    if not albums:
        albums_html = ('<section class="empty"><h2>没有可预览的画册</h2>'
                       '<p>请先在输入目录放入照片并运行主程序。'
                       '（提示：本工具不包含任何照片数据。）</p></section>')
    else:
        spine_items = []
        cards = []
        for album in albums:
            safe_name = html.escape(album["name"])
            if album["has_spine"]:
                spine_items.append(
                    '<figure class="spine">'
                    '<img src="{src}" alt="{name} 书脊墙">'
                    '<figcaption>{name} &middot; {pages} 页</figcaption>'
                    "</figure>".format(src=album["spine"], name=safe_name,
                                       pages=album["pages"]))

            pdf_block = ""
            if album["has_pdf"]:
                pdf_block = (
                    '<p class="meta">下载：<a class="download" href="{pdf}" '
                    'download="album.pdf">album.pdf</a></p>'
                ).format(pdf=album["pdf"])
            cards.append(
                '<article class="album">'
                '<h2>{name}</h2>'
                '<a href="{pdf}"><img class="cover" src="{cover}" '
                'alt="{name} 封面"></a>'
                '<p class="meta">{pages} 个跨页</p>'
                '{pdf_block}'
                "</article>".format(name=safe_name, pdf=album["pdf"],
                                    cover=album["cover"], pages=album["pages"],
                                    pdf_block=pdf_block))

        albums_html = (
            '<section id="spines"><h2>书脊墙</h2>'
            '<div class="spine-row">{spines}</div></section>'
            '<section id="albums"><h2>画册</h2>'
            '<div class="album-grid">{cards}</div></section>'
        ).format(spines="".join(spine_items), cards="".join(cards))

    return """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Photo Album · 本地预览</title>
<style>
  :root {{ color-scheme: dark; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: #0f0f0f; color: #ededed;
         font: 15px/1.6 system-ui, "Segoe UI", "PingFang SC",
              "Microsoft YaHei", sans-serif; }}
  header, main, footer {{ padding: 0 32px; }}
  header {{ border-bottom: 1px solid #262626; padding: 24px 32px; }}
  header h1 {{ margin: 0; font-size: 22px; }}
  header p {{ margin: 4px 0 0; color: #9a9a9a; font-size: 13px; }}
  section {{ padding-top: 16px; }}
  h2 {{ font-size: 16px; color: #bbb; letter-spacing: 0.05em; }}
  a {{ color: #8ab8ff; }}
  .spine-row {{ display: flex; gap: 28px; flex-wrap: wrap; align-items: flex-end; }}
  .spine {{ margin: 0; }}
  .spine img {{ display: block; height: 400px; width: auto; background: #000;
               border: 1px solid #2a2a2a; }}
  .spine figcaption {{ margin-top: 6px; text-align: center;
                       font-size: 12px; color: #9a9a9a; }}
  .album-grid {{ display: grid; gap: 28px; margin-bottom: 32px;
                grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); }}
  .album {{ padding: 16px; background: #161616; border: 1px solid #262626; }}
  .album h2 {{ margin: 0 0 10px; color: #ededed; font-size: 15px; }}
  .album .cover {{ display: block; width: 100%; height: auto;
                   border: 1px solid #2a2a2a; background: #000; }}
  .meta {{ color: #9a9a9a; font-size: 13px; margin: 8px 0 0; }}
  .download {{ font-weight: 600; }}
  .empty {{ color: #8a8a8a; padding-bottom: 32px; }}
  footer {{ border-top: 1px solid #262626; padding: 18px 32px; color: #777;
            font-size: 12px; }}
</style>
</head>
<body>
<header>
  <h1>AI Photo Album</h1>
  <p>本地生成的画册预览 · 照片全程在本地处理，不包含任何原始用户照片数据</p>
</header>
<main>
{albums_html}
</main>
<footer>仅用于本地预览。若需发布，请先确认其中不含可识别的个人或敏感信息。</footer>
</body>
</html>
""".format(albums_html=albums_html)
