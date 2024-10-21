import os
import sys
import yaml
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

def transcribe_file(file_path, transcription_file):
    # Load the Whisper model
    model = whisper.load_model("base")
    result = model.transcribe(file_path, task="transcribe", language="en")

    # Open the output VTT file
    with open(transcription_file, 'w', encoding='utf-8') as vtt_file:
        vtt_file.write("WEBVTT\n\n")
        # Iterate over the segments and format them as VTT
        for segment in result["segments"]:
            start = format_timestamp(segment["start"])
            end = format_timestamp(segment["end"])
            # Write the VTT cue
            vtt_file.write(f"{start} --> {end}\n")
            vtt_file.write(f"{segment['text'].strip()}\n\n")
    
    print(f"Transcription saved to {transcription_file}")

def transcribe(collection_id=None):
    for col in os.listdir(root):
        col_path = os.path.join(root, col)

        # Check if collection_id is provided and matches the current collection
        if collection_id and collection_id not in col:
            continue  # Skip this collection if it doesn't match

        if os.path.isdir(col_path):
            for obj in os.listdir(col_path):
                obj_path = os.path.join(col_path, obj, "v1")
                metadata_path = os.path.join(obj_path, "metadata.yml")
                output_dir = os.path.join(obj_path, "vtt")

                # Create transcription output directory if it doesn't exist
                if not os.path.exists(output_dir):
                    os.mkdir(output_dir)

                # Load metadata
                with open(metadata_path, 'r') as yml_file:
                    metadata = yaml.safe_load(yml_file)

                # Determine file type and paths based on resource type
                file_paths = []
                if metadata["resource_type"].lower() == "audio":
                    audio_formats = ["mp3", "ogg"]
                    for audio_format in audio_formats:
                        format_path = os.path.join(obj_path, audio_format)
                        if os.path.exists(format_path):
                            file_paths.extend(
                                [os.path.join(format_path, f) for f in os.listdir(format_path) if f.lower().endswith(f".{audio_format}")]
                            )
                elif metadata["resource_type"].lower() == "video":
                    video_formats = ["mp4", "mov", "webm"]
                    for video_format in video_formats:
                        format_path = os.path.join(obj_path, video_format)
                        if os.path.exists(format_path):
                            file_paths.extend(
                                [os.path.join(format_path, f) for f in os.listdir(format_path) if f.lower().endswith(f".{video_format}")]
                            )

                # Process each file
                for file_path in file_paths:
                    filename, file_extension = os.path.splitext(os.path.basename(file_path))
                    transcription_file = os.path.join(output_dir, f"{filename}{file_extension}.vtt")
                    print(f"Transcribing file: {file_path}")

                    # Transcribe and save in VTT format
                    transcribe_file(file_path, transcription_file)

if __name__ == "__main__":
    # Check for command-line arguments
    if len(sys.argv) > 1:
        collection_id_arg = sys.argv[1]
        transcribe(collection_id=collection_id_arg)
    else:
        transcribe()
