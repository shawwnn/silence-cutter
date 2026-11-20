The preview console shows a runtime crash in the slider, so I'll check the current app state and dev server logs before writing the report.

# Silence Cutter UI/UX Inspection Report

**Scope:** This report comes from the source I wrote and one live screenshot. I have not clicked through each state in the browser, so the interaction behavior below is from code, not runtime testing.

**Console crash:** The preview console showed `Invalid hook call` and `null (reading 'useRef')` errors in the Radix Slider and TooltipProvider. They appeared while the dev server was reconnecting. The current render works and the slider displays. The likely cause is a stale dependency cache after the restart, but I haven't confirmed that. If the crash returns, restart the dev server.

## 1. Screen structure

- **Header (all pages):** Logo and "Silence Cutter" link to `/`. Tagline "Powered by FFmpeg · runs on your computer" is hidden below 640px.
- **Preview banner:** Shown only when no desktop shell provides `window.silenceCutter`. It states that no video is processed and no file is written.
- **Hero:** Headline, one-paragraph description, and a four-step indicator (Select video → Set threshold → Process → Done).
- **Workspace:** Left column is the video area. Right column (340px, 1024px and up) holds the threshold control and the process panel. Below 1024px the columns stack.
- **Other route:** Unknown paths show a 404 with a "Back to workspace" button.

## 2. Flow from start to finish

**Idle (first load)**

- Step 1 is current. The drop zone reads "Drop a video here". Threshold is at −35 dB and enabled. "Remove silence" is disabled with the hint "Select a video to get started."
- Clicking the zone or pressing Enter/Space opens the file picker. Cancelling does nothing.
- Dragging a file over the zone turns the border lime and changes the text to "Drop to select".
- An unsupported file shows a red-tinted zone and an inline message, for example `".txt" files aren't supported. Choose MP4, MOV, MKV, AVI, WEBM, M4V.` The state stays idle.
- An empty file shows "This file is empty."

**Selected (350 ms)**

- A video card appears with the filename, format, size, and a spinning duration value. The helper text says "Reading video details…" and the process button says "Reading the video…" (still disabled).
- Gap: the file is read before this state starts. With the preview bridge, that read can take up to 4 seconds, and the drop zone shows no feedback during it.

**Ready**

- Step 2 is current. The card shows format, size, and duration. The helper reads "Drop another video here to replace it."
- "Choose a different video" is enabled. The threshold slider is enabled. Moving it updates the dB readout and the description text immediately. A "Reset to default" link appears once the value is changed.
- "Remove silence" becomes lime and enabled. The hint reads "Your original file is never changed." (this is an assumption I wrote, not something the backend guarantees).
- Clicking "Remove silence" starts processing. Repeat clicks are blocked by both the disabled button and an internal guard.

**Processing**

- Step 3 is current.
- The button reads "Processing…" with a spinner. It is disabled, so it renders at 50% opacity.
- The progress bar sweeps indeterminately. It shows a percentage only if the backend reports a real fraction. Status text comes from the backend (the preview cycles through "Detecting silent sections" and "Rendering the trimmed video").
- The card's "Choose a different video" button is dimmed. Its helper reads "Locked while processing." Drag-and-drop is ignored.
- The threshold section is dimmed to 60% opacity and the slider is disabled.
- The helper reads "Keep this window open. Longer videos take longer."
- There is no cancel button.

**Completed**

- All four steps show checkmarks.
- Threshold is dimmed and disabled, and the threshold setting carries over to the next video.
- The panel shows a green check. Its heading is "Silence removed", or "Preview complete" in preview mode. It lists the output filename and the folder.
- "Open output folder" is the primary action. Failures appear as a toast.
- "Process another video" opens the file picker. Cancelling leaves the completed result on screen.

**Failed**

- Step 3 stays current. A red alert box shows "Processing failed" with the error text. The text is the raw error from the backend, or "Processing stopped unexpectedly." if none was given.
- "Try again" returns to Ready with the same video and threshold, so no reselection is needed.
- "Choose a different video" is a ghost button that opens the picker.
- Threshold stays enabled so the user can adjust it before retrying.

**Replacing a video**

- Choosing a valid new file clears the previous result, error, and progress. The threshold is kept.
- If the new file is invalid while a result is showing, the old result stays and the error appears under the old video's card. This is confusing.

## 3. Enabled, disabled, and dimmed states

| Element                  | Idle                   | Selected                   | Ready              | Processing                    | Completed           | Failed                |
| ------------------------ | ---------------------- | -------------------------- | ------------------ | ----------------------------- | ------------------- | --------------------- |
| Drop zone / replace drag | Active                 | Card shown; replace active | Active             | Locked, drops ignored         | Active              | Active                |
| Choose a different video | Not shown              | Enabled                    | Enabled            | Dimmed, disabled              | Enabled             | Enabled               |
| Threshold slider         | Enabled                | Enabled                    | Enabled            | Dimmed, disabled              | Dimmed, disabled    | Enabled               |
| Reset link               | Hidden when at default | Hidden when at default     | Shown when changed | Hidden                        | Hidden              | Shown when changed    |
| Remove silence           | Disabled               | Disabled                   | Enabled            | Disabled, reads "Processing…" | Replaced by results | Replaced by Try again |
| Open output folder       | —                      | —                          | —                  | —                             | Enabled             | —                     |
| Try again                | —                      | —                          | —                  | —                             | —                   | Enabled               |
| Process another video    | —                      | —                          | —                  | —                             | Enabled             | —                     |

The Reset link is hidden with opacity, not removed, so the layout does not shift.

## 4. Responsive and accessibility

- **Below 640px:** The tagline is hidden, step connectors are hidden, and the steps wrap onto two lines. Verified in a narrow screenshot.
- **Below 1024px:** Single column. Verified.
- **1024px and up:** The two-column layout is not verified. My desktop screenshot cut off before the sidebar.
- **Keyboard:** The drop zone is a real button with a focus ring. The slider uses Radix keyboard controls.
- **Screen readers:** Errors use `role="alert"`, the progress bar is labeled, and the current step has `aria-current`.
- **Not verified:** Contrast ratios, a full keyboard pass, and screen reader behavior.

## 5. Findings, most important first

1. **No feedback while reading a file.** The drop zone looks unchanged for up to 4 seconds. Fix: set the selected state before the file read starts.
2. **The active processing button looks disabled.** "Processing…" is at 50% opacity. Fix: keep full opacity and rely on the spinner.
3. **No way to cancel processing.** Cancel is not in the approved scope, so I need your decision.
4. **"Open output folder" fails in preview.** It is enabled but always shows "Opening folders needs the desktop app." Fix: hide it in preview mode.
5. **Rejected file after a result.** The old result stays with an error under the old card. Fix: clear the result or show the error in the panel.
6. **Unverified claims and copy.** "Your original file is never changed.", the hero headline, the tagline, the supported formats, the −35 dB default, and the threshold descriptions are all my assumptions. None come from your app.
7. **Preview success looks real.** It uses the same green check as a real result. The label says "Preview complete", but the styling may still mislead.
8. **Raw backend errors.** Failure messages are shown exactly as the backend provides them.
9. **Minor.** An unreadable duration shows "—" with no explanation. While dragging over the locked state, nothing says the video can't be replaced.

## 6. Questions for you

- Should processing have a cancel button? It would need backend support.
- Does the backend report real progress percentages, or only status messages?
- Is the original file ever modified? I assumed not.
- Are the six formats, the −35 dB default, and the −60 to −10 dB range right?
- Should I apply the fixes for findings 1, 2, 4, and 5 now?
