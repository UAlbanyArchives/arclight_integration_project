import os
import pytest
from iiiflow import validate_metadata
from test_utils import load_config, iterate_collections_and_objects

config_path = "./.iiiflow.yml"
discovery_storage_root, log_file_path = load_config(config_path)

def test_metadata():
    # Test presence of metadata.yml and validate it with validate_metadata()

    def test_action(collection_id, object_id, object_path):
        valid = validate_metadata(collection_id, object_id, config_path=config_path)
        assert valid, f"metadata.yml for {object_path} is invalid."

    iterate_collections_and_objects(discovery_storage_root, test_action)
