import os
import sys
import pymupdf

if os.name == "nt":
    root = "\\\\Lincoln\\Library\\SPE_DAO"
else:
    root = "/media/Library/SPE_DAO"

def extract_text(collection_id=None):
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
                if os.path.isdir(pdfPath):

                    pdfCount = 0
                    for pdf in os.listdir(pdfPath):
                        pdfFilePath = os.path.join(pdfPath, pdf)
                        output_path = os.path.join(objPath, "txt")
                        if not os.path.isdir(output_path):
                            os.mkdir(output_path)
                        output_txt_path = os.path.join(output_path, os.path.splitext(pdf)[0] + ".txt")
                        if os.path.isfile(pdfFilePath) and pdf.lower().endswith(".pdf"):
                            pdfCount += 1

                            with pymupdf.open(pdfFilePath) as pdf:
                                with open(output_txt_path, 'w', encoding='utf-8') as txt_file:
                                    # Loop through each page
                                    for page_num in range(len(pdf)):
                                        page = pdf[page_num]
                                        text = page.get_text()  # Extract the text

                                        # Write the page number and text to the output file
                                        txt_file.write(f"Page {page_num + 1}\n")
                                        txt_file.write(text)
                                        txt_file.write("\n" + "-" * 80 + "\n")  # Separator for pages

                                print(f"Text extracted and saved to {output_txt_path}")




if __name__ == "__main__":
    # Check for command-line arguments
    if len(sys.argv) > 1:
        collection_id_arg = sys.argv[1]
        extract_text(collection_id=collection_id_arg)
    else:
        extract_text()
