import json
import os
import urllib.parse
import zipfile
from iiif_prezi3 import Annotation, AnnotationPage


def _normalize_page_url(url):
    return (url or "").strip().rstrip("/")


def _read_wacz_pages(wacz_path):
    """Extract pages from pages/pages.jsonl inside a WACZ file, skipping the header line."""
    pages = []
    with zipfile.ZipFile(wacz_path, "r") as zf:
        if "pages/pages.jsonl" not in zf.namelist():
            return pages
        content = zf.read("pages/pages.jsonl").decode("utf-8")
        for line in content.strip().splitlines():
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            # Skip the format descriptor header line (has 'format' key but no 'url')
            if not entry.get("url"):
                continue
            pages.append(entry)
    return pages


def _build_page_replay_url(obj_url_root, wacz_filename, page_url, page_ts):
    """Construct a per-page ReplayWeb.page URL for a given archived page."""
    wacz_source_url = f"{obj_url_root}/wacz/{urllib.parse.quote(wacz_filename)}"
    # Convert ISO timestamp to compact form: 2025-01-27T16:03:37.104Z -> 20250127160337
    ts_compact = page_ts.replace("-", "").replace("T", "").replace(":", "")[:14]
    fragment = f"view=replay&url={urllib.parse.quote(page_url, safe='')}&ts={ts_compact}"
    return f"https://replayweb.page/?source={urllib.parse.quote(wacz_source_url, safe='')}#{fragment}"


def create_wacz_canvases(manifest, wacz_dir, obj_url_root, thumbnail_data, lang_code, metadata):
    """Create one IIIF canvas per page found in the WACZ web archive."""
    wacz_files = [f for f in os.listdir(wacz_dir) if f.lower().endswith(".wacz")]
    if not wacz_files:
        return

    wacz_filename = wacz_files[0]
    wacz_path = os.path.join(wacz_dir, wacz_filename)
    pages = _read_wacz_pages(wacz_path)
    target_page_url = _normalize_page_url(metadata.get("replay_url"))

    if target_page_url:
        pages = [page for page in pages if _normalize_page_url(page.get("url")) == target_page_url]

    for page_count, page in enumerate(pages, start=1):
        page_url = page.get("url", "")
        page_title = page.get("title") or page_url
        page_ts = page.get("ts", "")

        replay_url = _build_page_replay_url(obj_url_root, wacz_filename, page_url, page_ts)

        canvas = manifest.make_canvas(
            id=f"{obj_url_root}/canvas/p{page_count}",
            label={lang_code: [page_title]},
        )

        anno_page = AnnotationPage(id=f"{obj_url_root}/canvas/p{page_count}/page")
        annotation = Annotation(
            id=f"{obj_url_root}/canvas/p{page_count}/page/annotation",
            motivation="painting",
            body={
                "id": replay_url,
                "type": "Text",
                "format": "text/html",
            },
            target=f"{obj_url_root}/canvas/p{page_count}",
        )
        anno_page.items.append(annotation)
        canvas.items.append(anno_page)

        if page_count == 1 and "url" in thumbnail_data:
            thumbnail_width = thumbnail_data.get("width")
            thumbnail_height = thumbnail_data.get("height")
            thumbnail = {
                "id": thumbnail_data["url"],
                "type": "Image",
                "format": "image/jpeg",
            }
            if thumbnail_width and thumbnail_height:
                thumbnail["width"] = thumbnail_width
                thumbnail["height"] = thumbnail_height
            canvas.thumbnail = [thumbnail]
