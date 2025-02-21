import os
import yaml
import ffmpeg
import traceback
from PIL import Image

def log_path(config_path):
    """
    Gets the log file path from .iiiflow config

    Args:
        config_path (str): Path to the configuration YAML file.

    Returns:
        str: A string to the log file path
    """
    if config_path.startswith("~"):
        config_path = os.path.expanduser(config_path)
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file {config_path} not found.")

    # Load configuration
    with open(config_path, "r") as config_file:
        config = yaml.safe_load(config_file)
        log_file_path = config.get("error_log_file")

    return log_file_path

def validate_config_and_paths(config_path, collection_id=None, object_id=None, return_url_root=False, return_audio_thumbnail_file=False):
    """
    Validates and retrieves paths based on the configuration file and inputs.
    Optionally returns the `url_root` from the configuration if `return_url_root` is True.

    Args:
        config_path (str): Path to the configuration YAML file.
        collection_id (str): The collection ID.
        object_id (str): The object ID.
        return_url_root (bool): Whether to return the `url_root` from the config.
        return_audio_thumbnail_file (bool): Whether to return the `audio_thumbnail_file` from the config.

    Returns:
        tuple: A tuple containing discovery_storage_root, log_file_path, object_path, 
               and optionally url_root and/or audio_thumbnail_file if those options are True.
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
    audio_thumbnail_file = config.get("audio_thumbnail_file")

    if not discovery_storage_root:
        raise ValueError("`discovery_storage_root` not defined in configuration file.")
    if not log_file_path:
        raise ValueError("`error_log_file` not defined in configuration file.")
    if not os.path.isdir(discovery_storage_root):
        raise ValueError(f"Configured discovery storage root is not a directory: {discovery_storage_root}")

    config_data = [discovery_storage_root, log_file_path]

    # Build and validate object path
    if collection_id and object_id:
        object_path = os.path.join(discovery_storage_root, collection_id, object_id)
        if not os.path.isdir(object_path):
            raise ValueError(f"Object path does not exist: {object_path}")
        config_data.append(object_path)
    else:
        config_data.append(None)

    # If requested, return the url_root along with the other paths
    if return_url_root:
        config_data.append(url_root)

    if return_audio_thumbnail_file:
        config_data.append(audio_thumbnail_file)

    return tuple(config_data)


def check_no_image_type(object_path):
    """ Checks if an object should have images based on resource_type in metadata.yml
        Returns True if the object may not have images.
        False should have images
    """
    no_image_types = ["Audio", "Dataset", "Video"]
    metadata_path = os.path.join(object_path, "metadata.yml")
    if not os.path.isfile(metadata_path):
        raise FileNotFoundError(f"Missing metadata file {metadata_path}.")
    else:
        try:
            with open(metadata_path, "r") as metadata_file:
                metadata = yaml.safe_load(metadata_file)
                if not metadata["resource_type"] in no_image_types:
                    return False
                else:
                    return True
        except Exception as e:
            with open(log_file_path, "a") as log:
                log.write(f"\nERROR reading metadata.yml for {object_path}\n")
                log.write(traceback.format_exc())

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
