# Render Portfolio Deployment Specification

Status: Deployed from `main`; real uploaded-video smoke test pending

Baseline: [React + Vite Migration Specification](../react-migration/specification.md)

## Purpose

Make Silence Cutter presentable as a small, public portfolio demo without turning the existing local MVP into an unlimited video-processing service. A visitor must be able to upload a small video, remove detected silence, and download a separate MP4. The service must automatically remove visitor media after a short retention period.

## Approved deployment decisions

| Decision | Approved value |
|---|---:|
| Hosting | One Docker-based Render web service |
| Public URL | Render `onrender.com` URL initially |
| Maximum upload size | 100 MB |
| Maximum input duration | 5 minutes |
| Maximum public resolution | 1080p / 2.07 megapixels |
| Output retention | Up to 30 minutes after completion |
| Concurrency | One active processing job per service |
| Output | Separate H.264/AAC MP4 download named `<source-stem>_cut_<local-server-timestamp>.mp4` |
| Authentication | None for the portfolio MVP |
| Original input | Never modified; temporary server copy deleted after retention |

## Existing-system assessment

### Reusable functionality

- `src/api.js` already sends a selected `File` as multipart form data.
- `POST /api/metadata` and `POST /api/jobs` already accept multipart form data.
- FFprobe validates media and detects audio/video streams.
- The processing pipeline creates an accurate MP4 through a single FFmpeg filter graph.
- The job manager already limits the process to one active job and supports cancellation.

### Deployment gaps

- The Flask bridge binds only to `127.0.0.1:5050`; Render requires a public bind on `0.0.0.0` and its supplied `PORT`.
- Multipart uploads have no maximum request/file size and are saved before a size check.
- A job's upload directory is not owned or removed by `JobManager` after a successful job.
- Outputs are written to `assets/outputs`, persist indefinitely, and are named from visitor filenames.
- The API exposes `output_path`; a public API must not disclose server filesystem paths.
- The UI's **Open output folder** action is meaningful only on the local machine. A public browser needs an authenticated-by-job download URL instead.
- The legacy JSON `input_path` flow must remain local-only and be disabled for public deployment.
- The service has no expiry cleanup, no privacy notice, no rate/concurrency guard beyond a single in-memory job, and no production WSGI/Docker configuration.

## Expected public behavior

1. Visitor selects a video under 100 MB.
2. The client shows the upload limit and posts the file plus settings once to create a job.
3. The server streams the upload into an unpredictable per-job temporary directory and rejects oversized requests.
4. FFprobe rejects unreadable media, video without audio, and input longer than five minutes.
5. The public demo rejects video streams above 1080p / 2.07 megapixels before processing.
6. The existing processor runs once; the source server copy is never modified.
7. The frontend polls status exactly as it does today, without receiving server paths.
8. On success, the interface shows **Download MP4**. The download uses a source-based name such as `goo test_cut_2026-11-21_14-32-08.mp4` and works only for that job while it is retained.
9. Cancellation, failure, no-silence, completion, and expired jobs remove temporary media safely.
10. After up to 30 minutes, the job and its downloadable file are unavailable and the UI explains that it expired. Starting a new job may delete the previous job earlier because this MVP retains one job record.

## API contract changes

| Endpoint | Public deployment behavior |
|---|---|
| `POST /api/jobs` | Multipart-only in deployed mode; file and settings create one job. Reject more than 100 MB before storing further bytes where supported. |
| `POST /api/metadata` | Optional preflight only. It must use the same limits and must not retain media. To avoid uploading twice, the deployed UI should create a job directly rather than preflight-upload then re-upload. |
| `GET /api/jobs/<job_id>` | Return public state, progress, message, and summary only—never `input_path`, `output_path`, temp directory, or FFmpeg diagnostics. |
| `GET /api/jobs/<job_id>/download` | Send the completed MP4 as an attachment only while the job is retained. Return `404` for unknown/expired jobs and `409` before completion. |
| `POST /api/jobs/<job_id>/cancel` | Retain cancellation behavior and remove all job files. |
| `POST /api/jobs/<job_id>/open-output-folder` | Local-only endpoint; omit or return unavailable in deployed mode. |

## Acceptance criteria

