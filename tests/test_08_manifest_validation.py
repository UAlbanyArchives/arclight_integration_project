import os
import json
from iiif_prezi3 import Manifest
from iiiflow import create_manifest
from test_utils import load_config, iterate_collections_and_objects, create_temp_fixture_config


config_path = "./.iiiflow.yml"
discovery_storage_root, log_file_path = load_config(config_path)


def test_generated_manifests_validate_as_iiif_presentation_v3(tmp_path):
    """Generate manifests from fixtures and validate they parse as IIIF Presentation v3 manifests."""
    temp_discovery_storage_root, temp_config_path = create_temp_fixture_config(tmp_path, config_path)

    def test_action(collection_id, object_id, object_path):
        manifest_path = os.path.join(object_path, "manifest.json")
        source_folders = ["ptif", "jpg", "ogg", "mp3", "webm"]

        if not any(os.path.isdir(os.path.join(object_path, folder)) for folder in source_folders):
            return

        if os.path.isfile(manifest_path):
            os.remove(manifest_path)

        create_manifest(collection_id, object_id, config_path=temp_config_path)

        assert os.path.isfile(manifest_path), f"manifest.json was not created for {collection_id}/{object_id}"
        assert os.path.getsize(manifest_path) > 0, f"manifest.json is empty for {collection_id}/{object_id}"

        with open(manifest_path, "r", encoding="utf-8") as manifest_file:
            manifest_json = json.load(manifest_file)

        assert manifest_json.get("@context") == "http://iiif.io/api/presentation/3/context.json", (
            f"Invalid IIIF Presentation context for {collection_id}/{object_id}: {manifest_json.get('@context')}"
        )
        assert manifest_json.get("type") == "Manifest", (
            f"Invalid IIIF Presentation type for {collection_id}/{object_id}: {manifest_json.get('type')}"
        )

        try:
            Manifest.parse_obj(manifest_json)
        except Exception as exc:
            raise AssertionError(
                f"Manifest failed iiif-prezi3 validation for {collection_id}/{object_id}: {exc}"
            ) from exc

    iterate_collections_and_objects(temp_discovery_storage_root, test_action)
