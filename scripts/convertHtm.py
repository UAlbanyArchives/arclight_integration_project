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


def convert_htm_to_pdf(input_file, output_file):
    # Get the output directory from the output file path
    output_dir = os.path.dirname(output_file)

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Construct the command as a list
    command = [
        "Chrome.exe",
        "--headless",
        "--run-all-compositor-stages-before-draw",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={output_file}",
        input_file
    ]
    
    # Print the command for debugging
    print("Running command:", " ".join(command))
    
    try:
        # Run the command
        subprocess.run(command, check=True)
        print(f"Conversion successful: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")
    except FileNotFoundError:
        print("LibreOffice is not installed or not in the system PATH.")


def convert_txt(collection_id=None, object_id=None, force=None):
    for col in os.listdir(root):
        col_path = os.path.join(root, col)


        # Check if collection_id is provided and matches the current collection
        if collection_id and collection_id != col:
            continue  # Skip this collection if it doesn't match


        if os.path.isdir(col_path):
            for obj in os.listdir(col_path):
                if object_id and object_id != obj:
                    continue  # Skip this object if it doesn't match

                objPath = os.path.join(col_path, obj)
                metadataPath = os.path.join(objPath, "metadata.yml")

                if not os.path.isfile(metadataPath):
                    print(f"Metadata file not found: {metadataPath}")
                    continue


                with open(metadataPath, 'r', encoding='utf-8') as file:
                    metadata = yaml.safe_load(file)

                out_dir = os.path.join(objPath, "pdf")
                if not os.path.isdir(out_dir) or force:
                    if not os.path.isdir(out_dir):
                        os.mkdir(out_dir)

                    file_order = ["htm"]
                    for format_ext in file_order:
                        file_dir = os.path.join(objPath, format_ext)
                        if os.path.isdir(file_dir) and len(os.listdir(file_dir)) > 0:
                            for file in os.listdir(file_dir):
                                #print(file)
                                if "Thumbs.db" in file:
                                    continue

                                input_file = os.path.join(file_dir, file)
                                output_image = os.path.join(out_dir, os.path.splitext(file)[0] + ".pdf")
                                
                                convert_htm_to_pdf(input_file, output_image)

                            
                            break




if __name__ == "__main__":
    # Check for command-line arguments
    print (sys.argv)
    if len(sys.argv) > 2:
        collection_id = sys.argv[1]
        object_id_arg = sys.argv[2]
        force_flag = len(sys.argv) > 3 and sys.argv[3].lower() == "-f"
        convert_txt(collection_id=collection_id, object_id=object_id_arg, force=force_flag)
    elif len(sys.argv) > 1:
        collection_ids = sys.argv[1].split(',')
        force_flag = len(sys.argv) > 2 and sys.argv[2].lower() == "-f"
        
        for collection_id in collection_ids:
            print(f"Processing collection: {collection_id}")
            convert_txt(collection_id=collection_id, force=force_flag)
    else:
        convert_txt()
