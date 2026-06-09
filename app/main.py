from silence_detector import detect_silence
from silence_parser import parse_silence
from cut_builder import build_keep_intervals

VIDEO = "tests/sample.mov"

logs = detect_silence(VIDEO)

silences = parse_silence(logs)

for silence in silences:
    print(silence)

# TEMP: you still need video duration manually for now
video_duration = 20.0

keep_intervals = build_keep_intervals(silences, video_duration)

print("\nKEEP INTERVALS:")
for k in keep_intervals:
    print(k)
