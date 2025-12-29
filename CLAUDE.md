# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MTS to MP4 video converter that adds dynamic timestamp overlays showing the original filming date/time. The timestamp updates every minute as video playback progresses.

## Requirements

- Python 3.6+
- FFmpeg (must be in system PATH)

## Running the Application

```bash
# Command-line version (single file)
python mts_converter.py input.mts [output.mp4]

# Command-line version (batch)
python mts_converter.py file1.mts file2.mts file3.mts
python mts_converter.py ./videos/                     # All MTS in directory
python mts_converter.py *.mts --output-dir ./output/  # With output directory
python mts_converter.py input.mts -p top-left         # Specify timestamp position

# GUI version (Windows)
python mts_converter_gui.py
# Or double-click convert_gui.bat

# Drag-and-drop (Windows)
# Drag .MTS files onto convert.bat
```

## Architecture

### Module Structure
- `mts_converter.py` - CLI version with interactive fallback when no args provided
- `mts_converter_gui.py` - tkinter GUI with threading for non-blocking conversion
- `batch_converter.py` - Batch processing module with progress callbacks
- `ffmpeg_utils.py` - FFmpeg path resolution (bundled/system)

### Core Conversion Flow
1. Extract filming timestamp via `ffprobe` metadata (raises `MetadataExtractionError` if unavailable)
2. Build FFmpeg `drawtext` filter using `pts:localtime` for dynamic time display
3. Transcode to H.264/AAC MP4 with `+faststart` flag

### Timestamp Position
The timestamp overlay position can be configured via CLI (`-p/--position`) or GUI dropdown:
- `top-left`, `top-right`, `bottom-left`, `bottom-right`
- Default: `bottom-right`

Position constants and coordinate calculation are in `mts_converter.py`:
- `POSITIONS` dict maps position names to FFmpeg x:y coordinate expressions
- `get_position_coordinates(position, margin)` returns the coordinate string

### Batch Processing
The `BatchConverter` class in `batch_converter.py` provides:
- File discovery from paths, directories, and glob patterns
- Progress callbacks for UI updates (`BatchProgress` protocol)
- Result tracking via `BatchResult` dataclass
- Output directory support with conflict resolution (numeric suffix)
- Continue-on-error behavior (individual failures don't stop batch)

Key FFmpeg filter pattern:
```
drawtext=text='%{pts\:localtime\:<unix_timestamp>\:%Y-%m-%d %H\:%M}':...
```

## Windows Compatibility

All subprocess calls use `creationflags=subprocess.CREATE_NO_WINDOW` on win32 to prevent console window flashing.

## Building Standalone Package

To create a fully standalone distribution (no Python or FFmpeg installation required):

1. Install build dependencies:
   ```bash
   pip install -r requirements-build.txt
   ```

2. Download FFmpeg from https://www.gyan.dev/ffmpeg/builds/ (get `ffmpeg-release-essentials.zip`)

3. Extract `ffmpeg.exe` and `ffprobe.exe` to this directory (or `ffmpeg/` subdirectory)

4. Run build script:
   ```bash
   build.bat
   ```

5. Distribute the `dist/MTS_Converter/` folder

### Files for Standalone Build
- `ffmpeg_utils.py` - Helper to locate bundled/system FFmpeg
- `mts_converter.spec` - PyInstaller configuration
- `build.bat` - Automated build script
