# Desktop React UI Migration Plan

## Purpose

This document describes how Silence Cutter can replace its current CustomTkinter desktop interface with the existing React interface, while keeping the Python/FFmpeg processing pipeline as the application core.

The goal is to establish a shared understanding and planning process before changing the desktop entry point or removing the Tkinter implementation.

## Proposed Direction

React becomes the single source of truth for the user interface.

Python remains responsible for:

- FFmpeg and FFprobe execution
- media validation and metadata inspection
- silence detection and cut generation
- job progress, cancellation, and result validation
- desktop-only filesystem operations exposed through the local bridge

A thin desktop window wrapper loads the built React application and connects it to the local Python bridge.

```text
React UI
    ↓
Desktop window wrapper
    ↓
Local Python bridge
    ↓
Processing pipeline
    ↓
FFmpeg / FFprobe
```

The existing web and desktop experiences should share the same React components, styles, state model, and workflow states. They may differ only where the environment requires it, such as selecting a local file or opening an output folder.

## Initial Decisions

These decisions close the first alignment discussion. They may be refined later, but they are the working baseline for the prototype.

### Operating systems

The first implementation and verification target is macOS because that is the currently available development environment. Windows and Linux remain planned targets for a later packaging and compatibility phase.

The architecture should avoid macOS-specific assumptions wherever possible. Cross-platform behavior will be isolated behind the desktop capability layer so that Windows and Linux implementations can be added later without rebuilding the React UI.

### Window behavior

The desktop application will use a normal resizable window with a sensible minimum size. It should be possible to maximize the window or use full-screen mode when desired, but full-screen mode will not be required at startup.

This gives the small current React interface room to grow while remaining familiar as a desktop application.

### Shared interface

The web and desktop applications will use the same React components and styling. The basic website appearance and the desktop appearance should match.

Future changes to the original React UI should automatically remain available to the desktop application through the normal development and build process. Desktop-specific controls must be implemented through a stable capability boundary rather than scattered throughout the components. This allows desktop controls to survive future visual redesigns and workflow improvements.

### File and result actions

The desktop experience should support both native file selection and drag-and-drop. The React screen remains shared; the desktop wrapper supplies the native file capability.

When processing completes, the application should show a result state with an explicit `Open Output Folder` action. It should not open a folder automatically.

### Desktop runtime

The first desktop-wrapper technology to investigate is pywebview because the existing backend is Python-based. This is a prototype recommendation, not yet a final technology commitment.

The packaged desktop application should start the local Python bridge automatically. Users should not need to open Terminal or run a separate command.

### FFmpeg packaging

FFmpeg and FFprobe packaging will be decided after the desktop prototype and core desktop workflow are working. Bundling or automatically managing them is the preferred direction for a beginner-friendly final product, but it is intentionally deferred because it is primarily a distribution concern.

## Current Situation

The repository currently contains two user interfaces:

1. A basic CustomTkinter desktop GUI in `app/gui/gui.py`.
2. A more complete React/Vite interface in `src/`.

The React interface already represents the intended product direction more closely. It includes the workflow steps, video metadata, adjustable settings, processing states, cancellation, warnings, and result actions.

The Python bridge also supports desktop-host requests using an absolute `input_path`, which provides a foundation for native desktop file access without duplicating the UI.

## Important Terminology

### Frontend

The React application in `src/`. This contains the visual design, interaction flow, state transitions, and user-facing messages.

### Desktop wrapper

A small native application shell that opens a desktop window and loads the React frontend. It is not a second UI. It should contain as little product logic as possible.

### Bridge

The local Python HTTP/API layer that connects the frontend to the processing pipeline. It should remain the boundary between UI concerns and media-processing concerns.

### Development build

The version used while implementing and testing changes. It may load React from a Vite development server and can support hot reload.

### Packaged build

The distributable desktop application. It loads compiled React assets and requires a rebuild/repackage before frontend changes appear in the delivered application.

## What “Reuse the React Frontend” Means

There should be one React codebase, but two possible runtime environments:

```text
                 shared React code
                /                 \
       web runtime          desktop runtime
       browser upload       native file picker
       download result      open output folder
```

