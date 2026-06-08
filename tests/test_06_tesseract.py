import os
import yaml
from iiiflow import create_hocr
from test_utils import load_config, iterate_collections_and_objects, create_temp_fixture_config, assert_text_file_similar

config_path = "./.iiiflow.yml"
discovery_storage_root, log_file_path = load_config(config_path)

def test_tesseract(tmp_path):

    temp_discovery_storage_root, temp_config_path = create_temp_fixture_config(tmp_path, config_path)

    def test_action(collection_id, object_id, object_path):
        canonical_object_path = os.path.join(discovery_storage_root, collection_id, object_id)
        metadata_path = os.path.join(object_path, "metadata.yml")
        metadata = {}
        if os.path.isfile(metadata_path):
            with open(metadata_path, "r", encoding="utf-8") as metadata_file:
                metadata = yaml.safe_load(metadata_file) or {}

        automated_text_tool = metadata.get("automated_text_tool")
        automated_text_tool_normalized = str(automated_text_tool).strip().lower() if automated_text_tool is not None else ""
        should_run_tesseract = automated_text_tool is None or automated_text_tool_normalized == "tesseract"

        # Check for HOCR and TXT
        img_formats = ["jpg", "png", "jpeg", "tif"]
        for img_format in img_formats:
            format_path = os.path.join(canonical_object_path, img_format)
            if os.path.isdir(format_path):
                hocr_path = os.path.join(object_path, "hocr")
                txt_path = os.path.join(object_path, "txt")
                content_path = os.path.join(object_path, "content.txt")

                if os.path.isdir(hocr_path):
                    for filename in os.listdir(hocr_path):
                        os.remove(os.path.join(hocr_path, filename))
                if os.path.isdir(txt_path):
                    for filename in os.listdir(txt_path):
                        os.remove(os.path.join(txt_path, filename))
                if os.path.isfile(content_path):
                    os.remove(content_path)

                create_hocr(collection_id, object_id, config_path=temp_config_path)

                if not should_run_tesseract:
                    assert not os.path.isfile(content_path), (
                        f"content.txt should not be created when automated_text_tool is '{automated_text_tool_normalized}'"
                    )
                    break

                generated_hocr_dir = os.path.join(object_path, "hocr")
                generated_txt_dir = os.path.join(object_path, "txt")
                canonical_hocr_dir = os.path.join(canonical_object_path, "hocr")
                canonical_txt_dir = os.path.join(canonical_object_path, "txt")

                for input_file in sorted(os.listdir(format_path)):
                    if input_file.lower().endswith(img_format):
                        hocr_file = os.path.splitext(input_file)[0] + ".hocr"
                        generated_hocr_path = os.path.join(generated_hocr_dir, hocr_file)
                        txt_file = os.path.splitext(input_file)[0] + ".txt"
                        generated_txt_path = os.path.join(generated_txt_dir, txt_file)
                        canonical_hocr_path = os.path.join(canonical_hocr_dir, hocr_file)
                        canonical_txt_path = os.path.join(canonical_txt_dir, txt_file)

                        # Assert the output
                        assert os.path.isfile(generated_hocr_path), "HOCR file was not created."
                        assert os.path.getsize(generated_hocr_path) > 0, f"{hocr_file} is empty."
                        if os.path.isfile(canonical_hocr_path):
                            assert os.path.getsize(canonical_hocr_path) > 0, f"Canonical {hocr_file} is empty."

                        assert os.path.isfile(generated_txt_path), "TXT file was not created."
                        # Per-page OCR text can vary substantially; enforce quality via content.txt below.

                # Check for content.txt
                assert os.path.isfile(content_path), "content.txt file was not created."
                assert os.path.getsize(content_path) > 0, "content.txt is empty."
                canonical_content_path = os.path.join(canonical_object_path, "content.txt")
                if os.path.isfile(canonical_content_path):
                    assert_text_file_similar(content_path, canonical_content_path, min_length_ratio=0.75, min_similarity_ratio=0.8)

                break

    iterate_collections_and_objects(temp_discovery_storage_root, test_action)


def test_tesseract_web_archive_text_extraction(tmp_path):
    temp_discovery_storage_root, temp_config_path = create_temp_fixture_config(tmp_path, config_path)

    web_archive_objects = [
        ("ua600.007", "d31b512cf15fb175cd50150637af7153"),
        ("ua600.007", "10bf52164d525cc86b92ebd9f9bb668e"),
    ]

    for collection_id, object_id in web_archive_objects:
        object_path = os.path.join(temp_discovery_storage_root, collection_id, object_id)
        txt_path = os.path.join(object_path, "txt")
        content_path = os.path.join(object_path, "content.txt")

        if os.path.isdir(txt_path):
            for filename in os.listdir(txt_path):
                os.remove(os.path.join(txt_path, filename))
        if os.path.isfile(content_path):
            os.remove(content_path)

        create_hocr(collection_id, object_id, config_path=temp_config_path)
        
        assert os.path.isdir(txt_path), f"Missing txt directory for {collection_id}/{object_id}"
        generated_txt_files = [f for f in os.listdir(txt_path) if f.lower().endswith(".txt")]
        assert generated_txt_files, f"No per-page txt files generated for {collection_id}/{object_id}"

        assert os.path.isfile(content_path), f"Missing content.txt for {collection_id}/{object_id}"
        assert os.path.getsize(content_path) > 0, f"content.txt is empty for {collection_id}/{object_id}"
    