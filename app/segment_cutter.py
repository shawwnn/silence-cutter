import subprocess
import shutil

# segment_cutter.py


def cut_segment(input_video, start_time, end_time, output_video):

    ffmpeg_path = shutil.which("ffmpeg")
    print("FFMPEG =", ffmpeg_path)

    # fallback for mac OS
    if not ffmpeg_path:
        ffmpeg_path = "/usr/local/bin/ffmpeg"

    duration = end_time - start_time

    if duration <= 0:
        print(
            f"Warning: Invalid segment duration ({duration}s) for {input_video}. Skipping cut."
        )
        return

    cmd = [
        ffmpeg_path,
        "-y",
        "-ss", str(start_time),
        "-to", str(end_time),
        "-i", input_video,

        "-c", "copy",
        "-c:a", "aac",

        output_video
    ]

    print(f"Executing FFMpeg: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            check=True
        )

        print(f"FFMpeg worked successfully")

    except subprocess.TimeoutExpired:
        print(f"FFMpeg command timed out for segment: {input_video}")
        raise

    except subprocess.CalledProcessError as e:
        print(f"FFMpeg failed with error: {e.stderr}")
        raise
