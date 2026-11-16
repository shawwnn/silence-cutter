import subprocess
import json
import shutil

# video_info.py


def get_video_duration(video_path):
    if shutil.which("ffprobe") is None:
        raise RuntimeError(
            "FFprobe was not found on PATH. Install FFmpeg and try again."
        )

    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json",
        video_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)

    return float(data["format"]["duration"])
