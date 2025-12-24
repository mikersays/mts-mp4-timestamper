#!/usr/bin/env python3
"""
FFmpeg utilities for locating bundled or system FFmpeg executables.

Supports both development (system PATH) and PyInstaller frozen builds.
"""

import os
import sys
import subprocess


def get_base_path():
    """Get the base path for bundled files (works with PyInstaller)."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))


def find_executable(name):
    """
    Find an executable by name, checking bundled location first.

    Args:
        name: Executable name without extension (e.g., 'ffmpeg', 'ffprobe')

    Returns:
        Full path to executable, or just the name if relying on system PATH.
    """
    base_path = get_base_path()

    # On Windows, add .exe extension
    if sys.platform == 'win32':
        exe_name = f"{name}.exe"
    else:
        exe_name = name

    # Check bundled location (same directory as script/executable)
    bundled_path = os.path.join(base_path, exe_name)
    if os.path.isfile(bundled_path):
        return bundled_path

    # Check in 'ffmpeg' subdirectory
    subdir_path = os.path.join(base_path, 'ffmpeg', exe_name)
    if os.path.isfile(subdir_path):
        return subdir_path

    # Fall back to system PATH
    return name


def get_ffmpeg_path():
    """Get path to ffmpeg executable."""
    return find_executable('ffmpeg')


def get_ffprobe_path():
    """Get path to ffprobe executable."""
    return find_executable('ffprobe')


def check_ffmpeg_available():
    """
    Check if FFmpeg is available (bundled or system).

    Returns:
        tuple: (is_available: bool, ffmpeg_path: str, ffprobe_path: str)
    """
    ffmpeg = get_ffmpeg_path()
    ffprobe = get_ffprobe_path()

    creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0

    try:
        subprocess.run(
            [ffmpeg, '-version'],
            capture_output=True,
            check=True,
            creationflags=creationflags
        )
        subprocess.run(
            [ffprobe, '-version'],
            capture_output=True,
            check=True,
            creationflags=creationflags
        )
        return True, ffmpeg, ffprobe
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False, ffmpeg, ffprobe


def get_subprocess_flags():
    """Get platform-specific subprocess creation flags."""
    if sys.platform == 'win32':
        return subprocess.CREATE_NO_WINDOW
    return 0
