import os
import pytest
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

    iterate_collections_and_objects(discovery_storage_root, cleanup_action)

def test_manifest(clean_manifest):
    # Test creation of manifest.json

    def test_action(collection_id, object_id, object_path):
        create_manifest(collection_id, object_id, config_path=config_path)
        manifest_path = os.path.join(object_path, "manifest.json")

        # Assert the thumbnail
        assert os.path.isfile(manifest_path), "manifest.json was not created."
        assert os.path.getsize(manifest_path) > 0, f"Manifest {manifest_path} is empty."

    iterate_collections_and_objects(discovery_storage_root, test_action)
