import os, re, sys
import yaml
from subprocess import Popen, PIPE
#from pypdf import PdfReader, PdfWriter

root_path = "\\\\Lincoln\\Library\\SPE_DAO" if os.name == "nt" else "/media/Library/SPE_DAO"
obj_path = os.path.join(root_path, "examples", "apap362", "kjo56png0e")

#exts = []
#exts = ['.pdf', '.tmp', '.lck', '.shtml', '.doc', '.gif', '.db']

exts = ['.docx', '.pdf', '.doc', '.wbk', '.txt', '.eml', '.pub', '.xlsx', '.xls', '.shtml']

for root, dirs, files in os.walk(obj_path):
    for file in files:
        if file.startswith("."):
            continue
        filename, ext = os.path.splitext(file)
        if not ext.lower() in exts:
            exts.append(ext.lower())
            continue
        if ext.lower() == ".wbk":
            print (root)

        """
        in_path = os.path.join(root, file)
        out_path = os.path.join(root, filename + ".pdf")
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
        """    
print (exts)