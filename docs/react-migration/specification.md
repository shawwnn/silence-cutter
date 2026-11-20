# Silence Cutter React + Vite Migration Specification

Status: Approved baseline

## Objective

Convert the current Python/CustomTkinter Silence Cutter MVP into a lightweight React + Vite portfolio project while preserving the existing Python/FFmpeg processing capability.

## User workflow

1. Select a video file.
2. Read and display basic metadata.
3. Configure minimum silence duration and silence threshold.
4. Start processing.
5. Observe status and progress.
6. Cancel processing when requested.
7. Receive a separate processed MP4 output.

The original input file must remain untouched.

## Approved settings

| Setting | Default | Allowed range |
|---|---:|---:|
| Minimum silence duration | 1.0 second | 0.1–60 seconds |
| Silence threshold | -38 dB | -100–0 dB |

These values map to FFmpeg's `silencedetect` `duration` and `noise` options.

## Input and output behavior

- Input selection should not rely on a short hardcoded extension list.
- FFprobe determines whether the selected file is a usable media input.
- Any input readable by the installed FFmpeg/FFprobe is eligible.
- Every successful result is written as a separate MP4 file.
- Existing outputs must not be overwritten without an explicit policy.
- Temporary files are isolated per processing job and cleaned afterward.

## Scope

### Included

- React + Vite frontend.
- Local Python bridge for real processing.
- Existing Python/FFmpeg backend retained as the processing source of truth.
- File selection and metadata display.
- Duration and dB controls.
- Processing, completion, failure, and cancellation states.
- Responsive layout for mobile-sized screens.
- Focused reliability fixes and tests.
- Spec-driven implementation records and Mermaid roadmap.

### Deferred

- Desktop installers.
- Native mobile application.
- Timeline or waveform editing.
- Manual interval selection.
- Batch processing.
- Pause/resume.
- Transcription, captions, and cloud processing.
- Processing history and export presets.

## Acceptance criteria

- The Vite application builds successfully.
- A valid video can be selected and inspected.
- Duration and dB settings are validated and sent to the bridge.
- A processing job reports states and progress where available.
- Cancellation stops the active job and cleans up its temporary files.
- The original input remains unchanged.
- A successful job produces a valid MP4.
- Invalid inputs and backend failures produce understandable errors.
- Existing backend behavior remains covered by tests.
- The responsive layout is usable on desktop and narrow screens.

## Architecture decision for Phase 0

Use a local Python bridge between the Vite frontend and the existing processing modules. The bridge contract will be specified before frontend implementation. The first implementation should remain lightweight and local; no database, authentication, cloud service, or installer is required.

## Non-functional constraints

- Use subprocess argument arrays; do not build shell commands from unsanitized strings.
- Preserve the original input file.
- Avoid loading entire videos into memory.
- Prevent duplicate active jobs.
- Keep user-facing errors separate from technical diagnostics.
- Record implementation evidence for each completed phase.
