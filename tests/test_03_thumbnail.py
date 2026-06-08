import os
import shutil
from iiiflow import make_thumbnail
from test_utils import load_config, iterate_collections_and_objects, create_temp_fixture_config

config_path = "./.iiiflow.yml"
discovery_storage_root, log_file_path = load_config(config_path)

def test_thumbnail(tmp_path):
    """Test creating thumbnail.jpg"""

    temp_discovery_storage_root, temp_config_path = create_temp_fixture_config(tmp_path, config_path)

    def test_action(collection_id, object_id, object_path):
        canonical_thumbnail_path = os.path.join(discovery_storage_root, collection_id, object_id, "thumbnail.jpg")
        thumbnail_path = os.path.join(object_path, "thumbnail.jpg")
        if os.path.isfile(thumbnail_path):
            os.remove(thumbnail_path)

        make_thumbnail(collection_id, object_id, config_path=temp_config_path)
        thumbnail_path = os.path.join(object_path, "thumbnail.jpg")

        # Assert the thumbnail
        assert os.path.isfile(thumbnail_path), "Thumbnail was not created."
        assert os.path.getsize(thumbnail_path) > 0, f"Thumbnail {thumbnail_path} is empty."

        if not os.path.isfile(canonical_thumbnail_path):
            os.makedirs(os.path.dirname(canonical_thumbnail_path), exist_ok=True)
            shutil.copy2(thumbnail_path, canonical_thumbnail_path)

    iterate_collections_and_objects(temp_discovery_storage_root, test_action)
