import os
import shutil
import pytest
from iiiflow import create_hocr
from test_utils import load_config, iterate_collections_and_objects

config_path = "./.iiiflow.yml"
discovery_storage_root, log_file_path = load_config(config_path)

@pytest.fixture
def clean_text_directories():
    # This fixture cleans up any ptif directories at the start of the test

    def cleanup_action(collection_id, object_id, object_path):
        hocr_path = os.path.join(object_path, "hocr")
        txt_path = os.path.join(object_path, "txt")
        content_path = os.path.join(object_path, "content.txt")
        if os.path.isdir(hocr_path):
            shutil.rmtree(hocr_path)  # Delete the hocr directory
            print(f"Deleted hocr directory: {hocr_path}")
        if os.path.isdir(txt_path):
            shutil.rmtree(txt_path)  # Delete the txt directory
            print(f"Deleted txt directory: {txt_path}")
        if os.path.isfile(content_path):
            os.remove(content_path)  # Delete content.txt
            print(f"Deleted content.txt: {content_path}")

    return cleanup_action


def test_tesseract(clean_text_directories):

    def test_action(collection_id, object_id, object_path):
        

        # Check for HOCR and TXT
        img_formats = ["jpg", "png", "jpeg", "tif"]
        for img_format in img_formats:
            format_path = os.path.join(object_path, img_format)
            if os.path.isdir(format_path):

                clean_text_directories(collection_id, object_id, object_path)
                create_hocr(collection_id, object_id, config_path=config_path)

                for input_file in os.listdir(format_path):
                    if input_file.lower().endswith(img_format):
                        hocr_file = os.path.splitext(input_file)[0] + ".hocr"
                        hocr_path = os.path.join(object_path, "hocr", hocr_file)
                        txt_file = os.path.splitext(input_file)[0] + ".txt"
                        txt_path = os.path.join(object_path, "txt", txt_file)

                        # Assert the output
                        assert os.path.isfile(hocr_path), "HOCR file was not created."
                        assert os.path.getsize(hocr_path) > 0, f"{hocr_file} is empty."
                        assert os.path.isfile(txt_path), "TXT file was not created."
                        assert os.path.getsize(txt_path) > 0, f"{txt_file} is empty."
                # Check for content.txt
                content_path = os.path.join(object_path, "content.txt")
                assert os.path.isfile(content_path), "content.txt file was not created."
                assert os.path.getsize(content_path) > 0, "content.txt is empty."
                break

    iterate_collections_and_objects(discovery_storage_root, test_action)
    