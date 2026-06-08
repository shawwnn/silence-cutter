import os
import subprocess

# Python script that uses FFmpeg to detect silence
# in a video without creating an output file.

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

video_path = os.path.join(BASE_DIR, "tests", "sample.mov")

cmd = [
    "ffmpeg",
    "-i", video_path,
    "-af", "silencedetect=noise=-30dB:d=0.5",
    "-f", "null",
    "-"
]

result = subprocess.run(cmd, capture_output=True, text=True)

print(result.stderr)
