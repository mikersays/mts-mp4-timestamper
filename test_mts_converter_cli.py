#!/usr/bin/env python3
"""Tests for mts_converter CLI argument parsing.

Tests the argument parser for batch processing support.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch


class TestCLIArgumentParser:
    """Tests for CLI argument parser."""

    def test_parse_args_function_exists(self):
        """parse_args function should exist in mts_converter module."""
        from mts_converter import parse_args

        assert parse_args is not None
        assert callable(parse_args)

    def test_parse_args_single_file(self):
        """parse_args should accept a single input file."""
        from mts_converter import parse_args

        args = parse_args(['video.mts'])

        assert args.input_paths == ['video.mts']

    def test_parse_args_multiple_files(self):
        """parse_args should accept multiple input files."""
        from mts_converter import parse_args

        args = parse_args(['video1.mts', 'video2.mts', 'video3.mts'])

        assert args.input_paths == ['video1.mts', 'video2.mts', 'video3.mts']

    def test_parse_args_output_dir_option(self):
        """parse_args should accept --output-dir option."""
        from mts_converter import parse_args

        args = parse_args(['video.mts', '--output-dir', '/tmp/output'])

        assert args.output_dir == '/tmp/output'

    def test_parse_args_output_dir_short_option(self):
        """parse_args should accept -o as short form of --output-dir."""
        from mts_converter import parse_args

        args = parse_args(['video.mts', '-o', '/tmp/output'])

        assert args.output_dir == '/tmp/output'

    def test_parse_args_output_dir_defaults_none(self):
        """parse_args output_dir should default to None."""
        from mts_converter import parse_args

        args = parse_args(['video.mts'])

        assert args.output_dir is None

    def test_parse_args_continue_on_error_flag(self):
        """parse_args should accept --continue-on-error flag."""
        from mts_converter import parse_args

        args = parse_args(['video.mts', '--continue-on-error'])

        assert args.continue_on_error is True

    def test_parse_args_continue_on_error_defaults_true(self):
        """parse_args continue_on_error should default to True."""
        from mts_converter import parse_args

        args = parse_args(['video.mts'])

        assert args.continue_on_error is True

    def test_parse_args_stop_on_error_flag(self):
        """parse_args should accept --stop-on-error to disable continue_on_error."""
        from mts_converter import parse_args

        args = parse_args(['video.mts', '--stop-on-error'])

        assert args.continue_on_error is False

    def test_parse_args_combined_options(self):
        """parse_args should handle multiple options together."""
        from mts_converter import parse_args

        args = parse_args([
            'video1.mts', 'video2.mts',
            '--output-dir', '/tmp/output',
            '--stop-on-error'
        ])

        assert args.input_paths == ['video1.mts', 'video2.mts']
        assert args.output_dir == '/tmp/output'
        assert args.continue_on_error is False

    def test_parse_args_backward_compatible_output_file(self):
        """parse_args should support legacy output.mp4 positional argument."""
        from mts_converter import parse_args

        # Legacy usage: mts_converter.py input.mts output.mp4
        args = parse_args(['input.mts', 'output.mp4'])

        # When second arg ends in .mp4, treat as legacy single-file mode
        assert args.input_paths == ['input.mts']
        assert args.output_file == 'output.mp4'

    def test_parse_args_legacy_mode_detection(self):
        """parse_args should detect legacy single-file mode."""
        from mts_converter import parse_args

        # Legacy: input.mts output.mp4
        args = parse_args(['input.mts', 'output.mp4'])
        assert args.legacy_mode is True

        # Batch mode: multiple .mts files
        args = parse_args(['video1.mts', 'video2.mts'])
        assert args.legacy_mode is False

    def test_parse_args_no_input_returns_none(self):
        """parse_args with no input should return None for interactive mode."""
        from mts_converter import parse_args

        args = parse_args([])

        assert args is None


class TestCLIBackwardCompatibility:
    """Tests for backward compatibility with existing CLI usage."""

    def test_single_file_conversion_still_works(self, tmp_path, mocker):
        """Single file usage should still work as before."""
        from mts_converter import parse_args

        args = parse_args(['input.mts'])

        # Should support single-file mode
        assert len(args.input_paths) == 1
        assert args.input_paths[0] == 'input.mts'

    def test_single_file_with_output_still_works(self):
        """Single file with explicit output should still work."""
        from mts_converter import parse_args

        args = parse_args(['input.mts', 'custom_output.mp4'])

        assert args.input_paths == ['input.mts']
        assert args.output_file == 'custom_output.mp4'
        assert args.legacy_mode is True
