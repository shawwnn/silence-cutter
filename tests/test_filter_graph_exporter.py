import pytest
from unittest.mock import patch

from app.filter_graph_exporter import build_filter_graph


def test_filter_graph_normalizes_and_concatenates_intervals():
    graph = build_filter_graph([(0.0, 1.25), (3.5, 8.0)])

    assert "[0:v]trim=start=0.000000:end=1.250000,setpts=PTS-STARTPTS[v0]" in graph
    assert "[0:a]atrim=start=3.500000:end=8.000000,asetpts=PTS-STARTPTS[a1]" in graph
    assert "[v0][a0][v1][a1]concat=n=2:v=1:a=1[outv][outa]" in graph


def test_filter_graph_rejects_invalid_intervals():
    with pytest.raises(ValueError):
        build_filter_graph([(2.0, 2.0)])


def test_export_limits_ffmpeg_parallelism_and_uses_light_public_preset(tmp_path):
    output = tmp_path / "output.mp4"
    completed = type("Completed", (), {"returncode": 0, "stderr": ""})()
    with patch("app.filter_graph_exporter.shutil.which", return_value="ffmpeg"), \
         patch("app.filter_graph_exporter.subprocess.run", return_value=completed) as run, \
         patch.dict("os.environ", {"SILENCE_CUTTER_PUBLIC_MODE": "true"}):
        from app.filter_graph_exporter import export_precise_intervals
        export_precise_intervals("input.mp4", [(0, 1)], str(output))

    command = run.call_args.args[0]
    assert command[2:8] == ["-threads", "1", "-filter_threads", "1", "-filter_complex_threads", "1"]
    assert "-preset" in command and command[command.index("-preset") + 1] == "ultrafast"
