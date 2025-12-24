@echo off
REM Build script for MTS to MP4 Converter standalone package
REM
REM Prerequisites:
REM   1. Python 3.6+ installed
REM   2. pip install pyinstaller
REM   3. Download FFmpeg from https://www.gyan.dev/ffmpeg/builds/
REM      (Get ffmpeg-release-essentials.zip)
REM
REM This script will:
REM   1. Build the executable using PyInstaller
REM   2. Copy FFmpeg binaries to the dist folder
REM   3. Create a ready-to-distribute package

echo ============================================
echo   MTS to MP4 Converter - Build Script
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
if not exist "ffmpeg\ffmpeg.exe" (
    if not exist "ffmpeg.exe" (
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
)

echo Building executable with PyInstaller...
echo.

pyinstaller --clean mts_converter.spec

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Build failed!
    exit /b 1
)

echo.
echo Copying FFmpeg binaries to dist folder...

REM Copy FFmpeg from ffmpeg subfolder or current directory
if exist "ffmpeg\ffmpeg.exe" (
    copy /Y "ffmpeg\ffmpeg.exe" "dist\MTS_Converter\"
    copy /Y "ffmpeg\ffprobe.exe" "dist\MTS_Converter\"
) else (
    copy /Y "ffmpeg.exe" "dist\MTS_Converter\"
    copy /Y "ffprobe.exe" "dist\MTS_Converter\"
)

echo.
echo ============================================
echo   BUILD COMPLETE!
echo ============================================
echo.
echo Standalone package is in: dist\MTS_Converter\
echo.
echo Contents:
dir /b dist\MTS_Converter\
echo.
echo You can now zip the dist\MTS_Converter folder
echo and distribute it to your client.
echo.
pause
