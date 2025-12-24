#!/usr/bin/env python3
"""
MTS to MP4 Video Converter with Dynamic Timestamp Overlay

This tool converts .MTS video files to .MP4 format while adding a timestamp
overlay that shows when the video was filmed and tracks time as it progresses.
"""

import subprocess
import sys
import os
import re
from datetime import datetime
from pathlib import Path

from ffmpeg_utils import (
    get_ffmpeg_path,
    get_ffprobe_path,
    check_ffmpeg_available,
    get_subprocess_flags
)


# Module-level paths (set during initialization)
FFMPEG_PATH = None
FFPROBE_PATH = None


def check_ffmpeg():
    """Check if FFmpeg is installed and available."""
    global FFMPEG_PATH, FFPROBE_PATH
    available, ffmpeg, ffprobe = check_ffmpeg_available()
    if available:
        FFMPEG_PATH = ffmpeg
        FFPROBE_PATH = ffprobe
    return available


def get_video_creation_time(input_file):
    """Extract the creation/recording time from video metadata using ffprobe."""
    ffprobe = FFPROBE_PATH or get_ffprobe_path()
    try:
        result = subprocess.run(
            [
                ffprobe,
                "-v", "quiet",
                "-select_streams", "v:0",
                "-show_entries", "format_tags=creation_time:stream_tags=creation_time",
                "-of", "csv=p=0",
                input_file
            ],
            capture_output=True,
            text=True,
            creationflags=get_subprocess_flags()
        )

        output = result.stdout.strip()
        if output:
            # Parse the creation time (usually in ISO format)
            time_str = output.split('\n')[0].strip(',')
            if time_str:
                # Handle various date formats
                for fmt in [
                    "%Y-%m-%dT%H:%M:%S.%fZ",
                    "%Y-%m-%dT%H:%M:%SZ",
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S.%f",
                    "%Y-%m-%dT%H:%M:%S"
                ]:
                    try:
                        return datetime.strptime(time_str, fmt)
                    except ValueError:
                        continue
    except Exception as e:
        print(f"Warning: Could not extract creation time from metadata: {e}")

    # Fallback to file modification time
    try:
        mtime = os.path.getmtime(input_file)
        return datetime.fromtimestamp(mtime)
    except Exception:
        return datetime.now()


def convert_video(input_file, output_file=None, font_size=24, position="top-left"):
    """
    Convert MTS to MP4 with dynamic timestamp overlay.

    The timestamp shows the original filming date/time and updates every minute
    as the video progresses.
    """
    input_path = Path(input_file)

    if not input_path.exists():
        print(f"Error: Input file '{input_file}' not found.")
        return False

    if not input_path.suffix.lower() == '.mts':
        print(f"Warning: Input file is not .MTS format, proceeding anyway...")

    # Set output filename
    if output_file is None:
        output_file = input_path.with_suffix('.mp4')
    output_path = Path(output_file)

    # Get the original filming time
    filming_time = get_video_creation_time(input_file)
    print(f"Detected filming time: {filming_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Calculate base timestamp components for FFmpeg expression
    base_year = filming_time.year
    base_month = filming_time.month
    base_day = filming_time.day
    base_hour = filming_time.hour
    base_minute = filming_time.minute
    base_second = filming_time.second

    # Convert base time to total seconds since midnight for easier calculation
    base_seconds = base_hour * 3600 + base_minute * 60 + base_second

    # Position mapping
    positions = {
        "top-left": "x=20:y=20",
        "top-right": "x=w-tw-20:y=20",
        "bottom-left": "x=20:y=h-th-20",
        "bottom-right": "x=w-tw-20:y=h-th-20",
        "center": "x=(w-tw)/2:y=(h-th)/2"
    }
    pos = positions.get(position, positions["top-left"])

    # Build the drawtext filter with dynamic time calculation
    # The timestamp updates every minute (floor to minute)
    # We use FFmpeg expression language to calculate current time
    drawtext_filter = (
        f"drawtext="
        f"text='%{{pts\\:localtime\\:{int(filming_time.timestamp())}\\:%Y-%m-%d %H\\\\\\:%M}}':"
        f"fontsize={font_size}:"
        f"fontcolor=white:"
        f"borderw=2:"
        f"bordercolor=black:"
        f"{pos}"
    )

    # FFmpeg command
    ffmpeg = FFMPEG_PATH or get_ffmpeg_path()
    cmd = [
        ffmpeg,
        "-i", str(input_path),
        "-vf", drawtext_filter,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-y",  # Overwrite output file if exists
        str(output_path)
    ]

    print(f"\nConverting: {input_path.name} -> {output_path.name}")
    print("This may take a while depending on video length...\n")

    try:
        # Run FFmpeg with progress output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            creationflags=get_subprocess_flags()
        )

        # Show progress
        for line in process.stdout:
            if "frame=" in line or "time=" in line:
                # Extract progress info
                print(f"\r{line.strip()[:80]}", end="", flush=True)

        process.wait()

        if process.returncode == 0:
            print(f"\n\nSuccess! Output saved to: {output_path}")
            return True
        else:
            print(f"\n\nError: FFmpeg returned code {process.returncode}")
            return False

    except Exception as e:
        print(f"\n\nError during conversion: {e}")
        return False


def main():
    """Main entry point."""
    print("=" * 60)
    print("  MTS to MP4 Converter with Timestamp Overlay")
    print("=" * 60)

    # Check for FFmpeg
    if not check_ffmpeg():
        print("\nError: FFmpeg is not installed or not in PATH.")
        print("Please install FFmpeg:")
        print("  - Windows: Download from https://ffmpeg.org/download.html")
        print("            or use: winget install FFmpeg")
        print("  - Add FFmpeg to your system PATH")
        sys.exit(1)

    # Parse arguments
    if len(sys.argv) < 2:
        print("\nUsage: python mts_converter.py <input.mts> [output.mp4]")
        print("\nOptions:")
        print("  input.mts   - Path to the input .MTS video file")
        print("  output.mp4  - (Optional) Path for the output .MP4 file")
        print("\nThe timestamp overlay shows the original filming date/time")
        print("and updates every minute as the video plays.")

        # Interactive mode
        print("\n" + "-" * 40)
        input_file = input("Enter path to .MTS file (or drag & drop): ").strip().strip('"\'')

        if not input_file:
            print("No file provided. Exiting.")
            sys.exit(1)
    else:
        input_file = sys.argv[1]

    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    # Convert
    success = convert_video(input_file, output_file)

    if not success:
        sys.exit(1)

    print("\nDone!")


if __name__ == "__main__":
    main()
