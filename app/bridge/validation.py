"""Validation rules for bridge inputs and public-demo limits."""

from __future__ import annotations

from pathlib import Path
from typing import Any


MIN_DURATION, MAX_DURATION = 0.1, 60.0
MIN_NOISE_DB, MAX_NOISE_DB = -100.0, 0.0
MAX_PUBLIC_VIDEO_DIMENSION = 1920
MAX_PUBLIC_VIDEO_PIXELS = 1920 * 1080


def validate_settings(payload: dict[str, Any]) -> tuple[float, float]:
    try:
        duration = float(payload.get("silence_duration", 1.0))
        noise_db = float(payload.get("noise_db", -38.0))
    except (TypeError, ValueError) as exc:
        raise ValueError("silence_duration and noise_db must be numbers") from exc
    if not MIN_DURATION <= duration <= MAX_DURATION:
        raise ValueError("silence_duration must be between 0.1 and 60 seconds")
    if not MIN_NOISE_DB <= noise_db <= MAX_NOISE_DB:
        raise ValueError("noise_db must be between -100 and 0 dB")
    return duration, noise_db


def validate_input(input_path: Any) -> Path:
    if not isinstance(input_path, str) or not input_path.strip():
        raise ValueError("input_path is required")
    path = Path(input_path).expanduser().resolve()
    if not path.is_file():
        raise ValueError("input_path must point to an existing file")
    return path


def validate_public_video_size(media: dict[str, Any]) -> None:
    """Keep free-demo jobs within a resolution the small instance can render."""
    video_streams = [stream for stream in media.get("streams", [])
                     if stream.get("codec_type") == "video"]
    for stream in video_streams:
        width, height = stream.get("width"), stream.get("height")
        if not isinstance(width, int) or not isinstance(height, int):
            continue
        if (max(width, height) > MAX_PUBLIC_VIDEO_DIMENSION
                or width * height > MAX_PUBLIC_VIDEO_PIXELS):
            raise ValueError("Public demo supports videos up to 1080p. Use a lower-resolution video.")
