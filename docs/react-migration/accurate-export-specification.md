# Accurate FFmpeg Export Specification

Status: Approved for implementation

## Problem

The existing engine stream-copies independently cut segments and concatenates them. This may cut at nearby keyframes rather than the requested timestamps and can introduce visible/audio glitches or timestamp discontinuities.

## Solution

Render every retained interval in one FFmpeg filter graph:

1. `trim` and reset video timestamps for each interval.
2. `atrim` and reset audio timestamps for each interval.
3. Concatenate normalized video/audio pairs.
4. Encode one MP4 using H.264 video and AAC audio.

## Acceptance criteria

- No intermediate segment files or concat-list file are used for normal exports.
- The command uses the requested interval boundaries.
- The result maps one video and one audio output from the filter graph.
- FFmpeg errors include useful diagnostics.
- Existing tests and new filter-graph tests pass.
