#!/usr/bin/env python3
"""Tests for mts_converter_gui batch processing features.

Tests the GUI batch conversion functionality including file queue management,
progress UI, batch conversion, and cancel functionality.

These tests verify the existence of batch-related attributes and methods
by directly inspecting the class definition, avoiding tkinter initialization.
"""

import pytest
import sys
import inspect
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestFileQueueUI:
    """Tests for file queue UI components (Task 3.1).

    These tests verify that the MTSConverterGUI class has the required
    attributes and methods for batch file queue management.
    """

    def test_gui_class_has_file_queue_initialization(self):
        """GUI should initialize file_queue as a list in __init__."""
        # Read the source file and check for file_queue initialization
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'self.file_queue' in source, \
            "MTSConverterGUI should have a file_queue attribute"
        # Allow for type annotation syntax: self.file_queue: List[Path] = []
        assert ('self.file_queue = []' in source or
                'self.file_queue=[]' in source or
                'self.file_queue:' in source), \
            "file_queue should be initialized as a list"

    def test_gui_class_has_file_listbox(self):
        """GUI should have a listbox for displaying file queue."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'self.file_listbox' in source, \
            "MTSConverterGUI should have a file_listbox attribute"

    def test_gui_class_has_add_files_button(self):
        """GUI should have an 'Add Files' button."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'self.add_files_btn' in source, \
            "MTSConverterGUI should have an add_files_btn attribute"

    def test_gui_class_has_add_folder_button(self):
        """GUI should have an 'Add Folder' button."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'self.add_folder_btn' in source, \
            "MTSConverterGUI should have an add_folder_btn attribute"

    def test_gui_class_has_remove_button(self):
        """GUI should have a 'Remove' button."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'self.remove_btn' in source, \
            "MTSConverterGUI should have a remove_btn attribute"

    def test_gui_class_has_clear_all_button(self):
        """GUI should have a 'Clear All' button."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'self.clear_all_btn' in source, \
            "MTSConverterGUI should have a clear_all_btn attribute"

    def test_gui_class_has_add_files_to_queue_method(self):
        """GUI should have add_files_to_queue method."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'def add_files_to_queue(self' in source, \
            "MTSConverterGUI should have add_files_to_queue method"

    def test_gui_class_has_remove_files_from_queue_method(self):
        """GUI should have remove_files_from_queue method."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'def remove_files_from_queue(self' in source, \
            "MTSConverterGUI should have remove_files_from_queue method"

    def test_gui_class_has_clear_file_queue_method(self):
        """GUI should have clear_file_queue method."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'def clear_file_queue(self' in source, \
            "MTSConverterGUI should have clear_file_queue method"


class TestBatchProgressUI:
    """Tests for batch progress UI components (Task 3.2)."""

    def test_gui_class_has_batch_progress_var(self):
        """GUI should have batch_progress_var for tracking overall progress."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'self.batch_progress_var' in source, \
            "MTSConverterGUI should have batch_progress_var attribute"

    def test_gui_class_has_batch_progress_bar(self):
        """GUI should have batch_progress_bar widget."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'self.batch_progress_bar' in source, \
            "MTSConverterGUI should have batch_progress_bar attribute"

    def test_gui_class_has_current_file_label(self):
        """GUI should have current_file_label to show current file."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'self.current_file_label' in source, \
            "MTSConverterGUI should have current_file_label attribute"

    def test_gui_class_has_file_counter_label(self):
        """GUI should have file_counter_label for 'X of Y files'."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'self.file_counter_label' in source, \
            "MTSConverterGUI should have file_counter_label attribute"

    def test_gui_class_has_elapsed_time_label(self):
        """GUI should have elapsed_time_label."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'self.elapsed_time_label' in source, \
            "MTSConverterGUI should have elapsed_time_label attribute"


class TestBatchConversionIntegration:
    """Tests for batch conversion integration with GUI (Task 3.3)."""

    def test_gui_class_has_start_batch_conversion_method(self):
        """GUI should have start_batch_conversion method."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'def start_batch_conversion(self' in source, \
            "MTSConverterGUI should have start_batch_conversion method"

    def test_gui_class_has_on_batch_progress_method(self):
        """GUI should have on_batch_progress callback method."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'def on_batch_progress(self' in source, \
            "MTSConverterGUI should have on_batch_progress method"

    def test_gui_class_has_output_dir(self):
        """GUI should have output_dir attribute."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'self.output_dir' in source, \
            "MTSConverterGUI should have output_dir attribute"

    def test_gui_class_has_browse_output_dir_button(self):
        """GUI should have browse_output_dir_btn button."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'self.browse_output_dir_btn' in source, \
            "MTSConverterGUI should have browse_output_dir_btn attribute"


class TestCancelFunctionality:
    """Tests for cancel functionality (Task 3.4)."""

    def test_gui_class_has_cancel_button(self):
        """GUI should have a cancel button."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'self.cancel_btn' in source, \
            "MTSConverterGUI should have cancel_btn attribute"

    def test_gui_class_has_cancel_flag(self):
        """GUI should have cancel_requested flag."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'self.cancel_requested' in source, \
            "MTSConverterGUI should have cancel_requested attribute"

    def test_gui_class_has_request_cancel_method(self):
        """GUI should have request_cancel method."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'def request_cancel(self' in source, \
            "MTSConverterGUI should have request_cancel method"


