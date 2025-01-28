import os
import shutil
import pytest
from iiiflow import create_transcription
from test_utils import load_config, iterate_collections_and_objects

config_path = "./.iiiflow.yml"
discovery_storage_root, log_file_path = load_config(config_path)

@pytest.fixture
def clean_transcripion():
    # This fixture cleans up existing transcripion the start of the test

    def cleanup_action(collection_id, object_id, object_path):
        vtt_path = os.path.join(object_path, "vtt")
        txt_path = os.path.join(object_path, "txt")
        content_path = os.path.join(object_path, "content.txt")
        if os.path.isdir(vtt_path):
            shutil.rmtree(vtt_path)  # Delete the hocr directory
            print(f"Deleted vtt directory: {vtt_path}")
        if os.path.isdir(txt_path):
            shutil.rmtree(txt_path)  # Delete the txt directory
            print(f"Deleted txt directory: {txt_path}")
        if os.path.isfile(content_path):
            os.remove(content_path)  # Delete content.txt
            print(f"Deleted content.txt: {content_path}")

    iterate_collections_and_objects(discovery_storage_root, cleanup_action)

def test_transcription(clean_transcripion):
    """Test A/V transcriptions"""

    def test_action(collection_id, object_id, object_path):
        create_transcription(collection_id, object_id, config_path=config_path)
        thumbnail_path = os.path.join(object_path, "thumbnail.jpg")

        # Check for content.txt
        content_path = os.path.join(object_path, "content.txt")
        assert os.path.isfile(content_path), "content.txt file was not created."
        assert os.path.getsize(content_path) > 0, "content.txt is empty."

        # Check for HOCR and TXT
        formats = ["webm", "ogg", "mp3"]
        for av_format in formats:
            format_path = os.path.join(object_path, av_format)
            if os.path.isdir(format_path):
                for input_file in os.listdir(format_path):
                    if input_file.lower().endswith(av_format):
                        vtt_file = os.path.splitext(input_file)[0] + ".vtt"
                        vtt_path = os.path.join(object_path, "vtt", vtt_file)
                        txt_file = os.path.splitext(input_file)[0] + ".txt"
                        txt_path = os.path.join(object_path, "txt", txt_file)

                        # Assert the output
                        assert os.path.isfile(vtt_path), "HOCR file was not created."
                        assert os.path.getsize(vtt_path) > 0, f"{vtt_file} is empty."
                        assert os.path.isfile(txt_path), "TXT file was not created."
                        assert os.path.getsize(txt_path) > 0, f"{txt_file} is empty."
                break

    iterate_collections_and_objects(discovery_storage_root, test_action)
