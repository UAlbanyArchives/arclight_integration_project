import os
import sys
import pymupdf
import traceback

if os.name == "nt":
    root = "\\\\Lincoln\\Library\\SPE_DAO"
else:
    root = "/media/Library/SPE_DAO"

log_path = "/media/Library/ESPYderivatives/export_logs/text"

def extract_text(collection_id=None, object_id=None):
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

                    objPath = os.path.join(col_path, obj)
                    print(f"Reading {obj}...")
                    metadataPath = os.path.join(objPath, "metadata.yml")

                    pdfPath = os.path.join(objPath, "pdf")
                    if os.path.isdir(pdfPath):

                        pdfCount = 0
                        content_txt_path = os.path.join(objPath, "content.txt")
                        
                        with open(content_txt_path, 'w', encoding='utf-8') as content_file:
                            for pdf in os.listdir(pdfPath):
                                filename = os.path.splitext(pdf)[0]
                                pdfFilePath = os.path.join(pdfPath, pdf)
                                output_path = os.path.join(objPath, "txt")
                                if not os.path.isdir(output_path):
                                    os.mkdir(output_path)

                                if os.path.isfile(pdfFilePath) and pdf.lower().endswith(".pdf"):
                                    pdfCount += 1

                                    with pymupdf.open(pdfFilePath) as pdf:
                                        # Loop through each page
                                        for page_num in range(len(pdf)):
                                            page = pdf[page_num]
                                            text = page.get_text()  # Extract the text

                                            # Save each page to a separate file
                                            out_file = f"{filename}-{page_num + 1}.txt"
                                            page_txt_path = os.path.join(output_path, out_file)
                                            with open(page_txt_path, 'w', encoding='utf-8') as page_file:
                                                page_file.write(text)
                                                print(f"\tText extracted and saved to {out_file}")

                                            # Append page text to the combined content file
                                            content_file.write(text)

                        print(f"\tCombined text saved to {content_txt_path}")

        except Exception as e:
            with open(log_file, "a") as log:
                log.write(f"\nERROR extracting text for {objPath}\n")
                log.write(traceback.format_exc())
        



if __name__ == "__main__":
    # Check for command-line arguments
    if len(sys.argv) > 2:
        collection_id_arg = sys.argv[1]
        object_id_arg = sys.argv[2].split(",")
        extract_text(collection_id=collection_id_arg, object_id=object_id_arg)
    elif len(sys.argv) > 1:
        collection_id_arg = sys.argv[1]
        extract_text(collection_id=collection_id_arg)
    else:
        extract_text()
