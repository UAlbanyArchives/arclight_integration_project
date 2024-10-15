import os
import sys
import subprocess
from utils import get_latest_version

if len(sys.argv) != 2:
    print("Usage: python tesseract.py <input_dir>")
    sys.exit(1)
else:
    colID = sys.argv[1]

if os.name == "nt":
    root = "\\\\Lincoln\\Library\\SPE_DAO"
else:
    root = "/media/Library/SPE_DAO"

colDir = os.path.join(root, colID)
if not os.path.isdir(colDir):
    raise Exception(f"ERROR: {colDir} does not exist.")

# Loop through each .jpg file in the input directory
for obj in os.listdir(colDir):
    objDir = os.path.join(colDir, obj)
    jpgDir = os.path.join(get_latest_version(objDir), "jpg")
    ocrDir = os.path.join(get_latest_version(objDir), "ocr")

    # Ensure the output directory exists
    if not os.path.isdir(ocrDir):
        os.mkdir(ocrDir)

    print (f"Processing {colID}/{obj}...")

    for filename in os.listdir(jpgDir):
        if filename.endswith('.jpg'):
            # Remove the .jpg extension to get the base name
            base_name = os.path.splitext(filename)[0]
            
            # Define the full path for input and output files
            input_path = os.path.join(jpgDir, filename)
            output_path = os.path.join(ocrDir, base_name)
            
            # Run the Tesseract command to create HOCR output
            subprocess.run(['tesseract', input_path, output_path, '-c', 'tessedit_create_hocr=1'])
            
            print(f"\tProcessed jpg/{filename} to ocr/{base_name}.hocr")
