from silence_detector import detect_silence
from silence_parser import parse_silence
from cut_builder import build_keep_intervals
from video_info import get_video_duration

from segment_pipeline import generate_segments
from concat_builder import create_concat_file
from video_merger import concat_segments

# main.py

VIDEO = "tests/sample.mov"

# 1. detect silence (FFmpeg logs)
logs = detect_silence(VIDEO)

# 2. parse silences
silences = parse_silence(logs)

print("\nSILENCES:")
for s in silences:
    print(s)

# 3. get duration
video_duration = get_video_duration(VIDEO)

# 4. build keep intervals
keep_intervals = build_keep_intervals(silences, video_duration)

print("\nDEBUG KEEP TYPE:", type(keep_intervals))
print("DEBUG KEEP RAW:", keep_intervals)

print("\nKEEP INTERVALS:")
for k in keep_intervals:
    print(k)

# 5. CUT VIDEO into segments
segments = generate_segments(VIDEO, keep_intervals)

print("\nSEGMENTS CREATED:")
for s in segments:
    print(s)

# 6. create concat file
list_file = create_concat_file(segments)

# 7. merge final output
output = "assets/outputs/final.mp4"
concat_segments(list_file, output)

print("\nDONE →", output)
