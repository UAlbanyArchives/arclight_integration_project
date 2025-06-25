import os
import sys
import yaml
import shutil
import whisper

if os.name == "nt":
    root = "\\\\Lincoln\\Library\\SPE_DAO\\aaa_migration"
else:
    root = "/media/Library/SPE_DAO/aaa_migration"

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
    result = model.transcribe(file_path, task="transcribe", language="de")

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


for mp3 in os.listdir(root):
    if mp3.endswith(".mp3"):
        filename = os.path.splitext(mp3)[0]
        mp3_path = os.path.join(root, mp3)
        vtt_file_path = os.path.join(root, filename + ".vtt")
        txt_file_path = os.path.join(root, filename + ".txt")
        print (mp3)
        transcribe_file(mp3_path, vtt_file_path, txt_file_path)

