import os
import sys
import time
import subprocess
import traceback
import yaml

if os.name == "nt":
    root = "\\\\Lincoln\\Library\\SPE_DAO"
else:
    root = "/media/Library/SPE_DAO"

log_path = "/media/Library/ESPYderivatives/export_logs/text"

def run_tesseract(collection_id=None, object_id=None, only_docs=False):
    start_time = time.time()

    colDir = os.path.join(root, collection_id)
    if not os.path.isdir(colDir):
        raise Exception(f"ERROR: {colDir} does not exist.")

    log_file = os.path.join(log_path, collection_id + ".log")

    try:

        for obj in os.listdir(colDir):
            if object_id and obj not in object_id:
                continue  # Skip this object if it doesn't match

            objDir = os.path.join(colDir, obj)
            jpgDir = os.path.join(objDir, "jpg")
            ocrDir = os.path.join(objDir, "hocr")
            txtDir = os.path.join(objDir, "txt")
            metadataPath = os.path.join(objDir, "metadata.yml")

            if only_docs:
                if not os.path.isfile(metadataPath):
                    print(f"Metadata file not found: {metadataPath}")
                    continue
                with open(metadataPath, 'r', encoding='utf-8') as file:
                    metadata = yaml.safe_load(file)
                    if not metadata.get('resource_type') == "Document":
                        print(f"\tSkipping non-Document...")
                        continue

            # Ensure the output directories exist
            if not os.path.isdir(ocrDir):
                os.mkdir(ocrDir)
            if not os.path.isdir(txtDir):
                os.mkdir(txtDir)

            print (f"Processing {collection_id}/{obj}...")

            if not os.path.isdir(jpgDir):
                # Try tiffs?
                jpgDir = os.path.join(objDir, "tif")
                #jpgDir = os.path.join(objDir, "ptif")
            if not os.path.isdir(jpgDir):
                # Try pngs?
                jpgDir = os.path.join(objDir, "png")
            if not os.path.isdir(jpgDir):
                print (f"ERROR: Could not find jpg or ptif folder in {objDir}.")
            else:
                # Create a content.txt file that will aggregate all text files
                content_file_path = os.path.join(objDir, "content.txt")
                with open(content_file_path, "w", encoding="utf-8") as content_file:

                    for filename in os.listdir(jpgDir):
                        if filename.endswith('.jpg') or filename.endswith('.ptif') or filename.endswith('.png'):
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

                            generated_txt_path = ocr_output_path + ".txt"

                            # Append the contents of the individual .txt file to content.txt
                            with open(generated_txt_path, "r", encoding="utf-8") as txt_file:
                                content = txt_file.read()
                                content_file.write(content)

                            # Move the generated .txt file to the txt directory
                            if os.path.exists(generated_txt_path):
                                if not os.path.isfile(txt_output_path + ".txt"):
                                    os.rename(generated_txt_path, txt_output_path + ".txt")
                                else:
                                    os.remove(generated_txt_path)

                            print(f"\tProcessed {filename} to hocr/{base_name}.hocr and txt/{base_name}.txt")

    except Exception as e:
        with open(log_file, "a") as log:
            log.write(f"\nERROR reading text for {objDir}\n")
            log.write(traceback.format_exc())

    # End time
    end_time = time.time()

    # Calculate elapsed time
    elapsed_time = end_time - start_time
    print(f"\nProcessing completed in {elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    # Check for command-line arguments
    if len(sys.argv) > 2:
        collection_id_arg = sys.argv[1]
        object_id_arg = sys.argv[2].split(",")
        if isinstance(object_id_arg, str) and object_id_arg.lower() == "only_docs":
            run_tesseract(collection_id=collection_id_arg, only_docs=True)
        else:
            run_tesseract(collection_id=collection_id_arg, object_id=object_id_arg)
    elif len(sys.argv) > 1:
        collection_ids = sys.argv[1].split(',')
        for collection_id in collection_ids:
            print(f"Processing collection: {collection_id}")
            run_tesseract(collection_id=collection_id)
    else:
        run_tesseract()
