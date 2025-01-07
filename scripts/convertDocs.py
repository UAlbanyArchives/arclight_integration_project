import os
import yaml
import time
import sys
import traceback
import shutil
import subprocess
import pandas as pd

if os.name == "nt":
    root = "\\\\Lincoln\\Library\\SPE_DAO"
else:
    root = "/media/Library/SPE_DAO"


def csv_to_pdf(input_file, output_file):
    # Get the output directory from the output file path
    output_dir = os.path.dirname(output_file)
    output_html = os.path.join(output_dir, os.path.splitext(os.path.basename(output_file))[0] + ".html")

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    df = pd.read_csv(input_file)
    df.to_html(output_html, index=False)

    # Construct the command as a list
    command = [
        "wkhtmltopdf",
        "--orientation",
        "Landscape",
        output_html,
        output_file,
    ]
    
    # Print the command for debugging
    print("Running command:", " ".join(command))
    
    try:
        # Run the command
        subprocess.run(command, check=True)
        print(f"Conversion successful: {output_file}")
        os.remove(output_html)
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")
    except FileNotFoundError:
        print("wkhtmltopdf is not installed or not in the system PATH.")

def convert_rtf_to_pdf(input_file, output_file):
    # Get the output directory from the output file path
    output_dir = os.path.dirname(output_file)

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Construct the command as a list
    command = [
        "libreoffice",
        "--headless",
        "--convert-to",
        "pdf",
        input_file,
        "--outdir",
        output_dir,
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

def convert_docs(collection_id=None, object_id=None, force=None):
    for col in os.listdir(root):
        col_path = os.path.join(root, col)


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

                with open(metadataPath, 'r', encoding='utf-8') as file:
                    metadata = yaml.safe_load(file)

                out_dir = os.path.join(objPath, "pdf")
                if not os.path.isdir(out_dir) or force:
                    if not os.path.isdir(out_dir):
                        os.mkdir(out_dir)

                    file_order = ["doc", "rtf", "docx", "pps", "txt", "docx", "csv"]
                    for format_ext in file_order:
                        file_dir = os.path.join(objPath, format_ext)
                        if os.path.isdir(file_dir) and len(os.listdir(file_dir)) > 0:
                            for file in os.listdir(file_dir):
                                #print(file)
                                if file == "Thumbs.db":
                                    continue

                                input_file = os.path.join(file_dir, file)
                                output_file = os.path.join(out_dir, os.path.splitext(file)[0] + ".pdf")
                                if input_file.lower().endswith(".csv"):
                                    csv_to_pdf(input_file, output_file)   
                                else:
                                    convert_rtf_to_pdf(input_file, output_file)       
                                                      




if __name__ == "__main__":
    # Check for command-line arguments
    print (sys.argv)
    if len(sys.argv) > 2:
        collection_id = sys.argv[1]
        object_id_arg = sys.argv[2].split(",")
        force_flag = len(sys.argv) > 3 and sys.argv[3].lower() == "-f"
        convert_docs(collection_id=collection_id, object_id=object_id_arg, force=force_flag)
    elif len(sys.argv) > 1:
        collection_ids = sys.argv[1].split(',')
        force_flag = len(sys.argv) > 2 and sys.argv[2].lower() == "-f"
        
        for collection_id in collection_ids:
            print(f"Processing collection: {collection_id}")
            convert_docs(collection_id=collection_id, force=force_flag)
    else:
        convert_docs()
