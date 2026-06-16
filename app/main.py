from pathlib import Path

from app.pipeline.pipeline_finalizer import finalize_pipeline
from app.silence_detector import detect_silence
from app.silence_parser import parse_silence
from app.cut_builder import build_keep_intervals
from app.video_info import get_video_duration
from app.segment_pipeline import generate_segments
from app.concat_builder import create_concat_file
from app.video_merger import concat_segments


# main.py


def run_pipeline(video_path, output_path=None,
                 progress_callback=None,
                 status_callback=None,
                 silence_duration=1.0):
    def update_progress_and_status_backend(status=None, progress=None):
        if progress_callback and progress is not None:
            progress_callback(progress)
        if status_callback and status:
            status_callback(status)

    # Phase 0 Prepare name
        # create dynamic output if none provided
    if output_path is None:

        input_file = Path(video_path)

        output_path = (
            Path("assets/outputs")
            / f"{input_file.stem}_cut{input_file.suffix}"
        )

        output_path = str(output_path)

    print("\n========================")
    print("PHASE 1 - DETECT SILENCE")
    print("========================")

    print(f"Using silence threshold: {silence_duration}s")
    logs = detect_silence(
        video_path,
        silence_duration
    )

    update_progress_and_status_backend(
        status="Detecting silence...", progress=0.33)  # 33%

    print("\n========================")
    print("PHASE 2 - PARSE SILENCES")
    print("========================")

    silences = parse_silence(logs)
    update_progress_and_status_backend(
        status="Parsing silences...", progress=0.65)  # 20%

    print("\n========================")
    print("PHASE 3 - VIDEO INFO")
    print("========================")

    video_duration = get_video_duration(video_path)
    update_progress_and_status_backend(
        status="Fetching video info...", progress=0.70)  # 70%

    print("\n========================")
    print("PHASE 4 - BUILD KEEP INTERVALS")
    print("========================")

    keep_intervals = build_keep_intervals(silences, video_duration)
    update_progress_and_status_backend(
        status="Building keep intervals...", progress=0.75)  # 75%

    print("\n========================")
    print("PHASE 5 - GENERATE SEGMENTS")
    print("========================")

    segments = generate_segments(video_path, keep_intervals)
    update_progress_and_status_backend(
        status="Generating segments...", progress=0.80)  # 80%

    print("\n========================")
    print("PHASE 6 - CREATE CONCAT FILE")
    print("========================")

    list_file = create_concat_file(segments)
    update_progress_and_status_backend(
        status="Creating concat file...", progress=0.85)  # 85%

    print("\n========================")
    print("PHASE 7 - MERGE VIDEO")
    print("========================")

    concat_segments(list_file, output_path)
    update_progress_and_status_backend(
        status="Merging video...", progress=0.95)  # 95%

    print("\n========================")
    print("PHASE 8 - FINALIZE")
    print("========================")

    finalize_pipeline(output_path)
    update_progress_and_status_backend(
        status="Finalizing...", progress=1)  # 100%

    print("\nDONE →", output_path)

    return output_path


if __name__ == "__main__":
    run_pipeline("tests/sample.mov")
