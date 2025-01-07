import os, re, sys
import yaml
from subprocess import Popen, PIPE
from pypdf import PdfReader, PdfWriter
import traceback

if os.name == "nt":
    root = "\\\\Lincoln\\Library\\SPE_DAO"
else:
    root = "/media/Library/SPE_DAO"

log_path = "/media/Library/ESPYderivatives/export_logs/images"

def extract_from_pdf(log_file, filepath, convertDir, outfile):
    pdfimagesCmd = ["pdftoppm", filepath, outfile, "-jpeg"]
    #pdfimagesCmd =["pdfimages", "-all", filepath, outfile]
    print("Running command:", " ".join(pdfimagesCmd))
    
    with Popen(pdfimagesCmd, stdout=PIPE, stderr=PIPE, text=True) as process:
        stdout, stderr = process.communicate()  # Collect both outputs
        
        # Print or log stdout
        if stdout:
            print(stdout)
        
        # Check return code
        if process.returncode != 0:
            print(f"Error: Command failed with exit code {process.returncode}")
            # Print or log stderr
            if stderr:
                print(stderr, end='')
                with open(log_file, "a") as log:
                    log.write(stderr)

def extract_images(collection_id=None, object_id=None):
    for col in os.listdir(root):
        col_path = os.path.join(root, col)

        # Check if collection_id is provided and matches the current collection
        if collection_id and collection_id not in col:
            continue  # Skip this collection if it doesn't match

        log_file = os.path.join(log_path, collection_id + ".log")

        try:

            if os.path.isdir(col_path):
                for obj in os.listdir(col_path):
                    if object_id and obj not in object_id:
                        continue  # Skip this object if it doesn't match

                    print (f"Reading {obj}...")
                    objPath = os.path.join(col_path, obj)
                    metadataPath = os.path.join(objPath, "metadata.yml")
                    pdfPath = os.path.join(objPath, "pdf")
                    if os.path.exists(pdfPath):
                        jpgPath = os.path.join(objPath, "jpg")

                        pdfCount = 0
                        for pdf in os.listdir(pdfPath):
                            pdfFilePath = os.path.join(pdfPath, pdf)
                            if os.path.isfile(pdfFilePath) and pdf.lower().endswith(".pdf"):
                                pdfCount += 1

                        convertDir = jpgPath
                        if not os.path.isdir(convertDir):
                            os.mkdir(convertDir)

                        if pdfCount != 1:
                            #with open(log_file, "a") as log:
                            #    log.write(f"\nWARN: found {pdfCount} PDF files for {col}/{obj}\n")
                            #raise Exception(f"ERROR: found {pdfCount} PDF files for {col}/{obj}")
                            with open(metadataPath, 'r', encoding='utf-8') as file:
                                metadata = yaml.safe_load(file)

                            pdfNum = 0
                            for file_set in metadata["file_sets"]:
                                pdfNum += 1
                                pdf = os.path.splitext(metadata["file_sets"][file_set])[0] + ".pdf"
                                formatted_number = str(pdfNum).zfill(4)
                                filepath = os.path.join(pdfPath, pdf)
                                filename = f"{formatted_number}_{os.path.splitext(pdf)[0]}"
                                print (filename)
                                
                                print (f"Processing {pdf} from {col}/{obj}...")

                                outfile = os.path.join(convertDir, filename)

                                extract_from_pdf(log_file, filepath, convertDir, outfile)
                        else:
                            for pdf in os.listdir(pdfPath):
                                filepath = os.path.join(pdfPath, pdf)
                                filename = os.path.splitext(pdf)[0]

                                print (f"Processing {pdf} from {col}/{obj}...")

                                outfile = os.path.join(convertDir, filename)

                                extract_from_pdf(log_file, filepath, convertDir, outfile)

        except Exception as e:
            print (traceback.format_exc())
            with open(log_file, "a") as log:
                log.write(f"\nERROR extracting images for {objPath}\n")
                log.write(traceback.format_exc())

if __name__ == "__main__":
    # Check for command-line arguments
    if len(sys.argv) > 2:
        collection_id_arg = sys.argv[1]
        object_id_arg = sys.argv[2].split(",")
        extract_images(collection_id=collection_id_arg, object_id=object_id_arg)
    elif len(sys.argv) > 1:
        collection_ids = sys.argv[1].split(',')
        for collection_id in collection_ids:
            print(f"Processing collection: {collection_id}")
            extract_images(collection_id=collection_id)
    else:
        extract_images()
