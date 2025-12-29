@echo off
REM Build script for MTS to MP4 Converter standalone package (Single-file mode)
REM
REM Prerequisites:
REM   1. Python 3.6+ installed
REM   2. pip install pyinstaller
REM   3. Download FFmpeg from https://www.gyan.dev/ffmpeg/builds/
REM      (Get ffmpeg-release-essentials.zip)
REM
REM This script will build single-file executables with FFmpeg bundled inside.

echo ============================================
echo   MTS to MP4 Converter - Build Script
echo   (Single-file mode)
echo ============================================
echo.

REM Check for PyInstaller
where pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: PyInstaller not found!
    echo Please install it with: pip install pyinstaller
    exit /b 1
)

REM Check for FFmpeg files
set FFMPEG_FOUND=0
if exist "ffmpeg.exe" set FFMPEG_FOUND=1
if exist "ffmpeg\ffmpeg.exe" set FFMPEG_FOUND=1

if %FFMPEG_FOUND%==0 (
    echo.
    echo WARNING: ffmpeg.exe not found!
    echo.
    echo Please download FFmpeg and place the files:
    echo   - ffmpeg.exe
    echo   - ffprobe.exe
    echo.
    echo Either in this directory or in a 'ffmpeg' subdirectory.
    echo.
    echo Download from: https://www.gyan.dev/ffmpeg/builds/
    echo Get: ffmpeg-release-essentials.zip
    echo Extract ffmpeg.exe and ffprobe.exe from the bin folder.
    echo.
    pause
    exit /b 1
)

echo Building single-file executables with PyInstaller...
echo (This may take a few minutes - FFmpeg binaries are being bundled)
echo.

pyinstaller --clean mts_converter.spec

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Build failed!
    exit /b 1
)

echo.
echo ============================================
echo   BUILD COMPLETE!
echo ============================================
echo.
echo Single-file executables are in: dist\
echo.
echo Output files:
dir /b dist\*.exe
echo.
echo You can now share these .exe files directly!
echo Each file is fully standalone with FFmpeg bundled inside.
echo.
echo NOTE: First startup may be slightly slower as the exe
echo       extracts bundled files to a temp directory.
echo.
pause
