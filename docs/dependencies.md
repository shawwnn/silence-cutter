# Dependencies

## Python

Install the application's runtime Python dependency with:

```bash
python -m pip install -r requirements.txt
```

The requirements file contains `customtkinter`, which is imported by the desktop GUI. The other Python imports used by the application are either part of Python's standard library or local modules in `app/`.

The application currently targets a Python installation that includes Tkinter, which is part of the Python standard library but may need to be installed separately by some operating-system Python distributions.

## External software

FFmpeg and FFprobe are required at runtime and must be installed separately. The application invokes the `ffmpeg` and `ffprobe` commands from the system PATH to detect silence, inspect video duration, cut segments, and merge the output.

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

The current tests cover silence-log parsing, retained video interval calculation, and default output filename generation. GUI behavior and FFmpeg execution are not automated by this test suite.
