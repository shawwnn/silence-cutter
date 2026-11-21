from datetime import datetime
from pathlib import Path


def build_output_name(input_name: str, *, now: datetime | None = None) -> str:
    """Return a predictable MP4 name while preserving the source stem."""
    source = Path(input_name)
    timestamp = (now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S")
    return f"{source.stem}_cut_{timestamp}.mp4"