class TestBatchCompletionDisplay:
    """Tests for batch completion and error display (Task 3.5)."""

    def test_gui_class_has_show_batch_summary_method(self):
        """GUI should have show_batch_summary method."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'def show_batch_summary(self' in source, \
            "MTSConverterGUI should have show_batch_summary method"

    def test_gui_class_has_batch_results(self):
        """GUI should have batch_results attribute."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'self.batch_results' in source, \
            "MTSConverterGUI should have batch_results attribute"


class TestPositionDropdown:
    """Tests for position dropdown widget (Task 4.1)."""

    def test_gui_class_has_position_variable(self):
        """GUI should have position StringVar."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'self.position' in source, \
            "MTSConverterGUI should have position attribute"

    def test_gui_position_dropdown_has_four_options(self):
        """Position dropdown should have exactly four corner options."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        # Check that position combobox values contain exactly the four corners
        assert '"top-left"' in source, "Position dropdown should include top-left"
        assert '"top-right"' in source, "Position dropdown should include top-right"
        assert '"bottom-left"' in source, "Position dropdown should include bottom-left"
        assert '"bottom-right"' in source, "Position dropdown should include bottom-right"
        # Ensure center is NOT in the position options
        # The values list should only have the four corners
        import re
        values_match = re.search(r'values=\[([^\]]+)\]', source)
        if values_match:
            values_str = values_match.group(1)
            assert '"center"' not in values_str, \
                "Position dropdown should NOT include center option"

    def test_gui_position_default_is_bottom_right(self):
        """Position dropdown should default to bottom-right."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        # Check that position StringVar is initialized with "bottom-right"
        assert 'self.position = tk.StringVar(value="bottom-right")' in source, \
            "Position should default to bottom-right"

    def test_gui_has_position_combobox(self):
        """GUI should have a combobox for position selection."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'ttk.Combobox' in source, \
            "GUI should use ttk.Combobox for position selection"
        assert 'textvariable=self.position' in source, \
            "Position combobox should be bound to self.position"


class TestGUIPositionIntegration:
    """Tests for GUI position integration with conversion (Task 4.2)."""

    def test_gui_conversion_uses_position_variable(self):
        """GUI conversion should read position from self.position."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'self.position.get()' in source, \
            "GUI should read position value using self.position.get()"

    def test_gui_conversion_has_position_mapping(self):
        """GUI conversion should have positions mapping dictionary."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        # Check that position mapping is defined in conversion code
        assert 'positions = {' in source, \
            "GUI should have positions dictionary for coordinate mapping"

    def test_gui_conversion_position_mapping_matches_cli(self):
        """GUI position mapping should match CLI position constants."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        # Verify all four corner positions have correct x:y coordinates
        assert '"top-left": "x=20:y=20"' in source, \
            "top-left position should use correct coordinates"
        assert '"top-right": "x=w-tw-20:y=20"' in source, \
            "top-right position should use correct coordinates"
        assert '"bottom-left": "x=20:y=h-th-20"' in source, \
            "bottom-left position should use correct coordinates"
        assert '"bottom-right": "x=w-tw-20:y=h-th-20"' in source, \
            "bottom-right position should use correct coordinates"

    def test_gui_conversion_default_fallback_is_bottom_right(self):
        """GUI conversion should fall back to bottom-right if position invalid."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        # Check the .get() fallback uses bottom-right
        assert 'positions["bottom-right"]' in source, \
            "GUI should use bottom-right as fallback position"


class TestGUIMetadataErrorDisplay:
    """Tests for GUI metadata error display (Task 4.3)."""

    def test_gui_imports_metadata_extraction_error(self):
        """GUI should import MetadataExtractionError from mts_converter."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        assert 'MetadataExtractionError' in source, \
            "GUI should import MetadataExtractionError"

    def test_gui_does_not_fallback_to_file_mtime(self):
        """GUI should NOT fall back to file modification time."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        # Check that getmtime fallback is not present in get_video_creation_time
        # The old code had: mtime = os.path.getmtime(input_file)
        assert 'os.path.getmtime' not in source, \
            "GUI should NOT use os.path.getmtime as fallback"

    def test_gui_does_not_fallback_to_datetime_now(self):
        """GUI should NOT fall back to datetime.now()."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        # Count occurrences of datetime.now() - should only be for elapsed time tracking
        import re
        now_calls = re.findall(r'datetime\.now\(\)', source)
        # If datetime.now() is used, it should not be in get_video_creation_time
        # Check by looking for the fallback pattern
        assert 'return datetime.now()' not in source, \
            "GUI should NOT fall back to datetime.now()"

    def test_gui_raises_error_on_metadata_failure(self):
        """GUI should raise MetadataExtractionError when metadata unavailable."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        # Check that MetadataExtractionError is raised in extraction
        assert 'raise MetadataExtractionError' in source, \
            "GUI should raise MetadataExtractionError when metadata unavailable"

    def test_gui_handles_metadata_error_gracefully(self):
        """GUI should catch metadata errors and continue batch processing."""
        with open('mts_converter_gui.py', 'r') as f:
            source = f.read()
        # Check that MetadataExtractionError is caught in conversion logic
        assert 'except MetadataExtractionError' in source or \
               'except Exception' in source, \
            "GUI should catch metadata errors"
