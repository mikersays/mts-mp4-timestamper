@echo off
setlocal enabledelayedexpansion

title MTS to MP4 Converter with Timestamp

echo ============================================================
echo   MTS to MP4 Converter with Timestamp Overlay
echo ============================================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

:: Check if FFmpeg is available
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo Error: FFmpeg is not installed or not in PATH.
    echo Please install FFmpeg:
    echo   - Download from https://ffmpeg.org/download.html
    echo   - Or use: winget install FFmpeg
    echo   - Make sure to add FFmpeg to your system PATH
    pause
    exit /b 1
)

:: Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"

:: Check if a file was dragged onto the batch file
if "%~1"=="" (
    :: No file provided, run in interactive mode
    python "%SCRIPT_DIR%mts_converter.py"
) else (
    :: Process all dragged files
    for %%f in (%*) do (
        echo Processing: %%~nxf
        python "%SCRIPT_DIR%mts_converter.py" "%%~f"
        echo.
    )
)

echo.
echo ============================================================
pause
