"""Local bridge and deployment-safe HTTP API for the React frontend."""

from __future__ import annotations

import multiprocessing
import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from queue import Empty
from typing import Any

from flask import Flask, jsonify, request, send_file, send_from_directory

from app.bridge.media import probe_metadata
from app.bridge.job_state import public_job as build_public_job
from app.bridge.worker import run_worker
from app.bridge.validation import (
    validate_input,
    validate_public_video_size,
    validate_settings,
)
from app.output_naming import build_output_name


MAX_UPLOAD_BYTES = 100 * 1024 * 1024
MAX_INPUT_DURATION_SECONDS = 5 * 60
OUTPUT_RETENTION_SECONDS = 30 * 60
PUBLIC_MODE_ENV = "SILENCE_CUTTER_PUBLIC_MODE"


def _error(message: str, status: int = 400, code: str | None = None):
    payload = {"error": message}
    if code:
        payload["code"] = code
    return jsonify(payload), status


_probe_metadata = probe_metadata
_validate_settings = validate_settings
_validate_input = validate_input
_validate_public_video_size = validate_public_video_size


_worker = run_worker


class JobManager:
    """Owns one worker and every temporary file produced by that worker."""

    def __init__(self, output_dir: str | Path = "assets/outputs", *, storage_root: str | Path | None = None,
                 public_mode: bool = False, retention_seconds: int = OUTPUT_RETENTION_SECONDS):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.storage_root = Path(storage_root or tempfile.gettempdir())
        self.storage_root.mkdir(parents=True, exist_ok=True)
        self.public_mode, self.retention_seconds, self.job = public_mode, retention_seconds, None

    def _cleanup_job_files(self):
        if self.job and self.job.get("job_dir"):
            shutil.rmtree(self.job["job_dir"], ignore_errors=True)

    def _finalize_terminal_state(self):
        if not self.job:
            return
        state = self.job.get("state")
        if state in {"completed", "timing_warning"} and not self.job.get("completed_at"):
            self.job["completed_at"] = time.time()
        elif state in {"needs_confirmation", "settings_warning", "failed", "cancelled"}:
            self._cleanup_job_files()

    def _expire_if_needed(self):
        if not self.job or self.job.get("state") not in {"completed", "timing_warning"}:
            return
        completed_at = self.job.get("completed_at")
        if completed_at and time.time() >= completed_at + self.retention_seconds:
            self._cleanup_job_files()
            self.job.update({"state": "expired", "message": "Download expired and temporary files were deleted",
                             "error": None})

    def _refresh(self):
        if not self.job:
            return
        worker, events = self.job["worker"], self.job["events"]
        while True:
            try: self.job.update(events.get_nowait())
            except Empty: break
        if self.job.get("state") == "running" and not worker.is_alive():
            worker.join(timeout=0)
            while True:
                try: self.job.update(events.get(timeout=0.1))
                except Empty: break
            if self.job.get("state") == "running":
                self.job.update({"state": "failed", "error": "Processing stopped unexpectedly",
                                 "message": "Processing failed"})
        self._finalize_terminal_state()
        self._expire_if_needed()

    def public_job(self):
        self._refresh()
        return build_public_job(self.job, self.retention_seconds)

    def _start(self, input_path: Path, duration: float, noise_db: float, *, job_dir: Path,
               output_path: Path, output_name: str | None = None):
        self._refresh()
        if self.job and self.job.get("state") in {"queued", "running"}:
            raise RuntimeError("Another processing job is already running")
        # This MVP retains one job record. Starting another job intentionally
        # removes the previous terminal job's temporary files early.
        if self.job:
            self._cleanup_job_files()
        job_id, temp_dir, events = uuid.uuid4().hex, job_dir / "work", multiprocessing.Queue()
        temp_dir.mkdir(parents=True, exist_ok=True)
        worker = multiprocessing.Process(target=_worker, args=(str(input_path), str(output_path), duration,
            noise_db, str(temp_dir), events), daemon=True)
        self.job = {"job_id": job_id, "state": "queued", "progress": 0.0, "message": "Queued",
                    "events": events, "worker": worker, "job_dir": str(job_dir),
                    "output_file": str(output_path), "output_name": output_name or output_path.name}
        worker.start()
        self.job["state"] = "running"
        return self.public_job() or {}

    def start(self, input_path: Path, duration: float, noise_db: float):
        """Legacy local-path flow; public mode rejects it at the route boundary."""
        job_dir = Path(tempfile.mkdtemp(prefix="silence-cutter-local-"))
        output_name = build_output_name(input_path.name)
        output_path = self.output_dir / output_name
        return self._start(input_path, duration, noise_db, job_dir=job_dir, output_path=output_path)

    def start_upload(self, file_storage: Any, duration: float, noise_db: float):
        self._refresh()
        if self.job and self.job.get("state") in {"queued", "running"}:
            raise RuntimeError("Another processing job is already running")
        if file_storage is None or not file_storage.filename:
            raise ValueError("A video file is required")
        job_dir = Path(tempfile.mkdtemp(prefix="silence-cutter-job-", dir=self.storage_root))
        input_path = job_dir / f"input{Path(file_storage.filename).suffix.lower()}"
        try:
            file_storage.save(input_path)
            if input_path.stat().st_size > MAX_UPLOAD_BYTES:
                raise ValueError("Video must be 100 MB or smaller")
            media = _probe_metadata(input_path)
            if media.get("duration_seconds") and media["duration_seconds"] > MAX_INPUT_DURATION_SECONDS:
                raise ValueError("Video must be 5 minutes or shorter")
            if self.public_mode:
                _validate_public_video_size(media)
            if not media["has_audio"]:
                raise ValueError("This video has no audio track. Silence Cutter needs audio to detect silence.")
            output_name = build_output_name(file_storage.filename)
            job = self._start(input_path, duration, noise_db, job_dir=job_dir,
                              output_path=job_dir / output_name, output_name=output_name)
            return job, media
        except Exception:
            shutil.rmtree(job_dir, ignore_errors=True)
            raise

    def cancel(self, job_id: str):
        self._refresh()
        if not self.job or self.job.get("job_id") != job_id:
            raise KeyError("Job not found")
        if self.job.get("state") not in {"queued", "running"}:
            return self.public_job() or {}
        worker = self.job["worker"]
        if worker.is_alive():
            worker.terminate()
            worker.join(timeout=5)
        self.job.update({"state": "cancelled", "message": "Cancelled"})
        self._finalize_terminal_state()
        return self.public_job() or {}

    def download_path(self, job_id: str):
        self._refresh()
        if not self.job or self.job.get("job_id") != job_id:
            raise KeyError("Job not found")
        if self.job.get("state") == "expired":
            raise FileNotFoundError("Download expired and temporary files were deleted")
        if self.job.get("state") not in {"completed", "timing_warning"}:
            raise RuntimeError("Output is not ready to download")
        output_file = Path(self.job["output_file"])
        if not output_file.is_file():
            raise FileNotFoundError("Processed output is unavailable")
        return output_file

    def download_name(self, job_id: str) -> str:
        self._refresh()
        if not self.job or self.job.get("job_id") != job_id:
            raise KeyError("Job not found")
        return self.job.get("output_name", "silence-cutter.mp4")


