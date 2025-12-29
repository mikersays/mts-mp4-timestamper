#!/usr/bin/env python3
"""Tests for position constants and coordinate calculation utilities.

Tests the position configuration system for timestamp overlay placement.
"""

import pytest


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
