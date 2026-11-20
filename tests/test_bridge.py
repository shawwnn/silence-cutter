from pathlib import Path

from app.bridge.server import JobManager, create_app


def test_health_endpoint(tmp_path):
    app = create_app(JobManager(tmp_path / "outputs"))
    response = app.test_client().get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {"ok": True}


def test_metadata_rejects_missing_input(tmp_path):
    app = create_app(JobManager(tmp_path / "outputs"))
    response = app.test_client().post("/api/metadata", json={})

    assert response.status_code == 400
    assert "input_path is required" in response.get_json()["error"]


def test_job_rejects_invalid_settings_before_media_probe(tmp_path):
    input_file = tmp_path / "not-a-video.txt"
    input_file.write_text("not video")
    app = create_app(JobManager(tmp_path / "outputs"))

    response = app.test_client().post(
        "/api/jobs",
        json={
            "input_path": str(input_file),
            "silence_duration": 0,
            "noise_db": -60,
        },
    )

    assert response.status_code == 400
    assert "silence_duration" in response.get_json()["error"]