def _is_public_mode(public_mode: bool | None) -> bool:
    return public_mode if public_mode is not None else os.environ.get(PUBLIC_MODE_ENV, "").lower() in {"1", "true", "yes"}


def create_app(job_manager: JobManager | None = None, *, public_mode: bool | None = None) -> Flask:
    public_mode = _is_public_mode(public_mode)
    web_dist = Path(__file__).resolve().parents[2] / "web-dist"
    assets_dir = web_dist / "assets"
    app = Flask(
        __name__,
        static_folder=str(assets_dir) if assets_dir.is_dir() else None,
        static_url_path="/assets",
    )
    app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES
    manager = job_manager or JobManager(public_mode=public_mode)

    @app.errorhandler(413)
    def request_too_large(_error_value): return _error("Video must be 100 MB or smaller", 413, "file_too_large")

    @app.get("/api/health")
    def health(): return jsonify({"ok": True, "public_mode": public_mode})

    @app.post("/api/metadata")
    def metadata():
        if public_mode:
            return _error("Metadata preflight is unavailable in the public demo; start a job instead", 405)
        try:
            if request.files.get("file"):
                temp_dir = Path(tempfile.mkdtemp(prefix="silence-cutter-metadata-"))
                try:
                    input_path = temp_dir / f"input{Path(request.files['file'].filename).suffix.lower()}"
                    request.files["file"].save(input_path)
                    if input_path.stat().st_size > MAX_UPLOAD_BYTES:
                        return _error("Video must be 100 MB or smaller", 413, "file_too_large")
                    return jsonify(_probe_metadata(input_path))
                finally: shutil.rmtree(temp_dir, ignore_errors=True)
            return jsonify(_probe_metadata(_validate_input((request.get_json(silent=True) or {}).get("input_path"))))
        except (ValueError, RuntimeError) as exc: return _error(str(exc))

    @app.post("/api/jobs")
    def start_job():
        payload = request.form.to_dict() if request.files else (request.get_json(silent=True) or {})
        try:
            duration, noise_db = _validate_settings(payload)
            if request.files.get("file"):
                job, media = manager.start_upload(request.files["file"], duration, noise_db)
                return jsonify({**job, "media": media}), 202
            if public_mode: return _error("A video upload is required", code="file_required")
            path = _validate_input(payload.get("input_path"))
            media = _probe_metadata(path)
            if not media["has_audio"]:
                return _error("This video has no audio track. Silence Cutter needs audio to detect silence.", code="missing_audio")
            return jsonify(manager.start(path, duration, noise_db)), 202
        except ValueError as exc:
            return _error(str(exc), code="missing_audio" if "no audio track" in str(exc) else None)
        except RuntimeError as exc:
            return _error(str(exc), 409 if "already running" in str(exc) else 400)

    @app.get("/api/jobs/<job_id>")
    def job_status(job_id: str):
        job = manager.public_job()
        return jsonify(job) if job and job["job_id"] == job_id else _error("Job not found", 404)

    @app.post("/api/jobs/<job_id>/cancel")
    def cancel_job(job_id: str):
        try: return jsonify(manager.cancel(job_id))
        except KeyError as exc: return _error(str(exc), 404)

    @app.get("/api/jobs/<job_id>/download")
    def download(job_id: str):
        try:
            return send_file(manager.download_path(job_id), as_attachment=True,
                             download_name=manager.download_name(job_id), mimetype="video/mp4")
        except KeyError as exc: return _error(str(exc), 404)
        except FileNotFoundError as exc: return _error(str(exc), 404, "download_expired")
        except RuntimeError as exc: return _error(str(exc), 409)

    @app.post("/api/jobs/<job_id>/open-output-folder")
    def open_output_folder(job_id: str):
        if public_mode: return _error("Use the download link in the public demo", 410, "local_only")
        try: output_file = manager.download_path(job_id)
        except (KeyError, FileNotFoundError, RuntimeError) as exc: return _error(str(exc), 404)
        output_folder = str(output_file.resolve().parent)
        if sys.platform == "darwin": subprocess.Popen(["open", output_folder])
        elif os.name == "nt": os.startfile(output_folder)
        else: subprocess.Popen(["xdg-open", output_folder])
        return jsonify({"opened": True})

    if web_dist.is_dir():
        @app.get("/")
        def index(): return send_from_directory(web_dist, "index.html")

        @app.get("/<path:path>")
        def frontend(path: str):
            return send_from_directory(web_dist, path) if (web_dist / path).is_file() else send_from_directory(web_dist, "index.html")
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5050")), debug=False)
