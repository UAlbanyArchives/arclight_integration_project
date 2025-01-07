import os
import yaml
import time
import sys
import traceback
import shutil
import subprocess

if os.name == "nt":
    root = "\\\\Lincoln\\Library\\SPE_DAO"
else:
    root = "/media/Library/SPE_DAO"

root_url = 'https://archives.albany.edu/downloads/'
log_path = "/media/Library/ESPYderivatives/export_logs/thumbs"

def make_thumb(collection_id=None, object_id=None, force=None):
    for col in os.listdir(root):
        col_path = os.path.join(root, col)

        log_file = os.path.join(log_path, collection_id + ".log")

        # Check if collection_id is provided and matches the current collection
        if collection_id and collection_id != col:
            continue  # Skip this collection if it doesn't match


        if os.path.isdir(col_path):
            for obj in os.listdir(col_path):
                if object_id and obj not in object_id:
                    continue  # Skip this object if it doesn't match

                objPath = os.path.join(col_path, obj)
                metadataPath = os.path.join(objPath, "metadata.yml")

                if not os.path.isfile(metadataPath):
                    print(f"Metadata file not found: {metadataPath}")
                    continue

                thumbnail_path = os.path.join(objPath, 'thumbnail.jpg')

                if not os.path.isfile(thumbnail_path) or force:

                    print(f"Creating thumbnail for {objPath}...")

                    #try:
                    with open(metadataPath, 'r', encoding='utf-8') as file:
                        metadata = yaml.safe_load(file)

                    if not metadata.get('resource_type') == "Audio":
                        image_order = ["jpg", "png"]
                        for format_ext in image_order:
                            image_dir = os.path.join(objPath, format_ext)
                            if os.path.isdir(image_dir) and len(os.listdir(image_dir)) > 0:
                                image_path = os.path.join(image_dir, os.listdir(image_dir)[0])
                                subprocess.run([
                                        'convert', image_path,
                                        '-resize',
                                        '300x300',
                                        thumbnail_path
                                    ])
                                break

                    else:
                        print ("copying audio thumb...")
                        shutil.copy2(os.path.join(root, "thumbnail.jpg"), thumbnail_path)                        

                    #except Exception as e:
                    #    with open(log_file, "a") as log:
                    #        log.write(f"\nERROR loading thumbnail for {objPath}\n")
                    #        log.write(traceback.format_exc())
                    #        time.sleep(5)




if __name__ == "__main__":
    # Check for command-line arguments
    print (sys.argv)
    if len(sys.argv) > 2:
        collection_id = sys.argv[1]
        object_id_arg = sys.argv[2].split(",")
        force_flag = len(sys.argv) > 2 and sys.argv[2].lower() == "-f"
        make_thumb(collection_id=collection_id, object_id=object_id_arg, force=force_flag)
    elif len(sys.argv) > 1:
        collection_ids = sys.argv[1].split(',')
        force_flag = len(sys.argv) > 2 and sys.argv[2].lower() == "-f"
        
        for collection_id in collection_ids:
            print(f"Processing collection: {collection_id}")
            make_thumb(collection_id=collection_id, force=force_flag)
    else:
        make_thumb()
