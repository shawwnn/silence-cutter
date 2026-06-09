def build_keep_intervals(silences, video_duration):
    keep_intervals = []
    current_time = 0

    for silence in silences:
        keep_intervals.append({
            current_time,
            silence["start"]
        })

        current_time = silence["end"]

    keep_intervals.append({
        current_time,
        video_duration
    })

    return keep_intervals