Visual and workflow changes should normally be made once in React. During development, those changes can appear immediately through hot reload. In a packaged desktop application, the React assets must be rebuilt and included in a new application package.

The desktop-specific behavior should be isolated behind a small capability layer. For example:

- web mode: use browser file input and download responses
- desktop mode: use native file selection and open the local output folder

The components should not contain platform-specific branching everywhere.

## Brainstorming Before Implementation

Before choosing a desktop wrapper or changing the entry point, we should answer the following questions.

### Product experience

- Should the desktop app preserve the same full-screen layout, or use a fixed/resizable window?
- What minimum window size keeps the two-column layout usable?
- Should the desktop app support drag-and-drop from Finder/Explorer?
- Should the app remember the last-used settings?
- What should happen when the user closes the app during processing?
- Should the output folder action reveal the file, open its parent folder, or both?

### Runtime and packaging

- Which desktop wrapper best fits the current Python architecture?
- Should the Python bridge be started by the wrapper or by a separate launcher?
- How will the wrapper discover the bridge port and health state?
- How will React assets be located in development and in a packaged application?
- How will FFmpeg and FFprobe be installed or bundled for each target operating system?
- What platforms are required first: macOS only, or macOS plus Windows/Linux?

### API and capability boundaries

- Which actions require native desktop capabilities?
- Should the bridge accept absolute paths only in desktop mode?
- How will path validation and permissions be handled?
- Should the desktop app expose a native file picker through the wrapper or through Python?
- How should browser-only download behavior map to a desktop output action?

### Reliability and safety

- Can a job continue if the window is refreshed or reopened?
- How will cancellation be handled when the window closes?
- What happens if the bridge fails to start?
- What happens if FFmpeg is missing?
- How will packaged builds be tested against real video files?
- How will we preserve the guarantee that the original input is never modified?

### Migration and maintenance

- Which behavior in Tkinter is still missing from React?
- When can Tkinter be considered safely removable?
- Do we need a temporary fallback launch mode during migration?
- How will web and desktop-specific behavior be tested without duplicating tests?

## Planning Principles

1. Preserve the processing pipeline while changing the presentation layer.
2. Make the bridge contract explicit before wiring a desktop wrapper to it.
3. Keep desktop-specific code narrow and isolated.
4. Prefer one shared React workflow over separate web and desktop implementations.
5. Do not remove Tkinter until the React desktop path has passed acceptance tests.
6. Make every phase independently testable and reversible where practical.
7. Treat packaging, filesystem permissions, and FFmpeg availability as product requirements, not final polish.

## Decision and Reuse Policy

Every meaningful decision made during this migration must be recorded before the related implementation proceeds. The record should include:

- the decision
- the alternatives considered
- the reason for the chosen direction
- the affected files or interfaces
- how the decision will be tested
- whether the decision is reversible

The primary record is this document for architecture and phase decisions. Detailed implementation decisions should also be recorded in the relevant migration or implementation document when they affect a specific subsystem.

The default approach is to reuse existing work. Before creating a new component, API, style, processing function, asset, test, or packaging rule, we should check whether an existing one can be extended.

The reuse priority is:

1. Existing React components and state transitions in `src/`.
2. Existing React styles, layout rules, typography, icons, and assets.
3. Existing bridge endpoints and request/response contracts.
4. Existing Python processing and validation pipeline.
5. Existing automated tests and manual test checklists.
6. Existing documentation and deployment conventions.
7. New code only where the desktop environment requires a capability that does not already exist.

“Reuse” does not mean forcing incompatible behavior into an existing file. If a new abstraction is needed, the decision should explain why it belongs at that boundary and how it avoids duplicating product logic.

## Code Size and Checkpoint Convention

To keep the implementation approachable, new production code should normally stay at or below roughly 200 lines per source file. This is a readability guideline, not a reason to split a small, cohesive function across artificial files. Existing files are not to be refactored merely to satisfy the guideline.

Every completed phase gate must have a checkpoint commit. Before each checkpoint commit:

1. record the decision and outcome in the documentation
2. review the changed-file list
3. run the smallest relevant build or test checks
4. confirm no unrelated user changes are included
5. commit with a phase-specific message

