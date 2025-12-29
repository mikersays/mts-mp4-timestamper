#!/usr/bin/env python3
"""
Batch converter module for processing multiple MTS files.

Provides BatchConverter class for batch conversion operations,
BatchResult dataclass for tracking conversion results, and
BatchProgress callback type for progress updates.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional


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
        results: List of BatchResult objects from conversions.
    """

    def __init__(self, progress_callback: Optional[BatchProgress] = None):
        """Initialize BatchConverter.

        Args:
            progress_callback: Optional callback for progress updates.
                               Called with (current, total, current_file).
        """
        self.progress_callback = progress_callback
        self.results: List[BatchResult] = []

    def convert_batch(self, files: List[Path]) -> List[BatchResult]:
        """Convert a batch of MTS files to MP4 format.

        Args:
            files: List of paths to MTS files to convert.

        Returns:
            List of BatchResult objects, one per input file.
        """
        # Implementation will be added in Task 1.3
        return self.results
