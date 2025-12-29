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


class TestCLIPositionArgument:
    """Tests for CLI --position argument parsing."""

    def test_parse_args_position_flag_exists(self):
        """parse_args should accept --position flag."""
        from mts_converter import parse_args

        args = parse_args(['video.mts', '--position', 'top-left'])

        assert hasattr(args, 'position')

    def test_parse_args_position_accepts_top_left(self):
        """parse_args should accept top-left position."""
        from mts_converter import parse_args

        args = parse_args(['video.mts', '--position', 'top-left'])

        assert args.position == 'top-left'

    def test_parse_args_position_accepts_top_right(self):
        """parse_args should accept top-right position."""
        from mts_converter import parse_args

        args = parse_args(['video.mts', '--position', 'top-right'])

        assert args.position == 'top-right'

    def test_parse_args_position_accepts_bottom_left(self):
        """parse_args should accept bottom-left position."""
        from mts_converter import parse_args

        args = parse_args(['video.mts', '--position', 'bottom-left'])

        assert args.position == 'bottom-left'

    def test_parse_args_position_accepts_bottom_right(self):
        """parse_args should accept bottom-right position."""
        from mts_converter import parse_args

        args = parse_args(['video.mts', '--position', 'bottom-right'])

        assert args.position == 'bottom-right'

    def test_parse_args_position_defaults_to_bottom_right(self):
        """parse_args position should default to bottom-right."""
        from mts_converter import parse_args, DEFAULT_POSITION

        args = parse_args(['video.mts'])

        assert args.position == DEFAULT_POSITION
        assert args.position == 'bottom-right'

    def test_parse_args_position_short_flag(self):
        """parse_args should accept -p as short form of --position."""
        from mts_converter import parse_args

        args = parse_args(['video.mts', '-p', 'top-left'])

        assert args.position == 'top-left'

    def test_parse_args_position_invalid_value_raises_error(self):
        """parse_args should reject invalid position values."""
        from mts_converter import parse_args
        import sys

        # argparse exits with SystemExit on invalid choices
        with pytest.raises(SystemExit):
            parse_args(['video.mts', '--position', 'invalid-position'])

    def test_parse_args_position_with_other_options(self):
        """parse_args should handle position with other options."""
        from mts_converter import parse_args

        args = parse_args([
            'video1.mts', 'video2.mts',
            '--position', 'top-right',
            '--output-dir', '/tmp/output'
        ])

        assert args.position == 'top-right'
        assert args.output_dir == '/tmp/output'
        assert args.input_paths == ['video1.mts', 'video2.mts']

    def test_parse_args_legacy_mode_has_position(self):
        """Legacy mode should also have position attribute."""
        from mts_converter import parse_args

        args = parse_args(['input.mts', 'output.mp4'])

        # Legacy mode should still have position (defaulted)
        assert hasattr(args, 'position')