The current checkpoint is the desktop-shell prototype and end-to-end workflow validation. Tkinter retirement and packaging are intentionally not part of this checkpoint.

## Next Gate: Packaging Scrutiny Options

The next phase is to determine how the working desktop shell becomes a distributable macOS application. Before changing packaging files, we will scrutinize the options in one of these ways.

### Option A: Minimal local packaging spike

Create the smallest macOS package around the existing `app/desktop.py` entry point and the existing React build. Test launch, bridge startup, React loading, video processing, and output-folder opening.

Tradeoffs:

- fastest way to discover real packaging problems
- keeps the current architecture visible
- may produce a developer-oriented package first
- may require follow-up work for bundled Python and FFmpeg

### Option B: Packaging requirements audit first

Document and inspect Python runtime, pywebview, React assets, FFmpeg, FFprobe, icons, output paths, permissions, and clean-machine behavior before creating a package.

Tradeoffs:

- gives a clearer distribution design before implementation
- reduces the chance of choosing a packaging tool prematurely
- takes longer before we have a launchable package
- may identify issues that are easier to learn from a real spike

Working recommendation: use Option A first, then use Option B to turn the successful spike into a repeatable distributable build. This preserves the reuse-first approach and gives us evidence before making a larger packaging decision.

## Gate 1 Working Method

Gate 1 will be completed in small documented passes:

1. Inventory the current React UI and list each user action.
2. Map each action to an existing bridge endpoint or identify a missing capability.
3. Separate shared behavior from web-only and desktop-only behavior.
4. Identify the smallest desktop capability interface.
5. Record open questions and proposed decisions.
6. Review and approve the boundary before implementing the desktop shell.

No Tkinter removal, desktop-wrapper commitment, or broad refactor should happen during this inventory pass.

## Gate 1 Initial Inventory

This is the first read-only inventory of the current implementation. It is a baseline for planning, not a request to rewrite anything.

### Already reusable

| Existing capability | Current location | Reuse direction |
| --- | --- | --- |
| React application state and workflow phases | `src/main.jsx` | Keep and adapt only where desktop capabilities differ |
| Video selection and drag-and-drop UI | `src/components.jsx` | Keep the shared UI; connect native selection through a capability boundary if needed |
| Settings controls | `src/components.jsx` | Reuse unchanged unless product requirements change |
| Processing, cancellation, progress, and result states | `src/main.jsx`, `src/components.jsx` | Reuse the existing state model and components |
| Dark/lime visual system and responsive layout | `src/styles.css` | Reuse as the desktop visual system |
| Health, job, cancellation, download, and output-folder APIs | `src/api.js` | Preserve the existing contracts where possible |
| Local input-path metadata and job support | `app/bridge/server.py` | Reuse for desktop file processing |
| Cross-platform output-folder route | `app/bridge/server.py` | Reuse; verify behavior on each target OS later |
| FFmpeg processing pipeline | `app/` | Do not rewrite as part of the UI migration |
| Processing tests and manual checklists | `tests/`, `docs/react-migration/` | Extend only for desktop-specific behavior |

### Current desktop-specific gaps

- The current React `sendVideo` path is browser-oriented and sends a `File` through `FormData`.
- Desktop mode needs a deliberate way to provide an absolute local path to the existing bridge path-based API.
- The desktop runtime needs a capability for native file selection, unless the browser file picker is sufficient for the chosen wrapper.
- The wrapper needs to start the Python bridge and load either the Vite development URL or compiled frontend assets.
- The packaged application needs a defined strategy for locating Python, FFmpeg, FFprobe, and React assets.
- The existing Tkinter entry point must remain untouched until the replacement passes its acceptance tests.

### Gate 1 decisions still required

These are the next questions to answer, one group at a time:

1. Should desktop mode use the existing browser file input first, or require a native picker in the first prototype?
2. Should the desktop capability boundary be exposed through a JavaScript bridge from the wrapper, or through additional local HTTP endpoints?
3. Should the desktop wrapper load the Vite development server during development and compiled `dist/` assets in packaged builds?
4. How should the wrapper start, monitor, and stop the Python bridge?
5. What is the smallest macOS prototype that proves file selection, metadata, processing, cancellation, and opening the output folder?

