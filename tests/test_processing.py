from app import main
from app.cut_builder import build_keep_intervals
from app.silence_parser import parse_silence


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
    monkeypatch.setattr(main, "detect_silence", lambda *args: "")
    monkeypatch.setattr(main, "get_video_duration", lambda *args: 10.0)
    monkeypatch.setattr(main, "generate_segments", lambda *args: [])
    monkeypatch.setattr(main, "create_concat_file", lambda *args: "concat.txt")
    monkeypatch.setattr(main, "concat_segments", lambda *args: None)
    monkeypatch.setattr(main, "finalize_pipeline", lambda *args: None)

    output_path = main.run_pipeline(str(tmp_path / "recording.mov"))

    assert output_path == "assets/outputs/recording_cut.mov"