class TestCLIPositionIntegration:
    """Tests for CLI position integration with conversion."""

    def test_run_cli_passes_position_to_convert_video_legacy(self, tmp_path, mocker):
        """run_cli should pass position to convert_video in legacy mode."""
        from mts_converter import run_cli

        mts_file = tmp_path / "video.mts"
        mts_file.touch()

        mock_convert = mocker.patch('mts_converter.convert_video', return_value=True)
        mocker.patch('mts_converter.check_ffmpeg', return_value=True)

        run_cli([str(mts_file), str(tmp_path / "output.mp4")])

        # Should call convert_video with position parameter (defaulted)
        call_kwargs = mock_convert.call_args
        # Position should be passed as keyword argument or positional
        assert 'position' in str(call_kwargs) or mock_convert.call_args[1].get('position') == 'bottom-right'

    def test_run_cli_passes_explicit_position_batch_single_file(self, tmp_path, mocker):
        """run_cli should pass explicit position for single file in batch mode."""
        from mts_converter import run_cli

        mts_file = tmp_path / "video.mts"
        mts_file.touch()

        # Must mock in batch_converter module since that's where it's imported
        mock_convert = mocker.patch('batch_converter.convert_video', return_value=True)
        mocker.patch('mts_converter.check_ffmpeg', return_value=True)
        mocker.patch('batch_converter.discover_files', return_value=[mts_file])

        run_cli([str(mts_file), '--position', 'top-left'])

        mock_convert.assert_called()
        # Verify position was passed
        call_kwargs = mock_convert.call_args[1]
        assert call_kwargs.get('position') == 'top-left'

    def test_run_cli_passes_position_to_batch_converter(self, tmp_path, mocker):
        """run_cli should pass position to BatchConverter."""
        from mts_converter import run_cli

        mts1 = tmp_path / "video1.mts"
        mts2 = tmp_path / "video2.mts"
        mts1.touch()
        mts2.touch()

        mocker.patch('batch_converter.discover_files', return_value=[mts1, mts2])
        mocker.patch('mts_converter.check_ffmpeg', return_value=True)

        mock_batch = mocker.patch('batch_converter.BatchConverter')
        mock_instance = mock_batch.return_value
        mock_instance.convert_batch.return_value = []

        run_cli([str(mts1), str(mts2), '--position', 'top-right'])

        # Check that BatchConverter was created with position
        call_kwargs = mock_batch.call_args[1]
        assert call_kwargs.get('position') == 'top-right'

    def test_batch_converter_passes_position_to_convert_video(self, tmp_path, mocker):
        """BatchConverter should pass position to convert_video for each file."""
        from batch_converter import BatchConverter

        mts_file = tmp_path / "video.mts"
        mts_file.touch()

        mock_convert = mocker.patch('batch_converter.convert_video', return_value=True)

        converter = BatchConverter(position='top-left')
        converter.convert_batch([mts_file])

        # convert_video should be called with position='top-left'
        call_kwargs = mock_convert.call_args[1] if mock_convert.call_args[1] else {}
        assert call_kwargs.get('position') == 'top-left'

    def test_batch_converter_uses_default_position_when_not_specified(self, tmp_path, mocker):
        """BatchConverter should use default position when not specified."""
        from batch_converter import BatchConverter
        from mts_converter import DEFAULT_POSITION

        mts_file = tmp_path / "video.mts"
        mts_file.touch()

        mock_convert = mocker.patch('batch_converter.convert_video', return_value=True)

        converter = BatchConverter()  # No position specified
        converter.convert_batch([mts_file])

        # convert_video should be called with default position
        call_kwargs = mock_convert.call_args[1] if mock_convert.call_args[1] else {}
        assert call_kwargs.get('position') == DEFAULT_POSITION


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


