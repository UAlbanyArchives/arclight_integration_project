import os
import yaml
import sys
import shutil

if os.name == "nt":
    root = "\\\\Lincoln\\Library\\SPE_DAO"
    preservation_storage = "\\\\Lincoln\\Masters\\Archives\\AIP"
else:
    root = "/media/Library/SPE_DAO"


def copy_files(collection_id=None):
    for col in os.listdir(root):
        col_path = os.path.join(root, col)

        # Check if collection_id is provided and matches the current collection
        if collection_id and collection_id not in col:
            continue  # Skip this collection if it doesn't match

        if os.path.isdir(col_path):
            for obj in os.listdir(col_path):
                objPath = os.path.join(col_path, obj)
                metadataPath = os.path.join(objPath, "metadata.yml")

                with open(metadataPath, 'r') as file:
                    metadata = yaml.safe_load(file)

                for file_set_id in metadata["file_sets"]:
                    filename = metadata["file_sets"][file_set_id]
                    file_root, file_extension = os.path.splitext(filename)
                    file_extension = file_extension[1:].lower()

                    # set original file
                    if file_set_id == metadata["representative_id"]:
                        metadata["original_file"] = filename
                        metadata["original_format"] = file_extension

                original_file = os.path.join(objPath, file_extension, filename)
                if os.path.isfile(original_file) and os.path.getsize(original_file) == 0:
                    # file is empty
                    accession = metadata["accession"]
                    derivativesPath = os.path.join(preservation_storage, col, accession, "data", "derivatives")
                    mastersPath = os.path.join(preservation_storage, col, accession, "data", "masters")
                    matches = []
                    for root_dir, dirs, files in os.walk(mastersPath):
                        for file in files:
                            if file == filename:
                                #match!
                                print ("found match!")
                                matches.append(os.path.join(root_dir, file))
                    if len(matches) == 1:
                        print ("found a single match")
                        os.remove(original_file)
                        shutil.copy2(matches[0], original_file)
                        print(f"File copied from {matches[0]} to {original_file} successfully.")
                    elif len(matches) == 0:
                        for root_dir, dirs, files in os.walk(mastersPath):
                            for file in files:
                                if file == filename:
                                    #match!
                                    print ("found match!")
                                    matches.append(os.path.join(root_dir, file))
                        if len(matches) == 1:
                            print ("found a single match")
                            os.remove(original_file)
                            shutil.copy2(matches[0], original_file)
                            print(f"File copied from {matches[0]} to {original_file} successfully.")

               # write back to metadata.yml
                with open(metadataPath, 'w') as yml_file:
                    yaml.dump(metadata, yml_file)




if __name__ == "__main__":
    # Check for command-line arguments
    if len(sys.argv) > 1:
        collection_id_arg = sys.argv[1]
        copy_files(collection_id=collection_id_arg)
    else:
        copy_files()