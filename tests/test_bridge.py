import io

from app.bridge import server
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


def test_multipart_job_receives_duration_and_noise_values(monkeypatch, tmp_path):
    class FakeManager:
        def start(self, input_path, duration, noise_db):
            assert input_path.is_file()
            assert duration == 3.5
            assert noise_db == -42.0
            return {"job_id": "job-1", "state": "running"}

        def public_job(self):
            return None

    monkeypatch.setattr(server, "_probe_metadata", lambda path: {})
    app = create_app(FakeManager())

    response = app.test_client().post(
        "/api/jobs",
        data={
            "file": (io.BytesIO(b"video bytes"), "sample.mp4"),
            "silence_duration": "3.5",
            "noise_db": "-42",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 202
    assert response.get_json()["job_id"] == "job-1"


def test_job_rejects_duplicate_active_job(monkeypatch, tmp_path):
    class FakeManager:
        def public_job(self):
            return {"job_id": "existing", "state": "running"}

        def start(self, *args):
            raise RuntimeError("Another processing job is already running")

    input_file = tmp_path / "sample.mp4"
    input_file.write_bytes(b"video bytes")
    monkeypatch.setattr(server, "_probe_metadata", lambda path: {})
    app = create_app(FakeManager())

    response = app.test_client().post(
        "/api/jobs",
        json={"input_path": str(input_file)},
    )

    assert response.status_code == 400
    assert "already running" in response.get_json()["error"]


def test_cancel_endpoint_returns_cancelled_state():
    class FakeManager:
        def cancel(self, job_id):
            assert job_id == "job-1"
            return {"job_id": job_id, "state": "cancelled"}

    app = create_app(FakeManager())
    response = app.test_client().post("/api/jobs/job-1/cancel")

    assert response.status_code == 200
    assert response.get_json()["state"] == "cancelled"