class TestCLIBatchIntegration:
    """Tests for batch converter integration with CLI."""

    def test_run_cli_function_exists(self):
        """run_cli function should exist in mts_converter module."""
        from mts_converter import run_cli

        assert run_cli is not None
        assert callable(run_cli)

    def test_run_cli_uses_batch_converter_for_multiple_files(self, tmp_path, mocker):
        """run_cli should use BatchConverter when multiple files are provided."""
        from mts_converter import run_cli

        # Create test files
        mts1 = tmp_path / "video1.mts"
        mts2 = tmp_path / "video2.mts"
        mts1.touch()
        mts2.touch()

        # Mock the batch converter in the batch_converter module
        mock_batch = mocker.patch('batch_converter.BatchConverter')
        mock_instance = mock_batch.return_value
        mock_instance.convert_batch.return_value = []

        # Mock discover_files in the batch_converter module
        mocker.patch('batch_converter.discover_files', return_value=[mts1, mts2])

        # Mock check_ffmpeg
        mocker.patch('mts_converter.check_ffmpeg', return_value=True)

        run_cli([str(mts1), str(mts2)])

        mock_batch.assert_called_once()
        mock_instance.convert_batch.assert_called_once()

    def test_run_cli_uses_single_file_mode_for_legacy(self, tmp_path, mocker):
        """run_cli should use legacy single-file mode for input.mts output.mp4."""
        from mts_converter import run_cli

        mts_file = tmp_path / "video.mts"
        mts_file.touch()

        # Mock convert_video
        mock_convert = mocker.patch('mts_converter.convert_video', return_value=True)
        mocker.patch('mts_converter.check_ffmpeg', return_value=True)

        run_cli([str(mts_file), str(tmp_path / "output.mp4")])

        # Should call convert_video directly, not BatchConverter
        mock_convert.assert_called_once()

    def test_run_cli_displays_progress_during_batch(self, tmp_path, mocker, capsys):
        """run_cli should display per-file progress during batch conversion."""
        from mts_converter import run_cli
        from batch_converter import BatchResult

        mts1 = tmp_path / "video1.mts"
        mts2 = tmp_path / "video2.mts"
        mts1.touch()
        mts2.touch()

        # Mock discover_files
        mocker.patch('batch_converter.discover_files', return_value=[mts1, mts2])
        mocker.patch('mts_converter.check_ffmpeg', return_value=True)

        # Mock BatchConverter to capture the progress callback
        mock_batch = mocker.patch('batch_converter.BatchConverter')
        mock_instance = mock_batch.return_value
        mock_instance.convert_batch.return_value = [
            BatchResult(input_file=mts1, output_file=mts1.with_suffix('.mp4'), success=True, error=None),
            BatchResult(input_file=mts2, output_file=mts2.with_suffix('.mp4'), success=True, error=None),
        ]

        run_cli([str(mts1), str(mts2)])

        # Check that progress callback was provided
        call_kwargs = mock_batch.call_args[1]
        assert 'progress_callback' in call_kwargs

    def test_run_cli_shows_batch_summary(self, tmp_path, mocker, capsys):
        """run_cli should show summary after batch completion."""
        from mts_converter import run_cli
        from batch_converter import BatchResult

        mts1 = tmp_path / "video1.mts"
        mts2 = tmp_path / "video2.mts"
        mts1.touch()
        mts2.touch()

        mocker.patch('batch_converter.discover_files', return_value=[mts1, mts2])
        mocker.patch('mts_converter.check_ffmpeg', return_value=True)

        mock_batch = mocker.patch('batch_converter.BatchConverter')
        mock_instance = mock_batch.return_value
        mock_instance.convert_batch.return_value = [
            BatchResult(input_file=mts1, output_file=mts1.with_suffix('.mp4'), success=True, error=None),
            BatchResult(input_file=mts2, output_file=mts2.with_suffix('.mp4'), success=True, error=None),
        ]

        run_cli([str(mts1), str(mts2)])

        captured = capsys.readouterr()
        # Should show some kind of summary
        assert "2" in captured.out  # Should mention the number of files

    def test_run_cli_passes_output_dir_to_batch_converter(self, tmp_path, mocker):
        """run_cli should pass output_dir to BatchConverter."""
        from mts_converter import run_cli

        mts_file = tmp_path / "video.mts"
        output_dir = tmp_path / "output"
        mts_file.touch()
        output_dir.mkdir()

        mocker.patch('batch_converter.discover_files', return_value=[mts_file])
        mocker.patch('mts_converter.check_ffmpeg', return_value=True)

        mock_batch = mocker.patch('batch_converter.BatchConverter')
        mock_instance = mock_batch.return_value
        mock_instance.convert_batch.return_value = []

        run_cli([str(mts_file), '-o', str(output_dir)])

        call_kwargs = mock_batch.call_args[1]
        assert call_kwargs.get('output_dir') == Path(output_dir)

    def test_run_cli_returns_success_count(self, tmp_path, mocker):
        """run_cli should return tuple of (success_count, failure_count)."""
        from mts_converter import run_cli
        from batch_converter import BatchResult

        mts1 = tmp_path / "video1.mts"
        mts2 = tmp_path / "video2.mts"
        mts1.touch()
        mts2.touch()

        mocker.patch('batch_converter.discover_files', return_value=[mts1, mts2])
        mocker.patch('mts_converter.check_ffmpeg', return_value=True)

        mock_batch = mocker.patch('batch_converter.BatchConverter')
        mock_instance = mock_batch.return_value
        mock_instance.convert_batch.return_value = [
            BatchResult(input_file=mts1, output_file=mts1.with_suffix('.mp4'), success=True, error=None),
            BatchResult(input_file=mts2, output_file=None, success=False, error="Error"),
        ]

        success, failed = run_cli([str(mts1), str(mts2)])

        assert success == 1
        assert failed == 1


