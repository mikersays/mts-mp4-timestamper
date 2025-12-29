# Specification: Timestamp Defaults and Metadata Fix

## Overview
Fix the timestamp overlay feature to use the correct footage recording time from video metadata (not file creation time) and change the default position to bottom-right corner with user-configurable position options.

## Functional Requirements

### FR-1: Default Timestamp Position
- **Current behavior:** Timestamp appears at a non-bottom-right position
- **New behavior:** Timestamp defaults to bottom-right corner
- Applies to both GUI and CLI versions

### FR-2: User-Configurable Position (GUI)
- Add a dropdown menu in the GUI to select timestamp position
- Available options:
  - Top-Left
  - Top-Right
  - Bottom-Left
  - Bottom-Right (default, selected by default)
- Position selection must be applied before conversion starts

### FR-3: User-Configurable Position (CLI)
- Add `--position` flag to CLI
- Accepted values: `top-left`, `top-right`, `bottom-left`, `bottom-right`
- Default value: `bottom-right`
- Example usage: `python mts_converter.py input.mts --position top-left`

### FR-4: Correct Timestamp Source
- **Current behavior:** Timestamp uses file creation/modification time
- **New behavior:** Timestamp must use the footage recording time extracted from MTS file metadata
- Use ffprobe to extract the actual recording timestamp from video metadata fields (e.g., `creation_time`, `date` tags)

### FR-5: Metadata Extraction Failure Handling
- If recording timestamp cannot be extracted from metadata (corrupted file, missing metadata):
  - Fail the conversion
  - Display clear error message explaining that the recording time could not be determined
  - Do not fall back to file system timestamps
- Error message should guide user on potential causes (corrupted file, non-MTS source, missing metadata)

## Non-Functional Requirements

### NFR-1: Backward Compatibility
- Existing single-file and batch conversion workflows must continue to work
- Only the default position and timestamp source behavior changes

### NFR-2: User Experience
- Position dropdown should be intuitive and clearly labeled
- Error messages for metadata failures should be user-friendly and actionable

## Acceptance Criteria

- [ ] Default timestamp position is bottom-right for both GUI and CLI
- [ ] GUI displays position dropdown with four corner options
- [ ] CLI accepts `--position` flag with four valid values
- [ ] Timestamp reflects actual footage recording time from metadata
- [ ] Conversion fails with clear error if metadata timestamp unavailable
- [ ] Batch processing respects position setting for all files
- [ ] Existing tests updated and new tests added for position/metadata logic

## Out of Scope
- Custom position coordinates (pixel-level positioning)
- Custom timestamp format changes
- Position presets or saved preferences
- Center position options (top-center, bottom-center, middle positions)

## Dependencies
- Existing `convert_video()` function in `mts_converter.py`
- Existing `ffmpeg_utils.py` module for ffprobe calls
- Existing GUI framework in `mts_converter_gui.py`
