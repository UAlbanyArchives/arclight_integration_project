import os
import yaml
from iiiflow import create_pdf
from test_utils import load_config, iterate_collections_and_objects, create_temp_fixture_config, assert_pdf_matches

config_path = "./.iiiflow.yml"
discovery_storage_root, log_file_path = load_config(config_path)

def test_pdf(tmp_path):
    # Test to see if create_pdf() creates the same PDF.

    temp_discovery_storage_root, temp_config_path = create_temp_fixture_config(tmp_path, config_path)

    def test_action(collection_id, object_id, object_path):
        canonical_object_path = os.path.join(discovery_storage_root, collection_id, object_id)
        metadata_path = os.path.join(object_path, "metadata.yml")
        metadata = {}
        if os.path.isfile(metadata_path):
            with open(metadata_path, "r", encoding="utf-8") as metadata_file:
                metadata = yaml.safe_load(metadata_file) or {}
        original_file_legacy = str(metadata.get("original_file_legacy", ""))
        original_ext = os.path.splitext(original_file_legacy)[1].lower()
        resource_type = str(metadata.get("resource_type", ""))
        source_image_dirs = ["png", "jpg", "jpeg", "tif", "tiff"]
        has_source_images = any(
            os.path.isdir(os.path.join(object_path, source_dir)) and os.listdir(os.path.join(object_path, source_dir))
            for source_dir in source_image_dirs
        )

        pdf_path = os.path.join(object_path, "pdf")
        if os.path.isdir(pdf_path):
            canonical_pdf_path = os.path.join(canonical_object_path, "pdf")

            pdf_files = [f for f in os.listdir(canonical_pdf_path) if f.lower().endswith(".pdf")]
            if len(pdf_files) != 1:
                raise RuntimeError(f"Expected 1 PDF in {canonical_pdf_path}, but found {len(pdf_files)}: {pdf_files}")

            pdf_file = os.path.join(pdf_path, pdf_files[0])
            canonical_pdf_file = os.path.join(canonical_pdf_path, pdf_files[0])

            # Web archives and other non-image resources may carry an externally-produced PDF derivative.
            # In those cases, validate the existing fixture PDF rather than forcing regeneration.
            if resource_type.casefold() == "web archive" or not has_source_images:
                assert os.path.isfile(pdf_file), "Expected existing PDF derivative for non-image resource."
                assert os.path.getsize(pdf_file) > 0, f"PDF {pdf_file} is empty."
                assert_pdf_matches(pdf_file, canonical_pdf_file)
                return

            if os.path.isfile(pdf_file) and original_ext != ".pdf":
                os.remove(pdf_file)

            create_pdf(collection_id, object_id, config_path=temp_config_path)

            generated_pdf_files = [f for f in os.listdir(pdf_path) if f.lower().endswith(".pdf")]
            assert len(generated_pdf_files) == 1, f"Expected 1 generated PDF in {pdf_path}, but found {len(generated_pdf_files)}: {generated_pdf_files}"
            generated_pdf_file = os.path.join(pdf_path, generated_pdf_files[0])

            assert os.path.isfile(generated_pdf_file), "PDF was not created."
            assert os.path.getsize(generated_pdf_file) > 0, f"PDF {generated_pdf_file} is empty."
            assert_pdf_matches(generated_pdf_file, canonical_pdf_file)

    iterate_collections_and_objects(temp_discovery_storage_root, test_action)
