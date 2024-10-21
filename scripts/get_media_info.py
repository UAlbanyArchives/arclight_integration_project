import ffmpeg

def get_media_info(resource_path):
    """Get media duration and format using ffprobe from ffmpeg."""
    try:
        probe = ffmpeg.probe(resource_path)
        format_info = probe.get('format', {})
        
        # Get duration and format
        duration = float(format_info.get('duration', 0))
        format_type = format_info.get('format_name', 'application/octet-stream')

        # Map WebM/OGG/etc. to correct mimetype
        mimetype_map = {
            'webm': 'video/webm',
            'ogg': 'audio/ogg',
            'mp4': 'video/mp4',
            'mp3': 'audio/mpeg'
        }
        mimetype = mimetype_map.get(format_type, 'application/octet-stream')
        
        return duration, mimetype
    except ffmpeg.Error as e:
        print(f"Error getting media info: {e}")
        return None, None
