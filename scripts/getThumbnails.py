import os
import yaml
import time
import requests
import sys
import traceback
import shutil

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

        session = requests.Session()
        session.verify = False

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

                    #try:
                    with open(metadataPath, 'r', encoding='utf-8') as file:
                        metadata = yaml.safe_load(file)

                    if not metadata.get('resource_type') == "Audio":
                        thumbnail_id = metadata.get('representative_id')
                        thumbnail_url = f"{root_url}{thumbnail_id}?file=thumbnail" if thumbnail_id else None

                        if thumbnail_url:
                            response = session.get(thumbnail_url)
                            if response.status_code == 200:
                                with open(thumbnail_path, 'wb') as img_file:
                                    img_file.write(response.content)
                                    #print(f"Thumbnail downloaded and saved as thumbnail.jpg in {objPath}")
                            else:
                                print(f"Failed to download image for {objPath}. Status code: {response.status_code}")
                        else:
                            print(f"No representative_id found in metadata for {objPath}.")
                    else:
                        print ("copying audio thumb...")
                        shutil.copy2(os.path.join(root, "thumbnail.jpg"), thumbnail_path)                        

                    #except Exception as e:
                    #    with open(log_file, "a") as log:
                    #        log.write(f"\nERROR loading thumbnail for {objPath}\n")
                    #        log.write(traceback.format_exc())
                    #        time.sleep(5)

        session.close()



if __name__ == "__main__":
    # Check for command-line arguments
    print (sys.argv)
    if len(sys.argv) > 1:
        collection_ids = sys.argv[1].split(',')
        force_flag = len(sys.argv) > 2 and sys.argv[2].lower() == "-f"
        
        for collection_id in collection_ids:
            print(f"Processing collection: {collection_id}")
            download_thumbnails(collection_id=collection_id, force=force_flag)
    else:
        download_thumbnails()
