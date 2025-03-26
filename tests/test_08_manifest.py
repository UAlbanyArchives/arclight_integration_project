import os
import json
import shutil
import pytest
import filecmp
import difflib
from iiiflow import create_manifest
from test_utils import load_config, iterate_collections_and_objects

config_path = "./.iiiflow.yml"
discovery_storage_root, log_file_path = load_config(config_path)

@pytest.fixture
def clean_manifest():
    # This fixture removes the existing manifest.json the start of the test

    def cleanup_action(collection_id, object_id, object_path):
        manifest_path = os.path.join(object_path, "manifest.json")
        if os.path.isfile(manifest_path):
            os.remove(manifest_path)
            print(f"Deleted manifest: {manifest_path}")

    return cleanup_action

def test_manifest(clean_manifest):
    # Test creation of manifest.json

    def test_action(collection_id, object_id, object_path):

        manifest_path = os.path.join(object_path, "manifest.json")
        manifest_tmp = shutil.copy(manifest_path, manifest_path + ".tmp")
        clean_manifest(collection_id, object_id, object_path)
        create_manifest(collection_id, object_id, config_path=config_path)

        # Check the manifest
        assert os.path.isfile(manifest_path), "manifest.json was not created."
        assert os.path.getsize(manifest_path) > 0, f"Manifest {manifest_path} is empty."

        # Compare the two files
        if not filecmp.cmp(manifest_path, manifest_tmp, shallow=False):
            # Load JSON content for structured comparison
            with open(manifest_path, "r", encoding="utf-8") as f1, open(manifest_tmp, "r", encoding="utf-8") as f2:
                manifest1 = json.dumps(json.load(f1), indent=2, sort_keys=True).splitlines()
                manifest2 = json.dumps(json.load(f2), indent=2, sort_keys=True).splitlines()

            # Generate a diff
            diff = "\n".join(difflib.unified_diff(manifest1, manifest2, fromfile="new_manifest", tofile="old_manifest", lineterm=""))
            
            assert False, f"Manifest does not match previous version:\n{diff}"

        # remove tmp manifest
        os.remove(manifest_tmp)

    iterate_collections_and_objects(discovery_storage_root, test_action)
