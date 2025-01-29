import os
import time
import traceback
from subprocess import Popen, PIPE
from .utils import check_no_image_type
from .utils import validate_config_and_paths

def create_hocr(collection_id, object_id, config_path="~/.iiiflow.yml"):
    """
    Processes images in a given collection and object directory with Tesseract OCR,
    creating HOCR and TXT files for the images, as well as content.txt
    Designed to be used with the discovery storage specification
    https://github.com/UAlbanyArchives/arclight_integration_project/blob/main/discovery_storage_spec.md

    Args:
        collection_id (str): The collection ID.
        object_id (str): The object ID.
        config_path (str): Path to the configuration YAML file.
    """
    
    # Read config and validate paths
    discovery_storage_root, log_file_path, object_path = validate_config_and_paths(
        config_path, collection_id, object_id
    )

    img_dir = os.path.join(object_path, "jpg")
    ocr_dir = os.path.join(object_path, "hocr")
    txt_dir = os.path.join(object_path, "txt")

    print(f"Processing {collection_id}/{object_id}...")

    # if theres no jpg, look for other images
    if not os.path.isdir(img_dir):
        for folder in ["jpeg", "png", "tif"]:
            img_dir = os.path.join(object_path, folder)
            if os.path.isdir(img_dir):
                break
        else:
            if not check_no_image_type:
                raise ValueError(f"ERROR: Could not find valid image folder in {object_path}.")

    if os.path.isdir(img_dir):

        # Ensure the output directories exist
        os.makedirs(ocr_dir, exist_ok=True)
        os.makedirs(txt_dir, exist_ok=True)

        # Aggregate all text files into a single content.txt file
        content_file_path = os.path.join(object_path, "content.txt")
        with open(content_file_path, "w", encoding="utf-8") as content_file:
            for filename in os.listdir(img_dir):
                if filename.lower().endswith((".jpg", ".jpeg", ".png", ".tif")):
                    img_filepath = os.path.join(img_dir, filename)
                    base_filename = os.path.splitext(filename)[0]

                    hocr_filepath = os.path.join(ocr_dir, f"{base_filename}")
                    txt_filepath = os.path.join(txt_dir, f"{base_filename}.txt")

                    tesseract_cmd = [
                        "tesseract",
                        img_filepath,
                        hocr_filepath,
                        '-c', 'tessedit_create_hocr=1',
                        '-c', 'tessedit_create_txt=1',
                        "--dpi", "300"
                    ]
                    generated_txt_path = hocr_filepath + ".txt"
                    
                    try:
                        process = Popen(tesseract_cmd, stdout=PIPE, stderr=PIPE)
                        stdout, stderr = process.communicate()
                        if process.returncode != 0:
                            raise RuntimeError(stderr.decode("utf-8"))

                        # Move the generated .txt file to the txt directory
                        if not os.path.isfile(generated_txt_path):
                            raise ValueError(f"No .txt output in {generated_txt_path}.")
                        else:
                            os.rename(generated_txt_path, txt_filepath)

                        # Append text content to content.txt
                        if os.path.isfile(txt_filepath):
                            with open(txt_filepath, "r", encoding="utf-8") as txt_file:
                                content_file.write(txt_file.read())
                                content_file.write("\n")

                    except Exception as e:
                        with open(log_file_path, "a") as log:
                            log.write(f"\nERROR processing {img_filepath} with Tesseract:\n")
                            log.write(traceback.format_exc())

    print(f"Completed processing for collection {collection_id}.")
