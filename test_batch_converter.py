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


class TestConvertBatch:
    """Tests for BatchConverter.convert_batch method."""

    def test_convert_batch_empty_list(self):
        """convert_batch with empty list should return empty results."""
        from batch_converter import BatchConverter

        converter = BatchConverter()
        results = converter.convert_batch([])

        assert results == []
        assert converter.results == []

    def test_convert_batch_calls_convert_for_each_file(self, tmp_path, mocker):
        """convert_batch should call convert_video for each file."""
        from batch_converter import BatchConverter
        from pathlib import Path

        # Create test files
        mts1 = tmp_path / "video1.mts"
        mts2 = tmp_path / "video2.mts"
        mts1.touch()
        mts2.touch()

        # Mock convert_video to return True
        mock_convert = mocker.patch(
            'batch_converter.convert_video',
            return_value=True
        )

        converter = BatchConverter()
        converter.convert_batch([mts1, mts2])

        assert mock_convert.call_count == 2

    def test_convert_batch_returns_results_for_each_file(self, tmp_path, mocker):
        """convert_batch should return a BatchResult for each input file."""
        from batch_converter import BatchConverter, BatchResult
        from pathlib import Path

        mts1 = tmp_path / "video1.mts"
        mts2 = tmp_path / "video2.mts"
        mts1.touch()
        mts2.touch()

        # Mock convert_video
        mocker.patch('batch_converter.convert_video', return_value=True)

        converter = BatchConverter()
        results = converter.convert_batch([mts1, mts2])

        assert len(results) == 2
        assert all(isinstance(r, BatchResult) for r in results)

    def test_convert_batch_tracks_success(self, tmp_path, mocker):
        """convert_batch should record success for successful conversions."""
        from batch_converter import BatchConverter
        from pathlib import Path

        mts_file = tmp_path / "video.mts"
        mts_file.touch()

        mocker.patch('batch_converter.convert_video', return_value=True)

        converter = BatchConverter()
        results = converter.convert_batch([mts_file])

        assert len(results) == 1
        assert results[0].success is True
        assert results[0].error is None

    def test_convert_batch_tracks_failure(self, tmp_path, mocker):
        """convert_batch should record failure for failed conversions."""
        from batch_converter import BatchConverter
        from pathlib import Path

        mts_file = tmp_path / "video.mts"
        mts_file.touch()

        mocker.patch('batch_converter.convert_video', return_value=False)

        converter = BatchConverter()
        results = converter.convert_batch([mts_file])

        assert len(results) == 1
        assert results[0].success is False
        assert results[0].error is not None

    def test_convert_batch_updates_results_attribute(self, tmp_path, mocker):
        """convert_batch should update the converter's results attribute."""
        from batch_converter import BatchConverter
        from pathlib import Path

        mts_file = tmp_path / "video.mts"
        mts_file.touch()

        mocker.patch('batch_converter.convert_video', return_value=True)

        converter = BatchConverter()
        results = converter.convert_batch([mts_file])

        assert converter.results == results
        assert len(converter.results) == 1

    def test_convert_batch_invokes_progress_callback(self, tmp_path, mocker):
        """convert_batch should invoke progress callback after each file."""
        from batch_converter import BatchConverter
        from pathlib import Path

        mts1 = tmp_path / "video1.mts"
        mts2 = tmp_path / "video2.mts"
        mts1.touch()
        mts2.touch()

        mocker.patch('batch_converter.convert_video', return_value=True)

        progress_calls = []

        def track_progress(current: int, total: int, current_file: Path) -> None:
            progress_calls.append((current, total, current_file))

        converter = BatchConverter(progress_callback=track_progress)
        converter.convert_batch([mts1, mts2])

        assert len(progress_calls) == 2
        assert progress_calls[0] == (1, 2, mts1)
        assert progress_calls[1] == (2, 2, mts2)

    def test_convert_batch_continues_after_failure(self, tmp_path, mocker):
        """convert_batch should continue processing after a failure."""
        from batch_converter import BatchConverter
        from pathlib import Path

        mts1 = tmp_path / "video1.mts"
        mts2 = tmp_path / "video2.mts"
        mts3 = tmp_path / "video3.mts"
        mts1.touch()
        mts2.touch()
        mts3.touch()

        # First and third succeed, second fails
        mocker.patch(
            'batch_converter.convert_video',
            side_effect=[True, False, True]
        )

        converter = BatchConverter()
        results = converter.convert_batch([mts1, mts2, mts3])

        assert len(results) == 3
        assert results[0].success is True
        assert results[1].success is False
        assert results[2].success is True

    def test_convert_batch_sets_output_file_on_success(self, tmp_path, mocker):
        """convert_batch should set output_file path on successful conversion."""
        from batch_converter import BatchConverter
        from pathlib import Path

        mts_file = tmp_path / "video.mts"
        mts_file.touch()

        mocker.patch('batch_converter.convert_video', return_value=True)

        converter = BatchConverter()
        results = converter.convert_batch([mts_file])

        assert results[0].output_file is not None
        assert results[0].output_file.suffix == '.mp4'

    def test_convert_batch_handles_exception(self, tmp_path, mocker):
        """convert_batch should handle exceptions during conversion."""
        from batch_converter import BatchConverter
        from pathlib import Path

        mts_file = tmp_path / "video.mts"
        mts_file.touch()

        mocker.patch(
            'batch_converter.convert_video',
            side_effect=Exception("FFmpeg crashed")
        )

        converter = BatchConverter()
        results = converter.convert_batch([mts_file])

        assert len(results) == 1
        assert results[0].success is False
        assert "FFmpeg crashed" in results[0].error


