import os
import urllib.parse


ALT_RENDERING_FORMATS = {
    "pdf": {
        "mimetype": "application/pdf",
        "label": "Download PDF"
    },
    "docx": {
        "mimetype": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "label": "Download DOCX"
    },
    "doc": {
        "mimetype": "application/msword",
        "label": "Download DOC"
    },
    "rtf": {
        "mimetype": "text/rtf",
        "label": "Download RTF"
    },
    "xlsx": {
        "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "label": "Download XLSX"
    },
    "xls": {
        "mimetype": "application/vnd.ms-excel",
        "label": "Download XLS"
    },
    "pptx": {
        "mimetype": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "label": "Download PPTX"
    },
    "ppt": {
        "mimetype": "application/vnd.ms-powerpoint",
        "label": "Download PPT"
    },
    "mp3": {
        "mimetype": "audio/mpeg",
        "label": "Download MP3"
    },
    "mp4": {
        "mimetype": "video/mp4",
        "label": "Download MP4"
    },
    "mov": {
        "mimetype": "video/quicktime",
        "label": "Download MOV"
    },
    "zip": {
        "mimetype": "application/zip",
        "label": "Download ZIP package"
    },
    "txt": {
        "mimetype": "text/plain",
        "label": "Automated Text transcription"
    },
    "csv": {
        "mimetype": "text/csv",
        "label": "Download CSV transcription"
    }
}


def append_manifest_renderings(manifest, file_dir, obj_url_root, metadata):
    manifest_renderings = []
    original_file = metadata.get("original_file_legacy", None)
    content_txt = os.path.join(os.path.dirname(file_dir), "content.txt")

    if os.path.isfile(content_txt):
        manifest_renderings.append({
            "id": f"{obj_url_root}/content.txt",
            "type": "Text",
            "format": "text/plain",
            "label": "Automated Text transcription"
        })

    for format_ext in ALT_RENDERING_FORMATS.keys():
        rendering_format = os.path.join(os.path.dirname(file_dir), format_ext)
        if not os.path.isdir(rendering_format):
            continue

        rendering_files = []
        dir_contents = os.listdir(rendering_format)
        if len(dir_contents) > 0 and (len(dir_contents) == 1 or "file_sets" not in metadata.keys()):
            rendering_files = [dir_contents[0]]
        else:
            for file_set in metadata["file_sets"].values():
                if file_set.lower().endswith(format_ext):
                    rendering_files.append(file_set)

        for rendering_file in rendering_files:
            rendering_filepath = os.path.join(rendering_format, rendering_file)
            if not os.path.isfile(rendering_filepath):
                continue

            if rendering_file == original_file:
                if not os.path.splitext(original_file)[1].lower() == ".pdf":
                    alt_label = f"{rendering_file} (Original)"
                else:
                    alt_label = f"{rendering_file}"
            elif format_ext == "txt":
                if os.path.isfile(content_txt):
                    continue
                alt_label = ALT_RENDERING_FORMATS[format_ext]["label"]
            else:
                alt_label = rendering_file

            manifest_renderings.append({
                "id": f"{obj_url_root}/{format_ext}/{urllib.parse.quote(os.path.basename(rendering_file))}",
                "type": "Text",
                "format": ALT_RENDERING_FORMATS[format_ext]["mimetype"],
                "label": alt_label
            })

    if manifest_renderings:
        manifest.rendering = manifest_renderings
