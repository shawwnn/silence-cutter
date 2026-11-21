# Accurate Export Timing Test Specification

Status: Approved for implementation

## Scope

Verify the accurate filter-graph exporter with generated local media fixtures. No user-facing missing-audio or duration-validation behavior is added in this task.

## Fixtures

- Retained content after a cut at the beginning.
- Retained content before a cut at the end.
- Two retained sections separated by a cut in the middle.
- Three retained sections separated by multiple cuts.

## Acceptance criteria

- Each fixture exports a playable MP4.
- FFprobe-reported output duration is within 0.15 seconds of the sum of retained intervals.
- Tests skip only when FFmpeg or FFprobe is not installed.
