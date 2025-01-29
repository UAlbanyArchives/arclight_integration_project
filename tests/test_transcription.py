import os
import shutil
import pytest
import filecmp
from iiiflow import create_transcription
from test_utils import load_config, iterate_collections_and_objects

config_path = "./.iiiflow.yml"
discovery_storage_root, log_file_path = load_config(config_path)

@pytest.fixture
def clean_transcription():
    # This fixture cleans up existing transcription at the start of the test

    def cleanup_action(collection_id, object_id, object_path):
        vtt_path = os.path.join(object_path, "vtt")
        txt_path = os.path.join(object_path, "txt")
        content_path = os.path.join(object_path, "content.txt")
        if os.path.isdir(vtt_path):
            shutil.rmtree(vtt_path)  # Delete the vtt directory
            print(f"Deleted vtt directory: {vtt_path}")
        if os.path.isdir(txt_path):
            shutil.rmtree(txt_path)  # Delete the txt directory
            print(f"Deleted txt directory: {txt_path}")
        if os.path.isfile(content_path):
            os.remove(content_path)  # Delete content.txt
            print(f"Deleted content.txt: {content_path}")

    return cleanup_action

def test_transcription(clean_transcription):
    """Test A/V transcriptions"""

    def test_action(collection_id, object_id, object_path):
        
        formats = ["webm", "ogg", "mp3"]
        for av_format in formats:
            format_path = os.path.join(object_path, av_format)
            if os.path.isdir(format_path):
                # Backup existing files before cleanup
                backup_files = {}
                content_path = os.path.join(object_path, "content.txt")
                backup_files[content_path] = shutil.copy(content_path, content_path + ".tmp")
                for input_file in os.listdir(format_path):
                    if input_file.lower().endswith(av_format):
                        vtt_file = os.path.splitext(input_file)[0] + ".vtt"
                        txt_file = os.path.splitext(input_file)[0] + ".txt"
                        vtt_path = os.path.join(object_path, "vtt", vtt_file)
                        txt_path = os.path.join(object_path, "txt", txt_file)
                        vtt_path_tmp = os.path.join(object_path, vtt_file + ".tmp")
                        txt_path_tmp = os.path.join(object_path, txt_file + ".tmp")

                        if os.path.isfile(vtt_path):
                            backup_files[vtt_path] = shutil.copy(vtt_path, vtt_path_tmp)
                        if os.path.isfile(txt_path):
                            backup_files[txt_path] = shutil.copy(txt_path, txt_path_tmp)                        

                # Now cleanup and create transcriptions
                clean_transcription(collection_id, object_id, object_path)
                create_transcription(collection_id, object_id, config_path=config_path)

                # After transcription, compare the files with backups
                for file_path, backup_path in backup_files.items():
                    assert filecmp.cmp(file_path, backup_path), f"File {file_path} does not match backup."
                    # Remove the backup after comparison
                    os.remove(backup_path)

                break

    iterate_collections_and_objects(discovery_storage_root, test_action)
