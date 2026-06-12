import os


def is_final_video_valid(output_file: str) -> bool:
    """
    Checks if the final video file exists and is not empty.
    """

    if not os.path.exists(output_file):
        print(f"Error: Final video file '{output_file}' does not exist.")
        return False

    if os.path.getsize(output_file) == 0:
        print(f"Error: Final video file '{output_file}' is empty.")
        return False

    print(f"Final video file '{output_file}' is valid.")
    return True
