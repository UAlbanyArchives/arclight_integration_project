import os
import yaml
import time
import sys
import traceback
import shutil
import subprocess

if os.name == "nt":
    root = "\\\\Lincoln\\Library\\SPE_DAO"
else:
    root = "/media/Library/SPE_DAO"

def check_encoding(filepath):
    """Check the file encoding using `file -i`."""
    try:
        result = subprocess.run(['file', '-i', filepath], capture_output=True, text=True)
        result.check_returncode()
        encoding_line = result.stdout
        # Parse encoding from the output
        encoding = encoding_line.split("charset=")[-1].strip()
        return encoding
    except Exception as e:
        print(f"Error checking encoding: {e}")
        return None

def convert_to_utf8(original_file, utf8_file):
    """Convert a file to UTF-8 encoding using `iconv`."""
    try:
        subprocess.run(['iconv', '-f', 'ISO-8859-1', '-t', 'UTF-8', original_file, '-o', utf8_file], check=True)
        print(f"Converted {original_file} to UTF-8 as {utf8_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")

def create_image(text_file, output_image):
    """Create an image from the text file using ImageMagick."""
    try:
        subprocess.run([
            'convert', 
            '-background', 'white', 
            '-fill', 'black', 
            '-font', 'DejaVu-Sans', 
            '-pointsize', '20', 
            '-size', '800x', 
            f'caption:@{text_file}', 
            '-bordercolor', 'white', 
            '-border', '125', 
            output_image
        ], check=True)
        print(f"Image created: {output_image}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating image: {e}")

def convert_txt(collection_id=None, object_id=None, force=None):
    for col in os.listdir(root):
        col_path = os.path.join(root, col)


        # Check if collection_id is provided and matches the current collection
        if collection_id and collection_id != col:
            continue  # Skip this collection if it doesn't match


        if os.path.isdir(col_path):
            for obj in os.listdir(col_path):
                if object_id and object_id != obj:
                    continue  # Skip this object if it doesn't match

                objPath = os.path.join(col_path, obj)
                metadataPath = os.path.join(objPath, "metadata.yml")

                if not os.path.isfile(metadataPath):
                    print(f"Metadata file not found: {metadataPath}")
                    continue


                with open(metadataPath, 'r', encoding='utf-8') as file:
                    metadata = yaml.safe_load(file)

                out_dir = os.path.join(objPath, "png")
                if not os.path.isdir(out_dir) or force:
                    if not os.path.isdir(out_dir):
                        os.mkdir(out_dir)

                    file_order = ["txt"]
                    for format_ext in file_order:
                        file_dir = os.path.join(objPath, format_ext)
                        if os.path.isdir(file_dir) and len(os.listdir(file_dir)) > 0:
                            for file in os.listdir(file_dir):
                                #print(file)
                                if "Thumbs.db" in file:
                                    continue

                                input_file = os.path.join(file_dir, file)
                                output_image = os.path.join(out_dir, os.path.splitext(file)[0] + ".png")
                                encoding = check_encoding(input_file)
                                if not encoding:
                                    print("Unable to determine encoding.")
                                if encoding.lower() != 'utf-8':
                                    utf8_file = f"{os.path.splitext(input_file)[0]}_utf8.txt"
                                    convert_to_utf8(input_file, utf8_file)
                                    text_file_to_use = utf8_file
                                else:
                                    text_file_to_use = input_file

                                create_image(text_file_to_use, output_image)

                                # Cleanup: Remove temporary UTF-8 file if created
                                if text_file_to_use != input_file and os.path.exists(text_file_to_use):
                                    os.remove(text_file_to_use)
                                    print(f"Temporary file {text_file_to_use} removed.")
                            
                            break




if __name__ == "__main__":
    # Check for command-line arguments
    print (sys.argv)
    if len(sys.argv) > 2:
        collection_id = sys.argv[1]
        object_id_arg = sys.argv[2]
        force_flag = len(sys.argv) > 3 and sys.argv[3].lower() == "-f"
        convert_txt(collection_id=collection_id, object_id=object_id_arg, force=force_flag)
    elif len(sys.argv) > 1:
        collection_ids = sys.argv[1].split(',')
        force_flag = len(sys.argv) > 2 and sys.argv[2].lower() == "-f"
        
        for collection_id in collection_ids:
            print(f"Processing collection: {collection_id}")
            convert_txt(collection_id=collection_id, force=force_flag)
    else:
        convert_txt()
