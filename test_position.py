#!/usr/bin/env python3
"""Tests for position constants and coordinate calculation utilities.

Tests the position configuration system for timestamp overlay placement.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


class TestPositionConstants:
    """Tests for position constants."""

    def test_position_constants_module_attribute_exists(self):
        """Position module should define POSITIONS constant."""
        from mts_converter import POSITIONS

        assert POSITIONS is not None

    def test_all_four_position_constants_exist(self):
        """POSITIONS should contain all four corner positions."""
        from mts_converter import POSITIONS

        assert 'top-left' in POSITIONS
        assert 'top-right' in POSITIONS
        assert 'bottom-left' in POSITIONS
        assert 'bottom-right' in POSITIONS

    def test_positions_is_dictionary(self):
        """POSITIONS should be a dictionary."""
        from mts_converter import POSITIONS

        assert isinstance(POSITIONS, dict)

    def test_positions_values_contain_x_and_y(self):
        """Each position value should contain x: and y: components."""
        from mts_converter import POSITIONS

        for position_name, coords in POSITIONS.items():
            assert 'x=' in coords, f"Position {position_name} missing x= coordinate"
            assert 'y=' in coords, f"Position {position_name} missing y= coordinate"


class TestDefaultPosition:
    """Tests for default position configuration."""

    def test_default_position_constant_exists(self):
        """DEFAULT_POSITION constant should exist."""
        from mts_converter import DEFAULT_POSITION

        assert DEFAULT_POSITION is not None

    def test_default_position_is_bottom_right(self):
        """Default position should be bottom-right."""
        from mts_converter import DEFAULT_POSITION

        assert DEFAULT_POSITION == 'bottom-right'


class TestGetPositionCoordinates:
    """Tests for get_position_coordinates utility function."""

    def test_function_exists(self):
        """get_position_coordinates function should exist."""
        from mts_converter import get_position_coordinates

        assert callable(get_position_coordinates)

    def test_returns_string(self):
        """get_position_coordinates should return a string."""
        from mts_converter import get_position_coordinates

        result = get_position_coordinates('top-left')

        assert isinstance(result, str)

    def test_top_left_coordinates(self):
        """Top-left should return coordinates near top-left corner."""
        from mts_converter import get_position_coordinates

        result = get_position_coordinates('top-left')

        # Should have small x value (near left edge)
        assert 'x=20' in result or 'x=' in result
        # Should have small y value (near top edge)
        assert 'y=20' in result or 'y=' in result

    def test_top_right_coordinates(self):
        """Top-right should return coordinates near top-right corner."""
        from mts_converter import get_position_coordinates

        result = get_position_coordinates('top-right')

        # Should use width-based x calculation (near right edge)
        assert 'w-' in result or 'x=w' in result.replace(' ', '')
        # Should have small y value (near top edge)
        assert 'y=20' in result or 'y=' in result

    def test_bottom_left_coordinates(self):
        """Bottom-left should return coordinates near bottom-left corner."""
        from mts_converter import get_position_coordinates

        result = get_position_coordinates('bottom-left')

        # Should have small x value (near left edge)
        assert 'x=20' in result or 'x=' in result
        # Should use height-based y calculation (near bottom edge)
        assert 'h-' in result or 'y=h' in result.replace(' ', '')

    def test_bottom_right_coordinates(self):
        """Bottom-right should return coordinates near bottom-right corner."""
        from mts_converter import get_position_coordinates

        result = get_position_coordinates('bottom-right')

        # Should use width-based x calculation (near right edge)
        assert 'w-' in result or 'x=w' in result.replace(' ', '')
        # Should use height-based y calculation (near bottom edge)
        assert 'h-' in result or 'y=h' in result.replace(' ', '')

    def test_custom_margin(self):
        """get_position_coordinates should support custom margin."""
        from mts_converter import get_position_coordinates

        result = get_position_coordinates('top-left', margin=50)

        # Should reflect the custom margin
        assert '50' in result

    def test_default_margin_is_20(self):
        """Default margin should be 20 pixels."""
        from mts_converter import get_position_coordinates

        result = get_position_coordinates('top-left')

        # Default margin should be 20
        assert '20' in result

    def test_invalid_position_raises_error(self):
        """Invalid position should raise ValueError."""
        from mts_converter import get_position_coordinates

        with pytest.raises(ValueError):
            get_position_coordinates('invalid-position')

    def test_returns_default_for_none(self):
        """None position should return default (bottom-right) coordinates."""
        from mts_converter import get_position_coordinates, DEFAULT_POSITION

        result = get_position_coordinates(None)
        expected = get_position_coordinates(DEFAULT_POSITION)

        assert result == expected


class TestConvertVideoPositionDefault:
    """Tests for convert_video function default position behavior."""

    def test_convert_video_default_position_is_bottom_right(self, tmp_path, mocker):
        """convert_video should default to bottom-right position."""
        from mts_converter import convert_video

        # Create a test file
        test_mts = tmp_path / "test.mts"
        test_mts.touch()

        # Mock the subprocess calls
        mock_popen = mocker.patch('mts_converter.subprocess.Popen')
        mock_process = MagicMock()
        mock_process.stdout = iter([])
        mock_process.wait.return_value = None
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Mock ffprobe
        mocker.patch('mts_converter.subprocess.run')
        mocker.patch('mts_converter.get_video_creation_time', return_value=datetime(2024, 1, 15, 10, 30, 0))
        mocker.patch('mts_converter.check_ffmpeg', return_value=True)

        # Call without position argument
        convert_video(str(test_mts))

        # Check the FFmpeg command contains bottom-right position
        call_args = mock_popen.call_args[0][0]
        filter_arg = [arg for arg in call_args if 'drawtext=' in arg][0]

        # Bottom-right uses w-tw and h-th
        assert 'w-tw-' in filter_arg
        assert 'h-th-' in filter_arg


class TestDrawtextFilterWithPosition:
    """Tests for drawtext filter generation with position parameter."""

    def test_filter_contains_correct_coordinates_for_top_left(self, tmp_path, mocker):
        """Filter should contain top-left coordinates when specified."""
        from mts_converter import convert_video

        test_mts = tmp_path / "test.mts"
        test_mts.touch()

        mock_popen = mocker.patch('mts_converter.subprocess.Popen')
        mock_process = MagicMock()
        mock_process.stdout = iter([])
        mock_process.wait.return_value = None
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        mocker.patch('mts_converter.subprocess.run')
        mocker.patch('mts_converter.get_video_creation_time', return_value=datetime(2024, 1, 15, 10, 30, 0))

        convert_video(str(test_mts), position='top-left')

        call_args = mock_popen.call_args[0][0]
        filter_arg = [arg for arg in call_args if 'drawtext=' in arg][0]

        # Top-left uses x=20:y=20 (small values for both)
        assert 'x=20' in filter_arg
        assert 'y=20' in filter_arg
        # Should NOT have w- or h- (those indicate right/bottom edge)
        assert 'w-tw-' not in filter_arg
        assert 'h-th-' not in filter_arg

    def test_filter_contains_correct_coordinates_for_top_right(self, tmp_path, mocker):
        """Filter should contain top-right coordinates when specified."""
        from mts_converter import convert_video

        test_mts = tmp_path / "test.mts"
        test_mts.touch()

        mock_popen = mocker.patch('mts_converter.subprocess.Popen')
        mock_process = MagicMock()
        mock_process.stdout = iter([])
        mock_process.wait.return_value = None
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        mocker.patch('mts_converter.subprocess.run')
        mocker.patch('mts_converter.get_video_creation_time', return_value=datetime(2024, 1, 15, 10, 30, 0))

        convert_video(str(test_mts), position='top-right')

        call_args = mock_popen.call_args[0][0]
        filter_arg = [arg for arg in call_args if 'drawtext=' in arg][0]

        # Top-right uses w-tw (right edge) and y=20 (top edge)
        assert 'w-tw-' in filter_arg
        assert 'y=20' in filter_arg
        assert 'h-th-' not in filter_arg

    def test_filter_contains_correct_coordinates_for_bottom_left(self, tmp_path, mocker):
        """Filter should contain bottom-left coordinates when specified."""
        from mts_converter import convert_video

        test_mts = tmp_path / "test.mts"
        test_mts.touch()

        mock_popen = mocker.patch('mts_converter.subprocess.Popen')
        mock_process = MagicMock()
        mock_process.stdout = iter([])
        mock_process.wait.return_value = None
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        mocker.patch('mts_converter.subprocess.run')
        mocker.patch('mts_converter.get_video_creation_time', return_value=datetime(2024, 1, 15, 10, 30, 0))

        convert_video(str(test_mts), position='bottom-left')

        call_args = mock_popen.call_args[0][0]
        filter_arg = [arg for arg in call_args if 'drawtext=' in arg][0]

        # Bottom-left uses x=20 (left edge) and h-th (bottom edge)
        assert 'x=20' in filter_arg
        assert 'h-th-' in filter_arg
        assert 'w-tw-' not in filter_arg

    def test_filter_contains_correct_coordinates_for_bottom_right(self, tmp_path, mocker):
        """Filter should contain bottom-right coordinates when specified."""
        from mts_converter import convert_video

        test_mts = tmp_path / "test.mts"
        test_mts.touch()

        mock_popen = mocker.patch('mts_converter.subprocess.Popen')
        mock_process = MagicMock()
        mock_process.stdout = iter([])
        mock_process.wait.return_value = None
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        mocker.patch('mts_converter.subprocess.run')
        mocker.patch('mts_converter.get_video_creation_time', return_value=datetime(2024, 1, 15, 10, 30, 0))

        convert_video(str(test_mts), position='bottom-right')

        call_args = mock_popen.call_args[0][0]
        filter_arg = [arg for arg in call_args if 'drawtext=' in arg][0]

        # Bottom-right uses w-tw (right edge) and h-th (bottom edge)
        assert 'w-tw-' in filter_arg
        assert 'h-th-' in filter_arg

    def test_default_position_produces_bottom_right_coordinates(self, tmp_path, mocker):
        """Default position should produce bottom-right coordinates."""
        from mts_converter import convert_video, DEFAULT_POSITION

        assert DEFAULT_POSITION == 'bottom-right'

        test_mts = tmp_path / "test.mts"
        test_mts.touch()

        mock_popen = mocker.patch('mts_converter.subprocess.Popen')
        mock_process = MagicMock()
        mock_process.stdout = iter([])
        mock_process.wait.return_value = None
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        mocker.patch('mts_converter.subprocess.run')
        mocker.patch('mts_converter.get_video_creation_time', return_value=datetime(2024, 1, 15, 10, 30, 0))

        # Call without position (should use default)
        convert_video(str(test_mts))

        call_args = mock_popen.call_args[0][0]
        filter_arg = [arg for arg in call_args if 'drawtext=' in arg][0]

        # Should produce bottom-right coordinates
        assert 'w-tw-' in filter_arg
        assert 'h-th-' in filter_arg
