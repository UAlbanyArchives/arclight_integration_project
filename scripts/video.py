from moviepy.editor import VideoFileClip
import os

if os.name == "nt":
	root = "\\\\Lincoln\\Library\\SPE_DAO"
else:
	root = "/media/Library/SPE_DAO"

video = VideoFileClip(os.path.join(root, "apap015", "8p58pm259", "v1", "webm", "nam_apap_015_video_000009.webm"))
width, height = video.size
duration = video.duration

print(f"Width: {width}, Height: {height}, Duration: {duration} seconds")