The default reuse-first assumption is to keep the existing React components and bridge contracts, add only the smallest adapter needed to support an absolute local path, and avoid creating a second desktop-specific component tree.

## Desktop File Selection Requirement

The desktop application must keep the existing React file-selection screen visually. The user should continue to see the same dropzone, browse action, selected-file card, metadata, and replace-file action.

Underneath that shared screen, desktop mode may use a native file picker so the application receives a real local path. This platform-specific behavior must be:

- easy to find in the code
- documented at the point where it is used
- small enough to read without understanding a large framework
- isolated to one or two clearly named files/functions
- reusable by future React UI changes
- free of a second desktop-specific component tree

The goal is not to hide complexity behind many abstractions. The goal is to keep one simple boundary where the desktop file-picker behavior differs from browser behavior.

## Desktop Communication Options

The desktop wrapper needs a way to receive a local file path from the native picker and provide it to React. There are two main approaches.

### Option A: JavaScript desktop API

The desktop wrapper exposes a small JavaScript function to the React page, such as:

```js
const selectedPath = await window.desktop.selectVideoFile()
```

React calls that function only when running in desktop mode. The wrapper opens the native file picker and returns the selected path. Web mode continues using the normal browser file input.

Advantages:

- usually the fewest code changes for native file selection
- direct and easy to understand for desktop-only actions
- no new HTTP endpoint is needed for opening a picker
- local file paths do not need to be sent through a browser upload request
- can also support future desktop actions such as revealing a file or choosing an output directory

Tradeoffs:

- introduces one small desktop-specific JavaScript API
- depends on the selected wrapper’s API and security model
- requires careful handling when the API is unavailable in web mode
- wrapper-specific code must be tested separately from the React page

Readability approach:

- put the desktop calls in one clearly named module such as `src/desktop.js`
- keep the API surface small and explicit
- use a simple `isDesktop()` check or capability object
- do not spread wrapper checks throughout the components

### Option B: Additional local HTTP endpoints

The React app calls a new Python endpoint, for example:

```text
POST /api/desktop/select-file
```

The Python bridge opens the native file picker, returns the selected path, and React then uses the existing path-based metadata and job APIs.

Advantages:

- keeps communication in the existing HTTP/API style
- centralizes native file operations in Python
- can be reused by any client that can call the local bridge
- avoids exposing a wrapper-specific JavaScript API to React

Tradeoffs:

- adds new bridge endpoints and request/response contracts
- makes the Python bridge responsible for GUI/native-picker behavior
- requires more code and more testing for a simple desktop action
- can blur the boundary between HTTP processing services and desktop shell behavior
- requires extra safeguards so a browser cannot misuse native desktop endpoints

Readability risk:

The HTTP approach may look consistent with the existing bridge, but it adds more moving parts for this particular requirement: a route, native-picker implementation, response schema, client function, and desktop-mode handling.

## Superseded Decision: Option A for file selection

Option A was initially selected for native file selection because it appeared to offer a small desktop capability boundary.

The initially proposed shape was:

```text
Shared React file-selection UI
        ↓
Small `desktop.js` capability module
        ↓
Native picker exposed by the desktop wrapper
        ↓
Absolute local path sent through the existing bridge contract
```

The prototype and visual review showed that a desktop-only file-selection branch would make the desktop browse control differ from the web control. This decision is therefore superseded for ordinary video selection. The existing React file input remains the implementation for both modes.

Decision record:

- Decision: initially use a small JavaScript desktop capability API for file selection.
- Alternatives considered: additional local HTTP endpoints.
- Reason: fewer changes, clearer separation, and easier reuse of the existing bridge and React UI.
- Scope: native file selection first; future native actions may use the same small capability module.
- Reversibility: high, because the existing bridge contracts and React workflow remain intact.
- Outcome: superseded after prototype review; the shared browser file-input flow better matches the required UI and has fewer code changes.

### Prototype implementation record

The first reversible prototype uses:

- `pywebview` as the desktop window wrapper
- `app/desktop.py` as the small desktop-shell entry point
- the existing Flask application from `app.bridge.server`
- the existing React/Vite development server at `http://127.0.0.1:5173`
- the existing React file input and multipart bridge flow

This prototype intentionally does not:

- replace `entry.py`
- remove `app/gui/gui.py`
- change the existing React component tree
- add new HTTP endpoints
- package FFmpeg, Python, or the frontend

The prototype decision is reversible. If pywebview cannot reliably provide the required native picker or window behavior, the evidence must be recorded before considering another wrapper or Option B.

Prototype development run:

```bash
npm run dev
python3 -m app.desktop
```

The Vite development server remains responsible for serving the existing React UI, while the prototype starts the existing local Flask bridge and opens it in a desktop window. This deliberately preserves React hot reload during the experiment.

Prototype validation record:

- `pywebview` installed successfully as version 6.2.1 on the macOS development environment.
- `app/desktop.py` imported successfully.
- `npm run build` completed successfully using the existing React application.
- The Vite development server started at `http://127.0.0.1:5173`.
- The desktop process launched as a native Python application.
- The React page reached the existing Flask `/api/health` endpoint while running inside the desktop process.
- The shared React file-selection control was visible inside the native pywebview window.

Validation decision: keep the pywebview direction because the shell, React asset loading, and bridge startup path are working. The file-selection test showed that the control should remain the same shared React file input rather than adding a desktop-only picker branch.

End-to-end desktop validation:

- launched the existing React/Vite development server
- launched the pywebview desktop window
- selected a real video through the shared file-input control
- displayed the selected filename, format, size, and duration
- started the existing silence-removal job
- displayed processing progress and completion state
- produced a separate output video
- verified the output duration in the existing result panel

Observed result: `goo test.mov` completed successfully. The input was 1 minute 25 seconds, the output was 17 seconds, 12 silence intervals were removed, and the duration difference was 0.044 seconds.

This closes the first desktop workflow validation. Tkinter remains in place until packaging and broader acceptance testing are complete.

### Revised implementation decision: shared browser file input

After inspecting the desktop prototype, the file-selection control should remain exactly the same React control in web and desktop mode. The desktop wrapper may still cause the operating system's normal file dialog to appear, but the React control and file-handling flow will not change by platform.

The implementation will therefore:

- use the existing React file-selection screen and styles
- reuse the existing browser `File` input and drag-and-drop behavior in both modes
- reuse the existing multipart `/api/metadata` contract
- reuse the existing multipart `/api/jobs` contract
- do not create desktop-specific duplicate components
- do not add new HTTP endpoints

This intentionally avoids a desktop-only file descriptor, native picker adapter, or path-specific React branch. The React workflow will continue to use the same file, metadata, settings, progress, cancellation, result, and error states everywhere.

Decision record:

- Decision: use the same React browser file input and drag-and-drop flow in web and desktop mode.
- Reason: the desktop control must look and behave like the web control, with fewer code changes and no platform-specific branch in the main workflow.
- Alternatives deferred: native picker through a JavaScript API may still be used later for a genuinely desktop-only capability, but not for ordinary video selection.
- Test: the same selected-file UI appears, metadata loads, and the existing multipart job flow works inside the desktop window.

## Proposed Phase Gates

The phase gates below are planning checkpoints, not a commitment to implement every detail immediately.

### Gate 0: Alignment and scope

Objective: agree on the target user experience and supported platforms.

Questions to close:

- target operating systems
- preferred desktop wrapper approach
- window behavior and minimum dimensions
- desktop-only capabilities
- release and packaging expectations

Exit criteria:

- initial target is macOS, with Windows and Linux planned later
- the window is resizable and can support maximize/full-screen behavior
- web and desktop share the React UI and styling
- native file selection, drag-and-drop, explicit output-folder opening, automatic bridge startup, and pywebview investigation are recorded as the working baseline
- unresolved decisions are identified
- no code removal has occurred

### Gate 1: Capability and bridge audit

Objective: verify that the existing React UI can be supported by the bridge in both browser and desktop contexts.

Activities:

- map every React action to an API or desktop capability
- identify browser-only behavior
- identify desktop-only behavior
- confirm metadata, job, cancellation, result, and output-folder flows
- define a small environment/capability interface

