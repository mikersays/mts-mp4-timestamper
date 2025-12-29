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
