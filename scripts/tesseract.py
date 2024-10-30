import os
import sys
import subprocess
from utils import get_latest_version


if os.name == "nt":
    root = "\\\\Lincoln\\Library\\SPE_DAO"
else:
    root = "/media/Library/SPE_DAO"

def run_tesseract(collection_id=None, object_id=None):

    colDir = os.path.join(root, collection_id)
    if not os.path.isdir(colDir):
        raise Exception(f"ERROR: {colDir} does not exist.")

    # Loop through each .jpg file in the input directory
    for obj in os.listdir(colDir):
        if object_id and object_id not in obj:
            continue  # Skip this object if it doesn't match

        versionDir = os.path.join(colDir, obj)
        objDir = os.path.join(versionDir, get_latest_version(versionDir))
        jpgDir = os.path.join(objDir, "jpg")
        ocrDir = os.path.join(objDir, "ocr")
        txtDir = os.path.join(objDir, "txt")

        # Ensure the output directories exist
        if not os.path.isdir(ocrDir):
            os.mkdir(ocrDir)
        if not os.path.isdir(txtDir):
            os.mkdir(txtDir)

        print (f"Processing {collection_id}/{obj}...")

        if not os.path.isdir(jpgDir):
            # Try tiffs?
            jpgDir = os.path.join(objDir, "tif")
        if not os.path.isdir(jpgDir):
            print (f"ERROR: Could not find jpg or tif folder in {objDir}.")
        else:
            # Create a content.txt file that will aggregate all text files
            content_file_path = os.path.join(objDir, "content.txt")
            with open(content_file_path, "w", encoding="utf-8") as content_file:

                for filename in os.listdir(jpgDir):
                    if filename.endswith('.jpg') or filename.endswith('.tif'):
                        # Remove the .jpg or .tif extension to get the base name
                        base_name = os.path.splitext(filename)[0]
                        
                        # Define the full path for input and output files
                        input_path = os.path.join(jpgDir, filename)
                        ocr_output_path = os.path.join(ocrDir, base_name)
                        txt_output_path = os.path.join(txtDir, base_name)
                        
                        # Run Tesseract to create both HOCR and TXT output
                        subprocess.run([
                            'tesseract', input_path, ocr_output_path, 
                            '-c', 'tessedit_create_hocr=1',
                            '-c', 'tessedit_create_txt=1'
                        ])

                        # Move the generated .txt file to the txt directory
                        generated_txt_path = ocr_output_path + ".txt"
                        if os.path.exists(generated_txt_path):
                            os.rename(generated_txt_path, txt_output_path + ".txt")

                            # Append the contents of the individual .txt file to content.txt
                            with open(txt_output_path + ".txt", "r", encoding="utf-8") as txt_file:
                                content = txt_file.read()
                                #content_file.write(f"\n\n--- {base_name}.txt ---\n\n")
                                content_file.write(content)

                        print(f"\tProcessed {filename} to ocr/{base_name}.hocr and txt/{base_name}.txt")

if __name__ == "__main__":
    # Check for command-line arguments
    if len(sys.argv) > 2:
        collection_id_arg = sys.argv[1]
        object_id_arg = sys.argv[2]
        run_tesseract(collection_id=collection_id_arg, object_id=object_id_arg)
    elif len(sys.argv) > 1:
        collection_id_arg = sys.argv[1]
        run_tesseract(collection_id=collection_id_arg)
    else:
        run_tesseract()
