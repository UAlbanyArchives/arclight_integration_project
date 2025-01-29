import os
import yaml
import traceback
from subprocess import Popen, PIPE
from .utils import check_no_image_type
from .utils import validate_config_and_paths

def create_ptif(collection_id, object_id, config_path="~/.iiiflow.yml"):
    """
    Converts images in a given collection and object directory to pyramidal TIFFs.
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

    img_path = os.path.join(object_path, "jpg")
    if not os.path.isdir(img_path):
        # Try alternate directories
        for folder in ["png", "jpeg", "tif"]:
            img_path = os.path.join(object_path, folder)
            if os.path.isdir(img_path):
                break
        else:
            if not check_no_image_type:
                raise ValueError(f"ERROR: Could not find valid image folder in {object_path}.")
            
    if os.path.isdir(img_path):
        ptif_path = os.path.join(object_path, "ptif")
        if not os.path.isdir(ptif_path):
            os.mkdir(ptif_path)

        for img in os.listdir(img_path):
            if img.lower().endswith((".jpg", ".jpeg", ".png", ".tif")):
                print(f"\tConverting {img}...")
                img_filepath = os.path.join(img_path, img)
                filename = os.path.splitext(img)[0]
                outfile = os.path.join(ptif_path, f"{filename}.ptif")

                vips_cmd = [
                    "vips", "tiffsave",
                    img_filepath, outfile,
                    "--tile",
                    "--pyramid",
                    "--compression=jpeg",
                    "--Q=90"
                ]

                try:
                    vips = Popen(vips_cmd, stdout=PIPE, stderr=PIPE)
                    stdout, stderr = vips.communicate()
                    if vips.returncode != 0:
                        raise RuntimeError(stderr.decode("utf-8"))
                except Exception as e:
                    with open(log_file_path, "a") as log:
                        log.write(f"\nERROR converting {img_filepath} to P-tiff:\n")
                        log.write(traceback.format_exc())

