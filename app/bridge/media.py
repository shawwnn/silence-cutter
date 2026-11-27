"""Media probing used by the HTTP bridge."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


def probe_metadata(path: Path) -> dict[str, Any]:
    if shutil.which("ffprobe") is None:
        raise RuntimeError("FFprobe was not found on PATH")
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise ValueError("FFprobe could not read this media file")
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("FFprobe returned invalid metadata") from exc
    streams = data.get("streams", [])
    has_video = any(stream.get("codec_type") == "video" for stream in streams)
    has_audio = any(stream.get("codec_type") == "audio" for stream in streams)
    if not has_video:
        raise ValueError("The selected file does not contain a video stream")
    format_data = data.get("format", {})
    duration = format_data.get("duration")
    suffix = path.suffix.lower().lstrip(".")
    return {
        "filename": path.name,
        "size_bytes": path.stat().st_size,
        "duration_seconds": float(duration) if duration else None,
        "format": suffix or format_data.get("format_name", "").split(",")[0],
        "has_video": has_video,
        "has_audio": has_audio,
        "streams": [{
            "codec_type": stream.get("codec_type"), "codec_name": stream.get("codec_name"),
            "width": stream.get("width"), "height": stream.get("height"),
        } for stream in streams],
    }
