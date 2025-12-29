# Specification: Batch Processing Support

## Overview
Add the ability to convert multiple MTS files in a single operation, with progress tracking for both individual files and the overall batch.

## User Stories

### US-1: CLI Batch Conversion
**As a** professional user automating video conversions
**I want to** convert multiple MTS files with a single command
**So that** I can process entire folders of footage efficiently

**Acceptance Criteria:**
- User can pass multiple file paths as arguments: `python mts_converter.py file1.mts file2.mts file3.mts`
- User can pass a directory path to convert all MTS files within: `python mts_converter.py ./videos/`
- User can use glob patterns: `python mts_converter.py *.mts`
- Progress shows current file number and total (e.g., "Converting 2/5: video2.mts")
- Summary displayed at end showing successful/failed conversions
- Non-zero exit code if any conversion fails

### US-2: GUI Batch Selection
**As a** professional user using the graphical interface
**I want to** select multiple MTS files for conversion
**So that** I can batch process without command-line knowledge

**Acceptance Criteria:**
- "Browse" button allows multi-file selection
- New "Add Folder" button to add all MTS files from a directory
- File list shows all queued files with status indicators
- User can remove individual files from the queue before starting
- Clear visual distinction between pending, converting, completed, and failed files

### US-3: Batch Progress Tracking
**As a** user converting multiple files
**I want to** see progress for the entire batch
**So that** I can estimate total time remaining

**Acceptance Criteria:**
- Overall progress bar showing batch completion percentage
- Current file indicator with individual progress
- Elapsed time and estimated time remaining
- Ability to cancel the batch (stops after current file completes)

### US-4: Batch Output Options
**As a** user processing multiple files
**I want to** control where converted files are saved
**So that** I can organize my output efficiently

**Acceptance Criteria:**
- Default: Save MP4 next to original MTS file
- Option: Specify output directory for all converted files
- Original filenames preserved (with .mp4 extension)
- Handle filename conflicts (append number if file exists)

## Technical Requirements

### TR-1: Core Batch Processing Module
- Create `batch_converter.py` module with reusable batch logic
- Support file discovery from directories and glob patterns
- Implement progress callback mechanism for UI updates
- Handle individual file failures without stopping batch

### TR-2: CLI Integration
- Update `mts_converter.py` argument parsing for multiple inputs
- Add `--output-dir` flag for batch output directory
- Add `--continue-on-error` flag (default: true)
- Maintain backward compatibility with single-file usage

### TR-3: GUI Integration
- Update `mts_converter_gui.py` with file queue management
- Add batch progress UI components
- Implement threaded batch processing
- Add cancel functionality

### TR-4: Error Handling
- Log individual file errors without stopping batch
- Generate summary report at completion
- Store error details for failed files

## Out of Scope
- Parallel processing (files converted sequentially)
- Recursive directory scanning
- File format filtering beyond .mts extension
- Pause/resume functionality

## Dependencies
- Existing `convert_video()` function in `mts_converter.py`
- Existing `ffmpeg_utils.py` module
- No new external dependencies required
