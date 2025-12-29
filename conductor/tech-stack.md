# Technology Stack

## Programming Language
- **Python 3.6+**
  - Cross-platform scripting language
  - Standard library includes tkinter for GUI
  - Subprocess module for FFmpeg integration

## GUI Framework
- **tkinter**
  - Python standard library (no external dependencies)
  - Native look and feel with ttk widgets
  - Threading support for non-blocking UI during conversion

## Video Processing
- **FFmpeg**
  - Industry-standard video transcoding tool
  - `drawtext` filter for dynamic timestamp overlay
  - H.264/AAC encoding for MP4 output
  - `+faststart` flag for web-optimized playback

- **ffprobe**
  - Metadata extraction from MTS files
  - Retrieves original recording timestamp
  - Part of FFmpeg distribution

## Build & Distribution
- **PyInstaller**
  - Creates standalone Windows executables
  - Bundles Python interpreter and dependencies
  - Single-folder distribution with bundled FFmpeg

## Platform
- **Windows**
  - Primary target platform
  - Subprocess flags for windowless execution (`CREATE_NO_WINDOW`)
  - Batch files for drag-and-drop and GUI launching

## File Formats
- **Input:** MTS (AVCHD video format from camcorders)
- **Output:** MP4 (H.264 video + AAC audio)

## Dependencies
### Runtime
- FFmpeg binaries (ffmpeg.exe, ffprobe.exe)
- No Python packages required beyond standard library

### Build
- PyInstaller >= 5.0
