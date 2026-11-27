"""Convert internal job state into the bridge's public response shape."""

from __future__ import annotations

import time
from typing import Any


PUBLIC_RESULT_FIELDS = {
    "input_duration_seconds",
    "expected_duration_seconds",
    "output_duration_seconds",
    "duration_difference_seconds",
    "duration_verified",
    "detected_silence_count",
    "removed_duration_seconds",
}


def public_result(job: dict[str, Any]) -> dict[str, Any] | None:
    result = job.get("result")
    if not result:
        return None
    return {key: value for key, value in result.items() if key in PUBLIC_RESULT_FIELDS}


def public_job(job: dict[str, Any] | None, retention_seconds: int) -> dict[str, Any] | None:
    if not job:
        return None
    completed_at = job.get("completed_at")
    return {
        "job_id": job["job_id"],
        "state": job.get("state"),
        "progress": job.get("progress"),
        "message": job.get("message"),
        "error": job.get("error"),
        "result": public_result(job),
        "download_available": job.get("state") in {"completed", "timing_warning"},
        "expires_in_seconds": max(0, int(completed_at + retention_seconds - time.time()))
        if completed_at else None,
    }
