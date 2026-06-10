# cut_builder.py

def build_keep_intervals(silences, video_duration):
    keep = []
    current = 0

    for silence in silences:
        start = silence["start"]
        end = silence["end"]

        # safety: ignore bad data
        if start < current:
            continue

        if start > current:
            keep.append((current, start))

        current = end

    # last segment
    if current < video_duration:
        keep.append((current, video_duration))

    return keep
