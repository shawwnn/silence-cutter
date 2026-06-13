from app.pipeline.pipeline_finalizer import finalize_pipeline
from app.silence_detector import detect_silence
from app.silence_parser import parse_silence
from app.cut_builder import build_keep_intervals
from app.video_info import get_video_duration
from app.segment_pipeline import generate_segments
from app.concat_builder import create_concat_file
from app.video_merger import concat_segments


def run_pipeline(video_path, output_path="assets/outputs/final.mp4", progress_callback=None):
    def update_progress_backend(value):
        if progress_callback:
            progress_callback(value)

    print("\n========================")
    print("PHASE 1 - DETECT SILENCE")
    print("========================")

    logs = detect_silence(video_path)
    update_progress_backend(0.33)  # 33%

    print("\n========================")
    print("PHASE 2 - PARSE SILENCES")
    print("========================")

    silences = parse_silence(logs)
    update_progress_backend(0.65)  # 20%

    print("\n========================")
    print("PHASE 3 - VIDEO INFO")
    print("========================")

    video_duration = get_video_duration(video_path)
    update_progress_backend(0.70)  # 70%

    print("\n========================")
    print("PHASE 4 - BUILD KEEP INTERVALS")
    print("========================")

    keep_intervals = build_keep_intervals(silences, video_duration)
    update_progress_backend(0.75)  # 75%

    print("\n========================")
    print("PHASE 5 - GENERATE SEGMENTS")
    print("========================")

    segments = generate_segments(video_path, keep_intervals)
    update_progress_backend(0.80)  # 80%

    print("\n========================")
    print("PHASE 6 - CREATE CONCAT FILE")
    print("========================")

    list_file = create_concat_file(segments)
    update_progress_backend(0.85)  # 85%

    print("\n========================")
    print("PHASE 7 - MERGE VIDEO")
    print("========================")

    concat_segments(list_file, output_path)
    update_progress_backend(0.95)  # 95%

    print("\n========================")
    print("PHASE 8 - FINALIZE")
    print("========================")

    finalize_pipeline(output_path)
    update_progress_backend(1)  # 100%

    print("\nDONE →", output_path)

    return output_path


if __name__ == "__main__":
    run_pipeline("tests/sample.mov")
