import os
import subprocess

# silence_detector.py


def detect_silence(video_path):
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-af", "silencedetect=noise=-30dB:d=0.5",
        "-f", "null",
        "-"
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    # FFmpeg logs always go to stderr
    return result.stderr
