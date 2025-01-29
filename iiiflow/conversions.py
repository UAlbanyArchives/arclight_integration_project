import os
import traceback
from subprocess import Popen, PIPE
from .utils import log_path

def pdf_to_jpgs(pdf_path, output_path=None, config_path="~/.iiiflow.yml"):
    """
    Extracts JPG images from PDF files using pdftoppm

    Args:
        pdf_path (str): The path to a PDF file.
        output_path (str): The path save export files (optional)
        config_path (str): Path to the configuration YAML file.
    """

    log_file_path = log_path(config_path)

    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"ERROR: PDF path {pdf_path} does not exist.")
    elif not pdf_path.lower().endswith(".pdf"):
        raise FileNotFoundError(f"ERROR: Invalid PDF file {pdf_path}.")
    else:
        pdf_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        if output_path is None:
            out_path = os.path.join(os.path.dirname(pdf_path), pdf_filename)
        else:
            out_path = os.path.join(output_path, pdf_filename)
        pdfimagesCmd = ["pdftoppm", pdf_path, out_path, "-jpeg"]
        #pdfimagesCmd =["pdfimages", "-all", filepath, outfile]
        print(f"Running command: {' '.join(pdfimagesCmd)}")
        
        try:
            with Popen(pdfimagesCmd, stdout=PIPE, stderr=PIPE, text=True) as process:
                stdout, stderr = process.communicate()
                
                # Print or log stdout
                if stdout:
                    print(stdout.decode("utf-8"))
                
                # Check return code
                if process.returncode != 0:
                    print(f"Error: Command failed with exit code {process.returncode}")
                    # Print or log stderr
                    if stderr:
                        print(stderr.decode("utf-8"), end='')
                        with open(log_file_path, "a") as log:
                            log.write(stderr.decode("utf-8"))
        except Exception as e:
            with open(log_file_path, "a") as log:
                log.write(f"\nERROR converting {pdf_path} images:\n")
                log.write(traceback.format_exc())
