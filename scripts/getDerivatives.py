import os
import yaml
import requests
import sys

if os.name == "nt":
    root = "\\\\Lincoln\\Library\\SPE_DAO"
else:
    root = "/media/Library/SPE_DAO"

root_url = 'https://archives.albany.edu/downloads/'

office_document_extensions = [
    "doc",   # Microsoft Word
    "docx",  # Microsoft Word (XML format)
    "xls",   # Microsoft Excel
    "xlsx",  # Microsoft Excel (XML format)
    "ppt",   # Microsoft PowerPoint
    "pptx",  # Microsoft PowerPoint (XML format)
    "odt",   # OpenDocument Text
    "ods",   # OpenDocument Spreadsheet
    "odp",   # OpenDocument Presentation
    #"pdf",   # Portable Document Format
    "rtf"    # Rich Text Format
]

video_file_extensions = [
    "mp4",   # MPEG-4 Video
    "mov",   # QuickTime Movie
    "avi",   # AVI Video
    "wmv",   # Windows Media Video
    "flv",   # Flash Video
    "mkv",   # Matroska Video
    "webm",  # WebM Video
    "mpeg",  # MPEG Video
    "mpg",   # MPEG Video
    "3gp",   # 3GPP Video
    "ogv",   # Ogg Video
    "m4v"    # MPEG-4 Video (variant)
]

audio_file_extensions = [
    "mp3",   # MP3 Audio
    "wav",   # Waveform Audio
    "aac",   # AAC Audio
    "flac",  # FLAC Audio
    "ogg",   # Ogg Vorbis Audio
    "m4a",   # MPEG-4 Audio
    "wma",   # Windows Media Audio
    "aiff",  # AIFF Audio
    "alac",  # Apple Lossless Audio
    "opus"   # Opus Audio
]

def write_file(objPath, url, file_extension, file_root):
    output_path = os.path.join(objPath, file_extension)
    response = requests.get(url)
    if response.status_code == 200:
        if not os.path.isdir(output_path):
            os.mkdir(output_path)
        with open(os.path.join(output_path, f"{file_root}.{file_extension}"), 'wb') as file:
            file.write(response.content)
            print(f"Derivative downloaded and saved as {file_root}.{file_extension} in {output_path}")

def download_derivatives(collection_id=None):
    for col in os.listdir(root):
        col_path = os.path.join(root, col)

        # Check if collection_id is provided and matches the current collection
        if collection_id and collection_id not in col:
            continue  # Skip this collection if it doesn't match

        if os.path.isdir(col_path):
            for obj in os.listdir(col_path):
                objPath = os.path.join(col_path, obj, "v1")
                metadataPath = os.path.join(objPath, "metadata.yml")

                if not os.path.exists(metadataPath):
                    print(f"Metadata file not found: {metadataPath}")
                    continue

                with open(metadataPath, 'r') as file:
                    metadata = yaml.safe_load(file)

                for file_set_id in metadata["file_sets"]:
                    filename = metadata["file_sets"][file_set_id]
                    file_root, file_extension = os.path.splitext(filename)
                    file_extension = file_extension[1:].lower()

                    # Get PDF derivative
                    if file_extension in office_document_extensions:
                        pdf_url = f"{root_url}{file_set_id}?file=pdf"
                        write_file(objPath, pdf_url, "pdf", file_root)

                    # Get audio derivatives
                    if file_extension in audio_file_extensions:
                        mp3_url = f"{root_url}{file_set_id}?file=mp3"
                        ogg_url = f"{root_url}{file_set_id}?file=ogg"
                        write_file(objPath, ogg_url, "ogg", file_root)
                        if file_extension != "mp3":
                            write_file(objPath, mp3_url, "mp3", file_root)

                    # Get video derivatives
                    if file_extension in video_file_extensions:
                        webm_url = f"{root_url}{file_set_id}?file=webm"
                        write_file(objPath, webm_url, "webm", file_root)



if __name__ == "__main__":
    # Check for command-line arguments
    if len(sys.argv) > 1:
        collection_id_arg = sys.argv[1]
        download_derivatives(collection_id=collection_id_arg)
    else:
        download_derivatives()