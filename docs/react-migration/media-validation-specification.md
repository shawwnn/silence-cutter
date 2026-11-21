# Media Validation Specification

Status: Approved for implementation

## Missing audio

- Metadata returns `has_audio` and `has_video`.
- The UI blocks processing when a selected video has no audio track.
- The job endpoint repeats the audio validation and returns `missing_audio` if bypassed.

## Duration verification

- Expected duration is the sum of retained intervals.
- Actual duration is read from the exported MP4 with FFprobe.
- A result is verified when the difference is no more than 0.25 seconds.
- A non-verified output is preserved for inspection but reported as a timing warning, not a success.

## Acceptance criteria

- No-audio media cannot start a job.
- Valid exports include expected duration, actual duration, difference, and verification status.
- Timing-warning results expose the output folder without calling the export successful.
