import os
import yaml

def load_config(config_path="./.iiiflow.yml"):
    """Load configuration from the specified YAML file."""
    with open(config_path, "r") as config_file:
        config = yaml.safe_load(config_file)
    return config["discovery_storage_root"], config["error_log_file"]

def iterate_collections_and_objects(discovery_storage_root, action):
    """
    Iterate through all collections and objects in the discovery storage root
    and apply the given action.

    :param discovery_storage_root: Path to the root directory for collections.
    :param action: A function that takes `collection_id`, `object_id`, and `object_path`.
    """
    for collection_id in os.listdir(discovery_storage_root):
        collection_path = os.path.join(discovery_storage_root, collection_id)
        if os.path.isdir(collection_path):
            for object_id in os.listdir(collection_path):
                object_path = os.path.join(collection_path, object_id)
                if os.path.isdir(object_path):
                    action(collection_id, object_id, object_path)
