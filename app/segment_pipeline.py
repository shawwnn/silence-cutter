import os
from app.segment_cutter import cut_segment

# segment_pipeline.py


def generate_segments(video, keep_intervals, output_dir="temp_segments"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    segments = []

    for idx, (start, end) in enumerate(keep_intervals):
        output_video = os.path.join(output_dir, f"segment_{idx + 1}.mp4")
        print(f"START CUT: {start} -> {end}")
        cut_segment(video, start, end, output_video)
        print(f"DONE CUT: {output_video}")
        segments.append(output_video)

    return segments
