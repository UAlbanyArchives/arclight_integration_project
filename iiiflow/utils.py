import os
import yaml
import ffmpeg
from PIL import Image

def validate_config_and_paths(config_path, collection_id, object_id, return_url_root=False):
    """
    Validates and retrieves paths based on the configuration file and inputs.
    Optionally returns the `url_root` from the configuration if `return_url_root` is True.

    Args:
        config_path (str): Path to the configuration YAML file.
        collection_id (str): The collection ID.
        object_id (str): The object ID.
        return_url_root (bool): Whether to return the `url_root` from the config.

    Returns:
        tuple: A tuple containing discovery_storage_root, log_file_path, object_path, 
               and optionally url_root if return_url_root is True.
    """

    # Resolve configuration file path
    if config_path.startswith("~"):
        config_path = os.path.expanduser(config_path)
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file {config_path} not found.")

    # Load configuration
    with open(config_path, "r") as config_file:
        config = yaml.safe_load(config_file)

    discovery_storage_root = config.get("discovery_storage_root")
    log_file_path = config.get("error_log_file")
    url_root = config.get("manifest_url_root")

    if not discovery_storage_root:
        raise ValueError("`discovery_storage_root` not defined in configuration file.")
    if not log_file_path:
        raise ValueError("`error_log_file` not defined in configuration file.")
    if not os.path.isdir(discovery_storage_root):
        raise ValueError(f"Configured discovery storage root is not a directory: {discovery_storage_root}")

    # Build and validate object path
    object_path = os.path.join(discovery_storage_root, collection_id, object_id)
    if not os.path.isdir(object_path):
        raise ValueError(f"Object path does not exist: {object_path}")

    # If requested, return the url_root along with the other paths
    if return_url_root:
        return discovery_storage_root, log_file_path, object_path, url_root

    # Otherwise, return just the basic paths
    return discovery_storage_root, log_file_path, object_path

def remove_nulls(d):
    """Recursively remove keys with None values from a dictionary or list."""
    if isinstance(d, dict):
        return {k: remove_nulls(v) for k, v in d.items() if v is not None}
    elif isinstance(d, list):
        return [remove_nulls(v) for v in d if v is not None]
    else:
        return d

def get_image_dimensions(image_path):
    # Get the width and height for an image
    with Image.open(image_path) as img:
        # Get the dimensions of the image (width, height)
        width, height = img.size
    return width, height

def get_media_info(resource_path):
    """Get media duration, format, width, and height using ffprobe from ffmpeg."""
    try:
        probe = ffmpeg.probe(resource_path)
        format_info = probe.get('format', {})
        
        # Get duration
        duration = float(format_info.get('duration', 0))

        # Initialize width and height
        video_width = None
        video_height = None
        mimetype = 'application/octet-stream'  # Default mimetype

        # Determine format and set mimetype accordingly
        format_name = format_info.get('format_name', '')

        if 'webm' in format_name:
            mimetype = 'video/webm'
        elif 'ogg' in format_name:
            mimetype = 'audio/ogg'
        elif 'mp4' in format_name:
            mimetype = 'video/mp4'
        elif 'mp3' in format_name:
            mimetype = 'audio/mpeg'

        # Get width and height for video formats
        if format_info.get('nb_streams', 0) > 0:
            streams = probe.get('streams', [])
            for stream in streams:
                if stream.get('codec_type') == 'video':
                    video_width = stream.get('width')
                    video_height = stream.get('height')
                    break  # Exit loop after first video stream

        return duration, mimetype, video_width, video_height

    except ffmpeg.Error as e:
        print(f"Error getting media info: {e}")
        return None, None, None, None
