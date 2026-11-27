"""Background video-processing worker for the bridge."""

from __future__ import annotations

import multiprocessing

from app.main import process_video
from app.pipeline.insufficient_retained_content import InsufficientRetainedContent
from app.pipeline.no_silence_detected import NoSilenceDetected


def run_worker(input_path: str, output_path: str, duration: float, noise_db: float,
               temp_dir: str, events: multiprocessing.Queue):
    def progress(value: float): events.put({"type": "progress", "progress": value})
    def status(message: str): events.put({"type": "status", "message": message})
    try:
        result = process_video(input_path, output_path=output_path, progress_callback=progress,
                              status_callback=status, silence_duration=duration, noise_db=noise_db,
                              temp_dir=temp_dir, return_summary=True)
        verified = result["duration_verified"]
        events.put({"type": "completed" if verified else "timing_warning",
                    "state": "completed" if verified else "timing_warning",
                    "message": "Completed" if verified else "Output timing could not be verified",
                    "progress": 1.0, "result": result})
    except NoSilenceDetected as exc:
        events.put({"type": "no_silence", "state": "needs_confirmation",
                    "message": "No matching silence found", "result": {
                        "input_duration_seconds": exc.input_duration_seconds,
                        "output_duration_seconds": None, "detected_silence_count": 0,
                        "removed_duration_seconds": 0}})
    except InsufficientRetainedContent as exc:
        events.put({"type": "over_cut", "state": "settings_warning",
                    "message": "Selected settings would remove virtually the entire video", "result": {
                        "input_duration_seconds": exc.input_duration_seconds,
                        "expected_duration_seconds": exc.retained_duration_seconds,
                        "output_duration_seconds": None,
                        "removed_duration_seconds": exc.removed_duration_seconds}})
    except Exception as exc:
        events.put({"type": "failed", "state": "failed", "error": str(exc),
                    "message": "Processing failed"})
    finally:
        events.close()
        events.join_thread()
