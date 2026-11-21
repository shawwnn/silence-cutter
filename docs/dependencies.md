# Dependencies

## Python

Install the application's runtime Python dependency with:

```bash
python -m pip install -r requirements.txt
```

The requirements file contains Flask for the local React-to-Python bridge. The other Python imports used by the application are either part of Python's standard library or local modules in `app/`.

## Frontend

Install JavaScript dependencies with:

```bash
npm install
```

Start the Vite development server with:

```bash
npm run dev
```

## External software

FFmpeg and FFprobe are required at runtime and must be installed separately. The application invokes them from the system PATH to detect silence, inspect media, render accurate filter-graph cuts, and validate final output duration.

Verify both commands are available before running the application:

```bash
ffmpeg -version
ffprobe -version
```

FFmpeg and FFprobe are intentionally not listed in `requirements.txt` because they are external executables, not Python packages.

## Testing

Test dependencies are kept separate from runtime dependencies. Install them with:

```bash
python -m pip install -r requirements-dev.txt
```

Run the automated tests from the repository root with:

```bash
python -m pytest
```

The tests cover silence-log parsing, retained interval calculation, Flask validation, filter-graph construction, and synthetic FFmpeg timing fixtures. Manual browser and representative-video checks remain required.
