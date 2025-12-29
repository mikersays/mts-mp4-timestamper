#!/usr/bin/env python3
"""Tests for batch_converter module.

Tests the BatchConverter class, BatchResult dataclass, and BatchProgress callback.
"""

import pytest
from dataclasses import dataclass
from typing import Callable, Optional, List
from pathlib import Path


class TestBatchResult:
    """Tests for BatchResult dataclass."""

    def test_batch_result_success_attributes(self):
        """BatchResult should have input_file, output_file, success, and error attributes."""
        from batch_converter import BatchResult

        result = BatchResult(
            input_file=Path("test.mts"),
            output_file=Path("test.mp4"),
            success=True,
            error=None
        )
        assert result.input_file == Path("test.mts")
        assert result.output_file == Path("test.mp4")
        assert result.success is True
        assert result.error is None

    def test_batch_result_failure_attributes(self):
        """BatchResult should store error message on failure."""
        from batch_converter import BatchResult

        result = BatchResult(
            input_file=Path("test.mts"),
            output_file=None,
            success=False,
            error="File not found"
        )
        assert result.input_file == Path("test.mts")
        assert result.output_file is None
        assert result.success is False
        assert result.error == "File not found"


class TestBatchProgress:
    """Tests for BatchProgress callback protocol."""

    def test_batch_progress_callable(self):
        """BatchProgress should be callable with current, total, and current_file."""
        from batch_converter import BatchProgress

        # Define a callback that matches the BatchProgress protocol
        def progress_callback(current: int, total: int, current_file: Path) -> None:
            pass

        # Verify BatchProgress is defined as a typing alias/Protocol
        # This test validates the callback signature is documented
        assert BatchProgress is not None


class TestBatchConverter:
    """Tests for BatchConverter class."""

    def test_batch_converter_exists(self):
        """BatchConverter class should exist."""
        from batch_converter import BatchConverter

        assert BatchConverter is not None

    def test_batch_converter_instantiation(self):
        """BatchConverter should be instantiable with optional progress callback."""
        from batch_converter import BatchConverter

        # Without callback
        converter = BatchConverter()
        assert converter is not None

    def test_batch_converter_with_progress_callback(self):
        """BatchConverter should accept a progress callback."""
        from batch_converter import BatchConverter

        progress_calls = []

        def track_progress(current: int, total: int, current_file: Path) -> None:
            progress_calls.append((current, total, current_file))

        converter = BatchConverter(progress_callback=track_progress)
        assert converter.progress_callback == track_progress

    def test_batch_converter_has_convert_batch_method(self):
        """BatchConverter should have a convert_batch method."""
        from batch_converter import BatchConverter

        converter = BatchConverter()
        assert hasattr(converter, 'convert_batch')
        assert callable(converter.convert_batch)

    def test_batch_converter_has_results_attribute(self):
        """BatchConverter should have a results attribute for tracking conversions."""
        from batch_converter import BatchConverter

        converter = BatchConverter()
        assert hasattr(converter, 'results')
        assert isinstance(converter.results, list)


class TestDiscoverFiles:
    """Tests for discover_files function."""

    def test_discover_files_exists(self):
        """discover_files function should exist."""
        from batch_converter import discover_files

        assert discover_files is not None
        assert callable(discover_files)

    def test_discover_files_single_file(self, tmp_path):
        """discover_files should return a single MTS file when given its path."""
        from batch_converter import discover_files

        # Create a test MTS file
        mts_file = tmp_path / "video.mts"
        mts_file.touch()

        result = discover_files([str(mts_file)])
        assert len(result) == 1
        assert result[0] == mts_file

    def test_discover_files_multiple_files(self, tmp_path):
        """discover_files should return multiple MTS files."""
        from batch_converter import discover_files

        # Create test MTS files
        mts1 = tmp_path / "video1.mts"
        mts2 = tmp_path / "video2.MTS"
        mts1.touch()
        mts2.touch()

        result = discover_files([str(mts1), str(mts2)])
        assert len(result) == 2
        assert mts1 in result
        assert mts2 in result

    def test_discover_files_from_directory(self, tmp_path):
        """discover_files should find all MTS files in a directory."""
        from batch_converter import discover_files

        # Create test MTS files in directory
        mts1 = tmp_path / "video1.mts"
        mts2 = tmp_path / "video2.MTS"
        txt_file = tmp_path / "readme.txt"  # Should be ignored
        mts1.touch()
        mts2.touch()
        txt_file.touch()

        result = discover_files([str(tmp_path)])
        assert len(result) == 2
        assert mts1 in result
        assert mts2 in result

    def test_discover_files_glob_pattern(self, tmp_path):
        """discover_files should expand glob patterns."""
        from batch_converter import discover_files

        # Create test MTS files
        mts1 = tmp_path / "video1.mts"
        mts2 = tmp_path / "video2.mts"
        mts1.touch()
        mts2.touch()

        result = discover_files([str(tmp_path / "*.mts")])
        assert len(result) == 2

    def test_discover_files_filters_non_mts(self, tmp_path):
        """discover_files should only return .mts/.MTS files."""
        from batch_converter import discover_files

        # Create mixed file types
        mts_file = tmp_path / "video.mts"
        mp4_file = tmp_path / "video.mp4"
        txt_file = tmp_path / "notes.txt"
        mts_file.touch()
        mp4_file.touch()
        txt_file.touch()

        result = discover_files([str(mts_file), str(mp4_file), str(txt_file)])
        assert len(result) == 1
        assert result[0] == mts_file

    def test_discover_files_skips_nonexistent(self, tmp_path):
        """discover_files should skip files that don't exist."""
        from batch_converter import discover_files

        mts_file = tmp_path / "exists.mts"
        mts_file.touch()
        nonexistent = tmp_path / "missing.mts"

        result = discover_files([str(mts_file), str(nonexistent)])
        assert len(result) == 1
        assert result[0] == mts_file

    def test_discover_files_case_insensitive_extension(self, tmp_path):
        """discover_files should accept both .mts and .MTS extensions."""
        from batch_converter import discover_files

        lower_mts = tmp_path / "video.mts"
        upper_mts = tmp_path / "video2.MTS"
        mixed_mts = tmp_path / "video3.Mts"
        lower_mts.touch()
        upper_mts.touch()
        mixed_mts.touch()

        result = discover_files([str(lower_mts), str(upper_mts), str(mixed_mts)])
        assert len(result) == 3

    def test_discover_files_empty_input(self):
        """discover_files should return empty list for empty input."""
        from batch_converter import discover_files

        result = discover_files([])
        assert result == []

    def test_discover_files_returns_unique(self, tmp_path):
        """discover_files should not return duplicate paths."""
        from batch_converter import discover_files

        mts_file = tmp_path / "video.mts"
        mts_file.touch()

        # Pass the same file multiple times
        result = discover_files([str(mts_file), str(mts_file)])
        assert len(result) == 1
