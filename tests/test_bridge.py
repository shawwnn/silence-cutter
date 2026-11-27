import io
from pathlib import Path

from app.bridge import server
from app.bridge import worker
from app.bridge.server import JobManager, create_app
from app.pipeline.insufficient_retained_content import InsufficientRetainedContent
from app.output_naming import build_output_name


def test_health_endpoint(tmp_path):
    app = create_app(JobManager(tmp_path / "outputs"))
    response = app.test_client().get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {"ok": True, "public_mode": False}


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
        def start_upload(self, file_storage, duration, noise_db):
            assert file_storage.filename == "sample.mp4"
            assert duration == 3.5
            assert noise_db == -42.0
            return ({"job_id": "job-1", "state": "running"}, {"has_audio": True})

        def public_job(self):
            return None

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
    assert response.get_json()["media"] == {"has_audio": True}


def test_job_rejects_duplicate_active_job(monkeypatch, tmp_path):
    class FakeManager:
        def public_job(self):
            return {"job_id": "existing", "state": "running"}

        def start(self, *args):
            raise RuntimeError("Another processing job is already running")

    input_file = tmp_path / "sample.mp4"
    input_file.write_bytes(b"video bytes")
    monkeypatch.setattr(server, "_probe_metadata", lambda path: {"has_audio": True})
    app = create_app(FakeManager())

    response = app.test_client().post(
        "/api/jobs",
        json={"input_path": str(input_file)},
    )

    assert response.status_code == 409
    assert "already running" in response.get_json()["error"]


def test_job_rejects_video_without_audio(monkeypatch, tmp_path):
    class FakeManager:
        def start(self, *args):
            pytest.fail("must not start a job without audio")

    input_file = tmp_path / "silent-video.mp4"
    input_file.write_bytes(b"video bytes")
    monkeypatch.setattr(server, "_probe_metadata", lambda path: {"has_audio": False})
    app = create_app(FakeManager())

    response = app.test_client().post("/api/jobs", json={"input_path": str(input_file)})

    assert response.status_code == 400
    assert response.get_json()["code"] == "missing_audio"


def test_cancel_endpoint_returns_cancelled_state():
    class FakeManager:
        def cancel(self, job_id):
            assert job_id == "job-1"
            return {"job_id": job_id, "state": "cancelled"}

    app = create_app(FakeManager())
    response = app.test_client().post("/api/jobs/job-1/cancel")

    assert response.status_code == 200
    assert response.get_json()["state"] == "cancelled"


def test_public_mode_rejects_legacy_local_path_and_metadata_preflight(tmp_path):
    app = create_app(JobManager(tmp_path / "outputs"), public_mode=True)

    metadata = app.test_client().post("/api/metadata", json={"input_path": "/tmp/video.mp4"})
    job = app.test_client().post("/api/jobs", json={"input_path": "/tmp/video.mp4"})

    assert metadata.status_code == 405
    assert job.status_code == 400
    assert job.get_json()["code"] == "file_required"


def test_public_mode_rejects_oversized_request_before_job_creation(tmp_path):
    app = create_app(JobManager(tmp_path / "outputs"), public_mode=True)
    app.config["MAX_CONTENT_LENGTH"] = 1

    response = app.test_client().post(
        "/api/jobs",
        data={"file": (io.BytesIO(b"too large"), "sample.mp4")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 413
    assert response.get_json()["code"] == "file_too_large"


def test_public_mode_rejects_video_above_1080p_before_starting(monkeypatch, tmp_path):
    manager = JobManager(tmp_path / "outputs", public_mode=True)
    monkeypatch.setattr(server, "_probe_metadata", lambda path: {
        "has_audio": True, "duration_seconds": 30,
        "streams": [{"codec_type": "video", "width": 3840, "height": 2160}],
    })
    monkeypatch.setattr(manager, "_start", lambda *args, **kwargs: pytest.fail("must not start"))
    app = create_app(manager, public_mode=True)

    response = app.test_client().post(
        "/api/jobs", data={"file": (io.BytesIO(b"video bytes"), "large.mp4")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Public demo supports videos up to 1080p. Use a lower-resolution video."


def test_local_mode_does_not_apply_public_resolution_limit(monkeypatch, tmp_path):
    manager = JobManager(tmp_path / "outputs", public_mode=False)
    monkeypatch.setattr(server, "_probe_metadata", lambda path: {
        "has_audio": True, "duration_seconds": 30,
        "streams": [{"codec_type": "video", "width": 3840, "height": 2160}],
    })
    monkeypatch.setattr(manager, "_start", lambda *args, **kwargs: {"job_id": "local-job"})

    job, _media = manager.start_upload(type("Upload", (), {
        "filename": "large.mp4", "save": lambda self, path: Path(path).write_bytes(b"video bytes"),
    })(), 1.0, -38.0)

    assert job == {"job_id": "local-job"}


def test_public_job_hides_filesystem_paths(tmp_path):
    manager = JobManager(tmp_path / "outputs", public_mode=True)
    manager.job = {
        "job_id": "job-1",
        "state": "completed",
        "progress": 1.0,
        "message": "Completed",
        "result": {"output_path": "/private/server/output.mp4", "input_duration_seconds": 10},
        "completed_at": server.time.time(),
        "worker": type("Worker", (), {"is_alive": lambda self: False})(),
        "events": type("Events", (), {"get_nowait": lambda self: (_ for _ in ()).throw(server.Empty)})(),
    }

    public = manager.public_job()

    assert public["result"] == {"input_duration_seconds": 10}
    assert "output_path" not in public
    assert "/private/server" not in str(public)


def test_expired_public_job_deletes_job_directory(tmp_path):
    job_dir = tmp_path / "job"
    job_dir.mkdir()
    (job_dir / "output.mp4").write_bytes(b"output")
    manager = JobManager(tmp_path / "outputs", public_mode=True, retention_seconds=1)
    manager.job = {"state": "completed", "job_dir": str(job_dir), "completed_at": server.time.time() - 2}

    manager._expire_if_needed()

    assert manager.job["state"] == "expired"
    assert not job_dir.exists()


def test_worker_reports_over_cut_without_a_downloadable_output(monkeypatch):
    class Events:
        def __init__(self): self.items = []
        def put(self, item): self.items.append(item)
        def close(self): pass
        def join_thread(self): pass

    monkeypatch.setattr(worker, "process_video", lambda *args, **kwargs: (_ for _ in ()).throw(
        InsufficientRetainedContent(254.0, 0.25, 253.75)
    ))
    events = Events()

    server._worker("input.mp4", "output.mp4", 1.0, -38.0, "temp", events)

    assert events.items[-1] == {
        "type": "over_cut", "state": "settings_warning",
        "message": "Selected settings would remove virtually the entire video",
        "result": {
            "input_duration_seconds": 254.0, "expected_duration_seconds": 0.25,
            "output_duration_seconds": None, "removed_duration_seconds": 253.75,
        },
    }
