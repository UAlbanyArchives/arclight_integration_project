import os
import shutil
import pytest
from iiiflow import create_ptif
from test_utils import load_config, iterate_collections_and_objects

config_path = "./.iiiflow.yml"
discovery_storage_root, log_file_path = load_config(config_path)

@pytest.fixture
def clean_ptif_directories():
    # This fixture cleans up any ptif directories at the start of the test

    def cleanup_action(collection_id, object_id, object_path):
        ptif_path = os.path.join(object_path, "ptif")
        if os.path.isdir(ptif_path):
            shutil.rmtree(ptif_path)  # Delete the ptif directory
            print(f"Deleted ptif directory: {ptif_path}")

    return cleanup_action


def test_ptifs(clean_ptif_directories):
    # Test to see if create_ptif() creates pyramidal tiffs

    def test_action(collection_id, object_id, object_path):

        img_formats = ["jpg", "png", "jpeg", "tif"]
        for img_format in img_formats:
            format_path = os.path.join(object_path, img_format)
            if os.path.isdir(format_path):

                clean_ptif_directories(collection_id, object_id, object_path)
                create_ptif(collection_id, object_id, config_path=config_path)

                for input_file in os.listdir(format_path):
                    if input_file.lower().endswith(img_format):
                        output_file = os.path.splitext(input_file)[0] + ".ptif"
                        output_path = os.path.join(object_path, "ptif", output_file)

                        # Assert the output
                        assert os.path.isfile(output_path), "Pyramidal TIFF was not created."
                        assert os.path.getsize(output_path) > 0, f"{output_file} is empty."
                break

    iterate_collections_and_objects(discovery_storage_root, test_action)
