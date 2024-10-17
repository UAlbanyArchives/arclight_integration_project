import os, re, sys
import yaml
from subprocess import Popen, PIPE
from pypdf import PdfReader, PdfWriter

if os.name == "nt":
    root = "\\\\Lincoln\\Library\\SPE_DAO"
else:
    root = "/media/Library/SPE_DAO"

def extract_images(collection_id=None):
    for col in os.listdir(root):
        col_path = os.path.join(root, col)

        # Check if collection_id is provided and matches the current collection
        if collection_id and collection_id not in col:
            continue  # Skip this collection if it doesn't match

        if os.path.isdir(col_path):
            for obj in os.listdir(col_path):
                objPath = os.path.join(col_path, obj, "v1")
                metadataPath = os.path.join(objPath, "metadata.yml")
                pdfPath = os.path.join(objPath, "pdf")
                if os.path.exists(pdfPath):
                    jpgPath = os.path.join(objPath, "jpg")

                    pdfCount = 0
                    for pdf in os.listdir(pdfPath):
                        pdfFilePath = os.path.join(pdfPath, pdf)
                        if os.path.isfile(pdfFilePath) and pdf.lower().endswith(".pdf"):
                            pdfCount += 1

                    if pdfCount != 1:
                        raise Exception(f"ERROR: found {pdfCount} PDF files for {col}/{obj}")
                    else:
                        for pdf in os.listdir(pdfPath):
                            filepath = os.path.join(pdfPath, pdf)
                            filename = os.path.splitext(pdf)[0]
                            #convertDir = os.path.join(jpgPath, filename)
                            convertDir = jpgPath

                            print (f"Processing {pdf} from {col}/{obj}...")

                            if not os.path.isdir(convertDir):
                                os.mkdir(convertDir)
                            outfile = os.path.join(convertDir, filename)

                            pdfimagesCmd = ["pdftoppm", filepath, outfile, "-jpeg"]
                            pdfimages = Popen(pdfimagesCmd, stdout=PIPE, stderr=PIPE)
                            stdout, stderr = pdfimages.communicate()
                            

if __name__ == "__main__":
    # Check for command-line arguments
    if len(sys.argv) > 1:
        collection_id_arg = sys.argv[1]
        extract_images(collection_id=collection_id_arg)
    else:
        extract_images()
