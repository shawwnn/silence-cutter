import subprocess
import os

# segment_cutter.py


def cut_segment(input_video, start_time, end_time, output_video):
    cmd = [
        "ffmpeg",
        "-y",
        "-ss", str(start_time),
        "-to", str(end_time),
        "-i", input_video,

        "-c", "copy",
        "-c:a", "aac",

        output_video
    ]

    subprocess.run(cmd, check=True)
