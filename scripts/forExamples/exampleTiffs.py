import os, re, sys
import yaml
import pyvips
from subprocess import Popen, PIPE
from pypdf import PdfReader, PdfWriter

root_path = "\\\\Lincoln\\Library\\SPE_DAO" if os.name == "nt" else "/media/Library/SPE_DAO"
obj_path = os.path.join(root_path, "apap362", "kjo56png0e")

for root, dirs, files in os.walk(obj_path):
    for file in files:
        if file.startswith("."):
            continue
        if not file.lower().endswith(".jpg"):
            continue
        filename, ext = os.path.splitext(file)
        in_path = os.path.join(root, file)
        out_path = os.path.join(root, filename + ".tiff")
        print (f"\tConverting {file}...")

        vipsCmd = [
            "vips", "tiffsave",
            in_path, out_path,
            "--tile",
            "--pyramid",
            "--compression=jpeg",
            "--Q=90"
        ]
        #print (vipsCmd)
        vips = Popen(vipsCmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = vips.communicate()            
