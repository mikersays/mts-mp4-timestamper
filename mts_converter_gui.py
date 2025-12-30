#!/usr/bin/env python3
"""
MTS to MP4 Video Converter with Dynamic Timestamp Overlay - GUI Version

A simple Windows GUI for converting .MTS videos to .MP4 with timestamp overlay.
Supports batch processing of multiple files with progress tracking.
"""

import re
import subprocess
import sys
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from ffmpeg_utils import (
    get_ffmpeg_path,
    get_ffprobe_path,
    check_ffmpeg_available,
    get_subprocess_flags
)
from mts_converter import MetadataExtractionError, extract_avchd_timestamp, build_video_filter

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
except ImportError:
    print("Error: tkinter is required for the GUI version.")
    print("Please use the command-line version: mts_converter.py")
    sys.exit(1)


class MTSConverterGUI:
    """GUI application for batch converting MTS videos to MP4 with timestamps."""

    def __init__(self, root):
        """Initialize the GUI application.

        Args:
            root: The tkinter root window.
        """
        self.root = root
        self.root.title("MTS to MP4 Converter with Timestamp")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        # File queue for batch processing
        self.file_queue: List[Path] = []
        self.batch_results: List = []

        # Batch processing state
        self.is_converting = False
        self.cancel_requested = False
        self.batch_start_time: Optional[float] = None

        # Output directory (None = same as source)
        self.output_dir: Optional[Path] = None

        # Timestamp options
        self.position = tk.StringVar(value="bottom-right")
        self.font_size = tk.IntVar(value=32)
        self.resolution = tk.StringVar(value="Original")

        # Progress tracking
        self.batch_progress_var = tk.DoubleVar(value=0)
        self.file_progress_var = tk.DoubleVar(value=0)

        self.create_widgets()
        self.check_dependencies()

    def create_widgets(self):
        """Create all GUI widgets."""
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="MTS to MP4 Batch Converter",
            font=("Segoe UI", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 10))

        subtitle = ttk.Label(
            main_frame,
            text="Convert MTS videos with dynamic timestamp overlay",
            font=("Segoe UI", 9)
        )
        subtitle.grid(row=1, column=0, columnspan=4, pady=(0, 15))

        # File queue frame
        queue_frame = ttk.LabelFrame(main_frame, text="File Queue", padding="5")
        queue_frame.grid(row=2, column=0, columnspan=4, sticky="nsew", pady=5)
        queue_frame.columnconfigure(0, weight=1)
        queue_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # File listbox with scrollbar
        self.file_listbox = tk.Listbox(
            queue_frame,
            height=8,
            selectmode=tk.EXTENDED
        )
        self.file_listbox.grid(row=0, column=0, sticky="nsew")

        queue_scrollbar = ttk.Scrollbar(
            queue_frame,
            orient="vertical",
            command=self.file_listbox.yview
        )
        queue_scrollbar.grid(row=0, column=1, sticky="ns")
        self.file_listbox.configure(yscrollcommand=queue_scrollbar.set)

        # File queue buttons
        queue_btn_frame = ttk.Frame(queue_frame)
        queue_btn_frame.grid(row=1, column=0, columnspan=2, pady=5)

        self.add_files_btn = ttk.Button(
            queue_btn_frame,
            text="Add Files",
            command=self.browse_add_files
        )
        self.add_files_btn.grid(row=0, column=0, padx=2)

        self.add_folder_btn = ttk.Button(
            queue_btn_frame,
            text="Add Folder",
            command=self.browse_add_folder
        )
        self.add_folder_btn.grid(row=0, column=1, padx=2)

        self.remove_btn = ttk.Button(
            queue_btn_frame,
            text="Remove Selected",
            command=self.remove_selected_files
        )
        self.remove_btn.grid(row=0, column=2, padx=2)

        self.clear_all_btn = ttk.Button(
            queue_btn_frame,
            text="Clear All",
            command=self.clear_file_queue
        )
        self.clear_all_btn.grid(row=0, column=3, padx=2)

        # Output directory frame
        output_frame = ttk.LabelFrame(main_frame, text="Output Options", padding="5")
        output_frame.grid(row=3, column=0, columnspan=4, sticky="ew", pady=5)
        output_frame.columnconfigure(1, weight=1)

        ttk.Label(output_frame, text="Output Directory:").grid(
            row=0, column=0, sticky="w", padx=5
        )
        self.output_dir_var = tk.StringVar(value="(Same as source)")
        output_dir_entry = ttk.Entry(
            output_frame,
            textvariable=self.output_dir_var,
            state="readonly"
        )
        output_dir_entry.grid(row=0, column=1, sticky="ew", padx=5)

        self.browse_output_dir_btn = ttk.Button(
            output_frame,
            text="Browse...",
            command=self.browse_output_dir
        )
        self.browse_output_dir_btn.grid(row=0, column=2, padx=5)

        ttk.Button(
            output_frame,
            text="Reset",
            command=self.reset_output_dir
        ).grid(row=0, column=3, padx=5)

        # Timestamp options frame
        options_frame = ttk.LabelFrame(main_frame, text="Timestamp Options", padding="5")
        options_frame.grid(row=4, column=0, columnspan=4, sticky="ew", pady=5)
        options_frame.columnconfigure(1, weight=1)

        # Position selection
        ttk.Label(options_frame, text="Position:").grid(row=0, column=0, sticky="w", pady=5)
        position_combo = ttk.Combobox(
            options_frame,
            textvariable=self.position,
            values=["top-left", "top-right", "bottom-left", "bottom-right"],
            state="readonly",
            width=15
        )
        position_combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Font size
        ttk.Label(options_frame, text="Font Size:").grid(row=1, column=0, sticky="w", pady=5)
        font_spin = ttk.Spinbox(
            options_frame,
            from_=12,
            to=72,
            textvariable=self.font_size,
            width=10
        )
        font_spin.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Resolution
        ttk.Label(options_frame, text="Resolution:").grid(row=2, column=0, sticky="w", pady=5)
        resolution_combo = ttk.Combobox(
            options_frame,
            textvariable=self.resolution,
            values=["Original", "1080p (1920x1080)", "720p (1280x720)", "480p (854x480)"],
            state="readonly",
            width=20
        )
        resolution_combo.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="5")
        progress_frame.grid(row=5, column=0, columnspan=4, sticky="ew", pady=5)
        progress_frame.columnconfigure(0, weight=1)

        # File counter label
        self.file_counter_label = ttk.Label(
            progress_frame,
            text="0 of 0 files",
            font=("Segoe UI", 9)
        )
        self.file_counter_label.grid(row=0, column=0, sticky="w")

        # Elapsed time label
        self.elapsed_time_label = ttk.Label(
            progress_frame,
            text="Elapsed: 00:00",
            font=("Segoe UI", 9)
        )
        self.elapsed_time_label.grid(row=0, column=1, sticky="e")

        # Batch progress bar
        self.batch_progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.batch_progress_var,
            maximum=100,
            mode='determinate'
        )
        self.batch_progress_bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)

        # Per-file progress label
        self.file_progress_label = ttk.Label(
            progress_frame,
            text="Current file: 0%",
            font=("Segoe UI", 9)
        )
        self.file_progress_label.grid(row=2, column=0, sticky="w")

        # Per-file progress bar
        self.file_progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.file_progress_var,
            maximum=100,
            mode='determinate'
        )
        self.file_progress_bar.grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)

        # Current file label
        self.current_file_label = ttk.Label(
            progress_frame,
            text="Ready",
            font=("Segoe UI", 9)
        )
        self.current_file_label.grid(row=4, column=0, columnspan=2, sticky="w")

        # Status label (for FFmpeg output)
        self.status_label = ttk.Label(progress_frame, text="", font=("Segoe UI", 9))
        self.status_label.grid(row=5, column=0, columnspan=2, sticky="w", pady=2)

        # Button frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=6, column=0, columnspan=4, pady=10)

        # Convert button
        self.convert_btn = ttk.Button(
            btn_frame,
            text="Convert All",
            command=self.start_batch_conversion,
            style="Accent.TButton"
        )
        self.convert_btn.grid(row=0, column=0, padx=5, ipadx=20, ipady=5)

        # Cancel button
        self.cancel_btn = ttk.Button(
            btn_frame,
            text="Cancel",
            command=self.request_cancel,
            state="disabled"
        )
        self.cancel_btn.grid(row=0, column=1, padx=5, ipadx=10, ipady=5)

        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.grid(row=7, column=0, columnspan=4, sticky="nsew", pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)

        self.log_text = tk.Text(log_frame, height=6, width=60, state="disabled")
        self.log_text.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=scrollbar.set)

    def log(self, message: str):
        """Add a message to the log area.

        Args:
            message: The message to log.
        """
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def browse_add_files(self):
        """Open file dialog to add multiple MTS files to queue."""
        filenames = filedialog.askopenfilenames(
            title="Select MTS Video Files",
            filetypes=[("MTS Files", "*.mts *.MTS"), ("All Files", "*.*")]
        )
        if filenames:
            self.add_files_to_queue([Path(f) for f in filenames])

    def browse_add_folder(self):
        """Open folder dialog to add all MTS files from a directory."""
        folder = filedialog.askdirectory(title="Select Folder with MTS Files")
        if folder:
            folder_path = Path(folder)
            mts_files = list(folder_path.glob("*.mts")) + list(folder_path.glob("*.MTS"))
            if mts_files:
                self.add_files_to_queue(mts_files)
                self.log(f"Added {len(mts_files)} file(s) from {folder}")
            else:
                messagebox.showinfo("No Files", "No MTS files found in the selected folder.")

    def browse_output_dir(self):
        """Open folder dialog to select output directory."""
        folder = filedialog.askdirectory(title="Select Output Directory")
        if folder:
            self.output_dir = Path(folder)
            self.output_dir_var.set(str(self.output_dir))

    def reset_output_dir(self):
        """Reset output directory to default (same as source)."""
        self.output_dir = None
        self.output_dir_var.set("(Same as source)")

    def add_files_to_queue(self, files: List[Path]):
        """Add files to the conversion queue.

        Args:
            files: List of Path objects to add to the queue.
        """
        added_count = 0
        for file_path in files:
            # Prevent duplicates
            if file_path not in self.file_queue:
                self.file_queue.append(file_path)
                self.file_listbox.insert(tk.END, file_path.name)
                added_count += 1

        if added_count > 0:
            self.log(f"Added {added_count} file(s) to queue")
        self._update_queue_display()

    def remove_files_from_queue(self, indices: List[int]):
        """Remove files at specified indices from the queue.

        Args:
            indices: List of indices to remove (in ascending order).
        """
        # Remove in reverse order to maintain correct indices
        for index in sorted(indices, reverse=True):
            if 0 <= index < len(self.file_queue):
                removed = self.file_queue.pop(index)
                self.file_listbox.delete(index)
                self.log(f"Removed: {removed.name}")
        self._update_queue_display()

    def remove_selected_files(self):
        """Remove currently selected files from the queue."""
        selected = list(self.file_listbox.curselection())
        if selected:
            self.remove_files_from_queue(selected)

    def clear_file_queue(self):
        """Remove all files from the queue."""
        self.file_queue.clear()
        self.file_listbox.delete(0, tk.END)
        self.log("Queue cleared")
        self._update_queue_display()

    def _update_queue_display(self):
        """Update the file counter display."""
        count = len(self.file_queue)
        self.file_counter_label.configure(text=f"0 of {count} files")

    def check_dependencies(self):
        """Check if FFmpeg is installed (bundled or system)."""
        available, ffmpeg, ffprobe = check_ffmpeg_available()
        if available:
            self.ffmpeg_path = ffmpeg
            self.ffprobe_path = ffprobe
            self.log(f"FFmpeg found: {ffmpeg}")
            self.log("Ready to convert.")
        else:
            self.ffmpeg_path = None
            self.ffprobe_path = None
            self.log("WARNING: FFmpeg not found!")
            self.log("Please ensure ffmpeg.exe and ffprobe.exe are in the same folder.")
            messagebox.showwarning(
                "FFmpeg Not Found",
                "FFmpeg is required but not found.\n\n"
                "Please ensure ffmpeg.exe and ffprobe.exe\n"
                "are in the same folder as this application."
            )

    def _get_resolution_value(self) -> str:
        """Convert GUI resolution display value to internal resolution key.

        Returns:
            Resolution key ('original', '1080p', '720p', '480p').
        """
        display = self.resolution.get()
        if display.startswith("1080p"):
            return "1080p"
        elif display.startswith("720p"):
            return "720p"
        elif display.startswith("480p"):
            return "480p"
        return "original"

    def _get_video_duration(self, input_path: str) -> float:
        """Get video duration in seconds using ffprobe.

        Args:
            input_path: Path to the video file.

        Returns:
            Duration in seconds, or 0.0 if duration cannot be determined.
        """
        ffprobe = self.ffprobe_path or get_ffprobe_path()
        try:
            result = subprocess.run(
                [
                    ffprobe,
                    "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    input_path
                ],
                capture_output=True,
                text=True,
                creationflags=get_subprocess_flags()
            )
            return float(result.stdout.strip())
        except (ValueError, subprocess.SubprocessError):
            return 0.0

    def _parse_ffmpeg_progress(self, line: str, total_duration: float) -> float:
        """Parse FFmpeg output line and return progress percentage.

        Args:
            line: A line of FFmpeg stderr output.
            total_duration: Total video duration in seconds.

        Returns:
            Progress percentage (0-100), or -1 if no progress info in line.
        """
        if total_duration <= 0:
            return -1

        # FFmpeg outputs: frame=  100 fps= 25 time=00:00:04.00 bitrate=...
        match = re.search(r'time=(\d+):(\d+):(\d+\.?\d*)', line)
        if match:
            hours, minutes, seconds = match.groups()
            current_time = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
            return min((current_time / total_duration) * 100, 100.0)
        return -1

    def _update_file_progress(self, percentage: float):
        """Thread-safe update of per-file progress bar.

        Args:
            percentage: Progress percentage (0-100).
        """
        self.root.after(0, lambda: self._set_file_progress(percentage))

    def _set_file_progress(self, percentage: float):
        """Update per-file progress UI elements (must be called from main thread)."""
        self.file_progress_var.set(percentage)
        self.file_progress_label.configure(text=f"Current file: {percentage:.0f}%")

    def get_video_creation_time(self, input_file: str) -> datetime:
        """Extract the creation/recording time from video metadata.

        Uses AVCHD DPM marker extraction as the primary method (for MTS files
        from Sony, Panasonic, and other AVCHD cameras), with ffprobe metadata
        extraction as a fallback.

        Args:
            input_file: Path to the input video file.

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
        ffprobe = self.ffprobe_path or get_ffprobe_path()
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
                time_str = output.split('\n')[0].strip(',')
                if time_str:
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

    def request_cancel(self):
        """Request cancellation of the current batch operation."""
        self.cancel_requested = True
        self.log("Cancel requested - will stop after current file...")
        self.cancel_btn.configure(state="disabled")

    def start_batch_conversion(self):
        """Start batch conversion of all queued files."""
        if self.is_converting:
            return

        if not self.file_queue:
            messagebox.showerror("Error", "Please add files to the queue first.")
            return

        # Validate all files exist
        missing_files = [f for f in self.file_queue if not f.exists()]
        if missing_files:
            messagebox.showerror(
                "Error",
                f"The following files were not found:\n" +
                "\n".join(str(f) for f in missing_files[:5])
            )
            return

        # Reset state
        self.is_converting = True
        self.cancel_requested = False
        self.batch_results = []
        self.batch_start_time = time.time()

        # Update UI
        self.convert_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.add_files_btn.configure(state="disabled")
        self.add_folder_btn.configure(state="disabled")
        self.remove_btn.configure(state="disabled")
        self.clear_all_btn.configure(state="disabled")

        # Start conversion in a separate thread
        thread = threading.Thread(
            target=self._run_batch_conversion,
            daemon=True
        )
        thread.start()

        # Start elapsed time updater
        self._update_elapsed_time()

    def _run_batch_conversion(self):
        """Run the batch conversion (called in a separate thread)."""
        from batch_converter import BatchConverter, BatchResult

        def progress_callback(current: int, total: int, current_file: Path):
            self.root.after(0, lambda: self.on_batch_progress(current, total, current_file))

        converter = BatchConverter(
            progress_callback=progress_callback,
            output_dir=self.output_dir
        )

        total = len(self.file_queue)
        for index, input_file in enumerate(self.file_queue, start=1):
            if self.cancel_requested:
                self.root.after(0, lambda: self.log("Batch cancelled by user"))
                break

            # Update current file display
            self.root.after(0, lambda f=input_file: self.current_file_label.configure(
                text=f"Converting: {f.name}"
            ))

            # Perform conversion
            output_file = converter._get_output_path(input_file)
            try:
                success = self._convert_single_file(str(input_file), str(output_file))
                if success:
                    result = BatchResult(
                        input_file=input_file,
                        output_file=output_file,
                        success=True,
                        error=None
                    )
                else:
                    result = BatchResult(
                        input_file=input_file,
                        output_file=None,
                        success=False,
                        error="Conversion failed"
                    )
            except Exception as e:
                result = BatchResult(
                    input_file=input_file,
                    output_file=None,
                    success=False,
                    error=str(e)
                )

            self.batch_results.append(result)
            progress_callback(index, total, input_file)

        # Conversion complete
        self.root.after(0, self._batch_complete)

    def _convert_single_file(self, input_path: str, output_path: str) -> bool:
        """Convert a single file.

        Args:
            input_path: Path to input MTS file.
            output_path: Path for output MP4 file.

        Returns:
            True if conversion succeeded, False otherwise.
        """
        try:
            # Reset per-file progress
            self._update_file_progress(0)

            # Get video duration for progress tracking
            total_duration = self._get_video_duration(input_path)

            # Get filming time
            filming_time = self.get_video_creation_time(input_path)
            self.root.after(0, lambda: self.log(
                f"Processing: {Path(input_path).name} "
                f"(filmed: {filming_time.strftime('%Y-%m-%d %H:%M')})"
            ))

            # Position mapping
            positions = {
                "top-left": "x=20:y=20",
                "top-right": "x=w-tw-20:y=20",
                "bottom-left": "x=20:y=h-th-20",
                "bottom-right": "x=w-tw-20:y=h-th-20",
            }
            pos = positions.get(self.position.get(), positions["bottom-right"])
            font_size = self.font_size.get()

            # Build drawtext filter
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
            resolution = self._get_resolution_value()
            video_filter = build_video_filter(drawtext_filter, resolution)

            ffmpeg = self.ffmpeg_path or get_ffmpeg_path()
            cmd = [
                ffmpeg,
                "-i", input_path,
                "-vf", video_filter,
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-threads", "0",  # Use all available CPU cores
                "-c:a", "aac",
                "-b:a", "192k",
                "-movflags", "+faststart",
                "-y",
                output_path
            ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=get_subprocess_flags()
            )

            for line in process.stdout:
                if "frame=" in line:
                    # Update status label with FFmpeg output
                    self.root.after(0, lambda l=line: self.status_label.configure(
                        text=l.strip()[:60]
                    ))
                    # Parse and update per-file progress
                    progress = self._parse_ffmpeg_progress(line, total_duration)
                    if progress >= 0:
                        self._update_file_progress(progress)

            process.wait()

            # Set progress to 100% on completion
            if process.returncode == 0:
                self._update_file_progress(100)

            return process.returncode == 0

        except MetadataExtractionError as e:
            self.root.after(0, lambda: self.log(f"Metadata Error: {e}"))
            raise  # Re-raise to be caught by batch handler
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Error: {e}"))
            return False

    def on_batch_progress(self, current: int, total: int, current_file: Path):
        """Handle batch progress updates.

        Args:
            current: Current file number (1-based).
            total: Total number of files.
            current_file: Path to the file just processed.
        """
        # Update progress bar
        progress_pct = (current / total) * 100
        self.batch_progress_var.set(progress_pct)

        # Update counter
        self.file_counter_label.configure(text=f"{current} of {total} files")

        # Update listbox to show completion status
        if current <= self.file_listbox.size():
            result = self.batch_results[current - 1] if current <= len(self.batch_results) else None
            if result:
                status = "✓" if result.success else "✗"
                item_text = f"{status} {current_file.name}"
                self.file_listbox.delete(current - 1)
                self.file_listbox.insert(current - 1, item_text)

    def _update_elapsed_time(self):
        """Update the elapsed time display."""
        if self.is_converting and self.batch_start_time:
            elapsed = int(time.time() - self.batch_start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.elapsed_time_label.configure(text=f"Elapsed: {minutes:02d}:{seconds:02d}")
            self.root.after(1000, self._update_elapsed_time)

    def _batch_complete(self):
        """Handle batch conversion completion."""
        self.is_converting = False

        # Reset UI
        self.convert_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.add_files_btn.configure(state="normal")
        self.add_folder_btn.configure(state="normal")
        self.remove_btn.configure(state="normal")
        self.clear_all_btn.configure(state="normal")
        self.current_file_label.configure(text="Batch complete")
        self.status_label.configure(text="")

        # Show summary
        self.show_batch_summary()

    def show_batch_summary(self):
        """Display a summary dialog of the batch conversion results."""
        if not self.batch_results:
            return

        successful = sum(1 for r in self.batch_results if r.success)
        failed = len(self.batch_results) - successful
        total = len(self.batch_results)

        # Build message
        message = f"Batch conversion complete!\n\n"
        message += f"Total: {total} files\n"
        message += f"Successful: {successful}\n"
        message += f"Failed: {failed}\n"

        if failed > 0:
            message += "\nFailed files:\n"
            for result in self.batch_results:
                if not result.success:
                    message += f"• {result.input_file.name}: {result.error}\n"

        self.log(f"Batch complete: {successful}/{total} successful")

        if failed > 0:
            messagebox.showwarning("Batch Complete", message)
        else:
            messagebox.showinfo("Batch Complete", message)


def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()

    # Try to use a modern theme on Windows
    try:
        root.tk.call("source", "azure.tcl")
        root.tk.call("set_theme", "light")
    except tk.TclError:
        pass

    app = MTSConverterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
