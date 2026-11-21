from app import main
from app.cut_builder import build_keep_intervals
from app.pipeline.no_silence_detected import NoSilenceDetected
from app.silence_parser import parse_silence
import pytest


def test_parse_silence_extracts_completed_intervals():
    log = """
    [silencedetect] silence_start: 1.25
    [silencedetect] silence_end: 3.75 | silence_duration: 2.50
    [silencedetect] silence_start: 8
    [silencedetect] silence_end: 9.5 | silence_duration: 1.5
    """

    assert parse_silence(log) == [
        {"start": 1.25, "end": 3.75, "duration": 2.5},
        {"start": 8.0, "end": 9.5, "duration": 1.5},
    ]


def test_build_keep_intervals_retains_content_around_silences():
    silences = [
        {"start": 2.0, "end": 4.0},
        {"start": 7.5, "end": 9.0},
    ]

    assert build_keep_intervals(silences, video_duration=12.0) == [
        (0, 2.0),
        (4.0, 7.5),
        (9.0, 12.0),
    ]


def test_run_pipeline_generates_default_output_filename(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        main,
        "detect_silence",
        lambda *args: "silence_start: 1\nsilence_end: 2 | silence_duration: 1",
    )
    monkeypatch.setattr(main, "get_video_duration", lambda *args: 10.0)
    monkeypatch.setattr(main, "export_precise_intervals", lambda *args: None)
    monkeypatch.setattr(main, "finalize_pipeline", lambda *args: None)

    output_path = main.run_pipeline(str(tmp_path / "recording.mov"))

    assert output_path == "assets/outputs/recording_cut.mov"


def test_run_pipeline_stops_before_output_when_no_silence_found(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "detect_silence", lambda *args: "")
    monkeypatch.setattr(main, "get_video_duration", lambda *args: 10.0)
    monkeypatch.setattr(main, "export_precise_intervals", lambda *args: pytest.fail("must not render"))

    with pytest.raises(NoSilenceDetected):
        main.run_pipeline(str(tmp_path / "recording.mov"))


def test_pipeline_summary_verifies_expected_output_duration(tmp_path, monkeypatch):
    input_file = tmp_path / "recording.mov"
    output_file = tmp_path / "output.mp4"
    monkeypatch.setattr(
        main,
        "detect_silence",
        lambda *args: "silence_start: 2\nsilence_end: 4 | silence_duration: 2",
    )
    monkeypatch.setattr(
        main,
        "get_video_duration",
        lambda path: 8.0 if str(path).endswith("output.mp4") else 10.0,
    )
    monkeypatch.setattr(main, "export_precise_intervals", lambda *args: None)
    monkeypatch.setattr(main, "finalize_pipeline", lambda *args: None)

    summary = main.run_pipeline(
        str(input_file), output_path=str(output_file), return_summary=True
    )

    assert summary["expected_duration_seconds"] == 8.0
    assert summary["duration_difference_seconds"] == 0.0
    assert summary["duration_verified"] is True
