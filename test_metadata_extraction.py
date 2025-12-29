#!/usr/bin/env python3
"""Tests for metadata timestamp extraction.

Tests the extraction of recording timestamps from video metadata,
ensuring file modification time is NOT used as fallback.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


class TestMetadataTimestampExtraction:
    """Tests for get_video_creation_time function."""

    def test_extracts_creation_time_from_valid_metadata(self, mocker):
        """Should extract creation_time from valid MTS metadata."""
        from mts_converter import get_video_creation_time

        # Mock ffprobe to return valid creation_time
        mock_result = MagicMock()
        mock_result.stdout = "2024-01-15T10:30:00Z\n"
        mock_result.returncode = 0
        mocker.patch('mts_converter.subprocess.run', return_value=mock_result)

        result = get_video_creation_time("test.mts")

        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30

    def test_extracts_creation_time_with_microseconds(self, mocker):
        """Should handle creation_time with microseconds."""
        from mts_converter import get_video_creation_time

        mock_result = MagicMock()
        mock_result.stdout = "2024-06-20T14:25:30.500000Z\n"
        mock_result.returncode = 0
        mocker.patch('mts_converter.subprocess.run', return_value=mock_result)

        result = get_video_creation_time("test.mts")

        assert result.year == 2024
        assert result.month == 6
        assert result.day == 20
        assert result.hour == 14
        assert result.minute == 25

    def test_handles_creation_time_without_timezone(self, mocker):
        """Should handle creation_time without Z timezone suffix."""
        from mts_converter import get_video_creation_time

        mock_result = MagicMock()
        mock_result.stdout = "2024-03-10T08:15:45\n"
        mock_result.returncode = 0
        mocker.patch('mts_converter.subprocess.run', return_value=mock_result)

        result = get_video_creation_time("test.mts")

        assert result.year == 2024
        assert result.month == 3
        assert result.day == 10


class TestMetadataExtractionFailure:
    """Tests for metadata extraction failure handling."""

    def test_raises_exception_when_metadata_missing(self, mocker):
        """Should raise MetadataExtractionError when metadata is missing."""
        from mts_converter import get_video_creation_time, MetadataExtractionError

        # Mock ffprobe to return empty output (no metadata)
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.returncode = 0
        mocker.patch('mts_converter.subprocess.run', return_value=mock_result)

        with pytest.raises(MetadataExtractionError):
            get_video_creation_time("test.mts")

    def test_raises_exception_when_ffprobe_fails(self, mocker):
        """Should raise MetadataExtractionError when ffprobe command fails."""
        from mts_converter import get_video_creation_time, MetadataExtractionError

        # Mock ffprobe to raise an exception
        mocker.patch('mts_converter.subprocess.run', side_effect=Exception("ffprobe not found"))

        with pytest.raises(MetadataExtractionError):
            get_video_creation_time("test.mts")

    def test_raises_exception_with_corrupted_metadata(self, mocker):
        """Should raise MetadataExtractionError when metadata format is invalid."""
        from mts_converter import get_video_creation_time, MetadataExtractionError

        # Mock ffprobe to return unparseable output
        mock_result = MagicMock()
        mock_result.stdout = "not-a-valid-date\n"
        mock_result.returncode = 0
        mocker.patch('mts_converter.subprocess.run', return_value=mock_result)

        with pytest.raises(MetadataExtractionError):
            get_video_creation_time("test.mts")


class TestNoFallbackToFileMtime:
    """Tests ensuring file modification time is NOT used as fallback."""

    def test_does_not_use_file_mtime_when_metadata_missing(self, mocker, tmp_path):
        """Should NOT fall back to file mtime when metadata is unavailable."""
        from mts_converter import get_video_creation_time, MetadataExtractionError

        # Create a test file
        test_file = tmp_path / "test.mts"
        test_file.touch()

        # Mock ffprobe to return empty output
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.returncode = 0
        mocker.patch('mts_converter.subprocess.run', return_value=mock_result)

        # Mock os.path.getmtime to track if it's called
        mock_getmtime = mocker.patch('mts_converter.os.path.getmtime', return_value=1700000000)

        # Should raise exception, not return mtime
        with pytest.raises(MetadataExtractionError):
            get_video_creation_time(str(test_file))

        # os.path.getmtime should NOT be called
        mock_getmtime.assert_not_called()

    def test_does_not_use_datetime_now_as_fallback(self, mocker):
        """Should NOT fall back to datetime.now() when metadata is unavailable."""
        from mts_converter import get_video_creation_time, MetadataExtractionError

        # Mock ffprobe to return empty output
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.returncode = 0
        mocker.patch('mts_converter.subprocess.run', return_value=mock_result)

        # Mock datetime.now to track if it's called
        original_datetime = datetime
        mock_now = MagicMock(return_value=datetime(2024, 12, 25, 12, 0, 0))

        # Should raise exception, not return datetime.now()
        with pytest.raises(MetadataExtractionError):
            get_video_creation_time("test.mts")


class TestMetadataExtractionErrorMessage:
    """Tests for error message content."""

    def test_error_message_indicates_metadata_unavailable(self, mocker):
        """Error message should clearly indicate metadata extraction failed."""
        from mts_converter import get_video_creation_time, MetadataExtractionError

        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.returncode = 0
        mocker.patch('mts_converter.subprocess.run', return_value=mock_result)

        with pytest.raises(MetadataExtractionError) as exc_info:
            get_video_creation_time("test.mts")

        error_msg = str(exc_info.value).lower()
        # Should mention metadata or timestamp in error message
        assert 'metadata' in error_msg or 'timestamp' in error_msg or 'creation' in error_msg

    def test_error_includes_filename(self, mocker):
        """Error message should include the filename."""
        from mts_converter import get_video_creation_time, MetadataExtractionError

        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.returncode = 0
        mocker.patch('mts_converter.subprocess.run', return_value=mock_result)

        with pytest.raises(MetadataExtractionError) as exc_info:
            get_video_creation_time("my_video.mts")

        error_msg = str(exc_info.value)
        assert "my_video.mts" in error_msg


class TestConvertVideoMetadataFailure:
    """Tests for convert_video handling metadata extraction failures."""

    def test_convert_video_returns_false_on_metadata_failure(self, tmp_path, mocker):
        """convert_video should return False when metadata extraction fails."""
        from mts_converter import convert_video, MetadataExtractionError

        test_mts = tmp_path / "test.mts"
        test_mts.touch()

        # Mock get_video_creation_time to raise MetadataExtractionError
        mocker.patch(
            'mts_converter.get_video_creation_time',
            side_effect=MetadataExtractionError("No metadata found")
        )

        result = convert_video(str(test_mts))

        assert result is False

    def test_convert_video_prints_error_message_on_metadata_failure(self, tmp_path, mocker, capsys):
        """convert_video should print error message when metadata extraction fails."""
        from mts_converter import convert_video, MetadataExtractionError

        test_mts = tmp_path / "test.mts"
        test_mts.touch()

        mocker.patch(
            'mts_converter.get_video_creation_time',
            side_effect=MetadataExtractionError("Could not extract timestamp")
        )

        convert_video(str(test_mts))

        captured = capsys.readouterr()
        # Should contain error-related text
        assert 'error' in captured.out.lower() or 'metadata' in captured.out.lower()

    def test_convert_video_does_not_raise_on_metadata_failure(self, tmp_path, mocker):
        """convert_video should NOT raise exception on metadata failure."""
        from mts_converter import convert_video, MetadataExtractionError

        test_mts = tmp_path / "test.mts"
        test_mts.touch()

        mocker.patch(
            'mts_converter.get_video_creation_time',
            side_effect=MetadataExtractionError("No metadata")
        )

        # Should not raise, just return False
        try:
            result = convert_video(str(test_mts))
            assert result is False
        except MetadataExtractionError:
            pytest.fail("convert_video should not raise MetadataExtractionError")


class TestBatchConverterMetadataFailure:
    """Tests for batch converter handling metadata extraction failures."""

    def test_batch_handles_individual_metadata_failures(self, tmp_path, mocker):
        """Batch converter should handle individual metadata failures correctly."""
        from batch_converter import BatchConverter
        from mts_converter import MetadataExtractionError

        # Create test files
        good_file = tmp_path / "good.mts"
        bad_file = tmp_path / "bad.mts"
        good_file.touch()
        bad_file.touch()

        # Mock convert_video to fail for bad_file
        def mock_convert(input_file, output_file=None):
            if 'bad' in input_file:
                raise MetadataExtractionError("No metadata in bad.mts")
            return True

        mocker.patch('batch_converter.convert_video', side_effect=mock_convert)

        converter = BatchConverter()
        results = converter.convert_batch([good_file, bad_file])

        assert len(results) == 2
        # First file should succeed
        good_result = next(r for r in results if r.input_file == good_file)
        assert good_result.success is True
        # Second file should fail with appropriate error
        bad_result = next(r for r in results if r.input_file == bad_file)
        assert bad_result.success is False
        assert 'metadata' in bad_result.error.lower() or 'bad.mts' in bad_result.error

    def test_batch_continues_after_metadata_failure(self, tmp_path, mocker):
        """Batch converter should continue processing after metadata failure."""
        from batch_converter import BatchConverter
        from mts_converter import MetadataExtractionError

        file1 = tmp_path / "first.mts"
        file2 = tmp_path / "second.mts"
        file3 = tmp_path / "third.mts"
        file1.touch()
        file2.touch()
        file3.touch()

        # Mock convert_video: first and third succeed, second fails
        call_count = [0]
        def mock_convert(input_file, output_file=None):
            call_count[0] += 1
            if 'second' in input_file:
                raise MetadataExtractionError("No metadata")
            return True

        mocker.patch('batch_converter.convert_video', side_effect=mock_convert)

        converter = BatchConverter()
        results = converter.convert_batch([file1, file2, file3])

        # All three files should have been processed
        assert call_count[0] == 3
        assert len(results) == 3
        # Check results
        assert results[0].success is True
        assert results[1].success is False
        assert results[2].success is True

    def test_batch_result_includes_metadata_error_message(self, tmp_path, mocker):
        """BatchResult should include the metadata error message."""
        from batch_converter import BatchConverter
        from mts_converter import MetadataExtractionError

        test_file = tmp_path / "test.mts"
        test_file.touch()

        error_msg = "Could not extract recording timestamp from 'test.mts'"
        mocker.patch(
            'batch_converter.convert_video',
            side_effect=MetadataExtractionError(error_msg)
        )

        converter = BatchConverter()
        results = converter.convert_batch([test_file])

        assert len(results) == 1
        assert results[0].success is False
        assert error_msg in results[0].error
