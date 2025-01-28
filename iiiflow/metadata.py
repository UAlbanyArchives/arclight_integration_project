import os
import yaml
import traceback
from .utils import validate_config_and_paths


def validate_metadata(collection_id, object_id, config_path="~/.iiiflow.yml"):
    """
    Validates metadata.yml
    Designed to be used with the discovery storage specification
    https://github.com/UAlbanyArchives/arclight_integration_project/blob/main/discovery_storage_spec.md

    Args:
        collection_id (str): The collection ID.
        object_id (str): The object ID.
        config_path (str): Path to the configuration YAML file.

    Returns:
        valid (bool)
    """

    # Read config and validate paths
    discovery_storage_root, log_file_path, object_path = validate_config_and_paths(
        config_path, collection_id, object_id
    )

    metadata_path = os.path.join(object_path, "metadata.yml")
    if not os.path.isfile(metadata_path):
        print (f"Missing metadata file {metadata_path}.")
        return False

    try:
        with open(metadata_path, "r") as metadata_file:
            metadata = yaml.safe_load(metadata_file)
    except Exception as e:
        with open(log_file_path, "a") as log:
            log.write(f"\nERROR reading metadata.yml for {object_path}\n")
            log.write(traceback.format_exc())
        return False

    required_keys = ["id",
        "title",
        "collection_number",
        "archivesspace_record",
        "coverage",
        "preservation_package",
        "resource_type",
        "license",
        "date_published",
        "visibility"
    ]
    min_length = 1
    for key in required_keys:
        if key not in metadata:
            raise KeyError(f"Missing required key: {key}")
        value = metadata[key]
        if not isinstance(value, str):
            raise TypeError(f"The value for key '{key}' must be a string, got {type(value).__name__}.")
        if len(value) < min_length:
            raise ValueError(f"The value for key '{key}' must be at least {min_length} characters long.")
    
    if not len(metadata["archivesspace_record"]) == 32:
    	raise ValueError(f"Invalid metadata.yml for {object_path}. archivesspace_record {metadata['archivesspace_record']} is not 32 characters.")

    if not collection_id == metadata["collection_number"]:
    	raise ValueError(f"Invalid metadata.yml for {object_path}. Collection_id {collection_id} does not match collection_number {metadata['collection_number']} in metadata.yml.")

    controlled_fields = {
   		"coverage": ["whole", "part"],
   		"license": [
   			"https://creativecommons.org/licenses/by-nc-nd/4.0/",
   			"https://creativecommons.org/publicdomain/zero/1.0/",
   			"http://creativecommons.org/publicdomain/mark/1.0/", # need to fix legacy data
   			"Unknown"
   			],
   		"resource_type": [
   			"Audio",
   			"Bound Volume",
   			"Dataset",
   			"Document",
   			"Image",
   			"Map",
   			"Mixed Materials",
   			"Pamphlet",
   			"Periodical",
   			"Slides",
   			"Video",
   			"Other"
   		],
   		"behavior": [
   			"unordered",
   			"individuals",
   			"continuous",
   			"paged"
   		]
   	}
    for field in controlled_fields.keys():
    	if field in metadata.keys():
    		if not metadata[field] in controlled_fields[field]:
    			raise ValueError(f"Invalid metadata.yml for {object_path}. Invalid controlled field {field} value {metadata[field]}.")

    rights_statements = [
    	"https://rightsstatements.org/page/InC-EDU/1.0/"
    ]
    if metadata["license"] == "Unknown":
    	if not metadata["rights_statement"] in rights_statements:
    		raise ValueError(f"Invalid metadata.yml for {object_path}. Missing or invalid rights_statement with Unknown license.")

    return True
