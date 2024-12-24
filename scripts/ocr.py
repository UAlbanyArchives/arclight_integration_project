import os
import sys
import time
import traceback
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

if os.name == "nt":
    root = "\\\\Lincoln\\Library\\SPE_DAO"
else:
    root = "/media/Library/SPE_DAO"

log_path = "/media/Library/ESPYderivatives/export_logs/text"

def run_doctr(collection_id=None, object_id=None):
    start_time = time.time()
    # Load the OCR predictor model
    model = ocr_predictor(pretrained=True)

    colDir = os.path.join(root, collection_id)
    if not os.path.isdir(colDir):
        raise Exception(f"ERROR: {colDir} does not exist.")

    log_file = os.path.join(log_path, collection_id + ".log")

    try:
        for obj in os.listdir(colDir):
            if object_id and object_id not in obj:
                continue  # Skip this object if it doesn't match

            objDir = os.path.join(colDir, obj)
            jpgDir = os.path.join(objDir, "jpg")
            ocrDir = os.path.join(objDir, "hocr2")
            txtDir = os.path.join(objDir, "txt2")

            # Ensure the output directories exist
            if not os.path.isdir(ocrDir):
                os.mkdir(ocrDir)
            if not os.path.isdir(txtDir):
                os.mkdir(txtDir)

            print(f"Processing {collection_id}/{obj}...")

            if not os.path.isdir(jpgDir):
                jpgDir = os.path.join(objDir, "ptif")
            if not os.path.isdir(jpgDir):
                jpgDir = os.path.join(objDir, "png")
            if not os.path.isdir(jpgDir):
                print(f"ERROR: Could not find jpg or ptif folder in {objDir}.")
            else:
                # Create a content.txt file that will aggregate all text files
                content_file_path = os.path.join(objDir, "content2.txt")
                with open(content_file_path, "w", encoding="utf-8") as content_file:

                    for filename in os.listdir(jpgDir):
                        if filename.endswith('.jpg') or filename.endswith('.ptif') or filename.endswith('.png'):
                            base_name = os.path.splitext(filename)[0]
                            input_path = os.path.join(jpgDir, filename)
                            txt_output_path = os.path.join(txtDir, base_name + ".txt")
                            hocr_output_path = os.path.join(ocrDir, base_name + ".hocr")

                            #try:
                            # Load the image file
                            print (input_path)
                            doc = DocumentFile.from_images(input_path)
                            # Run OCR prediction
                            result = model(doc)

                            # Extract text from OCR result
                            full_text = ""
                            for page in result.pages:
                                for block in page.blocks:  # Iterate through blocks
                                    for line in block.lines:  # Iterate through lines within each block
                                        # Concatenate word values to form line text
                                        line_text = " ".join(word.value for word in line.words)
                                        full_text += line_text + "\n"
                            #print (full_text)


                            # Write plain text output
                            with open(txt_output_path, "w", encoding="utf-8") as txt_file:
                                txt_file.write(full_text)

                            # Optionally generate HOCR-like output (requires custom formatting)
                            # For now, we'll just save bounding boxes (if needed).
                            with open(hocr_output_path, "w", encoding="utf-8") as hocr_file:
                                for page in result.pages:
                                    for block in page.blocks:
                                        for line in block.lines:
                                            for word in line.words:
                                                hocr_file.write(f"{word.value}\t{word.geometry}\n")

                            # Append plain text to content.txt
                            with open(txt_output_path, "r", encoding="utf-8") as txt_file:
                                content = txt_file.read()
                                content_file.write(full_text)

                            print(f"\tProcessed {filename} to {txt_output_path} and {hocr_output_path}")

                            #except Exception as e:
                            #    print(f"Error processing {input_path}: {e}")
                            #    #with open(log_file, "a") as log:
                            #    #    log.write(f"\nERROR processing {input_path}\n")
                            #    #    log.write(traceback.format_exc())

    except Exception as e:
        print (e)
        #with open(log_file, "a") as log:
        #    log.write(f"\nERROR reading text for {objDir}\n")
        #    log.write(traceback.format_exc())

    # End time
    end_time = time.time()

    # Calculate elapsed time
    elapsed_time = end_time - start_time
    print(f"\nProcessing completed in {elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        collection_id_arg = sys.argv[1]
        object_id_arg = sys.argv[2]
        run_doctr(collection_id=collection_id_arg, object_id=object_id_arg)
    elif len(sys.argv) > 1:
        collection_id_arg = sys.argv[1]
        run_doctr(collection_id=collection_id_arg)
    else:
        run_doctr()
