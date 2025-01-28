import os
import pytest
from iiiflow import make_thumbnail
from test_utils import load_config, iterate_collections_and_objects

config_path = "./.iiiflow.yml"
discovery_storage_root, log_file_path = load_config(config_path)

@pytest.fixture
def clean_thumbnail():
    # This fixture cleans up existing thumbnail the start of the test

    def cleanup_action(collection_id, object_id, object_path):
        thumbnail_path = os.path.join(object_path, "thumbnail.jpg")
        if os.path.isfile(thumbnail_path):
            os.remove(thumbnail_path)
            print(f"Deleted thumbnail: {thumbnail_path}")

    iterate_collections_and_objects(discovery_storage_root, cleanup_action)

def test_thumbnail(clean_thumbnail):
    """Test creating thumbnail.jpg"""

    def test_action(collection_id, object_id, object_path):
        make_thumbnail(collection_id, object_id, config_path=config_path)
        thumbnail_path = os.path.join(object_path, "thumbnail.jpg")

        # Assert the thumbnail
        assert os.path.isfile(thumbnail_path), "Thumbnail was not created."
        assert os.path.getsize(thumbnail_path) > 0, f"Thumbnail {thumbnail_path} is empty."

    iterate_collections_and_objects(discovery_storage_root, test_action)
