#!/usr/bin/env python3
"""
MTS to MP4 Video Converter with Dynamic Timestamp Overlay

This tool converts .MTS video files to .MP4 format while adding a timestamp
overlay that shows when the video was filmed and tracks time as it progresses.
"""

import argparse
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

# Position constants for timestamp overlay
DEFAULT_POSITION = 'bottom-right'
POSITIONS = {
    'top-left': 'x=20:y=20',
    'top-right': 'x=w-tw-20:y=20',
    'bottom-left': 'x=20:y=h-th-20',
    'bottom-right': 'x=w-tw-20:y=h-th-20',
}


def get_position_coordinates(position, margin=20):
    """Get FFmpeg x:y coordinate expression for a given position.

    Args:
        position: One of 'top-left', 'top-right', 'bottom-left', 'bottom-right',
                  or None (uses DEFAULT_POSITION).
        margin: Pixel margin from edges (default: 20).

    Returns:
        String containing FFmpeg x=...:y=... expression.

    Raises:
        ValueError: If position is not a valid position name.
    """
    if position is None:
        position = DEFAULT_POSITION

    if position not in POSITIONS:
        raise ValueError(
            f"Invalid position '{position}'. "
            f"Must be one of: {', '.join(POSITIONS.keys())}"
        )

    # Build coordinates with the specified margin
    if position == 'top-left':
        return f'x={margin}:y={margin}'
    elif position == 'top-right':
        return f'x=w-tw-{margin}:y={margin}'
    elif position == 'bottom-left':
        return f'x={margin}:y=h-th-{margin}'
    elif position == 'bottom-right':
        return f'x=w-tw-{margin}:y=h-th-{margin}'

    # Fallback (should not reach here due to validation above)
    return POSITIONS[position]


def parse_args(args):
    """Parse command-line arguments for batch processing support.

    Args:
        args: List of command-line arguments (without script name).

    Returns:
        Namespace with parsed arguments, or None if no input provided.
    """
    if not args:
        return None

    # Check for legacy mode: input.mts output.mp4
    # Legacy mode is when we have exactly 2 args and the second ends with .mp4
    if len(args) == 2 and args[1].lower().endswith('.mp4'):
        # Legacy single-file mode with explicit output
        result = argparse.Namespace()
        result.input_paths = [args[0]]
        result.output_file = args[1]
        result.output_dir = None
        result.continue_on_error = True
        result.legacy_mode = True
        return result

    parser = argparse.ArgumentParser(
        description='MTS to MP4 Converter with Timestamp Overlay',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s video.mts                    Convert single file
  %(prog)s video.mts output.mp4         Convert with specific output name
  %(prog)s *.mts                        Convert all MTS files in current dir
  %(prog)s video1.mts video2.mts        Convert multiple files
  %(prog)s ./videos/ -o ./converted/    Convert directory to output folder
'''
    )

    parser.add_argument(
        'input_paths',
        nargs='+',
        help='Input .MTS file(s), directory, or glob pattern'
    )

    parser.add_argument(
        '-o', '--output-dir',
        dest='output_dir',
        default=None,
        help='Output directory for converted files'
    )

    parser.add_argument(
        '--continue-on-error',
        action='store_true',
        default=True,
        dest='continue_on_error',
        help='Continue processing remaining files if one fails (default)'
    )

    parser.add_argument(
        '--stop-on-error',
        action='store_false',
        dest='continue_on_error',
        help='Stop processing if any file fails'
    )

    parsed = parser.parse_args(args)
    parsed.output_file = None
    parsed.legacy_mode = False

    return parsed


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


def convert_video(input_file, output_file=None, font_size=24, position=None):
    """
    Convert MTS to MP4 with dynamic timestamp overlay.

    The timestamp shows the original filming date/time and updates every minute
    as the video progresses.

    Args:
        input_file: Path to the input MTS file.
        output_file: Optional path for the output MP4 file.
        font_size: Font size for the timestamp text (default: 24).
        position: Timestamp position. One of 'top-left', 'top-right',
                  'bottom-left', 'bottom-right'. Default is DEFAULT_POSITION.

    Returns:
        True if conversion succeeded, False otherwise.
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

    # Get position coordinates using the utility function
    pos = get_position_coordinates(position)

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


def run_cli(args):
    """Run the CLI with the given arguments.

    Args:
        args: List of command-line arguments (without script name).

    Returns:
        Tuple of (success_count, failure_count).
    """
    # Import here to avoid circular import
    from batch_converter import BatchConverter, discover_files

    parsed = parse_args(args)

    if parsed is None:
        return (0, 0)

    # Check for FFmpeg
    if not check_ffmpeg():
        print("\nError: FFmpeg is not installed or not in PATH.")
        return (0, 0)

    # Legacy mode: single file with explicit output
    if parsed.legacy_mode:
        success = convert_video(parsed.input_paths[0], parsed.output_file)
        return (1, 0) if success else (0, 1)

    # Batch mode: discover files and use BatchConverter
    files = discover_files(parsed.input_paths)

    if not files:
        print("No MTS files found.")
        return (0, 0)

    # Progress callback for displaying per-file progress
    def progress_callback(current, total, current_file):
        print(f"Converting {current}/{total}: {current_file.name}")

    # Create batch converter with output directory if specified
    output_dir = Path(parsed.output_dir) if parsed.output_dir else None
    converter = BatchConverter(
        progress_callback=progress_callback,
        output_dir=output_dir
    )

    # Run batch conversion
    results = converter.convert_batch(files)

    # Calculate success/failure counts
    success_count = sum(1 for r in results if r.success)
    failure_count = len(results) - success_count

    # Show batch summary
    print(f"\n{'=' * 40}")
    print(f"Batch conversion complete:")
    print(f"  Total: {len(results)} files")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {failure_count}")

    if failure_count > 0:
        print("\nFailed files:")
        for r in results:
            if not r.success:
                print(f"  - {r.input_file.name}: {r.error}")

    return (success_count, failure_count)


def main():
    """Main entry point."""
    print("=" * 60)
    print("  MTS to MP4 Converter with Timestamp Overlay")
    print("=" * 60)

    args = sys.argv[1:]

    # Interactive mode if no arguments
    if not args:
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

        args = [input_file]

    # Use run_cli for both single-file and batch mode
    success_count, failure_count = run_cli(args)

    # Print completion message for successful conversions
    if success_count > 0:
        print("\nDone!")

    # Exit with appropriate code
    if failure_count > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
