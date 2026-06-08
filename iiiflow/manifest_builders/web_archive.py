import json
import os
import urllib.parse
import zipfile
from iiif_prezi3 import Annotation, AnnotationPage

HTML_MIME_TYPES = ("text/html", "application/xhtml", "application/xhtml+xml")


def _normalize_page_url(url):
    return (url or "").strip().rstrip("/")


def _is_supported_page_url(url):
    normalized = (url or "").strip().lower()
    return normalized.startswith("http") or normalized.startswith("mailto:")


def _read_warc_pages(warc_path):
    """Extract HTML pages from a WARC or WARC.gz file, mimicking py-wacz --detect-pages logic."""
    from warcio.archiveiterator import ArchiveIterator

    pages = []
    # warcio handles both plain and gzip-compressed WARCs automatically from a raw binary stream
    with open(warc_path, "rb") as stream:
        for record in ArchiveIterator(stream):
            if record.rec_type != "response":
                continue
            url = record.rec_headers.get_header("WARC-Target-URI")
            if not _is_supported_page_url(url):
                continue
            # Skip non-2xx responses
            if record.http_headers:
                status = record.http_headers.get_statuscode()
                if not status.startswith("2"):
                    continue
            # Only HTML content types
            if record.http_headers:
                content_type = record.http_headers.get_header("Content-Type") or ""
            else:
                content_type = record.rec_headers.get_header("Content-Type") or ""
            mime = content_type.split(";")[0].strip()
            if mime not in HTML_MIME_TYPES:
                continue
            ts = record.rec_headers.get_header("WARC-Date", "")
            pages.append({"url": url, "ts": ts, "title": url})
    return pages


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


def _build_page_replay_url(obj_url_root, archive_subdir, archive_filename, page_url, page_ts):
    """Construct a per-page ReplayWeb.page URL for a given archived page."""
    source_url = f"{obj_url_root}/{archive_subdir}/{urllib.parse.quote(archive_filename)}"
    # Convert ISO timestamp to compact form: 2025-01-27T16:03:37.104Z -> 20250127160337
    ts_compact = page_ts.replace("-", "").replace("T", "").replace(":", "")[:14]

    # ReplayWeb handles non-http captures (e.g. mailto:) more reliably via resources mode.
    parsed_scheme = urllib.parse.urlparse(page_url).scheme.lower()
    if parsed_scheme and parsed_scheme not in {"http", "https"}:
        capture_url = page_url
        fragment = (
            f"view=resources&urlSearchType=prefix&url={urllib.parse.quote(capture_url, safe='')}"
        )
        if ts_compact:
            fragment += f"&ts={ts_compact}"
    else:
        fragment = f"view=replay&url={urllib.parse.quote(page_url, safe='')}&ts={ts_compact}"

    return f"https://replayweb.page/?source={urllib.parse.quote(source_url, safe='')}#{fragment}"


def _apply_replay_url_filter(pages, metadata):
    """Filter pages by metadata replay_url if set (single string or list)."""
    replay_url = metadata.get("replay_url")
    target_page_urls = []
    if replay_url:
        if isinstance(replay_url, list):
            target_page_urls = [_normalize_page_url(url) for url in replay_url if url]
        else:
            normalized = _normalize_page_url(replay_url)
            if normalized:
                target_page_urls = [normalized]
    if target_page_urls:
        pages = [page for page in pages if _normalize_page_url(page.get("url")) in target_page_urls]
    return pages


def _build_canvases(manifest, pages, obj_url_root, archive_subdir, archive_filename, thumbnail_data, lang_code):
    """Add one IIIF canvas per page to the manifest."""
    for page_count, page in enumerate(pages, start=1):
        page_url = page.get("url", "")
        page_title = page.get("title") or page_url
        page_ts = page.get("ts", "")

        replay_url = _build_page_replay_url(obj_url_root, archive_subdir, archive_filename, page_url, page_ts)

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


def create_web_archive_canvases(manifest, file_dir, obj_url_root, thumbnail_data, lang_code, metadata):
    """Create one IIIF canvas per page found in a WACZ or WARC/WARC.gz web archive.
    
    file_dir is the archive subdirectory (wacz/ or warc.gz/) as resolved by resolve_resource_source.
    """
    dir_name = os.path.basename(file_dir)

    if dir_name == "wacz":
        wacz_files = [f for f in os.listdir(file_dir) if f.lower().endswith(".wacz")]
        if wacz_files:
            wacz_filename = wacz_files[0]
            wacz_path = os.path.join(file_dir, wacz_filename)
            pages = _read_wacz_pages(wacz_path)
            pages = _apply_replay_url_filter(pages, metadata)
            _build_canvases(manifest, pages, obj_url_root, "wacz", wacz_filename, thumbnail_data, lang_code)

    elif dir_name == "warc.gz":
        warc_files = [f for f in os.listdir(file_dir) if f.lower().endswith(".warc") or f.lower().endswith(".warc.gz")]
        if warc_files:
            warc_filename = warc_files[0]
            warc_path = os.path.join(file_dir, warc_filename)
            pages = _read_warc_pages(warc_path)
            pages = _apply_replay_url_filter(pages, metadata)
            _build_canvases(manifest, pages, obj_url_root, "warc.gz", warc_filename, thumbnail_data, lang_code)


# Backward compatibility wrapper
def create_wacz_canvases(manifest, file_dir, obj_url_root, thumbnail_data, lang_code, metadata):
    """Deprecated: use create_web_archive_canvases instead."""
    return create_web_archive_canvases(manifest, file_dir, obj_url_root, thumbnail_data, lang_code, metadata)
