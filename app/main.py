from silence_detector import detect_silence
from silence_parser import parse_silence
from cut_builder import build_keep_intervals
from video_info import get_video_duration

from segment_pipeline import generate_segments
from concat_builder import create_concat_file
from video_merger import concat_segments

# main.py

VIDEO = "tests/sample.mov"


# 1. detect silences
print("\n========================")
print("PHASE 1 - DETECT SILENCE")
print("========================")

logs = detect_silence(VIDEO)

print(f"FFmpeg log length: {len(logs)} characters")
print(logs[:2000])  # first 2000 chars only

# 2. parse silences
print("\n========================")
print("PHASE 2 - PARSE SILENCES")
print("========================")

silences = parse_silence(logs)

print(f"Silences found: {len(silences)}")

for idx, silence in enumerate(silences, start=1):
    print(f"{idx}: {silence}")

# 3. get duration
print("\n========================")
print("PHASE 3 - VIDEO INFO")
print("========================")

video_duration = get_video_duration(VIDEO)

print(f"Video duration: {video_duration:.2f}s")

# 4. build keep intervals
print("\n========================")
print("PHASE 4 - BUILD KEEP INTERVALS")
print("========================")

keep_intervals = build_keep_intervals(
    silences,
    video_duration
)

print(f"Keep intervals found: {len(keep_intervals)}")

for idx, interval in enumerate(keep_intervals, start=1):
    start, end = interval

    print(
        f"{idx}: "
        f"{start:.2f}s -> {end:.2f}s "
        f"(duration {end-start:.2f}s)"
    )

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
