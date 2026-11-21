# All-Content Removal Safety Specification

Status: Implemented and verified

## Purpose

Prevent Silence Cutter from spending time exporting an MP4 when the selected silence settings would leave no meaningful video. This issue was found during a real Render deployment test: a four-minute input produced a near-zero-duration MP4 after almost two minutes of processing.

## Required behavior

- After silence detection and keep-interval construction, calculate retained duration before invoking FFmpeg export.
- If retained duration is 0.5 seconds or less, stop the job without creating an output file.
- Return `settings_warning` with input duration, estimated retained duration, and removed duration.
- Show a corrective UI message: use a lower (more negative) threshold or longer required silence duration.
- Preserve the existing `needs_confirmation` state for videos where no matching silence was found.
- Do not alter the original uploaded file.

## Non-goals

- Do not add a “render anyway” path for nearly empty video.
- Do not change FFmpeg encoding, file limits, or the stepper/progress design in this change.

## Acceptance evidence

- Pipeline tests cover fully removed and 0.25-second-retained inputs, and assert export is not called.
- Bridge test covers the `settings_warning` event and confirms no downloadable result is produced.
- Python test suite and Vite production build pass.

## Deferred UX revision

The approved next UX revision will merge **Select video** and **Set settings** into one step, rename **Process** to **Processing**, mark it complete only after processing reaches a terminal successful state, and mark **Done** complete only when an MP4 is downloadable. This is deferred until the processing-feedback phase.