Exit criteria:

- all current UI states have a backend path
- desktop file selection and output-folder behavior are specified
- bridge changes, if any, are documented before implementation

### Gate 2: Desktop shell spike

Objective: prove that a minimal desktop window can load React and communicate with the local Python bridge.

Activities:

- open a native window
- load the React development build
- start or connect to the bridge
- run a health check
- select a real local video
- complete a small processing job

Exit criteria:

- a throwaway or isolated prototype works end to end
- the chosen wrapper is technically viable
- packaging risks are understood

### Gate 3: Shared React desktop integration

Objective: integrate desktop capabilities into the existing React application without duplicating the UI.

Activities:

- add runtime/environment detection or capability injection
- support native file selection
- support local output-folder opening
- preserve web upload/download behavior
- handle bridge startup and failure states

Exit criteria:

- the same React components run in web and desktop development modes
- desktop-specific code is isolated
- existing web behavior remains functional

### Gate 4: Desktop UX and resilience

Objective: make the desktop experience production-ready from a user perspective.

Activities:

- test resize behavior and minimum window dimensions
- test drag-and-drop and large file metadata loading
- test cancellation and window-close behavior
- test missing FFmpeg/FFprobe and bridge startup failures
- review keyboard navigation, focus, labels, and error messages

Exit criteria:

- primary and failure workflows are usable
- no critical job or file-safety issue remains
- the UI is visually consistent with the React web experience

### Gate 5: Packaging and distribution

Objective: produce a repeatable packaged desktop build.

Activities:

- compile the React assets
- package the desktop wrapper
- include or document Python runtime and dependencies
- include or provision FFmpeg and FFprobe
- verify icons, app metadata, permissions, and output paths
- create a clean-machine or clean-environment test procedure

Exit criteria:

- a fresh packaged build launches successfully
- a real video can be processed end to end
- packaged assets and runtime dependencies are documented

### Gate 6: Tkinter retirement

Objective: remove the old desktop UI only after the replacement is proven.

Prerequisites:

- Gate 5 is complete
- desktop acceptance tests pass
- rollback or recovery instructions exist
- no required behavior exists only in Tkinter

Activities:

- change the desktop entry point to the React wrapper
- remove or archive `app/gui/gui.py` according to the agreed policy
- remove obsolete CustomTkinter dependencies
- update README and deployment documentation
- run the complete test suite and packaged smoke test

Exit criteria:

- the desktop product uses React exclusively
- documentation no longer describes Tkinter as the primary desktop UI
- the processing pipeline remains unchanged and verified

## Suggested Acceptance Test Matrix

| Area | Web mode | Desktop mode |
| --- | --- | --- |
| Select video | Browser file picker | Native file picker and/or drag-and-drop |
| Read metadata | Browser upload/metadata path | Absolute local input path |
| Configure silence settings | Shared React controls | Shared React controls |
| Start processing | Bridge job API | Bridge job API |
| Monitor progress | Shared polling/state model | Shared polling/state model |
| Cancel processing | Cancel API | Cancel API and close-window behavior |
| Retrieve output | Browser download | Open output folder and/or reveal file |
| Error handling | Shared UI states | Shared UI states plus startup/runtime errors |

## Definition of Success

The migration is successful when:

- React is the only maintained product UI.
- Web and desktop use the same visual system and workflow components.
- Desktop-specific behavior is isolated behind a small capability boundary.
- Python/FFmpeg processing behavior remains reliable and unchanged in purpose.
- A packaged desktop build can select, process, validate, and reveal a local video result.
- UI changes made in React can be carried into both environments through the normal development/build process.
- Tkinter can be removed without losing required functionality.

## Immediate Next Step

Gate 0 is now sufficiently defined to begin the next planning step. Before implementation begins, we should record:

1. the initial minimum window dimensions
2. the exact desktop capability boundary
3. the pywebview prototype acceptance test
4. the development workflow for running React, the bridge, and the desktop window together
5. the future Windows/Linux compatibility risks to keep visible

Only after those decisions should the implementation plan be converted into tickets or code changes.
