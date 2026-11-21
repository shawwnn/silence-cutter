# Reference UI Revamp Specification

Status: Approved for implementation

## Purpose

Replace the minimal React presentation with the approved Fusion reference design while preserving the existing Flask/Python/FFmpeg behavior.

## Included

- Dark workspace, header, hero, workflow steps, video stage, settings panel, processing, completion, no-silence, cancellation, and error states.
- Drag-and-drop and browse file selection.
- Real Flask endpoint integration.
- Duration and dB controls using the original desktop defaults: 1.0 second and -38 dB.
- User-facing sliders are centered around their preferred defaults: 0.1–1.9 seconds and -60 to -16 dB.

## Excluded

- Reference Express server, preview bridge, desktop-shell bridge, and unused generic UI components.
- Full-screen processing redesign.

## Acceptance criteria

- The reference workflow is represented with real backend states.
- Controls lock only while processing and unlock on every terminal state.
- No-silence behavior creates no output.
- Build and existing Python tests pass.
