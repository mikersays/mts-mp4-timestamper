#!/usr/bin/env python3
"""
Batch converter module for processing multiple MTS files.

Provides BatchConverter class for batch conversion operations,
BatchResult dataclass for tracking conversion results, and
BatchProgress callback type for progress updates.
"""

from dataclasses import dataclass
from glob import glob
from pathlib import Path
from typing import Callable, List, Optional

from mts_converter import convert_video, DEFAULT_POSITION


# Type alias for progress callback
# Signature: callback(current: int, total: int, current_file: Path) -> None
BatchProgress = Callable[[int, int, Path], None]


@dataclass
class BatchResult:
    """Result of a single file conversion within a batch.

    Attributes:
        input_file: Path to the source MTS file.
        output_file: Path to the output MP4 file, or None if conversion failed.
        success: Whether the conversion succeeded.
        error: Error message if conversion failed, None otherwise.
    """
    input_file: Path
    output_file: Optional[Path]
    success: bool
    error: Optional[str]


class BatchConverter:
    """Converts multiple MTS files to MP4 format with progress tracking.

    Attributes:
        progress_callback: Optional callback invoked after each file conversion.
        output_dir: Optional directory for output files.
        position: Timestamp overlay position.
        results: List of BatchResult objects from conversions.
    """

    def __init__(
        self,
        progress_callback: Optional[BatchProgress] = None,
        output_dir: Optional[Path] = None,
        position: Optional[str] = None
    ):
        """Initialize BatchConverter.

        Args:
            progress_callback: Optional callback for progress updates.
                               Called with (current, total, current_file).
            output_dir: Optional directory for output files. If None,
                        output files are saved next to input files.
            position: Timestamp position (default: DEFAULT_POSITION).
        """
        self.progress_callback = progress_callback
        self.output_dir = output_dir
        self.position = position if position is not None else DEFAULT_POSITION
        self.results: List[BatchResult] = []

    def _get_output_path(self, input_file: Path) -> Path:
        """Determine the output path for a given input file.

        Args:
            input_file: Path to the input MTS file.

        Returns:
            Path for the output MP4 file, handling conflicts if needed.
        """
        if self.output_dir is None:
            return input_file.with_suffix('.mp4')

        # Use output_dir with original filename
        base_output = self.output_dir / input_file.with_suffix('.mp4').name

        # Handle filename conflicts
        if not base_output.exists():
            return base_output

        # Find a unique filename with numeric suffix
        stem = input_file.stem
        counter = 1
        while True:
            candidate = self.output_dir / f"{stem}_{counter}.mp4"
            if not candidate.exists():
                return candidate
            counter += 1

    def convert_batch(self, files: List[Path]) -> List[BatchResult]:
        """Convert a batch of MTS files to MP4 format.

        Args:
            files: List of paths to MTS files to convert.

        Returns:
            List of BatchResult objects, one per input file.
        """
        self.results = []
        total = len(files)

        for index, input_file in enumerate(files, start=1):
            output_file = self._get_output_path(input_file)

            try:
                success = convert_video(
                    str(input_file),
                    str(output_file),
                    position=self.position
                )

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

            self.results.append(result)

            if self.progress_callback:
                self.progress_callback(index, total, input_file)

        return self.results


def discover_files(paths: List[str]) -> List[Path]:
    """Discover MTS files from a list of paths, directories, or glob patterns.

    Args:
        paths: List of file paths, directory paths, or glob patterns.

    Returns:
        List of Path objects pointing to existing MTS files.
        Files are deduplicated and only include .mts/.MTS files.
    """
    discovered: set[Path] = set()

    for path_str in paths:
        path = Path(path_str)

        if path.is_file():
            # Direct file path
            if _is_mts_file(path):
                discovered.add(path.resolve())
        elif path.is_dir():
            # Directory - find all MTS files within
            for item in path.iterdir():
                if item.is_file() and _is_mts_file(item):
                    discovered.add(item.resolve())
        else:
            # Try as glob pattern
            for match in glob(path_str):
                match_path = Path(match)
                if match_path.is_file() and _is_mts_file(match_path):
                    discovered.add(match_path.resolve())

    return list(discovered)


def _is_mts_file(path: Path) -> bool:
    """Check if a path is an MTS file (case-insensitive extension).

    Args:
        path: Path to check.

    Returns:
        True if the file has a .mts extension (any case), False otherwise.
    """
    return path.suffix.lower() == '.mts'
