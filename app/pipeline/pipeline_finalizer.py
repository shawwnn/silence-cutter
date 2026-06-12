from app.pipeline.cleanup_temp_directory import cleanup_temp_directory
from app.pipeline.check_final_video import is_final_video_valid


def finalize_pipeline(output_file: str, temp_dir="temp_segments"):
    """
    Finalize the pipeline: validate final video and clean up temp files.
    """

    print("Finalizing pipeline...")

    if not is_final_video_valid(output_file):
        print("Final video validation failed. Please check the logs for details.")
        return

    cleanup_temp_directory(temp_dir)

    print("Pipeline finalized successfully. Temporary files cleaned up.")
