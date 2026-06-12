import os
import shutil


def cleanup_temp_directory(temp_dir="temp_segments"):
    """
    delete ONLY contents of temp_segments directory, but not the directory itself
    """

    if not os.path.exists(temp_dir):
        print(
            f"Temporary directory '{temp_dir}' does not exist. No cleanup needed.")
        return

    try:
        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)

            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)

        print(f"Temporary directory '{temp_dir}' cleaned up successfully.")

    except Exception as e:
        print(f"Error while cleaning up temporary directory '{temp_dir}': {e}")
