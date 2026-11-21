import pytest

from app.filter_graph_exporter import build_filter_graph


def test_filter_graph_normalizes_and_concatenates_intervals():
    graph = build_filter_graph([(0.0, 1.25), (3.5, 8.0)])

    assert "[0:v]trim=start=0.000000:end=1.250000,setpts=PTS-STARTPTS[v0]" in graph
    assert "[0:a]atrim=start=3.500000:end=8.000000,asetpts=PTS-STARTPTS[a1]" in graph
    assert "[v0][a0][v1][a1]concat=n=2:v=1:a=1[outv][outa]" in graph


def test_filter_graph_rejects_invalid_intervals():
    with pytest.raises(ValueError):
        build_filter_graph([(2.0, 2.0)])
