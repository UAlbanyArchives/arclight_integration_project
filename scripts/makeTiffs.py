import os, re, sys
import yaml
import pyvips
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
                print (f"Reading {obj}...")
                objPath = os.path.join(col_path, obj, "v1")
                metadataPath = os.path.join(objPath, "metadata.yml")
                jpgPath = os.path.join(objPath, "jpg")
                if os.path.exists(jpgPath):
                    tiffPath = os.path.join(objPath, "tiff")
                    if not os.path.isdir(tiffPath):
                        os.mkdir(tiffPath)

                    for jpg in os.listdir(jpgPath):
                        print (f"\tConverting {jpg}...")
                        jpgFilepath = os.path.join(jpgPath, jpg)
                        filename = os.path.splitext(jpg)[0]
                        outfile = os.path.join(tiffPath, f"{filename}.tiff")

                        # Load image
                        #image = pyvips.Image.new_from_file(jpgFilepath)
                        # Save as pyramidal TIFF
                        #image.tiffsave(outfile, tile=True, pyramid=True, compression="jpeg", tile_width=256, tile_height=256, bigtiff=True)

                        vipsCmd = [
                            "vips", "tiffsave",
                            jpgFilepath, outfile,
                            "--tile",
                            "--pyramid",
                            "--compression=jpeg",
                            "--Q=90"
                        ]
                        #print (vipsCmd)
                        vips = Popen(vipsCmd, stdout=PIPE, stderr=PIPE)
                        stdout, stderr = vips.communicate()
                            

if __name__ == "__main__":
    # Check for command-line arguments
    if len(sys.argv) > 1:
        collection_id_arg = sys.argv[1]
        extract_images(collection_id=collection_id_arg)
    else:
        extract_images()
