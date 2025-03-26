import os
import shutil
import pytest
import filecmp
from iiiflow import create_pdf
from test_utils import load_config, iterate_collections_and_objects

config_path = "./.iiiflow.yml"
discovery_storage_root, log_file_path = load_config(config_path)

@pytest.fixture
def clean_pdf():
    # This fixture removes the existing manifest.json the start of the test

    def cleanup_action(collection_id, object_id, object_path):
        pdf_path = os.path.join(object_path, "pdf")
        pdf_files = [f for f in os.listdir(pdf_path) if f.lower().endswith(".pdf")]
        if len(pdf_files) != 1:
            raise RuntimeError(f"Expected 1 PDF in {pdf_path}, but found {len(pdf_files)}: {pdf_files}")
        pdf_file = os.path.join(pdf_path, pdf_files[0])
        if os.path.isfile(pdf_file):
            os.remove(pdf_file)
            print(f"Deleted pdf: {pdf_file}")

    return cleanup_action


def test_pdf(clean_pdf):
    # Test to see if create_pdf() creates the same PDF

    def test_action(collection_id, object_id, object_path):

        pdf_path = os.path.join(object_path, "pdf")
        if os.path.isdir(pdf_path):

            pdf_files = [f for f in os.listdir(pdf_path) if f.lower().endswith(".pdf")]
            if len(pdf_files) != 1:
                raise RuntimeError(f"Expected 1 PDF in {pdf_path}, but found {len(pdf_files)}: {pdf_files}")
            
            pdf_file = os.path.join(pdf_path, pdf_files[0])
            pdf_tmp = shutil.copy(pdf_file, pdf_file + ".tmp")
            clean_pdf(collection_id, object_id, object_path)
            create_pdf(collection_id, object_id, config_path=config_path)

            # Check the manifest
            assert os.path.isfile(pdf_file), "PDF was not created."
            assert os.path.getsize(pdf_file) > 0, f"PDF {pdf_file} is empty."
            assert filecmp.cmp(pdf_file, pdf_tmp), f"PDF does not match previous version."

            # remove tmp PDF
            os.remove(pdf_tmp)

    iterate_collections_and_objects(discovery_storage_root, test_action)
