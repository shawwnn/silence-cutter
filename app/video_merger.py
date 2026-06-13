import subprocess

# video_merger.py


def concat_segments(list_file, output_video):
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-c:v", "copy",
        "-c:a", "copy",
        output_video
    ]

    subprocess.run(cmd, check=True)
