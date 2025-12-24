#!/usr/bin/env python3
"""
MTS to MP4 Video Converter with Dynamic Timestamp Overlay - GUI Version

A simple Windows GUI for converting .MTS videos to .MP4 with timestamp overlay.
"""

import subprocess
import sys
import os
import threading
from datetime import datetime
from pathlib import Path

from ffmpeg_utils import (
    get_ffmpeg_path,
    get_ffprobe_path,
    check_ffmpeg_available,
    get_subprocess_flags
)

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
except ImportError:
    print("Error: tkinter is required for the GUI version.")
    print("Please use the command-line version: mts_converter.py")
    sys.exit(1)


class MTSConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MTS to MP4 Converter with Timestamp")
        self.root.geometry("600x450")
        self.root.resizable(True, True)

        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.position = tk.StringVar(value="top-left")
        self.font_size = tk.IntVar(value=24)
        self.is_converting = False

        self.create_widgets()
        self.check_dependencies()

    def create_widgets(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="MTS to MP4 Converter",
            font=("Segoe UI", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        subtitle = ttk.Label(
            main_frame,
            text="Converts MTS videos with dynamic timestamp overlay",
            font=("Segoe UI", 9)
        )
        subtitle.grid(row=1, column=0, columnspan=3, pady=(0, 15))

        # Input file selection
        ttk.Label(main_frame, text="Input File (.MTS):").grid(
            row=2, column=0, sticky="w", pady=5
        )
        input_entry = ttk.Entry(main_frame, textvariable=self.input_file, width=50)
        input_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_input).grid(
            row=2, column=2, pady=5
        )

        # Output file selection
        ttk.Label(main_frame, text="Output File (.MP4):").grid(
            row=3, column=0, sticky="w", pady=5
        )
        output_entry = ttk.Entry(main_frame, textvariable=self.output_file, width=50)
        output_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_output).grid(
            row=3, column=2, pady=5
        )

        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Timestamp Options", padding="10")
        options_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=15)
        options_frame.columnconfigure(1, weight=1)

        # Position selection
        ttk.Label(options_frame, text="Position:").grid(row=0, column=0, sticky="w", pady=5)
        position_combo = ttk.Combobox(
            options_frame,
            textvariable=self.position,
            values=["top-left", "top-right", "bottom-left", "bottom-right", "center"],
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

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            mode='indeterminate'
        )
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky="ew", pady=10)

        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready", font=("Segoe UI", 9))
        self.status_label.grid(row=6, column=0, columnspan=3, pady=5)

        # Convert button
        self.convert_btn = ttk.Button(
            main_frame,
            text="Convert Video",
            command=self.start_conversion,
            style="Accent.TButton"
        )
        self.convert_btn.grid(row=7, column=0, columnspan=3, pady=15, ipadx=20, ipady=5)

        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.grid(row=8, column=0, columnspan=3, sticky="nsew", pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(8, weight=1)

        self.log_text = tk.Text(log_frame, height=8, width=60, state="disabled")
        self.log_text.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=scrollbar.set)

    def log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def browse_input(self):
        filename = filedialog.askopenfilename(
            title="Select MTS Video File",
            filetypes=[("MTS Files", "*.mts *.MTS"), ("All Files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            # Auto-set output filename
            output = Path(filename).with_suffix('.mp4')
            self.output_file.set(str(output))

    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="Save MP4 File As",
            defaultextension=".mp4",
            filetypes=[("MP4 Files", "*.mp4"), ("All Files", "*.*")]
        )
        if filename:
            self.output_file.set(filename)

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

    def get_video_creation_time(self, input_file):
        """Extract the creation/recording time from video metadata."""
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
        except Exception as e:
            self.log(f"Warning: Could not extract metadata: {e}")

        # Fallback to file modification time
        try:
            mtime = os.path.getmtime(input_file)
            return datetime.fromtimestamp(mtime)
        except Exception:
            return datetime.now()

    def start_conversion(self):
        if self.is_converting:
            return

        input_path = self.input_file.get().strip()
        output_path = self.output_file.get().strip()

        if not input_path:
            messagebox.showerror("Error", "Please select an input file.")
            return

        if not os.path.exists(input_path):
            messagebox.showerror("Error", f"Input file not found:\n{input_path}")
            return

        if not output_path:
            output_path = str(Path(input_path).with_suffix('.mp4'))
            self.output_file.set(output_path)

        # Start conversion in a separate thread
        self.is_converting = True
        self.convert_btn.configure(state="disabled")
        self.progress_bar.start(10)
        self.status_label.configure(text="Converting...")

        thread = threading.Thread(
            target=self.convert_video,
            args=(input_path, output_path),
            daemon=True
        )
        thread.start()

    def convert_video(self, input_path, output_path):
        try:
            # Get filming time
            filming_time = self.get_video_creation_time(input_path)
            self.root.after(0, lambda: self.log(
                f"Filming time: {filming_time.strftime('%Y-%m-%d %H:%M:%S')}"
            ))

            # Position mapping
            positions = {
                "top-left": "x=20:y=20",
                "top-right": "x=w-tw-20:y=20",
                "bottom-left": "x=20:y=h-th-20",
                "bottom-right": "x=w-tw-20:y=h-th-20",
                "center": "x=(w-tw)/2:y=(h-th)/2"
            }
            pos = positions.get(self.position.get(), positions["top-left"])
            font_size = self.font_size.get()

            # Build drawtext filter
            drawtext_filter = (
                f"drawtext="
                f"text='%{{pts\\:localtime\\:{int(filming_time.timestamp())}\\:%Y-%m-%d %H\\\\\\:%M}}':"
                f"fontsize={font_size}:"
                f"fontcolor=white:"
                f"borderw=2:"
                f"bordercolor=black:"
                f"{pos}"
            )

            ffmpeg = self.ffmpeg_path or get_ffmpeg_path()
            cmd = [
                ffmpeg,
                "-i", input_path,
                "-vf", drawtext_filter,
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "192k",
                "-movflags", "+faststart",
                "-y",
                output_path
            ]

            self.root.after(0, lambda: self.log("Starting FFmpeg conversion..."))

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=get_subprocess_flags()
            )

            for line in process.stdout:
                if "frame=" in line:
                    self.root.after(0, lambda l=line: self.status_label.configure(
                        text=l.strip()[:60]
                    ))

            process.wait()

            if process.returncode == 0:
                self.root.after(0, lambda: self.conversion_complete(True, output_path))
            else:
                self.root.after(0, lambda: self.conversion_complete(False, "FFmpeg error"))

        except Exception as e:
            self.root.after(0, lambda: self.conversion_complete(False, str(e)))

    def conversion_complete(self, success, message):
        self.is_converting = False
        self.progress_bar.stop()
        self.convert_btn.configure(state="normal")

        if success:
            self.status_label.configure(text="Conversion complete!")
            self.log(f"Success! Output saved to: {message}")
            messagebox.showinfo("Success", f"Video converted successfully!\n\n{message}")
        else:
            self.status_label.configure(text="Conversion failed")
            self.log(f"Error: {message}")
            messagebox.showerror("Error", f"Conversion failed:\n{message}")


def main():
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
