# Flask Bridge Specification

Status: Approved for implementation

## Purpose

Provide a small localhost HTTP bridge that allows a future React + Vite frontend to use the existing Python/FFmpeg processing pipeline.

## Scope

The bridge supports one active processing job at a time and exposes:

- Health check.
- Media metadata inspection.
- Start processing.
- Read current job status.
- Cancel the active job.

It does not provide authentication, cloud access, arbitrary command execution, file uploads, or desktop packaging.

## API contract

### `GET /api/health`

Returns `{ "ok": true }` when the bridge is running.

### `POST /api/metadata`

Request:

```json
{ "input_path": "/absolute/path/to/video" }
```

Success response includes path, filename, size, duration, and stream information from FFprobe.

### `POST /api/jobs`

Request:

```json
{
  "input_path": "/absolute/path/to/video",
  "silence_duration": 2.0,
  "noise_db": -60.0
}
```

The original file remains untouched. Successful output is an MP4 in the configured output directory.

### `GET /api/jobs/<job_id>`

Returns job state, progress, status message, output path, and error information.

States: `queued`, `running`, `completed`, `failed`, `cancelled`.

### `POST /api/jobs/<job_id>/cancel`

Cancels the active job when possible. Cancellation terminates the worker process and removes that job's temporary files.

## Validation

- Input path must exist and be a regular file.
- Silence duration must be between 0.1 and 60 seconds.
- Noise threshold must be between -100 and 0 dB.
- Only one job may run at a time.
- The bridge binds to `127.0.0.1` only.
- FFprobe validates that the input is readable media.
- The bridge uses subprocess argument arrays and does not execute user-provided shell commands.

## Acceptance criteria

- Flask bridge starts locally.
- Health endpoint returns successfully.
- Metadata endpoint rejects invalid input and returns valid metadata.
- Job endpoint rejects invalid settings and duplicate active jobs.
- Job execution passes both settings to the pipeline.
- Status can be polled until completion, failure, or cancellation.
- Cancellation is observable and does not delete the original file.
- Errors are returned as structured JSON.
- Existing processing tests remain passing.
