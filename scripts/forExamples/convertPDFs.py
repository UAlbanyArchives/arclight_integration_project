import os, re, sys
import yaml
import subprocess
from subprocess import Popen, PIPE
#from pypdf import PdfReader, PdfWriter

root_path = "\\\\Lincoln\\Library\\SPE_DAO" if os.name == "nt" else "/media/Library/SPE_DAO"
obj_path = os.path.join(root_path, "apap362", "kjo56png0e")

exts = []
#exts = ['.pdf', '.tmp', '.lck', '.shtml', '.doc', '.gif', '.db']

#exts = ['.docx', '.pdf', '.doc', '.wbk', '.txt', '.eml', '.pub', '.xlsx', '.xls', '.shtml']


for root, dirs, files in os.walk(obj_path):
    for file in files:
        if file.startswith("."):
            continue
        filepath = os.path.join(root, file)
        filename, ext = os.path.splitext(file)
        if not ext.lower() in exts:
            exts.append(ext.lower())
            continue
        if ext.lower() == ".pdf":
            alt_folder = os.path.join(root, f"alt-{filename}")
            if os.path.isdir(alt_folder):
                context_text = os.path.join(alt_folder, "content.txt")
                with open(context_text, "w", encoding="utf-8") as content_file:
                    for jpg in os.listdir(alt_folder):
                        jpg_filename, jpg_ext = os.path.splitext(jpg)
                        if jpg_ext == ".jpg":

                            # Define the full path for input and output files
                            input_path = os.path.join(alt_folder, jpg)
                            out_path = os.path.join(alt_folder, jpg_filename)
                            txt_output_file = os.path.join(alt_folder, jpg_filename + ".txt")
                            
                            # Run Tesseract to create both HOCR and TXT output
                            subprocess.run([
                                'tesseract', input_path, out_path, 
                                '-c', 'tessedit_create_hocr=1',
                                '-c', 'tessedit_create_txt=1'
                            ])


                            # Append the contents of the individual .txt file to content.txt
                            with open(txt_output_file, "r", encoding="utf-8") as txt_file:
                                content = txt_file.read()
                                content_file.write(content)

                            print(f"\tProcessed OCR for {filename}")

                    print (f"\tConverting {jpg}...")
                    jpgFilepath = os.path.join(alt_folder, jpg)
                    outfile = os.path.join(alt_folder, f"{jpg_filename}.tiff")

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

            """
            if os.path.exists(alt_folder):
                pass
                #raise Exception(f"{alt_folder} already exists")
            else:
                os.mkdir(alt_folder)


                print (f"Processing {file} from {root}...")

                outfile = os.path.join(alt_folder, filename)

                pdfimagesCmd = ["pdftoppm", filepath, outfile, "-jpeg"]
                #pdfimagesCmd =["pdfimages", "-all", filepath, outfile]
                #print (pdfimagesCmd)
                with Popen(pdfimagesCmd, stdout=PIPE, stderr=PIPE, text=True) as process:
                    for line in process.stdout:
                        print(line, end='')
                    for line in process.stderr:
                        print(line, end='')
                    process.wait() 
            """
#print (exts)