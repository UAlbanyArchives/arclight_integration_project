import ffmpeg

def get_media_info(resource_path):
    """Get media duration, format, width, and height using ffprobe from ffmpeg."""
    try:
        probe = ffmpeg.probe(resource_path)
        format_info = probe.get('format', {})
        
        # Get duration
        duration = float(format_info.get('duration', 0))

        # Initialize width and height
        video_width = None
        video_height = None
        mimetype = 'application/octet-stream'  # Default mimetype

        # Determine format and set mimetype accordingly
        format_name = format_info.get('format_name', '')

        if 'webm' in format_name:
            mimetype = 'video/webm'
        elif 'ogg' in format_name:
            mimetype = 'audio/ogg'
        elif 'mp4' in format_name:
            mimetype = 'video/mp4'
        elif 'mp3' in format_name:
            mimetype = 'audio/mpeg'

        # Get width and height for video formats
        if format_info.get('nb_streams', 0) > 0:
            streams = probe.get('streams', [])
            for stream in streams:
                if stream.get('codec_type') == 'video':
                    video_width = stream.get('width')
                    video_height = stream.get('height')
                    break  # Exit loop after first video stream

        return duration, mimetype, video_width, video_height

    except ffmpeg.Error as e:
        print(f"Error getting media info: {e}")
        return None, None, None, None
