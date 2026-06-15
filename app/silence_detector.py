import os
import subprocess

# silence_detector.py


def detect_silence(video_path, silence_duration=1.0, noise=-32):
    filter_arg = f"silencedetect=noise={noise}dB:d={silence_duration}"

    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-af", filter_arg,
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
