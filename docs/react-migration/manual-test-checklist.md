# Manual Test Checklist

Run this checklist when a laptop and a representative video are available.

## Start

Terminal 1:

```bash
python3 -m app.bridge.server
```

Terminal 2:

```bash
npm run dev
```

Open the Vite URL, normally `http://localhost:5173`.

## Workflow

- [ ] Select a valid video.
- [ ] Confirm metadata appears.
- [ ] Confirm a no-audio video shows a blocked, understandable warning.
- [ ] Change silence duration from `1.0` second.
- [ ] Change noise threshold from `-38 dB`.
- [ ] Start processing.
- [ ] Confirm status changes while processing.
- [ ] Cancel one processing run.
- [ ] Confirm cancellation returns the UI to a usable state.
- [ ] Run processing again to completion.
- [ ] Confirm a separate MP4 output is created.
- [ ] Confirm the original input file remains unchanged.
- [ ] Confirm the result reports expected and actual output duration.
- [ ] Confirm a no-silence video creates no output and shows an adjustment warning.
- [ ] Try an invalid or unsupported file and confirm a clear error.

Record the result, date, video characteristics, and any failure in the implementation record.
