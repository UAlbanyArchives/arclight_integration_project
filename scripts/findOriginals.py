import os
import sys
import yaml
import shutil

if os.name == "nt":
    root = "\\\\Lincoln\\Library\\SPE_DAO"
    storage = "\\\\Lincoln\\Masters\\Archives\\AIP"
else:
    root = "/media/Library/SPE_DAO"
    storage = "/media/Masters/Archives/AIP"

def find_originals(collection_id=None, object_id=None):
    for col in os.listdir(root):
        col_path = os.path.join(root, col)

        # Check if collection_id is provided and matches the current collection
        if collection_id and collection_id not in col:
            continue  # Skip this collection if it doesn't match

        if os.path.isdir(col_path):
            for obj in os.listdir(col_path):
                if object_id and object_id not in obj:
                    continue  # Skip this object if it doesn't match

                objPath = os.path.join(col_path, obj)
                metadataPath = os.path.join(objPath, "metadata.yml")
                pdfPath = os.path.join(objPath, "pdf")
                if os.path.isdir(pdfPath):
                    with open(metadataPath, 'r') as file:
                        metadata = yaml.safe_load(file)
                    preservation_package = metadata["preservation_package"]
                    preservation_path = os.path.join(storage, col, preservation_package)

                    if not os.path.isdir(preservation_path):
                        raise Exception(f"ERROR: accession package not found {preservation_path}")

                    for pdf in os.listdir(pdfPath):
                        pdfFile = os.path.join(pdfPath, pdf)
                        if pdf.lower().endswith(".pdf") and os.path.isfile(pdfFile):
                            filename = os.path.splitext(pdf)[0]
                            print (f"Looking for {pdf}...")

                            matches = []
                            for rootDir, dirs, files in os.walk(preservation_path):
                                for folder in dirs:
                                    if folder == filename:
                                        matches.append(os.path.join(rootDir, folder))
                            if len(matches) != 1:
                                raise Exception(f"ERROR: found {len(matches)} matches for {filename}.")
                            else:
                                ext = os.path.splitext(os.listdir(matches[0])[0])[1][1:]
                                outFolder = os.path.join(objPath, ext)
                                if not os.path.isdir(outFolder):
                                    os.mkdir(outFolder)
                                for file in os.listdir(matches[0]):
                                    copyFile = os.path.join(matches[0], file)
                                    print (f"\tCopying {copyFile} to {ext}...")
                                    shutil.copy2(copyFile, outFolder)             
                            

if __name__ == "__main__":
    # Check for command-line arguments
    if len(sys.argv) > 2:
        collection_id_arg = sys.argv[1]
        object_id_arg = sys.argv[2]
        find_originals(collection_id=collection_id_arg, object_id=object_id_arg)
    elif len(sys.argv) > 1:
        collection_id_arg = sys.argv[1]
        find_originals(collection_id=collection_id_arg)
    else:
        find_originals()