class TestCLIExitCodes:
    """Tests for CLI exit code handling."""

    def test_main_exits_with_0_on_all_success(self, tmp_path, mocker):
        """main should exit with code 0 when all conversions succeed."""
        import sys
        from mts_converter import main
        from batch_converter import BatchResult

        mts1 = tmp_path / "video1.mts"
        mts2 = tmp_path / "video2.mts"
        mts1.touch()
        mts2.touch()

        mocker.patch('sys.argv', ['mts_converter', str(mts1), str(mts2)])
        mocker.patch('mts_converter.check_ffmpeg', return_value=True)
        mocker.patch('batch_converter.discover_files', return_value=[mts1, mts2])

        mock_batch = mocker.patch('batch_converter.BatchConverter')
        mock_instance = mock_batch.return_value
        mock_instance.convert_batch.return_value = [
            BatchResult(input_file=mts1, output_file=mts1.with_suffix('.mp4'), success=True, error=None),
            BatchResult(input_file=mts2, output_file=mts2.with_suffix('.mp4'), success=True, error=None),
        ]

        mock_exit = mocker.patch('sys.exit')

        main()

        # Should exit with 0 (success) or not call sys.exit at all
        if mock_exit.called:
            mock_exit.assert_called_with(0)

    def test_main_exits_with_1_on_any_failure(self, tmp_path, mocker):
        """main should exit with code 1 when any conversion fails."""
        import sys
        from mts_converter import main
        from batch_converter import BatchResult

        mts1 = tmp_path / "video1.mts"
        mts2 = tmp_path / "video2.mts"
        mts1.touch()
        mts2.touch()

        mocker.patch('sys.argv', ['mts_converter', str(mts1), str(mts2)])
        mocker.patch('mts_converter.check_ffmpeg', return_value=True)
        mocker.patch('batch_converter.discover_files', return_value=[mts1, mts2])

        mock_batch = mocker.patch('batch_converter.BatchConverter')
        mock_instance = mock_batch.return_value
        mock_instance.convert_batch.return_value = [
            BatchResult(input_file=mts1, output_file=mts1.with_suffix('.mp4'), success=True, error=None),
            BatchResult(input_file=mts2, output_file=None, success=False, error="Conversion failed"),
        ]

        mock_exit = mocker.patch('sys.exit')

        main()

        mock_exit.assert_called_with(1)

    def test_failed_files_display_error_messages(self, tmp_path, mocker, capsys):
        """Failed files should display clear error messages."""
        from mts_converter import run_cli
        from batch_converter import BatchResult

        mts1 = tmp_path / "video1.mts"
        mts2 = tmp_path / "video2.mts"
        mts1.touch()
        mts2.touch()

        mocker.patch('mts_converter.check_ffmpeg', return_value=True)
        mocker.patch('batch_converter.discover_files', return_value=[mts1, mts2])

        mock_batch = mocker.patch('batch_converter.BatchConverter')
        mock_instance = mock_batch.return_value
        mock_instance.convert_batch.return_value = [
            BatchResult(input_file=mts1, output_file=mts1.with_suffix('.mp4'), success=True, error=None),
            BatchResult(input_file=mts2, output_file=None, success=False, error="FFmpeg encoding error"),
        ]

        run_cli([str(mts1), str(mts2)])

        captured = capsys.readouterr()
        # Should display the failed file name and error
        assert "video2.mts" in captured.out
        assert "FFmpeg encoding error" in captured.out

    def test_main_uses_run_cli(self, tmp_path, mocker):
        """main should use run_cli for command execution."""
        from mts_converter import main

        mts_file = tmp_path / "video.mts"
        mts_file.touch()

        mocker.patch('sys.argv', ['mts_converter', str(mts_file)])
        mock_run_cli = mocker.patch('mts_converter.run_cli', return_value=(1, 0))

        try:
            main()
        except SystemExit:
            pass

        mock_run_cli.assert_called_once()
