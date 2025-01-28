import os
import sys
import yaml
import shutil
import whisper

if os.name == "nt":
    root = "\\\\Lincoln\\Library\\SPE_DAO"
else:
    root = "/media/Library/SPE_DAO"

def format_timestamp(seconds):
    # Convert seconds to hh:mm:ss.mmm format
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"

def transcribe_file(file_path, vtt_file_path, txt_file_path):
    # Load the Whisper model
    model = whisper.load_model("base")
    result = model.transcribe(file_path, task="transcribe", language="en")

    # Open the output VTT and TXT files
    with open(vtt_file_path, 'w', encoding='utf-8') as vtt_file, \
         open(txt_file_path, 'w', encoding='utf-8') as txt_file:
        
        # Write to VTT file
        vtt_file.write("WEBVTT\n\n")
        
        # Iterate over the segments and format them as VTT and plain text
        for segment in result["segments"]:
            start = format_timestamp(segment["start"])
            end = format_timestamp(segment["end"])
            # Write the VTT cue
            vtt_file.write(f"{start} --> {end}\n")
            vtt_file.write(f"{segment['text'].strip()}\n\n")
            # Write the plain text transcription (no timestamps)
            txt_file.write(f"{segment['text'].strip()}\n")

    print(f"Transcription saved to {vtt_file_path} and {txt_file_path}")

def transcribe(collection_id=None, object_id=None):
    for col in os.listdir(root):
        col_path = os.path.join(root, col)

        # Check if collection_id is provided and matches the current collection
        if collection_id and collection_id != col:
            continue  # Skip this collection if it doesn't match

        if os.path.isdir(col_path):
            for obj in os.listdir(col_path):
                if object_id and object_id not in obj:
                    continue  # Skip this object if it doesn't match
                    
                obj_path = os.path.join(col_path, obj)
                metadata_path = os.path.join(obj_path, "metadata.yml")
                vtt_output_dir = os.path.join(obj_path, "vtt")
                txt_output_dir = os.path.join(obj_path, "txt")
                content_txt_path = os.path.join(obj_path, "content.txt")

                # Load metadata
                with open(metadata_path, 'r', encoding="utf-8") as yml_file:
                    metadata = yaml.safe_load(yml_file)

                # Determine file type and paths based on resource type
                file_paths = []
                if metadata["resource_type"].lower() == "audio":
                    # In preferential order
                    audio_formats = ["ogg", "mp3"]
                    for audio_format in audio_formats:
                        format_path = os.path.join(obj_path, audio_format)
                        if os.path.isdir(format_path) and len(os.listdir(format_path)) > 0:
                            file_paths.extend(
                                [os.path.join(format_path, f) for f in os.listdir(format_path) if f.lower().endswith(f".{audio_format}")]
                            )
                            break
                elif metadata["resource_type"].lower() == "video":
                    # In preferential order
                    video_formats = ["webm", "mp4", "mov", "mp3"]
                    for video_format in video_formats:
                        format_path = os.path.join(obj_path, video_format)
                        if os.path.isdir(format_path) and len(os.listdir(format_path)) > 0:
                            file_paths.extend(
                                [os.path.join(format_path, f) for f in os.listdir(format_path) if f.lower().endswith(f".{video_format}")]
                            )
                            break
                
                # Process each file
                for file_path in file_paths:
                    # Create transcription output directories if they don't exist
                    if not os.path.isdir(vtt_output_dir):
                        os.mkdir(vtt_output_dir)
                    if not os.path.isdir(txt_output_dir):
                        os.mkdir(txt_output_dir)

                    filename, file_extension = os.path.splitext(os.path.basename(file_path))
                    vtt_file_path = os.path.join(vtt_output_dir, f"{filename}.vtt")
                    txt_file_path = os.path.join(txt_output_dir, f"{filename}.txt")
                    print(f"Transcribing file: {file_path}")

                    # Transcribe and save in both VTT and TXT formats
                    transcribe_file(file_path, vtt_file_path, txt_file_path)

                    # Copy or append to content.txt
                    if os.path.isfile(content_txt_path):
                        with open(content_txt_path, "a") as content_file:
                            with open(txt_file_path, "r") as txt_file:
                                content = txt_file.read()
                            content_file.write("\n" + content)
                    else:
                        shutil.copy2(txt_file_path, content_txt_path)

if __name__ == "__main__":
    # Check for command-line arguments
    if len(sys.argv) > 2:
        collection_id = sys.argv[1]
        object_id = sys.argv[2]
        transcribe(collection_id=collection_id, object_id=object_id)
    elif len(sys.argv) > 1:
        collection_ids = sys.argv[1].split(',')
        for collection_id in collection_ids:
            print(f"Processing collection: {collection_id}")
            transcribe(collection_id=collection_id)
    else:
        transcribe()
