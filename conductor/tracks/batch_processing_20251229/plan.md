# Implementation Plan: Batch Processing Support

## Phase 1: Core Batch Processing Module

### Task 1.1: Create batch converter module structure [abfabe0]
- [x] Create `batch_converter.py` with BatchConverter class
- [x] Define BatchResult dataclass for tracking conversion results
- [x] Define BatchProgress callback protocol for progress updates

### Task 1.2: Implement file discovery [94d8894]
- [x] Add function to resolve file paths from arguments (files, directories, globs)
- [x] Filter to only .mts/.MTS files
- [x] Validate all files exist before starting batch

### Task 1.3: Implement batch conversion logic [14aba37]
- [x] Create `convert_batch()` method that iterates through files
- [x] Call existing `convert_video()` for each file
- [x] Track success/failure for each file
- [x] Invoke progress callback after each file

### Task 1.4: Add output directory support
- [ ] Add `output_dir` parameter to batch converter
- [ ] Generate output paths in specified directory
- [ ] Handle filename conflicts with numeric suffix

### Task 1.5: Phase 1 Completion
- [ ] Run all tests and verify >80% coverage
- [ ] Manual verification of batch module
- [ ] Phase checkpoint

## Phase 2: CLI Integration

### Task 2.1: Update CLI argument parsing
- [ ] Modify argument parser to accept multiple input paths
- [ ] Add `--output-dir` option
- [ ] Add `--continue-on-error` flag
- [ ] Maintain single-file backward compatibility

### Task 2.2: Integrate batch converter with CLI
- [ ] Detect batch vs single-file mode based on arguments
- [ ] Display per-file progress during batch conversion
- [ ] Show batch summary at completion

### Task 2.3: CLI error handling and exit codes
- [ ] Return exit code 0 if all successful
- [ ] Return exit code 1 if any failures
- [ ] Display clear error messages for failed files

### Task 2.4: Phase 2 Completion
- [ ] Run all tests and verify >80% coverage
- [ ] Manual verification of CLI batch mode
- [ ] Phase checkpoint

## Phase 3: GUI Integration

### Task 3.1: Add file queue UI components
- [ ] Replace single file input with file list widget
- [ ] Add "Add Files" button for multi-file selection
- [ ] Add "Add Folder" button for directory selection
- [ ] Add "Remove" button to remove selected files from queue
- [ ] Add "Clear All" button

### Task 3.2: Update progress UI for batch mode
- [ ] Add overall batch progress bar
- [ ] Show current file being processed
- [ ] Display "X of Y files" counter
- [ ] Add elapsed/estimated time display

### Task 3.3: Implement batch conversion in GUI
- [ ] Integrate BatchConverter with GUI
- [ ] Update progress callback to refresh UI
- [ ] Handle thread-safe UI updates

### Task 3.4: Add cancel functionality
- [ ] Add "Cancel" button during conversion
- [ ] Implement graceful cancellation (finish current file)
- [ ] Update UI to show cancelled state

### Task 3.5: Batch completion and error display
- [ ] Show summary dialog on completion
- [ ] List any failed files with error reasons
- [ ] Allow user to retry failed files

### Task 3.6: Phase 3 Completion
- [ ] Run all tests and verify >80% coverage
- [ ] Manual verification of GUI batch mode
- [ ] Phase checkpoint

## Phase 4: Documentation and Polish

### Task 4.1: Update README documentation
- [ ] Document CLI batch usage with examples
- [ ] Document GUI batch workflow
- [ ] Add troubleshooting section for batch issues

### Task 4.2: Update CLAUDE.md
- [ ] Add batch processing to architecture section
- [ ] Document new module structure

### Task 4.3: Final testing and polish
- [ ] End-to-end testing with real MTS files
- [ ] Performance testing with large batches
- [ ] UI polish and edge case handling

### Task 4.4: Phase 4 Completion
- [ ] Final test run and coverage report
- [ ] Manual verification of complete feature
- [ ] Final phase checkpoint

## Notes
- All tasks follow TDD workflow: write tests first, then implement
- Each phase ends with verification checkpoint per workflow.md
- Existing single-file functionality must remain unchanged
