# Processing Feedback Bug-Fix Specification

## Purpose

Address verified usability and processing-result defects without expanding the approved MVP into a UI redesign.

## Requirements

- Disable duration and dB controls while a job is active; restore them after completion, failure, cancellation, or a failed job-start request.
- Display the selected file extension, human-readable size, and human-readable duration.
- Provide an output-folder action only after successful processing.
- Report input duration, output duration, detected silence count, and removed duration after a job completes.
- Explain when no silence meets the chosen duration and dB criteria.
- Stop before segment generation when no silence meets the criteria; do not create output.
- Preserve the original input file.

## Deferred

- Full-screen or cinematic processing experience.
- Timeline, waveform, and visual preview editing.

## Acceptance criteria

- Failed job creation re-enables the controls.
- Completion exposes an output-folder action that opens only the completed job's output directory.
- A no-silence result is distinguishable from a failed job.
- A no-silence result creates no output.
- The UI does not report a completed worker as unexpectedly stopped.
