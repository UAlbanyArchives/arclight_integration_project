import os
import pytest
from iiiflow import create_ptif
from test_utils import load_config, iterate_collections_and_objects, create_temp_fixture_config

config_path = "./.iiiflow.yml"
discovery_storage_root, log_file_path = load_config(config_path)

def test_ptifs(tmp_path):
    # Test to see if create_ptif() creates pyramidal tiffs

    temp_discovery_storage_root, temp_config_path = create_temp_fixture_config(tmp_path, config_path)

    def test_action(collection_id, object_id, object_path):
        canonical_object_path = os.path.join(discovery_storage_root, collection_id, object_id)

        img_formats = ["jpg", "png", "jpeg", "tif"]
        for img_format in img_formats:
            canonical_format_path = os.path.join(canonical_object_path, img_format)
            if os.path.isdir(canonical_format_path):
                ptif_path = os.path.join(object_path, "ptif")
                canonical_ptif_path = os.path.join(canonical_object_path, "ptif")
                if os.path.isdir(ptif_path):
                    for filename in os.listdir(ptif_path):
                        os.remove(os.path.join(ptif_path, filename))

                create_ptif(collection_id, object_id, config_path=temp_config_path)

                for input_file in os.listdir(canonical_format_path):
                    if input_file.lower().endswith(img_format):
                        output_file = os.path.splitext(input_file)[0] + ".ptif"
                        output_path = os.path.join(object_path, "ptif", output_file)
                        canonical_output_path = os.path.join(canonical_ptif_path, output_file)

                        # Assert the output
                        assert os.path.isfile(output_path), "Pyramidal TIFF was not created."
                        assert os.path.getsize(output_path) > 0, f"{output_file} is empty."
                        if os.path.isfile(canonical_output_path):
                            assert os.path.getsize(canonical_output_path) > 0, f"Canonical {output_file} is empty."
                break

    iterate_collections_and_objects(temp_discovery_storage_root, test_action)
