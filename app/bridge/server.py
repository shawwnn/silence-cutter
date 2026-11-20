"""Small localhost Flask bridge for React/Vite integration."""

from __future__ import annotations

import json
import multiprocessing
import os
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request

from app.main import run_pipeline


MIN_DURATION = 0.1
MAX_DURATION = 60.0
MIN_NOISE_DB = -100.0
MAX_NOISE_DB = 0.0


def _error(message: str, status: int = 400):
    return jsonify({"error": message}), status


def _validate_settings(payload: dict[str, Any]):
    try:
        duration = float(payload.get("silence_duration", 2.0))
        noise_db = float(payload.get("noise_db", -60.0))
    except (TypeError, ValueError):
        raise ValueError("silence_duration and noise_db must be numbers")

    if not MIN_DURATION <= duration <= MAX_DURATION:
        raise ValueError("silence_duration must be between 0.1 and 60 seconds")
    if not MIN_NOISE_DB <= noise_db <= MAX_NOISE_DB:
        raise ValueError("noise_db must be between -100 and 0 dB")

    return duration, noise_db


def _validate_input(input_path: Any) -> Path:
    if not isinstance(input_path, str) or not input_path.strip():
        raise ValueError("input_path is required")

    path = Path(input_path).expanduser().resolve()
    if not path.is_file():
        raise ValueError("input_path must point to an existing file")
    return path


def _probe_metadata(path: Path) -> dict[str, Any]:
    if shutil.which("ffprobe") is None:
        raise RuntimeError("FFprobe was not found on PATH")

    command = [
        "ffprobe", "-v", "error", "-show_format", "-show_streams",
        "-of", "json", str(path)
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise ValueError("FFprobe could not read this media file")

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("FFprobe returned invalid metadata") from exc

    streams = data.get("streams", [])
    if not any(stream.get("codec_type") == "video" for stream in streams):
        raise ValueError("The selected file does not contain a video stream")

    format_data = data.get("format", {})
    duration = format_data.get("duration")
    return {
        "path": str(path),
        "filename": path.name,
        "size_bytes": path.stat().st_size,
        "duration_seconds": float(duration) if duration else None,
        "format": format_data.get("format_name"),
        "streams": [
            {
                "codec_type": stream.get("codec_type"),
                "codec_name": stream.get("codec_name"),
                "width": stream.get("width"),
                "height": stream.get("height"),
            }
            for stream in streams
        ],
    }


def _save_upload(file_storage) -> tuple[Path, str]:
    if file_storage is None or not file_storage.filename:
        raise ValueError("A video file is required")

    upload_dir = Path(tempfile.mkdtemp(prefix="silence-cutter-upload-"))
    safe_name = Path(file_storage.filename).name
    input_path = upload_dir / safe_name
    file_storage.save(input_path)
    return input_path, str(upload_dir)


def _worker(job_id: str, input_path: str, output_path: str,
            duration: float, noise_db: float, temp_dir: str,
            events: multiprocessing.Queue):
    def progress(value):
        events.put({"type": "progress", "value": value})

    def status(message):
        events.put({"type": "status", "message": message})

    try:
        result = run_pipeline(
            input_path,
            output_path=output_path,
            progress_callback=progress,
            status_callback=status,
            silence_duration=duration,
            noise_db=noise_db,
            temp_dir=temp_dir,
        )
        events.put({"type": "completed", "output_path": result})
    except Exception as exc:  # worker boundary must report failures to the API
        events.put({"type": "failed", "error": str(exc)})


class JobManager:
    """Owns one cancellable processing worker and its temporary directory."""

    def __init__(self, output_dir: str | Path = "assets/outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.job: dict[str, Any] | None = None

    def _refresh(self):
        if not self.job:
            return

        worker = self.job["worker"]
        events = self.job["events"]
        while not events.empty():
            event = events.get()
            self.job.update(event)

        if self.job.get("state") == "running" and not worker.is_alive():
            self.job["state"] = "failed"
            self.job.setdefault("error", "Processing stopped unexpectedly")

    def public_job(self):
        self._refresh()
        if not self.job:
            return None
        return {
            key: self.job.get(key)
            for key in (
                "job_id", "state", "progress", "message", "error",
                "output_path"
            )
        }

    def start(self, input_path: Path, duration: float, noise_db: float):
        self._refresh()
        if self.job and self.job.get("state") in {"queued", "running"}:
            raise RuntimeError("Another processing job is already running")

        job_id = uuid.uuid4().hex
        temp_dir = tempfile.mkdtemp(prefix=f"silence-cutter-{job_id}-")
        output_path = self.output_dir / f"{input_path.stem}_cut.mp4"
        if output_path.exists():
            output_path = self.output_dir / f"{input_path.stem}_cut_{job_id[:8]}.mp4"

        events = multiprocessing.Queue()
        worker = multiprocessing.Process(
            target=_worker,
            args=(job_id, str(input_path), str(output_path), duration,
                  noise_db, temp_dir, events),
            daemon=True,
        )
        self.job = {
            "job_id": job_id,
            "state": "queued",
            "progress": 0.0,
            "message": "Queued",
            "events": events,
            "worker": worker,
            "temp_dir": temp_dir,
            "output_path": str(output_path),
        }
        worker.start()
        self.job["state"] = "running"
        return self.public_job()

    def cancel(self, job_id: str):
        self._refresh()
        if not self.job or self.job.get("job_id") != job_id:
            raise KeyError("Job not found")
        if self.job.get("state") not in {"queued", "running"}:
            return self.public_job()

        worker = self.job["worker"]
        if worker.is_alive():
            worker.terminate()
            worker.join(timeout=5)
        self.job["state"] = "cancelled"
        self.job["message"] = "Cancelled"
        shutil.rmtree(self.job["temp_dir"], ignore_errors=True)
        return self.public_job()


def create_app(job_manager: JobManager | None = None) -> Flask:
    app = Flask(__name__)
    manager = job_manager or JobManager()

    @app.get("/api/health")
    def health():
        return jsonify({"ok": True})

    @app.post("/api/metadata")
    def metadata():
        try:
            if request.files.get("file"):
                path, upload_dir = _save_upload(request.files["file"])
                try:
                    return jsonify(_probe_metadata(path))
                finally:
                    shutil.rmtree(upload_dir, ignore_errors=True)
            payload = request.get_json(silent=True) or {}
            path = _validate_input(payload.get("input_path"))
            return jsonify(_probe_metadata(path))
        except (ValueError, RuntimeError) as exc:
            return _error(str(exc))

    @app.post("/api/jobs")
    def start_job():
        payload = request.form.to_dict() if request.files else (request.get_json(silent=True) or {})
        try:
            upload_dir = None
            if request.files.get("file"):
                path, upload_dir = _save_upload(request.files["file"])
            else:
                path = _validate_input(payload.get("input_path"))
            duration, noise_db = _validate_settings(payload)
            _probe_metadata(path)
            return jsonify(manager.start(path, duration, noise_db)), 202
        except (ValueError, RuntimeError) as exc:
            if upload_dir:
                shutil.rmtree(upload_dir, ignore_errors=True)
            return _error(str(exc))

    @app.get("/api/jobs/<job_id>")
    def job_status(job_id: str):
        job = manager.public_job()
        if not job or job["job_id"] != job_id:
            return _error("Job not found", 404)
        return jsonify(job)

    @app.post("/api/jobs/<job_id>/cancel")
    def cancel_job(job_id: str):
        try:
            return jsonify(manager.cancel(job_id))
        except KeyError as exc:
            return _error(str(exc), 404)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
