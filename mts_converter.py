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


class MetadataExtractionError(Exception):
    """Raised when video metadata timestamp cannot be extracted.

    This error indicates that the recording timestamp could not be determined
    from the video file's metadata. The application does NOT fall back to
    file system timestamps to ensure timestamp accuracy.
    """
    pass


def get_unique_output_path(input_path: Path, output_dir: Path = None) -> Path:
    """Get a unique output path that won't overwrite existing files.

    Args:
        input_path: Path to the input file.
        output_dir: Optional output directory. If None, uses input file's directory.

    Returns:
        Path for the output MP4 file with sequential numbering if needed.
    """
    if output_dir is None:
        output_dir = input_path.parent

    # Base output path
    base_output = output_dir / input_path.with_suffix('.mp4').name

    # If no conflict, use the base name
    if not base_output.exists():
        return base_output

    # Find a unique filename with numeric suffix like "filename (1).mp4"
    stem = input_path.stem
    counter = 1
    while True:
        candidate = output_dir / f"{stem} ({counter}).mp4"
        if not candidate.exists():
            return candidate
        counter += 1


def _bcd_to_int(byte_val):
    """Decode a BCD (Binary-Coded Decimal) byte to integer.

    Args:
        byte_val: A byte value where each nibble represents a decimal digit.

    Returns:
        Integer value decoded from BCD.
    """
    return ((byte_val >> 4) * 10) + (byte_val & 0x0F)


def debug_dpm_bytes(input_file, num_bytes=32):
    """Dump hex bytes around DPM marker for debugging timestamp extraction.

    Args:
        input_file: Path to the MTS/AVCHD video file.
        num_bytes: Number of bytes to dump after finding DPM marker.

    Returns:
        Tuple of (hex_string, offset) where hex_string is space-separated hex bytes
        and offset is the file offset where DPM was found, or (None, None) if not found.
    """
    try:
        with open(input_file, 'rb') as f:
            data = f.read(65536)

        dpm_marker = b'DPM'
        idx = data.find(dpm_marker)

        if idx < 0:
            return None, None

        # Get bytes including the DPM marker
        end_idx = min(idx + num_bytes, len(data))
        raw_bytes = data[idx:end_idx]
        hex_str = ' '.join(f'{b:02X}' for b in raw_bytes)

        return hex_str, idx
    except (IOError, OSError):
        return None, None


def extract_avchd_timestamp(input_file):
    """Extract timestamp from AVCHD/MTS file using DPM marker in SEI data.

    AVCHD cameras (Sony, Panasonic, etc.) embed recording timestamps in
    H.264 SEI (Supplemental Enhancement Information) user data with a
    'DPM' marker. The timestamp is BCD-encoded.

    DPM marker format (at offset after 'DPM'):
        Bytes 0-2: Unknown/reserved
        Bytes 3-4: Year (BCD, e.g., 0x20 0x25 = 2025)
        Byte 5: Month (BCD, e.g., 0x09 = September)
        Byte 6: Unknown
        Byte 7: Day (BCD, e.g., 0x07 = 7th)
        Byte 8: Hour (BCD, e.g., 0x14 = 14:00)
        Byte 9: Minute (BCD, e.g., 0x32 = 32)
        Byte 10: Second (BCD, e.g., 0x35 = 35)

    Args:
        input_file: Path to the MTS/AVCHD video file.

    Returns:
        datetime object representing the recording timestamp, or None if
        the DPM marker is not found or cannot be parsed.
    """
    try:
        with open(input_file, 'rb') as f:
            # Read first 64KB - DPM marker is typically in the first few KB
            data = f.read(65536)

        # Search for DPM marker (0x44 0x50 0x4D = 'DPM')
        dpm_marker = b'DPM'
        idx = data.find(dpm_marker)

        if idx < 0:
            return None

        # Ensure we have enough bytes after the marker
        if idx + 14 > len(data):
            return None

        # Extract timestamp bytes (starting after 'DPM')
        ts_data = data[idx + 3:idx + 14]

        # Parse BCD-encoded timestamp
        year_hi = _bcd_to_int(ts_data[3])  # Usually 20
        year_lo = _bcd_to_int(ts_data[4])  # e.g., 25 for 2025
        year = year_hi * 100 + year_lo
        month = _bcd_to_int(ts_data[5])
        day = _bcd_to_int(ts_data[7])
        hour = _bcd_to_int(ts_data[8])
        minute = _bcd_to_int(ts_data[9])
        second = _bcd_to_int(ts_data[10])

        # Validate parsed values
        if not (1 <= month <= 12):
            return None
        if not (1 <= day <= 31):
            return None
        if not (0 <= hour <= 23):
            return None
        if not (0 <= minute <= 59):
            return None
        if not (0 <= second <= 59):
            return None
        if not (1990 <= year <= 2100):
            return None

        return datetime(year, month, day, hour, minute, second)

    except (IOError, OSError, ValueError):
        return None

