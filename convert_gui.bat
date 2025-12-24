@echo off
:: Launch the GUI version of MTS to MP4 Converter

set "SCRIPT_DIR=%~dp0"

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

:: Launch the GUI (use pythonw to hide console window)
start "" pythonw "%SCRIPT_DIR%mts_converter_gui.py"
