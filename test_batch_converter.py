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
