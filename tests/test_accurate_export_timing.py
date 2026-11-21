import shutil
import subprocess

import pytest

from app.filter_graph_exporter import export_precise_intervals
from app.video_info import get_video_duration


pytestmark = pytest.mark.skipif(
    not shutil.which("ffmpeg") or not shutil.which("ffprobe"),
    reason="FFmpeg and FFprobe are required for accurate export timing tests",
)


def create_source_video(path, duration=5):
    """Create a small A/V fixture with frame-based video and continuous audio."""
    command = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"testsrc2=size=160x90:rate=30:duration={duration}",
        "-f", "lavfi", "-i", f"sine=frequency=440:sample_rate=48000:duration={duration}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-shortest", str(path),
    ]
    subprocess.run(command, check=True, capture_output=True, text=True)


@pytest.mark.parametrize(
    ("name", "intervals", "expected_duration"),
    [
        ("cut_at_start", [(1.0, 5.0)], 4.0),
        ("cut_at_end", [(0.0, 4.0)], 4.0),
        ("cut_in_middle", [(0.0, 2.0), (3.0, 5.0)], 4.0),
        ("multiple_cuts", [(0.0, 1.0), (2.0, 3.0), (4.0, 5.0)], 3.0),
    ],
)
def test_accurate_export_matches_retained_duration(tmp_path, name, intervals, expected_duration):
    source = tmp_path / f"{name}_source.mp4"
    output = tmp_path / f"{name}_output.mp4"
    create_source_video(source)

    export_precise_intervals(str(source), intervals, str(output))

    assert output.is_file()
    assert abs(get_video_duration(str(output)) - expected_duration) <= 0.15
