import os
import shutil
import pytest
from iiiflow import pdf_to_jpgs
from test_utils import load_config

config_path = "./.iiiflow.yml"
fixture_path = "./fixtures"

def test_pdf_to_jpgs():
    # Test to see if pdf_to_jpgs() extracts jpgs

    pdf_path = os.path.join(fixture_path, "test.pdf")
    out_path = os.path.join(fixture_path, "conversions")
    os.mkdir(out_path)

    pdf_to_jpgs(pdf_path, out_path, config_path=config_path)

    outfiles = ["test-1.jpg", "test-2.jpg"]

    # Check the pdf
    for outfile in outfiles:
        outfile_path = os.path.join(out_path, outfile)
        assert os.path.isfile(outfile_path), "output image was not created."
        assert os.path.getsize(outfile_path) > 0, f"output image {pdf_path} is empty."

    shutil.rmtree(out_path)
