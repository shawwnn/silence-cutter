import os
from app.segment_cutter import cut_segment

# segment_pipeline.py


def generate_segments(video, keep_intervals, output_dir="temp_segments",
                      progress_callback=None, status_callback=None):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    segments = []

    for idx, (start, end) in enumerate(keep_intervals):
        if status_callback:
            status_callback(idx)
        output_video = os.path.join(output_dir, f"segment_{idx + 1}.mp4")

        duration = end - start
        print(
            f"Cutting segment {idx + 1}: {start} -> {end} (Duration: {duration})")

        cut_segment(video, start, end, output_video)

        if progress_callback:
            progress_callback(idx + 1)

        print(f"DONE CUT: {output_video}")
        segments.append(output_video)

    return segments
