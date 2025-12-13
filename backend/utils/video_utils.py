import os
import subprocess

# Read FFmpeg path from environment variable
# Fall back to "ffmpeg" if not set (for other machines)
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")

def extract_frames(video_path, output_dir, fps=1):
    os.makedirs(output_dir, exist_ok=True)

    command = [
        FFMPEG_PATH,
        "-i", video_path,
        "-vf", f"fps={fps}",
        os.path.join(output_dir, "frame_%04d.jpg")
    ]

    subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False
    )
