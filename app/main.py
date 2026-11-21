from pathlib import Path
import sys

from app.pipeline.pipeline_finalizer import finalize_pipeline
from app.pipeline.insufficient_retained_content import InsufficientRetainedContent
from app.pipeline.no_silence_detected import NoSilenceDetected
from app.output_naming import build_output_name
from app.silence_detector import detect_silence
from app.silence_parser import parse_silence
from app.cut_builder import build_keep_intervals
from app.video_info import get_video_duration
from app.filter_graph_exporter import export_precise_intervals


DURATION_TOLERANCE_SECONDS = 0.25
MIN_RETAINED_DURATION_SECONDS = 0.5


# main.py


def run_pipeline(video_path, output_path=None,
                 progress_callback=None,
                 status_callback=None,
                 silence_duration=1.0,
                 noise_db=-38.0,
                 temp_dir="temp_segments",
                 return_summary=False):
    def update_progress_and_status_backend(status=None, progress=None):
        if progress_callback and progress is not None:
            progress_callback(progress)
        if status_callback and status:
            status_callback(status)

    # Phase 0 Prepare name
        # create dynamic output if none provided
    if output_path is None:

        input_file = Path(video_path)

        # if PyInstaller runs
        if getattr(sys, "frozen", False):
            # make directory for app version
            output_dir = Path.home() / "SilenceCutter" / "outputs"
        else:
            # use dev directory
            output_dir = Path("assets/outputs")

        # make sure folder exists
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / build_output_name(input_file.name)

        output_path = str(output_path)

    print("\n========================")
    print("PHASE 1 - DETECT SILENCE")
    print("========================")

    print(
        f"Using silence duration: {silence_duration}s; "
        f"noise threshold: {noise_db}dB"
    )
    update_progress_and_status_backend(
        status="Detecting silence...", progress=0.05)
    logs = detect_silence(
        video_path,
        silence_duration,
        noise_db
    )

    print("\n========================")
    print("PHASE 2 - PARSE SILENCES")
    print("========================")

    update_progress_and_status_backend(
        status="Parsing silences...", progress=0.25)
    silences = parse_silence(logs)
    detected_silence_count = len(silences)
    removed_duration = sum(silence["duration"] for silence in silences)

    print("\n========================")
    print("PHASE 3 - VIDEO INFO")
    print("========================")

    update_progress_and_status_backend(
        status="Fetching video info...", progress=0.35)
    video_duration = get_video_duration(video_path)

    if not silences:
        raise NoSilenceDetected(video_duration)

    print("\n========================")
    print("PHASE 4 - BUILD KEEP INTERVALS")
    print("========================")

    update_progress_and_status_backend(
        status="Building keep intervals...", progress=0.45)
    keep_intervals = build_keep_intervals(silences, video_duration)
    expected_duration = sum(end - start for start, end in keep_intervals)
    if expected_duration <= MIN_RETAINED_DURATION_SECONDS:
        raise InsufficientRetainedContent(
            input_duration_seconds=video_duration,
            retained_duration_seconds=expected_duration,
            removed_duration_seconds=max(0.0, video_duration - expected_duration),
        )

    print("\n========================")
    print("PHASE 5 - RENDER PRECISE CUTS")
    print("========================")

    update_progress_and_status_backend(
        status="Rendering precise video and audio cuts...", progress=0.50)
    export_precise_intervals(video_path, keep_intervals, output_path)

    print("\n========================")
    print("PHASE 8 - FINALIZE")
    print("========================")

    update_progress_and_status_backend(
        status="Validating final video...", progress=0.95)
    finalize_pipeline(output_path, temp_dir)
    update_progress_and_status_backend(progress=1.0)

    print("\nDONE →", output_path)

    if return_summary:
        output_duration = get_video_duration(output_path)
        duration_difference = abs(expected_duration - output_duration)
        return {
            "output_path": output_path,
            "input_duration_seconds": video_duration,
            "expected_duration_seconds": expected_duration,
            "output_duration_seconds": output_duration,
            "duration_difference_seconds": duration_difference,
            "duration_verified": duration_difference <= DURATION_TOLERANCE_SECONDS,
            "detected_silence_count": detected_silence_count,
            "removed_duration_seconds": removed_duration,
        }

    return output_path


if __name__ == "__main__":
    run_pipeline("tests/sample.mov")