# Position constants for timestamp overlay
DEFAULT_POSITION = 'bottom-right'
POSITIONS = {
    'top-left': 'x=20:y=20',
    'top-right': 'x=w-tw-20:y=20',
    'bottom-left': 'x=20:y=h-th-20',
    'bottom-right': 'x=w-tw-20:y=h-th-20',
}

# Resolution presets for output scaling
DEFAULT_RESOLUTION = 'original'
RESOLUTION_PRESETS = {
    'original': None,
    '1080p': (1920, 1080),
    '720p': (1280, 720),
    '480p': (854, 480),
}


def build_video_filter(drawtext_filter, resolution='original'):
    """Build combined video filter with optional scaling.

    Args:
        drawtext_filter: The drawtext filter string for timestamp overlay.
        resolution: Resolution preset name ('original', '1080p', '720p', '480p').

    Returns:
        Combined filter string with drawtext and optional scale filter.
    """
    if resolution == 'original' or resolution is None:
        return drawtext_filter

    dims = RESOLUTION_PRESETS.get(resolution)
    if dims is None:
        return drawtext_filter

    width, height = dims
    # Use -2 for height to auto-calculate while keeping even number (required for h264)
    scale_filter = f"scale={width}:-2"
    return f"{drawtext_filter},{scale_filter}"


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
        result.position = DEFAULT_POSITION
        result.resolution = DEFAULT_RESOLUTION
        result.debug_timestamp = False
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

    parser.add_argument(
        '-p', '--position',
        dest='position',
        default=DEFAULT_POSITION,
        choices=['top-left', 'top-right', 'bottom-left', 'bottom-right'],
        help=f'Timestamp position (default: {DEFAULT_POSITION})'
    )

    parser.add_argument(
        '-r', '--resolution',
        dest='resolution',
        default=DEFAULT_RESOLUTION,
        choices=['original', '1080p', '720p', '480p'],
        help=f'Output resolution preset (default: {DEFAULT_RESOLUTION})'
    )

    parser.add_argument(
        '--debug-timestamp',
        action='store_true',
        dest='debug_timestamp',
        help='Debug mode: dump DPM marker hex bytes for timestamp analysis'
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
    """Extract the creation/recording time from video metadata.

    Uses AVCHD DPM marker extraction as the primary method (for MTS files
    from Sony, Panasonic, and other AVCHD cameras), with ffprobe metadata
    extraction as a fallback.

    Args:
        input_file: Path to the video file.

    Returns:
        datetime object representing the recording timestamp.

    Raises:
        MetadataExtractionError: If the timestamp cannot be extracted from
            video metadata. This error is raised instead of falling back to
            file modification time to ensure timestamp accuracy.
    """
    # Primary method: Extract from AVCHD DPM marker (embedded in H.264 SEI data)
    avchd_timestamp = extract_avchd_timestamp(input_file)
    if avchd_timestamp is not None:
        return avchd_timestamp

    # Fallback: Try ffprobe creation_time tag
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

        # No valid timestamp found in metadata
        raise MetadataExtractionError(
            f"Could not extract recording timestamp from metadata in '{input_file}'. "
            "The file may be corrupted, missing metadata, or not an MTS video file."
        )

    except MetadataExtractionError:
        # Re-raise our own exception
        raise
    except Exception as e:
        raise MetadataExtractionError(
            f"Failed to extract recording timestamp from '{input_file}': {e}"
        )


def convert_video(input_file, output_file=None, font_size=32, position=None, resolution=None):
    """
    Convert MTS to MP4 with dynamic timestamp overlay.

    The timestamp shows the original filming date/time and updates every minute
    as the video progresses.

    Args:
        input_file: Path to the input MTS file.
        output_file: Optional path for the output MP4 file.
        font_size: Font size for the timestamp text (default: 32).
        position: Timestamp position. One of 'top-left', 'top-right',
                  'bottom-left', 'bottom-right'. Default is DEFAULT_POSITION.
        resolution: Output resolution preset. One of 'original', '1080p',
                    '720p', '480p'. Default is 'original' (no scaling).

    Returns:
        True if conversion succeeded, False otherwise.
    """
    input_path = Path(input_file)

    if not input_path.exists():
        print(f"Error: Input file '{input_file}' not found.")
        return False

    if not input_path.suffix.lower() == '.mts':
        print(f"Warning: Input file is not .MTS format, proceeding anyway...")

    # Set output filename - use unique path to avoid overwriting
    if output_file is None:
        output_path = get_unique_output_path(input_path)
    else:
        output_path = Path(output_file)

    # Get the original filming time
    try:
        filming_time = get_video_creation_time(input_file)
    except MetadataExtractionError as e:
        print(f"\nError: {e}")
        print("The recording timestamp could not be determined from the video metadata.")
        print("Possible causes: corrupted file, missing metadata, or non-MTS source file.")
        return False

    print(f"Detected filming time: {filming_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Get position coordinates using the utility function
    pos = get_position_coordinates(position)

    # Build the drawtext filter with dynamic time calculation
    # The timestamp updates every second as the video plays
    # We use FFmpeg expression language to calculate current time
    drawtext_filter = (
        f"drawtext="
        f"text='%{{pts\\:localtime\\:{int(filming_time.timestamp())}\\:%Y-%m-%d %H\\\\\\:%M\\\\\\:%S}}':"
        f"fontsize={font_size}:"
        f"fontcolor=white:"
        f"borderw=2:"
        f"bordercolor=black:"
        f"{pos}"
    )

    # Combine drawtext with optional resolution scaling
    video_filter = build_video_filter(drawtext_filter, resolution)

    # FFmpeg command
    ffmpeg = FFMPEG_PATH or get_ffmpeg_path()
    cmd = [
        ffmpeg,
        "-i", str(input_path),
        "-vf", video_filter,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-threads", "0",  # Use all available CPU cores
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

    # Debug timestamp mode: dump DPM bytes for analysis
    if parsed.debug_timestamp:
        files = discover_files(parsed.input_paths)
        if not files:
            print("No MTS files found.")
            return (0, 0)

        for f in files:
            print(f"\n{'='*60}")
            print(f"File: {f.name}")
            print(f"{'='*60}")

            hex_bytes, offset = debug_dpm_bytes(str(f))
            if hex_bytes is None:
                print("DPM marker not found in file.")
            else:
                print(f"DPM marker found at offset: {offset}")
                print(f"\nRaw bytes (starting at 'DPM'):")
                print(hex_bytes)
                print(f"\nByte positions after 'DPM' marker:")
                print("  Offset: 0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 ...")
                bytes_list = hex_bytes.split()
                print(f"  Values: {' '.join(bytes_list[3:18])}")  # Skip 'D P M'
                print(f"\nByte extraction mapping:")
                print(f"  Year:   byte[3-4] = {bytes_list[6] if len(bytes_list) > 6 else '?'} {bytes_list[7] if len(bytes_list) > 7 else '?'}")
                print(f"  Month:  byte[5]   = {bytes_list[8] if len(bytes_list) > 8 else '?'}")
                print(f"  Day:    byte[7]   = {bytes_list[10] if len(bytes_list) > 10 else '?'}")
                print(f"  Hour:   byte[8]   = {bytes_list[11] if len(bytes_list) > 11 else '?'}")
                print(f"  Minute: byte[9]   = {bytes_list[12] if len(bytes_list) > 12 else '?'}")
                print(f"  Second: byte[10]  = {bytes_list[13] if len(bytes_list) > 13 else '?'}")

                # Try current extraction
                ts = extract_avchd_timestamp(str(f))
                if ts:
                    print(f"\nExtracted timestamp: {ts.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    print(f"\nExtracted timestamp: FAILED")

        return (len(files), 0)

    # Check for FFmpeg
    if not check_ffmpeg():
        print("\nError: FFmpeg is not installed or not in PATH.")
        return (0, 0)

    # Legacy mode: single file with explicit output
    if parsed.legacy_mode:
        success = convert_video(
            parsed.input_paths[0],
            parsed.output_file,
            position=parsed.position,
            resolution=parsed.resolution
        )
        return (1, 0) if success else (0, 1)

    # Batch mode: discover files and use BatchConverter
    files = discover_files(parsed.input_paths)

    if not files:
        print("No MTS files found.")
        return (0, 0)

    # Progress callback for displaying per-file progress
    def progress_callback(current, total, current_file):
        print(f"Converting {current}/{total}: {current_file.name}")

    # Create batch converter with output directory, position and resolution if specified
    output_dir = Path(parsed.output_dir) if parsed.output_dir else None
    converter = BatchConverter(
        progress_callback=progress_callback,
        output_dir=output_dir,
        position=parsed.position,
        resolution=parsed.resolution
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
