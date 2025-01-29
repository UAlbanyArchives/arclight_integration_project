import os
import yaml
import shutil
import requests
import traceback
import subprocess
from .utils import validate_config_and_paths

def get_audio_thumbnail(audio_thumbnail_file, thumbnail_path):
    if audio_thumbnail_file:
        if audio_thumbnail_file.lower().startswith("http"):
            response = requests.get(audio_thumbnail_file, stream=True)
            response.raise_for_status()
            with open(thumbnail_path, "wb") as file:
                for chunk in response.iter_content(1024):  # Download in chunks
                    file.write(chunk)
        elif os.path.isfile(audio_thumbnail_file):
            shutil.copy2(audio_thumbnail_file, thumbnail_path)
        else:
            raise FileNotFoundError("No audio_thumbnail_file listed in .iiiflow.yml config not available.")
    else:
        raise FileNotFoundError("No audio_thumbnail_file listed in .iiiflow.yml config.")

def get_video_duration(video_path):
    """Gets the duration of the video using ffprobe."""
    cmd = [
        "ffprobe", 
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Error getting video duration: {e}")
        return 0  # Default to 0 if duration can't be determined

def create_video_thumbnail(video_path, thumbnail_path):
    """Creates a 300x300 thumbnail from the best timestamp in the video."""
    duration = get_video_duration(video_path)
    timestamp = min(30, duration)  # Use 30 seconds or the end of the video if shorter

    cmd = [
        "ffmpeg",
        "-y",  # Overwrite output if it exists
        "-i", video_path,
        "-vf", "scale=300:-1",
        "-ss", str(timestamp),  # Seek to the right time
        "-vframes", "1",  # Extract only one frame
        thumbnail_path
    ]
    print (cmd)
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print(f"Thumbnail saved at: {thumbnail_path}")
    except Exception as e:
        print(f"Error generating thumbnail: {e}")

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
    discovery_storage_root, log_file_path, object_path, audio_thumbnail_file = validate_config_and_paths(
        config_path, collection_id, object_id, False, True
    )

    thumbnail_path = os.path.join(object_path, 'thumbnail.jpg')

    print(f"Creating thumbnail for {object_path}...")

    try:

        metadata_path = os.path.join(object_path, "metadata.yml")
        if not os.path.isfile(metadata_path):
            raise FileNotFoundError(f"Missing metadata file {metadata_path}.")
        else:
            with open(metadata_path, "r") as metadata_file:
                metadata = yaml.safe_load(metadata_file)
                if metadata["resource_type"] == "Audio":
                    get_audio_thumbnail(audio_thumbnail_file, thumbnail_path)
                elif metadata["resource_type"] == "Video":
                    format_order = ["webm", "mp4", "mpeg", "mov", "avi"]
                    for format_ext in format_order:
                        video_dir = os.path.join(object_path, format_ext)
                        if os.path.isdir(video_dir) and len(os.listdir(video_dir)) > 0:
                            video_path = os.path.join(video_dir, os.listdir(video_dir)[0])
                            create_video_thumbnail(video_path, thumbnail_path)
                else:
                    image_order = ["jpg", "jpeg", "png"]
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

