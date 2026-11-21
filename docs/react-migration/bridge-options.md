# Python Bridge Options

React and Vite run frontend code. A browser cannot directly start Python or FFmpeg because that would be a security risk. A bridge is therefore needed between the React interface and the existing Python processing code.

## Option 1: Local HTTP API

```text
React/Vite → localhost HTTP request → Python bridge → FFmpeg
```

The Python application runs a small local server. React sends a processing request and receives status, progress, errors, cancellation results, and the output path.

### Advantages

- Clear separation between frontend and backend.
- Easy to explain in a portfolio.
- React can communicate with Python using familiar HTTP requests.
- Easy to test independently.
- Can support cancellation and structured job states.
- Does not require Electron or Tauri.

### Disadvantages

- Adds a local server process.
- Requires handling CORS or a Vite development proxy.
- The user must start the Python bridge separately during development.
- A future packaged desktop application would need an additional launcher.

### Lightweight variants

- Python standard-library HTTP server: few dependencies, more code to maintain.
- Flask: simple and approachable, adds one dependency.
- FastAPI: strong request validation and API documentation, but adds more dependencies and concepts.

## Option 2: Desktop-shell IPC

```text
React/Vite → Electron/Tauri IPC → Python process → FFmpeg
```

Electron or Tauri provides a desktop shell. The shell starts Python and passes messages between React and the backend.

### Advantages

- Feels like a true desktop application.
- Better access to local files and processes.
- Cancellation and process ownership can be tightly controlled.
- Easier path toward future installers.

### Disadvantages

- Adds Electron or Tauri complexity immediately.
- Requires learning desktop-shell concepts.
- Adds packaging and security configuration.
- Electron can be relatively large; Tauri requires Rust tooling.
- More than is needed for the current portfolio milestone.

## Option 3: Child-process integration

```text
React host → starts Python CLI → JSON messages → FFmpeg
```

The host application starts the Python program directly and reads structured JSON lines from standard output.

### Advantages

- Simple and efficient communication model.
- Good support for progress and cancellation.
- No HTTP server or database.
- Works well when a desktop host already exists.

### Disadvantages

- A normal browser cannot start the child process.
- Requires Electron, Tauri, PyWebView, or another host.
- More tightly coupled to the host implementation.
- Not suitable for a standalone Vite browser preview by itself.

## Option 4: Frontend-only demonstration

```text
React/Vite → simulated processing → simulated output
```

The interface demonstrates all screens but does not run Python or FFmpeg.

### Advantages

- Fastest portfolio presentation.
- No bridge, server, or packaging work.
- Easy to host as a static site.

### Disadvantages

- Does not perform real silence removal.
- Cannot honestly claim to be the converted application.
- Does not test integration, cancellation, or real media errors.
- The current Python work would not be connected.

## Comparison

| Option | Real processing | Complexity | Portfolio value | Future desktop path |
|---|---|---:|---:|---:|
| Local HTTP API | Yes | Low–medium | High | Good |
| Electron/Tauri IPC | Yes | High | High | Excellent |
| Child process | Yes | Medium | Medium–high | Good |
| Frontend-only demo | No | Low | Medium | Requires later replacement |

## Recommendation for the approved lightweight scope

Use Option 1: a local HTTP API.

For the first implementation, choose either:

1. Python standard library for the smallest dependency footprint; or
2. Flask for simpler routing and clearer beginner-friendly code.

The bridge should initially expose only two operations:

- Read metadata for a selected file.
- Start, observe, and cancel one processing job.

It should return structured JSON and never expose arbitrary command execution.

## Decision required

Approve one option before bridge implementation:

- Option 1A: standard-library Python HTTP bridge.
- Option 1B: Flask HTTP bridge.
- Option 2: Electron/Tauri desktop IPC.
- Option 3: child-process integration through a future host.
- Option 4: frontend-only demonstration.
