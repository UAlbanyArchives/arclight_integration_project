import os
import json
import filecmp
import difflib
from iiiflow import create_manifest
from test_utils import load_config, iterate_collections_and_objects, create_temp_fixture_config

config_path = "./.iiiflow.yml"
discovery_storage_root, log_file_path = load_config(config_path)


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
