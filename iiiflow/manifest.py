import os
import yaml
import json
from iiif_prezi3 import config
from .utils import validate_config_and_paths, remove_nulls
from .manifest_builders import (
    create_iiif_manifest as _create_iiif_manifest,
    create_iiif_canvas as _create_iiif_canvas,
    build_manifest_label,
    resolve_resource_source,
    thumbnail_data,
)


def create_iiif_canvas(*args, **kwargs):
    """Compatibility wrapper retained for external callers."""
    return _create_iiif_canvas(*args, **kwargs)


def create_iiif_manifest(*args, **kwargs):
    """Compatibility wrapper retained for external callers."""
    return _create_iiif_manifest(*args, **kwargs)


def create_manifest(collection_id, object_id, config_path="~/.iiiflow.yml"):
    """
    Creates a manifest.json compliant with the IIIF v3 Presentation API
    Designed to be used with the discovery storage specification.
    https://github.com/UAlbanyArchives/arclight_integration_project/blob/main/discovery_storage_spec.md

    Args:
        collection_id (str): The collection ID.
        object_id (str): The object ID.
        config_path (str): Path to the configuration YAML file.
    """

    discovery_storage_root, log_file_path, object_path, manifest_url_root, image_api_root, provider, lang_code = validate_config_and_paths(
        config_path, collection_id, object_id, True, False, True, True
    )

    config.configs["helpers.auto_fields.AutoLang"].auto_lang = lang_code

    metadata_path = os.path.join(object_path, "metadata.yml")
    manifest_path = os.path.join(object_path, "manifest.json")
    with open(metadata_path, "r", encoding="utf-8") as yml_file:
        metadata = yaml.safe_load(yml_file)

    resource_type = metadata["resource_type"]
    files_path, resource_format = resolve_resource_source(object_path, resource_type)

    if files_path and os.path.isdir(files_path):
        print(f"{collection_id}/{object_id}")

        obj_url_root = f"{manifest_url_root}/{collection_id}/{object_id}"
        iiif_url_root = f"{image_api_root}{collection_id}%2F{object_id}%2F{resource_format}"

        manifest_label = build_manifest_label(metadata)
        thumb_data = thumbnail_data(object_path, obj_url_root)

        iiif_manifest = _create_iiif_manifest(
            files_path,
            manifest_url_root,
            obj_url_root,
            iiif_url_root,
            resource_format,
            manifest_label,
            metadata,
            thumb_data,
            resource_type,
            lang_code,
            config_path,
        )
        manifest_dict = iiif_manifest.dict()
        manifest_dict = remove_nulls(manifest_dict)

        provider_data = [
            {
                "id": manifest_url_root,
                "type": "Agent",
                "label": {lang_code: [provider]},
                "logo": [
                    {
                        "id": f"{manifest_url_root}/logo.png",
                        "type": "Image",
                        "format": "image/png"
                    }
                ]
            }
        ]

        manifest_output = {
            "@context": "http://iiif.io/api/presentation/3/context.json",
            "provider": provider_data,
            **manifest_dict
        }

        with open(manifest_path, "w") as file_handle:
            json.dump(manifest_output, file_handle, indent=2)

        print("\t --> IIIF manifest created successfully!")
    else:
        print(f"\tERROR: no path found {files_path}")
