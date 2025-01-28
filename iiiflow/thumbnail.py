import os
import traceback
import subprocess
from .utils import validate_config_and_paths

def make_thumbnail(collection_id, object_id, config_path="~/.iiiflow.yml"):
    """
    Creates a 300x300 thumbnail.jpg.
    Designed to be used with the discovery storage specification.
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

    thumbnail_path = os.path.join(object_path, 'thumbnail.jpg')

    print(f"Creating thumbnail for {object_path}...")

    try:

        image_order = ["jpg", "png"]
        for format_ext in image_order:
            image_dir = os.path.join(object_path, format_ext)
            if os.path.isdir(image_dir) and len(os.listdir(image_dir)) > 0:
                image_path = os.path.join(image_dir, os.listdir(image_dir)[0])
                subprocess.run([
                        'convert', image_path,
                        '-resize',
                        '300x300',
                        thumbnail_path
                    ])
                break

    except Exception as e:
        with open(log_file_path, "a") as log:
            log.write(f"\nERROR creating thumbnail for {object_path}\n")
            log.write(traceback.format_exc())

