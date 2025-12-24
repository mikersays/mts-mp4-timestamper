# MTS to MP4 Video Converter with Timestamp Overlay

Converts .MTS video files to .MP4 format while adding a dynamic timestamp overlay showing the original filming date/time. The timestamp updates every minute as the video plays.

## For End Users (Standalone Package)

If you received this as a standalone package, no installation is required.

### Contents of Standalone Package

```
MTS_Converter/
├── MTS_Converter.exe      # GUI version (double-click to run)
├── MTS_Converter_CLI.exe  # Command-line version
├── ffmpeg.exe             # Video processing (bundled)
├── ffprobe.exe            # Metadata extraction (bundled)
└── (other support files)
```

### How to Use

**GUI Version (Recommended):**
1. Double-click `MTS_Converter.exe`
2. Click "Browse" to select your .MTS file
3. Choose timestamp position and font size
4. Click "Convert Video"
5. The MP4 file will be saved next to the original

**Command Line Version:**
```
MTS_Converter_CLI.exe "C:\Videos\recording.MTS"
MTS_Converter_CLI.exe "C:\Videos\recording.MTS" "C:\Output\video.mp4"
```

### Timestamp Format

The timestamp appears as: `YYYY-MM-DD HH:MM`

Example: `2024-12-15 14:35`

As the video plays, the minutes increment to show the actual time when each part was recorded.

---

## For Developers

### Requirements

- Python 3.6+
- FFmpeg (in system PATH, or bundled with executable)

### Running from Source

```bash
# Command-line version
python mts_converter.py input.mts [output.mp4]

# GUI version
python mts_converter_gui.py

# Windows batch files
convert_gui.bat          # Launch GUI
convert.bat <file.mts>   # Drag-and-drop conversion
```

### Project Structure

```
├── mts_converter.py       # CLI converter
├── mts_converter_gui.py   # GUI converter (tkinter)
├── ffmpeg_utils.py        # FFmpeg path resolution (bundled/system)
├── convert.bat            # Windows drag-and-drop launcher
├── convert_gui.bat        # Windows GUI launcher
├── mts_converter.spec     # PyInstaller build configuration
├── build.bat              # Automated build script
└── requirements-build.txt # Build dependencies
```

---

## Building Standalone Package

To create a fully standalone distribution that requires no installation:

### Prerequisites

1. **Windows machine** (PyInstaller builds for the host platform)
2. **Python 3.6+** installed
3. **FFmpeg binaries** downloaded

### Step 1: Install Build Tools

```bash
pip install -r requirements-build.txt
```

Or directly:

```bash
pip install pyinstaller
```

### Step 2: Download FFmpeg

1. Go to https://www.gyan.dev/ffmpeg/builds/
2. Download `ffmpeg-release-essentials.zip`
3. Extract the ZIP file
4. Copy `ffmpeg.exe` and `ffprobe.exe` from the `bin` folder to this project directory

Your project folder should now contain:
```
├── ffmpeg.exe
├── ffprobe.exe
├── mts_converter.py
├── mts_converter_gui.py
├── (etc...)
```

### Step 3: Build

Run the build script:

```bash
build.bat
```

Or manually with PyInstaller:

```bash
pyinstaller --clean mts_converter.spec
```

### Step 4: Package for Distribution

After building, copy FFmpeg to the dist folder:

```bash
copy ffmpeg.exe dist\MTS_Converter\
copy ffprobe.exe dist\MTS_Converter\
```

The `dist\MTS_Converter\` folder is now ready to distribute. Zip it up and send to your client:

```bash
cd dist
powershell Compress-Archive -Path MTS_Converter -DestinationPath MTS_Converter.zip
```

---

## Troubleshooting

### "FFmpeg not found" error

**Standalone version:**
- Ensure `ffmpeg.exe` and `ffprobe.exe` are in the same folder as `MTS_Converter.exe`

**Running from source:**
- Install FFmpeg: `winget install FFmpeg`
- Or download from https://ffmpeg.org/download.html
- Add FFmpeg's `bin` folder to your system PATH
- Restart your terminal

### Video won't play

- Install VLC media player
- The output uses standard H.264/AAC codecs which work on most players

### Wrong timestamp

- The tool reads the filming time from video metadata
- If metadata is missing, it falls back to the file's modification date
- MTS files from camcorders typically have accurate metadata

---

## How It Works

1. Extracts the original filming timestamp from video metadata using `ffprobe`
2. Falls back to file modification time if metadata is unavailable
3. Applies FFmpeg `drawtext` filter with dynamic time calculation
4. Transcodes to H.264 video + AAC audio in MP4 container
5. Uses `+faststart` flag for web-optimized playback

### FFmpeg Filter

```
drawtext=text='%{pts\:localtime\:<unix_timestamp>\:%Y-%m-%d %H\:%M}':fontsize=24:fontcolor=white:borderw=2:bordercolor=black:x=20:y=20
```

This filter displays the time based on video PTS (presentation timestamp) plus the original recording time, updating every minute.

---

## License

MIT License - Feel free to modify and distribute.
