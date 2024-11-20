import os
import yaml
import requests
import sys
import traceback

if os.name == "nt":
    root = "\\\\Lincoln\\Library\\SPE_DAO"
else:
    root = "/media/Library/SPE_DAO"

root_url = 'https://archives.albany.edu/downloads/'
log_path = "/media/Library/ESPYderivatives/export_logs/thumbs"

def download_thumbnails(collection_id=None, force=None):
    for col in os.listdir(root):
        col_path = os.path.join(root, col)

        log_file = os.path.join(log_path, collection_id + ".log")

        # Check if collection_id is provided and matches the current collection
        if collection_id and collection_id not in col:
            continue  # Skip this collection if it doesn't match

        if os.path.isdir(col_path):
            for obj in os.listdir(col_path):
                objPath = os.path.join(col_path, obj)
                metadataPath = os.path.join(objPath, "metadata.yml")

                if not os.path.isfile(metadataPath):
                    print(f"Metadata file not found: {metadataPath}")
                    continue

                thumbnail_path = os.path.join(objPath, 'thumbnail.jpg')

                if not os.path.isfile(thumbnail_path) or force:

                    print(f"Loading thumbnail for {objPath}...")

                    try:
                        with open(metadataPath, 'r', encoding='utf-8') as file:
                            metadata = yaml.safe_load(file)

                        if metadata.get('resource_type') == "Audio":
                            thumbnail_url = "https://archives.albany.edu/assets/audio-5133b642ee875760dbd85bfab48649d009efd4bd29db1165f891b48a90b4f37e.png"
                        else:
                            thumbnail_id = metadata.get('representative_id')
                            thumbnail_url = f"{root_url}{thumbnail_id}?file=thumbnail" if thumbnail_id else None

                        if thumbnail_url:
                            response = requests.get(thumbnail_url)
                            if response.status_code == 200:
                                with open(thumbnail_path, 'wb') as img_file:
                                    img_file.write(response.content)
                                    #print(f"Thumbnail downloaded and saved as thumbnail.jpg in {objPath}")
                            else:
                                print(f"Failed to download image for {objPath}. Status code: {response.status_code}")
                        else:
                            print(f"No representative_id found in metadata for {objPath}.")
                    except Exception as e:
                        with open(log_file, "a") as log:
                            log.write(f"\nERROR loading thumbnail for {objPath}\n")
                            log.write(traceback.format_exc())



if __name__ == "__main__":
    # Check for command-line arguments
    if len(sys.argv) > 1:
        collection_id_arg = sys.argv[1]
        download_thumbnails(collection_id=collection_id_arg)
    else:
        download_thumbnails()
