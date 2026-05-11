import os
import json
import filecmp
import difflib
import yaml
from iiiflow import create_manifest
from test_utils import load_config, iterate_collections_and_objects, create_temp_fixture_config

config_path = "./.iiiflow.yml"
discovery_storage_root, log_file_path = load_config(config_path)


def _generate_manifest(tmp_path, collection_id, object_id, config_overrides=None):
    """Generate a manifest for one fixture object in an isolated temp copy and return parsed JSON."""
    temp_discovery_storage_root, temp_config_path = create_temp_fixture_config(tmp_path, config_path)

    if config_overrides:
        with open(temp_config_path, "r", encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file) or {}
        for key, value in config_overrides.items():
            if value is None:
                config.pop(key, None)
            else:
                config[key] = value
        with open(temp_config_path, "w", encoding="utf-8") as config_file:
            yaml.safe_dump(config, config_file, sort_keys=False)

    object_path = os.path.join(temp_discovery_storage_root, collection_id, object_id)
    manifest_path = os.path.join(object_path, "manifest.json")
    if os.path.isfile(manifest_path):
        os.remove(manifest_path)

    create_manifest(collection_id, object_id, config_path=temp_config_path)

    assert os.path.isfile(manifest_path), f"manifest.json was not created for {collection_id}/{object_id}"
    assert os.path.getsize(manifest_path) > 0, f"Generated manifest is empty for {collection_id}/{object_id}"

    with open(manifest_path, "r", encoding="utf-8") as manifest_file:
        return json.load(manifest_file)


def test_manifest(tmp_path):
    # Test creation of manifest.json against canonical fixture manifests.

    temp_discovery_storage_root, temp_config_path = create_temp_fixture_config(tmp_path, config_path)

    def test_action(collection_id, object_id, object_path):
        canonical_manifest_path = os.path.join(discovery_storage_root, collection_id, object_id, "manifest.json")
        manifest_path = os.path.join(object_path, "manifest.json")
        source_folders = ["ptif", "jpg", "ogg", "mp3", "webm"]

        assert os.path.isfile(canonical_manifest_path), f"Fixture manifest missing: {canonical_manifest_path}"

        if not any(os.path.isdir(os.path.join(object_path, folder)) for folder in source_folders):
            return

        if os.path.isfile(manifest_path):
            os.remove(manifest_path)

        create_manifest(collection_id, object_id, config_path=temp_config_path)

        # Check the generated manifest.
        assert os.path.isfile(manifest_path), "manifest.json was not created."
        assert os.path.getsize(manifest_path) > 0, f"Manifest {manifest_path} is empty."

        # Compare the generated manifest to the canonical fixture version.
        if not filecmp.cmp(manifest_path, canonical_manifest_path, shallow=False):
            with open(manifest_path, "r", encoding="utf-8") as f1, open(canonical_manifest_path, "r", encoding="utf-8") as f2:
                manifest1 = json.dumps(json.load(f1), indent=2, sort_keys=True).splitlines()
                manifest2 = json.dumps(json.load(f2), indent=2, sort_keys=True).splitlines()

            diff = "\n".join(difflib.unified_diff(manifest1, manifest2, fromfile="new_manifest", tofile="canonical_manifest", lineterm=""))

            assert False, f"Manifest does not match canonical fixture version:\n{diff}"

    iterate_collections_and_objects(temp_discovery_storage_root, test_action)


def test_manifest_top_level_shape(tmp_path):
    manifest = _generate_manifest(tmp_path, "ua200", "fd198d1a2ebfdddad630c9698a38df29")

    assert manifest.get("@context") == "http://iiif.io/api/presentation/3/context.json"
    assert manifest.get("type") == "Manifest"
    assert isinstance(manifest.get("provider"), list) and manifest["provider"], "Manifest provider is missing."
    assert isinstance(manifest.get("items"), list) and manifest["items"], "Manifest canvases are missing."


def test_manifest_search_service_present_when_hocr_and_content_search_configured(tmp_path):
    manifest = _generate_manifest(tmp_path, "ua200", "fd198d1a2ebfdddad630c9698a38df29")

    services = manifest.get("service", [])
    assert services, "Expected content search service when hOCR exists and content_search_url is configured."
    assert services[0].get("type") == "SearchService"
    assert services[0].get("profile") == "http://iiif.io/api/search/1/search"
    assert services[0].get("id", "").endswith("/ua200/fd198d1a2ebfdddad630c9698a38df29")


def test_manifest_search_service_absent_when_content_search_not_configured(tmp_path):
    manifest = _generate_manifest(
        tmp_path,
        "ua200",
        "fd198d1a2ebfdddad630c9698a38df29",
        config_overrides={"content_search_url": None},
    )

    assert "service" not in manifest or not manifest.get("service"), (
        "Did not expect content search service when content_search_url is not configured."
    )


def test_manifest_video_canvas_includes_vtt_supplementing_annotation(tmp_path):
    manifest = _generate_manifest(tmp_path, "apap150", "894a38c4895e189ea982af845f46e99e")

    first_canvas = manifest["items"][0]
    annotations = first_canvas.get("annotations", [])
    assert annotations, "Expected supplementing annotations on video canvas."

    bodies = annotations[0]["items"][0].get("body", [])
    assert any(body.get("format") == "text/vtt" for body in bodies), "Expected VTT supplementing body on video canvas."


def test_manifest_audio_canvas_includes_primary_and_alternate_audio_bodies(tmp_path):
    manifest = _generate_manifest(tmp_path, "apap401", "56b3ab1c00ac03862ef0f47650905013")

    first_canvas = manifest["items"][0]
    anno_page = first_canvas["items"][0]
    painting_annotations = [item for item in anno_page.get("items", []) if item.get("motivation") == "painting"]
    formats = {item.get("body", {}).get("format") for item in painting_annotations}

    assert "audio/ogg" in formats, "Expected primary OGG painting annotation."
    assert "audio/mpeg" in formats, "Expected alternate MP3 painting annotation when MP3 derivative exists."


def test_manifest_renderings_include_content_and_original_label(tmp_path):
    manifest = _generate_manifest(tmp_path, "ua200", "fd198d1a2ebfdddad630c9698a38df29")

    renderings = manifest.get("rendering", [])
    assert renderings, "Expected rendering entries in ua200 manifest."

    rendering_ids = [item.get("id", "") for item in renderings]
    assert any(item_id.endswith("/content.txt") for item_id in rendering_ids), "Expected content.txt rendering entry."

    labels = []
    for rendering in renderings:
        label = rendering.get("label", {})
        if isinstance(label, dict):
            labels.extend(label.get("en", []))
    assert any("(Original)" in label for label in labels), "Expected at least one rendering label marked as original."
