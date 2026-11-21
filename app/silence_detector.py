import os
import subprocess
import shutil

# silence_detector.py


def detect_silence(video_path, silence_duration=0.45, noise=-38):
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "FFmpeg was not found on PATH. Install FFmpeg and try again."
        )

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

    if result.returncode != 0:
        raise RuntimeError(
            "FFmpeg could not analyze the selected video: "
            f"{result.stderr.strip() or 'unknown error'}"
        )

    # FFmpeg logs always go to stderr
    return result.stderr
