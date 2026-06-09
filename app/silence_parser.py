import re


def parse_silence(log_text):
    silences = []

    current_start = None

    for line in log_text.splitlines():

        start = re.search(r"silence_start:\s*([\d.]+)", line)
        if start:
            current_start = float(start.group(1))
            continue

        end = re.search(
            r"silence_end:\s*([\d.]+)\s*\|\s*silence_duration:\s*([\d.]+)",
            line
        )

        if end and current_start is not None:
            silences.append({
                "start": current_start,
                "end": float(end.group(1)),
                "duration": float(end.group(2))
            })

            current_start = None

    return silences
