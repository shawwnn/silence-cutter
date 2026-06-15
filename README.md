# 🎬 Silence Cutter Desktop App

A lightweight desktop application that automatically removes long pauses and silence from videos while preserving original video quality.

---

## 📌 Project Overview

This tool is designed for content creators who want cleaner, more concise videos without manual editing.

It processes videos locally using FFmpeg and removes silent segments based on configurable thresholds.

---

## 🚀 MVP Scope

### ✅ Included

- Rule-based silence detection using FFmpeg
- Local video processing (no cloud)
- Desktop GUI (CustomTkinter)
- High-quality re-encoding (CRF 18–20)
- MP4 input/output support
- Adjustable silence threshold

### ❌ Not Included

- AI transcription (Whisper, NLP)
- “um / ah” filler word removal
- Cloud processing or uploads
- Timeline-based editor
- Streaming/export presets

---

## 🧠 Core Idea

Remove long silences while keeping video quality visually unchanged.

---

## ⚙️ System Architecture
User selects video
→ FFmpeg detects silence intervals
→ Build keep/cut timestamps
→ FFmpeg trims and merges segments
→ Export final MP4


---

## 🔧 Technology Stack

- Python
- homebrew
- FFmpeg
- CustomTkinter
- PyInstaller

---

## 🎥 Processing Strategy

### Silence Detection

Uses FFmpeg silence detection filters:

- Silence threshold (e.g. 1.5s+)
- Start/end timestamps extraction

### Encoding Settings

- CRF: 18–20 (high quality)
- Preset: medium (balanced speed)
- Audio: AAC (high bitrate or copy)
- No resizing

---

## 🧱 Project Structure
app/
├── pipeline/
│   └──  mutiple python files
├── main.py                   # Backend pipeline entry point
│   ├── mutiple python files
├── gui/
│   └── gui.py                # GUI entry (CustomTkinter)
├── tests/
│   └── sample.mov            # Input video location
├── assets/outputs
│       └── sample.mov        # Output video location
└── concat_list.txt           # Logs how videos cut into segmeents


---

## ⚙️ Processing Flow

1. User selects video file
2. FFmpeg detects silence segments
3. Extract timestamps
4. Convert into keep/cut intervals
5. Rebuild video using FFmpeg concat
6. Export final MP4

---

## 🎛️ UI (MVP Preview)
Silence Cutter
[ Select Video ]
Silence Threshold: 1.5s
[------●------]
[ Start Processing ]
Progress: ███████░░░


---

## 🧪 Build Plan

### 1. FFmpeg Setup
Test silence detection in terminal

### 2. Core Script
Extract silence timestamps in Python

### 3. Video Processing
Implement cut + merge pipeline

### 4. GUI
Build CustomTkinter interface

### 5. Packaging
PyInstaller (.app / .exe)

---

## ⚡ Key Design Principle

No AI editing.

Only:
> FFmpeg-based silence detection + deterministic video reconstruction

---

## 🎯 Output Behavior

Input:
- Raw video with pauses

Output:
- Clean video with:
  - long silences removed
  - minimal quality loss
  - similar file size


---

## 🖥️ How to Use the App

1. Run the GUI (Recommended)
This is the main user entry point:
python -m app.gui.gui

This launches the desktop interface.

From the GUI:
Select video
Set silence threshold           # ongoing feature
Click Start Processing
Backend pipeline runs automatically

2. Run backend directly (CLI / testing mode)
Use this if you want to bypass GUI and test pipeline logic:
python main.py --input tests/sample.mp4 --output assets/output/final.mp4
---

## ⚠️ Notes

- Fully offline tool
- No uploads required
- Optimized for simplicity and speed
- Portfolio-grade FFmpeg project

---

## 📈 Future Improvements

- Whisper-based transcript editing
- Filler word removal (“um / ah”)
- Scene detection
- Auto captions
- Timeline preview editor