class TestOutputDirectory:
    """Tests for output directory support in BatchConverter."""

    def test_batch_converter_accepts_output_dir(self):
        """BatchConverter should accept an output_dir parameter."""
        from batch_converter import BatchConverter
        from pathlib import Path

        output_dir = Path("/tmp/output")
        converter = BatchConverter(output_dir=output_dir)

        assert converter.output_dir == output_dir

    def test_batch_converter_output_dir_defaults_none(self):
        """BatchConverter output_dir should default to None."""
        from batch_converter import BatchConverter

        converter = BatchConverter()
        assert converter.output_dir is None

    def test_convert_batch_uses_output_dir(self, tmp_path, mocker):
        """convert_batch should save to output_dir when specified."""
        from batch_converter import BatchConverter
        from pathlib import Path

        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        mts_file = input_dir / "video.mts"
        mts_file.touch()

        mock_convert = mocker.patch('batch_converter.convert_video', return_value=True)

        converter = BatchConverter(output_dir=output_dir)
        results = converter.convert_batch([mts_file])

        # Check that convert_video was called with output in output_dir
        call_args = mock_convert.call_args[0]
        output_path = Path(call_args[1])
        assert output_path.parent == output_dir
        assert output_path.name == "video.mp4"

    def test_convert_batch_preserves_filename_in_output_dir(self, tmp_path, mocker):
        """convert_batch should preserve original filename in output_dir."""
        from batch_converter import BatchConverter
        from pathlib import Path

        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        mts_file = input_dir / "my_vacation_2024.mts"
        mts_file.touch()

        mocker.patch('batch_converter.convert_video', return_value=True)

        converter = BatchConverter(output_dir=output_dir)
        results = converter.convert_batch([mts_file])

        assert results[0].output_file == output_dir / "my_vacation_2024.mp4"

    def test_convert_batch_handles_filename_conflict(self, tmp_path, mocker):
        """convert_batch should handle filename conflicts with numeric suffix."""
        from batch_converter import BatchConverter
        from pathlib import Path

        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        # Create existing file in output directory
        existing_output = output_dir / "video.mp4"
        existing_output.touch()

        mts_file = input_dir / "video.mts"
        mts_file.touch()

        mock_convert = mocker.patch('batch_converter.convert_video', return_value=True)

        converter = BatchConverter(output_dir=output_dir)
        results = converter.convert_batch([mts_file])

        # Should have used video_1.mp4 instead
        call_args = mock_convert.call_args[0]
        output_path = Path(call_args[1])
        assert output_path.name == "video_1.mp4"

    def test_convert_batch_handles_multiple_conflicts(self, tmp_path, mocker):
        """convert_batch should increment suffix for multiple conflicts."""
        from batch_converter import BatchConverter
        from pathlib import Path

        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        # Create multiple existing files
        (output_dir / "video.mp4").touch()
        (output_dir / "video_1.mp4").touch()
        (output_dir / "video_2.mp4").touch()

        mts_file = input_dir / "video.mts"
        mts_file.touch()

        mock_convert = mocker.patch('batch_converter.convert_video', return_value=True)

        converter = BatchConverter(output_dir=output_dir)
        results = converter.convert_batch([mts_file])

        call_args = mock_convert.call_args[0]
        output_path = Path(call_args[1])
        assert output_path.name == "video_3.mp4"

    def test_convert_batch_without_output_dir_uses_source_dir(self, tmp_path, mocker):
        """convert_batch without output_dir should save next to source file."""
        from batch_converter import BatchConverter
        from pathlib import Path

        mts_file = tmp_path / "video.mts"
        mts_file.touch()

        mock_convert = mocker.patch('batch_converter.convert_video', return_value=True)

        converter = BatchConverter()  # No output_dir
        results = converter.convert_batch([mts_file])

        call_args = mock_convert.call_args[0]
        output_path = Path(call_args[1])
        assert output_path.parent == tmp_path
        assert output_path.name == "video.mp4"
