# Silence Cutter — Portfolio Update Brief

This is a self-contained brief for updating a separate resume/portfolio repository. It contains the current verified facts, the recruiter-facing story, the chronology, the architecture, the engineering problems, the trade-offs, and the content rules.

## Copy-paste implementation prompt

```text
Update the existing Silence Cutter project section in my recruiter-facing resume portfolio.

Do not create a separate unrelated project. Preserve the existing portfolio design, typography, spacing, and project-card structure unless a small improvement is needed for readability. Replace the outdated Silence Cutter text with the updated case-study content below.

Use the repository and demo links provided below. Keep the wording accurate: the current desktop React workflow was verified on macOS, but Windows and Linux desktop behavior have not been tested. Do not claim that a macOS, Windows, or Linux installer exists. Do not claim that FFmpeg is bundled. Do not present Tkinter as the final desktop interface; describe it as the original legacy implementation that motivated the React migration.

The portfolio audience is recruiters and technical hiring managers. Emphasize ownership, architectural reasoning, debugging, validation, trade-offs, and measurable outcomes. Keep the visible project summary concise, and put the deeper technical history in an expandable case-study section, modal, detail page, or project subpage if the existing portfolio supports one.

Use the following project content exactly as the factual source of truth. Reuse the existing portfolio components and styles. Add no duplicated application logic; this is a content and presentation update only.
```

## Project identity

### Title

Silence Cutter — Local Video Processing Application

### One-line summary

A local-first video-processing application that detects long silent sections and creates a separate, accurately trimmed MP4 without modifying the original file.

### Recruiter-facing summary

Silence Cutter began as a Python/CustomTkinter desktop tool and evolved into a React/Vite interface connected to a Python/Flask bridge and an FFmpeg processing pipeline. The project demonstrates full-stack ownership across media processing, API design, desktop UI migration, validation, deployment, testing, and iterative refactoring.

### Current status

The React/Vite web workflow and Flask bridge are working. A pywebview desktop-shell prototype was launched and tested end to end on macOS using the same React interface. The legacy Tkinter GUI remains in the repository as a fallback and has not yet been removed. No installable macOS, Windows, or Linux package is currently produced.

## Technology stack

Use this technology list in the portfolio:

```text
Python · React · Vite · Flask · FFmpeg · FFprobe
pywebview · Docker · Render · GitHub Actions
```

Optional historical technology:

```text
CustomTkinter/Tkinter — original desktop implementation
```

Do not list Builder.io or Codex as core runtime technologies. They may be mentioned separately as development/prototyping tools only if the portfolio has a section for AI-assisted development.

## Visible project-card copy

Use a concise version for the main portfolio card:

```text
Silence Cutter is a local-first video-processing application that removes long silent sections while preserving the original video. I built the FFmpeg-based processing pipeline in Python, connected it to a Flask bridge, and migrated the interface from a basic CustomTkinter desktop GUI to a reusable React/Vite workflow. The application validates media with FFprobe, reports processing progress, supports cancellation, verifies output duration, and produces a separate timestamped MP4.
```

Suggested status label:

```text
MVP complete · React web workflow verified · macOS desktop-shell prototype verified
```

Avoid using only `Finished` because the installable desktop distribution is intentionally deferred.

## Full case study

### The problem

Long pauses make recorded videos harder to watch, but manually finding and removing silence in a full editor is repetitive. The goal was to create a focused tool that detects long silent sections, removes them, preserves the order of the remaining content, and never modifies the original input file.

### Initial implementation

The first version was a Python desktop application using CustomTkinter. It connected a simple GUI to the existing processing pipeline and provided file selection, a silence-duration setting, progress feedback, and output-folder access.

This version proved the core idea, but the interface was visually basic and tightly coupled to the desktop GUI. It also used platform-specific behavior and was not a strong foundation for sharing the experience with a web interface.

### React migration

The interface was redesigned in React/Vite with a workflow focused on:

1. selecting a video
2. reviewing metadata
3. adjusting silence settings
4. processing the video
5. reviewing a verified result

The React UI uses shared components and styles for the main workflow. Desktop-specific behavior is kept outside the visual component tree wherever possible.

### Bridge architecture

The browser cannot directly start Python or FFmpeg, so a local Flask bridge was introduced:

```text
React/Vite interface
        ↓
Local Flask HTTP bridge
        ↓
Python processing service
        ↓
FFmpeg / FFprobe
```

The bridge handles health checks, media metadata, job creation, status polling, cancellation, downloads for public mode, and opening the output folder for local mode.

### Processing pipeline

The processing flow is:

```text
Validate input with FFprobe
    ↓
Detect silence with FFmpeg
    ↓
Parse silence intervals
    ↓
Build retained video intervals
    ↓
Render the retained sections through one FFmpeg filter graph
    ↓
Validate the final MP4 duration
    ↓
Return a separate timestamped output file
```

The original file remains untouched.

## Engineering problems and solutions

### Problem: inaccurate cuts at segment boundaries

