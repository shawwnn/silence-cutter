# MVP Refactor Plan

Status: reference plan after MVP completion

Current checkpoint: `main` at `8d58830` (`docs: close MVP verification records`)

## Decision

Use a lightweight layered architecture. Apply hexagonal architecture ideas only where they solve a real problem; do not introduce enterprise-style abstractions, dependency-injection frameworks, or interfaces for every function.

The main boundary is:

```text
React UI / Desktop GUI
          ↓
Flask bridge or desktop adapter
          ↓
Application service: process_video()
          ↓
Existing silence, interval, and FFmpeg modules
```

The video-processing core must not depend on React, Flask, desktop GUI code, or HTTP details.

## Why this fits the current codebase

The repository is still small and already has useful processing modules. A full rewrite into ports, adapters, and many classes would add ceremony without improving the MVP. Refactoring should preserve the existing modules where they are clear and introduce boundaries incrementally.

## Target responsibilities

- **Processing core:** detect silence, parse intervals, build retained intervals, export video, and validate output.
- **Application service:** coordinate one complete video-processing job and return a stable result.
- **Adapters:** translate desktop actions, HTTP requests, FFmpeg execution, and filesystem operations into calls the application service understands.
- **React UI:** manage screen state and display progress, errors, settings, and results. It must not duplicate FFmpeg or silence rules.

## Refactor order

1. Preserve current behavior with the existing tests.
2. Extract one clear `process_video()` application service from the current pipeline.
3. Make the desktop GUI call that service.
4. Make the Flask bridge call the same service.
5. Split bridge responsibilities only when useful: routes, validation, job management, and response serialization.
6. Organize React around the video-processing feature and API state.
7. Remove duplicated or obsolete paths only after the replacement is tested.

## Guardrails

- Do not rewrite the desktop app, bridge, React UI, and processing logic in one change.
- Do not change API contracts and processing behavior in the same refactor step.
- Do not add abstractions without a concrete caller, test, or integration need.
- Run backend tests and the frontend build after each small slice.
- Keep the original desktop path working until the bridge uses the shared service successfully.

## Suggested future shape

```text
app/
  processing/       # existing silence and FFmpeg rules, moved only when useful
  application/      # complete use cases such as process_video()
  bridge/           # Flask routes, jobs, validation, serializers
  gui/              # desktop adapter

src/
  api/
  features/video-processing/
  components/
```

This structure is a direction, not a requirement to move every current file immediately.

## Completed checkpoints

- Gate 1: named the shared Python application service `process_video()`.
- Gate 2: migrated the desktop GUI to `process_video()`.
- Gate 3: migrated the Flask worker to `process_video()`.
- Gate 4: isolated bridge media probing, validation, job-state formatting, and the background worker.
- Gate 5: organized React media utilities, job polling, and terminal job outcomes under `src/features/video-processing/`.

Compatibility aliases remain in the bridge and `main.py` where tests or older callers still use the previous names. They are adapters, not duplicate implementations.
