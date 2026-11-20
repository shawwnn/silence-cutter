# Running the Flask Bridge

## Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

FFmpeg and FFprobe must also be installed and available on `PATH`.

## Start the bridge

From the repository root:

```bash
python3 -m app.bridge.server
```

The bridge listens only on the local computer at:

```text
http://127.0.0.1:5050
```

The future React application will send requests to this address. It is not a public website or cloud service.

## Basic health check

Open this URL in a browser or request it with a tool:

```text
http://127.0.0.1:5050/api/health
```

Expected response:

```json
{ "ok": true }
```

## What the bridge does

1. React sends a local video path and the two silence settings.
2. Flask validates the request.
3. Python starts the existing processing pipeline in a worker process.
4. The worker calls FFmpeg and FFprobe.
5. React polls the job for status and progress.
6. React can request cancellation.
7. The original input remains untouched and a separate MP4 is returned.

The bridge is intentionally local-only and currently supports one active job at a time.
