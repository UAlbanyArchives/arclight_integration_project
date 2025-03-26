import os
import yaml
import shutil
import traceback
from PIL import Image
from pypdf import PdfMerger
from subprocess import Popen, PIPE
from .utils import check_no_image_type
from .utils import validate_config_and_paths

def process_image_for_pdf(image_path, base_tmp_dir="tmp", max_size=1500, quality=85):
    """
    Processes an image (PNG or JPG) for inclusion in a PDF:
    - Resizes to max_size while maintaining aspect ratio.
    - Converts PNG to compressed JPG.
    - Saves both the temp JPG and a corresponding single-page temp PDF in tmp_dir.

    Returns:
        (temp_jpg_path, temp_pdf_path, tmp_dir)
    """
    # Create a unique temp directory inside base_tmp_dir for processed images
    tmp_dir = os.path.join(os.path.dirname(image_path), base_tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    # Determine new file paths
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    temp_jpg_path = os.path.join(tmp_dir, base_name + ".jpg")
    temp_pdf_path = os.path.join(tmp_dir, base_name + ".pdf")

    # Open and process image
    image = Image.open(image_path).convert("RGB")  # Convert to RGB to remove transparency if PNG
    image.thumbnail((max_size, max_size))  # Resize while maintaining aspect ratio

    # Save as a compressed JPEG
    image.save(temp_jpg_path, "JPEG", quality=quality)

    # Convert to single-page PDF
    image.save(temp_pdf_path, "PDF")

    return temp_jpg_path, temp_pdf_path, tmp_dir  # Return paths to temp files and directory



def create_pdf(collection_id, object_id, config_path="~/.iiiflow.yml"):
    """
    Converts images in a given collection and object directory to a PDF.
    Designed to be used with the discovery storage specification
    https://github.com/UAlbanyArchives/arclight_integration_project/blob/main/discovery_storage_spec.md

    Args:
        collection_id (str): The collection ID.
        object_id (str): The object ID.
        config_path (str): Path to the configuration YAML file.
    """

    img_priorities = ("png", "jpg", "jpeg", "tif", "tiff")

    # Read config and validate paths
    discovery_storage_root, log_file_path, object_path = validate_config_and_paths(
        config_path, collection_id, object_id
    )

    img_dir = None
    for folder in img_priorities:
        img_dir = os.path.join(object_path, folder)
        if os.path.isdir(img_dir):
            break
    if img_dir is None:
        if check_no_image_type:
            print ("Cannot create PDF. Object is A/V or dataset.")
        else:
            raise ValueError(f"ERROR: Could not find valid image folder in {object_path}.")
            
    pdf_path = os.path.join(object_path, "pdf")
    os.makedirs(pdf_path, exist_ok=True)

    # List of PDFs to merge
    pdf_files_to_merge = []

    # Sort images for correct order
    image_files = sorted(
        [f for f in os.listdir(img_dir) if f.lower().endswith(img_priorities)]
    )

    for img in image_files:
        print(f"\tConverting {img} to searchable PDF...")
        img_path = os.path.join(img_dir, img)

        # Generate a searchable PDF from the image using Tesseract
        temp_pdf_path = os.path.join(pdf_path, f"{img[:-4]}.pdf")
        tesseract_cmd = ["tesseract", img_path, temp_pdf_path[:-4], "pdf"]
        
        process = Popen(tesseract_cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            print(f"Tesseract OCR failed for {img}:\nSTDOUT: {stdout.decode('utf-8')}\nSTDERR: {stderr.decode('utf-8')}")
            raise RuntimeError(f"OCR processing failed for {img}.")

        # Append the individual searchable PDF to the list
        pdf_files_to_merge.append(temp_pdf_path)

    # Merge all the individual PDFs into one
    final_pdf_path = os.path.join(pdf_path, "binder.pdf")
    pdf_merger = PdfMerger()

    for pdf in pdf_files_to_merge:
        pdf_merger.append(pdf)

    # Write the final combined PDF
    pdf_merger.write(final_pdf_path)
    pdf_merger.close()

    # Cleanup: Remove individual PDFs
    print("Cleaning up temporary files...")
    for pdf in pdf_files_to_merge:
        os.remove(pdf)

    print(f"Searchable PDF successfully created: {final_pdf_path}")
