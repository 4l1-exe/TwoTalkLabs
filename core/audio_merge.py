from moviepy.editor import AudioFileClip, concatenate_audioclips

def merge_audio(files: list[str], output_path: str):
    """Merge multiple MP3 files into one safely."""
    clips = []
    try:
        # Load all individual audio clips
        clips = [AudioFileClip(f) for f in files]
        # Concatenate them sequentially
        final = concatenate_audioclips(clips)
        # Write the final merged MP3
        final.write_audiofile(output_path, codec="mp3")
    finally:
        # Close all clips to release file handles (important on Windows)
        for clip in clips:
            clip.close()
