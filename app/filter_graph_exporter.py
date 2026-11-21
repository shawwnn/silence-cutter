"""Accurate single-pass FFmpeg export for retained video intervals."""

from __future__ import annotations

import shutil
import subprocess
import os
from pathlib import Path


def build_filter_graph(keep_intervals: list[tuple[float, float]]) -> str:
    """Build a trim/atrim/concat graph with normalized timestamps."""
    if not keep_intervals:
        raise ValueError("At least one retained interval is required")

    chains: list[str] = []
    labels: list[str] = []
    for index, (start, end) in enumerate(keep_intervals):
        if end <= start:
            raise ValueError("Retained interval end must be after its start")
        start_text = f"{start:.6f}"
        end_text = f"{end:.6f}"
        video_label = f"v{index}"
        audio_label = f"a{index}"
        chains.append(
            f"[0:v]trim=start={start_text}:end={end_text},"
            f"setpts=PTS-STARTPTS[{video_label}]"
        )
        chains.append(
            f"[0:a]atrim=start={start_text}:end={end_text},"
            f"asetpts=PTS-STARTPTS[{audio_label}]"
        )
        labels.append(f"[{video_label}][{audio_label}]")

    chains.append(
        f"{''.join(labels)}concat=n={len(keep_intervals)}:v=1:a=1[outv][outa]"
    )
    return ";".join(chains)


def export_precise_intervals(input_video: str, keep_intervals: list[tuple[float, float]],
                             output_video: str) -> None:
    """Create one frame-accurate MP4 from all retained intervals."""
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        raise RuntimeError("FFmpeg was not found on PATH. Install FFmpeg and try again.")

    output_path = Path(output_video)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    filter_graph = build_filter_graph(keep_intervals)
    public_mode = os.environ.get("SILENCE_CUTTER_PUBLIC_MODE", "").lower() in {"1", "true", "yes"}
    command = [
        ffmpeg_path, "-y", "-threads", "1", "-filter_threads", "1",
        "-filter_complex_threads", "1", "-i", input_video,
        "-filter_complex", filter_graph,
        "-map", "[outv]", "-map", "[outa]",
        "-c:v", "libx264", "-preset", "ultrafast" if public_mode else "veryfast", "-crf", "22" if public_mode else "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(output_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            "FFmpeg could not render the edited video: "
            f"{result.stderr.strip() or 'unknown error'}"
        )
