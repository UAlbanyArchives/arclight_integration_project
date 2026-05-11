import os
import yaml


def attach_search_service_if_configured(manifest, file_dir, manifest_url_root, obj_url_root, lang_code, config_path):
    hocr_dir = os.path.join(os.path.dirname(file_dir), "hocr")
    if not (os.path.isdir(hocr_dir) and os.listdir(hocr_dir)):
        return

    try:
        if config_path.startswith("~"):
            config_path = os.path.expanduser(config_path)
        with open(config_path, "r") as config_file:
            loaded_config = yaml.safe_load(config_file)

        content_search_url = loaded_config.get("content_search_url")
        if not content_search_url:
            return

        path_parts = obj_url_root.split("/")
        if len(path_parts) >= 2:
            manifest.service = [{
                "id": f"{content_search_url}{obj_url_root.removeprefix(manifest_url_root)}",
                "type": "SearchService",
                "label": {lang_code: ["Content Search"]},
                "profile": "http://iiif.io/api/search/1/search"
            }]
    except Exception as e:
        print(f"Warning: Could not add content search service: {e}")
