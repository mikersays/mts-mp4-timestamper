# Plan: Timestamp Defaults and Metadata Fix

## Phase 1: Core Position Configuration [checkpoint: ]

### Task 1.1: Add Position Constants and Utility Functions [ffc74e6]
- [x] **Red:** Write tests for position constants and coordinate calculation
  - [x] Test that all four position constants exist (TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT)
  - [x] Test coordinate calculation function returns correct x:y values for each position
  - [x] Test default position is BOTTOM_RIGHT
- [x] **Green:** Implement position constants and coordinate calculation
  - [x] Add position constants to module
  - [x] Create `get_position_coordinates(position, margin)` function
  - [x] Return appropriate FFmpeg x:y expressions for each corner
- [x] **Refactor:** Clean up implementation if needed

### Task 1.2: Update FFmpeg drawtext Filter for Position [309af1b]
- [x] **Red:** Write tests for drawtext filter generation with position parameter
  - [x] Test filter string contains correct x:y coordinates for each position
  - [x] Test default position produces bottom-right coordinates
- [x] **Green:** Modify drawtext filter builder to accept position parameter
  - [x] Update filter generation function signature
  - [x] Integrate position coordinates into filter string
- [x] **Refactor:** Ensure backward compatibility with existing calls

### Task 1.3: Conductor - Phase 1 Completion Verification
- [x] Execute Phase Completion Verification Protocol (see workflow.md)

---

## Phase 2: Fix Metadata Timestamp Extraction [checkpoint: ]

### Task 2.1: Improve Metadata Timestamp Extraction
- [ ] **Red:** Write tests for metadata timestamp extraction
  - [ ] Test extraction of creation_time from valid MTS metadata
  - [ ] Test extraction fails gracefully when metadata missing
  - [ ] Test that file mtime is NOT used as fallback
- [ ] **Green:** Update timestamp extraction to use correct metadata field
  - [ ] Review current ffprobe metadata extraction logic
  - [ ] Ensure `creation_time` or appropriate field is used
  - [ ] Remove fallback to file modification time
- [ ] **Refactor:** Consolidate metadata extraction logic

### Task 2.2: Implement Strict Error Handling for Missing Metadata
- [ ] **Red:** Write tests for error handling behavior
  - [ ] Test conversion fails when metadata timestamp unavailable
  - [ ] Test appropriate error message is returned
  - [ ] Test batch processing handles individual metadata failures correctly
- [ ] **Green:** Implement strict failure mode
  - [ ] Raise exception when metadata timestamp cannot be extracted
  - [ ] Create user-friendly error message explaining the issue
  - [ ] Ensure batch converter reports individual failures properly
- [ ] **Refactor:** Ensure error messages are consistent across CLI and GUI

### Task 2.3: Conductor - Phase 2 Completion Verification
- [ ] Execute Phase Completion Verification Protocol (see workflow.md)

---

## Phase 3: CLI Integration [checkpoint: ]

### Task 3.1: Add --position Flag to CLI
- [ ] **Red:** Write tests for CLI position argument parsing
  - [ ] Test --position flag accepts valid values (top-left, top-right, bottom-left, bottom-right)
  - [ ] Test --position defaults to bottom-right when not specified
  - [ ] Test invalid position value shows helpful error
- [ ] **Green:** Implement CLI argument parsing for position
  - [ ] Add --position argument to argparse configuration
  - [ ] Validate position value against allowed options
  - [ ] Pass position to conversion function
- [ ] **Refactor:** Update help text and usage examples

### Task 3.2: Integrate Position into CLI Conversion Flow
- [ ] **Red:** Write integration tests for CLI with position flag
  - [ ] Test single file conversion with explicit position
  - [ ] Test batch conversion applies position to all files
- [ ] **Green:** Wire position parameter through CLI conversion
  - [ ] Update convert_video() calls to include position
  - [ ] Ensure batch processing passes position correctly
- [ ] **Refactor:** Clean up any redundant code

### Task 3.3: Conductor - Phase 3 Completion Verification
- [ ] Execute Phase Completion Verification Protocol (see workflow.md)

---

## Phase 4: GUI Integration [checkpoint: ]

### Task 4.1: Add Position Dropdown to GUI
- [ ] **Red:** Write tests for GUI position dropdown widget
  - [ ] Test dropdown exists with four position options
  - [ ] Test default selection is Bottom-Right
  - [ ] Test selection can be changed programmatically
- [ ] **Green:** Implement position dropdown in GUI
  - [ ] Add ttk.Combobox for position selection
  - [ ] Populate with four corner options
  - [ ] Set default value to Bottom-Right
  - [ ] Position widget appropriately in layout
- [ ] **Refactor:** Ensure consistent styling with existing GUI elements

### Task 4.2: Integrate Position Selection into GUI Conversion
- [ ] **Red:** Write tests for GUI conversion with position
  - [ ] Test selected position is passed to conversion function
  - [ ] Test batch conversion uses selected position for all files
- [ ] **Green:** Wire position selection to conversion logic
  - [ ] Read selected position value when conversion starts
  - [ ] Pass position to convert_video() and batch converter
- [ ] **Refactor:** Ensure UI state is properly managed

### Task 4.3: Improve GUI Error Display for Metadata Failures
- [ ] **Red:** Write tests for error display in GUI
  - [ ] Test metadata failure shows user-friendly error dialog
  - [ ] Test error message is clear and actionable
- [ ] **Green:** Implement error handling UI
  - [ ] Catch metadata extraction exceptions
  - [ ] Display appropriate error dialog with guidance
  - [ ] Ensure batch processing continues with other files, reports failures
- [ ] **Refactor:** Ensure consistent error handling patterns

### Task 4.4: Conductor - Phase 4 Completion Verification
- [ ] Execute Phase Completion Verification Protocol (see workflow.md)

---

## Phase 5: Documentation and Polish [checkpoint: ]

### Task 5.1: Update CLAUDE.md and Code Comments
- [ ] Update CLAUDE.md with new --position flag documentation
- [ ] Ensure docstrings reflect new position parameter
- [ ] Update any inline comments for clarity

### Task 5.2: Final Integration Testing
- [ ] Run full test suite with coverage report
- [ ] Verify >80% code coverage maintained
- [ ] Run pylint and fix any issues

### Task 5.3: Conductor - Phase 5 Completion Verification
- [ ] Execute Phase Completion Verification Protocol (see workflow.md)