Naive per-segment exports can introduce timing drift and synchronization problems.

Solution: build one FFmpeg filter graph that trims, normalizes timestamps, and concatenates retained intervals in a controlled export. Then compare the actual output duration with the expected retained duration.

### Problem: exports that remove all meaningful content

Aggressive silence settings can leave almost no video or produce an invalid result.

Solution: calculate the retained duration before export and stop early when the result would leave 0.5 seconds or less. Show a clear `Cut too aggressive` state instead of creating a bad MP4.

### Problem: videos without audio

Silence detection requires an audio stream.

Solution: inspect the media with FFprobe before starting the job and return a specific no-audio state instead of allowing the pipeline to fail later.

### Problem: long-running work blocking the UI

Video processing can take time and should not freeze the interface.

Solution: run processing in a worker process, expose job state through the bridge, poll status from React, and provide cancellation.

### Problem: web and desktop interfaces drifting apart

Maintaining separate Tkinter and React product interfaces would duplicate UI work and cause inconsistent behavior.

Solution: make React the intended shared interface and keep Python/FFmpeg behind the bridge. The pywebview shell loads the React interface in a desktop window while the web workflow uses the same React components.

### Problem: development changes versus packaged application changes

React changes appear immediately through Vite hot reload during development, but a packaged application would require a rebuild.

Solution: keep the current workflow source-based and development-friendly. Defer installers until distribution is required. When needed, add one readable on-demand packaging script and keep generated installers out of GitHub.

## Trade-offs

### Tkinter versus React desktop UI

Tkinter was faster for the original desktop proof of concept and remains as a fallback. React was chosen for the intended product interface because it provides a more polished workflow, reusable components, responsive layout, and consistency between web and desktop.

Trade-off: the React desktop path requires a wrapper and bridge startup, but avoids maintaining two product UIs.

### Browser file input versus native picker integration

The same React file input and drag-and-drop flow are used in web and desktop mode. A desktop-specific native picker API was considered, but it would add platform-specific branching and make the control differ from the web interface.

Trade-off: the operating system may still display its normal file dialog, but the React control and application workflow remain identical and easier to maintain.

### Local processing versus cloud processing

Local processing keeps user videos on the computer and avoids upload/storage costs. A temporary Render demo was also prepared for portfolio use with bounded limits.

Trade-off: local users must have the Python dependencies and FFmpeg/FFprobe available, while a hosted demo needs upload limits, temporary retention, and resource controls.

### Packaging now versus packaging on demand

Installers are not currently required, so generated `.app`, `.exe`, or Linux bundles are not stored in the repository.

Trade-off: terminal-based setup is less convenient for nontechnical users, but it avoids premature packaging complexity. A future packaging script can generate an installer only when distribution is needed.

## Testing and verification

Automated checks include:

- React production build
- Python desktop-entry syntax validation
- 30 automated Python tests
- bridge validation tests
- silence parsing and retained-interval tests
- filter-graph export tests
- output-duration verification tests

The desktop-shell prototype was manually verified on macOS with a real video:

```text
Input: 1 minute 25 seconds
Output: 17 seconds
Silence intervals removed: 12
Duration difference: 0.044 seconds
```

The repository also has a GitHub Actions checker that runs the existing React build, Python syntax check, and automated tests on pushes and pull requests. It does not build installers.

## Deployment

The project has two contexts:

### Local application

The React interface communicates with a local Flask bridge. FFmpeg and FFprobe run on the same computer, and the original video stays local.

### Portfolio web demo

The public Render demo provides a temporary upload-and-download workflow with bounded processing limits and cleanup behavior. It is a portfolio demonstration, not the same as a packaged desktop installer.

## Important accuracy rules

Do not claim:

- Windows desktop verification has been completed.
- Linux desktop verification has been completed.
- a macOS, Windows, or Linux installer currently exists.
- FFmpeg and FFprobe are bundled in the current application.
- Tkinter is the final intended product UI.
- the React desktop shell has replaced the Tkinter entry point.

It is accurate to claim:

- the core processing pipeline works locally
- the React/Vite and Flask workflow is implemented
- the macOS pywebview desktop-shell prototype was tested end to end
- the original input remains unchanged
- output duration is verified
- the repository has automated checks and documented architecture decisions

## Links

```text
GitHub repository: https://github.com/shawwnn/silence-cutter
Portfolio demo: https://silence-cutter-portfolio.onrender.com/
Portfolio website: https://cv-resume-responsive.vercel.app/
```

## Suggested portfolio update checklist

- Replace the outdated Silence Cutter technology list.
- Replace the old description that treats Tkinter as the main desktop path.
- Keep the existing screenshots if they remain visually useful; add current React workflow screenshots when available.
- Add the concise project-card copy.
- Add a recruiter-readable case-study detail section using the chronology above.
- Include the GitHub repository and live demo links.
- Clearly label the desktop shell as a macOS prototype if mentioning it.
- Preserve the existing portfolio visual design.
- Run the portfolio repository’s own build/checks before publishing.