- The production container starts with Gunicorn on `0.0.0.0:$PORT` and includes FFmpeg/FFprobe.
- A 100 MB-or-smaller valid input can be uploaded once, processed, and downloaded as a separate MP4.
- A request above 100 MB is rejected with a clear `413` response and no retained upload.
- A readable video over five minutes is rejected before processing.
- A public video above 1080p / 2.07 megapixels is rejected before processing; local mode remains unrestricted.
- No JSON response exposes a server file path.
- No job media remains after cancellation, failure, no-silence, or the 30-minute expiry.
- The one-job concurrency rule produces a clear busy response without corrupting either job.
- The original local source file is never changed.
- Existing accurate-export, no-audio, cancellation, and duration-verification behavior remains tested.
- `npm run build`, the Python test suite, a container build, and a manual live Render smoke test pass.

## Implementation tasks and verification

| ID | Files | Expected result | Verification |
|---|---|---|---|
| D1 | `app/bridge/server.py`, new tests | Create a job-owned directory, bounded upload stream, and expiry cleanup; separate local/public mode. | Unit tests for size, duration, cleanup, expiry, and no leaked paths. |
| D2 | `app/bridge/server.py`, new tests | Add download endpoint and remove folder-opening behavior from public mode. | Test pending/complete/expired downloads. |
| D3 | `src/api.js`, `src/main.jsx`, `src/components.jsx` | Create one job from the selected file; replace folder-open with download; show size/expiry notices. | Vite build and browser-flow manual test. |
| D4 | `requirements.txt`, `Dockerfile`, `.dockerignore`, optional `render.yaml` | Build a reproducible app image with FFmpeg, React assets, and Gunicorn. | Local `docker build` and health check. |
| D5 | `README.md`, deployment docs | Explain privacy/retention, free-tier sleep behavior, and live URL. | Documentation review against actual behavior. |
| D6 | `tests/`, `docs/react-migration/implementation-record.md` | Record test evidence and final deployment outcome. | Automated suite and Render smoke-test checklist. |

## Risks and safeguards

| Risk | Safeguard |
|---|---|
| Free service exhaustion or abuse | 100 MB, five-minute, and one-job limits; clear busy/size errors. |
| Visitor media retention | Per-job directories, cleanup on terminal states, expiry sweep, and documented 30-minute window. |
| Sensitive server paths or logs exposed | Public job serializer allowlist; generic user errors; server diagnostics stay in service logs. |
| FFmpeg resource usage | Strict input limits, one active process, no permanent uploads, and a lightweight portfolio-only scope. |
| Free instance restart during export | Reject high-resolution public inputs before export and show a clear recovery message if an upstream response is interrupted. |
| Free Render cold starts | Explain wake-up delay in the README and portfolio copy. |
| Regression of local development | Preserve a documented local mode; test both mode boundaries rather than silently changing local workflow. |

## Out of scope

- User accounts, permanent saved projects, database storage, payment, or queues.
- CDN/object storage, background workers, or multi-instance scaling.
- Uploading arbitrary non-video content or supporting unlimited file types/sizes.
- Claiming production-grade availability or privacy compliance beyond the documented temporary-demo behavior.

## Deployment record

The public deployment is live at [silence-cutter-portfolio.onrender.com](https://silence-cutter-portfolio.onrender.com/), using the free Render plan and Render service `silence-cutter-portfolio`. On 2026-11-21, its tracked branch changed from the temporary `feature/react-vite-migration` branch to `main`; Render successfully deployed main commit `ee219c8` in 40.8 seconds. The Render build log confirms checkout from `main`; `/api/health` returned `{"ok":true,"public_mode":true}` and the public React interface loaded with the revised workflow steps.

Manual testing later exposed a Render instance restart during Phase 5 (FFmpeg export) for a 5.2 MB, 1:25 input that succeeded locally. The browser received an empty response and previously showed a JSON parsing error. The code now handles unavailable/non-JSON service responses with a recovery message and rejects public video streams above 1080p / 2.07 megapixels before creating a job. The exact restart reason was not labeled in Render logs; free-instance resource exhaustion is the working hypothesis. Public exports now also bound FFmpeg/filter parallelism to one thread and use a lighter encoding preset; local exports retain the original quality profile.

Local Docker verification was skipped because the workspace could not access the Docker engine. A manual uploaded-video smoke test remains required before considering the deployment fully verified.
